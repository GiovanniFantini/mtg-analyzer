# Review UX della pagina Draft, 23 ottobre 2026

Quattro giri effettivi tramite Claude CLI, alias `sonnet`, modello restituito `claude-sonnet-5-5`. I primi due giri sono completi; il terzo verifica le modifiche dal secondo e il quarto le ultime correzioni dal terzo. I file rimasti invariati sono verificati con SHA-256. L'ultimo giro restituisce `findings: []` e nessun rilievo confermato resta aperto.

Sonnet ha esaminato sorgenti numerati ed evidenze testuali. Le riproduzioni nel browser e l'ispezione degli screenshot sono dell'autore. Non si tratta di una certificazione generale di accessibilità o di una prova su dispositivi fisici iOS.

| Giro | Rilievi | Decisioni |
| --- | --- | --- |
| 1 | 9 | Correzioni a contrasto dei nomi carta, cronologia, copertura del feedback, stampa, alias nelle situazioni di scelta, indice annidato, pannello piano e viewport ridotta |
| 2 | 6 | Cinque correzioni di accessibilità e interazione; scartato il giudizio soggettivo sull'ingombro della navigazione senza un difetto concreto |
| 3 | 4 | Ripristinati titolo e attribuzioni in stampa; estesa la stabilità della nav ai tablet. Due ipotesi su focus e padding scartate tramite ordine reale dei fogli e stili effettivi |
| 4 | 0 | Correzioni e possibili regressioni ricontrollate, nessun rilievo |

Durante le riproduzioni è stato corretto anche un tocco intermittente sul link di recupero del pool: il cambio da nav statica a sticky tra rilascio del dito e click poteva cambiare il bersaglio. La nav resta ora statica fino alla navigazione esplicita quando si lavora nei campi su telefono o con viewport ridotta.

## Evidenze

- [Decisioni per ogni rilievo](decisions.json).
- Manifest con versione, hash e modello: [giro 1](manifest-1.json), [giro 2](manifest-2.json), [giro 3](manifest-3.json), [giro 4](manifest-4.json).
- Risposte del revisore: [giro 1](findings-1.json), [giro 2](findings-2.json), [giro 3](findings-3.json), [giro 4](findings-4.json).
- [Rapporto browser finale](browser-final.json).
- [Helper riproducibile](review.py). Ogni giro è immutabile; richieste, risposte grezze e diff sono in `docs/local/reviews/draft-workspace-20261023/`, esclusi da Git.

Build offline, collegamenti locali, 24 controlli responsive su quattro viste e sei larghezze, regressioni mirate e suite completa dell'assistente riusciti. Verificati anche Contrasto elevato, focus della cronologia, zoom, viewport ridotta, transizione tablet, stampa, anteprime e recupero dei salvataggi. Restano fuori perimetro i due errori preesistenti della suite di collazione descritti nel [resoconto UX](../../docs/history/2026-10-23-draft-ux.md).

Le modifiche sono locali. Nessun commit, push o nuova pubblicazione inclusi nell'attività.
