"""Normalize the complete acquired Draftsim review; no network during integration."""
import hashlib
import json
import re
import unicodedata
from html import unescape
from pathlib import Path
import argparse


def norm(value):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', value).casefold())


def extract(capture, catalog):
    raw = capture.read_bytes()
    text = raw.decode('utf-8')
    headers = list(re.finditer(r'<h([23])\b[^>]*>(.*?)</h\1>', text, re.S | re.I))
    by_name = {norm(name): c for c in catalog for name in [c['name'], c.get('oracleName', '')] if name}
    groups = {
        'The Planet Dual Lands': [c for c in catalog if c['set'] == 'TRK' and c['land'] and c['rarity'] == 'common' and 'Planet' in c['type']],
        'The Anomaly Lands': [c for c in catalog if c['set'] == 'TRK' and c['name'].endswith(' Anomaly')],
        'The Shock Lands': [c for c in catalog if c['set'] == 'TRK' and c['land'] and 'you may pay 2 life' in c['text']],
        'The Dilemma Lands': [c for c in catalog if c['set'] == 'TRK' and c['land'] and 'choose one' in c['text'].lower()],
    }
    assert {k: len(v) for k, v in groups.items()} == {'The Planet Dual Lands': 10, 'The Anomaly Lands': 5, 'The Shock Lands': 10, 'The Dilemma Lands': 5}
    rows, unmatched, seen = [], [], set()
    for index, heading in enumerate(headers):
        name = unescape(re.sub('<[^>]+>', ' ', heading[2])).strip()
        chunk = text[heading.end():headers[index + 1].start() if index + 1 < len(headers) else len(text)]
        plain = unescape(re.sub('<[^>]+>', ' ', chunk))
        rating = re.search(r'Rating:\s*(\d+(?:\.\d+)?)/10', plain)
        if not rating:
            continue
        # SDS headings explicitly give both the reskin and the canonical name.
        canonical = re.search(r'\(([^()]*)\)$', name)
        card = by_name.get(norm(name)) or (by_name.get(norm(canonical[1])) if canonical else None)
        matches = groups.get(name, [card] if card else [])
        if not matches:
            unmatched.append(name)
        for card in matches:
            if card['id'] in seen:
                raise ValueError('Duplicate: ' + card['name'])
            seen.add(card['id'])
            rows.append({'catalogId': card['id'], 'name': card['name'], 'sourceName': name,
                         'value': float(rating[1]), 'scaleMax': 10,
                         'groupAssessment': name if name in groups else None})
    expected = {c['id'] for c in catalog if not c['basic']}
    missing = sorted(expected - seen)
    if unmatched or missing or seen != expected:
        raise ValueError({'unmatched': unmatched, 'missing': missing})
    author = re.search(r'<meta name="author" content="([^"]+)"', text)
    published = re.search(r'"datePublished":"(\d{4}-\d{2}-\d{2})', text)
    return {'date': '2026-11-03', 'source': 'draftsim-trk-limited-20261103',
            'url': 'https://draftsim.com/mtg-trk-limited-set-review/',
            'author': unescape(author[1]), 'published': published[1],
            'context': 'Limited, recensione prima dell’uscita; nessun voto Sealed distinto',
            'captureSha256': hashlib.sha256(raw).hexdigest(), 'captureBytes': len(raw),
            'method': 'Voti trascritti, senza media. Quattro valutazioni di cicli sono espanse sui membri verificati; le SDS sono abbinate dal nome canonico fra parentesi.',
            'matchedCards': len(rows), 'unmatched': unmatched, 'missing': missing, 'cards': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    cards = json.loads((root / 'expansions/star-trek/cards.json').read_text(encoding='utf-8'))['cards']
    result = extract(args.capture, cards)
    Path(__file__).with_name('draftsim-reviews.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'cards'}, ensure_ascii=False))
