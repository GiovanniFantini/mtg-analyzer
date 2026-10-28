"""Refresh the dated TRK/SDS preview snapshot, preserving existing catalog IDs.

Run explicitly with network access. The offline site build never imports this file.
"""
import argparse
import copy
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = '2026-10-28'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-snapshot',action='store_true',help='Ricalcola offline dalla cattura datata già salvata')
    args=parser.parse_args()
    path = ROOT / 'expansions/star-trek/cards.json'
    previous = json.loads(path.read_text(encoding='utf-8'))
    existing = {c['name']: c for c in previous['cards']}
    by_oracle = {c['id']:c for c in previous['cards']}
    url = 'https://api.scryfall.com/cards/search?' + urllib.parse.urlencode({
        'q': '(set:trk or set:sds)', 'unique': 'prints', 'order': 'set',
    })
    query = url
    if args.from_snapshot:
        raw=json.loads((ROOT / 'star-trek-scryfall-20261028.json').read_text(encoding='utf-8'))['data']
    else:
        raw = []
        while url:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'MTG-Analyzer-preview-refresh/1.0', 'Accept': 'application/json',
            })
            with urllib.request.urlopen(req, timeout=45) as response:
                page = json.load(response)
            raw.extend(page['data'])
            url = page.get('next_page')
            time.sleep(0.12)
        save(ROOT / 'star-trek-scryfall-20261028.json', {
            'date': DATE, 'source_query': query, 'data': raw,
        })
    grouped = {}
    for printing in raw:
        grouped.setdefault(printing['name'], []).append(printing)
    assert set(by_oracle) <= {p['oracle_id'] for p in raw}, 'Existing identities missing: do not replace catalog'
    cards = []
    for name, prints in grouped.items():
        prints.sort(key=lambda p: (not p['collector_number'].isdigit(),
                                  int(p['collector_number']) if p['collector_number'].isdigit() else 0,
                                  p['collector_number']))
        p = prints[0]
        faces = p.get('card_faces', [])
        images = p.get('image_uris') or (faces[0].get('image_uris', {}) if faces else {})
        card = copy.deepcopy(by_oracle.get(p['oracle_id'],existing.get(name, {})))
        if card.get('name') and card['name']!=name:
            card['previousNames']=sorted(set(card.get('previousNames',[])+[card['name']]))
        card.update({
            'id': card.get('id') or p['oracle_id'], 'name': name,
            'image': images.get('normal', ''), 'mana': p.get('mana_cost', ''),
            'cmc': p['cmc'], 'colors': p.get('colors', []),
            'identity': p['color_identity'], 'type': p['type_line'].replace('\u2014', ':'),
            'text': p.get('oracle_text', ''), 'rarity': p['rarity'],
            'set': p['set'].upper(), 'number': p['collector_number'],
            'url': p['scryfall_uri'].split('?')[0], 'legalities': p['legalities'],
            'keywords': p.get('keywords', []),
            'prints': [{
                'number': v['collector_number'],
                'image': (v.get('image_uris') or (v.get('card_faces') or [{}])[0].get('image_uris', {})).get('normal', ''),
                'finishes': v['finishes'], 'frame_effects': v.get('frame_effects', []),
                'promo_types': v.get('promo_types', []),
            } for v in prints],
            'faces': faces, 'power': p.get('power', ''), 'toughness': p.get('toughness', ''),
        })
        # Keep both supported aliases coherent before passing through the loader.
        card.update(full=name, cost=card['mana'], mv=card['cmc'], oracle=card['text'], large=card['image'])
        cards.append(card)
    cards.sort(key=lambda c: (c['set'], int(c['number']) if c['number'].isdigit() else 100000, c['name']))
    result = {**previous, 'date': DATE, 'cards': cards, 'print_count': len(raw),
              'source_queries': [query]}
    result['complete']=False
    result['partial']=True
    save(path, result)
    save(ROOT / 'star-trek-cards-20261028.json', {k: v for k, v in result.items() if k != '$schema'})
    print(f'{len(cards)} cards, {len(raw)} printings; {len(cards)-len(by_oracle)} new identities')


if __name__ == '__main__':
    main()
