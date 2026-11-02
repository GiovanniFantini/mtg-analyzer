"""Offline integration of the saved 2 November TRK evidence.

--extract normalizes factual ratings from the acquisition's temporary HTML.
Without it, every input comes from the repository; no network is used.
"""
import argparse
import copy
import gzip
import hashlib
import html
import json
import re
import unicodedata
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from research_star_trek_20261102 import CACHE, DATE, OUT, ROOT, save

BASE = ROOT / 'expansions/star-trek'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def key(name):
    return ''.join(c for c in unicodedata.normalize('NFKD', name).casefold() if c.isalnum())


class Headings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.heading = None
        self.parts = []
        self.name = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if tag in ('h2', 'h3'):
            self.heading, self.parts = tag, []

    def handle_data(self, data):
        if self.heading:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == self.heading:
            text = ''.join(self.parts).strip()
            self.heading = None
            if text.startswith('Rating:'):
                match = re.fullmatch(r'Rating:\s*([0-5](?:\.\d+)?)/5', text)
                if not match:
                    raise ValueError('Unrecognized rating: ' + text)
                self.rows.append({'sourceName': self.name, 'value': float(match[1]), 'original': match[1] + '/5'})
            else:
                self.name = text


def extract():
    raw = load(OUT / 'scryfall.json')['data']
    canonical = {key(r['name']): r for r in raw}
    canonical = {k: min([r for r in raw if key(r['name']) == k], key=lambda r: (len(r['collector_number']), r['collector_number'])) for k in canonical}
    groups = {
        'Planets': [r['name'] for r in raw if r['set'] == 'trk' and r['collector_number'].isdigit() and int(r['collector_number']) <= 311 and 'Land' in r['type_line'] and 'Planet' in r['type_line']],
        'Shock Lands': [r['name'] for r in raw if r['set'] == 'trk' and r['collector_number'].isdigit() and int(r['collector_number']) <= 311 and 'pay 2 life' in r.get('oracle_text', '')],
        'Surveil Lands': [r['name'] for r in raw if r['set'] == 'trk' and r['collector_number'].isdigit() and int(r['collector_number']) <= 311 and 'two or more other lands' in r.get('oracle_text', '')],
    }
    assert {k: len(v) for k, v in groups.items()} == {'Planets': 10, 'Shock Lands': 10, 'Surveil Lands': 5}
    rows, source_rows = [], []
    for color in ('white', 'blue', 'black', 'red', 'green', 'multicolor', 'artifacts-and-lands'):
        ident = 'arenazone-trk-' + color
        content = (CACHE / (ident + '.html')).read_text(encoding='utf-8')
        parser = Headings()
        parser.feed(content)
        published = re.search(r'"datePublished":"([^"T]+)', content)[1]
        source_rows.append({'source': ident, 'ratingEntries': len(parser.rows), 'published': published, 'author': 'J2SJosh (j2sjosh)', 'inputSha256': hashlib.sha256(content.encode('utf-8')).hexdigest()})
        for row in parser.rows:
            names = groups.get(row['sourceName'], [row['sourceName']])
            for name in names:
                card = canonical.get(key(name))
                if card is None:
                    raise ValueError('Unmatched review: ' + name)
                rows.append({**row, 'catalogId': card['oracle_id'], 'name': card['name'], 'source': ident, 'published': published, 'author': 'J2SJosh (j2sjosh)', 'scaleMax': 5, 'context': 'Draft, pre-release editorial review', 'groupAssessment': row['sourceName'] if row['sourceName'] in groups else None})
    assert len(rows) == len({r['catalogId'] for r in rows}) == 306
    expected = {r['oracle_id'] for r in raw if r['set'] == 'trk' and 'Basic Land' not in r['type_line']}
    assert {r['catalogId'] for r in rows} == expected
    save(OUT / 'limited-reviews.json', {'date': DATE, 'provider': 'MTG Arena Zone', 'sources': source_rows, 'sourceEntries': sum(s['ratingEntries'] for s in source_rows), 'cards': rows, 'groups': groups, 'missingTrkNonbasic': [], 'sdsCoverage': 0, 'method': 'Original 0-5 scores preserved without averaging. Group scores apply only to explicitly illustrated land cycles. No review prose copied; no engine score assigned.'})
    import enrich_star_trek_20261027 as helpers
    helpers.DATE, helpers.OUT, helpers.CACHE = DATE, OUT, CACHE
    stub = [{'id': r['oracle_id'], 'name': r['name']} for r in {r['oracle_id']: r for r in raw}.values()]
    models = helpers.standard_capture(stub, raw)
    assert models['unmatchedNames'] == []


def fresh_prospects(card, printing, finding):
    formats = {}
    for fmt in ('standard', 'pioneer', 'modern', 'legacy', 'vintage', 'pauper', 'commander', 'cedh', 'duel', 'draft', 'sealed', 'pick_two'):
        legal = card['legalities'].get('commander' if fmt == 'cedh' else fmt, 'unknown')
        entry = {'legality': legal, 'evidence': 'non_documentata', 'prospect': 'da_verificare', 'confidence': 'bassa', 'note': 'Nessun risultato post-uscita TRK acquisito. Lo stato corrente e l’ammissibilità prevista restano distinti.'}
        if fmt in ('draft', 'sealed', 'pick_two'):
            entry.update(legality='product_dependent', note='Utilizzabile se aperta nel prodotto previsto dall’evento; il catalogo non è una ricetta di collazione.')
        elif card['set'] == 'TRK' and legal not in ('banned', 'restricted') and (fmt != 'pauper' or card['rarity'] == 'common'):
            entry['releaseEligibility'] = {'date': '2026-11-13', 'status': 'legal', 'source': 'wizards-release-trk', 'kind': 'previsione_di_ammissibilita'}
        formats[fmt] = entry
    return {'date': DATE, 'kind': 'evidence_and_editorial_scenarios', 'summary': finding, 'gameplayReview': {'kind': 'analisi_editoriale_oracle', 'finding': finding, 'evidenceOfTournamentSuccess': False}, 'sources': ['scryfall-api', 'wizards-collecting', 'wizards-release-trk'], 'oracle': {}, 'formats': formats, 'tournamentObservations': [], 'commanderObservations': [], 'price': {'date': None, 'currency': 'EUR', 'metric': 'From', 'sourceLabel': 'Cardmarket', 'source': 'cardmarket-spoiler', 'printingId': None, 'set': card['set'].lower(), 'number': card['number'], 'from': None, 'nonfoil': None, 'foil': None, 'finishFilter': 'any', 'variants': [], 'comparison': {'date': '2026-10-27', 'samePrinting': None, 'nonfoil': None, 'from': None, 'changePct': None, 'status': 'missing_reference'}, 'coverageNote': 'Nessuna rilevazione Cardmarket acquisita per questa carta. Prezzi e finiture restano N/D.', 'outlook': {'kind': 'scenario_condizionale', 'thesis': 'Mancano prezzi verificati e dati di domanda sufficienti per una previsione economica.', 'confidence': 'bassa', 'targetPrice': None, 'probabilityOfRise': None}}, 'limitations': ['Valutazione prima dell’uscita, senza WR o risultati agonistici TRK.', 'Nessun prezzo, voto o risultato ereditato da un’altra carta.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract', action='store_true')
    args = parser.parse_args()
    if args.extract:
        extract()
    baseline = json.loads(gzip.decompress((OUT / 'baseline-cards.json.gz').read_bytes()))
    old = {c['id']: c for c in baseline['cards']}
    raw_doc = load(OUT / 'scryfall.json')
    raw = raw_doc['data']
    notes = {}
    old_names = {c['name']: c for c in baseline['cards']}
    # Use the audited active findings, preserving the six October corrections.
    for dated in ('20261027', '20261028'):
        for name in load(ROOT / ('research/star-trek-' + dated + '/editorial-notes.json')):
            if name in old_names:
                notes[name] = old_names[name]['prospects']['gameplayReview']['finding']
    for filename in ('editorial-notes.json', 'editorial-completion.json', 'editorial-final.json', 'land-assessments.json'):
        notes.update(load(OUT / filename))
    grouped = {}
    for printing in raw:
        grouped.setdefault(printing['oracle_id'], []).append(printing)
    assert set(old) <= set(grouped), 'Never silently remove existing identities'
    grades_doc = load(OUT / 'limited-reviews.json')
    grades = {r['catalogId']: r for r in grades_doc['cards']}
    models_doc = load(OUT / 'standard-constructed-preview.json')
    models = {r['catalogId']: r for r in models_doc['cards']}
    ratings = load(BASE / 'ratings.json')
    sources = load(BASE / 'sources.json')
    registry = {r['id']: r for r in sources['research']['sources']}
    for record in load(OUT / 'source-assessments.json')['sources']:
        previous = registry.get(record['id'], {})
        registry[record['id']] = {**previous, **record, 'label': previous.get('label', record.get('publisher', record['id'])), 'checked': DATE}
        sources['links'][record['id']] = record['url']
    registry['scryfall-api'].update(retrieved=DATE, checked=DATE, url=raw_doc['source_query'], status='retrieved', finding='Acquisite tutte le pagine, 341 identità e 611 stampe TRK/SDS. Identità di base complete; censimento dei trattamenti non certificato completo.')
    cards, delta = [], []
    import enrich_star_trek_20261027 as helpers
    for ident, prints in grouped.items():
        prints.sort(key=lambda p: (not p['collector_number'].isdigit(), int(p['collector_number']) if p['collector_number'].isdigit() else 100000, p['collector_number']))
        p = prints[0]
        card = copy.deepcopy(old.get(ident, {}))
        previous_name = card.get('name')
        if previous_name and previous_name != p['name']:
            card['previousNames'] = sorted(set(card.get('previousNames', []) + [previous_name]))
        image = (p.get('image_uris') or (p.get('card_faces') or [{}])[0].get('image_uris', {})).get('normal', '')
        card.update(id=ident, oracleId=ident, name=p['name'], full=p['name'], set=p['set'].upper(), number=p['collector_number'], mana=p.get('mana_cost', ''), cost=p.get('mana_cost', ''), cmc=p['cmc'], mv=p['cmc'], colors=p.get('colors', []), identity=p['color_identity'], type=p['type_line'].replace('\u2014', ':'), text=p.get('oracle_text', ''), rarity=p['rarity'], keywords=p.get('keywords', []), legalities=p['legalities'], image=image, large=image, url=p['scryfall_uri'].split('?')[0], faces=p.get('card_faces', []), power=p.get('power', ''), toughness=p.get('toughness', ''), releasedAt=p['released_at'], legalitiesRetrieved=DATE, legalitySource=p['scryfall_uri'].split('?')[0])
        card['prints'] = [{'number': r['collector_number'], 'image': (r.get('image_uris') or (r.get('card_faces') or [{}])[0].get('image_uris', {})).get('normal', ''), 'finishes': r['finishes'], 'frame_effects': r.get('frame_effects', []), 'promo_types': r.get('promo_types', [])} for r in prints]
        card.update(basic='Basic Land' in p['type_line'], land='Land' in p['type_line'], creature='Creature' in p['type_line'])
        for fix in card.get('catalogCorrections', []):
            field = fix['field']
            if fix['rawValue'] in card.get(field, ''):
                card[field] = card[field].replace(fix['rawValue'], fix['correctedValue'])
        card['oracle'] = card['text']
        # New identities must have an original, card-specific assessment.
        if ident not in old and card['name'] not in notes:
            raise ValueError('Missing original assessment: ' + card['name'])
        role, finding = helpers.profile(card, {k: {'role': card.get('role') or ('Mana e fixing' if card['land'] else 'Piano e condizioni'), 'finding': v} for k, v in notes.items()})
        prospect = copy.deepcopy(card.get('prospects')) if card.get('prospects') else fresh_prospects(card, p, finding)
        if card['name'] in notes:
            prospect.update(summary=finding, gameplayReview={'kind': 'analisi_editoriale_oracle', 'finding': finding, 'evidenceOfTournamentSuccess': False})
            card.update(role=role, why=finding)
        prospect.update(date=DATE, oracle={'printingId': p['id'], 'url': card['url'], 'set': p['set'], 'number': card['number'], 'manaCost': card['mana'], 'text': card['text']})
        prospect['limitations'] = ['Identità TRK/SDS complete; censimento dei trattamenti e collazione non certificati completi.' if s == 'Catalogo di anteprima parziale: i nuovi dati non rappresentano il set completo.' else s for s in prospect['limitations']]
        for fmt, entry in prospect['formats'].items():
            if fmt not in ('draft', 'sealed', 'pick_two'):
                entry['legality'] = p['legalities'].get('commander' if fmt == 'cedh' else fmt, 'unknown')
                entry['note'] = entry.get('note', '').replace('Stato Scryfall del 28 ottobre 2026', 'Stato Scryfall del 2 novembre 2026')
            else:
                entry['note'] = 'Identità TRK/SDS complete. Idoneità della specifica stampa e collazione da verificare; nessuna WR TRK importata.'
                entry['prospect'] = 'anteprima_da_testare'
        prospect['sources'] = sorted(set(prospect['sources']) | {'scryfall-api', 'wizards-release-trk'})
        if ident in models:
            prospect['automatedEvaluations'] = [{**models[ident], 'source': 'standard-preview-ratings', 'kind': 'automated_constructed_preview', 'retrieved': DATE, 'context': 'Constructed, prima dell’uscita'}]
            prospect['sources'] = sorted(set(prospect['sources']) | {'standard-preview-ratings', 'standard-method'})
        rating = copy.deepcopy(ratings['cards'].get(ident, {}))
        rating.update(role=card.get('role', role), why=card.get('why', finding))
        rating.setdefault('condition', 'Analisi preliminare: confronta curva, mana e supporto effettivo nel pool.')
        if ident in grades:
            grade = grades[ident]
            source = registry[grade['source']]
            evidence = {'author': grade['author'], 'original': grade['original'], 'stars': grade['value'], 'url': source['url'], 'kind': 'Recensione Draft prima dell’uscita', 'published': grade['published'], 'retrieved': DATE, 'source': grade['source']}
            if grade['groupAssessment']:
                evidence['groupAssessment'] = grade['groupAssessment']
            rating.update(community=grade['value'], communitySource=source['url'], communityMethod='Unica recensione Draft attribuita, scala originale 0-5 conservata. Nessuna media fra fonti o conversione da WR.', evidence=[evidence])
            prospect['sources'] = sorted(set(prospect['sources']) | {grade['source']})
            prospect['limitedReview'] = {**grade, 'retrieved': DATE, 'url': source['url']}
            prospect['formats']['draft'].update(evidence='recensione', note='Recensione Draft preliminare di J2SJosh, scala 0-5. Idoneità della specifica stampa al prodotto e risultati di gioco restano distinti.')
            rating['condition'] = 'Verifica curva, base di mana e supporti nel pool. Voto Draft esterno attribuito disponibile; nessun voto Sealed o peso numerico dei bot assegnato.'
        for field in ('score', 'community', 'communitySource', 'communityMethod', 'evidence', 'role', 'why', 'condition'):
            if field in rating:
                card[field] = rating[field]
        card['prospects'] = prospect
        ratings['cards'][ident] = rating
        changed = {k: {'before': old[ident].get(k), 'after': card.get(k)} for k in ('name', 'text', 'mana', 'type', 'rarity') if ident in old and old[ident].get(k) != card.get(k)}
        if ident not in old or changed:
            delta.append({'catalogId': ident, 'name': card['name'], 'new': ident not in old, 'changes': changed})
        cards.append(card)
    cards.sort(key=lambda c: (c['set'], int(c['number']) if c['number'].isdigit() else 100000, c['name']))
    assert len(cards) == 341 and len(raw) == 611
    for set_code, count in [('TRK', 311), ('SDS', 30)]:
        assert {int(c['number']) for c in cards if c['set'] == set_code} == set(range(1, count + 1))
    apply_editorial_evidence(cards, registry)
    add_new_indices(cards, old)
    doc = {**baseline, 'date': DATE, 'prospectsDate': DATE, 'cards': cards, 'print_count': len(raw), 'source_queries': [raw_doc['source_query']], 'complete': True, 'partial': False, 'catalogScope': 'Identità di gioco TRK 1-311 e SDS 1-30; non certifica la completezza di tutti i trattamenti.', 'printingCoverage': {'complete': False, 'observed': len(raw), 'reason': 'Varianti, promo e finiture non sono una collazione verificata.'}, 'eligibility_note': 'Identità TRK/SDS complete. Nessuna deduzione di probabilità o idoneità di ogni stampa dal solo flag booster.'}
    ratings['date'] = '02/11/2026'
    sources['research'].update(date=DATE, sources=list(registry.values()), catalogSnapshot='research/star-trek-20261102/catalog.json', rawSnapshot='research/star-trek-20261102/scryfall.json', previousCatalogSnapshot='star-trek-cards-20261028.json', newDistinctCards=len(set(grouped) - set(old)), automatedEvaluationsSnapshot='research/star-trek-20261102/standard-constructed-preview.json')
    coverage = {**sources['research']['coverage'], 'catalogCards': len(cards), 'printings': len(raw), 'gameplayProfiles': len(cards), 'specificEditorialNotes': sum(c['name'] in notes for c in cards), 'constructedModelCards': len(models), 'limitedExpertGrades': len(grades), 'limitedReviewAuthors': 1, 'limitedReviewPublications': 7, 'observedWinRates': 0, 'catalogIdentityComplete': True, 'printingTreatmentsComplete': False, 'priceObservationDate': '2026-10-27', 'commanderObservationDate': '2026-10-27'}
    coverage['publishersRead'] = len({r.get('publisher') for r in registry.values() if r.get('status') in ('read', 'ratings_extracted', 'retrieved') and r.get('publisher')})
    sources['research']['coverage'] = coverage
    sources['research']['limitations'] = ['Catalogo delle identità completo, ma censimento di varianti e collazione non certificati completi.', '306 voti Draft attribuiti a un solo autore: non sono consenso multi-autore, WR o voti Sealed.', 'WR Draft e WR Sealed TRK assenti prima dell’apertura degli eventi Arena del 10 novembre.', f'{len(models)} previsioni Constructed automatiche, distinte dalle recensioni strategiche e dai risultati di torneo.', 'Gli indici torneo conservano il campione fino al 28 ottobre; le nuove TRK non hanno risultati post-uscita.', 'Prezzi From Cardmarket del 27 ottobre conservati: 201 carte, nessuna copertura completa delle finiture.', 'Inclusioni EDHREC del 27 ottobre conservate, senza ridatarle o trattarle come risultati cEDH.', 'Commander TRC in appendice separata, senza inserimento nel catalogo o nei pool Limited.']
    sources['research']['latestUpdate'] = {'snapshot': 'research/star-trek-20261102/coverage.json', 'sourceAudit': 'research/star-trek-20261102/source-assessments.json', 'method': 'Confronto delle identità, acquisizione integrale dei voti pubblici, scenari editoriali e limiti distinti per formato.'}
    sources['reviewAnalysis']['latestUpdate'] = {'date': DATE, 'limitedExpertGrades': len(grades), 'source': 'research/star-trek-20261102/limited-reviews.json', 'limitations': 'Le precedenti verifiche del 22 ottobre restano storiche. Recensioni Draft, non partite osservate.'}
    for filename, value in [('cards', doc), ('ratings', ratings), ('sources', sources)]:
        save(BASE / (filename + '.json'), value)
    save(OUT / 'catalog.json', {k: v for k, v in doc.items() if k != '$schema'})
    save(OUT / 'catalog-delta.json', {'date': DATE, 'beforeCards': len(old), 'beforePrintings': baseline['print_count'], 'cards': len(cards), 'printings': len(raw), 'changes': delta})
    save(OUT / 'coverage.json', coverage)
    update_guides(coverage)
    update_metadata(cards, coverage)
    commander_appendix(cards)
    print(json.dumps(coverage, ensure_ascii=False))


def apply_editorial_evidence(cards, registry):
    # Short attributed findings; card names alone are not an endorsement.
    evidence = load(OUT / 'format-observations.json')
    by_name = {c['name']: c for c in cards}
    for record in evidence['cards']:
        card = by_name[record['name']]
        p = card['prospects']
        p.setdefault('researchNotes', [])
        note = {k: v for k, v in record.items() if k != 'name'}
        note['date'] = record['published']
        note['context'] = ', '.join(record['formats']) + ' · ' + registry[record['source']].get('publisher', record['source'])
        p['researchNotes'].append(note)
        p['sources'] = sorted(set(p['sources']) | {record['source']})
        for fmt in record['formats']:
            entry = p['formats'][fmt]
            entry.update(evidence='recensione', prospect='anteprima_da_testare', confidence='bassa')
            entry['editorialObservation'] = note


def add_new_indices(cards, old):
    # Reuse the original measured corpus, without pretending it was refreshed.
    from tournament_index import FORMATS, calculate_index, merge_events, prepare_events, validate_index
    corpus = ROOT / 'research/tournament-prospects-20261028/events'
    events = prepare_events(merge_events([load(p) for p in corpus.glob('*.json')]))
    known_release = {}
    for manifest in load(ROOT / 'expansions.json'):
        for c in load(ROOT / Path(manifest['manifest']).parent / 'cards.json')['cards']:
            if c.get('releasedAt'):
                ident = c.get('oracleId', c['id'])
                known_release[ident] = min(known_release.get(ident, c['releasedAt']), c['releasedAt'])
    for c in cards:
        if c['id'] in old:
            continue
        p = c['prospects']
        for fmt in FORMATS:
            index = calculate_index(c, fmt, events, known_release.get(c['id'], c['releasedAt']), as_of='2026-10-28')
            validate_index(index)
            p['formats'][fmt]['tournamentIndex'] = index
        p['tournamentDate'] = '2026-10-28'
        p['sources'] = sorted(set(p['sources']) | {'official-tournament-corpus-20261028'})


def update_metadata(cards, coverage):
    stats = load(BASE / 'statistics.json')
    stats['catalogDate'] = DATE
    stats['catalog'] = [{'color': color, 'curve': [sum(c['cmc'] == v and color in c['colors'] and not c['land'] for c in cards) for v in range(6)] + [sum(c['cmc'] >= 6 and color in c['colors'] and not c['land'] for c in cards)], 'names': []} for color in 'WUBRG']
    stats['researchAvailability'].update(date=DATE, observedWinRates=False, draftWinRates={'status': 'unavailable', 'reason': 'Nessun campione post-uscita TRK acquisito.'}, sealedWinRates={'status': 'unavailable', 'reason': 'Nessun campione post-uscita TRK acquisito.'})
    save(BASE / 'statistics.json', stats)
    prices = load(BASE / 'prices.json')
    prices['references']['catalogCards'] = len(cards)
    save(BASE / 'prices.json', prices)
    manifest = load(BASE / 'expansion.json')
    manifest['date'] = '2 novembre 2026'
    manifest['description'] = 'Catalogo TRK e SDS, recensioni Draft attribuite, analisi per carta e scenari per formato prima dell’uscita.'
    manifest['assets'] = list(dict.fromkeys(manifest['assets'] + ['research/star-trek-20261102/catalog.json', 'research/star-trek-20261102/commander-appendix.json', 'research/star-trek-20261102/limited-reviews.json']))
    save(BASE / 'expansion.json', manifest)


def update_guides(coverage):
    guide = load(BASE / 'guides.json')
    structured = load(OUT / 'draft-guide.json')
    for key_ in ('pickGuide', 'pickDecisions', 'draftCombos'):
        guide[key_] = structured[key_]
    fragments = guide['fragments']
    fragments['set.copy-0'] = 'ANALISI PRIMA DELL’USCITA / 2 NOVEMBRE 2026'
    fragments['method.copy-1'] = 'Catalogo verificato il 2 novembre 2026: {{cardCount}} identità, {{printingCount}} stampe. Complete le identità TRK 1-311 e SDS 1-30; varianti e collazione restano da certificare. Ogni carta conserva testo, provenienza e collegamento Scryfall.'
    fragments['discovery.copy-1'] = 'Stato Scryfall al 2 novembre; campione torneo fino al 28 ottobre'
    fragments['rules.copy-2'] = 'Per le nuove meccaniche e i chiarimenti per carta sono disponibili le release notes ufficiali del 30 ottobre. Le CR generali collegate conservano la loro data del 25 settembre.'
    fragments['analysis.panel-1'] = '<section class="trk-panel"><h2>Conoscenza del set</h2><p>341 identità, 611 stampe e 306 voti Draft attribuiti a J2SJosh, nelle sette recensioni MTG Arena Zone del 30 ottobre-2 novembre. Catalogo completo delle identità TRK/SDS, con varianti non certificate complete.</p><p>Le recensioni sono previsioni prima dell’uscita. Le WR Draft e Sealed sono ancora N/D. I modelli Constructed, gli indici di torneo fino al 28 ottobre e le inclusioni Commander hanno contesti distinti.</p><div id="trk-statistics"></div></section>'
    fragments['draft.panel-0'] = '<section class="trk-panel"><h2>Preparare Draft e Pick-Two</h2><p>Tre Play Booster a testa: una carta per passaggio nel Draft, due nel Pick-Two. Le 306 recensioni consultabili nel catalogo riguardano il Draft tradizionale; non costituiscono una graduatoria misurata per Pick-Two o Sealed.</p><p>Prima scegli carte efficienti e una curva sostenibile, poi valuta densità e payoff. Creature economiche restano necessarie anche nei mazzi Spacecraft, perché station richiede il loro tap.</p></section>'
    fragments['simulator.panel-0'] = '<section class="trk-panel"><h2>Apertura delle buste</h2><p>Le identità del catalogo sono complete. L’apertura fedele resta in attesa della verifica delle stampe ammesse e delle ambiguità di collazione pubblicate. Il catalogo da solo non determina una ricetta Play Booster.</p></section>'
    fragments['gallery.strategy'] = (OUT / 'sealed-guide.html').read_text(encoding='utf-8')
    guide['sealed'] = True
    fragments['draft.examples'] = fragments['draft.examples'].replace('Ipotesi editoriali sul catalogo parziale del 27 ottobre, senza voti o risultati Limited.', 'Piani editoriali aggiornati sul catalogo del 2 novembre. Le recensioni Draft sono disponibili; mancano risultati Limited osservati.')
    fragments['method.panel-1'] = '<section class="trk-panel"><h2>Copertura e limiti</h2><p>{{fragment:method.copy-1}}</p><ul><li>Recensioni Draft: tutte le 306 carte TRK non base, un solo autore. Le 30 SDS non ricevono voti da queste recensioni.</li><li>WR Draft e Sealed: assenti. Le carte nuove non hanno ancora risultati agonistici dopo l’uscita.</li><li>Cardmarket: 201 minimi From, rilevati il 27 ottobre, senza copertura completa delle finiture. Nessun valore atteso del box.</li><li>Commander: appendice distinta dai pool Limited, con provenienza e limiti propri.</li></ul><p><a href="catalog.json" download>Catalogo aggiornato</a> · <a href="limited-reviews.json" download>Voti Draft e provenienza</a> · <a href="commander-appendix.json" download>Appendice Commander aggiornata</a></p></section>'
    # Keep the prior dated findings accessible, but put current evidence first.
    prior = fragments['method.panel-0']
    if '<!-- research-20261102 -->' in prior:
        prior = prior.split('<!-- research-20261102-end -->', 1)[1]
    registry = {r['id']: r for r in load(OUT / 'source-assessments.json')['sources']}
    selected = ['wizards-release-trk', 'wizards-commander-lists', 'cardsrealm-standard-trk', 'cardsrealm-pauper-trk', 'rocks-best-trk'] + ['arenazone-trk-' + color for color in ('white', 'blue', 'black', 'red', 'green', 'multicolor', 'artifacts-and-lands')]
    links = ''.join('<li><a href="' + html.escape(registry[k]['url'], quote=True) + '" target="_blank" rel="noopener">' + html.escape(registry[k].get('publisher', k) + ': ' + k.replace('arenazone-trk-', 'Draft ')) + '</a></li>' for k in selected)
    fragments['method.panel-0'] = '<!-- research-20261102 --><section class="trk-panel"><h2>Ricerca del 2 novembre</h2><p>Fonti ufficiali, recensioni Draft e prospettive per formato, con contesti e limiti separati. Le analisi precedenti riportate sotto conservano le loro date.</p><ul>' + links + '</ul><p><a href="catalog.json" download>Scarica il catalogo aggiornato</a>.</p></section><!-- research-20261102-end -->' + prior
    guide['researchUpdate'] = {'date': DATE, 'coverage': coverage, 'report': 'research/star-trek-20261102/README.md'}
    fragments['pick-guide-section.copy-0'] = ' Valutazioni editoriali prima dell’uscita: controlla colori, curva e supporto. Le recensioni attribuite sono nel catalogo; le WR sono N/D.'
    fragments['pick-guide-section.copy-1'] = 'Scegli il ruolo che manca al mazzo. Una terra utile, una creatura economica o una risposta possono valere più di un ulteriore payoff senza supporto.'
    fragments['pick-guide-section.sources-0'] = '<p>Sequenze verificate sui testi Oracle del 2 novembre e sulle release notes ufficiali del 30 ottobre. Ipotesi strategiche editoriali, senza frequenze di vittoria misurate.</p>'
    save(BASE / 'guides.json', guide)


def commander_appendix(main_cards):
    raw = load(OUT / 'scryfall-commander.json')
    grouped = {}
    for p in raw['data']:
        grouped.setdefault(p['oracle_id'], []).append(p)
    main = {c['id']: c for c in main_cards}
    rows = []
    for ident, prints in grouped.items():
        p = min(prints, key=lambda r: (not r['collector_number'].isdigit(), int(r['collector_number']) if r['collector_number'].isdigit() else 100000))
        row = {'oracleId': ident, 'name': p['name'], 'set': p['set'].upper(), 'number': p['collector_number'], 'mana': p.get('mana_cost', ''), 'type': p['type_line'], 'text': p.get('oracle_text', ''), 'legalities': p['legalities'], 'url': p['scryfall_uri'].split('?')[0], 'prints': [r['collector_number'] for r in prints], 'scope': 'commander_appendix', 'sources': ['scryfall-commander-20261102', 'wizards-commander-lists'], 'analysisCoverage': 'catalog_and_product_scope', 'tournamentResults': None, 'cedhResults': None, 'price': None, 'limitations': ['Catalogo e testo acquisiti. Nessuna analisi agonistica individuale o quotazione aggiunta per questa identità TRC.']}
        if ident in main:
            row['mainCatalogId'] = ident
            row['sharedGameplayAssessment'] = main[ident]['prospects']['gameplayReview']['finding']
        rows.append(row)
    save(OUT / 'commander-appendix.json', {'date': DATE, 'source_query': raw['source_query'], 'catalogCards': len(rows), 'printings': len(raw['data']), 'complete': False, 'scope': 'Tutte le pagine Scryfall TRC disponibili, separate dal Limited. Non equivale a recensioni complete dei quattro precon.', 'cards': sorted(rows, key=lambda r: int(r['number']) if r['number'].isdigit() else 100000), 'deckAnalysis': load(OUT / 'commander-decks.json')})


if __name__ == '__main__':
    main()
