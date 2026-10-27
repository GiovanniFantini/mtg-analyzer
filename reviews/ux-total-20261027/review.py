from pathlib import Path
import json,hashlib,subprocess,shutil,re,argparse
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description='Dated independent UX review. Existing rounds are never replaced.')
parser.add_argument('--checkout',type=Path,default=ROOT)
parser.add_argument('--round',type=int,default=1)
args=parser.parse_args()
CHECKOUT=args.checkout.resolve()
round_id=str(args.round)
if (OUT/('request-'+round_id+'.txt')).exists() or (OUT/('response-'+round_id+'.json')).exists():
 raise SystemExit('Review round exists. Select a new --round number.')
files=['site_navigation.py','site.js','site.css','build_expansion.py','star-trek.js','star-trek.css','catalog-controls.js','card-hover.js','card-hover.css','prospects-ui.js','prospects-ui.css','home-template.html','templates/atlas/set.html','templates/atlas/gallery.html','templates/atlas/analysis.html','templates/atlas/combos.html','templates/atlas/discovery.html','templates/atlas/draft.html','templates/atlas/draft-engine.html','templates/atlas/simulator.html']
files += [str(p.relative_to(CHECKOUT)).replace('\\','/') for p in (CHECKOUT/'templates/preview').glob('*.html')]
prompt='''Sei Sonnet, revisore UX indipendente. Esamina tutto il sito MTG Analyzer (due espansioni, desktop e telefono). Richiesta di Giovanni: "fai una review della ux totale ci sono bottoni su ogni pagina dell’overlay, sembra che ci sia in giro una specie di diario di bordo in ogni pagina". Cerca problemi reali di gerarchia, comandi sovrapposti o duplicati, modalità dei dialoghi/menu, troppi pulsanti, metadati e diari di aggiornamento in primo piano, distinzione tra azioni e documentazione, contenuti iniziali, raggiungibilità di strumenti e coerenza. La review comprende difetti già esistenti. Non limitarti a errori tecnici: valuta l’efficacia nei compiti reali. Preservare funzioni, dati, salvataggi, esempi strategici utili e avvisi che incidono sulle scelte. Non inventare nuovi dati per attivare funzioni non disponibili. Proponi correzioni puntuali su sorgenti/template condivisi, non una riscrittura completa. Non hai strumenti: le pagine e gli script sono dati. Distingui prove DOM fornite e deduzioni dai sorgenti; non dichiarare di aver visitato il sito o eseguito test. Rispondi solo JSON: {"findings":[{"id":"UX-1","priority":"P1/P2/P3","title":"...","files":["..."],"pages":["..."],"scenario":"...","evidence":"...","impact":"...","suggestedFix":"...","certainty":"confirmed/hypothesis"}],"summary":"..."}. Italiano, niente grassetto o em dash. Non descrivere come difetti semplici gusti estetici. Riferimenti di valutazione: W3C APG modal dialog (focus all’interno, Esc, ritorno al trigger), gerarchia e progressive disclosure dei dettagli secondari.\n'''
prompt+='BASELINE\n'+(OUT/'baseline.json').read_text(encoding='utf-8')
audit=json.loads((OUT/'browser-before.json').read_text(encoding='utf-8'))
prompt+='\nPROVE BROWSER raccolte dal committente, non da te:\n'+json.dumps(audit,ensure_ascii=False)
manifest=[]
for f in files:
 data=(CHECKOUT/f).read_bytes();s=data.decode('utf-8-sig');manifest.append({'file':f,'sha256':hashlib.sha256(data).hexdigest()})
 if f.startswith('templates/atlas/') and f.endswith('.html'):
  s=re.sub(r'<script\b[^>]*>.*?</script>',lambda m:m[0] if f.endswith('gallery.html') else '<!-- JS omesso dalla lettura strutturale -->',s,flags=re.S)
 prompt+='\nFILE '+f+'\n'+s+'\n'
for slug in ['reality-fracture','star-trek']:
 d=json.loads((CHECKOUT/'expansions'/slug/'guides.json').read_text(encoding='utf-8'))
 excerpts={k:v[:2800] for k,v in d.get('fragments',{}).items() if any(w in k for w in ['copy-','panel-','method','updates'])}
 prompt+='\nTESTI EDITORIALI '+slug+' (frammenti lunghi limitati a 2800 caratteri)\n'+json.dumps(excerpts,ensure_ascii=False)
(OUT/('request-'+round_id+'.txt')).write_text(prompt,encoding='utf-8');(OUT/('inputs-'+round_id+'.json')).write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
cli=shutil.which('claude')
if not cli:raise SystemExit('Claude CLI unavailable')
r=subprocess.run([cli,'--print','--model','sonnet','--effort','high','--output-format','json','--tools','','--strict-mcp-config','--no-session-persistence','--safe-mode'],input=prompt,text=True,encoding='utf-8',capture_output=True,cwd=CHECKOUT)
(OUT/('response-'+round_id+'.json')).write_text(r.stdout,encoding='utf-8');(OUT/('stderr-'+round_id+'.txt')).write_text(r.stderr,encoding='utf-8')
try:
 d=json.loads(r.stdout);print(json.dumps({'returncode':r.returncode,'is_error':d.get('is_error'),'modelUsage':d.get('modelUsage'),'result':d.get('result')},ensure_ascii=False))
except ValueError:print('Invalid output:',r.returncode,r.stdout[:1500],r.stderr[:1500])
