# Dove conservare istruzioni e conoscenza

## Criteri di collocazione

| Informazione | Destinazione | Aggiornamento |
| --- | --- | --- |
| Preferenza personale valida per tutti i progetti, comprese email e stile | `~/.codex/AGENTS.md` | Solo per una preferenza generale confermata |
| Vincolo che cambia il comportamento in tutto questo progetto | `AGENTS.md` | Regola breve, con ambito e rinvio se serve |
| Procedura ricorrente che serve soltanto per alcune richieste | `.agents/skills/<nome>/SKILL.md` | Trigger preciso, passaggi utili, riferimenti caricati a richiesta |
| Contratto o spiegazione tecnica dell'implementazione | Documento tematico in `docs/`, schemi e validazione | Nello stesso intervento che cambia il contratto |
| Contenuto, valutazione, fonte o dato specifico di un'espansione | `expansions/<slug>/*.json` e acquisizioni datate | Con provenienza, data e copertura |
| Esito di ricerca, review o misura su una versione | Snapshot, `research/`, `reviews/` o `docs/history/`; verbali con materiale privato in `docs/local/reviews/` | Nuovo record datato; nei registri condivisibili solo hash, decisioni ed evidenze prive dei valori personali |
| Requisito ancora da realizzare | `docs/requirements.md` | Separare sempre stato richiesto e implementato |
| Costo personale di acquisto e memoria privata | `docs/local/` e file `ev-*`, ignorati da Git | Conservare i dati confermati e i riferimenti storici |

Il README è l'ingresso per chi usa o sviluppa il progetto: avvio, mappa e collegamenti. Evitare di trasformarlo in un registro di sessione o di ricopiare al suo interno ogni procedura. AGENTS.md contiene soltanto ciò che serve sempre e i criteri per trovare il resto. Le skill non sostituiscono i dati o la documentazione tecnica.

## Quando aggiungere una regola o una skill

Trasformare una correzione in istruzione permanente soltanto se descrive un vincolo ancora valido e riutilizzabile. Un bug risolto appartiene prima di tutto a codice, controllo di regressione e registro datato. Evitare regole universali nate da un singolo esempio, prescrizioni su modelli specifici non richiesti e obblighi di leggere o provare tutto per una modifica piccola.

Creare una skill quando esiste un flusso ricorrente con decisioni non ovvie. Preferire una breve procedura autonoma; aggiungere riferimenti soltanto quando servono a percorsi differenti. Prima di aggiungere un file cercare il luogo esistente con lo stesso significato. Non duplicare la stessa istruzione in più documenti; i riepiloghi devono rimandare al riferimento di dettaglio.

Le `.rules` di Codex regolano l'esecuzione di comandi e le relative decisioni di approvazione. Non sono contenitori di linee guida editoriali o tecniche.

## Controlli di manutenzione

Controllare link locali e riferimenti ai comandi, frontmatter e riferimenti delle skill, file non tracciati o ignorati e diff finale. Per ogni skill usare il validatore `quick_validate.py` fornito con skill-creator quando disponibile. Verificare anche il significato: richiesta di soli prezzi, modifica UX e indagine sui bot devono caricare percorsi diversi, senza attivare attività non autorizzate. Un validatore di struttura non dimostra il comportamento dell'agente.

Fonti consultate per l'organizzazione: [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [skill locali](https://learn.chatgpt.com/docs/build-skills), [regole di esecuzione](https://learn.chatgpt.com/docs/agent-configuration/rules). Consultate il 22 ottobre 2026. Le skill di repository sono in `.agents/skills/`; il limite documentato predefinito delle istruzioni aggregate è 32 KiB. Il caricamento progressivo evita di consumarlo con cronologie e procedure non pertinenti.

Per la mappa della migrazione e gli esiti datati vedere il [resoconto del 22 ottobre](history/2026-10-22.md#riorganizzazione-documentale). Per i cicli indipendenti successivi vedere `reviews/docs-reorganization-20261022/decisions.json`.
