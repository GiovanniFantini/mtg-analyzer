# Integrazione simulatori Star Trek, 9 novembre 2026

Il catalogo conteneva 341 identità ma non le stampe utilizzabili dal motore, una ricetta di apertura o voti numerici per i bot. Questa integrazione abilita Draft a otto, Pick-Two a quattro e Sealed da sei buste attraverso i motori condivisi. Non modifica le loro politiche decisionali.

## Fonti e perimetro

- Scryfall: snapshot completo di quattro pagine, 616 stampe TRK e SDS, in `printings-source.json`. Le identità canoniche e il testo corretto del catalogo rimangono stabili. Il modello seleziona 460 stampe di queste 616, attraverso 24 gruppi.
- [Draftmancer, sorgente fissato al commit](https://github.com/Senryoku/Draftmancer/blob/f2aeb566634b22fed933b8bcc8e196e414f9c1b5/src/BoosterFactory.ts): adattamento dei pesi e dei gruppi del suo `TRKBoosterFactory` in otto operazioni dichiarative già supportate. Estratto e licenza MIT conservati accanto al modello. Le buste sono indipendenti, senza bilanciamento colori.
- [Draftsim, pick order](https://draftsim.com/TRK-pick-order/): 341 righe della tabella del simulatore, scala originale 0–5. I 336 voti non base sono importati senza trasformazione. Le cinque terre base mantengono voto assente; il valore sorgente -1 resta solo nello snapshot. Provenienza e hash del bundle e del TSV in `bot-ratings.json`. È una fonte distinta dalla recensione Andrew Quinn, che usa un'altra scala. I voti dei bot sono identificati separatamente nel dettaglio carta.
- [Wizards, Collecting Star Trek](https://magic.wizards.com/en/news/feature/collecting-star-trek): composizione pubblicata e date. Prerelease dal 6 novembre, Arena dal 10, uscita nei negozi il 13. Lo stato diventa `prerelease` senza anticipare l'uscita commerciale.
- MTGJSON TRK aggiornato all'8 novembre: ancora `isPartialPreview: true`, senza ricetta booster. Non è stato usato come fonte di una collazione inesistente.

## Limiti del modello

È un modello di allenamento di terzi, con frequenze stimate dove Wizards pubblica solo un limite inferiore all'1%. Il residuo è distribuito dal modello sorgente fra i rami non specificati: wildcard 2,3/11, rare 0,8/5, foil 3,1/11 punti percentuali. Le probabilità ufficiali originarie rimangono separate nei dati `published`.

Non è una replica integrale del generatore Draftmancer. La sua [funzione pickCard](https://github.com/Senryoku/Draftmancer/blob/f2aeb566634b22fed933b8bcc8e196e414f9c1b5/src/cardUtils.ts) protegge dai duplicati di stampa attraverso gli slot e consuma un pool di copie. Il contratto condiviso qui conserva invece unicità per identità dentro i comuni base e i tre non comuni, permettendo ripetizioni negli altri slot. Ordine di estrazione e protezione dai duplicati sono diversi; i pesi delle famiglie rimangono quelli della fonte. Questa differenza è dichiarata nelle assunzioni pubbliche e nell'avviso del simulatore.

Lo slot terra normalizza il totale arrotondato 100,2 e applica il 20% foil come la fonte. Il modello include Away Team foil come la lista ufficiale degli slot, che contraddice il paragrafo generale sul trattamento. Queste assunzioni rimangono esplicite nel prodotto e l'avviso è visibile sopra entrambi i simulatori. Le aperture non certificano fogli di stampa, correlazioni fra buste o valore economico di un box.

Le WR early access restano escluse dagli indici ordinari e dai bot. Recensioni, proiezioni Constructed, giudizi Draft/Sealed e ruoli strategici già acquisiti restano distinti dai nuovi voti del motore. Questa integrazione non costituisce approvazione finale di Opus o nuova misurazione del metagame.

## Compatibilità e riproduzione

Chiavi storage e identità canoniche restano invariate. Il nuovo profilo funzionale ha una revisione diversa dal precedente profilo vuoto: non si dichiara compatibilità di replay fra collazioni diverse. I vecchi record incompatibili seguono il recupero condiviso con backup completo verificato prima della sostituzione. `functional-audit.json` registra le revisioni.

La risoluzione dei vecchi collegamenti preserva gli URL già assegnati nel manifest: `simulatore.html` continua ad aprire la prova del mazzo, mentre il simulatore di buste usa `sealed-simulator.html`. Una regressione dedicata protegge questa distinzione anche quando il nome del percorso coincide con un alias storico.

Importazione offline dagli snapshot, senza rete durante la build:

```sh
python research/star-trek-integration-20261109/prepare-model.py
python integrate_star_trek_simulators.py
python build_site.py
python -m unittest test_star_trek_simulators.py
```

`verify-simulation.cjs` usa fixture generate dai due eventi e poste nella cartella indicata da `MTG_SIM_QA_DIR` (`draft.json`, `picktwo.json`). Verifica 10.000 buste e sei draft completi, versioni motore 2, 3 e 4: 42 carte per giocatore, conservazione di tutte le carte, replay e rifiuto di revisione alterata. Nel campione deterministico: Stardates 4,11%, foil medi 1,2018, terra doppia 49,77%. Sono controlli di conformità al modello, non percentuali osservate in buste reali.

`verify-browser.cjs` richiede `MTG_SITE_URL`, `MTG_PLAYWRIGHT_MODULE`, `MTG_BROWSER_CHANNEL` e una nuova `MTG_QA_DIR`; verifica i tre eventi, export, ripresa e anteprime mouse, tastiera e tocco. I rapporti, screenshot e salvataggi di prova sono conservati in `docs/local/qa/`, senza sostituire evidenze storiche.
