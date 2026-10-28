"""Acquire and match original Draftsim Limited grades by exact Oracle name."""
import concurrent.futures
import hashlib
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path('research').resolve()))
from enrich_recent_sets_20261028 import blocks,key
from integrate_middle_sets_20261028 import CONFIG, DATE
from research_middle_sets_20261028 import fetch
from import_expansion_catalogs import write_json

def acquire(item):
 slug,cfg=item;code=cfg[1]
 source_code='spm' if code=='om1' else code
 url='https://draftsim.com/mtg-'+source_code+'-limited-set-review/'
 research=Path('research')/(slug+'-20261028');dest=Path('expansions')/slug
 audit=json.loads((research/'fetch-audit.json').read_text(encoding='utf-8'))
 try:
  raw=fetch(url);path=research/'limited-review.html';path.write_bytes(raw)
  metadata=raw.decode('utf-8','replace')
  author_match=re.search(r'"author"\s*:\s*\{\s*"name"\s*:\s*"([^"]+)"',metadata)
  author=author_match.group(1) if author_match else 'Autore da verificare'
  published_match=re.search(r'"datePublished"\s*:\s*"([^"]+)"',metadata)
  published=published_match.group(1)[:10] if published_match else None
  audit['acquisitions'].append({'provider':'Draftsim','id':'limited-review','url':url,'retrieved':DATE,'status':'acquired','file':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
 except Exception as exc:
  audit['acquisitions'].append({'provider':'Draftsim','url':url,'retrieved':DATE,'status':'unavailable','error':str(exc)});write_json(research/'fetch-audit.json',audit);return(slug,str(exc))
 doc=json.loads((dest/'cards.json').read_text(encoding='utf-8'));catalog=doc['cards'];lookup={}
 for c in catalog:
  for name in [c['name'],c.get('oracleName',''),c.get('printedName','')]+[f['name'] for f in c.get('faces',[])]:
   if name:lookup[key(name)]=c
 ratings={};headings=[];unmatched=[];active=None
 for tag,text in blocks(path):
  if tag in ['h2','h3','h4','h5']:
   candidate=re.sub(r'^#?\d+\.\s*','',text);candidate=re.sub(r'\s*\([^)]*\)\s*$','',candidate)
   active=lookup.get(key(candidate))
   if active:headings.append({'catalogId':active['id'],'name':active['name'],'heading':text})
  elif tag=='p':
   rating=re.fullmatch(r'Rating:\s*([0-9]+(?:\.[0-9]+)?)/10',text)
   if rating and active:
    value=float(rating.group(1));assert 0<=value<=10
    ratings[active['id']]={'score':value/2,'why':f'Valutazione Limited iniziale Draftsim: {value:g}/10. Conversione lineare in scala 0-5.','condition':'Opinione iniziale attribuita, distinta dai risultati osservati e dalle guide successive.','evidence':[{'author':author,'published':published,'original':f'{value:g}/10','stars':value/2,'url':url,'retrieved':DATE,'kind':'Recensione Limited iniziale','scale':{'min':0,'max':10,'conversion':'score = original / 2'}}]}
   elif rating:unmatched.append(text)
 write_json(dest/'ratings.json',{'date':DATE,'source':url,'method':'Titoli abbinati esattamente ai nomi Oracle o alle facce, voti originali 0-10 divisi per due. Nessun valore stimato.','cards':ratings})
 observations={}
 for identity,value in ratings.items():
  n=value['score']*2
  observations[identity]={'tone':'positivo' if n>=7 else 'negativo' if n<=3 else 'condizionato','breadth':'Recensione Limited numerica iniziale','summary':f'Draftsim: {n:g}/10. Controlla la guida successiva per le revisioni del giudizio.','sources':[{'id':'limited-review','label':'Draftsim, '+author,'url':url,'kind':'Limited','retrieved':DATE,'published':published}],'observations':[{'source':'limited-review','tone':'condizionato','text':f'Voto iniziale {n:g}/10, non una misura di vittorie.'}]}
 write_json(dest/'sentiment.json',{'meta':{'isoDate':DATE,'covered':len(observations),'method':'Voti attribuiti e abbinati esattamente, senza riprodurre la prosa della recensione.'},'cards':observations})
 source_doc=json.loads((dest/'sources.json').read_text(encoding='utf-8'))
 source_doc['links']['limited-review']=url
 source_doc['research']['sources'].append({'id':'limited-review','label':'Draftsim: recensione Limited e scala numerica originale','url':url,'author':author,'published':published,'retrieved':DATE,'status':'acquired_and_integrated','coverage':{'catalogCards':len(catalog),'ratedCards':len(ratings)},'limitation':'Le carte senza voto numerico singolo restano prive di rating. Una recensione iniziale non equivale ai risultati del formato.'})
 write_json(dest/'sources.json',source_doc)
 write_json(research/'matched-review-observations.json',{'date':DATE,'source':url,'headings':headings,'ratedCards':len(ratings),'catalogCards':len(catalog),'missingCardIds':[c['id'] for c in catalog if c['id'] not in ratings],'unmatchedRatings':unmatched})
 write_json(research/'fetch-audit.json',audit)
 return slug,len(ratings)

if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for result in pool.map(acquire,CONFIG.items()):print(result,flush=True)
