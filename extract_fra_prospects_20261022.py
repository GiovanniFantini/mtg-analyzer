"""Normalize numerical public evidence without treating missing sightings as zero play."""
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from research_fra_prospects_20261022 import OUT, ROOT, CACHE, fetch, TextParser

class Node:
    def __init__(self, tag='', attrs=None): self.tag=tag;self.attrs=dict(attrs or []);self.children=[]
    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c,Node): yield from c.walk()
    def text(self): return ' '.join(c.text() if isinstance(c,Node) else c for c in self.children).strip()

class DOM(HTMLParser):
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self): super().__init__();self.root=Node('root');self.stack=[self.root]
    def handle_starttag(self,tag,attrs):
        n=Node(tag,attrs);self.stack[-1].children.append(n)
        if tag not in self.VOID:self.stack.append(n)
    def handle_startendtag(self,tag,attrs):
        n=Node(tag,attrs);self.stack[-1].children.append(n)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:self.stack=self.stack[:i];break
    def handle_data(self,data):
        if self.stack[-1].tag not in ('script','style') and data.strip():self.stack[-1].children.append(data.strip())

def dom(name):
    text=(CACHE/(name+'.html')).read_text(encoding='utf-8');parser=DOM();parser.feed(text)
    ids={n.attrs['id']:n for n in parser.root.walk() if 'id' in n.attrs}
    for src,dst in re.findall(r'\$RS\("([^"\n]+)","([^"\n]+)"\)',text):
        if src in ids and dst in ids: ids[dst].children=ids[src].children
    return parser.root

def save(name,data): (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    cards=json.loads((ROOT/'expansions/reality-fracture/cards.json').read_text(encoding='utf-8'))['cards']
    names={c['name'] for c in cards}
    root=dom('postboard'); records=[];contexts={}; seen_sections=set()
    for sec in root.walk():
        fmt=sec.attrs.get('id','')
        if sec.tag!='section' or fmt not in ('standard','pioneer','modern','pauper','legacy') or fmt in seen_sections:continue
        seen_sections.add(fmt)
        text=sec.text();m=re.search(r'(\d[\d,]*)\s*decklists since',text)
        contexts[fmt]={'decklists':int(m[1].replace(',','')) if m else None,'since':'2026-09-25','retrieved':'2026-10-22'}
        for parent in sec.walk():
            if parent.tag!='div' or 'rounded-lg border' not in parent.attrs.get('class',''):continue
            headings=[n for n in parent.walk() if n.tag=='h3']
            if len(headings)!=1:continue
            name=headings[0].text()
            if name not in names:continue
            text=parent.text();m=re.search(r'(\d+) decks\s*[· ]+([\d.]+) avg copies\s*[· ]+([^S]+?)(?:See how|Won|Top|2nd|3rd|Played|$)',text)
            if not m:
                m=re.search(r'(\d+) decks\s*·\s*([\d.]+) avg copies\s*·\s*(.*?)(?:See how|Won|Top|2nd|3rd|Played|$)',text,re.I)
            pct=re.search(re.escape(name)+r'\s*([\d.]+)\s*%',text)
            decks=re.search(r'(\d+) decks',text);avg=re.search(r'([\d.]+) avg copies',text)
            links=[{'label':n.text(),'url':'https://www.postboard.gg'+n.attrs['href']} for n in parent.walk() if n.tag=='a' and n.attrs.get('href','').startswith('/decks/')]
            records.append({'name':name,'format':fmt,'decklistsWithCard':int(decks[1]) if decks else None,'eventWeightedSharePct':float(pct[1]) if pct else None,'averageCopies':float(avg[1]) if avg else None,'deckExamples':links,'source':'postboard','coverage':'tiles require at least 3 lists; early sightings and hidden singletons are not represented here'})
        # Explicit early sightings have names in one li, without h3 headings.
        for li in sec.walk():
            if li.tag!='li':continue
            text=li.text()
            if '2 decks' not in text:continue
            for name in sorted(names,key=len,reverse=True):
                if text.startswith(name):
                    if not any(r['name']==name and r['format']==fmt for r in records):
                        links=[{'label':n.text(),'url':'https://www.postboard.gg'+n.attrs['href']} for n in li.walk() if n.tag=='a' and n.attrs.get('href','').startswith('/decks/')]
                        records.append({'name':name,'format':fmt,'decklistsWithCard':2,'eventWeightedSharePct':None,'averageCopies':None,'deckExamples':links,'source':'postboard','coverage':'explicit early sighting'})
                    break
    save('tournament-evidence.json',{'contexts':contexts,'cards':records})
    parser=TextParser();parser.feed((CACHE/'edhrec.html').read_text(encoding='utf-8'))
    edh_data=json.loads(next(s['text'] for s in parser.scripts if s.get('id')=='__NEXT_DATA__'))
    save('edhrec-data.json',edh_data)
    edh=edh_data['props']['pageProps']['data']['container']['json_dict']['cardlists']
    save('commander-evidence.json',[{'group':group['header'],'name':c['name'],'decks':c.get('num_decks'),'eligibleDecks':c.get('potential_decks'),'url':'https://edhrec.com'+c['url'],'source':'edhrec'} for group in edh for c in group['cardviews']])
    root=dom('draftsim');ratings=[]
    nodes=list(root.walk())
    for i,n in enumerate(nodes):
        if n.tag!='h3' or n.text() not in names:continue
        for other in nodes[i+1:i+35]:
            if other.tag=='h3':break
            match=re.fullmatch(r'Rating:\s*([\d.]+)/10',other.text())
            if match:
                ratings.append({'name':n.text(),'rating':float(match[1]),'scale':10,'context':'Limited review; not a Constructed rating','source':'draftsim'});break
    save('limited-review-evidence.json',ratings)
    historical=[]
    for row in dom('mtgdecks').walk():
        if row.tag!='tr':continue
        cells=[n for n in row.children if isinstance(n,Node) and n.tag=='td']
        if len(cells)<7 or cells[2].text() not in names:continue
        match=re.search(r'([\d,]+) decks',cells[-1].text())
        if match:historical.append({'name':cells[2].text(),'lists':int(match[1].replace(',','')),'window':'last 2 years, all editions and formats; not FRA-only adoption','source':'mtgdecks'})
    save('historical-usage-crosscheck.json',historical)
    # Independent ratings keep their original scale, without averaging reviewers.
    zone=[]; nodes=list(dom('arenazone').walk())
    for i,n in enumerate(nodes):
        name=n.text().replace('\u2019',"'")
        if n.tag not in ('h2','h3') or name not in names:continue
        for other in nodes[i+1:i+130]:
            if other.tag=='h2':break
            match=re.fullmatch(r'Rating:\s*([\d.]+)/5',other.text())
            if match:
                zone.append({'name':name,'rating':float(match[1]),'scale':5,'context':'Limited review; not a Constructed rating','source':'arenazone'});break
    save('limited-independent-evidence.json',zone)
    duel_text=(CACHE/'duel-meta.txt').read_text(encoding='utf-8')
    popular=duel_text.split('Popular new Cards',1)[1]
    asof=re.search(r'Data generated at ([\d-]+ [\d:]+)',duel_text)
    save('duel-evidence.json',{'source':'duel-meta','retrieved':'2026-10-22','sourceAsOf':asof[1] if asof else None,'kind':'beta_popular_card_list_not_performance','names':[name for name in sorted(names) if name in popular],'perCardCountsAvailable':False})
    # SPG is a separate set. A reprint does not inherit FRA Standard/Pioneer legality.
    previous=json.loads((OUT/'scryfall-spg-20261018.json').read_text(encoding='utf-8-sig'))
    spg=json.loads((OUT/'scryfall-spg.json').read_text(encoding='utf-8')) if (OUT/'scryfall-spg.json').exists() else [json.loads(fetch('https://api.scryfall.com/cards/'+c['id'])) for c in previous]
    save('scryfall-spg.json',spg)
    # Commander product is an appendix; never add it to Limited card pools.
    frc=json.loads((OUT/'scryfall-frc.json').read_text(encoding='utf-8')) if (OUT/'scryfall-frc.json').exists() else [];url=None if frc else 'https://api.scryfall.com/cards/search?q=set%3Afrc&unique=prints'
    while url:
        data=json.loads(fetch(url));frc.extend(data['data']);url=data.get('next_page')
    save('scryfall-frc.json',frc)
    print('Tournament records:',len(records),'contexts:',contexts)
    print('Limited review ratings:',len(ratings),'SPG:',len(spg),'FRC printings:',len(frc))
    print('Examples:',json.dumps([r for r in records if r['name'] in ['Dark Matter Manipulator','The Theorist, Jace Beleren','Twinned Vision']],ensure_ascii=False))

if __name__=='__main__':main()
