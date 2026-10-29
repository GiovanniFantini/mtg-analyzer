"""Run scoped checks with versioned outputs; never replace a prior acquisition."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[1]
label = sys.argv[1]
dest = DIRECTORY / f'checks-{label}.json'
if dest.exists():
    raise SystemExit('Check acquisition already exists')
mode = sys.argv[2] if len(sys.argv) > 2 else 'browser'
commands = {
    'unit': [[sys.executable, '-m', 'unittest', 'test_expansion_data.py']],
    'build': [[sys.executable, 'build_site.py']],
    'final': [[sys.executable, '-m', 'unittest', 'test_expansion_data.py'], ['node', 'verify-draft-policy-browser.cjs']],
    'browser': [['node','test-draft-visual.cjs'], ['node', 'verify-draft-table-visual.cjs'], ['node', 'verify-draft-table-recovery.cjs'], ['node', 'verify-draft-bots-browser.cjs'], ['node', 'verify-draft-policy-browser.cjs']],
}[mode]
env = dict(os.environ)
if mode == 'browser':
    env['MTG_QA_DIR'] = str(DIRECTORY / ('browser-' + label))
results = []
for command in commands:
    sources = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['draft-table.js','draft-visual.js','draft-engine.css','site.js','templates/atlas/draft-engine.html']}
    tests = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in command[1:] if (ROOT/p).is_file()}
    run = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    row = {'command': command[1:], 'exitCode': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr, 'sourceHashes': sources, 'testHashes': tests}
    results.append(row)
    dest.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'command':command[1:],'exitCode':run.returncode,'stdout':run.stdout[-1800:],'stderr':run.stderr[-1800:]},ensure_ascii=True),flush=True)
    if run.returncode:
        raise SystemExit(run.returncode)
