# MTG Analyzer

Sito statico in italiano per consultare e analizzare espansioni di Magic: The Gathering: cataloghi, guide Limited, pool personali, sinergie, analisi delle carte e strumenti di simulazione. Tutte le espansioni registrate usano Atlas, motori condivisi e documenti JSON distinti. Ogni strumento è disponibile in base ai dati effettivamente presenti.

[Apri il sito](https://giovannifantini.github.io/mtg-analyzer/).

## Avvio locale

Richiede Python 3.12 o successivo, senza pacchetti esterni per la build.

```sh
python build_site.py
python -m http.server 8765 --directory dist
```

Aprire [localhost:8765](http://localhost:8765). La build genera il sito dagli input locali e verifica i collegamenti HTML. Non scarica nuovi cataloghi, statistiche o prezzi. Node.js, Playwright e un browser compatibile servono soltanto ai relativi controlli.

Modificare i sorgenti e i template. `dist/` e le pagine generate non sono sorgenti da correggere manualmente. Un push su `main` avvia il workflow di build e pubblicazione GitHub Pages; la disponibilità online si conferma dall'esito del workflow, non dal solo push.

## Mappa del repository

| Percorso | Contenuto |
| --- | --- |
| `expansions.json`, `expansions/<slug>/` | Registro, manifest, cataloghi, prodotti, eventi e contenuti delle espansioni |
| `expansion_data.py`, `statistics_data.py`, `schemas/` | Caricamento, normalizzazione e validazione dei dati |
| `build_site.py`, `build_expansion.py`, `render_guides.py` | Build offline e rendering condiviso |
| `templates/atlas/`, `templates/preview/` | Presentazioni condivise; i builder storici sono adattatori di compatibilità |
| `collation.js`, `draft-engine.js`, `draft-table.js` | Collazione, decisioni dei bot e interfaccia Draft |
| `site_navigation.py`, `site.css`, `site.js`, `card-hover.*` | Navigazione, presentazione e anteprime delle carte |
| `research/`, `reviews/`, snapshot datati | Acquisizioni, evidenze e registri delle verifiche |
| `docs/`, `.agents/skills/`, `AGENTS.md` | Contratti, procedure riutilizzabili e istruzioni di progetto |

## Documentazione per attività

| Serve a | Leggere |
| --- | --- |
| Aggiungere un'espansione o cambiare il contratto | [Architettura e JSON](docs/architecture.md) |
| Importare WR, ricercare metagame o aggiornare gli indici Constructed | [Statistiche per carta e metodo dei tornei](docs/statistics.md) |
| Capire il motore e i profili dei bot | [Motore Draft](docs/draft-engine.md) |
| Verificare prezzi o valore di un box | [Metodo economico](docs/economics.md) |
| Consultare requisiti e limiti delle viste per formato | [Requisiti](docs/requirements.md) |
| Eseguire test, configurare il browser o verificare la pubblicazione | [Sviluppo e verifiche](docs/verification.md) |
| Riprendere ricerca e verifiche datate | [Resoconti del 22 ottobre 2026](docs/history/2026-10-22.md), poi snapshot e registri effettivi |
| Capire dove scrivere nuove istruzioni o documentazione | [Criteri di manutenzione](docs/documentation.md) |

Le procedure per gli agenti sono nelle skill locali: [ricerca](.agents/skills/mtg-research/SKILL.md), [nuova espansione e inventario fonti](.agents/skills/mtg-new-set/SKILL.md), [bot Draft](.agents/skills/mtg-draft-bots/SKILL.md), [UX](.agents/skills/mtg-site-ux/SKILL.md) e [review indipendente](.agents/skills/mtg-review/SKILL.md). [AGENTS.md](AGENTS.md) stabilisce quando usarle e contiene i vincoli permanenti. Le preferenze personali generali appartengono al file globale di Codex.

Il [gestore torneo Draft locale](docs/tournament.md), raggiungibile da Home e dal menu, gestisce da 2 a 8 giocatori con qualsiasi set: iscrizioni, turni alla svizzera, risultati, timer e classifica. Non richiede i dati di una specifica espansione.

## Dati, limiti e salvataggi

Nella pagina Draft della presentazione Atlas, “La prossima pick” offre un assistente per draft informali: ricerca per nome, colore, costo e tipo, registrazione nel pool Draft esistente, confronto contestuale di due carte e priorità fra le sole comuni. “Solo assistente” concentra la pagina sui controlli per telefono. I consigli sono euristiche sui voti Limited e sulle sinergie già documentate, non probabilità di vittoria o letture dei segnali del tavolo. Il piano si può scegliere manualmente o suggerire dal pool. `node verify-draft-assistant.cjs`, con le variabili browser documentate, verifica decisioni contestuali, costi ibridi e facce principali, telefono, anteprime, sincronizzazione e protezione dei salvataggi.

Espansione selezionata, formato di gioco ed evento Limited sono dimensioni distinte. Cataloghi, statistiche, recensioni e prezzi hanno date e coperture proprie: rigenerare il sito non li aggiorna. Le informazioni mancanti restano esplicite e non vengono inventate per abilitare strumenti. Nuove rilevazioni economiche usano Cardmarket; i modelli storici con fonti miste conservano il proprio metodo.

Ogni catalogo espone WR Draft e WR Sealed separati e prospettive per Standard, Pioneer, Modern e Pauper. Filtri e ordinamenti indicano fonte, campione e lacune. Gli indici Constructed misurano l'adozione nelle liste pubblicate; segnali di crescita e uso ripetuto aiutano a scegliere cosa seguire, senza stimare probabilità future. I Pro Tour storici restano distinti dal campione recente. Uno zero osservato e un dato non disponibile hanno significati diversi: il [metodo degli indici](docs/statistics.md) ne definisce il trattamento.

Pool e carte osservate sono conservati nel browser del visitatore, senza account o sincronizzazione. Cambiare origine, per esempio da un file locale al sito HTTPS, non trasferisce i salvataggi: usare esportazione e importazione dove disponibili. Replay e salvataggi incompatibili richiedono conservazione integrale prima di una nuova scrittura.

`ev-*` e `docs/local/` sono esclusi da Git e contengono analisi private. Non sono dipendenze della build pubblica. I resoconti storici documentano verifiche svolte su versioni precise, senza certificare modifiche successive.

Progetto indipendente. Magic: The Gathering, le immagini e i testi delle carte appartengono ai rispettivi titolari. Le fonti sono collegate nelle sezioni del sito.
