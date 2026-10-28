"""Acquisizioni datate del gruppo di sei espansioni 2025, senza prezzi."""
import hashlib
import json
import time
import urllib.request
from pathlib import Path

DATE = '2026-10-28'
GROUPS = {
 'through-the-omenpaths': ['om1'],
 'marvel-spider-man': ['spm','mar','spe'],
 'edge-of-eternities': ['eoe','eos','spg','eoc'],
 'final-fantasy': ['fin','fca','fic'],
 'tarkir-dragonstorm': ['tdm','spg','tdc'],
 'aetherdrift': ['dft','spg','drc'],
}
def fetch(url):
 req = urllib.request.Request(url,headers={'User-Agent':'MTGAnalyzer/1.0 (catalog research)','Accept':'application/json,text/html'})
 for attempt in range(4):
  try:
   with urllib.request.urlopen(req,timeout=90) as response:
    return response.read()
  except Exception:
   if attempt == 3: raise
   time.sleep(2 + attempt)

def main():
 cache = {}
 for slug,codes in GROUPS.items():
  folder = Path('research') / (slug+'-20261028')
  folder.mkdir(parents=True,exist_ok=True)
  audit=[]
  for code in codes:
   if code not in cache:
    meta_url='https://api.scryfall.com/sets/'+code
    meta_bytes=fetch(meta_url); meta=json.loads(meta_bytes)
    pages=[]; url=meta['search_uri']; rows=[]
    while url:
     raw=fetch(url); page=json.loads(raw); pages.append((url,raw)); rows.extend(page['data'])
     url=page.get('next_page') if page.get('has_more') else None
     time.sleep(.15)
    # Pricing providers other than Cardmarket are not imported into active datasets.
    cache[code]=(meta_url,meta_bytes,pages,rows)
   meta_url,meta_bytes,pages,rows=cache[code]
   (folder/(code+'-set.json')).write_bytes(meta_bytes)
   for n,(url,raw) in enumerate(pages,1):
    name=code+'-page-'+str(n)+'.json'; (folder/name).write_bytes(raw)
    audit.append({'provider':'Scryfall','url':url,'retrieved':DATE,'status':'acquired','file':name,'sha256':hashlib.sha256(raw).hexdigest(),'rows':len(json.loads(raw)['data'])})
   (folder/(code+'-cards.json')).write_text(json.dumps({'retrieved':DATE,'provider':'Scryfall','code':code,'cards':rows,'pages':len(pages)},ensure_ascii=False,indent=2),encoding='utf-8')
   print(slug,code,len(rows),flush=True)
  (folder/'fetch-audit.json').write_text(json.dumps({'retrieved':DATE,'acquisitions':audit},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__ == '__main__': main()
