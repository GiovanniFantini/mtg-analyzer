"""Import researched 2025 set catalogs and historical 17Lands observations."""
import concurrent.futures
import hashlib
import html
import json
import re
from pathlib import Path
from research_middle_sets_20261028 import fetch, DATE
from import_expansion_catalogs import create_expansion, write_json

CONFIG = {
 'through-the-omenpaths': ('Through the Omenpaths - Digital Only','om1','2025-09-23','2025-11-17','https://magic.wizards.com/en/news/mtg-arena/through-the-omenpaths-release-faq','https://draftsim.com/mtg-spm-draft-guide/'),
 'marvel-spider-man': ("Magic: The Gathering | Marvel’s Spider-Man",'spm','2025-09-26','2025-11-17','https://magic.wizards.com/en/news/feature/collecting-marvels-spider-man','https://draftsim.com/mtg-spm-draft-guide/'),
 'edge-of-eternities': ('Ai Confini dell’Eternità','eoe','2025-08-01','2025-09-22','https://magic.wizards.com/en/news/feature/collecting-edge-of-eternities','https://draftsim.com/mtg-eoe-draft-guide/'),
 'final-fantasy': ('Magic: The Gathering | FINAL FANTASY','fin','2025-06-13','2025-07-28','https://magic.wizards.com/en/news/feature/collecting-final-fantasy','https://draftsim.com/mtg-fin-sealed-guide/'),
 'tarkir-dragonstorm': ('Tarkir: La Dracotempesta','tdm','2025-04-11','2025-06-09','https://magic.wizards.com/en/news/feature/collecting-tarkir-dragonstorm','https://blog.cardkingdom.com/tarkir-dragonstorm-draft-guide/'),
 'aetherdrift': ('Aetherdrift','dft','2025-02-14','2025-04-07','https://magic.wizards.com/en/news/feature/collecting-aetherdrift','https://draftsim.com/mtg-dft-draft-guide/'),
}
BONUS = {'through-the-omenpaths':['omb'],'marvel-spider-man':['mar'],'edge-of-eternities':['eos','spg'],'final-fantasy':['fca'],'tarkir-dragonstorm':['spg'],'aetherdrift':['spg']}
COMMANDER={'marvel-spider-man':'spe','edge-of-eternities':'eoc','final-fantasy':'fic','tarkir-dragonstorm':'tdc','aetherdrift':'drc'}

def source_urls(slug, cfg):
 name,code,release,end,official,guide=cfg
 english={'through-the-omenpaths':'through-the-omenpaths','marvel-spider-man':'marvels-spider-man','edge-of-eternities':'edge-of-eternities','final-fantasy':'final-fantasy','tarkir-dragonstorm':'tarkir-dragonstorm','aetherdrift':'aetherdrift'}[slug]
 return [
  ('wizards','Wizards: prodotti, date e legalità',official),
  ('limited-guide','Guida Limited attribuita',guide),
  ('card-kingdom','Card Kingdom: guida Limited','https://blog.cardkingdom.com/'+english+'-draft-guide/'),
  ('cards-realm','Cards Realm: recensione Standard','https://mtg.cardsrealm.com/en-us/articles/standard-set-review-'+english),
  ('edhrec','EDHREC: inclusioni Commander','https://edhrec.com/sets/'+code),
  ('mtggoldfish','MTGGoldfish: catalogo e contesto','https://www.mtggoldfish.com/spoilers/'+{'through-the-omenpaths':'Through+the+Omenpaths','marvel-spider-man':"Marvels+Spider-Man",'edge-of-eternities':'Edge+of+Eternities','final-fantasy':'Final+Fantasy','tarkir-dragonstorm':'Tarkir+Dragonstorm','aetherdrift':'Aetherdrift'}[slug]),
  ('untapped','Untapped: archetipi e dati Limited','https://mtga.untapped.gg/limited/draft/'+english+'/set-guide'),
  ('cardmarket','Cardmarket: prezzi per stampa','https://www.cardmarket.com/en/Magic/Expansions/'+{'through-the-omenpaths':'Through-the-Omenpaths','marvel-spider-man':'Marvels-Spider-Man','edge-of-eternities':'Edge-of-Eternities','final-fantasy':'Final-Fantasy','tarkir-dragonstorm':'Tarkir-Dragonstorm','aetherdrift':'Aetherdrift'}[slug]),
  ('mtgdecks','MTGDECKS: adozione Constructed','https://mtgdecks.net/sets/'+code.upper()),
  ('aetherhub','AetherHub: catalogo e mazzi','https://aetherhub.com/Set/'+code.upper()),
 ]

def capture(job):
 folder, ident,label,url=job
 try:
  raw=fetch(url)
  text=raw.decode('utf-8','replace')
  title=re.search(r'<title[^>]*>(.*?)</title>',text,re.S|re.I)
  filename=ident+'-source.html';(folder/filename).write_bytes(raw)
  return {'id':ident,'label':label,'url':url,'retrieved':DATE,'status':'acquired','file':filename,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'title':html.unescape(re.sub('<[^>]+>','',title.group(1))).strip() if title else None,'coverage':'Cattura acquisita; contenuto dinamico e misure per carta da verificare prima dell’integrazione.'}
 except Exception as exc:
  return {'id':ident,'label':label,'url':url,'retrieved':DATE,'status':'unavailable','error':str(exc),'coverage':'Nessuna osservazione acquisita da questo tentativo; URL candidato, esistenza della pagina non certificata.'}

def main():
 # OMB is separate from OM1, with its own identities and legalities.
 folder=Path('research/through-the-omenpaths-20261028')
 if not (folder/'omb-cards.json').exists():
  meta=json.loads(fetch('https://api.scryfall.com/sets/omb'));write_json(folder/'omb-set.json',meta)
  raw=fetch(meta['search_uri']);page=json.loads(raw);write_json(folder/'omb-page-1.json',page)
  assert not page.get('has_more');write_json(folder/'omb-cards.json',{'retrieved':DATE,'code':'omb','cards':page['data'],'pages':1})
 for slug,cfg in CONFIG.items():
  name,code,release,end,official,guide=cfg
  research=Path('research')/(slug+'-20261028'); folder=Path('expansions')/slug
  def cards(c): return json.loads((research/(c+'-cards.json')).read_text(encoding='utf-8'))['cards']
  rows=cards(code); scope={code:len(rows)}
  for bonus in BONUS[slug]:
   bonus_rows=cards(bonus)
   if bonus=='spg':bonus_rows=[r for r in bonus_rows if r['released_at']==release]
   if bonus=='mar':bonus_rows=[r for r in bonus_rows if int(re.match(r'\d+',r['collector_number'])[0])<=40]
   rows.extend(bonus_rows);scope[bonus]=len(bonus_rows)
  # At present raw Scryfall lists cover the set and named bonus series, not certified booster pools.
  sources=[{'id':'scryfall','label':'Scryfall: catalogo paginato e Oracle','url':'https://scryfall.com/sets/'+code,'retrieved':DATE,'status':'acquired'}]
  jobs=[(research,*s) for s in source_urls(slug,cfg)]
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: captures=list(pool.map(capture,jobs))
  sources.extend(captures)
  audit=json.loads((research/'fetch-audit.json').read_text(encoding='utf-8'));audit['acquisitions'].extend(captures);write_json(research/'fetch-audit.json',audit)
  if not folder.exists(): create_expansion(slug,name,code,rows,release_date=release,digital=code=='om1',complete=True,sources=sources)
  for dataset in ['cards','printings']:
   data=json.loads((folder/(dataset+'.json')).read_text(encoding='utf-8'))
   raw_by={r['id']:r for r in rows}
   for card in data['cards']:
    raw=raw_by[card['id']]
    for source_key,target in [('printed_name','printedName'),('printed_text','printedText'),('printed_type_line','printedType')]:
     if raw.get(source_key): card[target]=raw[source_key]
   if dataset=='cards':
    data['coverage'].update(scope=scope,mainSetPrintingsComplete=True,boosterPoolCertified=False,commanderIncluded=False,note='Cataloghi Scryfall paginati completi del set e delle serie bonus documentate; il catalogo include varianti e promozionali, non equivale al pool di una busta.')
   write_json(folder/(dataset+'.json'),data)
  # Published composition is retained without inventing missing probabilities.
  play_size=14
  products={'play':{'name':'Limited Booster digitale' if code=='om1' else 'Play Booster','packSize':play_size,'collation':None,'published':{'source':official,'retrieved':DATE,'includedSets':list(scope),'countsCertifiedAsBoosterPool':False},'missing':['Associare ogni slot alle stampe ammesse e completare le probabilità non pubblicate o arrotondate.'],'assumptions':[]}}
  write_json(folder/'products.json',{'schemaVersion':1,'products':products})
  event_source='https://magic.wizards.com/en/formats/pick-two-draft' if code in ['spm','om1'] else 'https://magic.wizards.com/en/formats/booster-draft'
  events={}
  for kind,packs,picks,seats in [('draft',3,2 if code in ['spm','om1'] else 1,4 if code in ['spm','om1'] else 8),('sealed',6,0,1)]:
   events[kind]={'id':code+'-'+kind,'name':('Pick-Two Draft' if picks==2 else 'Booster Draft') if kind=='draft' else 'Sealed (buste ordinarie)','kind':kind,'product':'play','packsPerPlayer':packs,'seats':seats,'picksPerTurn':picks,'directions':[1,-1,1] if kind=='draft' else [],'minDeckSize':40,'maxCopies':None,'extraBasicLands':True,'mulligan':{'kind':'london','handSize':7,'freeMulligans':0},'sources':[event_source if kind=='draft' else 'https://magic.wizards.com/en/formats/sealed-deck']}
  write_json(folder/'limited.json',{'schemaVersion':1,'events':events,'limitations':['Il Sealed ordinario non modella il Prerelease a clan di Tarkir.' ] if code=='tdm' else []})
  audit['acquisitions'].append({'provider':'17Lands','url':'https://www.17lands.com/public_datasets','retrieved':DATE,'status':'requires_public_dataset','reason':'Gli aggregati API non vengono acquisiti o pubblicati: usare soltanto dataset pubblici con licenza verificata.'})
  write_json(research/'fetch-audit.json',audit)
  write_json(research/'scope-and-gaps.json',{'date':DATE,'scope':scope,'commanderSnapshot':COMMANDER.get(slug),'commanderIncludedInLimited':False,'catalogPaginationComplete':True,'boosterPoolCertified':False,'remaining':{'collation':'Slot, trattamenti e probabilità da associare e verificare; nessuna simulazione inventata.','ratings':'Recensioni Limited numeriche da acquisire e mappare sistematicamente.','prices':'Cardmarket per stampa e finitura, nessun prezzo di altri provider importato.','constructed':'Evidenze di torneo e analisi per carta da completare.','commander':'Catalogo separato acquisito dove previsto; inclusioni e cEDH da verificare.'}})
  print(slug,'integrato',len(rows),flush=True)

if __name__=='__main__':main()
