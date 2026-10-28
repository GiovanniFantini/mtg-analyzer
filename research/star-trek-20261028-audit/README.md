# Verifica dei dati precedenti Star Trek, 28 ottobre 2026

Controllati tutti i sedici documenti attivi dell’espansione, compresi i dati
già presenti prima dell’aggiornamento: catalogo, stampe, profili, archetipi,
guide, regole, prodotti, fonti, osservazioni, prezzi e metadati.

## Riscontri e correzioni

| Area | Copertura ed esito |
| --- | --- |
| Catalogo | Tutte le 265 identità confrontate con una nuova acquisizione Scryfall: nomi, costi, valore di mana, colori, identità, tipi, testi, rarità, legalità, keyword e forza/resistenza. Nessuna variazione rispetto alla cattura precedente. |
| Stampe | Tutte le 495 stampe ricontrollate per numero, finiture e trattamenti. Nessuna differenza di corrispondenza. Il catalogo resta parziale e non è una ricetta di collazione. |
| Trascrizioni | Due errori della fonte confermati dalle immagini: Jett Reno riportava `+1/1 counter`; Mirror Universe Intrusion ometteva i simboli colorati nel promemoria del kicker. Corretti in `text`, nell’alias `oracle` e in `prospects.oracle.text`, con provenienza esplicita. Il costo effettivo del kicker era già corretto. |
| Tipo | Normalizzato il separatore mancante di Culber and Stamets, Star-Crossed, verificato sull’immagine. Nessuna modifica a nome, costo o identità della carta. |
| Analisi | Letti i profili del catalogo e confrontati con il testo. Corretti sei profili, descritti sotto. Sincronizzati gli alias descrittivi con `ratings.json`. Nessun voto Limited assegnato. |
| Archetipi e sequenze | Verificati i dieci piani di colore, le carte citate, costi e restrizioni delle sequenze esistenti. Restano ipotesi editoriali, senza risultati o graduatorie inventati. |
| Statistiche | Ricontrollate tutte le cinque distribuzioni per colore. Descrivono il catalogo, senza rappresentare frequenze di apertura o vittorie. |
| Prezzi | Tutti i 201 riferimenti principali e le 189 osservazioni di variante coincidono con la cattura normalizzata Cardmarket originale. Importi, prodotti, filtri e data del 27 ottobre conservati. Nessun prezzo sostituito con zero. |
| Commander | Tutte le 321 osservazioni associate alle 238 carte coincidono con la cattura EDHREC. Le sezioni comandante/carta/ristampa restano distinte; le 113 righe esterne restano nell’appendice. Nessun conteggio interpretato come risultato agonistico. |
| Previsioni | Tutte le 231 associazioni e i valori MTG-Standard coincidono con la cattura del 28 ottobre. Nessuna conversione in WR o punteggi Draft. |
| Guide e riepiloghi | Rimossi i vecchi totali 248/462/210 e le indicazioni di rilevazione non più attuali. Corretto il falso avviso di assenza di prezzi. Download del catalogo collegato allo snapshot corrente; download storici etichettati con la propria data. |
| Prodotti ed eventi | Quantità, percentuali e trattamenti riscontrati nella pagina ufficiale; Draft, Sealed e profilo Pick-Two confrontati con le regole pertinenti. Nessuna ricetta, disponibilità o chiave di salvataggio modificata. |

Le sei correzioni ai profili sono:

1. Emergency Medical Hologram può bersagliare una creatura avversaria o se stesso.
2. Federation Probe non richiede una creatura propria diversa da sé per il bonus.
3. Peace in Our Time offre la scelta anche al suo controllore nel suo turno.
4. Borg Cube che lascia il campo e rientra non può assimilare le carte esiliate
   dalla precedente esistenza. Il riuso dell’esilio riguarda la stessa nave.
5. Amok Time non fa pescare. Il vecchio testo generico confondeva il promemoria
   delle Saghe con un effetto di pescata.
6. Genesis Effect richiede due bersagli nel lancio: una creatura e una terra
   propria. La descrizione precedente esplicitava soltanto il primo.

Rese precise anche le indicazioni sul segnalino +1/+1 dell’assimilazione e
sull’ambito non ancora risolto delle percentuali comuni/non comuni.
Rimossa dall’analisi pubblica la soglia di vendita di 0,10 euro presentata come
già scelta: non è una proprietà del prodotto e non esiste un modello EV TRK
completo a cui applicarla.

## Provenienza e limiti

Il confronto automatico completo è in `catalog-check.json` e
`derived-data-check.json`. `observation-check.json` riporta la copertura delle
osservazioni; `corrections.json` conserva i cambiamenti applicati.
Le immagini `67.jpg`, `248.jpg` e `191.jpg` sono le prove visive delle tre
anomalie di trascrizione o formattazione. Non sono nuove errata ufficiali.
Le acquisizioni grezze storiche non sono state riscritte. Il catalogo attivo e
lo snapshot scaricabile del 28 ottobre contengono le correzioni documentate.

Fonti ufficiali e riferimenti ricontrollati:

- [Meccaniche Star Trek](https://magic.wizards.com/en/news/feature/star-trek-mechanics), Matt Tabak, 20 ottobre.
- [Prodotti e composizione delle buste](https://magic.wizards.com/en/news/feature/collecting-star-trek), Zakeel Gordon e Jubilee Finnegan, 20 ottobre.
- [Calendario delle anteprime](https://magic.wizards.com/en/news/announcements/where-to-find-star-trek-previews) e [calendario Arena](https://magic.wizards.com/en/news/mtg-arena/star-trek-event-schedule).
- [Pagina ufficiale delle regole](https://magic.wizards.com/en/rules), che collega ancora le [CR del 25 settembre](https://media.wizards.com/2026/downloads/MagicCompRules%2020260925.txt). Verificati, secondo necessità, CR 100.2b, 100.4b, 103.5, 400.7, 603.3d, 607, 702.184 e 721.
- [MTR collegate da WPN](https://media.wizards.com/ContentResources/WPN/MTG_MTR_2026_Feb27_EN.pdf), sezioni 7.1, 7.2, 7.3 e 7.7, e [regole Pick-Two](https://magic.wizards.com/en/formats/pick-two-draft).
- [Avviso WPN sui ritardi](https://wpn.wizards.com/en/news/magic-the-gathering-star-trek-product-delays-in-select-regions), riscontrato nel [dettaglio regionale SCG](https://articles.starcitygames.com/magic-the-gathering/delays-expected-to-impact-select-magic-the-gathering-star-trek-products/).
- [Annuncio Magic Spotlight](https://magic.gg/news/start-your-voyage-at-magic-spotlight-star-trek-in-lille-and-minneapolis) e [intervista a Gavin Verhey](https://www.space.com/entertainment/space-games/magic-the-gathering-is-exploring-strange-new-worlds-with-the-star-trek-60th-anniversary-crossover-interview).

Le contraddizioni ufficiali sulla data della galleria completa e sulle terre
Away Team foil restano dichiarate. Le probabilità inferiori all’1% rimangono
limiti, senza trasformarle in valori puntuali. I dati mancanti impediscono
ancora di certificare la collazione o calcolare il valore atteso di un box.
La verifica dei prezzi riguarda la fedeltà delle osservazioni storiche, non una
nuova quotazione di mercato. Finiture distinte non rilevate restano mancanti.

## Riproduzione e verifiche

```sh
python audit_star_trek_20261028.py
python build_site.py
python -m unittest test_star_trek_research.py test_expansion_data.py
```

L’importatore `enrich_star_trek_20261028.py` applica automaticamente lo stesso
livello di correzione dopo l’integrazione. La ripetizione dell’importazione
ha prodotto sedici documenti attivi identici: `import-repeat-check.json`.
La build resta offline.

- Build riuscita, collegamenti locali validi.
- Otto test specifici Star Trek superati.
- Suite complessiva eseguita: 40 test, 38 superati e i due errori già presenti
  nelle fixture Reality Fracture `test_correlated_exclusions_are_not_rejected_by_upper_bounds`
  e `test_pair_unique_counts_use_actual_pair_members`. Nessuna modifica al
  validatore condiviso o ai dati Reality Fracture effettuata per questa attività.
- `verify-star-trek-research.cjs` e `verify-audit.cjs` superati a 1440 e 390 pixel:
  testi corretti, riepiloghi attuali, prezzi storici, legalità e anteprime da
  mouse, tastiera e tocco, senza errori JavaScript o overflow.
- Screenshot del catalogo e della pagina fonti ispezionati visivamente.
- Diff controllato senza errori di spaziatura.

Aggiornamento locale, nessun commit o push eseguito.
