"""Build the dated competitive discovery and integrate it into both portal editions."""
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
RC = 'https://magic.gg/news/metagame-mentor-modern-developments-at-five-2026-fall-regional-championships'
AGG = 'https://www.postboard.gg/sets/fra'
CEDH = 'https://deckcortex.com/articles/reality-fracture-cedh-first-ten-days'
SHOW = 'https://metagame.info/en-us/mtg/tournaments/mtgo-modern-showcase-challenge-12856566-top-8-2026-10-17'

def entry(name, formats, level, role, verdict, line, limit, evidence, sources, product='FRA'):
    return dict(name=name, formats=formats.split('|'), level=level, role=role, verdict=verdict,
                line=line, limit=limit, evidence=evidence, sources=sources, product=product)

def build():
    cards = [
        entry('Dark Matter Manipulator','Modern|Legacy','Confermata','Cimitero',
              'La prima carta da esplorare per i mazzi che trasformano il cimitero in pressione.',
              'Per {B} macini tre carte: alimenti Nethergoyf, il delirio di Fear of Missing Out e Detective\'s Phoenix.',
              'Soffre le risposte al cimitero. Il successo del mazzo non misura il contributo isolato della carta.',
              'Modern: 4 copie nel Rakdos di Shuhei Nakamura, Top 8 al Regional Giappone/Corea. Legacy: 4 copie nel Dimir Tempo di OSCA66, vincitore del Challenge del 16 ottobre.',
              [('Regional Championship',RC),('Vittoria Legacy','https://www.postboard.gg/decks/122828?card=Dark+Matter+Manipulator&set=fra'),('Showcase del 17 ottobre',SHOW)]),
        entry('Pompous Battlemage','Modern|Pioneer','Confermata','Aggro / prowess',
              'Una delle prove più convincenti del set in due formati.',
              'Primo turno: creatura per {R}. Nel turno successivo Improvised Act costa {R}, innesca destrezza e può cambiare una carta in mano.',
              'Le liste non concordano sul numero ottimale. Una lista Prowess in Top 4 allo Showcase non la giocava.',
              'Showcase Modern del 17 ottobre, 286 partecipanti: 2 copie nel mazzo finalista e 4 in una lista Top 4. Anche Wizards ne conferma l\'impatto Pioneer.',
              [('Liste Showcase',SHOW),('Pioneer, Wizards','https://magic.wizards.com/en/news/announcements/banned-and-restricted-october-12-2026')]),
        entry('Twinned Vision','Modern|Pauper','Confermata','Pescata / storm',
              'La comune da seguire per prima, con applicazioni anche in Modern.',
              'In Ruby Storm, Ruby Medallion riduce il costo. Se la lanci dall\'esilio con Wrenn\'s Resolve peschi due; Past in Flames offre un altro modo di rigiocarla.',
              'Dalla mano pesca una sola carta. Il flashback stampato richiede anche uno scarto.',
              'Due copie nel Ruby Storm di Max Dore, quarto al Regional canadese. Una copia nel Mono Red Madness vincitore del PauperNATION del 4 ottobre.',
              [('Regional Canada',RC),('Lista PauperNATION','https://www.postboard.gg/decks/118691?card=Twinned+Vision&set=fra')]),
        entry('Roiling Canopy','Modern','Confermata','Terre / combo',
              'Un pezzo specialistico per Amulet Titan, con una chiusura concreta.',
              'Yavimaya, Cradle of Growth rende Foreste le terre. Scapeshift può così produrre molte innescate e rendere letale anche Arboreal Grazer.',
              'Entra TAPpata, richiede cinque altre Foreste e una creatura bersaglio. Non è una terra da inserire in qualsiasi mazzo verde.',
              'Due copie nell\'Amulet di Julien Henry, qualificato al Pro Tour al Regional di Ghent.', [('Regional EMEA',RC)]),
        entry("Theorist's Sanctum",'Modern','Confermata','Valore / controllo',
              'Utilità cercabile con fetch, soprattutto in una copia.',
              'Flooded Strand può cercare questa Isola. Nelle partite lunghe l\'abilità empower Jace converte il mana in sorvegliare e pescate nel tempo.',
              'Senza behold di un Jace entra TAPpata. La capacità richiede mana e TAP: la pescata non è gratuita.',
              'Una copia nell\'Azorius Chant di Nate Green, vincitore del Regional di Los Angeles.', [('Regional USA',RC)]),
        entry('Seasoned Cryomancer','Pioneer|Modern','Emergente','Pescata / cimitero',
              'La seconda pista Pioneer da esplorare dopo Battlemage.',
              'Per {1}{U}{U} peschi due e scarti due: prepari il cimitero e sfrutti Proft\'s Eidetic Memory. Scartando non terre puoi anche stordire creature avversarie.',
              'Non crea automaticamente vantaggio carte all\'entrata. Per l\'abilità dal cimitero servono altri cinque mana.',
              'Quattro copie nell\'Izzet Cauldron di Cachorrowo, vincitore del Pioneer Challenge del 5 ottobre. Presenze Modern nel campione aggregato.',
              [('Lista vincitrice Pioneer','https://www.postboard.gg/decks/117404?card=Seasoned+Cryomancer&set=fra'),('Altri formati',AGG)]),
        entry('Carnivorous Cultivator','Legacy|Pioneer','Emergente','Terre / cimitero',
              'Una pista per strategie con terre utilità e recupero dal cimitero.',
              'Enroot mette Wasteland dal grimorio nel cimitero. Quando Cultivator infligge danno da combattimento a un giocatore puoi riprenderla in mano.',
              'La magia preparata costa altro mana e il recupero richiede di colpire un giocatore.',
              'Una copia nel Maverick di Bastiaan Boel, primo a Haarlem Night 41 il 7 ottobre, 25 giocatori. Altre presenze in Depths e mazzi verdi.',
              [('Lista Haarlem','https://www.postboard.gg/decks/119380?card=Carnivorous+Cultivator&set=fra'),('Campione internazionale',AGG)]),
        entry('Archive Arbiter','Legacy','Emergente','Risposte / artefatti',
              'Un bersaglio da sideboard per i mazzi con Karn, the Great Creator.',
              'Karn lo prende dal sideboard: l\'entrata può distruggere un permanente non creatura e non terra, oppure farti guadagnare quattro vite.',
              'Sei mana e un ruolo ristretto. Non è una rimozione universale.',
              'Due copie nel sideboard del Mystic Forge Combo di BHe, vincitore del Legacy Challenge del 30 settembre.',
              [('Lista vincitrice','https://www.postboard.gg/decks/115713?card=Archive+Arbiter&set=fra')]),
        entry('Unflinching Hortimancer','Pauper','Preliminare','Aggro / lifegain',
              'Una pista secondaria per aggro bianchi con guadagno di vite.',
              'Ogni evento di guadagno di vite aggiunge un segnalino +1/+1. Ward {1} rende un poco più costose le risposte avversarie.',
              'Due sole liste con Top 8 nel campione: troppo poco per chiamarla staple.',
              'Postboard registra due liste, di due giocatori, in Mono-white e Orzhov Aggro.', [('Campione Pauper',AGG)]),
        entry('Samut, Tyrant of Naktamun','Commander / cEDH','Confermata','Protezione / combo',
              'La nuova carta con l\'adozione cEDH più ampia nella rilevazione consultata.',
              'Con Samut in campo, Ad Nauseam e Brain Freeze hanno split second. La protezione vale anche per i tuoi counter istantanei.',
              'Samut stessa non ha split second. Le innescate restano attive e permanenti o abilità di combo non sono protetti automaticamente.',
              '682 su 3.351 liste cEDH, 2–11 ottobre: 20,4%, circa 20,0% escludendo possibili duplicati. È adozione, non win rate.', [('Rilevazione cEDH',CEDH)]),
        entry('Pia, Aether Ascetic','Commander / cEDH','Confermata','Tutore / incantesimi',
              'Molto interessante nei mazzi verdi che cercano incantesimi chiave.',
              'Un tutore per creature trova Pia; la sua entrata, scartando una carta, cerca Food Chain o un altro incantesimo utile.',
              'Richiede uno scarto. È un Umano: l\'abilità di Kinnan, Bonder Prodigy non può metterla in campo.',
              '376 su 3.351 liste nel campione cEDH. In Rograkh/Thrasios: 100 liste su 186.', [('Rilevazione cEDH',CEDH)]),
        entry("Samut, Hazoret's Champion",'Commander / cEDH','Confermata','Rapidità / combo',
              'Una scelta mirata per Sisay e motori che richiedono TAP.',
              'Dare rapidità alle creature permette di usare subito abilità con TAP di pezzi come Ioreth of the Healing House.',
              'Il dato è concentrato su Sisay. Non rende automaticamente migliore ogni mazzo rosso.',
              '204 liste cEDH; presente in 109 delle 167 liste Sisay, Weatherlight Captain del campione.', [('Rilevazione cEDH',CEDH)]),
        entry('Dack Fayden, Helping Hand','Commander / cEDH','Emergente','Blink / combo',
              'Il comandante emergente da esplorare separatamente dalle carte del box.',
              'Le creature entrano sotto il tuo controllo prima di essere cedute: le innescate rimangono tue. Le liste sfruttano Preston, the Vanisher, Felidar Guardian e Radiant Solar.',
              'Costa sei mana. Le combinazioni richiedono una lista costruita appositamente; campione ancora piccolo. Carta FRC, fuori dal Play Booster FRA.',
              'Tim Taranto vince BAKED ZITI 4 il 3 ottobre: 119 giocatori, record 6-0-1.',
              [('Classifica EDHTop16','https://edhtop16.com/tournament/baked-ziti-4-goldsabertooths-ny-cedh'),('Analisi delle liste','https://deckcortex.com/articles/dack-fayden-helping-hand-cedh')], 'FRC'),
        entry('Bloodline Recollector','Commander','Preliminare','Sacrificio / pescata',
              'Una valutazione strategica positiva per Aristocrats, ancora senza conferma competitiva qui documentata.',
              'Con Viscera Seer sacrifichi tre pedine: nella sottofase finale Recollector diventa preparato. Pagando {B} puoi poi pescare tre e perdere tre vite.',
              'Deve sopravvivere fino alla preparazione. Non entra preparato e non va confuso con una pescata immediata per un solo mana.',
              'Ipotesi basata sul testo della carta, senza un risultato di alto livello verificato in questa ricerca.', [('Testo e note Wizards','https://magic.wizards.com/en/news/feature/reality-fracture-release-notes')]),
        entry('The Theorist, Jace Beleren','Commander|Modern|Pioneer','Emergente','Valore / controllo',
              'Più attraente nel multiplayer che nei mazzi cEDH più veloci.',
              'In una partita a quattro, se sopravvive alle tre sottofasi di acquisizione avversarie, può farti pescare tre carte aggiuntive.',
              'Richiede quattro mana ed è vulnerabile agli attacchi. In cEDH la presenza rilevata è ancora limitata.',
              '48 su 3.351 liste cEDH nel campione. Presenze nei control Modern e in Pioneer nell\'archivio Postboard.', [('Campione cEDH',CEDH),('Liste constructed',AGG)]),
        entry("Jace's Machinations",'Pioneer','Preliminare','Combo',
              'Una scommessa con una combinazione potente, ancora da dimostrare nei risultati.',
              'Con Kasmina, Enigma Sage, gli otto segnalini sul Jace pedina permettono di usare il −8 concesso da Kasmina per lanciare Enter the Infinite e preparare Thassa\'s Oracle.',
              'Richiede più pezzi. Wizards il 12 ottobre segnalava l\'assenza di risultati Pioneer rilevanti.',
              'Combo discussa nell\'aggiornamento ufficiale delle banlist, non una vittoria documentata.', [('Valutazione Wizards','https://magic.wizards.com/en/news/announcements/banned-and-restricted-october-12-2026')]),
        entry('Stingcaster Mage','Pioneer','Preliminare','Recupero magie',
              'Carta da osservare, con evidenza più debole dei principali candidati Pioneer.',
              'Per {1}{R} ottieni un corpo rapido e dai flashback a una magia nel cimitero. Occorre pagare anche il costo di quella magia.',
              'Non ha flash: il ruolo differisce da Snapcaster Mage. Le presenze non bastano ancora a dimostrare un posto stabile.',
              'Quattro liste e due Top 8 nel campione Pioneer consultato.', [('Campione Pioneer',AGG)]),
    ]
    preview = {}
    for file in ['fra-all.json','fra-spg.json']:
        for c in json.loads((ROOT/file).read_text(encoding='utf-8')):
            faces=c.get('card_faces') or [c]
            image=c.get('image_uris',faces[0].get('image_uris',{})).get('normal')
            if image:
                for n in [c['name'],*[f['name'] for f in faces]]:
                    preview[n]=dict(name=n,image=image,full=c['name'],faces=[])
    extras = ['Dack Fayden, Helping Hand','Nethergoyf','Fear of Missing Out',"Detective's Phoenix",'Ruby Medallion',"Wrenn's Resolve",'Past in Flames','Yavimaya, Cradle of Growth','Scapeshift','Arboreal Grazer','Flooded Strand',"Proft's Eidetic Memory",'Wasteland','Karn, the Great Creator','Ad Nauseam','Brain Freeze','Food Chain','Kinnan, Bonder Prodigy','Ioreth of the Healing House','Sisay, Weatherlight Captain','Preston, the Vanisher','Felidar Guardian','Radiant Solar','Viscera Seer','Kasmina, Enigma Sage','Enter the Infinite',"Thassa's Oracle",'Snapcaster Mage']
    for name in extras:
        if name not in preview:
            preview[name]=dict(name=name,image='https://api.scryfall.com/cards/named?exact='+quote(name)+'&format=image',faces=[])
    for c in cards:
        c['image']=preview[c['name']]['image']
    payload=dict(date='18 ottobre 2026',cards=cards,previews=list(preview.values()))
    (ROOT/'discovery-data-20261018.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    html=(ROOT/'discovery-template.html').read_text(encoding='utf-8').replace('__DISCOVERY_DATA__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
    (ROOT/'Reality-Fracture-Discovery.html').write_text(html,encoding='utf-8')
    # Update both the retained template and generated portal without rebuilding unrelated reports.
    for file in ['database-template.html','Reality-Fracture-Sealed.html']:
        p=ROOT/file
        s=p.read_text(encoding='utf-8')
        if 'href="#discovery"' not in s:
            s=s.replace('<a href="#analysis">','<a href="#discovery">Discovery meta</a><a href="#analysis">',1)
            s=s.replace('</main>','<section id="discovery" class="workspace-embed"><iframe title="Discovery meta e tornei" data-src="Reality-Fracture-Discovery.html"></iframe></section></main>',1)
            s=s.replace("'combos','simulator','method'","'combos','simulator','discovery','method'")
        p.write_text(s,encoding='utf-8')
    p=ROOT/'build_share.py'
    s=p.read_text(encoding='utf-8')
    if "'Reality-Fracture-Discovery.html':'discovery'" not in s:
        s=s.replace(" 'Reality-Fracture-Draft.html':'draft',"," 'Reality-Fracture-Discovery.html':'discovery',\n 'Reality-Fracture-Draft.html':'draft',")
    s=s.replace('Copia condivisibile del 16 ottobre 2026','Copia condivisibile del 18 ottobre 2026').replace('portale del 16 ottobre 2026','portale del 18 ottobre 2026')
    p.write_text(s,encoding='utf-8')
    print(f'Discovery: {len(cards)} schede, {len(preview)} nomi con anteprima.')

if __name__=='__main__':
    build()
