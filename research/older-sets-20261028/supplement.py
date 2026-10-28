"""Broaden source checks; availability is not represented as per-card coverage."""
import concurrent.futures, hashlib, html, json, re, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from import_expansion_catalogs import write_json
from acquire import SETS
def run(spec):
 slug,code,*_=spec; d=ROOT/'research'/f'{slug}-20261028';rows=[]
 article={'foundations':'foundations-set-review-black','duskmourn':'duskmourn-set-review-black','bloomburrow':'bloomburrow-set-review-black','outlaws-of-thunder-junction':'outlaws-of-thunder-junction-set-review-black','murders-at-karlov-manor':'murders-at-karlov-manor-set-review-black','lost-caverns-of-ixalan':'the-lost-caverns-of-ixalan-set-review-black','wilds-of-eldraine':'wilds-of-eldraine-set-review-black'}[slug]
 urls=[('EDHREC',f'https://edhrec.com/articles/{article}'),('MTGGoldfish',f'https://www.mtggoldfish.com/articles/search?q={slug.replace("-","+")}'),('MTGDECKS',f'https://mtgdecks.net/{code}'),('Untapped',f'https://mtga.untapped.gg/limited/draft/{slug}/card-data'),('Card Kingdom',f'https://blog.cardkingdom.com/{slug}-draft-guide/'),('Cards Realm',f'https://mtg.cardsrealm.com/en-us/sets/{code.lower()}-{slug}')]
 for provider,url in urls:
  entry={'provider':provider,'url':url,'retrieved':'2026-10-28','dataIntegrated':False}
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'MTGAnalyzerResearch/1.0'})
   with urllib.request.urlopen(req,timeout=20) as response:raw=response.read();entry.update(status=response.status,resolvedUrl=response.url,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
   text=raw.decode('utf8','replace');title=re.search(r'<title[^>]*>(.*?)</title>',text,re.S|re.I);entry['title']=html.unescape(re.sub('<[^>]*>','',title[1])).strip() if title else None
   # Preserve readable evidence. Marketplace prices from other providers are not imported.
   if provider in ('EDHREC','Card Kingdom'):
    text=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',text,flags=re.S|re.I);text=html.unescape(re.sub('<[^>]*>','\n',text));text=re.sub(r'\n[ \t]*\n+','\n\n',text);file=provider.lower().replace(' ','-')+'-supplement.txt';(d/file).write_text(text,encoding='utf8');entry['snapshot']=file
   entry['limitation']='Pagina acquisita; nessuna estrazione sistematica delle osservazioni per carta da questa fonte. Tabelle dinamiche, contenuti bloccati o pagina indice non equivalgono a dati acquisiti.'
  except Exception as e:entry.update(status='unavailable',error=str(e),limitation='Nessun dato estratto; fonte candidata non verificata per copertura.')
  rows.append(entry)
 write_json(d/'supplemental-source-audit.json',{'date':'2026-10-28','scope':'Verifiche di accesso supplementari, distinte dalle recensioni per carta già integrate.','sources':rows});print(code,[(r['provider'],r['status']) for r in rows],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,SETS))
