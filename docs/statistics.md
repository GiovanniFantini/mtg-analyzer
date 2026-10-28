# Statistiche esterne e osservazioni per carta

Il contratto si aggiunge ai documenti descritti in [architecture.md](architecture.md). Per acquisire o aggiornare le osservazioni usare la skill [mtg-research](../.agents/skills/mtg-research/SKILL.md).

## Snapshot Draft indipendenti

`statistics.draft.externalSources` aggiunge snapshot indipendenti per provider senza cambiare lo schema 1 o i dati 17Lands esistenti. `schemas/statistics.schema.json` descrive il contratto; `statistics_data.py`, richiamato dal caricatore comune, verifica identità del catalogo, duplicati, date, unità, intervalli e metriche bloccate. Ogni provider conserva `schemaVersion`, `provider`, `url`, `retrieved`, `filters`, `rateUnit: percent`, definizioni `metrics` e osservazioni `cards` collegate tramite `catalogId`. I valori numerici delle WR sono punti percentuali (70,8% diventa `70.8`); `null` indica un dato assente o bloccato. Le definizioni distinguono `public`, `locked` e `suspect`; i valori sospetti restano trascritti ma non sono idonei alle valutazioni. `display` conserva la precisione originale e `coverage` elenca le carte assenti. I conteggi arrotondati della fonte non diventano denominatori esatti delle WR. Campi ulteriori compatibili restano conservati. Questi snapshot sono disponibili nei JSON pubblici, senza modificare automaticamente viste, voti, baseline, eventi o revisioni dei replay.

## Significato e copertura

Conservare per ciascuna metrica definizione, unità, fonte, data, finestra temporale, evento, ranghi, filtri di archetipo e campione effettivamente pubblicati. WR in mano, nella mano iniziale, quando giocata e quando inclusa sono metriche distinte. La posizione media di offerta e i conteggi non condividono automaticamente il denominatore di una WR.

Associare le righe al `catalogId` stabile. Controllare l'intero catalogo pertinente, comprese le carte ospiti, distinguendo carte osservate, carte con una specifica metrica e carte assenti. Ristampe e varianti non diventano nuove identità di gioco. Valori assenti o bloccati restano `null`, anomalie e precisione originale si conservano.

Riutilizzare proprietà con lo stesso significato; aggiungere estensioni compatibili per informazioni diverse. Non mediare automaticamente servizi, popolazioni o eventi differenti e non trasformare una WR in un voto editoriale o in un peso dei bot. Il contratto Draft non si applica a Sealed o Pick-Two cambiandone soltanto l'etichetta.

## Importazione Untapped

Da una cattura datata delle celle pubbliche:

```sh
python import_untapped_statistics.py research/reality-fracture-20261022/untapped-card-data-dom.json --expansion expansions/reality-fracture --apply
```

Lo script conserva lo snapshot datato e l'hash dell'input, aggiornando soltanto `statistics.draft.externalSources.untapped` e `sources.externalStatistics.untapped`. La build non acquisisce dati online. Per un nuovo aggiornamento serve una nuova cattura pubblica, rispettando i limiti di accesso. Le condizioni specifiche della cattura del 22 ottobre sono nel [resoconto datato](history/2026-10-22.md).

## Pick order Untapped

I tier pubblici della pagina Pick Order hanno un'importazione distinta dalle metriche Card Data:

```sh
python import_untapped_pick_order.py research/reality-fracture-20261027/untapped-pick-order-dom.json --expansion expansions/reality-fracture --apply
```

La cattura conserva filtri, testo della pagina e gruppi di carte. L'importatore associa tutte le righe al catalogo, rifiuta duplicati e nomi sconosciuti e salva uno snapshot normalizzato con hash dell'input. Aggiorna soltanto `ratings.cards.<catalogId>.untappedPickOrder` e `sources.externalRankings.untappedPickOrder`, preservando gli altri dati. `tierOrder` è l'indice del tier nella scala pubblica, con S per primo; non è un voto numerico. Il gruppo Low Match Volume conserva `tier: null` e `status: low_match_volume`. Le carte assenti non ricevono dati stimati.

Nel catalogo, “Tier Draft Untapped” ordina per tier e poi alfabeticamente; le carte senza tier seguono quelle classificate. Ogni scheda acquisita mostra tier, fonte, data e contesto. Il parametro `?order=untapped` attiva direttamente questo ordinamento. La selezione avviene dal menu comune del catalogo, senza un pulsante aggiuntivo. La data delle recensioni, le stelle, i pesi dei bot, i dati 17Lands e le revisioni dei replay restano distinti. La build continua a usare soltanto file locali.


## Filtri e ordinamenti del catalogo

Il catalogo di ogni presentazione permette di ordinare per colore, valore di mana, tipo, recensioni, tier Draft e WR in mano Untapped, oltre agli ordinamenti editoriali già presenti. Per valore di mana, recensioni, tier e WR sono disponibili entrambi i versi; i dati mancanti seguono sempre quelli disponibili. I tier mantengono ordine alfabetico al loro interno.

I filtri per colore, rarità, tipo, intervallo di valore di mana, stelle delle recensioni, tier e intervallo WR si combinano con ricerca, sentiment e pool personale. Recensioni e WR distinguono dati disponibili e assenti; il ranking distingue tier assegnati, campione insufficiente e carta non presente nella fonte. Se minimo e massimo si contraddicono, la selezione restituisce zero risultati; “Azzera filtri” ripristina l’intero catalogo.

`build_expansion.catalog_data` espone la WR in mano del provider Untapped soltanto se la metrica è pubblica. I valori null e lo zero reale restano distinti. Le altre metriche, incluse quelle bloccate o sospette, non vengono usate come sostituti. Fonte, data, filtri e partite riportate accompagnano i dati; la data della WR non viene sostituita con quella del ranking. La vista non acquisisce nuovi snapshot né modifica le valutazioni o il motore Draft.

Controlli specifici: `python -m unittest test_catalog_statistics.py` e `node verify-catalog-filters.cjs`, con le variabili browser descritte in [verification.md](verification.md). Il controllo browser verifica ordinamenti, filtri combinati, dati assenti, reset, anteprime e larghezze 1440, 768 e 390 px. Screenshot e rapporto vanno in `MTG_QA_DIR` o in una cartella temporanea.


I cataloghi Atlas e Preview usano `catalog-controls.js`, `catalog-indices.js` e `catalog-controls.css` per i controlli, la composizione dei filtri e gli ordinamenti. La presentazione conserva il proprio renderer delle schede e i propri salvataggi. I controlli senza misure utilizzabili restano visibili con la dicitura “dati assenti” e gli ordinamenti non applicabili sono disabilitati; una nota riepiloga le lacune. Le funzioni si attivano dai dati senza condizioni sul nome del set. Anche i filtri per valutazione Sealed, sentiment e solo pool personale sono presenti in entrambe le presentazioni.

`node verify-shared-catalog.cjs` controlla il catalogo Preview senza recensioni, tier o WR, e verifica con una fixture che l’aggiunta di tali dati abiliti controlli e ordinamenti senza cambiamenti al template. Verifica anche zero reale, dati null, filtri combinati e anteprime su desktop, tablet e telefono. Eseguire insieme a `verify-catalog-filters.cjs` per la regressione Atlas.

## Indici WR Draft, WR Sealed e prospettive Constructed

Ogni catalogo Atlas espone due indici WR separati, con ordinamento crescente/decrescente, intervallo percentuale, copertura e campione minimo. Fonte ed evento si selezionano separatamente per Draft e Sealed. `catalogPerformance` espone gli snapshot pubblici in `statistics.draft.externalSources` e `statistics.sealed.externalSources`; `catalogWinRates` resta compatibile con la vista Untapped precedente. Snapshot, provider ed eventi diversi non vengono mediati. Il filtro e l’ordinamento usano soltanto la fonte selezionata. I controlli restano visibili quando mancano misure; i valori mancanti seguono quelli presenti e uno zero reale rimane zero.

`import_public_game_statistics.py` deriva GIH WR dai file Game Data pubblicati in [17Lands Public Data](https://www.17lands.com/public_datasets), sotto licenza CC BY 4.0. Per ogni carta conta una sola osservazione per partita quando `opening_hand + drawn > 0`, indipendentemente dal numero di copie. Il numeratore conta le vittorie in queste partite; la WR è `100 * vittorie / osservazioni`. Un campione zero produce `null`. L’importazione usa pandas/numpy, mentre la build statica continua a usare soltanto la libreria standard e file locali.

L’importazione conserva hash SHA-256, URL del file, Last-Modified, dimensione compressa, conteggi, licenza, metodo, carte associate e lacune. Si usa tutto il file pubblico, con tutti i ranghi e gli archetipi: non è lo snapshot corrente della tabella live 17Lands. Non viene applicata una soglia nascosta e i campioni sotto 100 partite sono segnalati. Pick-Two conserva un dataset distinto; un prodotto cartaceo non eredita le statistiche di una versione digitale dal nome simile. Le carte assenti rimangono senza WR. I nuovi snapshot non aggiornano voti, politiche dei bot o revisioni funzionali dei replay.

```sh
python import_public_game_statistics.py --output research/<acquisizione>/17lands --apply --workers 3
```

I quattro indici Constructed leggono le valutazioni attribuite in `cards[].prospects.formats.standard`, `pioneer`, `modern`, `pauper`, insieme alla legalità del catalogo. Permettono filtro per formato, stato della prospettiva e legalità. I dataset precedenti conservano l’ordine qualitativo adozione ripetuta, adozione documentata, prime presenze. Quando è presente `tournamentIndex`, il suo indice numerico misurato diventa il riferimento per filtri e ordinamenti; lo zero osservato resta distinto da N/D. Anteprime, dati mancanti, legalità e osservazioni Commander rimangono distinti. Le carte mostrano tutti e quattro gli stati; i dettagli riportano analisi e fonti esistenti. Una data dell’analisi Commander non viene presentata come data di una prospettiva Standard assente.

Controlli: `python -m unittest test_catalog_statistics.py test_catalog_metrics.py`, `node test-catalog-indices.cjs`, `python -m unittest test_public_game_statistics.py` con pandas/numpy disponibili, e `node verify-catalog-indices.cjs` con le variabili browser documentate. Il controllo browser attraversa tutte le espansioni registrate e verifica ordinamenti, filtri combinati, legalità, campioni, assenze e conservazione dei salvataggi.

## Indice Constructed dai tornei

`prospects.formats.<formato>.tournamentIndex` aggiunge osservazioni misurabili per Standard, Pioneer, Modern e Pauper, senza sostituire le recensioni o le osservazioni storiche precedenti. Il metodo `published-deck-share-v1` assegna un indice 0–100 pari a `100 × liste con la carta / liste pubblicate ammissibili`. Una lista conta una volta anche se contiene più copie o la carta è sia nel main deck sia nel sideboard. Sono conservati separatamente main, sideboard, copie, eventi con presenza, Top 8, vittorie dei mazzi ed esempi collegati alla fonte. Questi risultati non dimostrano una WR causale della carta. Top 8 e vittorie contano soltanto piazzamenti documentati: zero attestazioni non certifica assenza di risultati nelle liste prive di rank, che rimangono `null` negli esempi.

L’indice recente usa la finestra dichiarata nel campione. I Pro Tour più vecchi sono riportati in `history` e `historicalExamples`, senza entrare nel denominatore recente. Ogni evento conserva numero di liste pubblicate, partecipanti quando dichiarati, copertura e tutte le pagine sorgente. Le pubblicazioni parziali non diventano un censimento completo del metagame. Le leghe selezionate per risultato non fanno parte di questa acquisizione. Un giocatore in due eventi diversi conta come due osservazioni di torneo; un duplicato dello stesso mazzo/evento viene eliminato.

Lo zero significa soltanto non osservata nel campione. Un evento anteriore alla prima uscita nota non produce un’assenza: senza campione ammissibile l’indice è `null`. Una presenza documentata più vecchia può attestare che un’identità ristampata esisteva già. L’abbinamento usa nomi normalizzati, nome Oracle e faccia principale, mantenendo gli ID del catalogo. Le date mancanti non sono inventate. Terre base, legalità sconosciuta e carte attualmente non legali hanno indice N/D, con motivo esplicito.

Il segnale uso ripetuto richiede almeno cinque liste in tre eventi. Le altre presenze sono prime segnalazioni. Il confronto temporale usa due periodi dichiarati con almeno 50 liste ciascuno: crescita e calo richiedono uno scarto di almeno un punto percentuale e almeno tre presenze nel periodo che sostiene il segnale. Non è un test di significatività. Da osservare indica prime presenze o crescita osservata; uso ripetuto documentato indica adozione ripetuta. Nessuna di queste etichette è una probabilità di successo futuro o una previsione economica.

Il catalogo ordina e filtra l’indice per formato, intervallo, dimensione del campione e segnale da seguire. I dettagli mostrano storico, Pro Tour ed esempi. La pagina Constructed riceve una selezione misurata per formato, affiancata alle schede editoriali esistenti; le valutazioni precedenti restano attribuite e datate. Con Tutti, l’ordinamento della selezione usa l’indice massimo fra i formati della carta; selezionare un formato rende omogeneo il confronto.

Acquisizione riproducibile: `research_tournament_lists.py --output research/<acquisizione>` scarica e normalizza le liste ufficiali, conservando URL, data e hash del documento. Per le vecchie pagine dinamiche del Pro Tour Pioneer di Karlov Manor usare anche `node capture_pioneer_pro_tour.cjs`, con Playwright configurato. Le 258 liste vengono estratte dal testo visibile delle cinque pagine ufficiali e controllate con i totali di main e sideboard. `integrate_tournament_prospects.py --research research/<acquisizione> --apply` calcola gli indici di ogni carta nei cataloghi registrati e aggiorna discovery e fonti. `tournament_index.py` contiene calcolo e validazione; `competitive-prospects-ui.js` presenta le misure condivise. Le fonti restano locali per la build offline. La selezione datata dei tornei e la finestra del metodo devono essere aggiornate esplicitamente per una nuova acquisizione, senza cambiare la data di un vecchio campione.

Controlli: `python -m unittest test_tournament_index.py test_research_tournament_lists.py`, `node test-catalog-indices.cjs`, controlli del contratto e browser pertinenti. Gli indici restano separati da WR Limited, voti, politiche dei bot, salvataggi e revisioni funzionali dei replay.
