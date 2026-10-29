"""Offline build of staged Git bytes, without untracked local dependencies."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
dest = Path(__file__).resolve().parent
target = Path(sys.argv[1]).resolve()
assert target.name.startswith('mtg-push-staged-') and target.is_dir()
subprocess.run(['git', '-c', 'core.autocrlf=false', 'checkout-index', '--all', '--force',
                '--prefix', target.as_posix() + '/'], cwd=root, check=True)
sources = ['draft-policy.js', 'draft-engine.js', 'draft-worker.js',
           'draft-worker-client.js', 'draft-table.js', 'bot_profiles.py']
hashes = {}
for source in sources:
    staged = subprocess.check_output(['git', 'show', ':' + source], cwd=root)
    assert staged == (target / source).read_bytes()
    hashes[source] = hashlib.sha256(staged).hexdigest()
run = subprocess.run([sys.executable, 'build_site.py'], cwd=target, capture_output=True,
                     text=True, encoding='utf-8', errors='replace')
record = {'scope': 'Offline build of exact staged LF bytes, matching Linux checkout. No untracked local files copied.',
          'indexTreeBeforeEvidence': subprocess.check_output(['git', 'write-tree'], cwd=root, text=True).strip(),
          'sourceHashes': hashes, 'command': ['python', 'build_site.py'],
          'exitCode': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr,
          'externalReview': 'Final Opus approval remains pending quota; user explicitly authorized push.'}
(dest / 'push-preflight.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(record, ensure_ascii=True), flush=True)
raise SystemExit(run.returncode)
