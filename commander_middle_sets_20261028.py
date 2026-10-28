"""Acquisizione EDHREC e abbinamento esplicito di osservazioni Commander."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
from integrate_middle_sets_20261028 import CONFIG, DATE
from research_middle_sets_20261028 import fetch
from import_expansion_catalogs import write_json
from import_cardmarket_catalog import key

def process(item):
 slug,cfg=item;code=cfg[1];folder=Path('research')/(slug+'-20261028');dest=Path('expansions')/slug
 url='https://json.edhrec.com/pages/sets/'+code+'.json'
 audit=json.loads((folder/'fetch-audit.json').read_text(encoding='utf-8'))
 try:
  raw=fetch(url);(folder/'edhrec-set-data.json').write_bytes(raw);data=json.loads(raw)
  audit['acquisitions'].append({'provider':'EDHREC','id':'edhrec-set-data','url':url,'retrieved':DATE,'status':'acquired','file':'edhrec-set-data.json','sha256':hashlib.sha256(raw).hexdigest()})
 except Exception as exc:
  audit['acquisitions'].append({'provider':'EDHREC','url':url,'retrieved':DATE,'status':'unavailable','error':str(exc)});write_json(folder/'fetch-audit.json',audit);return(slug,str(exc))
 rows=[]
 def walk(value):
  if isinstance(value,dict):
   if isinstance(value.get('name'),str) and ('num_decks' in value or 'inclusion' in value):rows.append(value)
   for sub in value.values():walk(sub)
  elif isinstance(value,list):
   for sub in value:walk(sub)
 walk(data)
 doc=json.loads((dest/'cards.json').read_text(encoding='utf-8'));cards=doc['cards'];lookup={}
 for c in cards:
  for name in [c['name'],c.get('oracleName',''),c.get('printedName','')]+[f['name'] for f in c.get('faces',[])]:
   if name:lookup[key(name)]=c
 matched={};unmatched=[]
 for row in rows:
  c=lookup.get(key(row['name']))
  if not c:unmatched.append(row['name']);continue
  observation={k:row[k] for k in ['name','num_decks','potential_decks','inclusion','label','set','url'] if k in row}
  observation.update(source='edhrec-set-data',date=DATE,context='Liste Commander aggregate EDHREC, adozione e popolarità; non risultati di torneo o vittorie.')
  observation['role']='commander' if '/commanders/' in observation.get('url','') else 'inclusion'
  if c.get('oracleName'):observation['identityMapping']='Nome Oracle condiviso con controparte cartacea; non evidenza di un evento Commander digitale OM1.'
  if observation not in matched.setdefault(c['id'],[]):matched[c['id']].append(observation)
 source_doc=json.loads((dest/'sources.json').read_text(encoding='utf-8'))
 source_doc['research']['sources'].append({'id':'edhrec-set-data','label':'EDHREC: inclusioni e comandanti per set','url':url,'retrieved':DATE,'status':'acquired_and_integrated','coverage':{'sourceRows':len(rows),'matchedCards':len(matched)}})
 source_doc['links']['edhrec-set-data']='https://edhrec.com/sets/'+code
 write_json(dest/'sources.json',source_doc)
 prices=json.loads((dest/'prices.json').read_text(encoding='utf-8')).get('references',{}).get('cards',{})
 ratings=json.loads((dest/'ratings.json').read_text(encoding='utf-8'))['cards']
 for c in cards:
  if c['id'] not in matched:continue
  minimum=prices.get(c['id'],{}).get('from');observed_price=prices.get(c['id'],{}).get('observations',[])
  price={'date':DATE if observed_price else None,'currency':'EUR','metric':'From' if observed_price else None,'printingId':None,'from':minimum,'finishFilter':'any','nonfoil':None,'foil':None,'comparison':{'date':None,'samePrinting':None,'nonfoil':None,'changePct':None,'status':'missing_reference'},'variants':observed_price,'outlook':{'kind':'scenario_condizionale','thesis':'Non viene formulata una previsione economica da inclusioni e prezzi minimi. Servono confronto omogeneo e finiture documentate.','confidence':'bassa','targetPrice':None,'probabilityOfRise':None}}
  if observed_price:price.update(source='Cardmarket',url=observed_price[0]['url'])
  c['prospects']={'date':DATE,'kind':'evidence_and_editorial_scenarios','summary':'Disponibili conteggi di inclusione nelle liste Commander EDHREC. Sono osservazioni di adozione, non prove di rendimento.','gameplayReview':{'kind':'analisi_editoriale_oracle','finding':ratings.get(c['id'],{}).get('why','Testo Oracle acquisito; valutazione di gioco specifica non ancora documentata.'),'evidenceOfTournamentSuccess':False},'sources':['scryfall','edhrec-set-data']+(['cardmarket-browser-catalog'] if observed_price else []),'oracle':{'printingId':c['id'],'url':c['url'],'set':c['set'],'number':c['number'],'text':c['text']},'formats':{'commander':{'legality':c['legalities'].get('commander','not_legal'),'evidence':'inclusioni_documentate','prospect':'da_verificare','confidence':'bassa'}},'tournamentObservations':[],'commanderObservations':matched[c['id']],'price':price,'limitations':['Le inclusioni EDHREC non misurano vittorie e non dimostrano risultati cEDH.','Non sono stati verificati risultati di torneo Constructed per questa carta.','Un minimo Cardmarket privo di filtro finitura non certifica nonfoil, foil o una stampa Scryfall.']}
 doc['prospectsDate']=DATE;write_json(dest/'cards.json',doc)
 write_json(folder/'edhrec-matched-observations.json',{'date':DATE,'sourceRows':len(rows),'matchedCards':len(matched),'observations':matched,'unmatchedNames':sorted(set(unmatched)),'missingCatalogIds':[c['id'] for c in cards if c['id'] not in matched]})
 write_json(folder/'fetch-audit.json',audit)
 return slug,len(matched)

if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for result in pool.map(process,CONFIG.items()):print(result,flush=True)
