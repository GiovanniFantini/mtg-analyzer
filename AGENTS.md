# Istruzioni del progetto MTG Analyzer

## Vincoli permanenti

- Rispondere in italiano salvo richiesta diversa. Conservare le preferenze personali ereditate dal file globale, in particolare le autorizzazioni per email. Le istruzioni del progetto non autorizzano comunicazioni esterne.
- Per regole verificare Oracle e documenti ufficiali aggiornati: Comprehensive Rules (CR), Magic Tournament Rules (MTR), Magic Infraction Procedure Guide (IPG) o Judging at Regular Rules Enforcement Level (JAR), secondo necessità. Distinguere regole e policy considerando il Rules Enforcement Level (REL) dell'evento. Nelle risposte di arbitraggio l'assistente non deve presentarsi come Judge certificato o attribuirsi qualifiche personali reali. Per strategie usare ricerche pertinenti, esempi di carte del set, colori e sequenze concrete, anche nelle versioni per telefono.
- Nel deck building valutare piano, sinergie, curva, base di mana, consistenza, vittorie, sideboard e matchup secondo formato, legalità, budget e metagame pertinenti. Chiedere dettagli mancanti solo se incidono sulla risposta, esplicitando le ipotesi utili.
- Distinguere espansione selezionata, formato di gioco Constructed ed evento Limited. Verificare informazioni variabili e dichiarare cataloghi parziali, dati mancanti e incertezze.
- Ogni riferimento a una carta nel sito deve offrire anteprima con mouse, tastiera e tocco, compresi i contenuti dinamici.
- Modificare sorgenti e template, non pagine generate o `dist/`. La build deve riuscire offline dai soli file del repository.
- Espansioni in `expansions/<slug>/`, registrate in `expansions.json`. Nessun builder dedicato o condizione sul nome del set nei motori condivisi. Prodotto ed evento restano distinti; non inventare collazione, probabilità, voti o statistiche per abilitare strumenti.
- Conservare campi compatibili dei JSON. Per modifiche incompatibili aggiornare versione, adattatore, schemi, validazione e documentazione. Disponibilità dalle dipendenze reali, anche per singolo evento, non dal solo `requested`.
- Proteggere isolamento e salvataggi: chiavi per espansione, replay coerenti con la revisione funzionale, backup integrale prima di sostituire record incompatibili. Se il backup fallisce non sovrascrivere. Immagini, fonti e testi non invalidano replay.
- Per nuovi prezzi usare soltanto Cardmarket. Non sostituire dati mancanti con altre fonti o zeri. Conservare metrica, filtri, finitura, data e provenienza; gli snapshot storici mantengono il loro metodo originale.
- Conservare modifiche di altre attività. Commit e push devono rientrare nell'autorizzazione ricevuta per l'attività, compresa quella già valida nella sessione senza richiederla di nuovo. Una verifica dello stato Git richiede anche `git fetch` e controllo delle esclusioni, senza autorizzare commit o push. Distinguere aggiornamento locale, push e pubblicazione verificata sul workflow del commit.

## Caricare soltanto il contesto pertinente

| Attività | Riferimento da leggere |
| --- | --- |
| Contratti JSON, nuova espansione, renderer, collazione, disponibilità o salvataggi | [Architettura](docs/architecture.md) |
| Inserimento di una nuova espansione e riuso delle fonti | [Skill mtg-new-set](.agents/skills/mtg-new-set/SKILL.md) |
| Ricerca, ranking, recensioni, pool e mazzi Limited, sinergie, confronti fra draft, estrazione per carta, prospettive, prezzi o box | [Skill mtg-research](.agents/skills/mtg-research/SKILL.md) |
| Scelte sospette o modifica delle politiche dei bot Draft | [Skill mtg-draft-bots](.agents/skills/mtg-draft-bots/SKILL.md) |
| Restyling o miglioramento generale dell'esperienza | [Skill mtg-site-ux](.agents/skills/mtg-site-ux/SKILL.md) |
| Review indipendente richiesta, Sonnet o cicli di correzione | [Skill mtg-review](.agents/skills/mtg-review/SKILL.md) |
| Verifiche del codice, ambiente browser o pubblicazione | [Verifiche](docs/verification.md) |
| Consultazione completa per legalità e funzionalità ancora richieste | [Requisiti](docs/requirements.md) |
| Ripresa dell'analisi privata del box Reality Fracture | `docs/local/reality-fracture-box.md`, se presente; poi snapshot più recenti |
| Esiti e limiti delle attività del 22 ottobre | [Resoconto storico](docs/history/2026-10-22.md), poi registri e dati effettivi |

Applicare le skill indicate quando ricorre l'attività. Se non compaiono nel selettore, leggere direttamente il relativo `SKILL.md`. I link non impongono di leggere tutta la documentazione per ogni modifica.

## Verifiche minime per area

- Contratto, renderer o profili JSON: `python build_site.py` e `python -m unittest test_expansion_data.py`.
- Collazione, eventi o replay: anche `node verify-expansions.cjs`, `node verify-draft-engine.cjs` e `python verify-collation-contract.py`.
- Disponibilità, isolamento o salvataggi: anche `python verify-expansion-review.py` e `node verify-expansion-browser.cjs`, con sito servito da `dist/`.
- Modifiche visibili: controlli browser pertinenti e anteprime da mouse, tastiera e tocco. Configurare `MTG_SITE_URL`, `MTG_PLAYWRIGHT_MODULE` e `MTG_BROWSER_CHANNEL` senza percorsi personali fissi.
- Sola documentazione: verificare collegamenti, riferimenti e diff; non ripetere l'intera suite.

## Mantenere queste istruzioni

Qui restano vincoli e instradamento. Procedure nelle skill, contratti in `docs/`, contenuti e dati nei JSON, risultati in registri datati. Non aggiungere cronologie, prezzi, conteggi o parametri puntuali ad AGENTS.md. Seguire i criteri di [manutenzione documentale](docs/documentation.md).
