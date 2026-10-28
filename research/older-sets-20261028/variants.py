"""Certify pagination including non-default variations and enrich print identities."""
import concurrent.futures, json, sys, time, urllib.parse
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from import_expansion_catalogs import write_json, normalize_printing
from acquire import SETS, fetch
def run(spec):
 slug,code,*_=spec;d=ROOT/'research'/f'{slug}-20261028';audit=json.loads((d/'fetch-audit.json').read_text());raws={}
 for p in d.glob('scryfall-catalog-*.json'):
  for r in json.loads(p.read_text())['cards']:raws[r['id']]=r
 before=set(raws);queries=[json.loads(p.read_text())['query'] for p in sorted(d.glob('scryfall-catalog-*.json'))]; new=[]
 for qi,q in enumerate(queries):
  url='https://api.scryfall.com/cards/search?'+urllib.parse.urlencode({'q':q,'unique':'prints','order':'set','include_extras':'true','include_variations':'true'});pages=0;count=0
  while url:
   pages+=1;p=d/f'variants-{qi}-{pages}.json';raw=fetch(url,p,audit['acquisitions'])
   if raw is None:break
   data=json.loads(raw);count+=len(data.get('data',[]))
   for r in data.get('data',[]):
    if r.get('layout') in ('token','double_faced_token','art_series','emblem') or r.get('oversized'):continue
    if r['id'] not in raws:new.append(r)
    raws[r['id']]=r
   p.unlink();url=data.get('next_page') if data.get('has_more') else None;time.sleep(.12)
  audit.setdefault('variantPagination',[]).append({'query':q,'include_extras':True,'include_variations':True,'pages':pages,'returnedPrintings':count,'complete':bool(raw) and not url})
 write_json(d/'scryfall-additional-variations.json',{'date':'2026-10-28','cards':new,'note':'Only identities absent from the original, fully paginated snapshots; token/emblem/art/oversized objects excluded.'})
 out=ROOT/'expansions'/slug; document=json.loads((out/'cards.json').read_text()); old={(c['set'],c.get('oracleId') or c['name']):c for c in document['cards']};grouped=defaultdict(list)
 for r in raws.values():grouped[(r['set'].upper(),r.get('oracle_id') or r['name'])].append(r)
 cards=[];prints=[]
 for key,entries in grouped.items():
  card=old.get(key) or normalize_printing(entries[0]);card['prints']=[]
  for r in entries:
   p=normalize_printing(r);p['catalogId']=card['id'];prints.append(p);card['prints'].append({'id':p['id'],'number':p['number'],'image':p['image'],'finishes':p['finishes'],'url':p['url'],'set':p['set']})
  cards.append(card)
 document.update(cards=cards,print_count=len(prints));document['coverage']['pagination']={'include_extras':True,'include_variations':True,'complete':all(x['complete'] for x in audit['variantPagination']),'excludedLayouts':['token','double_faced_token','emblem','art_series'],'additionalPrintings':len(set(raws)-before)}
 write_json(out/'cards.json',document);write_json(out/'printings.json',{'date':'2026-10-28','cards':prints});write_json(d/'fetch-audit.json',audit);print(code,len(cards),len(prints),'additional',len(new),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,SETS))
