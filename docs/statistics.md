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


I cataloghi Atlas e Preview usano `catalog-controls.js` e `catalog-controls.css` per i controlli, la composizione dei filtri e gli ordinamenti. La presentazione conserva il proprio renderer delle schede e i propri salvataggi. I controlli senza misure utilizzabili restano visibili con la dicitura “dati assenti” e gli ordinamenti non applicabili sono disabilitati; una nota riepiloga le lacune. Le funzioni si attivano dai dati senza condizioni sul nome del set. Anche i filtri per valutazione Sealed, sentiment e solo pool personale sono presenti in entrambe le presentazioni.

`node verify-shared-catalog.cjs` controlla il catalogo Preview senza recensioni, tier o WR, e verifica con una fixture che l’aggiunta di tali dati abiliti controlli e ordinamenti senza cambiamenti al template. Verifica anche zero reale, dati null, filtri combinati e anteprime su desktop, tablet e telefono. Eseguire insieme a `verify-catalog-filters.cjs` per la regressione Atlas.
