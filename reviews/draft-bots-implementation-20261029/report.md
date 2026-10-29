# Implementazione dei requisiti Draft BOT, 29 ottobre 2026

Politica v4 implementata nel motore condiviso e selezionabile come opzione sperimentale. V3 rimane predefinita; i replay storici continuano con la propria politica. Nessun commit, push o modifica alla pipeline.

## Comportamento implementato

- Profili minimi offline per stampa attiva, separati dai voti. La disponibilità richiede copertura completa dei dati minimi e un tavolo realmente disponibile.
- Main provvisorio e finale costruito dalle carte possedute e dalle basi ammesse dall'evento. Refill dopo le esclusioni; le carte scartate non continuano a fornire mana, curva o supporti.
- Confronto dei piani sul valore assoluto del main, con bisogni funzionali e mana. Solo gli slot ancora vuoti ricevono una stima di riempimento futuro, basata su dati pubblici, ruolo, colore e pick restanti.
- Splash con basi aggiungibili, landcycling tipizzato o base, fetch, facce terra e produttori accessibili. Gli usi alternativi occupano un solo slot; la carta non fornisce il mana per lanciare se stessa. Le stime sono approssimate e dichiarate.
- Relazioni causali con sostegno di riferimento, rendimenti, opzioni e risorse contese, subordinate alla copertura completa di carte e piani.
- Memoria separata per verso di passaggio, qualità/profondità attesa e wheel. Nessun accesso ai pool avversari o alle buste future. Nessun costo affondato per le pick spese.
- Preferenze dei profili, curve aggro e controllo, riserve BO3 e costo opportunità della negazione. BO1 e contesto sconosciuto non ricevono valore di sideboarding.
- Flussi casuali separati per posto e decisione nella nuova versione; collazione storica preservata. Scelte congiunte limitate per Pick-Two e modalità deterministica tramite API.
- Revisione finale con main, fonti, alternative, migliore stimata, sorteggio, busta, pool precedente, sostituzioni e lacune. Anteprime mouse, tastiera e tocco; log avversari disponibili soltanto a draft concluso.
- Record v4 con opzioni e impronte di dati, algoritmo e schema casuale. Backup integrale dei record incompatibili prima della sostituzione; se fallisce, l'originale resta intatto.

## Copertura dei requisiti

| Requisiti | Implementazione e limiti |
| --- | --- |
| BOT-01 | `bot_profiles.py`, schema facoltativo, validazione e manifest per carta/piano. Descrittori Oracle conservativi, non un interprete completo. |
| BOT-02, BOT-03 | Costruttore, refill, attese per gli slot vuoti, main assoluto e delta coerente tra piani. Il costruttore è euristico, non esaustivo. |
| BOT-04 | Modello di fonti e pagamento, alternativa per copia, fonti raggiungibili, target reali per cycling/fetch e configurazioni con basi di splash. Nessuna simulazione dei mulligan o delle partite. |
| BOT-05 | Motore causale verificato su fixture; componente disattivata uniformemente dove i riferimenti e le relazioni sono incompleti. |
| BOT-06, BOT-07 | Memoria per lato, confidenza, wheel, piani alternativi e pivot. Frequenze marginali della ricetta approssimate per le sole attese. |
| BOT-08, BOT-09 | Ruoli, costi ridotti prudenti, preferenze aggro/controllo/fixing/bomba e controllo di pura potenza. Adattivo rimane configurazione interna di riferimento, senza decimo profilo esposto. |
| BOT-10 | Riserve dipendenti dal match e negazione subordinata ai miglioramenti propri. Non viene inventato un destinatario certo della carta negata. |
| BOT-11, BOT-14 | Nuova versione isolata, impronte, replay e flussi separati; fixture storiche congelate prima delle modifiche. |
| BOT-12 | Revisione dinamica completa e verifiche browser desktop/tocco/tastiera. |
| BOT-13 | Semi di taratura e riservati separati, stessi dati e buste, conservazione, costruttore diagnostico comune e input anonimi per Opus. Esiti e denominatori nella sezione di confronto finale. |

## Review indipendente

Richieste, hash degli input, risposte grezze e JSON normalizzati sono conservati in questa cartella. Le review sono eseguite tramite Claude CLI, con modello effettivo `claude-opus-5-5`, senza strumenti e senza persistenza della sessione. Non sono risposte simulate da Codex.

Il primo round ha individuato nove difetti confermati: refill, doppi simboli del colore principale, riduzioni, terre solo incolori, fetch, auto-supporto della carta, costi compositi, impronta della collazione e fase in Pick-Two. Il secondo ne ha individuati sette: obiettivo assoluto dei piani, delta con segnali coerenti, rimozioni rosse/verdi, valore del riempitivo finale, splash con basi, ordine dei candidati e tipo artefatto funzionale. Il terzo ne ha individuati quattro: costo distinto dal turno di splash, modalità solo fixing anche in colore, facce terra con restrizioni e main finale scelto senza segnali. Le risoluzioni sono in [code-decisions.json](code-decisions.json); le regressioni riproducibili sono in [verify-draft-policy-regressions.cjs](../../verify-draft-policy-regressions.cjs) e [test_bot_profiles.py](../../test_bot_profiles.py).

Il quarto round ha aggiunto valore delle opzioni di piano, fetch con basi possedute, esclusione delle terre tappate dominate e spiegazioni separate dei pivot. Il quinto ha rilevato il doppio credito di un piano già diventato migliore: il termine di opzione ora lo esclude. Il sesto ha corretto i falsi pivot dovuti alla sola sideboard, il campo pivot nelle scelte congiunte e il costo opportunità del corpo usato come fixing. Le fixture speculari e le risposte originarie restano conservate. In totale 28 rilievi confermati corretti prima della valutazione riservata.

## Verifiche e confronto finale

Implementazione e verifiche funzionali concluse. Il settimo ricontrollo mirato di Opus ha restituito zero rilievi; gli hash dei sorgenti esaminati coincidono con quelli finali. Motore storico, collazione, caricatore e schema non erano cambiati dalle review complete precedenti.

Controlli passati:

- `python build_site.py`: 21 espansioni, 290 pagine HTML, collegamenti locali verificati e build offline.
- 42 test Python fra `test_expansion_data.py` e `test_bot_profiles.py`.
- Compatibilità storica, 30.000 buste nel controllo del motore, verifiche delle espansioni e del contratto di collazione. Esiti e output in [checks.json](checks.json).
- Fixture v4 e regressioni dei 28 rilievi: costi, fonti, alternativa per copia, main, pivot, opzioni, BO1/BO3, Pick-Two, casualità e replay.
- Browser v4 e storico: ripresa parziale e completa, export, privacy in corso, mouse, tastiera, tocco, 390 px, backup integrale e backup fallito. [Esiti](browser-checks.json).
- Diciannove fixture JSON isolate e controlli di disponibilità, salvataggi Sealed e pagine con funzionalità mancanti. [Esiti](supplemental-checks.json).
- Lista finale espansa verificata su desktop e telefono, comprese basi e carte solo fixing. [Desktop](browser/policy-v4-main-desktop.png), [telefono](browser/policy-v4-main-mobile.png).

I fallimenti intermedi non sono stati cancellati: una fixture di pivot pretendeva di abbandonare otto giocabili W davanti a cinque U; ora conserva quel caso come stabilità e verifica il pivot sulle carte effettivamente incluse nel main. Un controllo aveva letto `dist` durante la sua rigenerazione ed è stato rieseguito a build conclusa. Vedere `checks-before-fixture-correction.json`, `checks-before-pivot-observation.json` e `checks-dist-build-race.json`.

### Acquisizione riservata

Il candidato è rimasto fermo durante la valutazione. [Manifest dei sorgenti](source-manifest.json), [ambiente](environment.json), [risultati completi](reserved-0aaee222bc/results.json), [riepilogo](reserved-0aaee222bc/summary.json) e [validazione finale](final-validation.json). La cartella conserva formato completo, fixture, sorgenti della politica e del banco di prova, record e impronte delle singole buste.

Revisione funzionale storica: `b8507e3f2b0065d879d9c570c3f321bd5c8ad90f64097d8b72967de38cf88bab`. Revisione dei descrittori: `bcc1af08ef04818fe09b73262840d94b5137c73e22d65f7c66f1dfecc816ea4d`. Impronta combinata del codice acquisito: `0aaee222bc47e58a72048f883667c77183c56ea08a0226127b268aea0ec275a4`.

Sono stati completati 15 tavoli, 105 mazzi dei bot e 4.410 pick dei bot. Tutti i main hanno 40 carte, nessun UID ripetuto, soltanto carte del pool e basi ammesse, nessuno slot magia scoperto e nessun errore di mana impossibile secondo il modello. Ogni replay coincide con il digest originario dei bot. Le impronte delle buste iniziali coincidono nei confronti appaiati.

| Scenario | V3 | V4 | Mazzi diagnosticati |
| --- | --- | --- | --- |
| Misto, quattro semi e posti ruotati | 4 tavoli | 4 tavoli | 28 per versione |
| Omogeneo Lettura dei segnali | 1 tavolo | 1 tavolo | 7 per versione |
| Omogeneo Adattivo interno, stessa collazione | 0 | 1 tavolo | 7 |
| Misto con Adattivo interno, quattro semi | 0 | 4 tavoli | 28 |

Il giocatore umano usa sempre il valutatore v2, seme separato e identificativo reale della busta osservata. Il diagnostico finale è `finalBuild` neutrale e identico per tutti i pool, inclusi quelli v3. Il misto con Adattivo cambia la composizione dei profili: è esplorativo e non isola l'effetto causale di un solo posto. Non si confrontano come gruppi equivalenti i 35 mazzi v3 e i 70 v4.

Gli indicatori `early` e `interaction` sono classificazioni del modello. `early` conta creature dal costo stimato fino a tre, senza applicare il ritardo dello splash o una probabilità di lancio: non dimostra giocate iniziali affidabili. Le carte solo fixing sono escluse da quei conteggi nella valutazione riservata. La correzione del solo conteggio diagnostico, precedente all'acquisizione riservata, è registrata nel manifest e non cambia le decisioni.

### Prestazioni

Ambiente: Windows x64, Node 24.20.0, Python 3.15.0, Edge per il browser, Ryzen 9 8940HX esposto con quattro processori logici. Desktop condiviso, senza riserva esclusiva della macchina.

| Misura | V3 | V4 |
| --- | --- | --- |
| Mediana del tempo completo per tavolo | 2,39 s | 134,63 s |
| Intervallo dei p95 per mossa del tavolo | da 0,014 a 0,019 s | da 3,34 a 4,81 s |

Il tempo completo comprende draft, replay e diagnostico. La mossa misura l'avanzamento del tavolo con i sette bot, senza il tempo di lettura del giocatore. Sono osservazioni su questo campione e ambiente, non una garanzia su altri dispositivi. La v4 ha un costo interattivo sensibile; ripresa e revisione ricostruiscono il draft. Il candidato non viene promosso per la sola riuscita dei test.

### Valutazione cieca

Opus ha ricevuto 15 mazzi anonimizzati e 15 pick, in due richieste indipendenti senza persistenza. Il giudice delle pick non ha visto le liste finali; nessuno dei due ha ricevuto la mappa fra campione e politica. Catalogo, costi, statistiche stampate e Oracle erano forniti. Le pick sono tutte B2 P7, con pool precedente e busta, senza sequenza completa delle buste precedenti o profilo stilistico.

[Giudizio sui mazzi](blind-review-decks-1.review.json), [giudizio sulle pick](blind-review-picks-1.review.json), [decisioni di lettura](blind-adjudication.json). Entrambe le risposte dichiarano insufficiente l'evidenza per la promozione.

Nelle pick la preferenza di Opus coincide con 2/5 scelte v3 e 6/10 scelte v4; per la v4 ci sono inoltre tre preferenze diverse e un caso incerto. Sono accordi con un giudizio, non percentuali di accuratezza. Per esempio considera coerente Skilled Battlecarver in RG per la curva; preferisce Sphinx's Approach a una seconda Yargle nel campione omogeneo v4, pur riconoscendo il bisogno di creature. Le due prese di terre criticate più nettamente appartengono alla v3; la lettura del secondo caso è troppo categorica, perché il pool contiene già Cruel Calculations blu. Non vengono trasformate in un tasso di errore certo.

Sui mazzi il limite ricorrente è il mana: colori principali poco serviti, splash discutibili e curva talvolta alta. Per esempio il campione `sample-54d07d96` ha dieci carte che richiedono R e cinque fonti rosse fisse; `sample-c35e8337` presenta solo cinque Forest con molte carte G. Sono criticità del costruttore diagnostico condiviso, quindi non possono essere attribuite automaticamente alla sola politica che ha draftato il pool. Fonti indirette e costi ridotti vanno comunque considerati; non tutte le critiche ai duplicati leggendari implicano un taglio corretto.

La valutazione riservata non è stata usata per ritoccare pesi o scelte del candidato. Un'ulteriore taratura di mana, tempo dello splash e gestione delle copie richiederà nuovi casi riservati o una dichiarazione esplicita di riuso. Non è attestata competenza competitiva generale: la v4 resta opt-in sperimentale e Adattivo resta interno al banco di prova.

## Limiti e decisione di disponibilità

Reality Fracture è l'evento Draft realmente disponibile nel catalogo corrente. La copertura minima è 411/411 stampe attive. Gli altri set non vengono abilitati per allargare il benchmark. I profili minimi del set sono inferiti dai dati locali; i voti e la collazione restano quelli originari.

Le annotazioni causali complete e il contesto editoriale dei voti non sono disponibili per tutte le carte e tutti i piani di Reality Fracture. La componente di sinergia resta quindi spenta nell'intero evento, per tutti i profili aggiornati, con lacuna visibile. Le fixture provano il supporto del motore, senza attestare una ricerca per carta già completata.

Le misure del costruttore diagnostico condividono codice e obiettivo con il candidato: indicano coerenza interna, non forza indipendente. Non sono state simulate partite e non viene dichiarata una WR. Il campione limitato di un solo evento e i dati causali mancanti non giustificano una promozione a bot competitivo generale o un cambio del default.
