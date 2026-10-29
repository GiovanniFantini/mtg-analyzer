"""Run the required checks and preserve their actual exit codes and output."""
import json
import hashlib
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
dest = Path(__file__).resolve().parent
commands = [
    [sys.executable, '-m', 'unittest', 'test_expansion_data.py', 'test_bot_profiles.py'],
    ['node', 'verify-draft-bots.cjs'],
    ['node', 'verify-draft-engine.cjs'],
    ['node', 'verify-expansions.cjs'],
    [sys.executable, 'verify-collation-contract.py'],
    ['node', 'verify-draft-policy.cjs'],
    ['node', 'verify-draft-policy-regressions.cjs'],
    ['node', 'verify-draft-production.cjs'],
    ['node', 'verify-draft-worker.cjs'],
    ['node', 'verify-draft-worker-client.cjs'],
    ['node', 'verify-draft-async.cjs'],
    ['node', 'verify-draft-policy-optimization.cjs'],
]
results = []
if '--resume-policy' in sys.argv:
    prior = json.loads((dest / 'checks.json').read_text(encoding='utf-8'))
    backup = dest / 'checks-before-fixture-correction.json'
    if not backup.exists():
        backup.write_text(json.dumps(prior, ensure_ascii=False, indent=2), encoding='utf-8')
    assert all(row['exitCode'] == 0 for row in prior[:5])
    results = prior[:5]
    commands = commands[5:]
for command in commands:
    source_hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in ['draft-policy.js','draft-engine.js','draft-worker.js','draft-worker-client.js','draft-table.js','bot_profiles.py']}
    run = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding='utf-8', errors='replace')
    results.append({'command': command, 'exitCode': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr, 'sourceHashes': source_hashes})
    print(json.dumps({'command': command[1:], 'exitCode': run.returncode}), flush=True)
    (dest / 'checks.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    if run.returncode:
        print(run.stdout, run.stderr)
        raise SystemExit(run.returncode)
