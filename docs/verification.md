# Sviluppo, verifiche e pubblicazione

## Ambiente e build

Python 3.12 o successivo. La build usa la libreria standard e i soli file presenti nel repository. Node.js serve ai controlli JavaScript; Playwright e un browser compatibile servono ai controlli browser, non al sito pubblicato.

```sh
python build_site.py
python -m http.server 8765 --directory dist
```

La build rigenera `index.html`, prepara `dist/`, carica e valida le espansioni e controlla i collegamenti HTML locali. Non acquisisce prezzi, cataloghi o statistiche dalla rete. Modificare sorgenti e template, mai correggere a mano pagine generate o `dist/`.

## Scegliere i controlli

Applicare tutte le righe pertinenti alla modifica, senza ripetere controlli già passati in assenza di nuove ragioni. Una modifica soltanto documentale richiede collegamenti, riferimenti e diff; non richiede l'intera suite del sito.

| Area modificata | Controlli richiesti |
| --- | --- |
| Contratto, renderer, profili JSON | `python build_site.py`; `python -m unittest test_expansion_data.py` |
| Collazione, eventi, replay | Anche `node verify-expansions.cjs`; `node verify-draft-engine.cjs`; `python verify-collation-contract.py` |
| Disponibilità, isolamento, salvataggi | Anche `python verify-expansion-review.py`; `node verify-expansion-browser.cjs` |
| Politica dei bot | Anche `node verify-draft-engine.cjs` per conservazione di carte e buste; `node verify-draft-bots.cjs`; confronti riproducibili prima/dopo; `node verify-draft-bots-browser.cjs` per i flussi coinvolti |
| Interfaccia visibile | Controlli browser pertinenti; desktop, telefono, mouse, tastiera e tocco, comprese anteprime e contenuti dinamici |

I controlli del contratto comprendono fixture di espansioni alternative, buste e replay storici e Pick-Two. Non equivalgono a una prova esaustiva di tutte le collazioni possibili. La validazione corrente del caricatore e i test sono il riferimento eseguibile.

`verify-draft-engine.cjs` usa la fixture del tavolo Reality Fracture generata in `dist/`: controlla coppie e slot, frequenze campionarie, conservazione di carte e buste nel tavolo completo, entrambi i versi di passaggio, replay identico, input invalidi e differenze fra strategie. Il superamento di questa fixture non certifica automaticamente prodotti o eventi diversi: per quelli usare anche i controlli del contratto e delle espansioni pertinenti.

## Browser

Servire `dist/`, usare un profilo di prova e impostare esplicitamente le variabili previste dagli script. Per esempio in PowerShell, con Playwright già disponibile:

```powershell
$env:MTG_SITE_URL = 'http://127.0.0.1:8765/'
$env:MTG_PLAYWRIGHT_MODULE = (node -p "require.resolve('playwright')")
$env:MTG_BROWSER_CHANNEL = 'msedge'
node verify-expansion-browser.cjs
```

Se il modulo è in un runtime esterno, assegnare il suo percorso effettivo a `MTG_PLAYWRIGHT_MODULE`. Non introdurre percorsi personali fissi. Gli script hanno default di porta e modulo non uniformi: impostare le variabili evita di verificare un server diverso da quello voluto.

| Script | Ambito |
| --- | --- |
| `verify-atlas-expansions.cjs` (anche `verify-expansion-catalogs.cjs`) | Tutte le espansioni registrate: shell Atlas, route, salvataggi manuali, eventi alternativi, anteprime mouse/tastiera/tocco e layout desktop/telefono. Accetta slug opzionali e `MTG_QA_DIR` |
| `verify-catalog-indices.cjs` | Indici WR Draft/Sealed, fonti ed eventi, campioni minimi, prospettive Standard/Pioneer/Modern/Pauper e legalità per tutte le espansioni registrate, con conservazione dei salvataggi |
| `verify-tournament-prospects.cjs` | Tutti i cataloghi e metagame registrati: indici numerici per quattro formati, filtri, zero/N/D, campioni, segnali, analisi complete, fonti e anteprime mouse/tastiera/tocco |
| `verify-site.cjs` | Navigazione e strumenti Atlas, vecchi collegamenti |
| `verify-ux.cjs` | Layout delle route elencate nello script, più larghezze, movimento ridotto, Draft e contenuti senza JavaScript |
| `verify-expansion-browser.cjs` | Salvataggi e compatibilità fra espansioni |
| `verify-star-trek.cjs`, `verify-star-trek-review.cjs` | Preview, pool, import/export, mulligan, aggiornamento fra schede e regressioni |
| `verify-draft-bots-browser.cjs` | Ripresa, completamento, esportazione e anteprime dei bot |
| `verify-draft-assistant.cjs` | Confronto contestuale, costi ibridi e faccia principale, pick e annullamento, comuni, telefono, anteprime, sincronizzazione e salvataggi protetti |
| `verify-draft-workspace.cjs` | Quattro viste Draft, collegamenti diretti, cronologia, sei larghezze, tastiera, tocco, anteprime dinamiche e contenuti senza JavaScript. Screenshot e rapporto nella cartella temporanea, oppure in `MTG_QA_DIR` |
| `python -m unittest test_draft_assistant.py` | Coerenza del pool con il catalogo quando lo snapshot statistico è parziale o obsoleto, conservazione delle metriche presenti e assenza di win rate inventati |
| `verify-prospects-browser.cjs` | Consultazione delle analisi per carta; controllo datato con conteggi fissi e scrittura di screenshot, vedere sotto |

Ispezionare le route effettive negli script: conteggi storici di pagine o viewport non certificano espansioni aggiunte in seguito. Per ogni cambiamento visibile verificare le anteprime delle carte con hover, focus e tocco, anche nei risultati creati dopo il caricamento.

Prima di eseguire controlli datati, verificare anche le destinazioni dei rapporti e degli screenshot. `verify-prospects-browser.cjs` assume il catalogo della propria acquisizione e scrive quattro PNG in `research/reality-fracture-20261022/`, sovrascrivendo quelli omonimi se avviato dalla radice del repository. I percorsi degli screenshot sono relativi alla cartella di lavoro: per una verifica nuova avviare lo script tramite il suo percorso assoluto da una cartella temporanea, mantenendo `MTG_SITE_URL` e `MTG_PLAYWRIGHT_MODULE` configurati. Non sostituire le evidenze storiche e non ripristinare automaticamente file che potrebbero contenere lavoro di altre attività. Questo script non è una verifica generica della completezza di cataloghi successivi.

## Git e pubblicazione

Per il torneo locale usare `node test-tournament.cjs` e `node verify-tournament-browser.cjs`. Il secondo richiede `MTG_SITE_URL`, `MTG_PLAYWRIGHT_MODULE` e, se serve, `MTG_BROWSER_CHANNEL`: copre desktop e tocco, torneo completo, timer dopo ricaricamento, classifica, export/import, recupero di JSON incompatibili e backup fallito. `python -m unittest test_shared_features.py` verifica che dati pronti nelle presentazioni di anteprima raggiungano i renderer condivisi; `python audit-expansion-capabilities.py` stampa requisiti e lacune per tutti i set.

Il workflow `.github/workflows/` esegue build e pubblicazione di `dist/` a ogni push su `main` e su avvio manuale. Un errore di build impedisce il deploy. La build pubblica `schemas/`, le pagine e i dati runtime, i manifest e i dataset sotto `sets/<slug>/data/`. Inoltre copia in ciascun set ogni file `*.js` e `*.css` presente nella radice del repository, anche se non è dichiarato come asset. I JSON delle espansioni, gli schemi e questi file sono quindi pubblici, non un luogo per annotazioni private.

Un asset dichiarato nel manifest può essere un file oppure una directory: nel secondo caso la build ne copia ricorsivamente l'intero contenuto. Le directory di documentazione, skill, review e ricerca e i file privati `ev-*` non vengono copiati in blocco per il solo fatto di esistere, ma un riferimento negli asset li renderebbe pubblici. Controllare quindi percorsi e contenuti di `dist/` quando si aggiungono asset di tipo directory o file JavaScript/CSS in radice. La visibilità su Git è distinta dalla pubblicazione in `dist/`.

Una richiesta sullo stato Git non autorizza commit o push. Rileggere modifiche tracciate, file non tracciati, esclusioni rilevanti e commit locali; fare `git fetch` prima di dichiarare cosa manca sul remoto. Distinguere il lavoro corrente dalle modifiche di altre chat, verificare i file inclusi e le dipendenze locali non versionate prima di un push autorizzato. `ev-*` e `docs/local/` restano privati.

Per dichiarare il sito aggiornato verificare il workflow GitHub Pages del commit pertinente. Push riuscito, deploy riuscito e risorse online verificate sono esiti distinti. I limiti dell'hosting vanno ricontrollati sulle fonti ufficiali quando rilevanti; una misura locale non è una misura del traffico reale.

La migrazione Atlas è coperta anche da `python -m unittest test_atlas_migration.py` e `node test-pool-record.cjs`. Le fixture preview in `test_shared_features.py` e `verify-expansion-review.py` verificano la compatibilità storica; i vecchi script dedicati alla preview Star Trek non sono il controllo generale delle espansioni Atlas correnti.
