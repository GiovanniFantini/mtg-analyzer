"""Acquire and normalize EDHREC public set aggregates without copying prices."""
import concurrent.futures, json, re, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from import_expansion_catalogs import write_json
from acquire import SETS,fetch
def key(x):return re.sub('[^a-z0-9]','',x.lower())
EDITORIAL={
'Helpful Hunter':'La creatura lascia una carta in mano all’ingresso e offre un corpo per scambi, sacrifici o potenziamenti. Ripeterne l’ingresso genera altre pescate, purché il costo dell’effetto resti sostenibile.',
'Stab':'La riduzione di costituzione elimina creature piccole e può completare un combattimento. Non distrugge automaticamente creature con costituzione superiore a due e non va conteggiata come rimozione universale.',
'Dazzling Angel':'I successivi ingressi di creature generano un punto vita ciascuno e possono sostenere le carte che premiano il guadagno di vite. L’abilità richiede altre creature; da sola l’Angelo non attiva il proprio innesco.',
'Optimistic Scavenger':'Gli incantesimi che entrano e le Stanze completamente aperte fanno crescere una creatura a scelta. Il numero di incantesimi giocabili e il mana per aprire le porte contano più del solo numero di Stanze nel pool.',
'Gremlin Tamer':'Trasforma gli ingressi degli incantesimi e le Stanze completamente aperte in corpi aggiuntivi. I Gremlin allargano il campo, ma non sono una risposta immediata a una minaccia evasiva già presente.',
'Say Its Name':'Macina tre carte e può recuperare una creatura o una terra da tutto il cimitero. Cercare Altanak richiede tre copie nel cimitero e l’attivazione a velocità stregoneria: non è il rendimento ordinario di una singola copia.',
'Carrot Cake':'Offre un Coniglio e scry all’ingresso, poi un secondo Coniglio e un altro scry quando viene sacrificata. È anche un Cibo: consumarla per forage fa scattare il sacrificio senza ottenere automaticamente le tre vite dell’abilità attivata.',
'Pond Prophet':'La pescata all’ingresso rende utile riprendere la creatura in mano o farla rientrare. Il vantaggio richiede di spendere nuovamente mana o una risorsa: non rende ogni effetto di rimbalzo conveniente in qualsiasi posizione.',
'Cache Grab':'Riempie il cimitero e può riprendere un permanente fra le quattro carte appena macinate. Il Cibo richiede uno Scoiattolo in campo o uno Scoiattolo recuperato in questo modo; non viene creato incondizionatamente.',
'Outcaster Greenblade':'Cerca una terra base o un Deserto in mano e cresce con i Deserti controllati. La ricerca migliora i successivi land drop e il fixing, ma non mette una terra direttamente sul campo.',
'Deepmuck Desperado':'Macina tre carte a ciascun avversario dopo un crimine, una sola volta per turno. Per ripetere il beneficio nel turno avversario serve un modo legale di commettere un altro crimine in quel turno.',
'Throw from the Saddle':'La tua creatura infligge danno a quella avversaria dopo un aumento di forza. Un Mount riceve un segnalino permanente invece del potenziamento temporaneo. La rimozione avversaria sul tuo bersaglio può interrompere il piano.',
'Novice Inspector':'Fornisce un corpo e un Indizio, con una pescata da pagare successivamente. Il corpo sostiene gli attacchi in gruppo e i sacrifici, mentre l’Indizio offre un artefatto distinto dalla creatura.',
'Case of the Gateway Express':'Il danno iniziale cresce con le tue creature. Per risolvere il Caso devono avere attaccato almeno tre creature nello stesso turno; il beneficio risolto aumenta la forza, senza aumentare la costituzione.',
'Person of Interest':'Offre due corpi, ma il sospettato non può bloccare. La pedina Detective resta disponibile per difendere: il totale delle statistiche non coincide con la capacità difensiva immediata.',
'Zoetic Glyph':'Trasforma un artefatto in una creatura con forza e costituzione base 5/4 e offre discover 3 quando l’Aura finisce dal campo al cimitero. Il bersaglio deve restare disponibile durante il lancio: una rimozione in risposta può impedire l’ingresso dell’Aura.',
'Deep-Cavern Bat':'Il corpo evasivo con legame vitale si affianca a un esilio temporaneo dalla mano avversaria. La carta torna quando il Pipistrello lascia il campo, quindi non è uno scarto permanente.',
'Sunshot Militia':'Converte due artefatti o creature STAPpati in un danno a ciascun avversario, a velocità stregoneria. Tappare bloccanti può esporre il tuo campo; gli artefatti non creatura possono sostenere l’abilità senza quel costo difensivo.',
'Candy Grapple':'A due mana riduce forza e costituzione di tre, o di cinque con bargain. Le pedine e gli incantesimi sacrificabili aumentano il numero di bersagli eliminabili, ma sono risorse consumate nel costo.',
'Torch the Tower':'Infligge due danni, oppure tre e scry con bargain. Il permanente danneggiato viene esiliato se dovesse morire nello stesso turno, utile contro benefici di morte o recuperi dal cimitero.',
'Up the Beanstalk':'Rimpiazza se stesso all’ingresso e premia il lancio di magie con valore di mana almeno cinque. La soglia riguarda il valore di mana della magia, non il mana effettivamente speso dopo riduzioni.'}
def run(spec):
 slug,code,*_=spec;d=ROOT/'research'/f'{slug}-20261028';audit=[];url=f'https://json.edhrec.com/pages/sets/{code.lower()}.json';raw=fetch(url,d/'edhrec-set-data.json',audit)
 if not raw:write_json(d/'edhrec-fetch-audit.json',{'acquisitions':audit});return
 rows=[]
 def walk(x):
  if isinstance(x,dict):
   if isinstance(x.get('name'),str) and ('num_decks' in x or 'inclusion' in x):rows.append(x)
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(json.loads(raw));out=ROOT/'expansions'/slug;doc=json.loads((out/'cards.json').read_text());cards=doc['cards'];lookup={key(c['name']):c for c in cards}
 for c in cards:
  for f in c.get('faces',[]):lookup[key(f['name'])]=c
 matched={}
 for row in rows:
  c=lookup.get(key(row['name']))
  if not c:continue
  obs={k:row[k] for k in ('name','num_decks','potential_decks','inclusion','label','set','url') if k in row};obs.update(source='edhrec-set-data',date='2026-10-28',context='Liste aggregate Commander EDHREC; inclusioni e popolarità non misurano vittorie, cEDH o torneo.')
  matched.setdefault(c['id'],[])
  if obs not in matched[c['id']]:matched[c['id']].append(obs)
 sources=json.loads((out/'sources.json').read_text());sid='scryfall-'+code.lower();sources['research']['sources'] += [{'id':'edhrec-set-data','url':url,'label':'EDHREC: inclusioni nelle liste Commander','retrieved':'2026-10-28','status':'acquired'},{'id':sid,'url':'https://scryfall.com/sets/'+code.lower(),'label':'Oracle e legalità Scryfall','retrieved':'2026-10-28','status':'acquired'}];sources['links']['edhrec-set-data']='https://edhrec.com/sets/'+code.lower();sources['links'][sid]='https://scryfall.com/sets/'+code.lower();write_json(out/'sources.json',sources)
 for c in cards:
  if c['id'] not in matched and c['name'] not in EDITORIAL:continue
  c['prospects']={'date':'2026-10-28','kind':'evidence_and_editorial_scenarios','summary':EDITORIAL.get(c['name'],'Sono disponibili osservazioni delle liste Commander aggregate da EDHREC. Sono indicatori di adozione, senza risultati di vittoria.'),'gameplayReview':{'kind':'analisi_editoriale_oracle','finding':EDITORIAL.get(c['name'],'Controlla testo Oracle e legalità del profilo. Le inclusioni non dimostrano il rendimento o una sinergia specifica.'),'evidenceOfTournamentSuccess':False},'sources':[sid,'edhrec-set-data'],'oracle':{'printingId':c['id'],'url':c['url'],'set':c['set'],'number':c['number'],'text':c['text']},'formats':{'commander':{'legality':c['legalities'].get('commander','not_legal'),'evidence':'inclusioni_documentate' if c['id'] in matched else 'non_documentata','prospect':'da_verificare','confidence':'bassa'}},'tournamentObservations':[],'commanderObservations':matched.get(c['id'],[]),'price':{'date':None,'currency':'EUR','metric':None,'printingId':c['id'],'from':None,'nonfoil':None,'foil':None,'comparison':{'date':None,'samePrinting':None,'nonfoil':None,'changePct':None,'status':'missing_reference'},'variants':[],'outlook':{'kind':'scenario_condizionale','thesis':'Le osservazioni non permettono una previsione economica per stampa e finitura.','confidence':'bassa','targetPrice':None,'probabilityOfRise':None}},'limitations':['EDHREC non misura vittorie o risultati cEDH.','Nessun risultato di torneo verificato per questa carta in questo aggiornamento.','Eventuali listini Cardmarket sono conservati separatamente in prices.references; nessun prezzo ereditato da EDHREC.']}
 doc['prospectsDate']='2026-10-28';write_json(out/'cards.json',doc);write_json(d/'edhrec-matched-observations.json',{'date':'2026-10-28','sourceRows':len(rows),'matchedCards':len(matched),'observations':matched,'missingCatalogIds':[c['id'] for c in cards if c['id'] not in matched]});write_json(d/'edhrec-fetch-audit.json',{'acquisitions':audit});print(code,'EDHREC',len(matched),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,SETS))
