"""Record final local evidence without making an external-review claim."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

root = Path(__file__).resolve().parents[2]
dest = Path(__file__).resolve().parent
qa = dest / 'qa-05bca7a673a4'
runtime = ['draft-policy.js', 'draft-engine.js', 'draft-worker.js',
           'draft-worker-client.js', 'draft-table.js', 'bot_profiles.py']
hashes = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in runtime}
old_worker = (dest / 'worker-before-cpu-reserve.js.txt').read_bytes()
assert hashlib.sha256(old_worker).hexdigest() == '5041d79dd145197a64bf142e2edec3a276903d5506bfa2c73dec476faea3ed5f'
expected_worker = old_worker.replace(b' try{for(let i=0;', b' // Leave capacity for the page, coordinator and browser work under CPU load.\n try{for(let i=0;').replace(b'(self.navigator?.hardwareConcurrency||2)-1', b'(self.navigator?.hardwareConcurrency||2)-2')
assert (root / 'draft-worker.js').read_bytes() == expected_worker
prior_qa = dest / 'qa-d944c5fcda32'
logs = [dest / 'checks.json', prior_qa / 'workers1-checks.json',
        prior_qa / 'legacy1-checks.json', qa / 'transport1-checks.json', qa / 'performance1-checks.json']
checks = []
for log, expected in zip(logs, [12, 2, 3, 3, 1]):
    rows = json.loads(log.read_text(encoding='utf-8'))
    assert len(rows) == expected, log
    for row in rows:
        assert row['exitCode'] == 0, (log, row['command'])
        if log in logs[:3]:
            prior_hashes = {**hashes, 'draft-worker.js': '5041d79dd145197a64bf142e2edec3a276903d5506bfa2c73dec476faea3ed5f'}
            assert row['sourceHashes'] == prior_hashes, (log, row['command'])
        else:
            assert row['sourceHashes'] == hashes, (log, row['command'])
        checks.append({'log': str(log.relative_to(dest)),
                       'command': row['command'], 'exitCode': row['exitCode'], 'sourceHashes': row['sourceHashes']})
perf = json.loads((qa / 'performance.json').read_text())
parity = json.loads((qa / 'sequential-parity.json').read_text())
browser_parity = json.loads((qa / 'browser-sequential-parity.json').read_text())
assert perf['complete'] and parity['complete']
assert browser_parity['complete'] and all(r['exactFullExportParity'] for r in browser_parity['results'])
assert len(perf['rows']) == len(parity['results']) == 4
assert perf['default']['decisions'] == 126
assert perf['default']['p95Ms'] <= 5000
for row in perf['rows']:
    assert row['longestTask'] <= 200 and row['maxGap'] < 500
    for replay in row['replays']:
        assert replay['longestTask'] <= 200 and replay['maxGap'] < 500
f = json.loads((qa / 'format.json').read_text())
algorithm = hashlib.sha256(b'\0'.join((root / p).read_bytes() for p in
                                   ['draft-policy.js', 'draft-engine.js', 'collation.js'])).hexdigest()
assert f['botPolicy']['algorithmRevision'] == algorithm
assert f['botPolicy']['workerRevision'] == hashes['draft-worker.js']
sources = runtime + ['collation.js', 'build_expansion.py', 'expansion_data.py',
    'schemas/bot-policy.schema.json', 'schemas/limited.schema.json',
    'draft-engine-template.html', 'templates/atlas/draft-engine.html',
    'docs/requirements.md', 'docs/draft-engine.md', 'docs/verification.md',
    'test_bot_profiles.py', 'benchmark-draft-policy.cjs']
sources += [str(p.relative_to(root)).replace('\\', '/') for p in root.glob('verify-draft-*.cjs')]
sources += [str(p.relative_to(root)).replace('\\', '/') for p in (root / 'tests').rglob('draft-*') if p.is_file()]
sources += [str(p.relative_to(root)).replace('\\', '/') for p in (root / 'expansions').rglob('*.json')]
sources += [str(p.relative_to(root)).replace('\\', '/') for p in dest.glob('*.cjs')]
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
result = {'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Local experimental release evidence only. v3 default, promotion false, final actual Opus review pending quota.',
    'head': head, 'algorithmRevision': algorithm, 'workerRevision': hashes['draft-worker.js'],
    'runtimeHashes': hashes, 'offlineBuild': 'Completed successfully before final browser acquisition: 21 expansions, 290 HTML pages and local links. No network needed by builder.',
    'checks': checks, 'performance': perf, 'sequentialParity': parity, 'browserSequentialParity': browser_parity,
    'sourceAndDataHashes': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sorted(set(sources))}}
(dest / 'local-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
status_path = dest / 'status.json'
status = json.loads(status_path.read_text(encoding='utf-8'))
status['pending'] = ['Final actual Opus review on updated code and complete local evidence. User will handle resumption.']
status['localVerification'] = {'complete': True, 'artifact': 'local-verification.json',
    'runtimeHashes': hashes, 'defaultLatency': perf['default'], 'actualWorkerSequentialTables': 4,
    'competitivePromotion': False, 'finalOpusApproval': False}
status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
report_path = dest / 'report.md'
report = report_path.read_text(encoding='utf-8')
text = ('Build offline completata: 21 espansioni, 290 pagine HTML e collegamenti locali. '
        'Passate le 43 prove Python, il controllo del contratto di collazione, tutte le 10 verifiche Node del motore e dei worker, '
        'i controlli browser v4 e storici, e le 19 fixture isolate del contratto. '
        'La sola modifica successiva alla suite completa riserva una CPU aggiuntiva alla pagina riducendo il numero di worker. '
        'Cinque sorgenti runtime sono identici; la differenza del sesto è verificata byte per byte e registrata in cpu-reserve-decision.json. '
        'Sul worker aggiornato sono ripassati parità ed export, gestione degli errori nel client, flussi browser dei worker e acquisizione completa con replay.\n\n')
text += f"Le 126 scelte predefinite hanno p50 {perf['default']['p50Ms']} ms, p95 {perf['default']['p95Ms']} ms e massimo {perf['default']['maxMs']} ms. "
power = next(row for row in perf['rows'] if row['scenario'] == 'power')
text += f"Il controllo separato Potenza pura comprende 42 scelte, p95 {power['p95Ms']} ms. "
all_metrics = perf['rows'] + [r for row in perf['rows'] for r in row['replays']]
text += f"Task massimo dell'interfaccia, comprese le riprese, {max(row['longestTask'] for row in all_metrics)} ms; intervallo massimo del battito {max(row['maxGap'] for row in all_metrics):.1f} ms.\n\n"
text += 'Le riprese complete sul primo seme: ' + '; '.join(f"{r['picks']} scelte in {r['durationMs']/1000:.1f} secondi" for r in perf['rows'][0]['replays']) + '. L’export dopo ripresa completa coincide con quello originale.\n\n'
text += ('I quattro tavoli reali nel browser coincidono esattamente con il replay sequenziale per tutti i pool e log. '
         'Il confronto esatto usa lo stesso Chromium e byte verificati dei sorgenti. Il primo confronto con Node aveva differenze nelle ultime cifre decimali dei punteggi: quel tentativo non è stato accettato come parità esatta e il limite è conservato in node-cross-runtime-limitation.json. '
         'Ogni tavolo conserva tutte le 336 carte della collazione iniziale. '
         'Il confronto v3 usa la stessa collazione; la diagnosi condivisa costruisce 56 mazzi da 40 slot usando soltanto carte possedute e basi ammesse. '
         'Errori di mana e carenze rimangono registrati come diagnosi, senza sostituirli con un giudizio di forza. '
         'Vedere [evidenze locali complete](local-verification.json), [prestazioni](qa-05bca7a673a4/performance.json) e [parità sequenziale](qa-05bca7a673a4/sequential-parity.json).')
old = 'Le verifiche sulla versione finale e le misure complete sono registrate nella cartella [QA finale](qa-05bca7a673a4/). Il riepilogo numerico viene completato dopo la conclusione delle acquisizioni.'
assert old in report
report_path.write_text(report.replace(old, text), encoding='utf-8')
print(json.dumps({'complete': True, 'commands': len(checks), 'default': perf['default'], 'finalOpusApproval': False}))
