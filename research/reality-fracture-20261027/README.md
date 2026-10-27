# Reality Fracture: ranking Untapped del 27 ottobre 2026

Fonte: https://mtga.untapped.gg/limited/draft/reality-fracture/pick-order

Acquisizione del DOM pubblico nel browser, con Premier Draft, Latest Event, Bronze–Platinum, All Archetypes e tiering In Hand WR. La pagina riportava 980.000 partite e aggiornamento circa tre ore prima. Il testo originale e gli URL delle carte sono conservati in `untapped-pick-order-dom.json`. La lettura web indicizzata mostrava alcuni gruppi diversi: per questa importazione fa fede esclusivamente la cattura browser salvata.

Copertura: 290 carte abbinate senza ambiguità a 295 identità del catalogo, incluse tutte le dieci Special Guests. Sono presenti 283 tier assegnati e sette carte con campione insufficiente; le cinque terre base non sono elencate. Il gruppo senza tier non è convertito in F o in zero. Non sono state acquisite metriche Premium.

`untapped-pick-order-20261027.json` conserva la normalizzazione con hash SHA-256 dell’input. Per riprodurre l’importazione:

```sh
python import_untapped_pick_order.py research/reality-fracture-20261027/untapped-pick-order-dom.json --expansion expansions/reality-fracture --apply
```

Il catalogo offre il pulsante “Mostra ranking Draft Untapped”, l’ordinamento “Tier Draft Untapped” e il parametro `?order=untapped`. Ordine alfabetico all’interno dei tier, dati insufficienti in fondo. Fonte, data e filtri sono riportati nelle schede. I campi precedenti di ratings.json, incluse recensioni e data, sono stati confrontati con HEAD e risultano identici eliminando la sola nuova proprietà untappedPickOrder. I dati statistici già presenti e le modifiche di altre attività sono conservati.

Verifiche: build offline riuscita e collegamenti locali validi; tre test dell’importatore superati, inclusi duplicati, nomi sconosciuti e campioni insufficienti; seconda importazione identica alla prima. La suite test_expansion_data.py esegue 32 test: 30 superati e due errori nelle fixture di collazione (test_correlated_exclusions_are_not_rejected_by_upper_bounds, test_pair_unique_counts_use_actual_pair_members). Gli stessi due errori sono stati riprodotti togliendo dai dati in memoria tutti i nuovi ranking: sono indipendenti da questa modifica.

Il controllo browser riproducibile è `check-ranking.cjs`, configurato tramite MTG_SITE_URL, MTG_PLAYWRIGHT_MODULE e MTG_BROWSER_CHANNEL. Esito browser: nessun errore JavaScript; ordinamento, ricerca, gruppo senza tier e anteprime verificati su desktop a 1440 px e telefono a 390 px. Il mouse apre il tooltip; tastiera e tocco sul titolo aprono il dialogo della carta. Esiti e immagini sono salvati accanto alla cattura. Verifiche eseguite prima del commit.

Verifica del contenuto preparato per il push: checkout separato dai soli file nell’indice Git, build offline riuscita, 35 test superati (importatore e contratto espansioni), controlli browser desktop/mobile superati. I due errori del workspace non si riproducono con i soli file destinati al commit. La regola Git eol=lf sulla cattura conserva i byte dell’hash SHA-256 anche nei checkout Windows.
