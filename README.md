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

Per aggiornare i dati, conservare gli input datati e creare nuovi snapshot con provenienza e data; aggiornare i riferimenti e le date del builder e degli strumenti, verificare la collazione e le regole ufficiali prima di abilitare nuove stime. Il campo Scryfall `booster` non viene usato da solo per decidere l'idoneità durante l'anteprima.

Con il server di `dist/` sulla porta 8871, `node verify-star-trek.cjs` controlla le dieci pagine a 360, 768 e 1440 pixel, navigazione, anteprime, separazione pool, quantità, import/export, mulligan e compatibilità del catalogo FRA. Il percorso Playwright e il browser si configurano con `MTG_PLAYWRIGHT_MODULE` e `MTG_BROWSER_CHANNEL`; `MTG_SITE_URL` cambia l'URL del server.

I contenuti editoriali, le finestre statistiche e le fonti hanno date esplicite. Le classificazioni della discovery sono valutazioni editoriali e non previsioni di prezzo o probabilità di vittoria.

Pool e carte osservate sono memorizzati nel browser del visitatore, senza account o sincronizzazione. Il passaggio dal file locale al sito HTTPS non trasferisce automaticamente questi salvataggi: per il pool usare le funzioni di esportazione e importazione.

## Navigazione e layout

La homepage propone accessi per obiettivo; `set-template.html` è la panoramica di Reality Fracture. `site_navigation.py`, `site.css` e `site.js` applicano a tutte le pagine il menu organizzato per attività, il percorso di navigazione e il menu mobile accessibile da tastiera. Gli strumenti si aprono come pagine complete, senza iframe. I vecchi link alla panoramica con `#draft`, `#discovery` e gli altri identificatori degli strumenti continuano a funzionare. I salvataggi esistenti mantengono le stesse chiavi e la stessa origine.

Con il server locale avviato, `node verify-site.cjs` verifica le otto pagine a 360, 768 e 1440 pixel, menu mobile, navigazione, filtri, pool, anteprime e vecchi collegamenti. Richiede Playwright e Chrome; i percorsi si possono configurare con `MTG_PLAYWRIGHT_MODULE`, `MTG_BROWSER_CHANNEL` e `MTG_SITE_URL`.

Progetto indipendente. Magic: The Gathering, le immagini e i testi delle carte appartengono ai rispettivi titolari. I collegamenti alle fonti sono inclusi nelle sezioni del sito.
