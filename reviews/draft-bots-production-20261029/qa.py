from pathlib import Path
import hashlib,json,os,subprocess,sys
root=Path(__file__).resolve().parents[2];out=Path(os.environ['MTG_QA_DIR']);out.mkdir(parents=True,exist_ok=True)
phase=sys.argv[1];name=phase.rstrip('0123456789');log=out/(phase+'-checks.json')
if log.exists():raise SystemExit('Preserve existing check log')
commands={'transport':[['node','verify-draft-worker.cjs'],['node','verify-draft-worker-client.cjs'],['node','verify-draft-worker-browser.cjs']], 'workers':[['node','verify-draft-worker-browser.cjs'],['node','verify-draft-policy-browser.cjs']], 'performance':[['node','verify-draft-performance.cjs']], 'legacy':[['node','verify-draft-bots-browser.cjs'],['node','verify-expansion-browser.cjs'],[sys.executable,'verify-expansion-review.py']]}
results=[]
for command in commands[name]:
 hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in ['draft-policy.js','draft-engine.js','draft-worker.js','draft-worker-client.js','draft-table.js','bot_profiles.py']}
 run=subprocess.run(command,cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace');results.append({'command':command,'exitCode':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'sourceHashes':hashes})
 log.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(results[-1],ensure_ascii=True),flush=True)
 if run.returncode:raise SystemExit(run.returncode)
