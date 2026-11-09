"""Normalize factual grades, retaining identity, author, date and original scale."""
import collections,hashlib,importlib.util,json,re,sys,tempfile,unicodedata
from html import unescape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
OUT=Path(__file__).resolve().parent
CACHE=Path(tempfile.gettempdir())/'mtg-star-trek-research-20261109'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def key(s):return ''.join(c for c in unicodedata.normalize('NFKD',s).casefold() if c.isalnum())
cards=read(ROOT/'expansions/star-trek/cards.json')['cards']
names={key(c['name']):c for c in cards}
# The independently captured review explicitly gives reskin and canonical names.
aliases=read(ROOT/'research/star-trek-20261107/draftsim-review-refresh.json')['cards']
for r in aliases:
 if r.get('sourceName') and '(' in r['sourceName']:
  names[key(r['sourceName'].rsplit(' (',1)[0])]=next(c for c in cards if c['id']==r['catalogId'])
# The older article misspells Russell with one l; SDS 1 identifies the reskin.
names[key('Benny Russell, Dreamer')]=next(c for c in cards if c['set']=='SDS' and c['number']=='1')
raw=(CACHE/'limitedlibrary-data.html').read_bytes()
payload=json.JSONDecoder().raw_decode(raw.decode().split('=',1)[1])[0]
rows=[];excluded=[]
for c in payload['cards']:
 for r in c['reviews']:
  card=names[key(c['name'])]
  row=dict(catalogId=card['id'],name=card['name'],author=r['creator'],grade=r.get('sourceGrade') or r['grade'],normalizedGrade=r['grade'],gradeType=r['gradeType'],url=r['watchUrl'],source='limitedlibrary-20261109',date='2026-11-09',sourceUpdated=payload['updatedAt'],context='Limited, voto riportato da aggregatore; video non trascritto indipendentemente. Nessun voto Sealed separato.')
  (rows if r['gradeType']=='explicit' else excluded).append(row)
save(OUT/'attributed-grades.json',dict(date='2026-11-09',sourceUpdated=payload['updatedAt'],captureSha256=hashlib.sha256(raw).hexdigest(),cards=rows,excludedInferred=excluded,coverage=dict(authors=dict(collections.Counter(r['author'] for r in rows)),uniqueCards=len({r['catalogId'] for r in rows}))))
raw=(CACHE/'mtgsold-limited.html').read_bytes();html=raw.decode()
matches=re.findall(r'<span class="st-pop-name">(.*?)</span><span class="st-pop-grade">(.*?)</span>',html,re.S)
grades=collections.defaultdict(set)
for n,g in matches:grades[unescape(re.sub('<[^>]+>','',n))].add(unescape(re.sub('<[^>]+>','',g)))
assert all(len(g)==1 for g in grades.values())
rows=[];unmatched=[]
for name,values in grades.items():
 if name in ('Shock lands','Planet lands'):
  group=[c for c in cards if c['set']=='TRK' and c['land'] and ('pay 2 life' in c['text'] if name=='Shock lands' else 'Planet' in c['type'] and c['rarity']=='common')]
  assert len(group)==10
  rows.extend(dict(catalogId=c['id'],name=c['name'],grade=next(iter(values)),groupAssessment=name) for c in group)
  continue
 card=names.get(key(name))
 if not card:unmatched.append(name);continue
 rows.append(dict(catalogId=card['id'],name=card['name'],grade=next(iter(values))))
assert len(rows)==len({r['catalogId'] for r in rows})
save(OUT/'mtgsold-grades.json',dict(date='2026-11-09',published='2026-11-03',sourceUpdated='2026-11-06',url='https://mtgsold.com/blog/editorials/star-trek-limited-set-review/',author='mtgsold-analyst',captureSha256=hashlib.sha256(raw).hexdigest(),cards=rows,unmatched=unmatched,limitations=['Voto condiviso Draft e Sealed, non due valutazioni distinte.','Firma pseudonima: confronto editoriale supplementare, non prova di qualità statistica né sostituto dei recensori identificati.','Solo trascrizione dei voti. Nessuna riproduzione delle note, nessuna conversione o media. Le identità fuori dal catalogo attivo sono escluse.']))
raw=(CACHE/'draftsim-sealed-guide.html').read_bytes();html=raw.decode()
heads=re.findall(r'<h[234]\b[^>]*>(.*?)</h[234]>',html,re.S|re.I)
rows=[];unmatched=[]
groups={'Shock Lands':[c for c in cards if c['set']=='TRK' and c['land'] and 'pay 2 life' in c['text']],
        'Dilemma Lands':[c for c in cards if c['set']=='TRK' and c['land'] and 'choose one' in c['text'].lower()]}
for h in heads:
 h=unescape(re.sub('<[^>]+>','',h)).strip()
 m=re.fullmatch(r'(.*?) \((Bomb|Great|Good|Mediocre|Bad)\)',h)
 if not m:continue
 found=groups.get(m[1],[names[key(m[1])]] if key(m[1]) in names else [])
 if not found:unmatched.append(m[1])
 for c in found:rows.append(dict(catalogId=c['id'],name=c['name'],sourceName=m[1],grade=m[2],groupAssessment=m[1] if m[1] in groups else None))
assert not unmatched,unmatched
assert len(rows)==len({r['catalogId'] for r in rows})==135
save(OUT/'sealed-review.json',dict(date='2026-11-09',published='2026-11-05',author='Bryan Hohns (Veveil)',source='draftsim-sealed-20261109',url='https://draftsim.com/mtg-star-trek-sealed-guide/',captureSha256=hashlib.sha256(raw).hexdigest(),context='Recensione Sealed qualitativa, prima del weekend cartaceo; nessuna WR.',cards=rows,missing=[],unmatched=unmatched,method='Categorie originali trascritte dalle intestazioni. Due cicli espansi sui membri verificati. Alias SDS documentati nella recensione Limited precedente; nessuna conversione in stelle o voti Draft.'))
spec=importlib.util.spec_from_file_location('extract_reviews',ROOT/'research/star-trek-limited-20261103/extract_reviews.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
draftsim=module.extract(CACHE/'draftsim-review.html',cards)
draftsim.update(date='2026-11-09',source='draftsim-trk-limited-20261109')
old={r['catalogId']:r['value'] for r in read(ROOT/'research/star-trek-20261107/draftsim-review-refresh.json')['cards']}
draftsim['changedScores']=[r for r in draftsim['cards'] if old[r['catalogId']]!=r['value']]
save(OUT/'draftsim-review-refresh.json',draftsim)
script=(ROOT/'research/star-trek-20261107/refresh-arenazone.py').read_text(encoding='utf-8').replace('20261107','20261109').replace('2026-11-07','2026-11-09')
exec(compile(script,str(OUT/'normalize.py'),'exec'),{'__file__':str(OUT/'normalize.py'),'__name__':'normalization'})
print('Library',len(rows),'Draftsim changes',len(draftsim['changedScores']),'supplemental unmatched',unmatched)
