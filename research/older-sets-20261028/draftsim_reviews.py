"""Acquire Draftsim numerical reviews and merge attributed evidence per card."""
import concurrent.futures, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'research'))
from enrich_recent_sets_20261028 import blocks,key
from import_expansion_catalogs import write_json
from acquire import SETS, fetch
def run(spec):
 slug,code,*_=spec; d=ROOT/'research'/f'{slug}-20261028';audit=[];url=f'https://draftsim.com/mtg-{code.lower()}-limited-set-review/';raw=(d/'draftsim-numeric-review.html').read_bytes() if (d/'draftsim-numeric-review.html').exists() else fetch(url,d/'draftsim-numeric-review.html',audit)
 if not raw:write_json(d/'draftsim-review-audit.json',{'acquisitions':audit});return
 author_match=re.search(r'"author"\s*:\s*\{\s*"name"\s*:\s*"([^"]+)"',raw.decode('utf8')); author=author_match[1] if author_match else 'Autore da verificare'
 out=ROOT/'expansions'/slug;cards=json.loads((out/'cards.json').read_text())['cards'];lookup={key(c['name']):c for c in cards}
 for c in cards:
  for f in c.get('faces',[]):lookup[key(f['name'])]=c
 ratings=json.loads((out/'ratings.json').read_text());sentiment={'meta':{'isoDate':'2026-10-28','method':'Titoli e voti attribuiti abbinati a nomi Oracle; nessuna osservazione inventata.'},'cards':{}};heading=None;matches=[]
 for tag,text in blocks(d/'draftsim-numeric-review.html'):
  if tag in ('h2','h3','h4','h5'):
   heading=lookup.get(key(re.sub(r'\s*\([^)]*\)\s*$','',text)))
   if heading:sentiment['cards'][heading['id']]={'tone':'condizionato','breadth':'Recensione Limited','summary':'La fonte contiene una valutazione specifica della carta.','sources':[{'id':'draftsim-numeric-review','label':'Recensione Limited Draftsim','url':url,'kind':'Limited','retrieved':'2026-10-28','heading':text}]}
  elif heading and tag=='p':
   m=re.fullmatch(r'Rating\s*:\s*([0-9]+(?:\.[0-9]+)?)/10',text)
   if not m:continue
   original=float(m[1]);score=original/2
   row=ratings['cards'].get(heading['id'])
   evidence={'author':author,'original':f'{original:g}/10','stars':score,'url':url,'kind':'Recensione Limited Draftsim','retrieved':'2026-10-28','scale':{'min':0,'max':10,'conversion':'score = original / 2'}}
   if row:row.setdefault('evidence',[]).append(evidence)
   else:ratings['cards'][heading['id']]={'score':score,'why':f'Valutazione Limited Draftsim {original:g}/10, convertita linearmente nella scala 0-5.','condition':'Voto editoriale iniziale, distinto da risultati osservati.','evidence':[evidence]}
   sentiment['cards'][heading['id']]['summary']=f'Draftsim assegna {original:g}/10 nella recensione Limited iniziale.';matches.append({'catalogId':heading['id'],'name':heading['name'],'original':original,'score':score})
 ratings['date']='2026-10-28';ratings['coverage']={'rated':len(ratings['cards']),'catalogCards':len(cards),'missingIds':[c['id'] for c in cards if c['id'] not in ratings['cards']]};sentiment['meta']['covered']=len(sentiment['cards'])
 write_json(out/'ratings.json',ratings);write_json(out/'sentiment.json',sentiment);write_json(d/'draftsim-review-audit.json',{'acquisitions':audit,'matched':matches});print(code,'Draftsim',len(matches),'total',len(ratings['cards']),flush=True)
 sources=json.loads((out/'sources.json').read_text());sources['research']['sources'].append({'id':'draftsim-numeric-review','url':url,'label':'Recensione Limited numerica Draftsim','retrieved':'2026-10-28','status':'acquired'});write_json(out/'sources.json',sources)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,SETS))
