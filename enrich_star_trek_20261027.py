"""Integrate the saved 27 October public Star Trek captures, fully offline."""
import copy,hashlib,html,json,re,tempfile
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'research/star-trek-20261027'
BASE=ROOT/'expansions/star-trek'
DATE='2026-10-27'
RELEASE='2026-11-13'
CACHE=Path(tempfile.gettempdir())/'mtg-star-trek-research-20261027'
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def key(s):return re.sub(r'\s+',' ',s.replace('’',"'")).strip()
def euro(text):
 text=text.replace('\xa0',' ').replace('From','').replace('€','').strip()
 return None if text in ('N/A','-','') else float(text.replace('.','').replace(',','.'))
def standard_capture(cards,raw):
 target=OUT/'standard-constructed-preview.json'
 if not (CACHE/'standard-preview-ratings.html').exists():return load(target)
 source=(CACHE/'standard-preview-ratings.html').read_bytes();text=source.decode('utf-8')
 by_name={key(c['name']):c for c in cards};by_number={(p['set'],p['collector_number']):by_name[key(p['name'])] for p in raw}
 rows=[];unmatched=[];seen=set()
 for block in text.split('class="card-row')[1:]:
  n=re.search(r'<a[^>]*data-name="([^"]+)"',block)
  if not n:continue
  name=html.unescape(n[1]);card=by_name.get(key(name));reason='name'
  if card is None:
   number=re.search(r'https://manapool.com/card/(trk|sds)/(\d+)/',block)
   if number:card=by_number.get((number[1],number[2]));reason='set_and_collector_number_in_source_link'
  if card is None:unmatched.append(name);continue
  if card['id'] in seen:raise ValueError('Valutazione duplicata: '+name)
  seen.add(card['id'])
  score=float(re.search(r'data-composite="([\d.]+)"',block)[1])
  displayed=re.search(r'<div class="text-lg font-bold"[^>]*>([\d.]+)',block)
  url=re.search(r'<a href="(/cards/[^"]+)"',block)[1]
  role=re.search(r'data-role="([^"]+)"',block)
  rows.append({'catalogId':card['id'],'name':card['name'],'sourceName':name,'matchedBy':reason,'value':score,'display':displayed[1] if displayed else str(score),'scaleMax':5,'role':role[1] if role else None,'url':'https://www.mtg-standard.com'+url})
 result={'provider':'MTG-Standard','url':'https://www.mtg-standard.com/powerating/TRK','retrieved':DATE,'context':'Constructed: previsione automatica prima dell’uscita','kind':'automated_constructed_preview','inputSha256':hashlib.sha256(source).hexdigest(),'scaleMax':5,'sourceRows':len(rows)+len(unmatched),'matchedCards':len(rows),'unmatchedNames':unmatched,'limitations':['Il valore non è un voto di un esperto Limited né una WR.','Value conserva i decimali HTML del modello; display conserva la precisione visibile.','Due nomi provvisori sono associati solo tramite set e numero espliciti nel collegamento della fonte.'],'cards':rows}
 save(target,result);return result
def prices_capture(cards):
 main=load(OUT/'cardmarket-main-dom.json');extras=load(OUT/'cardmarket-extras-dom.json');direct=load(OUT/'cardmarket-type2-direct.json')
 by_name={key(c['name']):c for c in cards};primary={};variants={};unmatched=[]
 for capture,extra in [(main,False),(extras,True)]:
  for row in capture['rows']:
   name=re.sub(r' \(V\.\d+\)$','',row['name']);card=by_name.get(key(name))
   if not card:unmatched.append(row);continue
   reading={**row,'url':'https://www.cardmarket.com'+row['url'],'from':euro(row['price']),'date':DATE,'currency':'EUR','metric':'From','finishFilter':'any','filters':capture['filters'],'source':'cardmarket-extras-browser' if extra else 'cardmarket-main-browser','printingMatch':'product_name_and_expansion','collectorNumber':None}
   if extra or re.search(r' \(V\.\d+\)$',row['name']):variants.setdefault(card['id'],[]).append(reading)
   else:
    if card['id'] in primary:raise ValueError('Prodotto primario duplicato: '+name)
    primary[card['id']]=reading
 if direct['name'] in by_name:
  card=by_name[direct['name']]
  definitions={r['label']:r['value'] for r in direct['definitions']}
  assert definitions['Number']==card['number']
  variants.setdefault(card['id'],[]).append({**primary[card['id']],'acquisition':'earlier_spoiler_list'})
  primary[card['id']]={**primary[card['id']],'from':euro(definitions['From']),'display':direct['name']+' From '+definitions['From'],'price':definitions['From'],'source':'cardmarket-product-browser','collectorNumber':definitions['Number'],'printingMatch':'product_name_expansion_and_collector_number','acquisition':'after_spoiler_list'}
 result={'retrieved':DATE,'currency':'EUR','metric':'From','finishFilter':'any','mainProducts':len(main['rows']),'extraProducts':len(extras['rows']),'unmatched':unmatched,'cardsWithPrimaryFrom':sum(r['from'] is not None for r in primary.values()),'primary':primary,'variants':variants,'limitations':['Prezzi richiesti in prevendita, non ricavi realizzati.','Il minimo senza filtro di finitura non è un prezzo non foil o foil.','Le versioni V.n non sono equiparate a uno specifico numero di stampa senza verifica.','La lettura diretta successiva di Type-2 Phaser prevale sul listino, conservato come osservazione precedente.']}
 save(OUT/'cardmarket-normalized.json',result);return result
def profile(card,notes):
 if card['name'] in notes:return notes[card['name']]['role'],notes[card['name']]['finding']
 text=card['text'];type_=card['type'];mana=card['mana'] or 'nessun costo di mana';parts=[]
 if 'Basic Land' in type_:return 'Fonte di mana','Terra base: produce il mana indicato senza un costo di vita. Le copie dello stesso nome contano come un solo nome per strange new worlds; non ricevono un voto di potenza.'
 if 'Land' in type_:
  if 'pay 2 life' in text:parts.append('Offre due colori e i tipi di terra base stampati; per entrare STAPpata devi pagare due vite. Utile al fixing, con un costo concreto contro mazzi aggressivi.')
  elif 'two or more other lands' in text:parts.append('L’ingresso STAPpato richiede almeno altre due terre già sotto il tuo controllo. Il modo bonus è legato a quell’ingresso: non presumere di averlo al primo turno.')
  else:parts.append('Valuta i colori effettivamente prodotti e le condizioni d’ingresso del testo. Il nome diverso può sostenere strange new worlds, ma non rende conveniente aggiungere un colore che il mazzo non sa utilizzare.')
  return 'Mana e nomi delle terre',' '.join(parts)
 if 'Spacecraft' in type_:
  thresholds=re.findall(r'(\d+)\+\s*\|',text)
  parts.append('Spacecraft da '+mana+': le fasce '+', '.join(thresholds)+' richiedono segnalini carica prima di ottenere le abilità corrispondenti. Station tappa un’altra creatura e ha tempi da stregoneria: considera la perdita di attacchi o blocchi mentre prepari la nave.')
  return 'Nave da preparare',' '.join(parts)
 if 'Creature' in type_:parts.append('Creatura '+str(card.get('power','?'))+'/'+str(card.get('toughness','?'))+' da '+mana+'. La curva e il ruolo sul campo vanno valutati insieme all’abilità, senza dedurre la forza dalla rarità.')
 elif 'Sorcery' in type_:parts.append('Stregoneria da '+mana+': richiede una tua fase principale e pila vuota. Confronta l’impatto del turno con il costo di tenere mana per le altre giocate.')
 elif 'Instant' in type_:parts.append('Istantaneo da '+mana+': puoi scegliere la finestra di risposta, ma restano tutti i limiti e i bersagli indicati dal testo.')
 elif 'Saga' in type_:parts.append('Saga da '+mana+': il vantaggio è distribuito fra capitoli e turni; non sommare gli effetti come se fossero disponibili tutti all’ingresso.')
 elif 'Equipment' in type_:parts.append('Equipaggiamento da '+mana+': il costo di lancio non comprende quello di equipaggiare. Serve una creatura utile e il tempo per spostarlo con i normali tempi da stregoneria.')
 else:parts.append('Permanente da '+mana+': considera separatamente costo iniziale, abilità attivate e risorse necessarie prima di ottenere un vantaggio.')
 if 'Strange new worlds' in text:parts.append('Strange new worlds conta i nomi diversi delle terre, non i tipi base: ripetere Forest non aumenta quel conteggio.')
 if 'Federation' in text:parts.append('Federation conta i tipi delle creature non Borg; nessuno dei tipi su una creatura Borg contribuisce. Diversificare i tipi richiede creature che restino utili anche da sole.')
 if re.search(r'Beam me up\s+\{',text,re.I):parts.append('Beam me up consente un secondo lancio dal cimitero pagando il costo scritto e riprendendo una tua creatura come parte del costo; la magia sarà poi esiliata. Non cambia i tempi del suo tipo di carta.')
 if '•' in text:parts.append('La scelta di uno o più modi è un dilemma e può sostenere Seven of Nine o Sisko; più modi della stessa scelta non sono dilemmi distinti. Non tutti i modi hanno necessariamente un bersaglio legale.')
 if 'assimilate' in text.lower():parts.append('L’assimilazione rende la creatura una creatura artefatto Borg e le toglie gli altri tipi; questo modifica sia affinità sia federation.')
 if len(parts)==1:
  if 'draw' in text.lower():parts.append('Interagisce con le pescate: verifica chi pesca, gli eventuali scarti e i costi richiesti prima di considerarlo vantaggio netto.')
  elif 'token' in text.lower():parts.append('Le pedine richiedono le condizioni scritte nell’abilità: controlla quantità, momento di creazione e durata prima di contarle nella pressione o nella difesa.')
  elif 'counter target' in text.lower():parts.append('Il testo restringe cosa puoi neutralizzare: una risposta a un’abilità non è intercambiabile con un counter per qualsiasi magia.')
  elif re.search(r'(destroy|exile) target',text,re.I):parts.append('L’interazione dipende dal bersaglio legale e dalle sue restrizioni. Valuta cosa resta sul campo o in mano dopo la risoluzione, non soltanto il costo stampato.')
  else:parts.append('Profilo preliminare basato sul testo Oracle. L’efficacia va verificata nel mazzo e contro il formato completo: mancano ancora risultati con l’espansione.')
 return ('Corpo e sinergie' if 'Creature' in type_ else 'Interazione' if 'Instant' in type_ or 'Sorcery' in type_ else 'Permanente di supporto'),' '.join(parts)
def main():
 doc=load(BASE/'cards.json');cards=doc['cards'];raw=load(ROOT/'star-trek-scryfall-20261027.json')['data'];notes=load(OUT/'editorial-notes.json')
 by_id={c['id']:c for c in cards};by_name={c['name']:c for c in cards};prints={}
 for p in raw:prints.setdefault(p['oracle_id'],[]).append(p)
 standard=standard_capture(cards,raw);market=prices_capture(cards);scores={r['catalogId']:r for r in standard['cards']}
 edh=load(OUT/'edhrec-set-observations.json')
 audit=load(OUT/'source-audit.json');sources=load(BASE/'sources.json');registry={r['id']:r for r in sources.get('research',{}).get('sources',[])}
 for r in audit['sources']:
  registry[r['id']]={**registry.get(r['id'],{}),**r,'label':registry.get(r['id'],{}).get('label',r['publisher']),'checked':DATE}
 registry['untapped-pick-order'].update(status='no_set_data',finding='La pagina pubblica TRK restituisce Error - Totally Lost; nessun ranking acquisito.')
 registry['cardmarket-spoiler'].update(status='retrieved_browser',finding='221 prodotti principali e 168 Extras acquisiti dal DOM pubblico; accesso HTTP diretto 403.')
 registry['scryfall-api']={'id':'scryfall-api','publisher':'Scryfall','kind':'oracle-and-catalog','url':doc['source_queries'][0],'retrieved':DATE,'checked':DATE,'label':'Scryfall API: catalogo, Oracle e legalità'}
 registry['cardmarket-product-browser']={'id':'cardmarket-product-browser','publisher':'Cardmarket','kind':'product-price','url':'https://www.cardmarket.com/en/Magic/Products/Singles/Star-Trek/Type-2-Phaser','retrieved':DATE,'checked':DATE,'label':'Cardmarket: lettura diretta successiva'}
 registry['cardmarket-main-browser']={'id':'cardmarket-main-browser','publisher':'Cardmarket','kind':'price-list','url':'https://www.cardmarket.com/en/Magic/Spoilers/Star-Trek','retrieved':DATE,'checked':DATE,'label':'Cardmarket: catalogo principale'}
 registry['cardmarket-extras-browser']={'id':'cardmarket-extras-browser','publisher':'Cardmarket','kind':'variant-price-list','url':'https://www.cardmarket.com/en/Magic/Spoilers/Star-Trek-Extras','retrieved':DATE,'checked':DATE,'label':'Cardmarket: Extras'}
 registry['edhrec-set']={'id':'edhrec-set','publisher':'EDHREC','kind':'published-commander-lists','url':'https://edhrec.com/sets/trk','retrieved':DATE,'checked':DATE,'label':'EDHREC: liste Commander e ristampe, conteggi distinti per sezione'}
 rating_doc=load(BASE/'ratings.json');old_observations={r['cardId']:r for r in sources.get('reviewAnalysis',{}).get('observations',[])}
 for c in cards:
  p=next(p for p in prints[c['id']] if p['collector_number']==c['number'] and p['set'].upper()==c['set'])
  role,finding=profile(c,notes)
  rating_doc['cards'][c['id']]={**rating_doc['cards'].get(c['id'],{}),'role':role,'why':finding,'condition':'Anteprima: verifica curva, base di mana, densità degli enabler e testo dei bersagli. Nessun voto numerico Limited assegnato.'}
  refs=['scryfall-api','wizards-collecting','wizards-mechanics'];formats={}
  for f in ('standard','pioneer','modern','legacy','vintage','pauper','commander','duel'):
   actual=c['legalities'].get(f,'unknown');predicted=None
   if c['set']=='TRK' and actual not in ('banned','restricted') and f in ('standard','pioneer','modern','legacy','vintage','commander','duel'):predicted='legal'
   if c['set']=='TRK' and f=='pauper' and c['rarity']=='common' and actual!='banned':predicted='legal'
   note='Stato Scryfall del 27 ottobre 2026.'
   if predicted and actual!='legal':note+=' Ammissibilità prevista all’uscita del 13 novembre: legale; non equivale alla legalità già attiva né a risultati di torneo.'
   if c['set']=='SDS':note+=' Ristampa Stardates: i formati ammessi dipendono dalla carta, non dal set TRK.'
   formats[f]={'legality':actual,'evidence':'non_documentata' if actual in ('legal','not_legal','unknown') else 'non_legale','prospect':'anteprima_da_testare' if c['set']=='TRK' else 'da_verificare','confidence':'bassa','note':note}
   if predicted:formats[f]['releaseEligibility']={'date':RELEASE,'status':predicted,'source':'wizards-collecting','kind':'previsione_di_ammissibilita'}
  formats['cedh']={'legality':c['legalities'].get('commander','unknown'),'evidence':'non_documentata','prospect':'da_verificare','confidence':'bassa','note':'cEDH usa la legalità Commander; non sono stati verificati risultati agonistici del set.'}
  for f in ('draft','sealed','pick_two'):formats[f]={'legality':'product_dependent','evidence':'regole_ufficiali','prospect':'profilo_editoriale_preliminare','confidence':'bassa','note':'Catalogo ancora parziale. La disponibilità della specifica stampa nel prodotto e la collazione restano da verificare; nessuna WR importata.'}
  reading=market['primary'].get(c['id']);variants=market['variants'].get(c['id'],[])
  price={'date':DATE,'currency':'EUR','metric':'Cardmarket From, minimo richiesto del prodotto senza filtro di finitura','metricLabel':'Minimo Cardmarket del prodotto','printingId':p['id'] if reading and reading.get('collectorNumber')==p['collector_number'] else None,'sourceLabel':'Cardmarket','source':'cardmarket','set':p['set'],'number':p['collector_number'],'from':reading['from'] if reading else None,'finishFilter':'any','nonfoil':None,'foil':None,'comparison':{'date':'2026-10-22','samePrinting':None,'nonfoil':None,'from':None,'changePct':None,'status':'missing_reference'},'variants':variants,'outlook':{'kind':'conditional_editorial_scenario','thesis':'Prezzi di prevendita: l’offerta all’uscita e il successivo utilizzo possono modificarli. Nessun obiettivo di prezzo o rendimento atteso è stimato.','confidence':'bassa','targetPrice':None,'probabilityOfRise':None,'horizonsMonths':[1,6],'upsideConditions':['Domanda di gioco documentata dopo l’uscita e disponibilità della specifica stampa.'],'downsideRisks':['Nuova offerta all’uscita, concorrenza delle ristampe e assenza di risultati verificati.']},'methodNote':'Nessun filtro di lingua, condizione o paese; spedizione esclusa. Finiture non foil e foil non verificate separatamente.','printingMatch':reading.get('printingMatch') if reading else None,'coverageNote':'Numero di stampa verificato solo dove indicato nella lettura della fonte. Lo snapshot non copre tutte le finiture o le stampe e non consente di aggiornare il valore atteso del box.'}
  if reading:price.update(url=reading['url'],productName=reading['name'],sourceReading=reading);refs.append(reading['source'])
  if variants:refs.append('cardmarket-extras-browser')
  prospects={'date':DATE,'kind':'evidence_and_editorial_scenarios','summary':finding,'gameplayReview':{'kind':'analisi_editoriale_oracle','finding':finding,'evidenceOfTournamentSuccess':False},'sources':refs,'oracle':{'printingId':p['id'],'url':p['scryfall_uri'].split('?')[0],'set':p['set'],'number':p['collector_number'],'manaCost':p.get('mana_cost',''),'text':p.get('oracle_text','')},'formats':formats,'tournamentObservations':[],'commanderObservations':[],'price':price,'limitations':['Catalogo di anteprima parziale: i nuovi dati non rappresentano il set completo.','Profilo editoriale Oracle, distinto da recensioni attribuite, modelli automatici e risultati osservati.','Nessuna WR o priorità Draft da partite verificata.','Le ristampe possono avere storia competitiva precedente: non viene attribuita al nuovo formato TRK.']}
  observations=[r for r in edh['rows'] if r.get('catalogId')==c['id']]
  if observations:
   prospects['commanderObservations']=observations;refs.append('edhrec-set');formats['commander']['evidence']='liste_pubblicate_non_agonistiche';formats['commander']['note']+=' EDHREC riporta liste pubblicate, anche di anteprima; non risultati di torneo o cEDH.'
  if c['id'] in scores:
   prospects['automatedEvaluations']=[{**scores[c['id']],'source':'standard-preview-ratings','kind':'automated_constructed_preview','retrieved':DATE,'context':'Constructed, prima dell’uscita'}];refs+=['standard-preview-ratings','standard-method']
  if c['id'] in old_observations:
   o=old_observations[c['id']];prospects['researchNotes']=[{'context':o['context'],'finding':o['summary'],'sources':o['sources'],'date':'2026-10-22'}];refs+=o['sources']
  prospects['sources']=sorted(set(refs));c['prospects']=prospects
 doc['prospectsDate']=DATE;doc['eligibility_note']='TRK e SDS ancora parziali. Le stampe non sono un elenco di collazione verificato; il flag booster delle anteprime non viene usato per inventare l’idoneità al prodotto.'
 rating_doc['date']='27/10/2026';rating_doc['method']='Profili editoriali basati su Oracle, senza voti numerici Limited o conversione dei modelli Constructed.'
 sources['research'].update(date=DATE,catalogSnapshot='star-trek-cards-20261027.json',rawSnapshot='star-trek-scryfall-20261027.json',previousCatalogSnapshot='star-trek-cards-20261022.json',newDistinctCards=55,sources=list(registry.values()))
 sources['research']['coverage']={'catalogCards':len(cards),'printings':len(raw),'gameplayProfiles':len(cards),'specificEditorialNotes':len(notes),'constructedModelCards':len(scores),'commanderObservedCards':edh['coverage']['catalogCards'],'commanderAppendixRows':edh['coverage']['commanderAppendixRows'],'limitedExpertGrades':0,'observedWinRates':0,'primaryCardmarketMinima':market['cardsWithPrimaryFrom'],'publishersRead':len({r['publisher'] for r in audit['sources'] if r['status']=='retrieved'}|{'Scryfall','Cardmarket'})}
 sources['research']['limitations']=['Untapped non espone ancora una pagina Pick Order TRK utilizzabile.','MTGMeta dichiara assenza di partite del set: valori su vecchie ristampe non sono trattati come WR TRK.','MTG-Standard espone 210 previsioni Constructed, non giudizi di esperti Limited.','Le anticipazioni su Commander non vengono trasformate in voti Draft o importate nel pool TRK/SDS.','Cardmarket From in prevendita: riferimenti parziali, non valore atteso di un box.']
 sources['collation']['verified']=DATE
 prices=load(BASE/'prices.json');prices['missing']=['Collazione eseguibile e copertura completa di stampe e finiture assenti: valore atteso del box non calcolabile.'];prices['references']={'date':DATE,'source':'Cardmarket','currency':'EUR','metric':'From','finishFilter':'any','catalogCards':len(cards),'cardsWithFrom':market['cardsWithPrimaryFrom'],'extraProductsObserved':market['extraProducts'],'unmatchedProducts':len(market['unmatched']),'nonfoilCoverage':0,'foilCoverage':0,'snapshot':'research/star-trek-20261027/cardmarket-normalized.json','limitations':market['limitations']}
 stats=load(BASE/'statistics.json');stats['catalogDate']=DATE;stats['catalog']=[{'color':color,'curve':[sum(c['cmc']==v and color in c['colors'] and 'Land' not in c['type'] for c in cards) for v in range(6)]+[sum(c['cmc']>=6 and color in c['colors'] and 'Land' not in c['type'] for c in cards)],'names':[]} for color in 'WUBRG'];stats['researchAvailability']={'date':DATE,'observedWinRates':False,'untappedPickOrder':'set_page_unavailable','mtgMeta':'no_recorded_set_games','reason':'Il set esce su Arena il 10 novembre e su carta il 13 novembre. I modelli preliminari non sono risultati di gioco.'}
 save(ROOT/'star-trek-commander-observations-20261027.json',{'date':DATE,'source':'edhrec-set','scope':'Appendice Commander, esclusa da TRK/SDS e dai pool Limited','rows':[r for r in edh['rows'] if r['scope']=='commander_appendix'],'limitations':edh['limitations']})
 save(BASE/'cards.json',doc);save(BASE/'ratings.json',rating_doc);save(BASE/'sources.json',sources);save(BASE/'prices.json',prices);save(BASE/'statistics.json',stats)
 save(OUT/'coverage.json',sources['research']['coverage']);print(json.dumps(sources['research']['coverage'],ensure_ascii=False));print('Standard unmatched:',standard['unmatchedNames']);print('Cardmarket unmatched:',len(market['unmatched']))
if __name__=='__main__':main()
