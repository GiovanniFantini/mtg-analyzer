"""Request Opus editorial contributions, recording exact inputs and actual model."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
PRIVATE=ROOT/'docs/local/reviews/star-trek-20261109'
PRIVATE.mkdir(parents=True,exist_ok=True)
cards=json.loads((ROOT/'expansions/star-trek/cards.json').read_text(encoding='utf-8'))['cards']
missing=[c for c in cards if not c['basic'] and c['rarity'] not in ('common','uncommon')]
batch=int(sys.argv[1]);selected=missing[batch*45:(batch+1)*45]
prefix='contribution-'+str(batch)
if (PRIVATE/(prefix+'.response.json')).exists():raise SystemExit('Existing acquisition')
compact=lambda c:dict(id=c['id'],name=c['name'],set=c['set'],number=c['number'],mana=c['cost'],type=c['type'],text=c['text'],power=c.get('power'),toughness=c.get('toughness'),review=c['prospects'].get('gameplayReview'),reviews=c['prospects'].get('limitedReviews'),analysis=c['prospects'].get('limitedAnalysis'))
prompt='''Giovanni chiede di completare ogni carta Star Trek con ranking attendibili Draft e Sealed e proiezione di utilizzo nel set. Data 9 novembre 2026. Contributo editoriale originale, non recensione esterna né risultato osservato. Nessuna WR utilizzabile: early access con enormi incertezze; Arena apre il 10 novembre. Non inventare partite, consenso, percentuali o test. Valuta Oracle, costo, curva, impatto immediato, rischio, supporto, costo opportunità del pick e selezione nel pool chiuso. Non trasferire automaticamente i voti Draft al Sealed e non mediare autori. Scala QUALITATIVA P=Prioritaria (può includere bombe), S=Solida, Y=Dipende dalle sinergie, F=Riempitivo, B=Riserva mirata, N=Eviterei di base. Rarità non è un voto. Terre rare valutate per fixing e costo del pick. Carte SDS sono ospiti: analisi condizionata alla presenza nell'evento, non garantire collazione. Distingui costruire attorno a una carta dal semplice beneficio di una sinergia. Fornisci note specifiche in italiano senza trattino lungo, circa 30-55 parole per Draft e Sealed, non ripetizioni generiche. Per ogni carta selezionata restituisci id, draft:{tier,note}, sealed:{tier,note}, partners:[2-4 nomi ESATTI dal catalogo con sinergia reale], usage:{role (stringa breve), plan (20-45 parole), conditions (20-40 parole), confidence:"media" o "bassa"}. La confidence riguarda il GIUDIZIO editoriale, non risultati. Non citare come fonti i modelli. Prima di rispondere verifica restrizioni Oracle, modi alternativi, tap/station, costi e colori. Se giudizi esterni divergono spiega il punto decisivo anziché fingere accordo. Rispondi SOLO JSON {"cards":[...],"concerns":[...]}, copertura esattamente le carte selezionate una volta ciascuna. Nessuno strumento disponibile, non fingere ricerca autonoma.
'''
prompt+='\nCATALOGO PER SUPPORTI\n'+json.dumps([dict(name=c['name'],mana=c['cost'],type=c['type'],text=c['text']) for c in cards],ensure_ascii=False,separators=(',',':'))
prompt+='\nCARTE SELEZIONATE\n'+json.dumps([compact(c) for c in selected],ensure_ascii=False,separators=(',',':'))
(PRIVATE/(prefix+'.request.txt')).write_text(prompt,encoding='utf-8')
r=subprocess.run([shutil.which('claude'),'--print','--model','opus','--effort','high','--output-format','json','--tools','','--strict-mcp-config','--no-session-persistence','--safe-mode'],input=prompt,text=True,capture_output=True,encoding='utf-8',cwd=ROOT)
(PRIVATE/(prefix+'.response.json')).write_text(r.stdout,encoding='utf-8')
(PRIVATE/(prefix+'.stderr.txt')).write_text(r.stderr,encoding='utf-8')
if r.returncode:raise SystemExit(r.stderr or r.stdout)
response=json.loads(r.stdout)
result=json.loads(response['result'].strip().removeprefix('```json').removesuffix('```').strip())
assert {c['id'] for c in result['cards']}=={c['id'] for c in selected} and len(result['cards'])==len(selected)
result.update(modelUsage=response.get('modelUsage'),requestSha256=hashlib.sha256(prompt.encode()).hexdigest(),date='2026-11-09',kind='editorial_contribution_not_external_review')
(OUT/(prefix+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Completed',batch,len(result['cards']),response.get('modelUsage'),flush=True)
