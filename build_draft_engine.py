"""Build the draft table offline from a versioned, public card snapshot."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def build():
    snapshot = json.loads((ROOT / 'draft-format-fra-20261021.json').read_text(encoding='utf-8'))
    catalog = json.loads((ROOT / 'sealed-database.json').read_text(encoding='utf-8'))
    reviews = {c['full']: c for c in catalog['cards']}
    archetypes = json.loads((ROOT / 'draft-archetypes.json').read_text(encoding='utf-8'))
    for card in snapshot['cards']:
        review = reviews.get(card['full'])
        if review is None:
            raise ValueError(f"Missing review: {card['full']}")
        card.update(score=review['score'], role=review['role'])
        card['archetypes'] = [key for key, a in archetypes.items()
                              if card['name'] in a['core'] + a['support']]
    data = {**snapshot, 'archetypes': archetypes}
    template = (ROOT / 'draft-engine-template.html').read_text(encoding='utf-8')
    return template.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))

if __name__ == '__main__':
    (ROOT / 'Reality-Fracture-Draft-Engine.html').write_text(build(), encoding='utf-8')
