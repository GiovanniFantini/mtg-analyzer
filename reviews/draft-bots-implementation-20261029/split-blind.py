"""Separate judging contexts: pick judges must not see final decks."""
import json
from pathlib import Path
import sys

folder = Path(sys.argv[1])
source = json.loads((folder / 'blind-sample.json').read_text(encoding='utf-8'))
catalog = {c['id']: c for c in source['cards']}
for section in ('decks', 'picks'):
    target = folder / ('blind-' + section + '.json')
    assert not target.exists(), 'Preserve prior acquisition'
    needed = set()
    for row in source[section]:
        if section == 'decks':
            needed.update(item['id'] for item in row['main'])
            needed.update(row['lands'])
            needed.update(row['manaOnly'])
        else:
            needed.update(row['poolBefore'])
            needed.update(row['observed'])
            needed.add(row['selected'])
    output = {'cards': [catalog[key] for key in sorted(needed)], section: source[section]}
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(section, len(source[section]), 'catalog cards', len(needed))
