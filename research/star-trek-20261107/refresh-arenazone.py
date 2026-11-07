"""Re-extract current factual review grades without running historic integrators."""
import hashlib,json,re,tempfile,unicodedata
from pathlib import Path
from html import unescape
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
CACHE=Path(tempfile.gettempdir())/'mtg-star-trek-research-20261107'
def key(s):return ''.join(c for c in unicodedata.normalize('NFKD',s).casefold() if c.isalnum())
cards=json.loads((ROOT/'expansions/star-trek/cards.json').read_text(encoding='utf-8'))['cards']
by_name={key(c['name']):c for c in cards}
groups={'Planets':[c for c in cards if c['set']=='TRK' and c['land'] and 'Planet' in c['type']],
 'Shock Lands':[c for c in cards if c['set']=='TRK' and c['land'] and 'pay 2 life' in c['text']],
 'Surveil Lands':[c for c in cards if c['set']=='TRK' and c['land'] and 'two or more other lands' in c['text']]}
rows=[];sources=[]
for color in ['white','blue','black','red','green','multicolor','artifacts-and-lands']:
 ident='arenazone-trk-'+color
 raw=(CACHE/(ident+'.html')).read_bytes();text=raw.decode('utf-8')
 heads=re.findall(r'<h[23]\b[^>]*>(.*?)</h[23]>',text,re.S|re.I)
 name=None;count=0
 for h in heads:
  h=unescape(re.sub('<[^>]+>','',h)).strip()
  m=re.fullmatch(r'Rating:\s*([0-5](?:\.\d+)?)/5',h)
  if not m:name=h;continue
  count+=1
  for c in groups.get(name,[by_name.get(key(name or ''))]):
   if c is None:raise ValueError('Unmatched '+str(name))
   rows.append(dict(catalogId=c['id'],name=c['name'],value=float(m[1]),scaleMax=5,source=ident,author='J2SJosh (j2sjosh)',retrieved='2026-11-07',published=re.search(r'"datePublished":"([^"T]+)',text)[1]))
 sources.append(dict(source=ident,entries=count,inputSha256=hashlib.sha256(raw).hexdigest()))
 print(color,count,flush=True)
assert len(rows)==len({r['catalogId'] for r in rows})==306
old={r['catalogId']:r['value'] for r in json.loads((ROOT/'research/star-trek-20261102/limited-reviews.json').read_text(encoding='utf-8'))['cards']}
result=dict(date='2026-11-07',compared=len(rows),changed=[r for r in rows if old[r['catalogId']]!=r['value']],sources=sources,cards=rows)
(OUT/'arenazone-comparison.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Changed',len(result['changed']))
