"""Dated acquisition for the seven 2023/24 expansions; no build dependency."""
import concurrent.futures, hashlib, html, json, re, time, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SETS=[('foundations','FDN','2024-11-12','2025-02-10',[]),('duskmourn','DSK','2024-09-24','2024-11-11',['set:spg cn>=64 cn<=73']),('bloomburrow','BLB','2024-07-30','2024-09-23',['set:spg cn>=54 cn<=63']),('outlaws-of-thunder-junction','OTJ','2024-04-16','2024-07-29',['set:otp','set:big','set:spg cn>=29 cn<=38']),('murders-at-karlov-manor','MKM','2024-02-06','2024-04-15',['set:spg cn>=19 cn<=28']),('lost-caverns-of-ixalan','LCI','2023-11-14','2024-02-05',[]),('wilds-of-eldraine','WOE','2023-09-05','2023-11-13',['set:wot'])]
def write(p,d):
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def fetch(url,path,audit):
 for attempt in range(4):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'MTGAnalyzerResearch/1.0','Accept':'application/json,text/html;q=0.9'})
   with urllib.request.urlopen(req,timeout=90) as r: raw=r.read(); status=r.status; actual=r.url
   path.write_bytes(raw); audit.append({'url':url,'resolvedUrl':actual,'file':path.name,'status':status,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'retrieved':'2026-10-28'})
   return raw
  except Exception as e:
   if attempt==3: audit.append({'url':url,'file':path.name,'status':'failed','error':str(e),'retrieved':'2026-10-28'}); return None
   time.sleep(1+attempt)
def run(spec):
 slug,code,start,end,extras=spec; directory=ROOT/'research'/f'{slug}-20261028'; directory.mkdir(exist_ok=True); audit=[]
 fetch(f'https://api.scryfall.com/sets/{code.lower()}',directory/'scryfall-set.json',audit)
 for ix,q in enumerate([f'set:{code.lower()}']+extras):
  url='https://api.scryfall.com/cards/search?'+urllib.parse.urlencode({'q':q,'unique':'prints','order':'set','include_extras':'false'}); cards=[]; pages=0
  while url:
   pages+=1; raw=fetch(url,directory/f'scryfall-{ix}-page-{pages}.json',audit)
   if not raw: break
   data=json.loads(raw); cards.extend(data.get('data',[])); url=data.get('next_page') if data.get('has_more') else None; time.sleep(.12)
  write(directory/f'scryfall-catalog-{ix}.json',{'query':q,'pages':pages,'complete':bool(raw) and not url,'cards':cards,'retrieved':'2026-10-28'})
 officialslug={'FDN':'foundations','DSK':'duskmourn','BLB':'bloomburrow','OTJ':'outlaws-of-thunder-junction','MKM':'murders-at-karlov-manor','LCI':'the-lost-caverns-of-ixalan','WOE':'wilds-of-eldraine'}[code]
 urls={'wizards-collecting':f'https://magic.wizards.com/en/news/feature/collecting-{officialslug}','wizards-mechanics':f'https://magic.wizards.com/en/news/feature/{officialslug}-mechanics','wizards-release-notes':f'https://magic.wizards.com/en/news/feature/{officialslug}-release-notes','draftsim-guide':f'https://draftsim.com/mtg-{code.lower()}-draft-guide/','draftsim-review':f'https://draftsim.com/{code.lower()}-limited-set-review/','cardmarket-set':f'https://www.cardmarket.com/en/Magic/Expansions/{officialslug.title()}'}
 if code=='MKM': urls['wizards-list']='https://magic.wizards.com/en/news/announcements/whats-new-on-the-list-for-murders-at-karlov-manor'
 for label,url in urls.items():
  raw=fetch(url,directory/f'{label}.html',audit)
  if raw:
   txt=raw.decode('utf-8','replace'); txt=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',txt,flags=re.S|re.I); txt=html.unescape(re.sub('<[^>]+>','\n',txt)); txt=re.sub(r'\n[ \t]*\n+', '\n\n',txt); (directory/f'{label}.txt').write_text(txt,encoding='utf-8')
 write(directory/'fetch-audit.json',{'date':'2026-10-28','set':code,'acquisitions':audit}); print(code,len(audit),flush=True)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(run,SETS))
