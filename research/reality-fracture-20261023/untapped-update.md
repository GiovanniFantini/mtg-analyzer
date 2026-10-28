# Aggiornamento Untapped del 23 ottobre 2026

Fonte: https://mtga.untapped.gg/limited/draft/reality-fracture/card-data

Acquisizione delle celle pubbliche della tabella dinamica mediante scorrimento completo. Filtri confermati: Reality Fracture, Premier Draft, Latest Event, Bronze–Platinum, All Archetypes. La fonte indica circa 910.000 partite e aggiornamento circa tre ore prima della cattura.

Copertura: 290 carte, comprese dieci Special Guests; 288 con In Hand WR. Le cinque terre base non sono elencate dalla fonte. Identità e copertura coincidono con lo snapshot del 22 ottobre, conservato integralmente.

In Hand WR Delta e Played WR restano bloccati e null. Included WR rimane 0% per tutte le righe, marcato suspect ed escluso dalle valutazioni. I trattini restano null; i conteggi mantengono la precisione arrotondata originale. Nessuna modifica a 17Lands, voti, politiche dei bot o replay.

Riproduzione offline:

```sh
python import_untapped_statistics.py research/reality-fracture-20261023/untapped-card-data-dom.json --expansion expansions/reality-fracture --apply
```

Differenze per metrica rispetto al 22 ottobre (numero di carte):

- avgLastOffered: 83
- inHandWinRate: 89
- inHandWinRateDelta: 0
- inOpeningHandWinRate: 148
- playedWinRate: 0
- includedWinRate: 0
- games: 159

Verifiche: build offline riuscita (due espansioni, 20 pagine HTML e link locali verificati); test specifici delle statistiche superati. Suite test_expansion_data: 30 test superati e due errori di collazione (sameAsFirst e pairs), riprodotti anche sostituendo in memoria lo snapshot precedente del 22 ottobre. Non sono causati da questo aggiornamento. Verificato che ogni altro dato statistico sia invariato rispetto a HEAD. Nessuna modifica all’interfaccia; nessun commit, push o pubblicazione eseguiti.
