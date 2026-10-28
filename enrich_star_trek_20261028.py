"""Integrate the 28 October captures offline, preserving dated market/EDHREC evidence.

First run refresh-star-trek-20261028.py and research_star_trek_20261028.py.
Reproduction: rerun the refresh with --from-snapshot, then this script.
"""
import copy
import json
import tempfile
from pathlib import Path

import enrich_star_trek_20261027 as helpers

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'expansions/star-trek'
OUT = ROOT / 'research/star-trek-20261028'
DATE = '2026-10-28'

# Original editorial assessments of the newly acquired Oracle texts, without grades.
NOTES = {
    'Andromedan Automatons': ('Corpi e copie', 'Cerca altre copie dello stesso nome e le mette in mano, senza lanciarle gratis. In Limited il vantaggio dipende dalle copie effettivamente raccolte: una sola copia non trova rinforzi.'),
    'Federation Resupply': ('Ricerca e riutilizzo', 'Per {1}{W} cerca un’Aura, un Equipaggiamento o una Spacecraft e la mette in mano. Richiede poi il mana per lanciarla; beam me up permette un secondo uso dal cimitero pagando {3}{W} e riprendendo una propria creatura.'),
    'The Measure of a Man': ('Esilio temporaneo e Indizio', 'Il primo capitolo esilia fino a un artefatto o una creatura non pedina; il terzo restituisce la carta sotto il controllo del proprietario. È interazione temporanea o un modo per riutilizzare un ingresso, con un Indizio nel mezzo che richiede altri due mana per pescare.'),
    'Sulu, Space Swashbuckler': ('Equipaggiamenti e navi', 'Attacco improvviso aiuta in combattimento. Per pescare quando Sulu viene tappato serve che un Equipaggiamento o una Spacecraft sia già entrato sotto il tuo controllo in quel turno; station può tapparlo senza attaccare, ma richiede una nave e tempi da stregoneria.'),
    'Starfleet Spanner Jockey': ('Magie prima dell’attacco', 'Difensore limita gli attacchi finché non lanci una magia non creatura nel turno. La condizione permette di attaccare, senza dare rapidità o eliminare il bisogno di mantenere una buona densità di magie di supporto.'),
    'Suus Mahna Practitioner': ('Controllo dei bloccanti', 'L’abilità tappa una creatura e costa {4}{U} più il tap. Strange new worlds riduce solo la parte generica in base ai nomi diversi delle terre: restano almeno {U} e il tap; cinque terre con lo stesso nome riducono di uno.'),
    'De-evolve': ('Neutralizzazione parziale', 'Per {1}{B} toglie quattro punti di forza e impedisce di bloccare, senza rimuovere le abilità della creatura. Con almeno sette carte nel tuo cimitero, l’innescata al mantenimento può esiliarla: prima della soglia resta sul campo.'),
    'Sela, Tal Shiar Paradox': ('Carte che lasciano il cimitero', 'Attaccando puoi esiliare fino a una carta da un cimitero. Per creare il Romulano 2/2 tappato deve uscire una carta dal tuo cimitero: esiliare quella avversaria non basta. Uscite simultanee di più carte producono una sola innescata.'),
    '"Assault on Area 51"': ('Morti e danno progressivo', 'Ogni creatura che muore aggiunge un segnalino missione e fa perdere vita all’avversario bersagliato. Dalla settima in poi la perdita è di due: servono morti effettive, non soltanto sacrifici di artefatti non creatura.'),
    'Genesis Effect': ('Rimozione e terra sostitutiva', 'Per {4}{R}, infligge sei danni a una creatura e distrugge una tua terra, poi crea New Planet tappata che produce qualsiasi colore. Il nome diverso può aiutare strange new worlds, ma non recuperi mana immediatamente e la magia richiede un bersaglio creatura legale.'),
    'Sarcophagus, Ship of the Dead': ('Pressione e morti', 'Potenzia le altre tue creature di +1/+0 anche mentre è solo un artefatto. Le morti aggiungono cariche soltanto finché non è una creatura; a dieci cariche diventa una minaccia volante. Station richiede di rinunciare al tap di un’altra creatura.'),
    'Culber and Stamets, Star-Crossed': ('Dilemma e mana', 'All’ingresso scegli fra un segnalino +1/+1 su una creatura bersaglio e due mana di un solo colore. Il mana può sostenere una seconda giocata nello stesso turno, senza restare disponibile per i turni successivi.'),
    'Dr. Leonard "Bones" McCoy': ('Recupero e protezione', 'Lampo permette di scegliere il momento dell’ingresso. Un modo recupera in mano un permanente non Doctor; l’altro prepara il ritorno di un’altra creatura solo se muore in quel turno, alla prossima sottofase finale. Non protegge dall’esilio.'),
    'Saru, Unthreatened': ('Protezione con lampo', 'Può entrare in risposta a una rimozione e dare anti-malocchio a un’altra tua creatura fino a fine turno. Non protegge se stesso con l’innescata e non ferma effetti che non bersagliano.'),
    'Dathon, His Heart Open': ('Incantesimi e Saghe', 'Fa pescare quando lanci un incantesimo; una Saga aggiunge anche due danni a ogni avversario. L’abilità da due mana aggiunge un segnalino del tipo già presente su un tuo incantesimo, solo come stregoneria: il piano richiede densità e tre colori affidabili.'),
    'Nog, Ambitious Cadet': ('Crescita e terre dal cimitero', 'Il primo investimento da {1} lo rende Scout 3/4 e aggiunge sorvegliare 2 quando viene tappato. Solo dopo puoi pagare {3} per renderlo Officer e giocare terre dal cimitero, con una terra aggiuntiva per turno. I passaggi richiedono mana oltre al costo iniziale.'),
    'Class-F Shuttlecraft': ('Fixing e nave', 'Per tre mana offre una fonte di qualsiasi colore, utile per magie successive. A sei cariche ottiene volare e cautela come creatura; station costa il tap di un’altra creatura. Diventare creatura rende rilevante la debolezza da evocazione per la sua abilità di mana con tap.'),
}


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    doc = load(BASE / 'cards.json')
    cards = doc['cards']
    previous = load(ROOT / 'star-trek-cards-20261027.json')
    old = {c['id']: c for c in previous['cards']}
    raw = load(ROOT / 'star-trek-scryfall-20261028.json')['data']
    helpers.DATE = DATE
    helpers.OUT = OUT
    helpers.CACHE = Path(tempfile.gettempdir()) / 'mtg-star-trek-research-20261028'
    scores_doc = helpers.standard_capture(cards, raw)
    if scores_doc['unmatchedNames']:
        raise ValueError(scores_doc['unmatchedNames'])
    scores = {r['catalogId']: r for r in scores_doc['cards']}
    template = next(c['prospects'] for c in cards if c['set'] == 'TRK' and c['rarity'] == 'common' and 'prospects' in c)
    ratings = load(BASE / 'ratings.json')
    new_cards, changed = [], []
    for card in cards:
        is_new = card['id'] not in old
        if is_new:
            new_cards.append({'id': card['id'], 'name': card['name'], 'set': card['set'], 'number': card['number']})
            role, finding = NOTES[card['name']]
            p = copy.deepcopy(template)
            for field in ('automatedEvaluations', 'researchNotes'):
                p.pop(field, None)
            p.update(summary=finding, gameplayReview={'kind': 'analisi_editoriale_oracle', 'finding': finding, 'evidenceOfTournamentSuccess': False}, sources=['scryfall-api', 'wizards-collecting', 'wizards-mechanics'], commanderObservations=[], tournamentObservations=[])
            # Empty price record, with no inherited product identity or stale amount.
            price = {k: copy.deepcopy(v) for k, v in template['price'].items() if k in ('currency', 'metric', 'metricLabel', 'sourceLabel', 'source', 'finishFilter', 'outlook', 'methodNote', 'coverageNote')}
            price.update(date=None, printingId=None, set=card['set'].lower(), number=card['number'], **{'from': None}, nonfoil=None, foil=None, variants=[], printingMatch=None, comparison={'date': '2026-10-27', 'samePrinting': None, 'nonfoil': None, 'from': None, 'changePct': None, 'status': 'missing_reference'})
            price['coverageNote'] = 'Nessuna osservazione Cardmarket acquisita per questa carta; prezzo e finiture non disponibili.'
            p['price'] = price
            card['prospects'] = p
            ratings['cards'][card['id']] = {'role': role, 'why': finding, 'condition': 'Profilo editoriale preliminare, senza voto Limited o risultati osservati.'}
        p = card['prospects']
        if not is_new:
            fields = [f for f in ('name', 'text', 'mana', 'type', 'rarity', 'legalities', 'number') if old[card['id']].get(f) != card.get(f)]
            if fields:
                changed.append({'id': card['id'], 'name': card['name'], 'fields': fields, 'before': {f: old[card['id']].get(f) for f in fields}, 'after': {f: card.get(f) for f in fields}})
        printing = next(r for r in raw if r['oracle_id'] == card['id'] and r['set'].upper() == card['set'] and r['collector_number'] == card['number'])
        p['oracle'] = {'printingId': printing['id'], 'url': card['url'], 'set': printing['set'], 'number': card['number'], 'manaCost': card['mana'], 'text': card['text']}
        p['date'] = DATE
        for fmt, entry in p['formats'].items():
            if fmt in ('draft', 'sealed', 'pick_two'):
                continue
            legality = card['legalities'].get('commander' if fmt == 'cedh' else fmt, 'unknown')
            entry['legality'] = legality
            entry['note'] = entry['note'].replace('27 ottobre 2026', '28 ottobre 2026')
            if is_new:
                entry['evidence'] = 'non_documentata'
                entry['note'] = 'Stato Scryfall del 28 ottobre 2026; nessun risultato di torneo verificato.'
                entry.pop('releaseEligibility', None)
                if card['set'] == 'TRK' and legality not in ('banned', 'restricted') and (fmt in ('standard', 'pioneer', 'modern', 'legacy', 'vintage', 'commander', 'duel') or fmt == 'pauper' and card['rarity'] == 'common'):
                    entry['releaseEligibility'] = {'date': '2026-11-13', 'status': 'legal', 'source': 'wizards-collecting', 'kind': 'previsione_di_ammissibilita'}
        if card['id'] in scores:
            p['automatedEvaluations'] = [{**scores[card['id']], 'source': 'standard-preview-ratings', 'kind': 'automated_constructed_preview', 'retrieved': DATE, 'context': 'Constructed, prima dell’uscita'}]
            p['sources'] = sorted(set(p['sources']) | {'standard-preview-ratings', 'standard-method'})
        else:
            p.pop('automatedEvaluations', None)
    sources = load(BASE / 'sources.json')
    registry = {r['id']: r for r in sources['research']['sources']}
    audit = load(OUT / 'source-audit.json')
    for record in audit['sources']:
        prior = registry.get(record['id'], {})
        registry[record['id']] = {**prior, **record, 'label': prior.get('label', record['publisher']), 'checked': DATE}
    registry['untapped-pick-order'].update(status='no_set_data', finding='La pagina Pick Order TRK restituisce Error - Totally Lost; nessun ranking acquisito.')
    registry['cardmarket-spoiler']['finding'] = 'Richiesta HTTP del 28 ottobre rifiutata (403). Prezzi conservati dalla cattura browser del 27 ottobre, senza ridatarli.'
    registry['scryfall-api'].update(retrieved=DATE, checked=DATE)
    sources['research'].update(date=DATE, catalogSnapshot='star-trek-cards-20261028.json', rawSnapshot='star-trek-scryfall-20261028.json', previousCatalogSnapshot='star-trek-cards-20261027.json', automatedEvaluationsSnapshot='research/star-trek-20261028/standard-constructed-preview.json', newDistinctCards=len(new_cards), sources=list(registry.values()))
    coverage = sources['research']['coverage']
    coverage.update(catalogCards=len(cards), printings=len(raw), gameplayProfiles=len(cards), constructedModelCards=len(scores), specificEditorialNotes=60 + len(NOTES), priceObservationDate='2026-10-27', commanderObservationDate='2026-10-27')
    sources['research']['limitations'] = [s.replace('210 previsioni', f'{len(scores)} previsioni') for s in sources['research']['limitations']]
    sources['research']['limitations'].append('Prezzi Cardmarket e osservazioni EDHREC conservano la data del 27 ottobre. Le 17 nuove carte non ereditano prezzi, liste o risultati dalle altre carte.')
    sources['research']['limitations'] = list(dict.fromkeys(sources['research']['limitations']))
    sources['collation']['verified'] = DATE
    stats = load(BASE / 'statistics.json')
    stats['catalogDate'] = DATE
    stats['catalog'] = [{'color': color, 'curve': [sum(c['cmc'] == v and color in c['colors'] and 'Land' not in c['type'] for c in cards) for v in range(6)] + [sum(c['cmc'] >= 6 and color in c['colors'] and 'Land' not in c['type'] for c in cards)], 'names': []} for color in 'WUBRG']
    stats['researchAvailability']['date'] = DATE
    prices = load(BASE / 'prices.json')
    prices['references']['catalogCards'] = len(cards)
    manifest = load(BASE / 'expansion.json')
    manifest['date'] = '28 ottobre 2026'
    manifest['assets'] = list(dict.fromkeys(manifest['assets'] + ['star-trek-cards-20261028.json']))
    guides = load(BASE / 'guides.json')
    guides['fragments']['set.copy-0'] = 'ANTEPRIMA / 28 OTTOBRE 2026'
    doc['prospectsDate'] = DATE
    ratings['date'] = '28/10/2026'
    for filename, value in [('cards', doc), ('ratings', ratings), ('sources', sources), ('statistics', stats), ('prices', prices), ('expansion', manifest), ('guides', guides)]:
        save(BASE / (filename + '.json'), value)
    save(ROOT / 'star-trek-cards-20261028.json', {k: v for k, v in doc.items() if k != '$schema'})
    save(OUT / 'editorial-notes.json', {name: {'role': role, 'finding': finding} for name, (role, finding) in NOTES.items()})
    save(OUT / 'coverage.json', coverage)
    save(OUT / 'catalog-delta.json', {'date': DATE, 'previousDate': '2026-10-27', 'newCards': new_cards, 'changedCards': changed, 'previousCards': len(old), 'cards': len(cards), 'previousPrintings': previous['print_count'], 'printings': len(raw)})
    import audit_star_trek_20261028 as audit
    audit.verify(audit.correct())
    print(json.dumps(load(BASE / 'sources.json')['research']['coverage'], ensure_ascii=False))


if __name__ == '__main__':
    main()
