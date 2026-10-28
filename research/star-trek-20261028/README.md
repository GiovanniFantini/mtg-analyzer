# Aggiornamento Star Trek del 28 ottobre 2026

Catalogo TRK/SDS aggiornato da Scryfall: 265 carte distinte e 495 stampe,
rispetto a 248 carte e 462 stampe del 27 ottobre. Il catalogo resta parziale.
Le 17 identità aggiunte sono tutte TRK. Identità precedenti e salvataggi conservati.
`catalog-delta.json` registra aggiunte, correzione del nome Holo-Engineer e
modifica del testo di Hit It! da look a reveal.

Profili editoriali aggiunti per tutte le nuove carte. Previsioni automatiche
Constructed MTG-Standard riacquisite e abbinate a 231 carte, senza convertirle
in voti Limited. `standard-constructed-preview.json` conserva metodo, scala,
associazioni e hash della pagina acquisita.

Le pagine ufficiali su prodotti, meccaniche e calendario Arena sono state
ricontrollate. Il testo di prodotti, meccaniche e calendario Arena coincide
con la cattura precedente. `source-audit.json` conserva URL, data, stato e hash
per le fonti richieste. Il Pick Order Untapped TRK restituisce ancora una pagina
di errore; nessuna classifica o percentuale di vittoria è stata importata.

Prezzi Cardmarket e osservazioni EDHREC restano datati 27 ottobre.
Cardmarket ha rifiutato la nuova acquisizione HTTP con 403. Le 17 carte aggiunte
non ereditano prezzi, osservazioni Commander o risultati da altre carte.
Restano 201 carte con minimo Cardmarket, 238 con osservazioni Commander e
113 righe nell’appendice Commander distinta dal pool Limited.
Collazione, eventi, disponibilità e chiavi locali non sono stati modificati.

## Riproduzione

Acquisizione di rete, da avviare esplicitamente dalla radice del repository:

```sh
python refresh-star-trek-20261028.py
python research_star_trek_20261028.py
python enrich_star_trek_20261028.py
```

Riproduzione offline dalle acquisizioni conservate:

```sh
python refresh-star-trek-20261028.py --from-snapshot
python enrich_star_trek_20261028.py
python build_site.py
```

Lo script di integrazione riutilizza il parser del 27 ottobre; se la cache HTML
temporanea manca, legge la cattura normalizzata del 28 ottobre. La build del sito
non esegue nessuno script di acquisizione e continua a funzionare offline.

## Verifiche

- Build riuscita: due espansioni, venti pagine HTML, collegamenti locali validi.
- Cinque test `test_star_trek_research.py` superati dopo aver collegato il test
  delle previsioni alla cattura corrente, conservando quelle storiche.
- Suite `test_expansion_data.py`: trenta test superati e due errori nelle fixture
  di Reality Fracture (`test_correlated_exclusions_are_not_rejected_by_upper_bounds`
  e `test_pair_unique_counts_use_actual_pair_members`). Il validatore
  `expansion_data.py` conteneva già modifiche locali prima dell’attività e non
  è stato modificato per questo aggiornamento.
- `verify-star-trek-research.cjs` superato con Chrome a 1440 e 390 pixel:
  previsioni, prezzi storici, legalità e anteprime da mouse, tastiera e tocco.
- `verify-update.cjs` superato: tutte le 17 carte cercabili su desktop e telefono,
  identità corrette, profilo nuovo, prezzo assente e anteprime accessibili.
  Evidenze in `browser-verification.json` e negli screenshot datati della cartella.
- Controllo del diff senza errori di spaziatura.

Aggiornamento locale. Nessun commit o push eseguito.
