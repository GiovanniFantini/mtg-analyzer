# MTG Analyzer

Sito statico in italiano dedicato alle espansioni di Magic: The Gathering. Reality Fracture comprende catalogo, pool personale, guida Draft, analisi Sealed, combo, simulatore e discovery del metagame. Star Trek ha una sezione di anteprima separata, con catalogo e strumenti Limited basati sui dati disponibili.

Sito: https://giovannifantini.github.io/mtg-analyzer/

## Sviluppo e pubblicazione

Richiede Python 3.12 o successivo, senza pacchetti esterni.

```sh
python build_site.py
python -m http.server 8765 --directory dist
```

Aprire http://localhost:8765. La build rigenera le pagine dai template e dagli snapshot locali, prepara `dist/` e verifica i riferimenti locali. Non scarica prezzi, risultati o nuovi dati da Internet.

Ogni push su `main` esegue la build e pubblica `dist/` con GitHub Actions e GitHub Pages. Un errore di build impedisce il deploy. La cartella di lavoro, gli script e i dati grezzi non vengono serviti come risorse del sito.

## Ricerca e analisi degli aggiornamenti delle espansioni

Giovanni richiede una ricerca che arrivi a informazioni utilizzabili: confronto con quanto già presente, lettura di fonti diverse, analisi critica dei giudizi e, quando richiesto, integrazione nel repository. La ricerca deve coprire anche recensioni delle singole carte senza voti numerici, senza fermarsi all'assenza di classifiche complete. Le preferenze operative sono in `AGENTS.md`, nella sezione sulla ricerca di aggiornamenti, ranking e recensioni.

Il procedimento è riutilizzabile per tutte le espansioni:

1. Leggere catalogo, snapshot e ricerca precedente; identificare le lacune e confrontare i nuovi risultati con la rilevazione precedente. Registrare separatamente nuove informazioni, conferme e contesto storico.
2. Consultare fonti ufficiali per annunci, regole, legalità e prodotti; affiancare fonti specialistiche e autori delle recensioni per valutazioni e strategie. Registrare URL, autore quando disponibile, data di pubblicazione e verifica, accesso diretto o solo tramite indice, ambito e copertura effettiva.
3. Analizzare separatamente statistiche osservate, ranking automatici e recensioni qualitative. Per un voto conservare scala, metodo e contesto; per una recensione conservare conclusione attribuita, motivazione e limiti. Verificare sul testo Oracle e sulle regole le interazioni da cui dipende il giudizio, documentando eventuali correzioni. Una recensione autorevole può comunque contenere errori.
4. Su richiesta di aggiornamento, conservare acquisizioni e analisi datate, collegare le osservazioni agli identificativi stabili e usare i documenti appropriati sotto `expansions/<slug>/`: provenienza e valutazione delle fonti in `sources.json`, sintesi per carta in `sentiment.json` quando pertinenti, contenuti e sequenze in `guides.json`, statistiche osservate in `statistics.json`. Usare `ratings.json` soltanto per valutazioni Limited con significato coerente con la scala del progetto. Un numero esterno non abilita automaticamente uno strumento o una politica dei bot.
5. Aggiornare le pagine interessate dai dati, mantenere esempi concreti e anteprime accessibili, eseguire le verifiche pertinenti e indicare copertura, limiti e stato reale del lavoro. Aggiornamento locale, push e pubblicazione riuscita sono esiti distinti.

Il confronto Star Trek del 22 ottobre 2026 è un'applicazione di questo flusso: `sources.reviewAnalysis` e `star-trek-reviews-20261022.json` conservano punteggi preliminari, recensioni e correzioni. Quel contenuto è uno snapshot specifico, non una classifica generale né un nuovo contratto obbligatorio per tutte le espansioni.

## Espansioni

`expansions.json` registra i manifest delle espansioni. La build usa `expansion_data.py` per caricare e validare i documenti e `build_expansion.py` per generare tutte le pagine. Non contiene diramazioni per codice del set. I vecchi builder sono ingressi di compatibilità verso lo stesso percorso.

Ogni espansione ha una cartella sotto `expansions/<slug>/`:

- `expansion.json`: versione dello schema, identità, file collegati, pagine, strumenti richiesti e chiavi dei salvataggi.
- `cards.json` e `printings.json`: catalogo delle carte e stampe effettivamente usate nella collazione. Le diverse stampe mantengono identità distinte; `catalogId` viene risolto per la visualizzazione.
- `products.json`: prodotti, dimensione delle buste, gruppi di stampe, probabilità, coppie e ricetta di estrazione.
- `limited.json`: eventi Draft, Sealed e Pick-Two, ciascuno collegato al proprio prodotto.
- `ratings.json`, `archetypes.json`, `combos.json`: valutazioni, piani e sinergie. Gli indici delle combo vengono ricalcolati dai dati.
- `guides.json`: contenuti editoriali, priorità dei pick, bait, situazioni di scelta e pacchetti Draft. I frammenti HTML sono contenuto di presentazione già presente, conservato per mantenere l’interfaccia. Le liste interattive sono generate dai dati strutturati.
- `statistics.json`: viste degli snapshot statistici, con le loro date e contesti. I dati datati del report restano distinti dal catalogo e non diventano aggiornati per effetto della build.
- `sentiment.json`: metadati della ricerca e osservazioni per identità di carta.
- `discovery.json`, `prices.json`, `sources.json`, `ui.json`: metagame documentato, disponibilità dei prezzi, fonti e testi/esempi specifici degli strumenti.

I template sotto `templates/atlas/` e `templates/preview/` conservano le due presentazioni esistenti. Il manifest sceglie i template condivisi per pagina. Aggiungere un’espansione richiede documenti JSON e una voce nel registro, senza un nuovo builder o una nuova interfaccia di gestione. Gli asset pubblici aggiuntivi sono elencati esplicitamente nel manifest; gli snapshot storici alla radice restano conservati.

I token `fragment:chiave` richiedono la stessa chiave in `guides.fragments`; `source:chiave` richiede un URL grezzo in `sources.links`. Chiavi mancanti fermano la build con documento e chiave da completare. `optionalFragment` e i frammenti `draft.report-N` possono essere omessi. Le guide strutturate, comprese le situazioni di scelta, non richiedono i frammenti del report. `sources.downloads` dichiara i download opzionali con `url` e `label`, e i relativi file vanno inclusi negli asset. Il catalogo e le statistiche conservano date separate (`ratings.date`, `statistics.catalogDate`, `statistics.draft.date`).

`ui.json` contiene esempi dei bot, alias, etichette dei set, esempi di importazione, preset di analisi ed eventuale ordine `discoveryLevels`. I formati della discovery derivano dalle carte. Un preset di analisi con un valore assente nei filtri non viene mostrato. I calcolatori delle combo sono opzionali: `calculator.kind: netMana`, `netPerCycle`, `unit`, `label` e `note` descrivono un guadagno fisso per ciclo senza codice eseguibile nei dati.

I template Atlas non richiedono fonti o frammenti di Reality Fracture per attivare uno strumento. Le note editoriali sono opzionali e i renderer delle guide hanno template condivisi predefiniti. Per fonti proprie, `sources.groups` contiene liste di oggetti `url` e `label`, con il nome della sezione (`draft-engine`, `pick-guide-section`, `gallery` e gli altri nomi dei template). La guida Sealed conserva il contenuto HTML in `guides.fragments.gallery.strategy`: se manca, la sezione indica esattamente questa proprietà da completare. I dati strutturati Draft restano disponibili anche senza i frammenti del report.

Un salvataggio Draft incompatibile viene conservato integralmente in una chiave separata prima della prima scrittura del nuovo draft. Se il backup fallisce, il salvataggio originale non viene sovrascritto. Il messaggio permette di scaricare il record precedente, anche dopo la riapertura del nuovo salvataggio.

La disponibilità del tavolo viene verificata per ogni evento Draft e per il suo prodotto; il selettore elenca soltanto eventi pronti e spiega cosa manca agli altri. Le statistiche per carta e il drilldown per contesto sono indipendenti: il secondo richiede anche `statistics.draft.drill.contexts` e `retrieved`.

I contratti di `cards.json` e `printings.json` sono descritti anche in `schemas/cards.schema.json` e `schemas/printings.schema.json`. Ogni carta richiede identità, nome, set, numero, colori, identità di colore, tipo, rarità, immagine, URL e dati di mana/testo. Le stampe del motore non richiedono un URL separato. Il caricatore accetta `cost`/`mana`, `mv`/`cmc` e `oracle`/`text`, mantenendo coerenti i due nomi; i campi aggiuntivi restano conservati. `full` usa il nome se omesso; facce, stampe, keyword e legalità mancanti hanno contenitori vuoti. I flag di carta base, terra e creatura si ricavano dal tipo della faccia principale se assenti. Gli errori dei campi essenziali indicano documento e carta. I documenti pubblicati contengono la forma normalizzata.

La homepage deriva percorsi e nomi dal registro. `home.featured` e `home.quickTools` nel manifest scelgono rispettivamente il set in evidenza e gli accessi rapidi; in assenza di indicazioni usa l’ultima e la prima espansione registrata. Il catalogo completo/parziale e la data della legalità derivano dai dati, anche nella presentazione di anteprima. I collegamenti locali alle sezioni assenti o non disponibili vengono omessi.

### Consultazione per legalità: requisito trasversale

L'esigenza espressa il 22 ottobre 2026 è poter consultare tutte le carte dell'espansione selezionata ammesse in un formato di gioco, per esempio Pauper, anche quando non hanno recensioni o risultati competitivi. Il requisito riguarda tutte le espansioni e tutti i formati pertinenti. Espansione, formato Constructed ed evento Limited sono dimensioni distinte.

La consultazione deve distinguere legalità attuale alla data dello snapshot, ammissibilità prevista all'uscita e interesse competitivo. Per le anteprime, conservare fonti, date e incertezze: uno stato attuale `not_legal` non basta a stabilire la futura esclusione. La copertura va dichiarata rispetto al catalogo disponibile, segnalando i set ancora parziali. Per Pauper il solo filtro di rarità della stampa non è equivalente alla legalità: contano anche le stampe comuni precedenti ammesse e la banlist. I prodotti collegati e le carte ospiti mantengono le proprie condizioni.

Stato rilevato nei sorgenti il 22 ottobre: Reality Fracture offre `Metagame e carte → Tutte le analisi` con filtro Pauper sulla legalità registrata; Star Trek non offre il filtro Pauper nel selettore Constructed né una vista dell'ammissibilità prevista all'uscita. Questa sezione documenta il requisito e il limite esistente; non attesta l'implementazione delle viste mancanti. I futuri interventi devono usare dati e componenti condivisi, mantenendo anteprime delle carte da mouse, tastiera e tocco.

### Regole delle buste e degli eventi

I documenti sono letti come oggetti JSON, attraverso un caricatore comune. Non serve un database: il sito resta statico e la build risolve i riferimenti, poi incorpora i dati necessari agli strumenti. I documenti pubblici si trovano anche sotto `sets/<slug>/data/`, compresi `runtime.json` e `availability.json`.

La collazione è una ricetta dichiarativa ordinata, eseguita da `collation.js` sia nel Draft sia nel Sealed. Le operazioni supportate sono:

- `draw`: estrae una o più carte da gruppi pesati. `unique` evita ripetizioni della stessa carta entro lo slot.
- `replace`: con probabilità `chance` sostituisce le prime carte estratte dallo slot `target`.
- `pair`: estrae una carta e il partner indicato in `partners`, con la stessa finitura.
- `exclude`: impedisce di estrarre carte con lo stesso nome completo di quelle già estratte dagli slot indicati. Per esempio, la terza echoed esclude la coppia garantita.

Esempio di uno slot, i cui gruppi sono definiti nello stesso documento:

```json
{
  "op": "draw",
  "id": "rare",
  "count": 1,
  "branches": [
    {"weight": 0.8, "group": "rare"},
    {"weight": 0.2, "group": "mythic"}
  ]
}
```

Questi pesi sono soltanto un esempio di struttura. Non sono probabilità di un prodotto reale. I pesi di ogni slot devono sommare a uno. I tassi pubblicati come `<1%` rimangono separati dai pesi modellati, con le assunzioni dichiarate. Un prodotto incompleto ha `collation: null`: i dati ufficiali disponibili possono essere conservati in `published`, ma il sito non li trasforma automaticamente in una simulazione.

Le regole dell’evento sono indipendenti dalla busta:

```json
{
  "id": "example-pick-two",
  "name": "Esempio Pick-Two",
  "kind": "draft",
  "product": "play",
  "packsPerPlayer": 3,
  "seats": 4,
  "picksPerTurn": 2,
  "directions": [1, -1, 1],
  "minDeckSize": 40,
  "maxCopies": null,
  "extraBasicLands": true,
  "mulligan": {"kind": "london", "handSize": 7, "freeMulligans": 0},
  "sources": ["https://magic.wizards.com/en/formats/pick-two-draft"]
}
```

Il motore prende entrambe le carte prima di passare la busta; se resta una sola carta, prende quella. `1` e `-1` indicano i due versi di passaggio. Sealed indica il proprio numero di buste e prodotto e usa `picksPerTurn: 0`. Le regole di costruzione e il London mulligan sono lette dal profilo dell’evento.

### Evoluzione, dati mancanti e salvataggi

`schemaVersion: 1` identifica il contratto. Proprietà aggiuntive ed `extensions` consentono ampliamenti compatibili. Una modifica incompatibile richiede una nuova versione e un adattatore esplicito nel caricatore. Una nuova operazione di collazione o procedura di gioco richiede supporto nel motore; non viene eseguito codice JavaScript dal JSON. Versioni e operazioni sconosciute fanno fallire la validazione.

Gli schemi JSON in `schemas/` descrivono manifest, prodotti ed eventi per gli editor. La build usa controlli Python senza dipendenze esterne: verifica identità, campi delle carte, riferimenti, archetipi, esempi, gruppi, partner, pesi, numerosità attese e regole degli eventi. Controlla anche la capienza delle sostituzioni ed esegue percorsi deterministici della ricetta, forzando i rami con probabilità positiva, per individuare gruppi esauriti da estrazioni uniche ed esclusioni. Queste verifiche eseguono i vincoli effettivi senza imporre limiti prudenziali che scarterebbero collazioni valide con esclusioni correlate; non costituiscono una prova esaustiva di ogni possibile sequenza. Le chiavi dei salvataggi non possono essere condivise da espansioni diverse.

`features.<strumento>.requested` indica che vogliamo quello strumento. La disponibilità effettiva viene calcolata dalle dipendenze: dichiararlo richiesto non abilita dati mancanti. Le pagine mostrano lo strumento non disponibile e cosa manca, mantenendo utilizzabili gli strumenti già pronti. Per i template Atlas sono protetti gli strumenti che richiedono collazione; nella pagina Draft le sole sezioni statistiche indicano i dati mancanti, mentre guide e pool restano utilizzabili. Le chiavi di salvataggio richieste dai controller sono validate prima della build. Scegliere un template esistente diverso richiede soltanto una modifica al manifest.

Le sessioni Draft nuove salvano la versione del motore e un’impronta dei soli dati che guidano le scelte: procedura dell’evento, collazione, identità e proprietà funzionali delle stampe, voti e appartenenza agli archetipi. Immagini, fonti e testi informativi non invalidano il replay. Le revisioni precedenti verificate sono collegate alla stessa impronta funzionale; una modifica al gioco disabilita automaticamente quelle compatibilità. Una sessione riferita a dati diversi viene rifiutata, preservando il salvataggio. Le sessioni FRA precedenti sono accettate soltanto con il profilo di compatibilità verificato. I pool e le buste Sealed già estratte mantengono le identità precedenti e le stesse chiavi locali.

Controlli del contratto:

```sh
python build_site.py
python -m unittest test_expansion_data.py
node verify-expansions.cjs
node verify-draft-engine.cjs
node verify-expansion-browser.cjs
python verify-expansion-review.py
python verify-collation-contract.py
```

I test coprono documenti incompleti o incoerenti, aggiunte compatibili, un’altra espansione senza nuovo codice, 3.000 buste storiche identiche, replay precedenti e Pick-Two a quattro posti con buste dispari.

### Star Trek

`build_star_trek.py` richiama il generatore comune per le dieci pagine sotto `sets/star-trek/`: panoramica, catalogo, Draft, pool Sealed, prova del mazzo, sinergie, analisi, Constructed, regole e fonti. I documenti attivi sono sotto `expansions/star-trek/`; gli snapshot storici `star-trek-cards-20261021.json` (163 carte distinte, 321 stampe TRK/SDS) e `star-trek-format-20261021.json` conservano la provenienza originaria. La pagina del tavolo Draft indica i requisiti ancora mancanti. La build è offline e non legge gli snapshot privati `ev-*`.

Aggiornamento del 22 ottobre 2026: il catalogo attivo comprende 193 carte distinte TRK/SDS e 366 stampe, con 30 carte aggiunte rispetto al 21 ottobre. `star-trek-scryfall-20261022.json` conserva la risposta API e `star-trek-cards-20261022.json` lo snapshot per il sito; `refresh-star-trek-20261022.py` riproduce esplicitamente la rilevazione online, fuori dalla build. Gli snapshot del 21 ottobre restano conservati e le identità delle carte già presenti sono mantenute. `sources.json` registra provenienza, date, limiti delle fonti secondarie e riscontri; `guides.json` pubblica il calendario Commander, i ritardi europei, lo Spotlight di Lille e il contesto di design. Le date editoriali e del catalogo sono distinte dalla collazione, ancora verificata al 21 ottobre e non eseguibile.

Analisi di ranking e recensioni del 22 ottobre: `star-trek-reviews-20261022.json` conserva fonti, contesti, punteggi automatici e correzioni verificate; la copia attiva è `sources.reviewAnalysis`. Le osservazioni usano gli identificativi del catalogo. I punteggi Constructed non entrano in `ratings.json` e non attivano i bot. I contenuti visibili sono in `guides.json`, nelle pagine Analisi, Draft, Constructed e Fonti, con esempi e anteprime delle carte già presenti. La recensione della carta Commander TRC è conservata separatamente dal catalogo TRK/SDS.

Il catalogo è incompleto e i prezzi non sono disponibili. Non viene simulata l'apertura delle buste né calcolato un ricavo atteso. La prova del mazzo mescola soltanto le carte selezionate dall'utente e implementa il London mulligan per il Limited uno contro uno. I controlli del mazzo verificano quantità e minimo di 40 carte, senza certificare l'idoneità delle carte al prodotto dell'evento.

I pool sono distinti per Sealed, Draft e Pick-Two, con chiavi `mtg-trk-<modalità>-v1`. Le osservate usano `mtg-trk-watch-v1`. Non vengono lette o modificate le chiavi di Reality Fracture. L'importazione JSON controlla versione, set, modalità, identità delle carte e quantità prima di sostituire lo stato.

Le modifiche rileggono il salvataggio aggiornato; Web Locks, quando disponibili, serializzano le scritture dello stesso pool fra schede. Gli eventi `storage` e `pageshow` aggiornano le pagine già aperte. Un salvataggio non leggibile viene conservato e non sovrascritto. La modalità scelta segue i collegamenti fra catalogo, costruzione, Draft e simulatore.

`node verify-star-trek-review.cjs` verifica le regressioni segnalate dalla review: aggiornamenti fra schede e simultanei, focus dei comandi e delle terre, mulligan da tastiera, modalità nei collegamenti, protezione dei dati non validi, chiusura delle anteprime fuori schermo, salvataggi FRA e memoria temporanea quando la scrittura nel browser fallisce.

Per aggiornare i dati, conservare gli input datati e creare nuovi snapshot con provenienza e data; aggiornare i riferimenti e le date nei JSON dell’espansione, verificare la collazione e le regole ufficiali prima di abilitare nuove stime. Il campo Scryfall `booster` non viene usato da solo per decidere l'idoneità durante l'anteprima.

Con il server di `dist/` sulla porta 8871, `node verify-star-trek.cjs` controlla le dieci pagine a 360, 768 e 1440 pixel, navigazione, anteprime, separazione pool, quantità, import/export, mulligan e compatibilità del catalogo FRA. Il percorso Playwright e il browser si configurano con `MTG_PLAYWRIGHT_MODULE` e `MTG_BROWSER_CHANNEL`; `MTG_SITE_URL` cambia l'URL del server.

I contenuti editoriali, le finestre statistiche e le fonti hanno date esplicite. Le classificazioni della discovery sono valutazioni editoriali e non previsioni di prezzo o probabilità di vittoria.

Pool e carte osservate sono memorizzati nel browser del visitatore, senza account o sincronizzazione. Il passaggio dal file locale al sito HTTPS non trasferisce automaticamente questi salvataggi: per il pool usare le funzioni di esportazione e importazione.

### Reality Fracture: utilizzo e prezzi, 22 ottobre 2026

Nel sito, `Metagame e carte` offre `Carte da mostrare → Tutte le analisi`: 295 identità del catalogo e 87 dell'appendice Commander, con ricerca, filtri e caricamento di 24 schede alla volta. Il filtro formato indica la legalità, non la presenza competitiva. Aprendo `Analisi per formato, prezzi e fonti` si consulta la ricerca completa. Le stesse informazioni sono nel catalogo tramite `Analisi, prezzi e fonti`. Il renderer condiviso `prospects-ui.js` legge i campi dei JSON; le espansioni senza `prospects` mantengono le proprie schede. L'appendice Commander resta separata dai pool Limited.

`cards.json` conserva in `cards[].prospects` la ricerca su tutte le 295 identità del catalogo (280 carte non base FRA, cinque identità di terre base e dieci Special Guests). Il campo aggiuntivo è compatibile con lo schema 1 e viene mantenuto dal caricatore esistente. `schemas/prospects.schema.json` ne descrive il contratto. `prospectsDate` non modifica la data del catalogo, i voti Limited o la revisione dei replay.

Ogni scheda distingue analisi editoriale del testo Oracle, legalità per formato, risultati di torneo, inclusioni Commander, recensioni Limited e scenari di prezzo. Lo stato `non_documentata` segnala una lacuna del campione, non una bocciatura. cEDH usa la legalità Commander ma conserva un giudizio distinto. Draft, Sealed e Pick-Two restano eventi separati: una recensione Draft non diventa una statistica degli altri eventi. Le Special Guests conservano le proprie legalità e non acquisiscono quelle del set ospitante.

`sources.json.research` registra 15 editori o servizi distinti, incluso Cardmarket: Wizards/Magic.gg, Scryfall, Postboard, EDHREC, MTGGoldfish, MTGDECKS, Cards Realm, MTG Arena Zone, Draftsim, PauperPilot, EchoMTG, DeckCortex, EDHTop16 e Duel Commander Meta. URL, data, hash degli input e limiti sono conservati. Lo snapshot Postboard comprende 3.313 liste in cinque formati; le schede estratte coprono 66 identità e 104 combinazioni carta/formato. Le apparizioni isolate non pubblicate non vengono inventate. EDHREC misura liste pubblicate, non partite vinte o vendite. I conteggi storici MTGDECKS comprendono edizioni precedenti e non sono adozione della sola ristampa FRA. Il campione cEDH DeckCortex resta datato 2-11 ottobre, con possibili duplicati; EDHTop16 conferma separatamente il risultato di Dack. Duel Commander Meta è una fonte beta e l'elenco delle carte popolari non è una misura di rendimento.

I valori economici correnti usano esclusivamente Cardmarket, letto direttamente nel browser il 22 ottobre: 387 prodotti (290 stampe base, 87 identità Commander e dieci Special Guests), che coprono tutte le 382 identità analizzate. `price.from` è il minimo richiesto per il prodotto, con `finishFilter: any`, senza filtri lingua, condizione o paese del venditore e senza spedizione. Non equivale al ricavo realizzato. `nonfoil` e `foil` sono valorizzati solo dopo verifica del filtro Cardmarket N/Y: sei non foil e una foil; gli altri sono null, mai sostituiti con Scryfall. La lettura sistematica delle schede è stata fermata dalla verifica di sicurezza Cardmarket. Le schede prodotto lette successivamente prevalgono sul listino per il medesimo prodotto/filtro; le osservazioni restano separate negli snapshot.

Il confronto al 18 ottobre usa esclusivamente i 48 minimi Cardmarket base esatti conservati nello snapshot storico, con `comparison.from`; non confronta il minimo con Price Trend, medie o prezzi Scryfall. I valori a 0,10 euro o meno del vecchio snapshot non erano conservati esattamente: restano mancanti, non zeri. Gli scenari a 3 e 12 mesi sono ricalcolati sul nuovo minimo e sul confronto disponibile, con confidenza bassa e senza target o probabilità inventate. Dove disponibili, Price Trend e medie hanno etichette e filtro distinti; il confronto tra medie di finestre sovrapposte non è una previsione. `prices.json.references` dichiara questa copertura parziale; il flag principale del modello economico e il valore atteso storico del box restano invariati, perché mancano prezzi verificati per tutte le finiture e varianti della collazione.

L'aggiornamento porta il registro a 15 editori/servizi, incluso Cardmarket come unica autorità dei prezzi; Scryfall resta fonte Oracle e legalità, EchoMTG resta storico. `capture_cardmarket_snapshot_20261022.py` normalizza la trascrizione dei listini, verificandola contro i checksum delle righe DOM complete. `refresh_cardmarket_prospects_20261022.py` applica la politica Cardmarket e viene richiamato come ultimo passaggio da `update_fra_prospects_20261022.py`, anche nelle rigenerazioni successive. Gli snapshot precedenti sono conservati.

`prospects-commander-20261022.json` contiene un'appendice separata per le 87 identità FRC rilevate (103 stampe), pubblicata come asset esplicito del set. Queste carte non entrano nei pool Limited. `research/reality-fracture-20261022/` conserva snapshot API, osservazioni numeriche normalizzate, valutazioni editoriali e audit. I testi integrali delle pagine consultate restano nella cache temporanea configurabile con `MTG_RESEARCH_CACHE`. `research_fra_prospects_20261022.py` raccoglie gli input online; `extract_fra_prospects_20261022.py` estrae i riscontri; `update_fra_prospects_20261022.py` aggiorna i documenti offline; `verify_fra_prospects_20261022.py` verifica copertura, corrispondenze e conservazione dei dati funzionali. Nessuno viene eseguito dalla build.

## Aggiornare e verificare l'analisi economica di un box

Una richiesta sui prezzi serve a valutare il costo del prodotto e il possibile ricavo delle singole. Prima di usare un risultato storico, cercare gli snapshot più recenti e leggerne osservazioni, fonti, date e copertura. Un aggiornamento delle analisi per carta non aggiorna automaticamente il valore atteso del box.

1. Identificare prodotto e numero di buste, lingua, costo comprensivo della spedizione e soglia di vendita. Usare la collazione documentata del prodotto, mantenendo distinte regole ufficiali e ipotesi del modello.
2. Rilevare su Cardmarket le stampe pertinenti e registrare metrica e filtri. `From` senza filtri lingua, condizione e finitura è un minimo di prodotto; non certifica il prezzo inglese NM non foil. Se il lettore web fallisce, verificare l'accesso dal browser e dichiarare le lacune residue.
3. Verificare la copertura di base, varianti ammesse, foil e carte ospiti, escludendo i trattamenti di altri prodotti. Conservare valori mancanti distinti dagli zeri e dalle carte escluse dalla soglia. Per una stima usare soltanto prezzi pertinenti o ipotesi dichiarate.
4. Ricalcolare lordo, commissioni verificate, netto e differenza dal costo. Dichiarare l'ipotesi di vendita di tutte le carte sopra soglia e i costi esclusi. Gli intervalli del modello storico misurano la sensibilità del valore atteso alle probabilità, non il risultato garantito di un box.
5. Confrontare gli snapshot a parità di fonte, metrica e modello; quantificare separatamente eventuali sostituzioni della fonte. Spiegare variazioni sorprendenti con carte e versioni concrete. I riferimenti Scryfall degli esperimenti storici non diventano minimi Cardmarket né aggiornano automaticamente le schede del sito.
6. Conservare acquisizioni e risultati datati, con gli input necessari a riprodurre il calcolo. Dichiarare separatamente cosa è stato acquisito, ricalcolato, integrato nel sito e pubblicato. I file privati `ev-*` sono esclusi da Git dalla configurazione attuale.

Le richieste sullo stato del push richiedono un controllo aggiornato di modifiche tracciate, file non tracciati o ignorati e commit rispetto al remoto dopo `git fetch`. Non autorizzano commit o push. La pubblicazione del sito va verificata sul workflow relativo al commit; il semplice allineamento di `main` e `origin/main` non ne conferma l'esito.

## Navigazione e layout

La veste comune usa caratteri di sistema, pannelli coerenti, accessi per obiettivo e microanimazioni CSS brevi, senza dipendenze aggiuntive. Le animazioni rispettano `prefers-reduced-motion`; i contenuti editoriali rimangono visibili anche senza JavaScript. Le tabelle nelle aree scorrevoli sono raggiungibili da tastiera. Nel tavolo Draft le colonne mantengono la stessa larghezza mentre diminuiscono le carte, le immagini riservano lo spazio prima del caricamento e i pulsanti di scelta sono allineati. La barra di avanzamento rappresenta le 42 pick, senza cambiare motore o salvataggi.

Con il server locale sulla porta 8765, `node verify-ux.cjs` controlla le 19 pagine a 320, 360, 768, 1024 e 1440 pixel, le dimensioni del draft per tutta la prima busta, ripresa della sessione, movimento ridotto e contenuti statici senza JavaScript. Salva anche anteprime desktop e mobile. Usa `MTG_PLAYWRIGHT_MODULE`, `MTG_BROWSER_CHANNEL` e `MTG_SITE_URL` per configurare l'ambiente, come gli altri controlli browser.

Verifica hosting del 22 ottobre 2026: il sito rimane statico e usa il workflow GitHub Actions esistente. La build locale produce circa 12,6 MB in meno di 10 secondi nell'ambiente di verifica. I [limiti ufficiali di GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) prevedono 1 GB per il sito pubblicato, timeout del deploy dopo 10 minuti e una soglia indicativa di traffico di 100 GB al mese. La soglia di 10 build all'ora non si applica ai workflow Actions personalizzati. Il traffico effettivo e le impostazioni dell'account non sono deducibili dalla build locale. Il sito informativo non introduce checkout, transazioni sensibili o un servizio commerciale SaaS.

Riferimenti UX: [animazioni efficienti con transform e opacity](https://web.dev/articles/animations-guide), [preferenza di movimento ridotto](https://www.w3.org/WAI/WCAG22/Techniques/css/C39), [dimensione e spaziatura dei controlli](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html). Le scelte privilegiano transizioni brevi, feedback delle azioni, immagini stabili e controlli principali da almeno 44 pixel sul telefono. Questi interventi non costituiscono una certificazione completa WCAG.

### Tavolo Draft con bot

La voce “Tavolo Draft con bot” apre `Reality-Fracture-Draft-Engine.html` nel set Reality Fracture. Offre sette avversari configurabili prima del draft, nove strategie, tre giri di buste con passaggio simultaneo, anteprime accessibili, ripresa locale e revisione delle scelte dei bot alla fine. Il codice del draft, la configurazione e le pick permettono la riproduzione deterministica. L'esportazione JSON contiene le pick umane e, solo a draft concluso, il resoconto degli avversari.

`draft-engine.js` contiene collazione, stato dei bot, transizioni condizionali e politica di scelta; non usa DOM, rete o salvataggi. `draft-table.js` gestisce l'interfaccia. `build_draft_engine.py` è un ingresso di compatibilità: il renderer comune integra valutazioni e archetipi dai documenti dell’espansione. Lo snapshot storico `draft-format-fra-20261021.json` conserva stampe pubbliche Scryfall del 18 ottobre, coppie garantite, ricetta degli slot, pesi e ipotesi. La build non legge snapshot privati `ev-*` per questo strumento. Per un nuovo formato occorrono catalogo completo, valutazioni, archetipi e un profilo di collazione verificato; Star Trek rimane disabilitato fino al completamento dei dati. Gli input attivi sono `products.json`, `limited.json` e `printings.json` dell’espansione. Il motore legge gruppi e ricetta dal profilo, senza percentuali FRA nel codice.

Le probabilità pubblicate come inferiori all'1% sono ripartite in parti uguali entro il residuo del rispettivo slot. La coppia echoed viene estratta insieme, con rarità e trattamento comuni, poi viene estratta una terza echoed distinta. Queste correlazioni e l'equiprobabilità entro i gruppi sono ipotesi esplicite, non una ricostruzione dei fogli di stampa. Le buste sono indipendenti e includono tutte le 14 carte, terre comprese; i token sono esclusi.

Ogni bot osserva soltanto le buste ricevute. Lo stato comprende pool, fase, bomba iniziale, archetipo corrente, segnali distinti per giro, carte passate e domanda di colori dedotta dalle carte scomparse al ritorno. Il modello usa transizioni tra esplorazione, orientamento, consolidamento e completamento, condizionate da progresso, sostegno all'archetipo e cambi di piano. La politica valuta potenza, compatibilità dei colori, supporti dell'archetipo, curva, interazione, segnali e fonti per splash. Le sinergie sono valutate tramite gli archetipi editoriali: il motore non esegue una ricerca generale delle combo. Il counterpick è un profilo sperimentale, attivo tardi con alternative proprie deboli e richiesta di colore dedotta. Il modello non è addestrato su risultati di partite e non stima percentuali di vittoria.

I nuovi tavoli usano la politica dei bot `engineVersion: 3`. Le coppie con sostegno equivalente restano aperte: l'ordine degli archetipi nei JSON non assegna bonus iniziali a bianco-blu. I bonus tattici complessivi (curva, sinergia, segnali e mana) sono limitati a +0,45 e le penalità a -0,20; la preferenza dei colori resta separata. La scelta probabilistica considera soltanto alternative entro 0,20 punti dal punteggio migliore. Questi limiti sono parametri editoriali del modello, non probabilità ricavate da partite. I costi ibridi vengono considerati nella compatibilità dei colori, le creature con X non sono contate come normali giocate iniziali e le copie della stessa carta non moltiplicano i supporti di sinergia. I voti delle carte restano quelli documentati in `ratings.json`, senza convertirli automaticamente dalle percentuali GIH.

La versione dell'algoritmo è distinta dall'impronta dei dati: i record precedenti (`engineVersion: 2` e i salvataggi storici ammessi) continuano con la politica originaria, anche dopo la ripresa e una nuova esportazione. `node verify-draft-bots.cjs` confronta questi replay con risultati congelati prima della correzione e verifica le scelte problematiche. `node audit-draft-bots.cjs 200 reality-fracture draft mixed 3` simula 200 tavoli e salva il rapporto in `reviews/draft-bots-20261022/`; l'ultimo argomento può essere `2` per confrontare il vecchio algoritmo con gli stessi semi e lo stesso giocatore simulato. `node verify-draft-bots-browser.cjs` controlla ripresa, completamento, esportazione e anteprime usando `MTG_SITE_URL`, `MTG_PLAYWRIGHT_MODULE` e `MTG_BROWSER_CHANNEL`.

Dopo `python build_site.py`, eseguire `node verify-draft-engine.cjs`: controlla 30.000 buste, coppie e slot, frequenze campionarie, conservazione di tutte le 336 carte del tavolo, entrambi i versi di passaggio, replay identico, configurazioni invalide e differenze tra strategie. Le anteprime e i controlli si verificano anche nel browser locale.

La homepage propone accessi per obiettivo; `set-template.html` è la panoramica di Reality Fracture. `site_navigation.py`, `site.css` e `site.js` applicano a tutte le pagine il menu organizzato per attività, il percorso di navigazione e il menu mobile accessibile da tastiera. Gli strumenti si aprono come pagine complete, senza iframe. I vecchi link alla panoramica con `#draft`, `#discovery` e gli altri identificatori degli strumenti continuano a funzionare. I salvataggi esistenti mantengono le stesse chiavi e la stessa origine.

Con il server locale avviato, `node verify-site.cjs` verifica le otto pagine a 360, 768 e 1440 pixel, menu mobile, navigazione, filtri, pool, anteprime e vecchi collegamenti. Richiede Playwright e Chrome; i percorsi si possono configurare con `MTG_PLAYWRIGHT_MODULE`, `MTG_BROWSER_CHANNEL` e `MTG_SITE_URL`.

Progetto indipendente. Magic: The Gathering, le immagini e i testi delle carte appartengono ai rispettivi titolari. I collegamenti alle fonti sono inclusi nelle sezioni del sito.
