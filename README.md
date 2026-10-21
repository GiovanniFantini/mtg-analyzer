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

## Espansioni

`expansions.json` alimenta la homepage. Ogni set ha un URL sotto `sets/<slug>/`. Per aggiungerne uno, creare prima i relativi contenuti e builder, estendere la selezione degli asset in `build_site.py`, poi registrarlo nel catalogo. I collegamenti Draft e discovery sono configurabili per set. Le pagine storiche di Reality Fracture mantengono i propri adattatori; le nuove espansioni possono usare `expansion_shell` con percorsi e gruppi propri.

### Star Trek

`build_star_trek.py` genera dieci pagine sotto `sets/star-trek/`: panoramica, catalogo, Draft, pool Sealed, prova del mazzo, sinergie, analisi, Constructed, regole e fonti. Gli input versionati sono `star-trek-cards-20261021.json` (163 carte distinte, 321 stampe TRK/SDS) e `star-trek-format-20261021.json` (collazione ufficiale). La build è offline e non legge gli snapshot privati `ev-*`.

Il catalogo è incompleto e i prezzi non sono disponibili. Non viene simulata l'apertura delle buste né calcolato un ricavo atteso. La prova del mazzo mescola soltanto le carte selezionate dall'utente e implementa il London mulligan per il Limited uno contro uno. I controlli del mazzo verificano quantità e minimo di 40 carte, senza certificare l'idoneità delle carte al prodotto dell'evento.

I pool sono distinti per Sealed, Draft e Pick-Two, con chiavi `mtg-trk-<modalità>-v1`. Le osservate usano `mtg-trk-watch-v1`. Non vengono lette o modificate le chiavi di Reality Fracture. L'importazione JSON controlla versione, set, modalità, identità delle carte e quantità prima di sostituire lo stato.

Le modifiche rileggono il salvataggio aggiornato; Web Locks, quando disponibili, serializzano le scritture dello stesso pool fra schede. Gli eventi `storage` e `pageshow` aggiornano le pagine già aperte. Un salvataggio non leggibile viene conservato e non sovrascritto. La modalità scelta segue i collegamenti fra catalogo, costruzione, Draft e simulatore.

`node verify-star-trek-review.cjs` verifica le regressioni segnalate dalla review: aggiornamenti fra schede e simultanei, focus dei comandi e delle terre, mulligan da tastiera, modalità nei collegamenti, protezione dei dati non validi, chiusura delle anteprime fuori schermo, salvataggi FRA e memoria temporanea quando la scrittura nel browser fallisce.

Per aggiornare i dati, conservare gli input datati e creare nuovi snapshot con provenienza e data; aggiornare i riferimenti e le date del builder e degli strumenti, verificare la collazione e le regole ufficiali prima di abilitare nuove stime. Il campo Scryfall `booster` non viene usato da solo per decidere l'idoneità durante l'anteprima.

Con il server di `dist/` sulla porta 8871, `node verify-star-trek.cjs` controlla le dieci pagine a 360, 768 e 1440 pixel, navigazione, anteprime, separazione pool, quantità, import/export, mulligan e compatibilità del catalogo FRA. Il percorso Playwright e il browser si configurano con `MTG_PLAYWRIGHT_MODULE` e `MTG_BROWSER_CHANNEL`; `MTG_SITE_URL` cambia l'URL del server.

I contenuti editoriali, le finestre statistiche e le fonti hanno date esplicite. Le classificazioni della discovery sono valutazioni editoriali e non previsioni di prezzo o probabilità di vittoria.

Pool e carte osservate sono memorizzati nel browser del visitatore, senza account o sincronizzazione. Il passaggio dal file locale al sito HTTPS non trasferisce automaticamente questi salvataggi: per il pool usare le funzioni di esportazione e importazione.

## Navigazione e layout

### Tavolo Draft con bot

La voce “Tavolo Draft con bot” apre `Reality-Fracture-Draft-Engine.html` nel set Reality Fracture. Offre sette avversari configurabili prima del draft, nove strategie, tre giri di buste con passaggio simultaneo, anteprime accessibili, ripresa locale e revisione delle scelte dei bot alla fine. Il codice del draft, la configurazione e le pick permettono la riproduzione deterministica. L'esportazione JSON contiene le pick umane e, solo a draft concluso, il resoconto degli avversari.

`draft-engine.js` contiene collazione, stato dei bot, transizioni condizionali e politica di scelta; non usa DOM, rete o salvataggi. `draft-table.js` gestisce l'interfaccia. `build_draft_engine.py` integra valutazioni e archetipi esistenti. `draft-format-fra-20261021.json` conserva stampe pubbliche Scryfall del 18 ottobre, coppie garantite, ricetta degli slot, pesi e ipotesi. La build non legge snapshot privati `ev-*` per questo strumento. Per un nuovo formato occorrono catalogo completo, valutazioni, archetipi e un profilo di collazione verificato; Star Trek rimane disabilitato fino al completamento dei dati. Il motore legge gruppi e ricetta dal profilo, senza percentuali FRA nel codice.

Le probabilità pubblicate come inferiori all'1% sono ripartite in parti uguali entro il residuo del rispettivo slot. La coppia echoed viene estratta insieme, con rarità e trattamento comuni, poi viene estratta una terza echoed distinta. Queste correlazioni e l'equiprobabilità entro i gruppi sono ipotesi esplicite, non una ricostruzione dei fogli di stampa. Le buste sono indipendenti e includono tutte le 14 carte, terre comprese; i token sono esclusi.

Ogni bot osserva soltanto le buste ricevute. Lo stato comprende pool, fase, bomba iniziale, archetipo corrente, segnali distinti per giro, carte passate e domanda di colori dedotta dalle carte scomparse al ritorno. Il modello usa transizioni tra esplorazione, orientamento, consolidamento e completamento, condizionate da progresso, sostegno all'archetipo e cambi di piano. La politica valuta potenza, compatibilità dei colori, supporti dell'archetipo, curva, interazione, segnali e fonti per splash. Le sinergie sono valutate tramite gli archetipi editoriali: il motore non esegue una ricerca generale delle combo. Il counterpick è un profilo sperimentale, attivo tardi con alternative proprie deboli e richiesta di colore dedotta. Il modello non è addestrato su risultati di partite e non stima percentuali di vittoria.

Dopo `python build_site.py`, eseguire `node verify-draft-engine.cjs`: controlla 30.000 buste, coppie e slot, frequenze campionarie, conservazione di tutte le 336 carte del tavolo, entrambi i versi di passaggio, replay identico, configurazioni invalide e differenze tra strategie. Le anteprime e i controlli si verificano anche nel browser locale.

La homepage propone accessi per obiettivo; `set-template.html` è la panoramica di Reality Fracture. `site_navigation.py`, `site.css` e `site.js` applicano a tutte le pagine il menu organizzato per attività, il percorso di navigazione e il menu mobile accessibile da tastiera. Gli strumenti si aprono come pagine complete, senza iframe. I vecchi link alla panoramica con `#draft`, `#discovery` e gli altri identificatori degli strumenti continuano a funzionare. I salvataggi esistenti mantengono le stesse chiavi e la stessa origine.

Con il server locale avviato, `node verify-site.cjs` verifica le otto pagine a 360, 768 e 1440 pixel, menu mobile, navigazione, filtri, pool, anteprime e vecchi collegamenti. Richiede Playwright e Chrome; i percorsi si possono configurare con `MTG_PLAYWRIGHT_MODULE`, `MTG_BROWSER_CHANNEL` e `MTG_SITE_URL`.

Progetto indipendente. Magic: The Gathering, le immagini e i testi delle carte appartengono ai rispettivi titolari. I collegamenti alle fonti sono inclusi nelle sezioni del sito.
