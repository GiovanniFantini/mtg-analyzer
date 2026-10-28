# Architettura e contratto delle espansioni

Contratto tecnico del sito statico. Leggere questo documento quando si modificano manifest, documenti JSON, renderer, collazione o salvataggi. Per i controlli usare [verification.md](verification.md); per le statistiche esterne usare [statistics.md](statistics.md).

## Documenti, renderer e presentazioni

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

Tutte le espansioni registrate usano la presentazione Atlas e i template condivisi sotto `templates/atlas/`. I template `preview` restano compatibilità per profili e fixture precedenti. Il manifest sceglie i template per pagina; la copertura dei dati abilita i singoli strumenti senza cambiare l’interfaccia. Aggiungere un’espansione richiede documenti JSON e una voce nel registro, senza un nuovo builder o una nuova interfaccia di gestione. Gli asset pubblici aggiuntivi sono elencati esplicitamente nel manifest; gli snapshot storici alla radice restano conservati. I controlli comuni sono in `catalog-controls.js`; `catalog-indices.js` gestisce gli indici WR Draft/Sealed e le prospettive Standard/Pioneer/Modern/Pauper. `catalog_metrics.py` espone gli snapshot per fonte ed evento, senza mediarli. Lo stile è in `catalog-controls.css` e il contratto è in [statistics.md](statistics.md).

I token `fragment:chiave` richiedono la stessa chiave in `guides.fragments`; `source:chiave` richiede un URL grezzo in `sources.links`. Chiavi mancanti fermano la build con documento e chiave da completare. `optionalFragment` e i frammenti `draft.report-N` possono essere omessi. Le guide strutturate, comprese le situazioni di scelta, non richiedono i frammenti del report. `sources.downloads` dichiara i download opzionali con `url` e `label`, e i relativi file vanno inclusi negli asset. Il catalogo e le statistiche conservano date separate (`ratings.date`, `statistics.catalogDate`, `statistics.draft.date`).

`ui.json` contiene esempi dei bot, alias, etichette dei set, esempi di importazione, preset di analisi ed eventuale ordine `discoveryLevels`. I formati della discovery derivano dalle carte. Un preset di analisi con un valore assente nei filtri non viene mostrato. I calcolatori delle combo sono opzionali: `calculator.kind: netMana`, `netPerCycle`, `unit`, `label` e `note` descrivono un guadagno fisso per ciclo senza codice eseguibile nei dati.

Il catalogo usa `ratings.cards.<id>.community` per filtri e ordinamento delle recensioni esterne; `score` resta il voto usato dagli strumenti Limited. Quando viene esposta una singola recensione, `communitySource` ne identifica l’URL in `evidence` e `communityMethod` descrive la selezione, senza implicare una media fra editori. Il catalogo mostra autore e voto originale di quella fonte accanto al valore normalizzato. Carte prive di una recensione numerica conservano il valore assente.

I template Atlas non richiedono fonti o frammenti di Reality Fracture per attivare uno strumento. Le note editoriali sono opzionali e i renderer delle guide hanno template condivisi predefiniti. Per fonti proprie, `sources.groups` contiene liste di oggetti `url` e `label`, con il nome della sezione (`draft-engine`, `pick-guide-section`, `gallery` e gli altri nomi dei template). La guida Sealed conserva il contenuto HTML in `guides.fragments.gallery.strategy`: se manca, la sezione indica esattamente questa proprietà da completare. I dati strutturati Draft restano disponibili anche senza i frammenti del report.

Un salvataggio Draft incompatibile viene conservato integralmente in una chiave separata prima della prima scrittura del nuovo draft. Se il backup fallisce, il salvataggio originale non viene sovrascritto. Il messaggio permette di scaricare il record precedente, anche dopo la riapertura del nuovo salvataggio.

La disponibilità del tavolo viene verificata per ogni evento Draft e per il suo prodotto; il selettore elenca soltanto eventi pronti e spiega cosa manca agli altri. Le statistiche per carta e il drilldown per contesto sono indipendenti: il secondo richiede anche `statistics.draft.drill.contexts` e `retrieved`.

I contratti di `cards.json` e `printings.json` sono descritti anche in `schemas/cards.schema.json` e `schemas/printings.schema.json`. Ogni carta richiede identità, nome, set, numero, colori, identità di colore, tipo, rarità, immagine, URL e dati di mana/testo. Le stampe del motore non richiedono un URL separato. Il caricatore accetta `cost`/`mana`, `mv`/`cmc` e `oracle`/`text`, mantenendo coerenti i due nomi; i campi aggiuntivi restano conservati. `full` usa il nome se omesso; facce, stampe, keyword e legalità mancanti hanno contenitori vuoti. I flag di carta base, terra e creatura si ricavano dal tipo della faccia principale se assenti. Gli errori dei campi essenziali indicano documento e carta. I documenti pubblicati contengono la forma normalizzata.

Le rinomine digitali documentate possono usare i nomi e i testi stampati per la visualizzazione, anche su entrambe le facce. `oracleName` e `canonicalOracleText` conservano l’identità e il testo di riferimento; il collegamento fra prodotti viene verificato tramite `oracle_id`, senza dedurre l’equivalenza soltanto dai nomi. L’importatore applica questa trasformazione solo quando richiesta esplicitamente.

La homepage deriva percorsi e nomi dal registro. `home.featured` e `home.quickTools` nel manifest scelgono rispettivamente il set in evidenza e gli accessi rapidi; in assenza di indicazioni usa l’ultima e la prima espansione registrata. Il catalogo completo/parziale e la data della legalità derivano dai dati, anche nella presentazione di anteprima. I collegamenti locali alle sezioni assenti o non disponibili vengono omessi.

## Analisi per carta e prezzi

La selezione degli eventi predefiniti deriva dal loro `kind` e dalla disponibilità effettiva, senza imporre che la chiave del registro sia `draft` o `sealed`. Il runtime espone `defaultEvents` e `eventAvailability`; l'ID del profilo dentro l'evento resta distinto dalla sua chiave nel registro. La disponibilità di ogni funzione conserva `requested`, `dataReady`, `requirements` e le lacune leggibili anche quando non è richiesta.

Una presentazione di anteprima passa ai renderer condivisi per Draft, combo, discovery, analisi e simulazione quando i dati necessari diventano disponibili. La prova della mano iniziale resta in una pagina separata quando si attiva il simulatore Sealed. Le guide Sealed hanno una route condivisa anche per set privi del relativo contenuto. La panoramica mostra la matrice degli strumenti, con ciò che serve a completare quelli non disponibili.

Quando si attivano le viste condivise, il banco manuale Draft e la prova del mazzo mantengono route separate e i salvataggi precedenti. I frammenti editoriali della preview rimangono consultabili negli approfondimenti. Le chiavi opzionali dei pool condivisi sono isolate per espansione anche se non erano dichiarate nel manifest di anteprima.

Il [torneo locale](tournament.md) è uno strumento trasversale e non dipende dai dataset di espansione. Il suo JSON versionato è separato dai pool personali e dai replay dei bot.

Le analisi aggiuntive risiedono in `cards.json: cards[].prospects`; `prospectsDate` è una data di ricerca distinta da quella del catalogo, dai voti e dalla revisione funzionale dei replay. Il contratto è in `schemas/prospects.schema.json`, con campi aggiuntivi compatibili. `prospects-ui.js` è il renderer condiviso; l'assenza di `prospects` mantiene la scheda ordinaria.

L'oggetto distingue `date`, `kind`, `summary`, `gameplayReview`, `oracle`, `formats`, `tournamentObservations`, `commanderObservations`, `price`, `sources` e `limitations`. Una valutazione in `formats.<formato>` separa `legality`, `evidence`, `prospect` e `confidence`; l'eventuale indice `observation` rimanda alle osservazioni di torneo. I riferimenti di `sources` si risolvono nel registro `sources.json: research.sources`. Lo schema resta il riferimento per campi richiesti, tipi e valori ammessi. `formats.<formato>.tournamentIndex` conserva un indice misurato da liste di torneo, distinto dal giudizio editoriale e dalle previsioni. Calcolo e validazione sono in `tournament_index.py`; `competitive-prospects-ui.js` presenta score, campione, segnali e storico. Il metodo è documentato in [statistics.md](statistics.md).

La convenzione `evidence: non_documentata` segnala una lacuna delle prove disponibili, non un giudizio negativo sulla carta; il renderer la mostra come Dati insufficienti. Non confonderla con `prospect`, che conserva il giudizio editoriale, per esempio `da_verificare` quando manca una valutazione sostenuta dai dati. cEDH usa la legalità Commander ma conserva osservazioni e giudizi distinti. Le Special Guests e gli altri prodotti collegati mantengono le proprie condizioni di legalità, senza ereditare quelle dell'espansione ospitante.

In `prospects.price` conservare `date`, `currency`, `metric`, stampa e provenienza. `from` è il minimo di prodotto; `finishFilter` specifica `any`, `nonfoil` o `foil`. `nonfoil` e `foil` restano null finché non è verificato il relativo filtro: le letture dirette possono essere conservate in `finishReadings`, con URL e filtro Cardmarket N/Y. `marketMetrics` conserva Price Trend e medie con la propria finitura, separatamente dal minimo. `comparison.from`, `comparison.nonfoil`, `samePrinting` e `status` descrivono il confronto effettivamente possibile; `sameProduct` è un'estensione compatibile opzionale presente nelle osservazioni, non un campo obbligatorio dello schema. Non riempire un campo con una metrica diversa. Questo paragrafo spiega la semantica di alcune proprietà, senza sostituire l'elenco completo dei campi e dei vincoli dello schema, anche per `comparison`, `variants` e `outlook`. Per il metodo di acquisizione e confronto vedere [economics.md](economics.md).

`prices.json.references` descrive disponibilità, data, metrica, copertura e lacune dei riferimenti per carta. Non rende automaticamente pronto il modello economico principale né aggiorna il valore del box. Un'appendice Commander può essere un documento aggiuntivo dichiarato esplicitamente in `expansion.json: assets`: non confluisce nei pool Limited. Nomi e date dei file sono specifici dell'espansione, non convenzioni rigide del renderer.

## Regole delle buste e degli eventi

I documenti sono letti come oggetti JSON, attraverso un caricatore comune. Non serve un database: il sito resta statico e la build risolve i riferimenti, poi incorpora i dati necessari agli strumenti. I documenti pubblici si trovano anche sotto `sets/<slug>/data/`, compresi `runtime.json` e `availability.json`.

La collazione è una ricetta dichiarativa ordinata, eseguita da `collation.js` sia nel Draft sia nel Sealed. Le operazioni supportate sono:

- `draw`: estrae una o più carte da gruppi pesati. `unique` evita ripetizioni della stessa carta entro lo slot.
- `replace`: con probabilità `chance` sostituisce le prime carte estratte dallo slot `target`.
- `pair`: estrae una carta e il partner indicato in `partners`, con la stessa finitura.
- `exclude`: impedisce di estrarre carte con lo stesso nome completo di quelle già estratte dagli slot indicati. Per esempio, dopo una coppia garantita, uno slot aggiuntivo può escludere entrambi i nomi per evitare ripetizioni.

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

## Evoluzione e disponibilità

`schemaVersion: 1` identifica il contratto. Proprietà aggiuntive ed `extensions` consentono ampliamenti compatibili. Una modifica incompatibile richiede una nuova versione e un adattatore esplicito nel caricatore. Una nuova operazione di collazione o procedura di gioco richiede supporto nel motore; non viene eseguito codice JavaScript dal JSON. Versioni e operazioni sconosciute fanno fallire la validazione.

Gli schemi JSON in `schemas/` descrivono manifest, prodotti ed eventi per gli editor. La build usa controlli Python senza dipendenze esterne: verifica identità, campi delle carte, riferimenti, archetipi, esempi, gruppi, partner, pesi, numerosità attese e regole degli eventi. Controlla anche la capienza delle sostituzioni ed esegue percorsi deterministici della ricetta, forzando i rami con probabilità positiva, per individuare gruppi esauriti da estrazioni uniche ed esclusioni. Queste verifiche eseguono i vincoli effettivi senza imporre limiti prudenziali che scarterebbero collazioni valide con esclusioni correlate; non costituiscono una prova esaustiva di ogni possibile sequenza. Le chiavi dei salvataggi non possono essere condivise da espansioni diverse.

`features.<strumento>.requested` indica che vogliamo quello strumento. La disponibilità effettiva viene calcolata dalle dipendenze: dichiararlo richiesto non abilita dati mancanti. Le pagine mostrano lo strumento non disponibile e cosa manca, mantenendo utilizzabili gli strumenti già pronti. Per i template Atlas sono protetti gli strumenti che richiedono collazione; nella pagina Draft le sole sezioni statistiche indicano i dati mancanti, mentre guide e pool restano utilizzabili. Le chiavi di salvataggio richieste dai controller sono validate prima della build. Scegliere un template esistente diverso richiede soltanto una modifica al manifest.

Le sessioni Draft nuove salvano la versione del motore e un’impronta dei soli dati che guidano le scelte: procedura dell’evento, collazione, identità e proprietà funzionali delle stampe, voti e appartenenza agli archetipi. Immagini, fonti e testi informativi non invalidano il replay. Le revisioni precedenti verificate sono collegate alla stessa impronta funzionale; una modifica al gioco disabilita automaticamente quelle compatibilità. Una sessione riferita a dati diversi viene rifiutata, preservando il salvataggio. La compatibilità storica deve essere verificata per il profilo dell'espansione interessata, senza estenderla automaticamente ad altri profili. I pool e le buste Sealed già estratte mantengono le identità precedenti e le stesse chiavi locali.

## Navigazione e collegamenti esistenti

Gli strumenti restano pagine complete. Preservare i vecchi collegamenti alla panoramica, compresi i frammenti storici come `#draft` e `#discovery`, tramite le route e gli adattatori pertinenti. Un riordino della navigazione non deve ripristinare i vecchi strumenti incorporati in iframe o interrompere questi accessi. `verify-site.cjs` copre la navigazione e i collegamenti storici della presentazione Atlas; le espansioni con route diverse richiedono controlli pertinenti ai propri manifest.

## Pool e importazione nella presentazione preview

Nella presentazione Atlas, l'assistente usa lo stesso pool della pagina Draft e la chiave `storage.draftPool`. Il record conserva `pool`, `mode`, `notes` e gli eventuali campi compatibili; `assistantPlan` è il piano di colori facoltativo scelto dall'utente e viene azzerato quando si svuota il pool. Le scritture rileggono il record corrente e, dove disponibili, usano Web Locks per serializzare modifiche da più schede. Pick, quantità, importazione, svuotamento e preferenze verificano il salvataggio prima di confermare l'esito. Record illeggibili o incompatibili restano protetti ed esportabili. L'annullamento verifica la firma delle sole quantità e viene ritirato quando le carte del pool cambiano; modifiche a piano, modalità o note non lo invalidano. `draft-advisor.js` valuta i dati Limited esistenti con euristiche esplicite; `draft-assistant.js` gestisce il flusso per telefono. I suggerimenti sulle comuni e il confronto non modificano la politica dei bot o i replay.

L'azione esplicita di recupero dei record protetti conserva prima il testo integrale in `storage.draftPool + ':protected-backups-v1'`, un documento con `version: 1` e `records` contenente `created` e `raw` per ogni archiviazione. Rilegge il backup prima di rimuovere il record principale; se l'archivio non è leggibile o la scrittura fallisce, il principale rimane intatto. I backup restano scaricabili anche dopo una nuova apertura della pagina. I nomi e i dati delle carte del pool Atlas derivano dal catalogo canonico, mentre le metriche e i campi compatibili dello snapshot statistico si conservano per corrispondenza di nome. Il confronto non deduce il mana prodotto dalle terre. Con un solo colore dedotto automaticamente, considera anche possibili secondi colori, senza dichiararli splash già sostenibili.

Se lo storage non è leggibile, Atlas conserva il pool disponibile in memoria e lavora solo nella pagina corrente, con avviso ed esportazione. Se viene rifiutata soltanto una scrittura, la modifica viene annullata e l'utente può attivare esplicitamente la modalità temporanea. Questa modalità non torna automaticamente alla persistenza anche se l'accesso riprende: non rilegge né sovrascrive eventuali record sul disco. Il testo suggerisce di scaricare il pool prima di chiudere o ricaricare. Un record presente e incompatibile rimane invece protetto e richiede il percorso di archiviazione, finché lo storage è accessibile.

Le chiavi derivano da `expansion.json: storage`, non dal nome del set nel controller condiviso. `star-trek.js` usa `poolPrefix` più modalità e suffisso di versione, una chiave `mode` e una chiave `watch`: il nome storico del file non limita la presentazione a Star Trek. Preservare le chiavi dichiarate quando cambia soltanto la presentazione.

Atlas mantiene questi record anche per i profili con `poolPrefix`: `poolSource` espone la chiave dell’evento e la struttura annidata. `pool-record.js` conserva `pool`, `deck`, `basics`, note e campi compatibili. Il catalogo usa gli ID originali; il banco Draft legge per nome mantenendo una mappa completa delle identità, comprese ristampe omonime di prodotti diversi. Le scritture conservano gli ID già presenti e riducono il mazzo soltanto quando si rimuovono intenzionalmente copie dal pool. Record non leggibili restano protetti e scaricabili. Le pagine Atlas `pool`, `workbench` e `practice` conservano il controllo manuale del mazzo e le mani iniziali; gli URL precedenti della prova del mazzo restano validi.

Prima di sostituire lo stato, l'importazione controlla versione, espansione, modalità, identità e quantità. Le modifiche rileggono lo stato aggiornato; Web Locks, se disponibili, serializzano le scritture dello stesso pool. Gli eventi `storage` e `pageshow` aggiornano le pagine aperte. Conservare questi comportamenti fra schede e la protezione dei salvataggi illeggibili. Quando la persistenza fallisce, mantenere esplicito il carattere temporaneo del lavoro e l'accesso all'esportazione. I controlli pertinenti sono elencati in [verification.md](verification.md).

Durante le anteprime il solo flag Scryfall `booster` non dimostra l'idoneità di una carta al prodotto. Verificare composizione e trattamenti con le fonti del prodotto prima di completare la collazione o abilitare stime.

## Lettura delle sinergie del pool

L'assistente Atlas espone `Come funziona il pool`, una lettura delle pick registrate e del piano colori corrente, distinta da una lista finale da 40 carte. Il payload `assistant.cards` conserva anche il testo `oracle` canonico. `draft-advisor.js: profile` riconosce alcuni pattern espliciti, escludendo i reminder fra parentesi; `poolAnalysis` collega fonti e beneficiari compatibili con il piano. Le osservazioni riguardano guadagno di vite, scry/surveil e condizioni legate alle abilità di lealtà. Modi diversi non vengono sommati come un unico effetto di rimozione e guadagno vite.

Le quantità contano separatamente carte che entrano preparate, carte che possono creare pedine creatura e carte con flashback. I gruppi possono sovrapporsi e non rappresentano creature già disponibili. Cicloterra base e produttori di mana di qualsiasi colore sono elencati anche fuori piano, con i loro vincoli; non equivalgono a fonti immediatamente utilizzabili. I simboli colorati fuori piano rispettano i costi ibridi e la faccia principale. Le terre e le forme di fixing non riconosciute richiedono una verifica manuale, senza dichiarare automaticamente sostenibile uno splash.

Il riconoscimento è parziale, non un interprete completo di Oracle: ogni collegamento offre le anteprime delle carte per controllare bersagli, costi e timing. Queste osservazioni non cambiano voti, win rate, priorità numeriche dei pick o politiche dei bot. Non importano risultati personali e ricordano di separare Quick, Premier e Traditional nei confronti. Anche il prompt esportato da `draft-pool.js` richiede di ricostruire sviluppo, stabilizzazione, risorse e chiusure, valutare ruoli simultanei e diversificazione delle bombe, distinguere risorse future e fixing e calibrare i giudizi sui risultati. Verifiche mirate: `node verify-pool-analysis.cjs`, `node verify-pool-analysis-browser.cjs` con le variabili browser descritte in [verification.md](verification.md), e `python -m unittest test_draft_assistant.py`.

## Aggiungere un'espansione

1. Creare `expansions/<slug>/` con il manifest e i documenti previsti dal contratto, quindi registrare il manifest in `expansions.json`.
2. Scegliere una presentazione condivisa e definire route, asset pubblici, contenuti e chiavi di salvataggio proprie. Usare gli schemi in `schemas/` insieme alla validazione effettiva di `expansion_data.py`.
3. Conservare esplicitamente copertura, provenienza e dati mancanti. Un prodotto incompleto mantiene `collation: null`; richiedere uno strumento non ne soddisfa le dipendenze.
4. Verificare build offline, isolamento e regressioni pertinenti secondo [verification.md](verification.md).

Nuovi dati non richiedono builder dedicati né condizioni sul nome del set nei motori condivisi. Nuove operazioni di gioco richiedono invece supporto esplicito nel motore. Non aggiungere un'interfaccia di amministrazione per aggiornare i JSON.
