"""Acquire public official tournament lists. Never used by the offline build."""
import argparse,concurrent.futures,hashlib,html,json,re,time,urllib.request
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

FORMATS={'standard':'Standard','pioneer':'Pioneer','modern':'Modern','pauper':'Pauper'}
WIZARDS=[
 ('pt-sos-2026','standard','historical-pro-tour','https://magic.gg/decklists/pro-tour-secrets-of-strixhaven-standard-decklists-'+suffix) for suffix in ['a-f','g-l','m-r','s-z']
]+[
 ('pt-msh-2026','modern','historical-pro-tour','https://magic.gg/decklists/pro-tour-marvel-super-heroes-modern-decklists-'+suffix) for suffix in ['a-e','f-k','l-p','r-z']
]+[
 ('arena-championship-13','standard','recent-premier','https://magic.gg/decklists/arena-championship-13-standard-decklists-'+suffix) for suffix in ['a-k','l-z']
]+[
 ('rc-los-angeles-20261011','modern','recent-published-top-finishers','https://magic.gg/decklists/united-states-regional-championships-los-angeles-october-2026-top-32-modern-decklists')
]
WIZARDS += [('pt-mkm-2024','pioneer','historical-pro-tour','https://magic.gg/decklists/pro-tour-murders-at-karlov-manor-pioneer-decklists-'+suffix) for suffix in ['a-d','e-j','k-n','o-s','t-z']]
class Attrs(HTMLParser):
 def __init__(self,s):super().__init__();self.attrs={};self.feed(s)
 def handle_starttag(self,t,a):self.attrs=dict(a)
def fetch(url):
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'MTG-Analyzer-Research/1.0','Accept':'text/html'})
   with urllib.request.urlopen(req,timeout=60) as r:return r.read()
  except Exception:
   if attempt==2:raise
   time.sleep(1+attempt)
def count_lines(s):
 s=re.sub(r'<br\s*/?>','\n',s,flags=re.I);s=re.sub('<[^>]+>','',s);out=Counter()
 for line in html.unescape(s).splitlines():
  if not line.strip():continue
  m=re.fullmatch(r'\s*(\d+)\s+(.+?)\s*',line)
  if not m:raise ValueError('Unrecognized card line: '+line[:100])
  out[m[2]]+=int(m[1])
 return dict(out)
def parse_wizards(text,url,event_id,format,kind):
 decks=[];dates=set();names=set()
 for block in re.finditer(r'(<deck-list\b[^>]*>)(.*?)</deck-list>',text,re.S|re.I):
  a=Attrs(block[1]).attrs;body=block[2]
  if a.get('format','').lower()!=format:raise ValueError('Unexpected format')
  md=re.search(r'<main-deck[^>]*>(.*?)</main-deck>',body,re.S|re.I);sb=re.search(r'<side-board[^>]*>(.*?)</side-board>',body,re.S|re.I)
  if not md:raise ValueError('Missing main deck')
  event_date=date.fromisoformat(__import__('datetime').datetime.strptime(a['event-date'],'%B %d, %Y').strftime('%Y-%m-%d')).isoformat();dates.add(event_date);names.add(a.get('event-name',event_id))
  decks.append({'id':event_id+':'+a['deck-title'],'player':a['deck-title'],'archetype':a.get('subtitle',''),'main':count_lines(md[1]),'sideboard':count_lines(sb[1]) if sb else {},'rank':None,'wins':None,'losses':None,'sourceUrl':url})
 if not decks or len(dates)!=1:raise ValueError('Missing lists or mixed dates')
 return {'id':event_id,'name':next(iter(names)),'date':dates.pop(),'format':format,'kind':kind,'publishedCoverage':'complete-field-published-in-parts' if kind in ['historical-pro-tour','recent-premier'] else 'published-top-finishers','players':None,'decks':decks,'url':url}
def parse_mtgo(text,url):
 matches=list(re.finditer(r'window\.MTGO\.decklists\.data\s*=\s*',text));data=None
 for m in matches:
  try:
   candidate,_=json.JSONDecoder().raw_decode(text[m.end():])
   if isinstance(candidate,dict) and 'decklists' in candidate:data=candidate;break
  except ValueError:pass
 if data is None:raise ValueError('Public decklist payload not found')
 format=next((f for f in FORMATS if f in data['format'].lower()),None)
 if not format:raise ValueError('Unsupported format: '+data['format'])
 ranks={r['loginid']:int(r['rank']) for r in (data.get('final_rank') or [])};results={r['loginid']:r for r in (data.get('winloss') or [])};decks=[]
 for d in data['decklists']:
  sections={}
  for field,key in [('main_deck','main'),('sideboard_deck','sideboard')]:
   counts=Counter()
   for c in (d.get(field) or []):counts[c['card_attributes']['card_name']]+=int(c['qty'])
   sections[key]=dict(counts)
  result=results.get(d['loginid'],{})
  decks.append({'id':'mtgo:'+data['event_id']+':'+d['loginid'],'player':d['player'],'archetype':'','rank':ranks.get(d['loginid']),'wins':int(result['wins']) if 'wins' in result else None,'losses':int(result['losses']) if 'losses' in result else None,'sourceUrl':url,**sections})
 players=int(data['player_count']['players']) if data.get('player_count') else None
 return {'id':'mtgo:'+data['event_id'],'name':data['description'],'date':data['starttime'][:10],'format':format,'kind':'recent-mtgo-challenge','publishedCoverage':'complete-field' if players==len(decks) else 'published-lists-only','players':players,'decks':decks,'url':url}
def acquire(spec,out):
 url=spec[-1];path=out/(hashlib.sha256(url.encode()).hexdigest()[:16]+'.json')
 if path.exists():
  cached=json.loads(path.read_text(encoding='utf-8'))
  if 'decks' in cached:return cached
 try:
  for attempt in range(3):
   raw=fetch(url);text=raw.decode('utf-8')
   try:event=parse_mtgo(text,url) if spec[0]=='mtgo' else parse_wizards(text,url,*spec[:3]);break
   except ValueError:
    if attempt==2:raise
    time.sleep(2+attempt)
  seen=set()
  for d in event['decks']:
   if d['id'] in seen:raise ValueError('Duplicate deck identity')
   seen.add(d['id'])
   if not 60<=sum(d['main'].values())<=250 or not 0<=sum(d['sideboard'].values())<=15:raise ValueError('Unexpected deck size: '+d['player'])
  event.update({'retrieved':date.today().isoformat(),'publisher':'Magic Online' if spec[0]=='mtgo' else 'Wizards of the Coast / Magic.gg','sha256':hashlib.sha256(raw).hexdigest(),'sourceBytes':len(raw)})
 except Exception as e:event={'url':url,'status':'unavailable','error':str(e),'retrieved':date.today().isoformat()}
 path.write_text(json.dumps(event,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return event
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--workers',default=5,type=int);a=p.parse_args();out=a.output/'events';out.mkdir(parents=True,exist_ok=True)
 index=fetch('https://www.mtgo.com/decklists/').decode('utf-8');links=list(dict.fromkeys(html.unescape(u) for u in re.findall(r'href=[\"\'](/decklist/[^\"\']+)',index)))
 selected=[u for u in links if re.search(r'/(standard|pioneer|modern|pauper)-(?:.*challenge|.*qualifier)',u) and re.search(r'2026-10-\d{2}',u)]
 specs=[('mtgo',None,None,'https://www.mtgo.com'+u) for u in selected]+WIZARDS
 (a.output/'inventory.json').write_text(json.dumps({'retrieved':date.today().isoformat(),'indexUrl':'https://www.mtgo.com/decklists/','selection':'All four-format Challenges, Showcase Challenges and Qualifiers linked in the October 2026 official archive, plus selected premier events and historical Pro Tours. Leagues excluded.','sources':[s[-1] for s in specs]},indent=2)+'\n',encoding='utf-8')
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
  results=list(pool.map(lambda s:acquire(s,out),specs))
 (a.output/'acquisition.json').write_text(json.dumps([{'url':r['url'],'status':r.get('status','ok'),'id':r.get('id'),'decks':len(r.get('decks',[])),'error':r.get('error')} for r in results],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'sources':len(results),'successful':sum('decks' in r for r in results),'decks':sum(len(r.get('decks',[])) for r in results),'errors':[r for r in results if 'decks' not in r]},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
