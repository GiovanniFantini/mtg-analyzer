"""Companion products are acquired separately and never added to Limited pools."""
import concurrent.futures, json, sys, time, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from import_expansion_catalogs import write_json
from acquire import fetch
RELATED={'foundations':[],'duskmourn':['dsc'],'bloomburrow':['blc'],'outlaws-of-thunder-junction':['otc'],'murders-at-karlov-manor':['mkc'],'lost-caverns-of-ixalan':['lcc','rex'],'wilds-of-eldraine':['woc']}
def run(item):
 slug,codes=item;d=ROOT/'research'/f'{slug}-20261028';audit=[];catalogs=[]
 for code in codes:
  url='https://api.scryfall.com/cards/search?'+urllib.parse.urlencode({'q':'set:'+code,'unique':'prints','order':'set','include_extras':'true','include_variations':'true'});cards=[];pages=0;complete=False
  while url:
   pages+=1;p=d/f'companion-{code}-page-{pages}.json';raw=fetch(url,p,audit)
   if not raw:break
   data=json.loads(raw)
   cards.extend(c for c in data.get('data',[]) if c.get('layout') not in ('token','double_faced_token','emblem','art_series') and not c.get('oversized'))
   url=data.get('next_page') if data.get('has_more') else None;complete=not url;time.sleep(.1)
  target=d/f'companion-{code}-catalog.json';write_json(target,{'date':'2026-10-28','code':code.upper(),'completePagination':complete,'pages':pages,'excludedFromLimitedPool':True,'cards':cards});catalogs.append({'code':code.upper(),'path':str(target.relative_to(ROOT)).replace('\\','/'),'printings':len(cards),'identities':len({c.get('oracle_id') or c['name'] for c in cards}),'completePagination':complete,'pages':pages,'excludedFromLimitedPool':True})
 manifest_path=ROOT/'expansions'/slug/'expansion.json';manifest=json.loads(manifest_path.read_text());manifest['researchAppendices']={'date':'2026-10-28','catalogs':catalogs,'limitations':['Appendici di prodotti distinti. Le carte non vengono immesse automaticamente nei pool Limited né nella collazione.']}
 if slug=='foundations':manifest['researchAppendices']['limitations'].append('Foundations Jumpstart J25 è un prodotto autonomo, non acquisito in questo inserimento FDN. Starter Collection e Beginner Box FDN sono incluse nel catalogo del codice principale; appartenenza ai prodotti distinta.')
 write_json(manifest_path,manifest);write_json(d/'companion-catalogs-audit.json',{'date':'2026-10-28','catalogs':catalogs,'acquisitions':audit});print(slug,[(x['code'],x['printings']) for x in catalogs],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,RELATED.items()))
