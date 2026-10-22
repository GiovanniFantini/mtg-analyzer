"""Fetch dated public research inputs. Never runs during the offline site build."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
import urllib.request
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'research' / 'reality-fracture-20261022'
OUT.mkdir(parents=True, exist_ok=True)
CACHE = Path(os.environ.get('MTG_RESEARCH_CACHE',str(Path(tempfile.gettempdir())/'mtg-research-fra-20261022')))
CACHE.mkdir(parents=True, exist_ok=True)
SOURCES = [
 ('wizards-standard', 'Wizards / Magic.gg', 'tournament-analysis', 'https://magic.gg/news/metagame-mentor-the-first-standard-results-with-reality-fracture'),
 ('wizards-modern', 'Wizards / Magic.gg', 'tournament-analysis', 'https://magic.gg/news/metagame-mentor-modern-developments-at-five-2026-fall-regional-championships'),
 ('wizards-banlist', 'Wizards / Magic.gg', 'official-policy', 'https://magic.wizards.com/en/news/announcements/banned-and-restricted-october-12-2026'),
 ('wizards-release', 'Wizards / Magic.gg', 'official-rules', 'https://magic.wizards.com/en/news/feature/reality-fracture-release-notes'),
 ('wizards-collecting', 'Wizards / Magic.gg', 'official-product', 'https://magic.wizards.com/en/news/feature/collecting-reality-fracture'),
 ('postboard', 'Postboard', 'tournament-aggregation', 'https://www.postboard.gg/sets/fra'),
 ('edhrec', 'EDHREC', 'deck-aggregation', 'https://edhrec.com/sets/fra'),
 ('edhrec-review', 'EDHREC', 'editorial-review', 'https://edhrec.com/articles/how-good-is-reality-fracture-for-commander'),
 ('goldfish-vintage', 'MTGGoldfish', 'editorial-review', 'https://www.mtggoldfish.com/articles/vintage-101-reality-is-doomed'),
 ('mtgdecks', 'MTGDECKS', 'tournament-market-aggregation', 'https://mtgdecks.net/prices/edition/FRA'),
 ('cardsrealm-cedh', 'Cards Realm', 'editorial-review', 'https://mtg.cardsrealm.com/en-us/articles/cedh-reality-fracture-review'),
 ('cardsrealm-pauper', 'Cards Realm', 'editorial-review', 'https://mtg.cardsrealm.com/en-us/articles/pauper-reality-fracture-review'),
 ('arenazone', 'MTG Arena Zone', 'limited-review', 'https://mtgazone.com/reality-fracture-fra-limited-set-review-artifacts-and-lands/'),
 ('draftsim', 'Draftsim', 'limited-review', 'https://draftsim.com/mtg-fra-limited-set-review/'),
 ('pauperpilot', 'PauperPilot', 'tournament-aggregation', 'https://pauperpilot.com/sets/fra/'),
 ('echomtg', 'EchoMTG', 'market-aggregation', 'https://www.echomtg.com/mtg/daily-movers/'),
 ('cardmarket', 'Cardmarket', 'marketplace', 'https://www.cardmarket.com/en/Magic/Spoilers/Reality-Fracture'),
 ('scryfall-docs', 'Scryfall', 'api-documentation', 'https://scryfall.com/docs/api/cards'),
 ('deckcortex-cedh', 'DeckCortex', 'tournament-aggregation', 'https://deckcortex.com/articles/reality-fracture-cedh-first-ten-days'),
 ('edhtop16-dack', 'EDHTop16', 'tournament-results', 'https://edhtop16.com/tournament/baked-ziti-4-goldsabertooths-ny-cedh'),
 ('duel-meta', 'Duel Commander Meta', 'tournament-aggregation-beta', 'https://duel-commander-meta.com/fra/index.html'),
]

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0; self.scripts=[]; self.current=None
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
        if tag=='script': self.current=dict(attrs); self.current['text']=''
        if tag in ('h1','h2','h3','h4','p','div','li','tr','td','section','a','br'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag=='script' and self.current is not None: self.scripts.append(self.current); self.current=None
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if tag in ('h1','h2','h3','h4','p','div','li','tr','td','section','a'): self.parts.append('\n')
    def handle_data(self,data):
        if self.current is not None: self.current['text']+=data
        if not self.skip and data.strip(): self.parts.append(data.strip())
    def text(self): return '\n'.join(x.strip() for x in ''.join(self.parts).splitlines() if x.strip())

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'MTG-Analyzer-Research/1.0','Accept':'application/json,text/html'})
    with urllib.request.urlopen(req,timeout=45) as response: return response.read()

def download(source):
    ident,publisher,kind,url=source
    record=dict(id=ident,publisher=publisher,kind=kind,url=url,retrieved='2026-10-22')
    try:
        raw=fetch(url); text=raw.decode('utf-8',errors='replace'); parser=TextParser(); parser.feed(text)
        (CACHE/(ident+'.html')).write_bytes(raw)
        (CACHE/(ident+'.txt')).write_text(parser.text(),encoding='utf-8')
        record.update(status='retrieved',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),archiveSha256=hashlib.sha256((CACHE/(ident+'.html')).read_bytes()).hexdigest(),textCharacters=len(parser.text()))
        if len(parser.text())<200:record.update(status='partial_html',note='HTTP response contains an application shell; substantive content requires another access method.')
    except Exception as exc: record.update(status='unavailable',error=str(exc))
    return record

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        records=list(pool.map(download,SOURCES))
    cards=[]; url='https://api.scryfall.com/cards/search?q=set%3Afra&unique=prints'
    while url:
        data=json.loads(fetch(url)); cards.extend(data['data']);url=data.get('next_page');time.sleep(.12)
    (OUT/'scryfall-fra.json').write_text(json.dumps(cards,ensure_ascii=False),encoding='utf-8')
    records.append(dict(id='scryfall-api',publisher='Scryfall',kind='oracle-legalities-market-reference',url='https://api.scryfall.com/cards/search?q=set%3Afra&unique=prints',retrieved='2026-10-22',status='retrieved',printings=len(cards)))
    (OUT/'fetch-audit.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in records: print(r['id'],r['status'],r.get('textCharacters',r.get('printings')),r.get('error',''))

if __name__=='__main__': main()
