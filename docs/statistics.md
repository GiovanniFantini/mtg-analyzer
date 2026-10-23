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
