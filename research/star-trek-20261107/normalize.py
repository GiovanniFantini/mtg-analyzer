"""Normalize saved public captures; never fetch during offline integration."""
import hashlib
import json
import re
import sys
import tempfile
import unicodedata
from html import unescape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from research_star_trek_20261102 import save
from statistics_data import validate_external_statistics
OUT=Path(__file__).resolve().parent
CACHE=Path(tempfile.gettempdir())/'mtg-star-trek-research-20261107'
CAPTURES=OUT/'captures'
DATE='2026-11-07'
def key(s):
 return ''.join(c for c in unicodedata.normalize('NFKD',s).casefold() if c.isalnum())
def load(p):return json.loads(p.read_text(encoding='utf-8'))
cards=load(ROOT/'expansions/star-trek/cards.json')['cards']
names={key(n):c for c in cards for n in (c['name'],c.get('full',c['name']))}
selected_filters={row['kind']:row for row in load(CAPTURES/'selected-filters.json')['rows']}
assert set(selected_filters)=={'draft','sealed','pick-order'}
for kind,selection in selected_filters.items():
 assert selection['eventTypeLabel']==('Sealed' if kind=='sealed' else 'Premier Draft')
 assert selection['periodLabel']=='Latest Event'
 assert selection['rankControlText']==('Unranked Game Mode' if kind=='sealed' else 'Bronze\nPlatinum')

def statistics(kind):
 raw=(CAPTURES/f'untapped-{kind}.json').read_bytes()
 capture=json.loads(raw);rows=capture['rows']
 labels=['Avg Last Offered','In Hand WR','In Hand WR Δ','In Opening Hand WR','Played WR','Included WR','Games'] if kind=='draft' else ['In Hand WR','In Hand WR Δ','In Opening Hand WR','Played WR','Included WR','Games']
 keys=['avgLastOffered','inHandWinRate','inHandWinRateDelta','inOpeningHandWinRate','playedWinRate','includedWinRate','games'] if kind=='draft' else ['inHandWinRate','inHandWinRateDelta','inOpeningHandWinRate','playedWinRate','includedWinRate','games']
 metrics={k:dict(label=l,unit='games' if k=='games' else 'pick' if k=='avgLastOffered' else 'percent',status='locked' if k in ('inHandWinRateDelta','playedWinRate') else 'suspect' if k=='includedWinRate' else 'public') for k,l in zip(keys,labels)}
 metrics['games']['role']='reported_volume_not_win_rate_denominator'
 metrics['inHandWinRate']['confidenceDefinition']=capture['confidenceDefinition']
 result=[]
 for row in rows:
  c=names[key(row['name'])]
  assert len(row['cells'])==len(keys)+1,row
  values={};display={};margins={}
  for k,cell in zip(keys,row['cells'][1:]):
   assert cell['locked']==(metrics[k]['status']=='locked'),(row['name'],k)
   text=cell['text'].strip();display[k]=text
   number=text.split('±')[0].replace(',','').removesuffix('%')
   values[k]=None if cell['locked'] or number in ('','–','-','N/A') else int(number) if k=='games' else float(number)
   if cell.get('margin'):margins[k]=cell['margin']
  result.append(dict(catalogId=c['id'],name=c['name'],sourceName=row['name'],sourceUrl='https://mtga.untapped.gg'+row['url'],metrics=values,display=display,confidenceMarginsDisplay=margins))
 assert len({r['catalogId'] for r in result})==len(result)
 assert all(r['metrics']['includedWinRate'] in (None,0) for r in result)
 seen={r['catalogId'] for r in result}
 snapshot=dict(schemaVersion=1,provider='Untapped.gg · early access 4 novembre',url='https://mtga.untapped.gg/limited/'+kind+'/star-trek/card-data'+('?eventType=SEALED' if kind=='sealed' else ''),retrieved=DATE,
  filters=dict(expansion='TRK',eventType='PremierDraft' if kind=='draft' else 'Sealed',event='Early Access 2026-11-04',dateRange='Latest Event',period='Early Access 2026-11-04',ranks=capture['rank'],archetype='All Archetypes'),
  rateUnit='percent',metrics=metrics,cards=sorted(result,key=lambda r:r['catalogId']),inputSha256=hashlib.sha256(raw).hexdigest(),sourceUpdatedLabel=capture['updatedLabel'],sourceUpdatedApproximate=capture['sourceUpdatedApproximate'],totalMatchesDisplay=capture['totalMatchesDisplay'],countsPrecision='source_display_rounded',
  limitations=['Campione early access del 4 novembre 2026, prima dell’apertura pubblica di Arena. Volume ridotto e selezione dei partecipanti: non rappresenta il metagame stabilizzato.',
   'WR in mano distinta da WR quando giocata, inclusa e nella mano iniziale. Games non è il denominatore documentato della WR in mano. I conteggi mostrati possono essere arrotondati.',
   'Included WR è zero nelle righe disponibili: valore sospetto conservato, escluso dagli indici. Le metriche Premium rimangono null.',
   'Nessuna media con altri provider o eventi, nessuna modifica di voti numerici, pesi bot o replay. I margini di confidenza pubblicati sono conservati nel JSON.',
   'Le carte non elencate rimangono senza osservazione, le righe con trattino rimangono null.'],
  coverage=dict(catalogCards=len(cards),observedCards=len(result),cardsWithInHandWinRate=sum(r['metrics']['inHandWinRate'] is not None for r in result),missingCards=[dict(catalogId=c['id'],name=c['name'],reason='not_listed_by_source') for c in cards if c['id'] not in seen]))
 validate_external_statistics({kind:{'externalSources':{'untapped':snapshot}}},cards)
 save(OUT/f'untapped-{kind}.json',snapshot)
 print(kind,snapshot['coverage']['observedCards'],snapshot['coverage']['cardsWithInHandWinRate'])

def grades():
 raw=(CAPTURES/'limitedlibrary-grades.json').read_bytes()
 payload=json.loads(raw)
 result=[];excluded=[]
 for card in payload['cards']:
  c=names.get(key(card['name']))
  if not c:raise ValueError(card['name'])
  for review in card['reviews']:
   r=dict(catalogId=c['id'],name=c['name'],author=review['creator'],grade=review.get('sourceGrade') or review['grade'],normalizedGrade=review['grade'],gradeType=review['gradeType'],url=review['watchUrl'],source='limitedlibrary-20261107',date=DATE,sourceUpdated=payload['updatedAt'],context='Limited; voto riportato da aggregatore, video non trascritto indipendentemente. Nessun voto Sealed separato.')
   (result if review['gradeType']=='explicit' else excluded).append(r)
 save(OUT/'attributed-grades.json',dict(date=DATE,url='https://limitedlibrary.com/sets/star-trek/',captureSha256=hashlib.sha256(raw).hexdigest(),cards=result,excludedInferred=excluded,method='Solo voti espliciti riportati da Limited Library. Conservati intervalli e doppie valutazioni senza trasformarli in una media o in stelle. Nessun dato importato per un autore presente solo nel menu.'))
 print('grades',len(result),'excluded',len(excluded))

def pick_order():
 from import_untapped_pick_order import normalize
 capture=load(CAPTURES/'untapped-pick-order.json')
 capture['filters']['format']=capture['filters'].get('format') or capture['filters'].get('eventType')
 capture['filters']['ranks']=capture['filters'].get('ranks') or capture['filters'].get('rank')
 capture['filters']['period']=capture['filters'].get('period') or capture['filters'].get('event')
 raw=(CAPTURES/'untapped-pick-order.json').read_bytes()
 snapshot=normalize(capture,cards,hashlib.sha256(raw).hexdigest())
 snapshot['limitations'].insert(0,'Solo early access del 4 novembre 2026, volume ridotto: tier instabili prima dell’apertura pubblica.')
 save(OUT/'untapped-pick-order.json',snapshot)
 print('pick order',snapshot['coverage']['observedCards'])

def community_grades():
 raw=(CAPTURES/'community-grades.json').read_bytes();capture=json.loads(raw)
 rows=[]
 for row in capture['rows']:
  c=names[key(row['name'])];m=re.fullmatch(r'Community grade: ([A-F][+-]?) from (\d+) raters?',row['community'] or '')
  if row['community'] and not m:raise ValueError('Unexpected community grade label: '+row['community'])
  rows.append(dict(catalogId=c['id'],name=c['name'],grade=m[1] if m else None,raters=int(m[2]) if m else None,url=row['url']))
 assert len(rows)==len({r['catalogId'] for r in rows})==336
 save(OUT/'community-grades.json',dict(date=DATE,provider='myLimitedGrades',url='https://mylimitedgrades.com/games/magic-the-gathering/sets/TRK',inputSha256=hashlib.sha256(raw).hexdigest(),cards=rows,coverage=dict(observed=len(rows),withGrade=sum(r['grade'] is not None for r in rows)),limitations=['Aggregati Community con numero di valutatori pubblicato, non recensioni di un esperto o partite osservate.','Nessuna conversione in stelle o peso dei bot. Nessun benchmark 17Lands disponibile nella pagina acquisita.']))

def capture_facts():
 CAPTURES.mkdir(exist_ok=True)
 for kind in ['draft','sealed']:
  text=(CACHE/f'untapped-{kind}.txt').read_text(encoding='utf-8')
  assert 'Early Access event on November 4, 2026' in text
  assert ('bronze' in text.casefold() and 'platinum' in text.casefold()) if kind=='draft' else 'Unranked Game Mode' in text
  assert 'Latest Event' in text and 'All Archetypes' in text
  total=re.search(r'Total matches:\s*([\d,]+)',text)[1]
  label=re.search(r'Last updated:\s*(.*?)Total matches:',text,re.S)[1].strip()
  browser=load(CACHE/f'untapped-{kind}-browser.json')
  assert '95% confidence margin' in browser['html']
  assert label=='1 day ago','Relative update label changed; derive its approximate date again'
  save(CAPTURES/f'untapped-{kind}.json',dict(retrieved=DATE,event='Early Access 2026-11-04',rank='Bronze-Platinum' if kind=='draft' else 'Unranked',updatedLabel=label,sourceUpdatedApproximate=dict(date='2026-11-06',method='Acquisition date minus displayed one day; approximate, not provider timestamp'),confidenceDefinition=dict(label='95% confidence margin',level=95,method='Public title attribute of the margin cell',intervalMethod='not_published'),totalMatchesDisplay=total,rows=load(CACHE/f'untapped-{kind}-rows.json')))
 raw=(CACHE/'limitedlibrary-data.html').read_bytes()
 d=json.JSONDecoder().raw_decode(raw.decode().split('=',1)[1])[0]
 save(CAPTURES/'limitedlibrary-grades.json',dict(updatedAt=d['updatedAt'],sourceSha256=hashlib.sha256(raw).hexdigest(),cards=[dict(name=c['name'],reviews=[{k:r.get(k) for k in ['creator','grade','sourceGrade','gradeType','watchUrl']} for r in c['reviews']]) for c in d['cards']]))
 raw=(CACHE/'untapped-pick-order.html').read_bytes()
 fulltext=(CACHE/'untapped-pick-order.txt').read_text(encoding='utf-8')
 assert 'Early Access event on November 4, 2026' in fulltext
 assert 'bronze' in fulltext.casefold() and 'platinum' in fulltext.casefold()
 assert all(label in fulltext for label in ['Latest Event','All Archetypes','Tiering by In Hand WR'])
 text=fulltext.split('TIERING STATS',1)[1].split('Back to top',1)[0]
 matches=re.findall(r'<a href="(/limited/draft/[^\"]+)"[^>]*>.*?<img alt="([^\"]+)"',raw.decode(),re.S)
 urls={key(unescape(n)):unescape(url) for url,n in matches}
 groups=[]
 for line in text.splitlines():
  if re.fullmatch(r'Tier(?:S|[ABCD][+-]?|F|\?)',line):
   groups.append(dict(tier=line.removeprefix('Tier'),cards=[]))
  elif key(line) in names:
   # Keep the provider's link rather than construct a card endpoint.
   groups[-1]['cards'].append(dict(name=names[key(line)]['name'],url=urls[key(line)]))
 capture=dict(source='Untapped.gg',url='https://mtga.untapped.gg/limited/draft/star-trek/pick-order',retrieved=DATE,
  filters=dict(tiering='In Hand WR',eventType='PremierDraft',event='Early Access 2026-11-04',rank='Bronze-Platinum',archetype='All Archetypes'),groups=groups)
 capture['sourceSha256']=hashlib.sha256(raw).hexdigest()
 save(CAPTURES/'untapped-pick-order.json',capture)

if __name__=='__main__':
 if '--capture' in sys.argv:capture_facts()
 statistics('draft');statistics('sealed');grades();pick_order();community_grades()
