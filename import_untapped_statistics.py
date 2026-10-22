"""Normalize a dated capture of the public Untapped Card Data DOM, offline.

The input records only rendered table cells, including their lock state.
Never downloads data or attempts to unlock Premium statistics.
"""
import argparse
import hashlib
import json
from pathlib import Path

from statistics_data import validate_external_statistics

METRICS = {
    'avgLastOffered': {'label': 'Avg Last Offered', 'unit': 'pick', 'status': 'public'},
    'inHandWinRate': {'label': 'In Hand WR', 'unit': 'percent', 'status': 'public'},
    'inHandWinRateDelta': {'label': 'In Hand WR Δ', 'unit': 'percent', 'status': 'locked'},
    'inOpeningHandWinRate': {'label': 'In Opening Hand WR', 'unit': 'percent', 'status': 'public'},
    'playedWinRate': {'label': 'Played WR', 'unit': 'percent', 'status': 'locked'},
    'includedWinRate': {'label': 'Included WR', 'unit': 'percent', 'status': 'suspect'},
    'games': {'label': 'Games', 'unit': 'games', 'status': 'public'},
}


def normalize(capture, catalog, input_hash):
    if capture['headers'] != ['Card'] + [m['label'] for m in METRICS.values()]:
        raise ValueError('Colonne della fonte cambiate: controllare il parser')
    names = {}
    for card in catalog:
        for name in {card['name'], card.get('full', card['name'])}:
            if name in names and names[name]['id'] != card['id']:
                raise ValueError('Nome ambiguo nel catalogo: ' + name)
            names[name] = card
    rows = []
    for source in capture['rows']:
        card = names[source['name']]
        if len(source['cells']) != len(METRICS) + 1:
            raise ValueError('Numero colonne non valido: ' + source['name'])
        values, display = {}, {}
        for (metric, definition), cell in zip(METRICS.items(), source['cells'][1:]):
            if cell['locked'] != (definition['status'] == 'locked'):
                raise ValueError('Accessibilità della metrica cambiata: ' + metric)
            raw = cell['text'].strip()
            display[metric] = raw
            value = None
            if not cell['locked'] and raw not in ('', '–', '-'):
                number = raw.replace(',', '').removesuffix('%')
                value = int(number) if definition['unit'] == 'games' else float(number)
            values[metric] = value
        rows.append({'catalogId': card['id'], 'name': source['name'],
                     'sourceCardId': source['url'].split('/')[3],
                     'sourceUrl': 'https://mtga.untapped.gg' + source['url'],
                     'metrics': values, 'display': display})
    rows.sort(key=lambda row: row['catalogId'])
    observed = {row['catalogId'] for row in rows}
    snapshot = {
        'schemaVersion': 1, 'provider': capture['source'], 'url': capture['url'],
        'retrieved': capture['retrieved'], 'filters': capture['filters'],
        'sourceUpdatedLabel': capture['updatedLabel'],
        'totalMatchesDisplay': capture['totalMatchesDisplay'],
        'totalMatchesApproximate': int(capture['totalMatchesDisplay'].replace(',', '')),
        'rateUnit': 'percent', 'countsPrecision': 'source_display_rounded',
        'inputSha256': input_hash, 'metrics': METRICS,
        'limitations': [
            'Campione Arena Premier Draft, ultimo evento, Bronze–Platinum e tutti gli archetipi; non rappresenta Sealed, Pick-Two o draft cartacei.',
            'Le date iniziale e finale del filtro Latest Event non sono esposte nella tabella acquisita.',
            'Partite e totale sono trascritti con la precisione mostrata dalla fonte; Games non è il denominatore documentato di ciascuna WR.',
            'Valori assenti (trattino) e metriche Premium bloccate restano null. Nessun valore è stimato.',
            'Included WR è 0% in tutte le righe di questo snapshot: conservato letteralmente, marcato suspect e da escludere dalle valutazioni finché non verificato.',
            'Le metriche non sono mediate con 17Lands e non aggiornano voti editoriali, baseline o replay.',
        ],
        'coverage': {'catalogCards': len(catalog), 'observedCards': len(rows),
                     'cardsWithInHandWinRate': sum(row['metrics']['inHandWinRate'] is not None for row in rows),
                     'missingCards': [{'catalogId': card['id'], 'name': card['name'], 'reason': 'not_listed_by_source'}
                                      for card in catalog if card['id'] not in observed]},
        'cards': rows,
    }
    if any(row['metrics']['includedWinRate'] != 0 for row in rows):
        raise ValueError('Included WR non più costante: riesaminare la nota di qualità')
    validate_external_statistics({'draft': {'externalSources': {'untapped': snapshot}}}, catalog)
    return snapshot


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--expansion', required=True, type=Path)
    parser.add_argument('--apply', action='store_true', help='Aggiorna statistics.json e sources.json')
    args = parser.parse_args()
    capture_bytes = args.capture.read_bytes()
    capture = json.loads(capture_bytes)
    catalog = json.loads((args.expansion / 'cards.json').read_text(encoding='utf-8'))['cards']
    snapshot = normalize(capture, catalog, hashlib.sha256(capture_bytes).hexdigest())
    dated = args.capture.parent / ('untapped-card-data-' + capture['retrieved'].replace('-', '') + '.json')
    if dated.exists() and json.loads(dated.read_text(encoding='utf-8')) != snapshot:
        raise ValueError('Snapshot datato già esistente con dati diversi: conservarlo e scegliere una nuova acquisizione')
    save(dated, snapshot)
    if args.apply:
        statistics_path = args.expansion / 'statistics.json'
        statistics = json.loads(statistics_path.read_text(encoding='utf-8'))
        statistics.setdefault('draft', {}).setdefault('externalSources', {})['untapped'] = snapshot
        validate_external_statistics(statistics, catalog)
        save(statistics_path, statistics)
        sources_path = args.expansion / 'sources.json'
        sources = json.loads(sources_path.read_text(encoding='utf-8'))
        sources.setdefault('externalStatistics', {})['untapped'] = {
            'url': snapshot['url'], 'retrieved': snapshot['retrieved'],
            'dataPath': 'statistics.draft.externalSources.untapped',
            'snapshot': dated.as_posix(), 'inputSha256': snapshot['inputSha256'],
            'note': 'Statistiche pubbliche per carta; filtri, valori mancanti e limiti conservati nello snapshot.'}
        save(sources_path, sources)
    print(json.dumps(snapshot['coverage'], ensure_ascii=False))


if __name__ == '__main__':
    main()
