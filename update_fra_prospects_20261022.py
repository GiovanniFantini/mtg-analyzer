"""Apply the 22 October research to extensible expansion JSON, offline.

Source observations and editorial scenarios stay separate. This script neither
changes Limited ratings/collation nor recalculates historical box EV.
"""
import collections
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
INPUT=ROOT/'research/reality-fracture-20261022'
EXP=ROOT/'expansions/reality-fracture'
DATE='2026-10-22'
READABLE='22 ottobre 2026'

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def first(name):return name.split(' // ')[0]

# Original editorial judgments from the current Oracle text. These are hypotheses
# about demand and deck construction, not attributed reviewer consensus.
EDITORIAL={
 'Dark Matter Manipulator':('Cimitero e pressione a un mana nero; alimenta Nethergoyf, Fear of Missing Out e Detective\'s Phoenix.','La domanda Modern e Legacy è concreta; risposte al cimitero e un possibile arretramento di Rakdos sono i principali rischi.'),
 'Pompous Battlemage':('Creatura rossa a un mana con prowess; Improvised Act filtra la mano e fornisce una seconda magia.','La domanda in più formati sostiene la tesi, ma una rara aperta nei Play Booster richiede adozione persistente.'),
 'The Theorist, Jace Beleren':('Motore blu da control con pescata, pedine e rimbalzo; Countersculpt e Theorist\'s Sanctum premiano la presenza di Jace.','Il prezzo incorpora già una rivalutazione: il rischio è pagare una crescita prima che i risultati successivi la confermino.'),
 'Seasoned Cryomancer':('Seleziona la mano, prepara il cimitero e rallenta gli attaccanti; adatto ai piani Superior Spider-Man e rianimazione.','La combinazione di utilizzo Standard e Pioneer è un sostegno; controllare che la domanda resti dopo la fase di esplorazione.'),
 'Stingcaster Mage':('Minaccia rapida rossa che concede flashback a un istantaneo o stregoneria nel cimitero; serve mana per la magia recuperata.','La crescita del riferimento EUR è più marcata della diffusione documentata: distinguere aspettative da adozione ripetuta.'),
 'Hexhaven Invigorator':('Quattro simboli verdi e un innesco da danno che cerca terre: investimento specifico per devotion e combinazioni con danni propri.','Richiede un mazzo dedicato; i primi risultati Pioneer non bastano a dimostrare domanda ampia.'),
 'Roiling Canopy':('Terra per Amulet e Scapeshift: Yavimaya fa contare le altre terre come Foreste e moltiplica gli inneschi.','Domanda specialistica, spesso una o due copie: servono più giocatori del mazzo per sostenere un rialzo duraturo.'),
 "Theorist's Sanctum":('Il sottotipo Isola consente alle fetch di cercarla; il valore nelle partite lunghe può giustificare una copia anche senza altri Jace.','Una copia per mazzo limita il volume di domanda, mentre la rara riceve nuova offerta dalle aperture.'),
 'Twinned Vision':('Costo ibrido e riutilizzo la rendono flessibile; in Ruby Storm guadagna valore dall\'esilio e da Past in Flames.','Comune: l\'utilizzo in più formati non elimina l\'offerta elevata né i costi di gestione delle singole economiche.'),
 'Enlightened Confidant':('Motore di carte bianco per curve basse e guadagno vite, insieme a Liliana the Faultless e Ajani Resolute.','La domanda resta legata soprattutto a Lifegain; controllare la tenuta dell\'archetipo e la sua base di giocatori.'),
 'Ajani Resolute':('Planeswalker bianco a due mana: guadagnare vite alimenta la fedeltà e le pedine.','Può beneficiare di Lifegain, ma perde attrattiva se il mazzo rimane marginale.'),
 'Liliana the Faultless':('Creatura bianca a un mana che sostiene guadagno vite e protezione delle minacce nei mazzi Orzhov.','Profilo efficiente, ma essere leggendaria e dipendere dalle sinergie limita le copie desiderate.'),
 'Theorix Charm':('Interazione blu-nera flessibile, con utilità anche nei piani che vogliono carte al cimitero.','Forte impiego non significa prezzo alto: è una non comune e la domanda deve assorbire molte copie disponibili.'),
 'Uldaros Theorix':('Creatura blu-nera costosa, particolarmente interessante da copiare con Superior Spider-Man dopo averla scartata.','Il valore dipende dalla tenuta dei mazzi che aggirano il costo; non attribuire al semplice costo di mana una bocciatura.'),
 'Yuriko, Hope from the Shadows':('Creatura blu a un mana impiegata nelle liste Dimir; seguire l\'utilizzo reale come carta di supporto.','La diffusione Standard può sostenere scambi e vendita in playset, con il limite dell\'offerta da non comune.'),
 'Master of Barbs':('Lizard rossa: i danni non da combattimento di Gev e Ingris Stingerquill potenziano gli attaccanti.','Il catalizzatore è Rakdos Lizards, quindi la domanda è concentrata in una singola famiglia di mazzi.'),
 'Ingris Stingerquill':('I danni separati durante gli attacchi alimentano Master of Barbs; in Commander può usare mana ripetutamente per creare attaccanti.','Due canali potenziali, competitivo e Commander, ma il costo nero-rosso restringe i mazzi compatibili.'),
 'Stingerquill Charm':('Interazione nero-rossa modulare che completa le minacce di Rakdos Lizards.','La non comune resta sensibile all\'offerta; il segnale utile è la continuità delle liste, non una singola Top 8.'),
 'Carnivorous Cultivator':('Enroot cerca una terra e la mette nel cimitero; il corpo con tocco letale può recuperare terre infliggendo danno da combattimento.','Più applicazioni di nicchia, ma serve diffusione oltre i test iniziali per una rivalutazione stabile.'),
 'Karn, Argent Defender':('Artefatto a due mana che ferma gli inneschi causati dall\'ingresso di artefatti e creature; può ostacolare anche il proprio mazzo.','Sideboard in poche copie e applicazioni Vintage possibili; evitare di trattare una recensione come risultato agonistico.'),
 'Samut, Tyrant of Naktamun':('Dà split second ai propri istantanei e stregonerie; il corpo con costituzione uno è vulnerabile a Orcish Bowmasters.','Domanda Commander e interesse cEDH, con giudizi Vintage più scettici: le conclusioni non si trasferiscono tra formati.'),
 "Samut, Hazoret's Champion":('Creatura rossa a due mana che dà rapidità alle proprie creature, adatta ai piani con molti permanenti da attivare o attaccanti.','La domanda Commander è un canale distinto dai risultati dei mazzi da sessanta carte.'),
 'Pia, Aether Ascetic':('Scartando una carta all\'ingresso cerca un incantesimo: i tutor per creature possono così trovare Food Chain o altri motori.','Interesse cEDH specialistico; servono liste e risultati successivi per superare la fase di recensione.'),
 'Flickering Hound':('Ogni magia creatura può riutilizzare un ingresso in campo; Cloud of Faeries e Peregrine Drake sono esempi di supporti.','Commander blink può sostenere domanda; il costo di quattro mana rende importante la velocità del tavolo.'),
 'Hall of Echoes':('Per cinque mana diventa temporaneamente copia di una propria creatura e sospende la regola delle leggende.','Interessante per abilità statiche o attivate di leggende; diventare copia non genera un nuovo ingresso in campo.'),
 'Marwyn, the Preserver':('Protegge le terre con anti-malocchio e recupera qualsiasi terra dal cimitero pagando due mana.','Domanda da mazzi terre e combo specifiche; una recensione positiva non prova diffusione cEDH.'),
 'Loot, the Nexus':('Produce mana per ciascuna forza diversa tra le proprie creature; richiede campo sviluppato e possibilità di TAPpare.','Il potenziale combo richiede supporti e una chiusura, quindi monitorare mazzi reali oltre alle sequenze teoriche.'),
 'Curse-Marred Demon':('Tutor rosso all\'ingresso seguito da scarto casuale: il risultato non è garantito se si perde la carta cercata.','Possibile domanda Commander da tutor e blink, con il limite del costo e dello scarto casuale.'),
 'Bloodline Recollector':('Per prepararlo devono essere morte almeno tre creature nel turno; Ancestral Craving offre tre carte al costo di mana e vite.','Sacrifice in Commander è il canale principale da verificare; il premio della serializzata non va trasferito alla stampa base.'),
 'Craterclaw Colossus':('Chiusura rapida da sette mana: il potenziamento della squadra cresce con il numero di artefatti controllati.','Domanda Commander artefatti plausibile; non emerge una prova equivalente di adozione competitiva ampia.'),
 'Loyal Tutor':('Tutor bianco per planeswalker che mette la carta in cima, quindi richiede una pescata successiva.','La domanda dipende dai mazzi planeswalker; non equivale a un tutor che aggiunge direttamente la carta alla mano.'),
 'Omnipresence':('Otto mana per un motore che lancia gratis dalla mano entro il valore di mana consentito dal numero di creature.','Richiede sia investimento iniziale sia campo ampio: scenario soprattutto Commander, vulnerabile alle rimozioni di massa.'),
 'Gardenize':('Le morti delle proprie creature accumulano segnalini che producono mana verde nelle fasi principali successive.','La domanda dipende da motori sacrifice persistenti; non genera subito il mana appena entra.'),
 'The Echoverse Fulcrum':('Filtra una carta all\'ingresso e offre una rimozione di massa differita pagando cinque mana, TAPpando ed esiliandolo.','È un\'opzione specialistica di controllo; confrontare il costo totale con le alternative del formato.'),
 'Geist of Saint Thalia':('Riduce il costo delle proprie magie non creatura, con applicazioni nei mazzi Lessons blu.','Sostegno possibile sia da Commander sia da Standard; verificare il numero di copie effettivamente adottato.'),
 'Darklight Phoenix':('Minaccia ricorrente per mazzi che riempiono il cimitero e possono soddisfare la condizione di ritorno.','Il richiamo ad Arclight Phoenix non prova equivalenza: costi di supporto e risultati del mazzo restano decisivi.'),
 'Vraska, the Cutting Glare':('Creatura nero-verde da midrange: l\'effetto di trasformazione in Tesoro richiede una base di terre sviluppata.','L\'adozione Golgari è il catalizzatore, mentre la richiesta di colori e la condizione di terre limitano la flessibilità.'),
 'Simulacrum Shaper':('Sviluppa il mana nei mazzi verdi e contribuisce a raggiungere la soglia di terre di Vraska, the Cutting Glare.','Servono mazzi che vogliano accelerazione a tre mana; il valore Limited non dimostra domanda Constructed.'),
 'Emrakul, the Exigent Doom':('L\'esilio dalla mano potenzia una terra; il successivo lancio da dieci mana STAPpa le proprie terre.','Domanda da ramp e Commander; il numero ridotto di copie nei mazzi limita il volume rispetto a una minaccia in quattro copie.'),
 'Surgical Precision':('Risposta bianca da valutare sui bersagli reali del Pauper; interesse della recensione separato dall\'adozione osservata.','Comune: anche un aumento di utilizzo può lasciare il prezzo basso per l\'offerta abbondante.'),
 'Jace\'s Machinations':('Permette attivazioni di fedeltà nel turno avversario e sostiene piani dedicati ai planeswalker.','Le combinazioni con Kasmina richiedono prove di torneo; il monitoraggio ufficiale non equivale a una previsione di ban.'),
 'Chandra, Chill of Compliance':('Planeswalker blu a tre mana per risorse e controllo temporaneo delle creature.','Confrontare adozione effettiva e prezzo già richiesto: le prime presenze non dimostrano una staple.'),
 'Chandra, Torch of Defiance':('Ristampa versatile per vantaggio carte, mana e rimozione nei mazzi rossi.','La nuova offerta si somma alle stampe precedenti; il ritorno in Standard può aumentare la domanda senza garantire rialzi.'),
 'Tarmogoyf':('Ristampa che premia diversi tipi di carta nei cimiteri; il successo storico non si trasferisce automaticamente allo Standard attuale.','Molte ristampe e cambiamento della concorrenza tra creature limitano l\'inferenza dal solo nome storico.'),
}

VINTAGE={
 'Ginger, Queen of Sweets':('ipotesi positiva','La recensione propone monarch e pedine negli artefatti Workshop; non costituisce un risultato di torneo.'),
 'Karn, Argent Defender':('ipotesi positiva','Possibile impiego con Mishra\'s Workshop e Phyrexian Dreadnought; mancano qui risultati che confermino la recensione.'),
 "Theorist's Proxy":('ipotesi positiva','Interessante con Lurrus per rendere non neutralizzabile una magia; la fonte è una recensione.'),
 'Darklight Phoenix':('scettica','La recensione mette in dubbio l\'affidabilità della condizione di ritorno.'),
 'Samut, Tyrant of Naktamun':('scettica','La recensione preferisce alternative e segnala la fragilità del corpo.'),
 "Vraska's Final Mercy":('esplorativa','Modalità di rimozione e Jace da esplorare; nessun risultato dimostrato dalla recensione.'),
 'Solitary Cell':('esplorativa','Risposta a permanenti piccoli e filtraggio: idea da testare.'),
}
CEDH={
 'Niv-Mizzet, Ghost Counsel':'esplorativa',
 'Samut, Tyrant of Naktamun':'priorità di test', 'Flickering Hound':'priorità di test',
 'Pia, Aether Ascetic':'priorità di test', 'Marwyn, the Preserver':'specialistica',
 'Carnivorous Cultivator':'specialistica', 'Loot, the Nexus':'specialistica',
 'Curse-Marred Demon':'specialistica', 'Ingris Stingerquill':'esplorativa',
 'Hall of Echoes':'specialistica',"Samut, Hazoret's Champion":'esplorativa',
}
PAUPER_REVIEW={'Surgical Precision':'candidata per test','Unflinching Hortimancer':'sinergia Lifegain',"Protege's Awakening":'test empower Jace','Cast Away Doubt':'attrito, senza casa evidente','Theoretical Necromancer':'combo specialistica','No Admittance':'valutazione prudente','Bestial Incursion':'valutazione prudente','Budding Insurgent':'risposta su creatura','Twinned Vision':'pescata riutilizzabile','Living Library':'valutazione prudente','Murmuring Volume':'valutazione prudente'}
LABELS={'standard':'Standard','pioneer':'Pioneer','modern':'Modern','legacy':'Legacy','vintage':'Vintage','pauper':'Pauper','commander':'Commander','historic':'Historic','timeless':'Timeless','alchemy':'Alchemy','duel':'Duel Commander','brawl':'Brawl','standardbrawl':'Standard Brawl','competitivebrawl':'Competitive Brawl','paupercommander':'Pauper Commander','oathbreaker':'Oathbreaker','penny':'Penny Dreadful','gladiator':'Gladiator','oldschool':'Old School','premodern':'Premodern','predh':'PreDH','tlr':'TLR'}

def numeric(value):return float(value) if value is not None else None

def main():
    cards_doc=read(EXP/'cards.json');catalog=cards_doc['cards']; ratings=read(EXP/'ratings.json')
    fra=read(INPUT/'scryfall-fra.json');spg=read(INPUT/'scryfall-spg.json');frc=read(INPUT/'scryfall-frc.json')
    old=read(INPUT/'scryfall-fra-20261018.json')+read(INPUT/'scryfall-spg-20261018.json')
    historical={c['id']:c for c in old}
    current=fra+spg+frc
    by_name=collections.defaultdict(list)
    for c in current:by_name[first(c['name'])].append(c)
    evidence=read(INPUT/'tournament-evidence.json');observed=collections.defaultdict(list)
    for row in evidence['cards']:observed[row['name']].append(row)
    edh=collections.defaultdict(list)
    for row in read(INPUT/'commander-evidence.json'):edh[row['name']].append(row)
    limited=collections.defaultdict(list)
    for file in ['limited-review-evidence.json','limited-independent-evidence.json']:
        for row in read(INPUT/file):limited[row['name']].append(row)
    cross={r['name']:r for r in read(INPUT/'historical-usage-crosscheck.json')}
    cedh_data=read(INPUT/'cedh-evidence.json');cedh={r['name']:r for r in cedh_data['cards']}
    duel_data=read(INPUT/'duel-evidence.json')
    audit=read(INPUT/'fetch-audit.json')
    reviews=read(INPUT/'editorial-card-reviews.json')['cards']
    assert set(reviews)=={c['id'] for c in catalog if not c.get('basic')}, 'Ogni carta non base deve avere una revisione editoriale distinta'
    commander_reviews=read(INPUT/'editorial-commander-reviews.json')['cards']
    sources={r['id']:r for r in audit}
    if 'deckcortex-cedh' in sources:
        sources['deckcortex-cedh'].update(status='retrieved',access='Article verified with the web reader; structured numerical findings in cedh-evidence.json. Direct HTTP response is only the application shell.',verifiedArticleDate='2026-10-12')
    sources['scryfall-spg']={'id':'scryfall-spg','publisher':'Scryfall','kind':'oracle-legalities-market-reference','url':spg[0]['uri'],'urls':[c['uri'] for c in spg],'retrieved':DATE,'status':'retrieved','cards':len(spg),'access':'Individual existing printing IDs, not a set-wide SPG query'}
    sources['scryfall-frc']={'id':'scryfall-frc','publisher':'Scryfall','kind':'oracle-legalities-market-reference','url':'https://api.scryfall.com/cards/search?q=set%3Afrc&unique=prints','retrieved':DATE,'status':'retrieved','printings':len(frc)}
    sources['wizards-commander-rules']={'id':'wizards-commander-rules','publisher':'Wizards / Magic.gg','kind':'official-rules','url':'https://magic.wizards.com/en/news/announcements/edge-of-eternities-update-bulletin','retrieved':DATE,'status':'retrieved','access':'Official source checked in web search','rules':['903.5e','903.11'],'finding':'Commander has no sideboard; ordinary outside-the-game effects cannot bring traditional cards into the game.'}

    def assessment(card, printing_set=None):
        name=card['name'];cid=card['id']; printings=[p for p in by_name[name] if printing_set is None or p['set']==printing_set]
        # Prefer a numbered base printing, irrespective of the catalog image treatment.
        printings.sort(key=lambda p:(not p['collector_number'].isdigit(),int(p['collector_number']) if p['collector_number'].isdigit() else 99999))
        selected=printings[0]; legality=selected['legalities']; basis=ratings['cards'].get(cid)
        current_eur=numeric(selected['prices'].get('eur'));prev=historical.get(selected['id']);old_eur=numeric(prev['prices'].get('eur')) if prev else None
        change=None if current_eur is None or old_eur in (None,0) else round((current_eur/old_eur-1)*100,2)
        observations=[];formats={}; source_ids={'scryfall-api' if selected['set']=='fra' else 'scryfall-'+selected['set'],'wizards-release','wizards-banlist','wizards-collecting'}
        for fmt in LABELS:
            legal=legality.get(fmt,'unknown')
            legal_now=legal in ('legal','restricted')
            row=next((r for r in observed[name] if r['format']==fmt),None)
            item={'legality':legal,'evidence':'non_documentata' if legal_now else 'non_legale' if legal in ('not_legal','banned') else 'non_verificata','prospect':'da_verificare' if legal_now else 'non_applicabile','confidence':'bassa' if legal_now else 'alta'}
            if row and legal_now:
                item.update(evidence='liste_documentate',prospect='adozione_ripetuta' if row['decklistsWithCard']>=10 else 'prime_presenze',confidence='media',observation=len(observations))
                observations.append(row);source_ids.add('postboard')
            if fmt=='vintage' and name in VINTAGE and legal_now:
                tone,note=VINTAGE[name];item.update(evidence='recensione',prospect=tone,note=note,confidence='bassa');source_ids.add('goldfish-vintage')
            if fmt=='pauper' and name in PAUPER_REVIEW and legal_now:
                item['review']={'source':'cardsrealm-pauper','finding':PAUPER_REVIEW[name]};source_ids.add('cardsrealm-pauper')
            formats[fmt]=item
        commander=edh[name]
        if commander and formats['commander']['legality']=='legal':
            formats['commander'].update(evidence='liste_pubblicate_non_agonistiche',prospect='adozione_documentata',confidence='media')
            source_ids.add('edhrec')
        commander_legal=legality.get('commander')=='legal'
        formats['cedh']={'legality':legality.get('commander','unknown'),'evidence':'recensione' if name in CEDH and commander_legal else 'non_documentata' if commander_legal else 'non_legale','prospect':CEDH.get(name,'da_verificare') if commander_legal else 'non_applicabile','confidence':'bassa'}
        if name in CEDH:source_ids.add('cardsrealm-cedh')
        if name=='Extrapolate the Impossible':
            for fmt in ['commander','cedh']:
                formats[fmt].update(evidence='regole_ufficiali',prospect='effetto_non_funzionante_regole_ordinarie',confidence='alta',rule='903.11')
            source_ids.add('wizards-commander-rules')
        cedh_row=cedh.get(name)
        if cedh_row and commander_legal:
            formats['cedh'].update(evidence='liste_documentate',prospect='adozione_documentata' if cedh_row['lists']>=10 else 'presenza_isolata',confidence='media' if cedh_row['lists']>=10 else 'bassa',sampleWindow=cedh_data['window'])
            source_ids.add('deckcortex-cedh')
        if name==cedh_data['verifiedTournament']['name']:
            formats['cedh'].update(evidence='risultato_di_torneo',prospect='primo_risultato_maggiore',confidence='media',tournament=cedh_data['verifiedTournament']);source_ids.add('edhtop16-dack')
        duel_row=name in duel_data['names']
        if duel_row and formats['duel']['legality'] in ('legal','restricted'):
            formats['duel'].update(evidence='elenco_popolari_beta',prospect='presenza_segnalata',confidence='bassa',sourceAsOf=duel_data['sourceAsOf']);source_ids.add('duel-meta')
        formats['draft']={'legality':'product_dependent','evidence':'recensioni' if limited[name] else 'profilo_editoriale_precedente' if basis else 'non_documentata','prospect':basis.get('role','da_verificare') if basis else 'da_verificare','confidence':'media' if limited[name] else 'bassa'}
        for fmt in ['sealed','pick_two']:formats[fmt]={'legality':'product_dependent','evidence':'nessuna_valutazione_specifica_nuova','prospect':'dipende_dal_pool','confidence':'bassa'}
        for review in limited[name]:source_ids.add(review['source'])
        if name in cross:source_ids.add('mtgdecks')
        observed_formats=[LABELS[r['format']] for r in observed[name]]
        summary=('Presenze nel campione: '+', '.join(f"{LABELS[r['format']]} ({r['decklistsWithCard']} liste)" for r in observed[name])+'.') if observed_formats else 'Nessuna presenza nelle schede pubblicate del campione a cinque formati; non equivale ad assenza di gioco.'
        if cedh_row:summary+=f" cEDH: {cedh_row['lists']} liste su 3.351 nella finestra 2-11 ottobre, con possibili duplicati."
        if duel_row:summary+=' Duel Commander: segnalata tra le carte popolari della fonte beta, senza conteggio o rendimento per carta.'
        if card.get('basic'):summary='Terra base: utilizzo strutturale, non una candidatura a nuova staple. Prezzo distinto per illustrazione e finitura.'
        thesis,price_note=EDITORIAL.get(name,(None,None))
        if thesis is None:
            thesis=('Ruolo nel Limited: '+basis['role']+'. '+basis['why']) if basis else 'Valutare il testo Oracle e la funzione nel mazzo; non è stata attribuita una valutazione competitiva senza riscontri.'
        has_competitive=bool(observed_formats)
        regular_commander=next((r for r in commander if r['group'].startswith('Cards') or r['group']=='Reprints'),None)
        if price_note is None:
            if card.get('basic'):price_note='Per la stampa base la domanda di gioco è diffusa; il premio di collezione va valutato sulla specifica illustrazione e finitura.'
            elif selected.get('reprint'):price_note='L\'utilizzo già esistente può sostenere domanda, ma l\'offerta della ristampa e le altre edizioni rendono incerto un rialzo.'
            elif has_competitive:price_note='Domanda agonistica osservata in '+', '.join(observed_formats)+'. La tenuta del prezzo richiede che l\'adozione assorba la nuova offerta.'
            elif regular_commander:price_note=f"Domanda Commander osservata in {regular_commander['decks']} liste: è un sostegno possibile, senza dimostrare crescita delle vendite o del prezzo."
            else:price_note='Non emerge un catalizzatore di domanda verificato: manca una base per prevedere un rialzo della stampa ordinaria.'
        if name=='Extrapolate the Impossible':price_note="In Commander ordinario l'effetto non funziona (903.11). La tesi di domanda deve basarsi sui formati con sideboard e su una coppia di opzioni entrambe utili."
        demand=['Adozione ripetuta nei mazzi '+', '.join(observed_formats)] if has_competitive else []
        if regular_commander and name!='Extrapolate the Impossible':demand.append('Domanda Commander da liste pubblicate; non risultati di torneo né compravendite')
        if name in CEDH:demand.append('Conferma futura dei test cEDH indicati dalla recensione')
        if cedh_row:demand.append(f"Conferma dell'adozione cEDH oltre la finestra 2-11 ottobre ({cedh_row['lists']} liste rilevate)")
        risks=['Nuove aperture e disponibilità di copie','Mancano dati su vendite concluse, liquidità e differenza tra acquisto e vendita']
        if selected.get('reprint'):risks.append('Offerta delle edizioni precedenti e della ristampa')
        if selected['rarity'] in ('common','uncommon'):risks.append('Offerta elevata e costi di gestione rispetto al valore unitario')
        if change is not None and change>20:risks.append('Il riferimento è già salito: il movimento passato può anticipare la domanda o riassorbirsi')
        if has_competitive and all(f=='Standard' for f in observed_formats):risks.append('Domanda competitiva concentrata nello Standard e soggetta al cambio del metagame')
        variants=[]
        for p in printings:
            variants.append({'printingId':p['id'],'number':p['collector_number'],'set':p['set'],'finishes':p['finishes'],'eur':numeric(p['prices'].get('eur')),'eurFoil':numeric(p['prices'].get('eur_foil')),'eurEtched':numeric(p['prices'].get('eur_etched')),'usd':numeric(p['prices'].get('usd')),'usdFoil':numeric(p['prices'].get('usd_foil'))})
        gameplay_review=reviews.get(cid,commander_reviews.get(cid))
        if card.get('basic'):gameplay_review='Terra base utilizzabile nei mazzi del colore appropriato. La domanda di collezione riguarda illustrazione e finitura: non confonderla con nuova giocabilità.'
        if gameplay_review is None:gameplay_review=thesis
        result={'date':DATE,'kind':'evidence_and_editorial_scenarios','summary':summary,'editorialThesis':thesis,'gameplayReview':{'kind':'analisi_editoriale_oracle','finding':gameplay_review,'evidenceOfTournamentSuccess':False},'sources':sorted(source_ids),'oracle':{'printingId':selected['id'],'url':selected['scryfall_uri'],'set':selected['set'],'number':selected['collector_number'],'manaCost':selected.get('mana_cost',card.get('cost','')),'text':selected.get('oracle_text') or '\n'.join(f['oracle_text'] for f in selected.get('card_faces',[]) if f.get('oracle_text'))},'formats':formats,'tournamentObservations':observations,'commanderObservations':commander,'limitedReviews':limited[name],'limitedProfile':{'date':ratings['date'],'role':basis['role'],'condition':basis['condition']} if basis else None,'historicalUsageCrosscheck':cross.get(name),'price':{'date':DATE,'currency':'EUR','metric':'Scryfall EUR reference for the identified printing; not Cardmarket From or realized sale','printingId':selected['id'],'set':selected['set'],'number':selected['collector_number'],'nonfoil':current_eur,'foil':numeric(selected['prices'].get('eur_foil')),'comparison':{'date':'2026-10-18','samePrinting':True if prev else None,'nonfoil':old_eur,'changePct':change,'status':'comparable' if change is not None else 'missing_reference'},'variants':variants,'outlook':{'kind':'scenario_condizionale','horizonsMonths':[3,12],'thesis':price_note,'gameplayDependency':gameplay_review,'upsideConditions':demand or ['Nuova adozione o domanda di collezione da documentare'],'downsideRisks':risks,'confidence':'bassa','targetPrice':None,'probabilityOfRise':None,'action':'monitorare_domanda_e_prezzo_della_stessa_stampa'}},'limitations':['Una lista può ricomparire in eventi diversi; non sommare le fonti come giocatori indipendenti.','Non documentata significa copertura insufficiente, non carta ingiocabile.','Le legalità da API non certificano la disponibilità su una piattaforma o nel prodotto Limited.']}
        result['cedhObservation']={**cedh_row,'window':cedh_data['window'],'source':'deckcortex-cedh'} if cedh_row else None
        result['duelObservation']={**duel_data,'names':[name]} if duel_row else None
        return result

    # Preserve a dated, reproducible baseline before overwriting expansion inputs.
    backup=INPUT/'before-update.json'
    if not backup.exists():write(backup,{key:read(EXP/(key+'.json')) for key in ['cards','discovery','prices','sources','expansion']})
    baseline=read(backup)
    if 'guides' not in baseline:
        baseline['guides']=read(EXP/'guides.json');write(backup,baseline)
    for card in catalog:card['prospects']=assessment(card,card['set'].lower())
    appendix=[]
    grouped=collections.defaultdict(list)
    for p in frc:grouped[p['oracle_id']].append(p)
    for oid,prints in grouped.items():
        p=min(prints,key=lambda c:int(c['collector_number']) if c['collector_number'].isdigit() else 9999)
        image=p.get('image_uris') or (p.get('card_faces') or [{}])[0].get('image_uris',{})
        card={'id':'frc-'+p['collector_number'],'name':first(p['name']),'full':p['name'],'set':'FRC','number':p['collector_number'],'basic':'Basic Land' in p['type_line'],'image':image.get('normal',''),'large':image.get('large',''),'url':p['scryfall_uri'],'type':p['type_line'],'cost':p.get('mana_cost',''),'rarity':p['rarity']}
        appendix.append({**card,'prospects':assessment(card,'frc')})
    assert set(commander_reviews)=={c['id'] for c in appendix}
    write(EXP/'prospects-commander-20261022.json',{'date':DATE,'scope':'87 identità del prodotto FRC; separate dalle 295 carte del catalogo Limited','cards':appendix})
    cards_doc['prospectsDate']=DATE
    write(EXP/'cards.json',cards_doc)

    registry=read(EXP/'sources.json');publishers=sorted({s['publisher'] for s in sources.values() if s['status']=='retrieved'})
    registry['research']={'date':DATE,'scope':{'catalogIdentities':len(catalog),'fraNonbasic':280,'basicLandIdentities':5,'specialGuestIdentities':10,'commanderProductIdentities':len(appendix),'treatmentRule':'Valutazione di gioco per identità; prezzi per stampa e finitura'},'publishers':publishers,'publisherCount':len(publishers),'sources':list(sources.values()),'tournamentContexts':evidence['contexts'],'methodology':{'observation':'Metriche pubblicate dalle fonti, senza trasformarle in causalità o probabilità di vittoria.','edhrec':'Liste pubblicate, non partite vinte; denominatore per identità di colore. Ristampe con storico di tutte le edizioni.','postboard':'Campione di 3.313 liste. 104 schede per carta/formato (66 identità) estratte; altre presenze isolate non sono visibili nelle schede. Percentuali ponderate per dimensione evento.','limited':'Recensioni con scala originale e profilo editoriale preesistente datato; nessuna modifica ai voti del motore. Non trasferire un voto Draft a Sealed o Pick-Two.','prices':'Confronto EUR Scryfall 18/22 ottobre della stessa stampa. USD, foil e trattamenti restano separati. Nessun nuovo minimo Cardmarket verificato.','forecast':'Scenari editoriali a 3 e 12 mesi, senza prezzi obiettivo o probabilità inventate.','unknownFormats':'Tutti i formati censiti dalle legalità ricevono uno stato; dove mancano risultati si dichiara la lacuna, senza assegnare voti fittizi.','productBoundaries':'Le Special Guests non acquisiscono legalità Standard o Pioneer dal prodotto FRA. Il prodotto Commander FRC resta separato dal catalogo e dalla collazione.'},'sourceDisagreements':[{'sources':['pauperpilot','postboard'],'finding':'PauperPilot mostra 1 carta nella finestra 12 settembre/11 ottobre; Postboard ne elenca 3 nel campione successivo. Finestre e copertura diverse, non mediare i dati.'},{'sources':['echomtg','scryfall-api'],'finding':'EchoMTG usa riferimenti TCGplayer mid USD, Scryfall espone riferimenti USD/EUR diversi. Non fondere quotazioni e trend.'}],'unavailable':[s for s in sources.values() if s['status']!='retrieved'],'commanderAppendix':'prospects-commander-20261022.json'}
    registry['research']['cedhContext']={'source':'deckcortex-cedh',**cedh_data['window'],'retrieved':DATE,'limitations':cedh_data['limitations']}
    registry['research']['duelContext']={key:value for key,value in duel_data.items() if key!='names'}
    write(EXP/'sources.json',registry)
    prices=read(EXP/'prices.json')
    # This is NOT sufficient to enable the historical box-EV capability.
    prices['references']={'available':True,'date':DATE,'metric':'Scryfall EUR per printing','location':'cards.json: cards[].prospects.price','cardmarketFromAvailable':False,'soldPricesAvailable':False,'boxEVUpdated':False,'missing':'Minimi Cardmarket aggiornati e vendite concluse non rilevati.'}
    write(EXP/'prices.json',prices)
    manifest=read(EXP/'expansion.json');asset='expansions/reality-fracture/prospects-commander-20261022.json'
    if asset not in manifest['assets']:manifest['assets'].append(asset)
    write(EXP/'expansion.json',manifest)
    discovery=read(EXP/'discovery.json');lookup={c['name']:c for c in catalog+appendix}
    for card in discovery['cards']:
        if card['name'] not in lookup:continue
        prospect=lookup[card['name']]['prospects'];rows=prospect['tournamentObservations']
        if rows:
            card['formats']=list(dict.fromkeys(card['formats']+[LABELS[r['format']] for r in rows]))
            card['evidence']=prospect['summary']+' Campione Postboard dal 25 settembre, rilevato il 22 ottobre; le presenze non sono una percentuale di vittorie.'
            if not any(url=='https://www.postboard.gg/sets/fra' for _,url in card['sources']):card['sources'].append(['Snapshot per formato, 22 ottobre','https://www.postboard.gg/sets/fra'])
        if prospect['cedhObservation']:
            card['evidence']=prospect['summary']
            if not any(url=='https://deckcortex.com/articles/reality-fracture-cedh-first-ten-days' for _,url in card['sources']):card['sources'].append(['Campione cEDH, 2-11 ottobre','https://deckcortex.com/articles/reality-fracture-cedh-first-ten-days'])
        if prospect['duelObservation'] and 'Duel Commander' not in card['formats']:card['formats'].append('Duel Commander')
        if card['name'] in ['Seasoned Cryomancer','Carnivorous Cultivator','The Theorist, Jace Beleren']:card['level']='Confermata'
        if card['name'] in ['Unflinching Hortimancer',"Jace's Machinations",'Stingcaster Mage']:card['level']='Emergente'
        if card['name']=='Pompous Battlemage':card['verdict']='Adozione ripetuta in Standard, Pioneer e Modern, con un ruolo coerente nei mazzi prowess.'
        if card['name']=='Seasoned Cryomancer':card['verdict']='Adozione confermata soprattutto in Standard, con presenze ripetute anche in Pioneer e Modern.'
        if card['name']=='The Theorist, Jace Beleren':card['verdict']='Domanda documentata in Standard, Pioneer, Modern e Commander; il prezzo è già cresciuto sensibilmente.'
        if card['name']=="Jace's Machinations":card['verdict']="Presenze ripetute in Standard; la combinazione Pioneer resta un'ipotesi distinta dai risultati del campione."
        if card['name']=='Dack Fayden, Helping Hand':card['evidence']='Tim Taranto vince BAKED ZITI 4 il 3 ottobre: 119 giocatori, 6-0-1. Risultato EDHTop16 ricontrollato il 22 ottobre; un torneo non basta a definirne la forza stabile.'
        card['priceProspect']=prospect['price']['outlook']
        card['priceReference']={k:prospect['price'][k] for k in ['date','currency','metric','nonfoil','foil','comparison','printingId']}
    discovery['date']=READABLE
    discovery['research']={'date':DATE,'catalogCoverage':295,'publisherCount':len(publishers),'details':'data/cards.json: cards[].prospects','commanderAppendix':'prospects-commander-20261022.json'}
    write(EXP/'discovery.json',discovery)
    guides=read(EXP/'guides.json')
    guides['fragments']['discovery.copy-0']='OSSERVATORIO CONSTRUCTED · 22 OTTOBRE 2026'
    guides['fragments']['discovery.copy-1']=' Riscontri aggiornati al 22 ottobre 2026. Scegli le carte selezionate o tutte le analisi per consultare utilizzo, prezzi e fonti. Le carte del prodotto Commander restano separate dal catalogo Limited. Le finestre delle fonti restano distinte; adozione e piazzamenti non misurano il contributo causale di una carta.'
    guides['fragments']['discovery.copy-4']='Snapshot Postboard del 22 ottobre: 3.313 liste in Standard, Pioneer, Modern, Pauper e Legacy. Le 104 schede carta/formato estratte coprono 66 identità; le presenze isolate non pubblicate non diventano zeri. Gli archivi possono condividere gli stessi eventi.'
    guides['fragments']['discovery.copy-6']='Il nuovo snapshot Postboard è aggregato per formato, senza un censimento geografico completo. I Regional dell\'analisi Wizards del 15 ottobre restano un campione separato. Non attribuiamo risultati a carte senza una lista verificabile e non sommiamo archivi potenzialmente sovrapposti.'
    method=guides['fragments']['discovery.method']
    method=method.replace('Non risultano Pro Tour post uscita del set nella copertura verificata.','Questo campione ufficiale è datato 15 ottobre e resta distinto dagli aggiornamenti successivi.')
    addition=f'<p id="prospects-research">Ricerca del 22 ottobre: 295 carte del catalogo e 87 identità del prodotto Commander, con {len(publishers)} editori o servizi distinti. Ogni carta separa giudizio Oracle, risultati, legalità e scenari di prezzo. <a href="data/cards.json">Scarica tutte le analisi del catalogo</a> · <a href="prospects-commander-20261022.json">Appendice Commander</a> · <a href="data/sources.json">Fonti, date e metodo</a>. Prezzi EUR Scryfall per la stessa stampa, con confronto al 18 ottobre: non sono minimi Cardmarket né vendite concluse. Nessun prezzo obiettivo o probabilità di rialzo.</p>'
    if 'id="prospects-research"' in method:method=re.sub(r'<p id="prospects-research">.*?</p>',lambda m:addition,method)
    else:method=method.replace('</details></section>','</details>'+addition+'</section>')
    guides['fragments']['discovery.method']=method
    write(EXP/'guides.json',guides)
    write(INPUT/'assessment-summary.json',{'date':DATE,'catalog':len(catalog),'commanderAppendix':len(appendix),'publishers':publishers,'withTournamentSightings':sum(bool(c['prospects']['tournamentObservations']) for c in catalog),'withCommanderSightings':sum(bool(c['prospects']['commanderObservations']) for c in catalog),'withLimitedReviews':sum(bool(c['prospects']['limitedReviews']) for c in catalog),'eurReferenceAvailable':sum(c['prospects']['price']['nonfoil'] is not None for c in catalog),'eurComparable':sum(c['prospects']['price']['comparison']['status']=='comparable' for c in catalog)})
    print(json.dumps(read(INPUT/'assessment-summary.json'),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
