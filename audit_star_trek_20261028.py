"""Apply the verified corrections from the complete Star Trek data audit.

Offline and idempotent. Raw historical captures remain unchanged. Run after
enrich_star_trek_20261028.py; that importer also invokes this correction layer.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'expansions/star-trek'
OUT = ROOT / 'research/star-trek-20261028-audit'
DATE = '2026-10-28'

PROFILES = {
    'Emergency Medical Hologram': 'Costa un mana bianco. All’ingresso mette un segnalino su una creatura bersaglio, anche avversaria o su se stesso, e fa guadagnare una vita. Con Open Communications dal cimitero spendi quattro mana totali per riprenderlo e rilanciarlo. L’innescata richiede un bersaglio legale per risolvere.',
    'Federation Probe': 'Il corpo 1/1 volante costa un mana blu. All’ingresso scegli fra sorvegliare 1 e dare +1/+1 fino a fine turno a una creatura bersaglio, compresa la Probe stessa o una creatura avversaria. Con Miles O’Brien puoi riusare l’ingresso; il punteggio automatico Constructed non prova un primo pick assoluto.',
    'Peace in Our Time': 'All’inizio del combattimento di ogni giocatore, quel giocatore può pescare rinunciando ad attaccare nel turno: la scelta riguarda anche te. Ciascuna accettazione aggiunge un segnalino pace, ma non garantisce la vittoria: servono almeno dodici segnalini alla tua manutenzione e l’incantesimo deve restare sul campo.',
    'Borg Cube': 'L’affinità conta creature artefatto, non artefatti generici o normali Tesori. All’ingresso normalmente esilia una creatura; un attacco successivo può assimilare una carta creatura esiliata con quella stessa nave. Se lascia il campo e rientra è un nuovo oggetto: perde il collegamento alle carte esiliate dalla sua esistenza precedente (CR 400.7 e 607).',
    'Amok Time': 'Il primo capitolo fa lottare una tua creatura bersaglio con fino a una creatura bersaglio avversaria. Il secondo fa guadagnare tre vite e il terzo recupera una carta creatura dal tuo cimitero in mano. La Saga non fa pescare: la menzione della sottofase di acquisizione nel promemoria indica quando aggiungere un segnalino sapere.',
    'Genesis Effect': 'Per {4}{R}, infligge sei danni a una creatura bersaglio e distrugge una tua terra bersaglio, poi crea New Planet tappata che produce qualsiasi colore. Per lanciarla servono entrambi i bersagli. Il nome diverso può aiutare strange new worlds, ma la nuova terra non fornisce mana immediatamente.',
}

TEXT_FIXES = {
    'Jett Reno, Problem Solver': ('+1/1 counter', '+1/+1 counter', '67.jpg'),
    'Mirror Universe Intrusion': ('pay an additional 4 as', 'pay an additional {4}{U}{B} as', '248.jpg'),
}


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def correct():
    OUT.mkdir(exist_ok=True)
    doc = load(BASE / 'cards.json')
    cards = doc['cards']
    ratings = load(BASE / 'ratings.json')
    sources = load(BASE / 'sources.json')
    raw = load(OUT / 'scryfall-verification.json')['data']
    by_id = {c['id']: c for c in cards}
    corrections = []
    for c in cards:
        if c['name'] in PROFILES:
            finding = PROFILES[c['name']]
            c['prospects']['summary'] = finding
            c['prospects']['gameplayReview'].update(finding=finding, checked=DATE)
            ratings['cards'][c['id']]['why'] = finding
            if c['name'] in ('Borg Cube', 'Emergency Medical Hologram'):
                c['prospects']['sources'] = sorted(set(c['prospects']['sources']) | {'comprehensive-rules'})
        if c['name'] in TEXT_FIXES:
            before, after, image = TEXT_FIXES[c['name']]
            c['text'] = c['text'].replace(before, after)
            c['oracle'] = c['text']
            c['prospects']['oracle']['text'] = c['text']
            printing = next(p for p in raw if p['oracle_id'] == c['id'] and p['collector_number'] == c['number'])
            observation = {'date': DATE, 'field': 'text', 'source': 'printed-card-proofreading', 'sourceUrl': printing['image_uris']['normal'], 'evidence': str((OUT / image).relative_to(ROOT)).replace('\\', '/'), 'rawValue': before, 'correctedValue': after, 'kind': 'snapshot_transcription_correction', 'note': 'Correzione locale del refuso nella trascrizione Scryfall, verificata sull’immagine della carta. Non è un’errata ufficiale.'}
            c['catalogCorrections'] = [observation]
            corrections.append({'id': c['id'], 'name': c['name'], **observation})
            c['prospects']['sources'] = sorted(set(c['prospects']['sources']) | {'printed-card-proofreading'})
        if c['name'] == 'Culber and Stamets, Star-Crossed':
            c['type'] = 'Legendary Creature : Human Doctor Artificer'
            observation = {'date': DATE, 'field': 'type', 'source': 'printed-card-proofreading', 'rawValue': 'Legendary Creature Human Doctor Artificer', 'correctedValue': c['type'], 'evidence': 'research/star-trek-20261028-audit/191.jpg', 'kind': 'type_separator_normalization'}
            c['catalogCorrections'] = [observation]
            c['prospects']['sources'] = sorted(set(c['prospects']['sources']) | {'printed-card-proofreading'})
            corrections.append({'id': c['id'], 'name': c['name'], **observation})
    registry = {r['id']: r for r in sources['research']['sources']}
    registry['printed-card-proofreading'] = {'id': 'printed-card-proofreading', 'publisher': 'Wizards of the Coast (immagini delle carte distribuite da Scryfall)', 'label': 'Immagini delle carte: riscontro dei refusi di trascrizione', 'url': 'https://magic.wizards.com/en/products/star-trek/card-image-gallery', 'kind': 'printed-card-image', 'retrieved': DATE, 'checked': DATE, 'limitations': ['Riscontro visivo delle immagini archiviate per le tre anomalie individuate; nessuna nuova errata ufficiale attribuita a Wizards.']}
    registry['comprehensive-rules'] = {'id': 'comprehensive-rules', 'publisher': 'Wizards of the Coast', 'label': 'Comprehensive Rules, 25 settembre 2026', 'kind': 'official-rules', 'url': 'https://media.wizards.com/2026/downloads/MagicCompRules%2020260925.txt', 'retrieved': DATE, 'checked': DATE}
    registry['scg-gallery']['label'] = 'Star City Games: galleria delle anteprime Star Trek'
    for ident in ('preview-calendar', 'regional-delays', 'scg-delays', 'spotlight', 'design-interview', 'arena-calendar'):
        registry[ident]['checked'] = DATE
    registry['wizards-mechanics']['authors'] = ['Matt Tabak']
    registry['wizards-collecting']['authors'] = ['Zakeel Gordon', 'Jubilee Finnegan']
    sources['reviewAnalysis']['rulesSource']['checked'] = DATE
    sources['research']['sources'] = list(registry.values())
    coverage = sources['research']['coverage']
    coverage.update(catalogCards=len(cards), gameplayProfiles=len(cards), specificEditorialNotes=78)
    sources['research']['dataAudit'] = {'date': DATE, 'scope': 'Tutti i 16 documenti attivi Star Trek, 265 identità, 495 stampe e osservazioni storiche collegate.', 'report': 'research/star-trek-20261028-audit/README.md', 'corrections': corrections, 'historicalCaptures': 'Le acquisizioni grezze datate restano inalterate. Il catalogo attivo e lo snapshot esportato del 28 ottobre includono le correzioni documentate.', 'priceObservationDate': '2026-10-27', 'commanderObservationDate': '2026-10-27'}
    sources['research']['dataAudit']['rulesReferences'] = [
        {'url': 'https://magic.wizards.com/en/rules', 'checked': DATE, 'finding': 'La pagina ufficiale collega ancora le CR del 25 settembre 2026.'},
        {'url': sources['reviewAnalysis']['rulesSource']['url'], 'checked': DATE, 'sections': ['100.2b', '100.4b', '103.5', '400.7', '603.3d', '607', '702.184', '721']},
        {'url': 'https://media.wizards.com/ContentResources/WPN/MTG_MTR_2026_Feb27_EN.pdf', 'checked': DATE, 'sections': ['7.1', '7.2', '7.3', '7.7']},
    ]
    guides = load(BASE / 'guides.json')
    fragments = guides['fragments']
    fragments['discovery.copy-1'] = 'Stato Scryfall al 28 ottobre'
    fragments['method.copy-1'] = 'Catalogo verificato il 28 ottobre 2026: {{cardCount}} carte distinte, {{printingCount}} stampe. Catalogo TRK e SDS incompleto. Le correzioni locali di trascrizione sono documentate nei dati; ogni carta conserva il collegamento Scryfall.'
    fragments['analysis.panel-1'] = fragments['analysis.panel-1'].replace('248 carte e 462 stampe al 27 ottobre 2026', '265 carte e 495 stampe al 28 ottobre 2026').replace('210 previsioni', '231 previsioni')
    fragments['analysis.panel-0'] = fragments['analysis.panel-0'].replace(' La soglia di vendita prevista è strettamente &gt;0,10 €.', '')
    fragments['analysis.panel-0'] = fragments['analysis.panel-0'].replace('Le frequenze seguenti si riferiscono a ciascuno slot indicato.', 'Le tabelle riportano le percentuali della fonte per i gruppi e gli slot indicati; l’ambito comune/noncomune resta da chiarire.')
    panel = fragments['method.panel-0']
    panel = panel.replace('href="star-trek-cards-20261027.json"', 'href="star-trek-cards-20261028.json"')
    panel = panel.replace('Aggiornamenti verificati il 27 ottobre 2026', 'Aggiornamenti verificati il 28 ottobre 2026')
    panel = panel.replace('248 carte distinte TRK/SDS e 462 stampe, 55 carte in più dello snapshot del 22 ottobre', '265 carte distinte TRK/SDS e 495 stampe, 17 carte in più dello snapshot del 27 ottobre')
    panel = panel.replace('Verifica aggiornata al 27 ottobre 2026', 'Verifica aggiornata al 28 ottobre 2026')
    panel = panel.replace('Copertura della ricerca del 27 ottobre', 'Copertura della ricerca del 28 ottobre')
    panel = panel.replace('248 profili Oracle, 210 previsioni automatiche Constructed', '265 profili Oracle, 231 previsioni automatiche Constructed')
    panel = panel.replace('osservazioni EDHREC per 238 carte e 201 minimi Cardmarket.', 'osservazioni EDHREC per 238 carte e 201 minimi Cardmarket, entrambi rilevati il 27 ottobre.')
    panel = panel.replace('Scarica i dati di collazione', 'Scarica la rilevazione storica dei prodotti del 21 ottobre')
    panel = panel.replace('Scarica l’analisi con fonti, punteggi e osservazioni per carta', 'Scarica l’analisi storica del 22 ottobre')
    fragments['method.panel-0'] = panel
    fragments['method.panel-1'] = fragments['method.panel-1'].replace('Prezzi: nessun valore EUR negli snapshot. Nessun minimo Cardmarket verificato in questa rilevazione.', 'Prezzi: 201 carte hanno un minimo Cardmarket in euro rilevato il 27 ottobre, senza filtro di finitura. Le 17 nuove carte non hanno una rilevazione di prezzo. Copertura parziale, nessun valore atteso del box disponibile.')
    # Both containers are retained for compatibility and must describe the same rules.
    for container in (fragments, guides['rules']):
        key = 'rules.panel-1'
        container[key] = container[key].replace('aggiungere un segnalino e renderla', 'aggiungere un segnalino +1/+1 e renderla')
    # Synchronize the older card-level aliases used by catalog consumers.
    for c in cards:
        rating = ratings['cards'][c['id']]
        for field in ('role', 'why', 'condition'):
            c[field] = rating.get(field, '')
    for filename, value in [('cards', doc), ('ratings', ratings), ('guides', guides), ('sources', sources)]:
        save(BASE / (filename + '.json'), value)
    save(ROOT / 'star-trek-cards-20261028.json', {k: v for k, v in doc.items() if k != '$schema'})
    save(ROOT / 'research/star-trek-20261028/coverage.json', coverage)
    save(OUT / 'corrections.json', {'date': DATE, 'profileCorrections': PROFILES, 'catalogCorrections': corrections})
    return by_id


def verify(cards):
    market = load(ROOT / 'research/star-trek-20261027/cardmarket-normalized.json')
    edh = load(ROOT / 'research/star-trek-20261027/edhrec-set-observations.json')
    models = load(ROOT / 'research/star-trek-20261028/standard-constructed-preview.json')
    errors = []
    counts = {'cards': len(cards), 'prices': 0, 'priceVariants': 0, 'commanderRows': 0, 'constructedModels': 0}
    for ident, c in cards.items():
        p = c['prospects']
        reading = market['primary'].get(ident)
        if p['price']['from'] != (reading['from'] if reading else None):
            errors.append([c['name'], 'price'])
        if reading:
            counts['prices'] += 1
            if p['price'].get('sourceReading') != reading or p['price']['date'] != '2026-10-27':
                errors.append([c['name'], 'price provenance'])
        if p['price']['variants'] != market['variants'].get(ident, []):
            errors.append([c['name'], 'price variants'])
        counts['priceVariants'] += len(p['price']['variants'])
        expected_edh = [r for r in edh['rows'] if r.get('catalogId') == ident]
        if p['commanderObservations'] != expected_edh:
            errors.append([c['name'], 'commander provenance'])
        counts['commanderRows'] += len(expected_edh)
        model = next((r for r in models['cards'] if r['catalogId'] == ident), None)
        if model:
            counts['constructedModels'] += 1
            actual = p['automatedEvaluations'][0]
            if any(actual[k] != v for k, v in model.items()):
                errors.append([c['name'], 'model'])
        for fmt, value in p['formats'].items():
            if fmt not in ('draft', 'sealed', 'pick_two') and value['legality'] != c['legalities'].get('commander' if fmt == 'cedh' else fmt, 'unknown'):
                errors.append([c['name'], 'legality', fmt])
    save(OUT / 'observation-check.json', {'date': DATE, 'counts': counts, 'errors': errors})
    if errors:
        raise ValueError(errors)
    print(json.dumps(counts))


if __name__ == '__main__':
    verify(correct())
