"""Acquire dated public Star Trek research. Never used by the offline build."""
import concurrent.futures,hashlib,json,tempfile,urllib.request
from html.parser import HTMLParser
from pathlib import Path
DATE='2026-10-28'
OUT=Path('research/star-trek-20261028');OUT.mkdir(parents=True,exist_ok=True)
CACHE=Path(tempfile.gettempdir())/'mtg-star-trek-research-20261028';CACHE.mkdir(exist_ok=True)
SOURCES=[
('wizards-collecting','Wizards of the Coast','official-product','https://magic.wizards.com/en/news/feature/collecting-star-trek'),
('wizards-mechanics','Wizards of the Coast','official-rules','https://magic.wizards.com/en/news/feature/star-trek-mechanics'),
('wizards-previews','Wizards of the Coast','official-calendar','https://magic.wizards.com/en/news/announcements/where-to-find-star-trek-previews'),
('wizards-arena','Wizards of the Coast','official-calendar','https://magic.wizards.com/en/news/mtg-arena/star-trek-event-schedule'),
('scg-gallery','Star City Games','preview-gallery','https://articles.starcitygames.com/magic-the-gathering/every-card-revealed-so-far-from-magic-the-gathering-star-trek/'),
('standard-preview-ratings','MTG-Standard','automated-constructed-ratings','https://www.mtg-standard.com/powerating/TRK'),
('standard-method','MTG-Standard','methodology','https://www.mtg-standard.com/power-rating-system'),
('meta-limited-preview','MTGMeta','prediction-not-observed-games','https://mtgmeta.com/limited/trk'),
('collectorunion-review','CollectorUnion','commander-editorial','https://collectorunion.com/blog/magic-star-trek-revealed-cards-first-impressions'),
('draftsim-collective-review','Draftsim','commander-editorial','https://draftsim.com/mtg-star-trek-join-the-collective-leak/'),
('deathmarked-cruiser','Deathmarked','constructed-editorial','https://deathmarked.info/d-7-battle-cruiser-magic-the-gathering-card-preview-standard-potential/'),
('deathmarked-munitions','Deathmarked','constructed-editorial','https://deathmarked.info/munitions-enthusiast-star-trek-mtg-card-review-and-potential/'),
('card-kingdom','Card Kingdom','product-overview','https://blog.cardkingdom.com/star-trek-first-look/'),
('goldfish-previews','MTGGoldfish','preview-gallery','https://www.mtggoldfish.com/articles/star-trek-spoilers-october-21-26-borg-commander-precon'),
('edhrec-debut','EDHREC','commander-editorial','https://edhrec.com/articles/star-trek-debut-stream-preview-recap'),
('arenazone-limited','MTG Arena Zone','limited-index','https://mtgazone.com/limited/'),
('untapped-pick-order','Untapped.gg','limited-ranking-availability','https://mtga.untapped.gg/limited/draft/star-trek/pick-order'),
('cardmarket-spoiler','Cardmarket','marketplace','https://www.cardmarket.com/en/Magic/Spoilers/Star-Trek'),
]
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style'):self.skip+=1
  if tag in ('p','div','li','tr','td','h1','h2','h3','a','br'):self.parts.append('\n')
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.skip=max(0,self.skip-1)
  if tag in ('p','div','li','tr','td','h1','h2','h3','a'):self.parts.append('\n')
 def handle_data(self,data):
  if not self.skip:self.parts.append(data)
 def text(self):return '\n'.join(x.strip() for x in ''.join(self.parts).splitlines() if x.strip())
def download(source):
 ident,publisher,kind,url=source;r=dict(id=ident,publisher=publisher,kind=kind,url=url,retrieved=DATE)
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'MTG-Analyzer-Research/1.0','Accept':'text/html'})
  with urllib.request.urlopen(req,timeout=30) as response:raw=response.read();r['finalUrl']=response.url
  p=Parser();p.feed(raw.decode('utf-8',errors='replace'));text=p.text()
  (CACHE/(ident+'.html')).write_bytes(raw);(CACHE/(ident+'.txt')).write_text(text,encoding='utf-8')
  r.update(status='retrieved' if len(text)>300 else 'application-shell',bytes=len(raw),textCharacters=len(text),sha256=hashlib.sha256(raw).hexdigest())
 except Exception as e:r.update(status='unavailable',error=str(e))
 return r
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:records=list(pool.map(download,SOURCES))
 (OUT/'source-audit.json').write_text(json.dumps({'date':DATE,'sources':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for r in records:print(r['id'],r['status'],r.get('textCharacters',r.get('error')))
 print('Cache:',CACHE)
