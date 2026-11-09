"""Compare current public facts with preserved snapshots, without inventing samples."""
import hashlib,json,re,sys,tempfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
CACHE=Path(tempfile.gettempdir())/'mtg-star-trek-research-20261109'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def key(s):return re.sub('[^a-z0-9]','',s.casefold())
audit=[]
for kind in ['draft','sealed']:
 rows=read(CACHE/f'untapped-{kind}-rows.json');by={key(r['name']):r for r in rows}
 old=read(ROOT/f'research/star-trek-20261107/untapped-{kind}.json')
 changes=[];matched=0
 for r in old['cards']:
  fresh=by.get(key(r['sourceName']))
  assert fresh,r['sourceName']
  matched+=1
  for label in ['inHandWinRate','inOpeningHandWinRate','games']:
   labels=list(old['metrics']);cell=fresh['cells'][labels.index(label)+1]
   if cell['text'].strip()!=r['display'][label].strip():changes.append(dict(name=r['name'],metric=label,previous=r['display'][label],current=cell['text']))
 metadata=read(CACHE/f'untapped-{kind}-browser.json')['metadata']
 text=metadata['text'];assert 'Early Access event on November 4, 2026' in text
 audit.append(dict(kind=kind,retrieved='2026-11-09',matched=matched,rows=len(rows),changes=changes,totalMatches=re.search(r'Total matches:\s*([\d,]+)',text)[1],updatedLabel=re.search(r'Last updated:\s*(.*?)\n',text)[1],selectedEvent=metadata['selectedEvent'],selectedPeriod=metadata['selectedPeriod'],selectedRank=metadata['selectedRankText'],captureSha256=hashlib.sha256((CACHE/f'untapped-{kind}-rows.json').read_bytes()).hexdigest(),decision='Conservare acquisizione precedente e escludere da ranking ordinari: nessun nuovo evento post-lancio.'))
save(OUT/'early-access-comparison.json',dict(date='2026-11-09',populations=audit))
url='https://api.scryfall.com/cards/search?q=%28set%3Atrk+cn%3C%3D311%29+or+set%3Asds&unique=cards&order=set'
rows=[];pages=[]
while url:
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MTG-Analyzer-Research/1.0','Accept':'application/json'}),timeout=40) as response:raw=response.read()
 d=json.loads(raw);rows.extend(d['data']);pages.append(dict(url=url,sha256=hashlib.sha256(raw).hexdigest(),cards=len(d['data'])))
 url=d.get('next_page')
catalog=read(ROOT/'expansions/star-trek/cards.json')['cards'];by={c['oracle_id']:c for c in rows}
assert {c['id'] for c in catalog}==set(by)
differences=[]
for c in catalog:
 s=by[c['id']]
 for local,remote in [('text','oracle_text'),('power','power'),('toughness','toughness'),('cost','mana_cost'),('legalities','legalities')]:
  if c.get(local,'')!=s.get(remote,''):differences.append(dict(catalogId=c['id'],name=c['name'],field=local,local=c.get(local),source=s.get(remote)))
save(OUT/'oracle-check.json',dict(date='2026-11-09',identities=len(catalog),pages=pages,differences=differences,allIdentitiesMatched=True))
save(OUT/'legalities.json',dict(date='2026-11-09',method='Current Scryfall catalog observation, distinct from platform availability and tournament outcomes.',cards=[dict(catalogId=c['id'],name=c['name'],legalities=by[c['id']]['legalities'],url=by[c['id']]['scryfall_uri']) for c in catalog]))
(CACHE/'scryfall-identities.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
print('Early access differences',[(a['kind'],len(a['changes'])) for a in audit],'Oracle differences',[(d['name'],d['field']) for d in differences])
