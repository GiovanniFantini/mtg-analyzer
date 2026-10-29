"""Capture offline inputs and provenance. Run from the repository root."""
import hashlib
import json
import subprocess
from pathlib import Path

from expansion_data import load_expansions

DEST = Path(__file__).resolve().parent
ROOT = DEST.parent.parent
expansions = load_expansions()
selected = ('reality-fracture', 'bloomburrow', 'foundations')
fields = ('id', 'name', 'full', 'colors', 'identity', 'cost', 'mv', 'type',
          'rarity', 'basic', 'land', 'creature', 'score', 'role', 'oracle', 'archetypes')
formats = {}
for slug in selected:
    fmt = next(e for e in expansions if e.manifest['id'] == slug).draft_format('draft')
    fmt.pop('ui', None)
    fmt['cards'] = [{key: card.get(key) for key in fields} for card in fmt['cards']]
    formats[slug] = fmt
availability = [{'id': e.manifest['id'], 'draftTable': e.capabilities()['draftTable']}
                for e in expansions]
sources = [ROOT / name for name in ('draft-engine.js', 'collation.js',
           'expansion_data.py', 'audit-draft-bots.cjs', 'verify-draft-bots.cjs')]
for slug in selected:
    sources.extend(sorted((ROOT / 'expansions' / slug).glob('*.json')))
manifest = {
    'date': '2026-10-29',
    'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'node': subprocess.check_output(['node', '--version'], text=True).strip(),
    'python': subprocess.check_output(['python', '--version'], text=True).strip(),
    'sha256': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sources},
    'notes': ['Snapshots omit UI and printing metadata unused by the evaluator.',
              'The existing full-table audit loads live repository inputs; compare these hashes before rerunning.'],
}
for name, data in [('formats', formats), ('availability', availability), ('input-manifest', manifest)]:
    (DEST / (name + '.json')).write_text(json.dumps(data, ensure_ascii=True, separators=(',', ':')) + '\n', encoding='utf-8')
print(json.dumps({'available': [x['id'] for x in availability if x['draftTable']['available']],
                  'snapshotBytes': (DEST / 'formats.json').stat().st_size}))
