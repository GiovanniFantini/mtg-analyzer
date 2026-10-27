"""Import a dated public Untapped pick-order DOM capture, entirely offline."""
import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

TIERS = ['S', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']


def normalize(capture, catalog, input_hash):
    date.fromisoformat(capture['retrieved'])
    parsed = urlparse(capture['url'])
    if parsed.netloc != 'mtga.untapped.gg' or not parsed.path.endswith('/pick-order'):
        raise ValueError('Fonte pick order non valida')
    if capture['filters'].get('tiering') != 'In Hand WR':
        raise ValueError('Metrica di tiering inattesa')
    names = {}
    for card in catalog:
        for name in {card['name'], card.get('full', card['name'])}:
            if name in names and names[name]['id'] != card['id']:
                raise ValueError('Nome ambiguo: ' + name)
            names[name] = card
    rows, seen, tiers = [], set(), set()
    for group in capture['groups']:
        tier = group['tier']
        if tier not in TIERS + ['?'] or tier in tiers:
            raise ValueError('Tier non valido o duplicato: ' + str(tier))
        tiers.add(tier)
        for position, source in enumerate(group['cards'], 1):
            card = names[source['name']]
            if card['id'] in seen or card.get('basic'):
                raise ValueError('Carta duplicata o base: ' + source['name'])
            seen.add(card['id'])
            if not source['url'].startswith('/limited/draft/'):
                raise ValueError('URL carta non valido')
            rows.append({'catalogId': card['id'], 'name': source['name'],
                         'tier': None if tier == '?' else tier,
                         'tierOrder': TIERS.index(tier) if tier != '?' else None,
                         'status': 'ranked' if tier != '?' else 'low_match_volume',
                         'sourcePositionWithinTier': position,
                         'url': 'https://mtga.untapped.gg' + source['url']})
    if not rows:
        raise ValueError('Acquisizione vuota')
    return {'provider': 'Untapped.gg', 'url': capture['url'],
            'retrieved': capture['retrieved'], 'filters': capture['filters'],
            'inputSha256': input_hash, 'tierOrder': TIERS,
            'limitations': [
                'Tier statistici In Hand WR di Arena, distinti dai voti editoriali e dalle recensioni.',
                'Il gruppo Low Match Volume resta senza tier; le carte assenti non ricevono stime.',
                'La posizione visualizzata entro un tier non viene interpretata come un voto o una priorità numerica.',
                'Nessuna conversione in stelle, modifica dei pesi dei bot o dei replay.',
            ],
            'coverage': {'catalogCards': len(catalog), 'observedCards': len(rows),
                         'rankedCards': sum(row['tier'] is not None for row in rows),
                         'lowMatchVolumeCards': sum(row['tier'] is None for row in rows),
                         'missingCards': [{'catalogId': c['id'], 'name': c['name']}
                                          for c in catalog if c['id'] not in seen]},
            'cards': rows}


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    parser.add_argument('--expansion', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    raw = args.capture.read_bytes()
    catalog = json.loads((args.expansion / 'cards.json').read_text(encoding='utf-8'))['cards']
    snapshot = normalize(json.loads(raw), catalog, hashlib.sha256(raw).hexdigest())
    target = args.capture.parent / ('untapped-pick-order-' + snapshot['retrieved'].replace('-', '') + '.json')
    if target.exists() and json.loads(target.read_text(encoding='utf-8')) != snapshot:
        raise ValueError('Snapshot datato già presente con contenuto diverso')
    if args.apply:
        ratings_path = args.expansion / 'ratings.json'
        sources_path = args.expansion / 'sources.json'
        ratings = json.loads(ratings_path.read_text(encoding='utf-8'))
        sources = json.loads(sources_path.read_text(encoding='utf-8'))
        for rating in ratings['cards'].values():
            rating.pop('untappedPickOrder', None)
        for row in snapshot['cards']:
            ratings['cards'].setdefault(row['catalogId'], {})['untappedPickOrder'] = {
                key: row[key] for key in ('tier', 'tierOrder', 'status', 'url')}
            ratings['cards'][row['catalogId']]['untappedPickOrder'].update(
                retrieved=snapshot['retrieved'], filters=snapshot['filters'])
        sources.setdefault('externalRankings', {})['untappedPickOrder'] = {
            key: value for key, value in snapshot.items() if key != 'cards'}
        save(ratings_path, ratings)
        save(sources_path, sources)
    save(target, snapshot)
    print(json.dumps(snapshot['coverage'], ensure_ascii=False))


if __name__ == '__main__':
    main()
