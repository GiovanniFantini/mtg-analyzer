# Star Trek: conoscenza e confronto con Reality Fracture

Ricerca del 2 novembre 2026. Aggiornamento locale dei dati e delle guide del sito.
Il riferimento di accuratezza è Reality Fracture; copertura delle informazioni e
quantità delle prove disponibili vengono confrontate separatamente. Una ricerca
estesa non certifica di avere esaurito ogni contenuto pubblicato sul web.

## Dati integrati

- 341 identità: tutte le TRK 1-311 e SDS 1-30. Sono 76 identità in più rispetto
  al catalogo del 28 ottobre. Le 611 stampe acquisite non certificano tutti i
  trattamenti, le finiture o l'idoneità di ciascuna stampa ai Play Booster.
- Analisi editoriale specifica di tutte le 341 identità, con testo Oracle,
  costi, condizioni, rischi e ruoli. Le analisi precedenti verificate sono
  conservate; quelle generiche sono state sostituite. Le note non sono risultati
  di gioco e non attribuiscono successo agonistico.
- 306 voti Draft: tutte le TRK non base, nessuna SDS. Un autore, J2SJosh,
  sette articoli MTG Arena Zone pubblicati dal 30 ottobre al 2 novembre.
  Scala originale 0-5, senza media, conversione da WR o attribuzione ai bot.
  Le 284 voci originali includono tre valutazioni di cicli di terre, espanse
  solo sulle 25 carte espressamente identificate. Associazioni e gruppi sono
  in [limited-reviews.json](limited-reviews.json).
- 306 previsioni automatiche Constructed MTG-Standard, acquisite integralmente
  e distinte dalle recensioni Draft. Nessuna corrispondenza irrisolta.
- Osservazioni qualitative attribuite Standard, Pauper, Pioneer, Modern,
  Legacy e Commander in [format-observations.json](format-observations.json).
  I contesti meno documentati mantengono evidenza insufficiente, senza
  trasformare una previsione in un risultato.
- Guida Sealed, priorità ragionate, sei situazioni di scelta e dieci pacchetti
  Draft, uno per coppia. Sono scenari editoriali verificati sui testi, senza
  inventare tassi di vittoria. Le carte citate hanno anteprime nel sito.
- [Appendice Commander](commander-appendix.json): 336 identità e 556 stampe
  TRC, acquisite da tutte le pagine Scryfall disponibili. Contiene catalogo,
  legalità e i piani dei quattro precon, separati da TRK/SDS e dai pool Limited.
  Non è una recensione individuale completa delle 336 carte né uno studio cEDH.

Il confronto completo è in [catalog-delta.json](catalog-delta.json).
Vengeance Mission conserva l'identità e il nome precedente
"Assault on Area 51". Le correzioni di trascrizione documentate il 28 ottobre
sono conservate dove ancora necessarie; nessuna errata è inventata dal sito.

## Fonti effettive e attendibilità

[source-audit.json](source-audit.json) registra acquisizioni HTTP, dimensioni,
hash e destinazioni. [source-assessments.json](source-assessments.json) distingue
lettura pertinente, estrazione di voti, pagina non analitica, redirect, shell
vuota e accesso bloccato. Quindici editori o servizi hanno fornito contenuti
pertinenti letti o dati effettivamente estratti: Wizards, Scryfall, MTG Arena
Zone, Cards Realm, MTG Rocks, Draftsim, EDHREC, Card Kingdom, MTGGoldfish,
CollectorUnion, Deathmarked, MTG-Standard, MTGMeta, myLimitedGrades e PreconForge.
Il numero non significa quindici recensioni indipendenti per ciascuna carta.
Le guide NerdSnack e TurnZero sono state considerate separatamente, con
correzioni e limiti; la graduatoria dei colori non è stata importata come fatto.

I riferimenti ufficiali principali sono le [release notes del 30 ottobre](https://magic.wizards.com/en/news/feature/star-trek-release-notes),
le [meccaniche](https://magic.wizards.com/en/news/feature/star-trek-mechanics),
il [prodotto](https://magic.wizards.com/en/news/feature/collecting-star-trek)
e le [liste Commander](https://magic.wizards.com/en/news/announcements/star-trek-commander-decklists).
Le valutazioni qualitative nuove includono [Standard di Romeu](https://mtg.cardsrealm.com/en-us/articles/standard-star-trek-review-for-the-format),
[Pauper di Romeu](https://mtg.cardsrealm.com/en-us/articles/pauper-star-trek-set-review)
e la [selezione di Riley Hicks](https://mtgrocks.com/mtg-star-trek-best-cards/).
Ogni voto rimanda alla propria recensione, autore e data nel file normalizzato.

Contraddizioni conservate e decisioni:

- Il calendario anteprime indica il 30 ottobre per la galleria completa,
  Collecting continua a riportare il 30 novembre. La copertura del catalogo è
  verificata sui numeri e sulle identità, senza dedurla da una di queste date.
- Collecting presenta indicazioni non coerenti su Away Team foil nei Play.
  Le percentuali inferiori all'1% e i dubbi sugli slot restano aperti.
- Le release notes hanno una sezione con titolo Seven of Nine e testo della
  diversa Seven of Nine, Unassimilated. Il catalogo conserva separatamente le
  due identità Oracle. La data interna del documento precede quella di pubblicazione.
- La selezione MTG Rocks usa anche nomi inesatti: Genesis Engine e Jadzia Dax,
  Living Legend sono ricondotti solo alle carte verificate Genesis Device e
  Jadzia Dax, Living Legacy. Le previsioni di adozione restano attribuite.
- Hit It! non è mill. I Tesori normali non riducono Borg Cube. New Planet
  ripetute alimentano landfall ma non aumentano i nomi diversi. Boarding Action
  e le pedine delle Duras Sisters non impongono sacrifici a fine turno.

## Distanza residua da FRA

| Area | Disponibile adesso | Dato mancante e fonte | Limite e prossima acquisizione utile |
| --- | --- | --- | --- |
| Identità TRK/SDS e analisi | 341/341 con note specifiche | Eventuali errata e aggiornamenti Oracle, Wizards/Scryfall | Nuovi testi richiedono confronto datato, non sostituzione cieca dei profili |
| Voti Draft | 306/306 TRK non base, un autore | Voti SDS e confronto con altri recensori | La copertura completa di un autore non equivale al consenso di FRA |
| WR Draft | N/D | Snapshot 17Lands o Untapped con evento, periodo e campioni | Arena inizia il 10 novembre; pagine e modelli attuali non sono partite osservate |
| WR Sealed | N/D | Campione Sealed distinto con identità e denominatori | Non trasferire statistiche Draft al Sealed |
| Guide e sinergie | Sealed, dieci coppie, dieci pacchetti e sei decisioni | Conferma dalle partite | Le sequenze sono verificate meccanicamente, la forza relativa non è misurata |
| Standard/Pioneer/Modern/Pauper | Legalità e prospettive separate; indici per ogni carta | Liste ufficiali dopo l'uscita per le nuove carte | Il corpus conservato termina il 28 ottobre; non è stato ridatato al 2 novembre |
| Legacy/Vintage | Legalità e scenari, senza nuovo indice completo | Review e liste post-uscita pertinenti | Non basta un commento Standard per dimostrare adozione in questi formati |
| Commander | Catalogo TRC separato, piani dei quattro precon e osservazioni storiche | Recensioni individuali complete, inclusioni aggiornate e risultati cEDH/Duel | Il catalogo TRC non è già una valutazione completa dei quattro mazzi |
| Prezzi | 201 riferimenti Cardmarket From del 27 ottobre | Nuova lettura Cardmarket, finiture e varianti | 403 anche in browser; nessuna fonte economica sostitutiva o ridatazione |
| Buste, bot e box | Dati ufficiali del prodotto e limiti | Stampe ammesse, pesi risolti e collazione eseguibile | Nessuna ricetta inventata; niente apertura fedele o EV certificato |

Le catture browser [Draft](17lands-draft-browser.json) e
[Sealed](17lands-sealed-browser.json) mostrano caricamento senza righe, non un
dataset scaricato. [Cardmarket](cardmarket-browser.json) conferma il blocco 403.
Untapped restituisce una pagina di errore. MTGMeta dichiara valori predetti e
nessuna partita registrata; myLimitedGrades dichiara benchmark ancora assenti.

## Riproduzione e verifiche

L'integrazione offline legge gli snapshot nel repository:

```sh
python enrich_star_trek_20261102.py
python build_site.py
python -m unittest test_star_trek_research.py test_expansion_data.py
```

`baseline-cards.json.gz` conserva integralmente il catalogo attivo precedente,
comprese osservazioni e prezzi, per impedire l'eredità di dati da un'altra
carta. Gli snapshot più vecchi non sono riscritti. Il controllo di ripetizione
è in [import-repeat-check.json](import-repeat-check.json).

L'acquisizione esplicita dalla rete è separata: `research_star_trek_20261102.py`,
poi `enrich_star_trek_20261102.py --extract`. Gli HTML rimangono nella cache
temporanea, non nel repository; gli hash non consentono di ricostruire una pagina
storica. Le osservazioni normalizzate conservate permettono invece di ripetere
l'integrazione offline. Non si aggirano blocchi, login o paywall.

Gli esiti finali dei controlli sono registrati in [verification.json](verification.json).
Nessuna modifica alla pipeline, nessun commit o push per questa attività.
