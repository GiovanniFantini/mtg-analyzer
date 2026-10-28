"""Integra osservazioni EDHREC e piani Limited attribuiti nei sei set."""
import json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from import_expansion_catalogs import write_json
from enrich_recent_sets_20261028 import SETS,ROOT,DATE,key
ARCH={
'the-hobbit': [('WU','Umani e recruit',["Bard's Company",'Bard the Bowman'],'Usa recruit per allargare il campo e sfruttare le sinergie fra Umani. La pescata aggiuntiva sostiene la pressione.'),('BR','Amass',["Bolg's Company",'Bolg of the North'],'Sviluppa un’Armata e mantieni pressione con rimozioni e creature nere. Evita di perdere tutta la minaccia su un unico bloccante.'),('BG','Ferocious',["Chief Warg's Company",'Rhovanion Rampager'],'Raggiungi la soglia di forza richiesta da ferocious e usa le rimozioni nere per liberare gli attacchi.'),('WR','Nani e storied',["Dáin's Company",'Dáin Ironfoot'],'Metti in campo Nani e permanenti leggendari, artefatti e Saghe per sostenere storied.'),('UG','Elfi e landfall',["Thranduil's Company",'Thranduil, the Elvenking'],'Sviluppa terre e creature Elfo; valuta attentamente la curva perché il formato premia partenze rapide.')],
'secrets-of-strixhaven':[('WB','Silverquill repartee',['Informed Inkwright','Silverquill Charm'],'Sviluppa creature economiche e conserva magie che le bersagliano per sfruttare repartee nello stesso turno.'),('UR','Prismari opus',['Prismari Charm','Sanar, Unfinished Genius // Wild Idea'],'Combina interazioni e magie costose per abilitare opus; raggiungere cinque mana spesi conta più del solo valore di mana stampato.'),('BG','Witherbloom infusion',['Witherbloom Charm','Witherbloom, the Balancer'],'Collega guadagno di vite e benefici infusion nello stesso turno, mantenendo sufficienti creature e rimozioni.'),('WR','Lorehold flashback',['Practiced Scrollsmith','Lorehold Charm'],'Scambia risorse e usa flashback per ottenere una seconda magia dal cimitero.'),('UG','Quandrix increment',['Quandrix Charm','Quandrix, the Proof'],'Aumenta il mana disponibile e fai crescere le creature con increment; conserva interazioni per raggiungere le magie decisive.')],
'teenage-mutant-ninja-turtles':[('WB','Sneak',['Uneasy Alliance','Squirrelanoids'],'Crea un attacco difficile da bloccare e usa sneak per riutilizzare ingressi e proteggere le creature.'),('UR','Artefatti',['Mouser Foundry','Return to the Sewers'],'Accumula artefatti economici e risorse riutilizzabili. Le comuni giuste sono essenziali perché la somma delle singole carte non basta.'),('BG','Disappear e midrange',['Frog Butler'],'Sfrutta fixing e rimozioni per un piano midrange. Considera lo splash solo con fonti adeguate e benefici concreti.')],
'lorwyn-eclipsed':[('WU','Tritoni e convoke',['Deepway Navigator','Wanderbrine Preacher'],'Sviluppa Tritoni, usa le creature per convoke e conserva modi di stapparle per attaccare o bloccare.'),('BG','Elfi e cimitero',["Morcant's Loyalist",'High Perfect Morcant'],'Raccogli benefici per Elfi e risorse dal cimitero, senza sostituire i payoff con soli corpi dello stesso tipo.'),('WG','Kithkin aggressivi',['Mistmeadow Council','Gallant Fowlknight'],'Allarga il campo con una curva bassa e sfrutta le ricompense Kithkin.'),('UR','Elementali e magie grandi',["Ashling's Command",'Explosive Prodigy'],'Sostieni le sinergie Elementali e le magie di valore di mana elevato. Un terzo colore richiede fixing reale.'),('BR','Goblin e sacrifici',["Grub's Command",'Taster of Wares'],'Usa Goblin sacrificabili e motori di vantaggio. La densità di payoff determina se il piano è realmente aperto.')],
'marvel-super-heroes':[('WU','Tempo e qualità delle carte',['S.H.I.E.L.D. Spy Kit','Justice, Vance Astrovik'],'Dai priorità a carte efficienti e interazioni; la guida considera morbidi i confini degli archetipi annunciati.'),('WB','Equipaggiamenti',['Ronin, Shadow Stalker','Winter Soldier, Icy Assassin'],'Collega creature che premiano gli equipaggiamenti con un numero sufficiente di equipaggiamenti economici.'),('WG','Heroes',['Ka-Zar of the Savage Land'],'Costruisci una curva aggressiva con creature efficienti, verificando quali carte richiedono specificamente Heroes.')],
'avatar-the-last-airbender':[('WU','Volanti',['Appa, Loyal Sky Bison'],'Sviluppa creature evasive e usa il tempo guadagnato dalle interazioni per continuare ad attaccare.'),('WG','Alleati',['Allies at Last'],'Sviluppa una massa di Alleati e conserva i payoff che premiano più ingressi.'),('UR','Lezioni',['Firebending Lesson','Waterbending Lesson'],'Scegli fra pressione e controllo in base alle carte, mantenendo un numero sufficiente di Lezioni e beneficiari.'),('WB','Sacrifici',["Zuko's Exile"],'Genera risorse da permanenti sacrificabili, evitando che i soli sacrificatori riducano la presenza sul campo.'),('BG','Segnalini',['Earthbending Lesson'],'Combina sviluppo del campo e segnalini, con rimozioni per prolungare la partita.')],
}
def main():
 for slug,code,_ in SETS:
  dest=ROOT/'expansions'/slug;folder=ROOT/'research'/f'{slug}-20261028'
  doc=json.loads((dest/'cards.json').read_text(encoding='utf8'));cards=doc['cards'];known={c['name'] for c in cards};name_map={key(c['name']):c for c in cards}
  for c in cards:
   for face in c.get('faces',[]):name_map[key(face['name'])]=c
  archetypes={pair:{'name':theme,'theme':theme,'core':[n for n in names if n in known],'support':[],'plan':plan,'early':plan,'middle':plan,'late':'Valuta risorse e condizioni di vittoria prima di aggiungere carte costose.','risk':'La valutazione della guida è attribuita all’autore, non una percentuale di vittorie né una priorità numerica universale.','date':DATE,'status':'sintesi_editoriale_da_guida_pubblicata','sources':['draft-guide']} for pair,theme,names,plan in ARCH[slug]}
  write_json(dest/'archetypes.json',archetypes)
  source_doc=json.loads((dest/'sources.json').read_text(encoding='utf8'));sources=source_doc['research']['sources']
  if not any(s['id']=='edhrec-set-data' for s in sources):sources.append({'id':'edhrec-set-data','url':f'https://json.edhrec.com/pages/sets/{code}.json','label':'EDHREC, inclusioni e comandanti per set','retrieved':DATE,'status':'acquired'})
  source_doc['links']['edhrec-set-data']=f'https://edhrec.com/sets/{code}';write_json(dest/'sources.json',source_doc)
  raw=json.loads((folder/'edhrec-set-data.json').read_text(encoding='utf8'));rows=[]
  def walk(value):
   if isinstance(value,dict):
    if isinstance(value.get('name'),str) and ('num_decks' in value or 'inclusion' in value):rows.append(value)
    for x in value.values():walk(x)
   elif isinstance(value,list):
    for x in value:walk(x)
  walk(raw);matched={}
  for row in rows:
   card=name_map.get(key(row['name']))
   if card:
    observation={k:row[k] for k in ['name','num_decks','potential_decks','inclusion','label','set','url'] if k in row};observation.update(source='edhrec-set-data',date=DATE,context='Commander, liste aggregate EDHREC. Inclusioni e popolarità non misurano vittorie.')
    matched.setdefault(card['id'],[])
    if observation not in matched[card['id']]:matched[card['id']].append(observation)
  for c in cards:
   if c['id'] not in matched:continue
   c['prospects']={'date':DATE,'kind':'evidence_and_editorial_scenarios','summary':'Sono disponibili osservazioni sulle liste Commander aggregate da EDHREC. I conteggi descrivono adozione, non risultati competitivi.','gameplayReview':{'kind':'analisi_editoriale_oracle','finding':'Il testo Oracle e le legalità sono consultabili nel profilo. Le inclusioni EDHREC non certificano rendimento o sinergie specifiche.','evidenceOfTournamentSuccess':False},'sources':['scryfall-'+code,'edhrec-set-data'],'oracle':{'printingId':c['id'],'url':c['url'],'set':c['set'],'number':c['number'],'text':c['text']},'formats':{'commander':{'legality':c['legalities'].get('commander','not_legal'),'evidence':'inclusioni_documentate','prospect':'da_verificare','confidence':'bassa'}},'tournamentObservations':[],'commanderObservations':matched[c['id']],'price':{'date':None,'currency':'EUR','metric':None,'printingId':c['id'],'from':None,'nonfoil':None,'foil':None,'comparison':{'date':None,'samePrinting':None,'nonfoil':None,'changePct':None,'status':'missing_reference'},'variants':[],'outlook':{'kind':'scenario_condizionale','thesis':'Prezzi Cardmarket per stampa e finitura non acquisiti; non viene formulata una previsione economica.','confidence':'bassa','targetPrice':None,'probabilityOfRise':None}},'limitations':['Le liste EDHREC non misurano vittorie, cEDH o legalità in altri formati.','Nessuna osservazione di torneo verificata per questa carta in questo aggiornamento.','Prezzi Cardmarket non acquisiti: accesso HTTP 403 registrato negli audit.']}
  doc['prospectsDate']=DATE;write_json(dest/'cards.json',doc)
  write_json(folder/'edhrec-matched-observations.json',{'date':DATE,'sourceRows':len(rows),'matchedCards':len(matched),'observations':matched,'missingCatalogIds':[c['id'] for c in cards if c['id'] not in matched]})
  # Retain only the existing acquisition audit and derived coverage. Raw API
  # responses were moved to a private temporary cache, outside the repository;
  # do not reacquire or republish them during offline integration.
  coverage_path=folder/'17lands-coverage.json'
  coverage=json.loads(coverage_path.read_text(encoding='utf8')) if coverage_path.exists() else {'date':DATE,'event':'PremierDraft','observedRows':None,'rowsWithGIHWR':None}
  coverage.update(rawRedistributed=False,limitation='Dati API 17Lands non redistribuiti e nessuna metrica integrata. Le condizioni di riuso richiedono di verificare i dataset pubblici autorizzati prima di una nuova acquisizione.')
  write_json(coverage_path,coverage)
  write_json(folder/'feature-coverage.json',{'date':DATE,'catalogCards':len(cards),'printings':doc['print_count'],'limitedRatings':len(json.loads((dest/'ratings.json').read_text())['cards']),'commanderObservedCards':len(matched),'archetypes':len(archetypes),'catalogComplete':False,'gaps':{'catalogProduct':'Appartenenza delle stampe a ciascun prodotto da certificare; TLE comprende anche carte esclusivamente Scene Box o Beginner Box.','collation':'Ricetta eseguibile non completata: percentuali arrotondate/<1% e abbinamento degli slot.','statistics':'Nessuna GIH WR numerica nell’acquisizione pubblica.','constructed':'Risultati torneo per carta non ancora estratti dalle fonti.','prices':'Cardmarket HTTP 403, nessun prezzo acquisito.','boxEV':'Richiede collazione e prezzi verificati.'}})
  print(slug,'EDHREC',len(matched),'archetypes',len(archetypes),flush=True)
if __name__=='__main__':main()
