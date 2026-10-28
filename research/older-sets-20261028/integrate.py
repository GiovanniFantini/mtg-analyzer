"""Offline normalization and qualitative, explicitly attributed research."""
import html, importlib.util, json, re, sys, urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
from import_expansion_catalogs import create_expansion, write_json
from acquire import SETS, fetch
NAMES={'FDN':'Fondamenti di Magic: The Gathering','DSK':'Duskmourn: La Casa degli Orrori','BLB':'Bloomburrow','OTJ':'Banditi di Crocevia Tonante (incluso The Big Score)','MKM':'Delitti al Maniero Karlov','LCI':'Le Caverne Perdute di Ixalan','WOE':'Terre Selvagge di Eldraine'}
NOTES={
'FDN':['Foundations comprende anche carte della Starter Collection e della Beginner Box. Il codice FDN non certifica da solo la presenza nelle Play Booster.','Le Play Booster contengono 14 carte; le Special Guests sostituiscono una comune nell’1,5% delle buste. Jumpstart J25 è un prodotto distinto.'],
'DSK':['Le Stanze permettono di pagare separatamente le due porte. Manifestare terrore guarda due carte, ne mette una a faccia in giù e una nel cimitero.','Il delirio richiede quattro tipi di carta nel cimitero. Una creatura incantesimo contribuisce a due tipi; non occorre giocare quattro colori.'],
'BLB':['Le sinergie dipendono dalla funzione e dalla densità, oltre che dal tipo di creatura. Carrot Cake offre corpi, selezione e una risorsa Cibo.','Forage può usare tre carte del cimitero oppure un Cibo. Le pedine di Carrot Cake aiutano anche le strategie Rabbits e i mazzi che guadagnano vite.'],
'OTJ':['Ogni Play Booster include una carta Breaking News. The Big Score e le Special Guests possono occupare lo slot The List, con legalità proprie.','Commettere un crimine richiede di bersagliare un avversario o le sue magie, abilità o carte nelle zone pertinenti. Non basta infliggere danno senza bersaglio.'],
'MKM':['Il prodotto cartaceo e quello Arena differiscono in tre carte di The List. Non trasferire automaticamente lo stesso catalogo di busta fra le due versioni.','Disguise protegge la creatura a faccia in giù con ward 2. Girarla a faccia in su è un’azione speciale; il mana richiesto va considerato nella curva.'],
'LCI':['Le Draft Booster contengono 15 carte, con una carta bifronte comune o non comune dedicata. Una foil sostituisce una comune nel 33% delle buste.','Special Guests e Jurassic World Collection si trovano nei prodotti Set/Collector, e non entrano automaticamente nelle Draft Booster.'],
'WOE':['Ogni Draft Booster ha uno slot Enchanting Tales. Le ristampe di quel foglio sono giocabili nel Limited del prodotto e mantengono la propria legalità Constructed.','Le avventure offrono due impieghi della stessa carta. Bargain richiede di sacrificare un artefatto, un incantesimo o una pedina: le risorse necessarie vanno contate nel mazzo.']}
THEMES={
'FDN':{'WU':'Volanti','UB':'Controllo e vantaggio','BR':'Sacrificio','RG':'Forza elevata','GW':'Segnalini +1/+1','WB':'Guadagno di vite','UR':'Magie','BG':'Cimitero','RW':'Attacco','GU':'Ramp'},
'DSK':{'WU':'Eerie e incantesimi','UB':'Eerie e controllo','BR':'Sacrificio','RG':'Delirio e pressione','GW':'Survival','WB':'Rianimazione','UR':'Stanze','BG':'Delirio','RW':'Attacchi e creature piccole','GU':'Manifestare terrore'},
'BLB':{'WU':'Uccelli e volanti','UB':'Ratti e soglia','BR':'Lucertole e perdita di vite','RG':'Procioni ed expend','GW':'Conigli e pedine','WB':'Pipistrelli e vite','UR':'Lontre e magie','BG':'Scoiattoli e forage','RW':'Topi e valiant','GU':'Rane e ingressi'},
'OTJ':{'WU':'Flash e controllo','UB':'Crimini','BR':'Fuorilegge','RG':'Forza 4 o superiore','GW':'Mount e saddle','WB':'Sacrificio','UR':'Due magie','BG':'Cimitero','RW':'Mercenari','GU':'Plot'},
'MKM':{'WU':'Detective','UB':'Indizi e controllo','BR':'Suspect','RG':'Creature a faccia in giù','GW':'Disguise','WB':'Creature piccole','UR':'Artefatti e Indizi','BG':'Cimitero','RW':'Attacco con tre creature','GU':'Raccogliere prove'},
'LCI':{'WU':'Artefatti e craft','UB':'Descend e controllo','BR':'Descend e sacrificio','RG':'Dinosauri','GW':'Creature e segnalini','WB':'Sacrificio','UR':'Pirates e artefatti','BG':'Descend e cimitero','RW':'Tap e artefatti','GU':'Merfolk ed explore'},
'WOE':{'WU':'Tappare creature','UB':'Faeries e controllo','BR':'Ratti e sacrificio','RG':'Forza 4 o superiore','GW':'Ruoli e Aure','WB':'Permanenti morti','UR':'Istantanei e stregonerie','BG':'Cibo','RW':'Attaccare con creature piccole','GU':'Costo 5 o superiore'}}
def load(p):return json.loads(p.read_text(encoding='utf-8'))
for slug,code,start,end,extras in SETS:
 d=ROOT/'research'/f'{slug}-20261028'; audit=load(d/'fetch-audit.json'); raws=[]
 if code=='FDN' and not (d/'scryfall-catalog-1.json').exists():
  q='set:spg cn>=74 cn<=83'; u='https://api.scryfall.com/cards/search?'+urllib.parse.urlencode({'q':q,'unique':'prints'})
  raw=fetch(u,d/'scryfall-1-page-1.json',audit['acquisitions'])
  if raw: write_json(d/'scryfall-catalog-1.json',{'query':q,'cards':json.loads(raw)['data'],'complete':True,'retrieved':'2026-10-28'})
 for p in sorted(d.glob('scryfall-catalog-*.json')): raws.extend(load(p)['cards'])
 source_list=[{'id':x['file'].split('.')[0],'url':x['url'],'label':x['file'].split('.')[0].replace('-',' '),'retrieved':'2026-10-28','status':'acquired' if x['status']==200 else 'unavailable','file':str(p.relative_to(ROOT)) if (p:=d/x['file']).exists() else None} for x in audit['acquisitions']]
 meta=load(d/'scryfall-set.json'); out=ROOT/'expansions'/slug
 if not out.exists(): create_expansion(slug,NAMES[code],code,raws,complete=False,release_date=meta['released_at'],sources=source_list)
 catalog=load(out/'cards.json')['cards']; byname={}
 for c in sorted(catalog,key=lambda c:c['set']!=code): byname.setdefault(c['name'],c)
 snapshot={'coverage':{'status':'not_integrated','reason':'Riuso API 17Lands riservato al sito; usare dataset pubblici autorizzati.'}}
 rows=[]
 write_json(out/'statistics.json',{'catalogDate':'2026-10-28','draft':{'limitations':[snapshot['coverage']['reason']]}})
 kind='draft' if code in ('WOE','LCI') else 'play'; size=15 if kind=='draft' else 14
 pub={'date':'2026-10-28','source':next(x['url'] for x in audit['acquisitions'] if x['file']=='wizards-collecting.html'),'packSize':size,'notes':NOTES[code],'sourceSnapshot':f'research/{slug}-20261028/wizards-collecting.txt'}
 if code=='LCI':pub.update(slots={'rareOrMythic':1,'doubleFacedCommonOrUncommon':1,'uncommon':3,'common':9,'land':1},foilReplacesCommonProbability=.33,land={'nonbasicCave':.7,'basic':.3})
 if code=='FDN':pub.update(slots={'common':[6,7],'uncommon':3,'rareOrMythic':1,'nonfoilWildcard':1,'foilWildcard':1,'land':1},specialGuestReplacesCommonProbability=.015,land={'characterBasic':.25,'commonDual':.5,'regularBasic':.25,'foil':.2})
 if code=='BLB':pub.update(slots={'common':[6,7],'uncommon':3,'rareOrMythic':1,'nonfoilWildcard':1,'foilWildcard':1,'land':1},specialGuestReplacesCommonProbability=.015,landSeason={'spring':.4,'summer':.3,'autumn':.2,'winter':.1})
 if code=='OTJ':pub.update(guaranteedBonusSheet='OTP',listProbability=.2,specialGuestProbability=1/64,bonusCodes=['OTP','BIG','SPG'])
 if code=='MKM':pub.update(listOrSpecialGuestProbability=.125,specialGuestProbability=.0156,arenaReplacements={'Baleful Mastery':'Possibility Storm','Cavalier of Thorns':'Evolutionary Leap','Death Cloud':"Smuggler’s Copter"})
 write_json(out/'products.json',{'schemaVersion':1,'products':{kind:{'name':'Draft Booster' if kind=='draft' else 'Play Booster','packSize':size,'tokensIncluded':False,'collation':None,'published':pub,'missing':['Ricetta completa con probabilità dei trattamenti, gruppi e dipendenze fra slot. Nessuna equiprobabilità dedotta dal flag booster.']}}})
 events={}
 for key,packs in [('draft',3),('sealed',6)]:events[key]={'id':f'{code.lower()}-{kind}-{key}','name':NAMES[code]+' '+key.title(),'kind':key,'product':kind,'packsPerPlayer':packs,'seats':8 if key=='draft' else 1,'picksPerTurn':1 if key=='draft' else 0,'directions':[1,-1,1] if key=='draft' else [],'minDeckSize':40,'maxCopies':None,'extraBasicLands':True,'mulligan':{'kind':'london','handSize':7,'freeMulligans':0},'sources':['https://magic.wizards.com/en/formats/'+('booster-draft' if key=='draft' else 'sealed-deck')]}
 write_json(out/'limited.json',{'schemaVersion':1,'events':events})
 guides=load(out/'guides.json'); guides['fragments']['rules.panel-0']='<section class="trk-panel"><h2>Prodotti e meccaniche</h2>'+''.join('<p>'+html.escape(x)+'</p>' for x in NOTES[code])+'</section>'
 guides['fragments']['gallery.strategy']='<section><h3>Costruzione del pool</h3><p>Parti da una curva di creature e interazioni coerente. Verifica le fonti colorate per le magie dei primi turni e valuta separatamente le carte costose o con costi alternativi.</p>'+''.join('<p>'+html.escape(x)+'</p>' for x in NOTES[code])+'</section>'
 guidehtml=(d/'draftsim-guide.html').read_text(encoding='utf-8') if (d/'draftsim-guide.html').exists() else ''
 headings=[html.unescape(re.sub('<[^>]+>','',x)).strip() for x in re.findall(r'<h[23][^>]*>.*?</h[23]>',guidehtml,re.S)]
 guides['research']={'date':'2026-10-28','source':'https://draftsim.com/mtg-'+code.lower()+'-draft-guide/','headings':headings,'coverage':'Guida completa acquisita nello snapshot, temi sintetizzati nei dati archetypes. Nessun voto numerico dedotto dalla prosa.'};write_json(out/'guides.json',guides)
 archetypes={}
 for colors,theme in THEMES[code].items():
  candidates=[c for c in catalog if c['set']==code and set(c['colors'])==set(colors) and c['rarity']=='uncommon']
  names=[c['name'] for c in candidates[:3]]
  archetypes[colors]={'name':colors,'theme':theme,'core':names,'support':[],'plan':'Costruisci una curva e una base di mana coerenti con il piano '+theme.lower()+'. Controlla sul testo delle carte quali risorse innescano i benefici e quante ne hai nel pool.','risk':'Il solo colore della carta non garantisce la sinergia. Le carte segnalate sono esempi del catalogo, senza priorità di pick numerica.','status':'tema_editoriale_da_fonti_del_set','date':'2026-10-28','sources':['draftsim-guide','wizards-mechanics'],'limitations':['Le carte esempio sono selezionate per colori e rarità; non rappresentano una graduatoria osservata.']}
 write_json(out/'archetypes.json',archetypes)
 write_json(d/'fetch-audit.json',audit)
 write_json(d/'assessment-summary.json',{'set':code,'date':'2026-10-28','catalogCards':len(catalog),'printings':len(raws),'catalogComplete':False,'scope':sorted(set(c['set'] for c in catalog)),'statistics':snapshot['coverage'],'notes':NOTES[code],'limitations':['Ricetta eseguibile non completata.','Recensioni per carta e risultati Constructed/Commander da integrare sistematicamente.','Prezzi Cardmarket non acquisiti: richieste dirette bloccate con HTTP 403.','Catalogo del codice principale paginato integralmente; certificazione di tutti i prodotti e contenuti bonus ancora parziale.']})
 print(code,len(catalog),len(raws),len(rows),flush=True)
