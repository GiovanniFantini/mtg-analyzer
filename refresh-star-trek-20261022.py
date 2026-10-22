"""Refresh the dated TRK/SDS preview snapshot, preserving existing catalog IDs.

Run explicitly with network access. The offline site build never imports this file.
"""
import copy
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = '2026-10-22'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    path = ROOT / 'expansions/star-trek/cards.json'
    previous = json.loads(path.read_text(encoding='utf-8'))
    existing = {c['name']: c for c in previous['cards']}
    url = 'https://api.scryfall.com/cards/search?' + urllib.parse.urlencode({
        'q': '(set:trk or set:sds)', 'unique': 'prints', 'order': 'set',
    })
    query = url
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
    save(ROOT / 'star-trek-scryfall-20261022.json', {
        'date': DATE, 'source_query': query, 'data': raw,
    })
    grouped = {}
    for printing in raw:
        grouped.setdefault(printing['name'], []).append(printing)
    assert set(existing) <= set(grouped), 'Existing cards missing: do not replace catalog'
    cards = []
    for name, prints in grouped.items():
        prints.sort(key=lambda p: (not p['collector_number'].isdigit(),
                                  int(p['collector_number']) if p['collector_number'].isdigit() else 0,
                                  p['collector_number']))
        p = prints[0]
        faces = p.get('card_faces', [])
        images = p.get('image_uris') or (faces[0].get('image_uris', {}) if faces else {})
        card = copy.deepcopy(existing.get(name, {}))
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
    save(path, result)
    save(ROOT / 'star-trek-cards-20261022.json', {k: v for k, v in result.items() if k != '$schema'})
    print(f'{len(cards)} cards, {len(raw)} printings; {len(set(grouped) - set(existing))} new cards')


if __name__ == '__main__':
    main()
