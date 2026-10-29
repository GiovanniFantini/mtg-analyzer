"""Integrate measured tournament presence across all registered expansion catalogs."""
import argparse,json,hashlib
from collections import Counter,defaultdict
from datetime import date,timedelta
from pathlib import Path
from tournament_index import FORMATS,START,END,MID,identity_aliases,name_key,merge_events,prepare_events,calculate_index,validate_index,signal_level
SOURCE='official-tournament-corpus-20261028'
LABELS={'standard':'Standard','pioneer':'Pioneer','modern':'Modern','pauper':'Pauper'}

def base_prospects(c):
 return {'date':END,'kind':'evidence_and_editorial_scenarios','analysisCoverage':'tournament_data_only','summary':'Indicatori di presenza nelle liste ufficiali di torneo, distinti da valutazioni strategiche e previsioni.','gameplayReview':{'kind':'analisi_editoriale_oracle','finding':'Nessuna nuova recensione strategica: questa acquisizione misura presenza nelle liste e risultati documentati dei mazzi.','evidenceOfTournamentSuccess':False},'sources':[SOURCE],'oracle':{'printingId':c['id'],'url':c['url'],'set':c['set'],'number':c['number'],'text':c.get('text',c.get('oracle',''))},'formats':{},'tournamentObservations':[],'commanderObservations':[],'price':{'status':'not_collected','date':END,'currency':'EUR','metric':'non disponibile','printingId':None,'nonfoil':None,'foil':None,'comparison':{'date':None,'samePrinting':None,'nonfoil':None,'changePct':None,'status':'missing_reference'},'variants':[],'outlook':{'kind':'scenario_condizionale','thesis':'Prospettive economiche non valutate in questa acquisizione.','confidence':'bassa','targetPrice':None,'probabilityOfRise':None}},'limitations':['Le presenze nelle liste non dimostrano il contributo causale della carta alle vittorie.','Lo zero significa non osservata nel campione dichiarato, non carta priva di potenziale.']}

def event_meta(e):
 return {k:e.get(k) for k in ['id','name','date','format','kind','trendKind','publishedCoverage','players','pages']}|{'publishedDecks':len(e['decks'])}

def refresh_editorial_indices(existing,cards):
 current_by_name={c['name']:c for c in cards}
 for old in existing:
  current=current_by_name.get(old['name'])
  if current:old['tournamentIndices']={f:row['tournamentIndex'] for f,row in current['prospects']['formats'].items() if f in FORMATS and 'tournamentIndex' in row}
  else:old.pop('tournamentIndices',None)

def is_tournament_generated(card):
 return card.get('generatedKind')=='tournament-measurement' or str(card.get('generatedBy','')).startswith('official-tournament-corpus-')

def shared_aliases(cards):
 groups=defaultdict(set);owners=defaultdict(set)
 for c in cards:
  identity=c.get('oracleId') or name_key(c['name'])
  groups[identity].update(identity_aliases(c))
  for alias in identity_aliases(c):owners[alias].add(identity)
 collisions={name:sorted(ids) for name,ids in owners.items() if len(ids)>1}
 if collisions:raise ValueError('Ambiguous tournament aliases: '+json.dumps(collisions,ensure_ascii=False))
 return groups

def supplement_facts(card,fact,legality_date):
 had_legalities=bool(card.get('legalities'))
 previous_date=card.get('legalitiesRetrieved') or card.get('tournamentFactsRetrieved') or legality_date
 for key in ['legalities','releasedAt','oracleId']:
  if not card.get(key):card[key]=fact[key]
 card['legalitiesRetrieved']=previous_date if had_legalities else END
 if not card.get('legalitySource'):card['legalitySource']=card.get('url')
 card['tournamentFactsRetrieved']=END

def candidate(c):
 indices={f:a['tournamentIndex'] for f,a in c['prospects']['formats'].items() if f in FORMATS and a.get('tournamentIndex',{}).get('score') is not None and a['tournamentIndex']['score']>0}
 if not indices:return None
 best=max(indices.values(),key=lambda i:i['score']);fmt=max(indices,key=lambda f:indices[f]['score']);o=best['observed'];sample=best['sample'];examples=best['examples'];level=signal_level(indices.values())
 return {'name':c['name'],'formats':[LABELS[f] for f in indices],'level':level,'role':best['archetypes'][0]['name'] if best['archetypes'] else 'Presenze da torneo','verdict':f"{o['withCard']} liste su {sample['decks']} nel campione {LABELS[fmt]}, in {o['eventsWithCard']} eventi distinti.",
  'line':f"Nel campione {LABELS[fmt]}: {o['mainDecks']} presenze nel main deck e {o['sideboardDecks']} nel sideboard. Le due categorie possono sovrapporsi.",'limit':'Campione di liste pubblicate, con copertura dichiarata per evento. I piazzamenti dei mazzi non sono una WR della carta o una previsione futura.','evidence':'Indice torneo calcolato dalle liste ufficiali. I Pro Tour precedenti alla finestra recente sono riportati separatamente nello storico.',
  'sources':[[e['event']+' · '+e['date'],e['url']] for e in examples[:2]],'product':c['set'],'image':c['image'],'tournamentIndices':indices,'generatedBy':SOURCE,'generatedKind':'tournament-measurement'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--research',type=Path,required=True);p.add_argument('--apply',action='store_true');p.add_argument('--report',type=Path);p.add_argument('--format',action='append',choices=FORMATS);a=p.parse_args()
 if a.apply and not a.report:p.error('--apply requires a new --report path to preserve acquisition history')
 if a.report and a.report.exists():p.error('--report already exists; choose a new path')
 records=[json.loads(x.read_text(encoding='utf-8')) for x in (a.research/'events').glob('*.json')];events=prepare_events(merge_events(records));registry=json.loads(Path('expansions.json').read_text());docs=[];release={}
 for r in registry:
  root=Path(r['manifest']).parent;doc=json.loads((root/'cards.json').read_text(encoding='utf-8'));docs.append((root,doc))
  for c in doc['cards']:
   key=c.get('oracleId') or name_key(c['name']);released=c.get('releasedAt') or '9999-12-31';release[key]=min(release.get(key,released),released)
 facts_path=a.research/'card-facts.json'
 facts=json.loads(facts_path.read_text(encoding='utf-8'))['cards'] if facts_path.exists() else {}
 for root,doc in docs:
  for c in doc['cards']:
   if not c.get('legalities') or not c.get('releasedAt') or not c.get('oracleId'):
    fact=facts.get(c['set']+':'+str(c['number']))
    if not fact:continue
    if name_key(fact['name']) not in identity_aliases(c) and c['id']!=fact['id'] and c.get('prospects',{}).get('oracle',{}).get('printingId')!=fact['id']:raise ValueError('Card facts identity mismatch: '+c['id'])
    supplement_facts(c,fact,doc.get('legalityDate') or doc.get('date'))
    release[c['oracleId']]=min(release.get(c['oracleId'],fact['releasedAt']),fact['releasedAt'])
 aliases_by_oracle=shared_aliases(c for _,doc in docs for c in doc['cards'])
 for root,doc in docs:
  for c in doc['cards']:
   c.setdefault('legalitiesRetrieved',c.get('tournamentFactsRetrieved') or doc.get('legalityDate') or doc.get('date'))
   c.setdefault('legalitySource',c.get('url'))
 report=[]
 for root,doc in docs:
  cards=doc['cards'];counts={f:Counter() for f in FORMATS};selected=[]
  for c in cards:
   p=c.setdefault('prospects',base_prospects(c));p.setdefault('sources',[])
   if SOURCE not in p['sources']:p['sources'].append(SOURCE)
   p['tournamentDate']=END
   if p.get('analysisCoverage')=='tournament_data_only' and p.get('price',{}).get('metric')=='non disponibile':p['price']['status']='not_collected'
   for f in FORMATS:
    if a.format and f not in a.format and p.get('formats',{}).get(f,{}).get('tournamentIndex'):
     current=p['formats'][f]['tournamentIndex'];counts[f][current['reason'] or current['status']]+=1;continue
    index=calculate_index(c,f,events,release[c.get('oracleId') or name_key(c['name'])],aliases=aliases_by_oracle[c.get('oracleId') or name_key(c['name'])]);validate_index(index)
    assessment=p.setdefault('formats',{}).setdefault(f,{'legality':c.get('legalities',{}).get(f,'unknown'),'evidence':'non_documentata','prospect':'da_verificare','confidence':'bassa'})
    assessment['tournamentIndex']=index;counts[f][index['reason'] or index['status']]+=1
   p['tournamentLevel']=signal_level(row['tournamentIndex'] for f,row in p['formats'].items() if f in FORMATS)
   if any(v['tournamentIndex']['observed']['withCard'] for f,v in p['formats'].items() if f in FORMATS):p['limitations']=[note for note in p.get('limitations',[]) if note!='Non sono stati verificati risultati di torneo Constructed per questa carta.']
   entry=candidate(c)
   if entry:selected.append(entry)
  # Keep a small measured selection per format; every card remains filterable in the catalog.
  all_measured={c['name']:c for c in selected}
  selected_names=set()
  for f in FORMATS:
   ranked=sorted([c for c in selected if f in c['tournamentIndices']],key=lambda c:(-c['tournamentIndices'][f]['score'],c['name']))
   selected_names.update(c['name'] for c in ranked[:20])
  selected=[c for c in selected if c['name'] in selected_names]
  discovery=json.loads((root/'discovery.json').read_text(encoding='utf-8'));existing=[c for c in discovery.get('cards',[]) if not is_tournament_generated(c)];by_name={c['name']:c for c in selected}
  refresh_editorial_indices(existing,cards)
  for old in existing:
   new=all_measured.get(old['name'])
   by_name.pop(old['name'],None)
   old.setdefault('editorialDate',discovery.get('date'))
  discovery.update({'date':END,'cards':existing+list(by_name.values()),'tournamentResearch':{'method':'published-deck-share-v1','start':START,'end':END,'trendPeriods':{'previous':{'start':START,'end':(date.fromisoformat(MID)-timedelta(days=1)).isoformat()},'recent':{'start':MID,'end':END}},'events':[event_meta(e) for e in events],'missingSourcePages':sum(r.get('status')=='unavailable' for r in records)},'defaultSort':'tournament'})
  sources=json.loads((root/'sources.json').read_text(encoding='utf-8'));rs=sources.setdefault('research',{}).setdefault('sources',[])
  if any(c.get('tournamentFactsRetrieved') for c in cards) and not any(r.get('id')=='scryfall-tournament-facts-20261028' for r in rs):rs.append({'id':'scryfall-tournament-facts-20261028','publisher':'Scryfall','kind':'card-release-and-legalities','url':'https://scryfall.com/docs/api/cards','retrieved':END})
  rs[:]=[r for r in rs if r.get('id')!=SOURCE];rs.append({'id':SOURCE,'publisher':'Magic Online / Wizards of the Coast','kind':'official-tournament-decklists','url':'https://www.mtgo.com/decklists/','retrieved':END,'method':'published-deck-share-v1','period':{'start':START,'end':END},'events':[event_meta(e) for e in events]})
  doc['tournamentResearchDate']=END
  report.append({'expansion':root.name,'cards':len(cards),'formats':{f:dict(counts[f]) for f in FORMATS},'selectedDiscoveryCards':len(discovery['cards']),'missingReleaseFacts':[c['id'] for c in cards if not c.get('releasedAt')]})
  if a.apply:
   for name,data in [('cards.json',doc),('discovery.json',discovery),('sources.json',sources)]:
    (root/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  print(root.name,len(cards),len(discovery['cards']),flush=True)
 if a.report:
  a.report.parent.mkdir(parents=True,exist_ok=True)
  a.report.write_text(json.dumps({'date':END,'integratorSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'acquisition':a.research.as_posix(),'applied':a.apply,'missingOracleIds':[c['id'] for _,doc in docs for c in doc['cards'] if not c.get('oracleId')],'events':[event_meta(e) for e in events],'unavailablePages':[r for r in records if r.get('status')=='unavailable'],'expansions':report},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
