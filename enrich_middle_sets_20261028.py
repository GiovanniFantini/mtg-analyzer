"""Offline, attributed Limited summaries and acquisition boundaries."""
import copy
import html
import json
from pathlib import Path
from integrate_middle_sets_20261028 import CONFIG, DATE
from import_expansion_catalogs import apply_printed_identity, write_json

GUIDES={
 'aetherdrift':('Bryan Hohns','2025-02-21','Draft','Privilegia lo sviluppo di creature e le rimozioni. Il verde sostiene i piani più robusti; il blu nero usa gli artefatti. I veicoli senza abbastanza piloti peggiorano le mani. Per velocità serve un piano coerente: i payoff dipendenti dal massimo non sono automaticamente buone carte isolate. Ciclare aiuta a selezionare, ma costa mana e non giustifica da solo un forte taglio delle terre.',{
  'BG':('Cimitero e midrange',['Broodheart Engine','Chitin Gravestalker']), 'UG':('Exhaust',['Sab-Sunen, Luxa Embodied','Elvish Refueler']), 'UB':('Artefatti',['Pactdoll Terror','Haunt the Network']), 'UR':('Ciclo e scarto',['Thunderhead Gunner','Marauding Mako']), 'WU':('Affinità',['Voyage Home','Voyager Quickwelder'])}),
 'edge-of-eternities':('Bryan Hohns','2025-08-08','Draft','Le creature restano necessarie per caricare le navicelle: troppe astronavi producono partenze inerti. Il verde blu sfrutta ramp e vantaggio carte; le carte terra aggiungono flessibilità agli splash, ma occorre contare le fonti. I payoff per segnalini rendono praticabile anche un piano bianco verde più aggressivo.',{
  'UG':('Ramp',['Biomechan Engineer','Galactic Wayfarer']), 'WG':('Segnalini +1/+1',['Haliya, Ascendant Cadet','Rayblade Trooper']), 'WU':('Seconda magia',['Station Monitor']), 'RG':('Terraferma',[]),'UB':('Artefatti',[]),'BR':('Void',[]),'UR':('Artefatti',[]),'WB':('Molte creature',[]),'BG':('Cimitero',[]),'WR':('Navicelle',['Sami, Ship’s Engineer'])}),
 'final-fantasy':('Bryan Hohns','2025-06-08','Sealed, previsione iniziale','Job select offre una creatura insieme all’equipaggiamento, quindi contribuisce sia alla curva sia agli artefatti. Le molte leggendarie premiano i payoff dedicati, ma copie identiche possono ostacolarsi. La guida nasce prima dei risultati del formato: le sue aspettative sul ritmo restano previsioni. Le carte Through the Ages mantengono la propria legalità e partecipano al Limited quando aperte nel prodotto.',{
  'WU':('Artefatti',[]),'UB':('Controllo',[]),'BR':('Black Mage aggressivo',[]),'RG':('Terraferma',[]),'WG':('Molte creature',[]),'WB':('Sacrificio',[]),'UR':('Magie non creatura costose',[]),'BG':('Valore dal cimitero',[]),'WR':('Equipaggiamenti',[]),'UG':('Town e ramp',[])}),
 'tarkir-dragonstorm':('Tom Anderson','2025-04-17','Draft','Le terre multicolori aiutano a sostenere i clan e vanno considerate prima dei riempitivi. Monumenti e creature che convertono mana completano la base senza sostituire il conteggio delle fonti. Le rimozioni efficienti impongono di sviluppare minacce iniziali: affidarsi a un solo drago costoso espone a perdere tempo. Il Prerelease con busta di clan è un prodotto distinto dal Sealed ordinario.',{
  'WBG':('Abzan: endure',[]),'URW':('Jeskai: flurry',[]),'BGU':('Sultai: renew',[]),'RWB':('Mardu: mobilize',[]),'GUR':('Temur: harmonize',[])}),
 'marvel-spider-man':('Bryan Hohns','2025-10-03','Pick-Two Draft','Con due pick simultanee, valuta insieme qualità e compatibilità della coppia. Il bianco verde sfrutta gli ingressi riutilizzati da web-slinging. Modificare creature sostiene bianco blu; scartare abilita mayhem. La guida tratta anche OM1, dichiarando quando usa i nomi cartacei per gli esempi digitali.',{
  'WG':('Web-slinging',['Gallant Citizen','Spider Manifestation']), 'UB':('Villain e connive',[]),'WU':('Creature modificate',['SP//dr, Piloted by Peni','Biorganic Carapace']),'BR':('Mayhem',['Pumpkin Bombardment','Romantic Rendezvous']),'RG':('Magie grandi',['Spider-Rex, Daring Dino'])}),
}

def main():
 for slug,cfg in CONFIG.items():
  folder=Path('expansions')/slug; research=Path('research')/(slug+'-20261028')
  load=lambda name:json.loads((folder/(name+'.json')).read_text(encoding='utf-8'))
  # API aggregates are excluded from public output because a related API carries a reuse restriction.
  stats={'catalogDate':DATE,'limitations':['Statistiche 17Lands non integrate: gli aggregati API non sono riutilizzati in attesa di derivazione dai dataset pubblici con licenza verificata.'],'publicDatasetSource':'https://www.17lands.com/public_datasets'}
  write_json(folder/'statistics.json',stats)
  api=research/'17lands-premier-draft.json'
  if api.exists():
   # Keep only acquisition metadata. No restricted aggregate is redistributed in repository research files.
   api.unlink()
  audit=json.loads((research/'fetch-audit.json').read_text(encoding='utf-8'))
  for acquisition in audit['acquisitions']:
   if acquisition.get('provider')=='17Lands':
    acquisition['status']='excluded_reuse_not_certified';acquisition.pop('file',None)
    acquisition['reason']='Related API notice restricts outside reuse; no API aggregates retained or published. Prefer public_datasets with verified license.'
   if acquisition.get('title') and ('article_errors' in acquisition['title'] or 'Page Not Found' in acquisition['title']):
    acquisition['status']='error_page';acquisition['coverage']='Pagina di errore HTTP 200: nessuna recensione acquisita.'
  write_json(research/'fetch-audit.json',audit)
  sources=load('sources')
  for s in sources['research']['sources']:
   if s.get('title') and 'article_errors' in s['title']: s['status']='error_page';s['coverage']='Pagina di errore, nessuna recensione acquisita.'
  sources['research']['limitations']=['Lo studio esteso non è completo: dieci editori o servizi sono stati cercati, ma pagine mancanti o bloccate non contano come analisi acquisite. Restano da completare recensioni per carta, adozione Constructed/Commander e prezzi Cardmarket.']
  sources['research']['scopeAudit']='research/'+research.name+'/scope-and-gaps.json'
  write_json(folder/'sources.json',sources)
  which='marvel-spider-man' if slug=='through-the-omenpaths' else slug
  author,published,context,summary,archetypes=GUIDES[which]
  cards=load('cards')['cards']; by_name={c['name']:c for c in cards}
  archetypes=copy.deepcopy(archetypes)
  if slug=='through-the-omenpaths':
   # Display names follow official digital counterparts while retaining Oracle and cross-platform aliases.
   for dataset in ['cards','printings']:
    data=load(dataset)
    raw_doc=json.loads((research/'om1-cards.json').read_text(encoding='utf-8'))
    raw_by_id={c['id']:c for c in raw_doc['cards']}
    for card in data['cards']:
     if card['id'] in raw_by_id:
      apply_printed_identity(card,raw_by_id[card['id']])
    write_json(folder/(dataset+'.json'),data)
   cards=load('cards')['cards'];by_name={c.get('oracleName',c['name']):c for c in cards}
  normalized={}
  for pair,(theme,names) in archetypes.items():
   valid=[by_name[n]['name'] for n in names if n in by_name]
   normalized[pair]={'name':theme,'theme':theme,'core':valid,'support':[],'plan':theme+'. Verifica curva, fonti e supporti nel pool prima di impegnare i colori.','risk':'La presenza del payoff non dimostra una densità sufficiente di supporti.','early':'Sviluppa creature e fonti coerenti.','middle':'Collega i supporti ai payoff del piano.','late':'Conserva interazione e una chiusura sostenibile.','date':DATE,'status':'sintesi_attribuita','sources':['limited-guide'],'limitations':['Sintesi qualitativa; nessun peso numerico assegnato ai bot.']}
  write_json(folder/'archetypes.json',normalized)
  guides=load('guides');safe_summary=html.escape(summary)
  panel='<section class="trk-panel"><h2>Piano Limited</h2><p>'+safe_summary+'</p><p>Fonte: '+html.escape(author)+', '+published+'. Contesto: '+html.escape(context)+'.</p><p><a href="'+html.escape(cfg[-1],quote=True)+'">Leggi la guida completa</a></p></section>'
  guides['fragments']['draft.panel-0']=panel
  guides['fragments']['gallery.strategy']=panel
  guides['limitedResearch']={'author':author,'published':published,'retrieved':DATE,'context':context,'summary':summary,'source':cfg[-1],'coverage':'Sintesi del piano e archetipi, non recensione sistematica di tutte le carte.'}
  guides['fragments']['method.panel-0']+='<p>La ricerca estesa per carta e la copertura di dieci editori effettivamente letti restano incomplete. Gli audit distinguono pagine acquisite, pagine di errore e accessi bloccati. Gli aggregati API 17Lands non vengono pubblicati; servono dataset pubblici riutilizzabili.</p>'
  write_json(folder/'guides.json',guides)
  # Retain precise official baseline product data without constructing unsupported collation weights.
  product=load('products')['products']['play']
  if cfg[1] in ['dft','tdm','eoe']:
   product['published']['mainPoolCounts']={'common':81,'uncommon':100,'rare':60,'mythic':20}
   product['published']['slots']={'commons':'6-7','uncommons':3,'wildcard':1,'rareOrMythic':1,'traditionalFoil':1,'land':1}
   product['published']['specialGuestsReplacementPercent']=1.8 if cfg[1]=='eoe' else 1.5
  if cfg[1]=='om1':
   official='https://www-cdn.daybreakgames.com/press/mtgo/article/through-the-omenpaths'
   event='https://www.mtgo.com/news/through-the-omenpaths-event-structure'
   product['name']='Through the Omenpaths Play Booster (MTGO)'
   product['published'].update(source=official,platform='Magic Online',slots={'common':7,'uncommon':3,'rareOrMythic':1,'nonfoilWildcard':1,'foilWildcard':1,'land':1},bonusSheetReplacement='1 common in 24 boosters',arenaCompositionCertified=False)
   events=load('limited')
   for e in events['events'].values():e['sources']=[event];e['platform']='Magic Online'
   events['events']['sealed']['name']='Sealed League MTGO (6 Play Booster)'
   events['events']['draft']['name']='Pick-Two Draft MTGO (4 giocatori)'
   write_json(folder/'limited.json',events)
   sources=load('sources');sources['research']['sources'].extend([{'id':'mtgo-collecting','label':'Magic Online: composizione digitale OM1','url':official,'retrieved':DATE,'status':'read'},{'id':'mtgo-events','label':'Magic Online: Pick-Two, Pick-One e Sealed OM1','url':event,'retrieved':DATE,'status':'read'}]);sources['links'].update({'mtgo-collecting':official,'mtgo-events':event});write_json(folder/'sources.json',sources)
  write_json(folder/'products.json',{'schemaVersion':1,'products':{'play':product}})
  print(slug,len(cards),len(normalized))

if __name__=='__main__':main()
