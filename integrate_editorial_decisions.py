"""Integrate a dated selection of editorial decisions without altering game data."""
import argparse
import copy
import html
import json
import re
from datetime import date
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def integrate(expansion, source):
    study = read(source)
    date.fromisoformat(study['date'])
    catalog = read(expansion / 'cards.json')
    cards = {c['name']: c for c in catalog['cards']}
    seen = set()
    for row in study['cards']:
        name = row['name']
        if name not in cards or name in seen:
            raise ValueError(f'Identità sconosciuta o duplicata: {name}')
        if not row.get('verdict') or not row.get('context') or not row.get('sections'):
            raise ValueError(f'Analisi incompleta: {name}')
        if any(not s.get('title') or not s.get('text') for s in row['sections']):
            raise ValueError(f'Sezione incompleta: {name}')
        seen.add(name)
    # Validate the entire input before updating any active document.
    for row in study['cards']:
        cards[row['name']]['prospects']['decisionReview'] = {
            'date': study['date'], 'kind': study['kind'],
            **copy.deepcopy({k: v for k, v in row.items() if k != 'name'})
        }
    guides = read(expansion / 'guides.json')
    gallery = read(expansion / 'expansion.json')['presentation']['pages']['gallery']['url']
    links = ' · '.join(
        '<a href="' + html.escape(gallery, quote=True) + '?card=' + cards[row['name']]['id']
        + '#gallery">' + html.escape(row['name']) + '</a>'
        for row in study['cards']
    )
    index = (
        '<div data-editorial-decisions><h2>Valutazioni e piani di gioco</h2>'
        f'<p>{len(seen)} approfondimenti campione su {len(cards)} identità. '
        'Apri la carta nel catalogo: la valutazione mostra piano, sequenza, '
        'alternative, rischi e cosa verificare nelle partite. '
        'Sono giudizi editoriali prima dell’uscita, distinti da voti, WR e prezzi.</p>'
        f'<p>{links}</p></div>'
    )
    intro = guides['fragments'].get('analysis.copy-0', '')
    intro = re.sub(r'<div data-editorial-decisions>.*?</div>', '', intro, flags=re.S)
    guides['fragments']['analysis.copy-0'] = intro + index
    guides['fragments'].pop('analysis.panel-decisions', None)
    sources = read(expansion / 'sources.json')
    sources['research']['editorialDecisions'] = {
        'date': study['date'], 'kind': study['kind'], 'cards': len(seen),
        'catalogCards': len(cards), 'scope': study['scope'],
        'input': source.as_posix(),
        'sources': ['Testi Oracle del catalogo', 'Release notes ufficiali',
                    'Pareri attribuiti conservati nelle singole schede'],
        'observedResultsAdded': False,
    }
    write(expansion / 'cards.json', catalog)
    write(expansion / 'guides.json', guides)
    write(expansion / 'sources.json', sources)
    return {'date': study['date'], 'cards': len(seen), 'catalogCards': len(cards)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expansion', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(integrate(args.expansion, args.input), ensure_ascii=False))
