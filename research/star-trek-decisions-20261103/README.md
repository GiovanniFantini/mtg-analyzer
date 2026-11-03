# Star Trek: valutazioni e piani di gioco

Approfondimento del 3 novembre 2026 su dodici identità TRK, a partire dalla ricerca del 2 novembre. È il primo blocco campione: le altre 329 identità conservano le analisi precedenti. La copertura delle identità del catalogo resta 341/341; non viene dichiarata una profondità equivalente per tutte le schede.

## Contenuti e accesso

[assessments.json](assessments.json) conserva conclusione, contesto, piano, supporti, sequenza con costi, alternative, rischi e criterio per rivedere il giudizio. Il campione comprende Salt Vampire, Holo-Engineer, Wesley Crusher, Genesis Device, McCoy, Scotty, Seven of Nine (UB), The Traveler, Deanna Troi, Borg Cube, Dal R'El e Boarding Action.

La pagina Analisi mostra l'indice dei dodici approfondimenti. I collegamenti selezionano la carta nel catalogo; aprendola si legge subito la valutazione, prima dei dettagli su formati e prezzi. Le nuove motivazioni sono cercabili nel catalogo. Anche Constructed, scegliendo tutte le analisi e aprendo i dettagli della carta, presenta l'approfondimento. I pareri originali hanno collegamenti diretti. Tutti i riferimenti del campione riguardano carte già disponibili per le anteprime.

Le sequenze sono analisi editoriali dei testi, con condizioni iniziali esplicite. Non sono liste competitive già provate. Esempi che attraversano più colori dichiarano il costo della base di mana; non implicano che lo splash sia consigliato. Non sono stati aggiunti voti di forza o praticità al catalogo delle combo per renderlo artificialmente disponibile.

## Provenienza e conservazione

[source-audit.json](source-audit.json) registra le riletture delle release notes Wizards, della recensione Cube di Usman/Kai e della recensione Standard di Cards Realm, con URL, data, dimensione e hash delle risposte. Le opinioni riportate restano attribuite ai contesti originari; i ragionamenti di gioco aggiunti sono giudizi editoriali propri. Non viene dichiarata una nuova raccolta estesa di recensori o una classifica di affidabilità degli autori. Gli articoli integrali non vengono distribuiti.

Le osservazioni normalizzate e i pareri precedenti sono in [ricerca del set](../star-trek-20261102/README.md) e [ricerca sugli autori](../star-trek-authors-20261102/README.md). Prezzi Cardmarket, date dei prezzi, testi Oracle, legalità, voti, indici di torneo, WR e identità delle carte restano invariati. La data dell'approfondimento è separata da quelle delle altre osservazioni.

## Riproduzione offline

```sh
python integrate_editorial_decisions.py --expansion expansions/star-trek --input research/star-trek-decisions-20261103/assessments.json
node test-editorial-decisions.cjs
python -m unittest test_editorial_decisions.py test_star_trek_research.py test_expansion_data.py
python build_site.py
```

Per i controlli browser servire `dist/` e configurare `MTG_SITE_URL`, `MTG_PLAYWRIGHT_MODULE`, `MTG_BROWSER_CHANNEL` e `MTG_QA_DIR` come in [verification.md](../../docs/verification.md), poi eseguire `node verify-editorial-decisions.cjs`. Il controllo attraversa tutte le dodici schede a 1440 e 390 px, verifica indice, collegamenti, fonti, consultazione Constructed, assenza di duplicazione e anteprime da mouse, tastiera e tocco.

Esiti effettivi in [verification.json](verification.json). Il confronto con il catalogo Git precedente conferma che il solo nuovo campo delle carte è `prospects.decisionReview`; la seconda importazione è identica byte per byte. Nessuna modifica alla pipeline. Build e controlli precedono il commit; la pubblicazione viene verificata separatamente sul workflow del commit.
