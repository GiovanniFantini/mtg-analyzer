# MTG Analyzer

Sito statico in italiano dedicato alle espansioni di Magic: The Gathering. Il primo set disponibile è Reality Fracture, con catalogo, pool personale, guida Draft, analisi Sealed, combo, simulatore e discovery del metagame.

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

`expansions.json` alimenta la homepage. Ogni set ha un URL sotto `sets/<slug>/`. Per aggiungerne uno, creare prima i relativi contenuti e builder, estendere la selezione degli asset in `build_site.py`, poi registrarlo nel catalogo. I template attuali sono specifici di Reality Fracture.

I contenuti editoriali, le finestre statistiche e le fonti hanno date esplicite. Le classificazioni della discovery sono valutazioni editoriali e non previsioni di prezzo o probabilità di vittoria.

Pool e carte osservate sono memorizzati nel browser del visitatore, senza account o sincronizzazione. Il passaggio dal file locale al sito HTTPS non trasferisce automaticamente questi salvataggi: per il pool usare le funzioni di esportazione e importazione.

Progetto indipendente. Magic: The Gathering, le immagini e i testi delle carte appartengono ai rispettivi titolari. I collegamenti alle fonti sono inclusi nelle sezioni del sito.
