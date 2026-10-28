# Audit di genericità e disponibilità, 28 ottobre 2026

## Contratto dei dati

I documenti versionati distinguono espansione, catalogo, stampe, prodotti, eventi Limited, valutazioni, statistiche e fonti. Non richiedono un match, il nome Reality Fracture o il codice FRA/TRK. Il contesto di una partita non è una proprietà obbligatoria del catalogo; gli snapshot statistici conservano il proprio contesto di gioco. I dati specifici del set risiedono nei documenti sotto `expansions/<slug>/`, secondo [il contratto architetturale](../architecture.md).

I salvataggi locali non vengono riversati nei JSON del catalogo. Pool e replay mantengono le proprie chiavi per espansione, le identità delle carte e la protezione dei record incompatibili. Il nome storico `star-trek.js` identifica un controller condiviso configurato dal manifest.

Quando una presentazione Preview attiva una pagina condivisa, il runtime fornisce anche `draftPool` e `sealedPool` se il manifest non li dichiara: `<id>-draft-pool-v1` e `<id>-sealed-pool-v1`. Le chiavi esplicite sono preservate. Il controllo delle collisioni fra espansioni include anche queste chiavi derivate; due test mirati verificano isolamento, conservazione e collisioni.

È stata rimossa una dipendenza residua delle disponibilità e dei controller dagli identificatori letterali `draft`, `sealed` e `picktwo`. Il tipo dell'evento deriva da `kind`; `defaultEvents` identifica un evento utilizzabile per tipo, preferendo gli identificatori storici se pronti. `eventAvailability` conserva le lacune di ogni singolo evento, anche quando un altro evento della stessa espansione è pronto. I dati precedenti e le chiavi dei salvataggi restano compatibili.

La disponibilità di una funzione espone separatamente `requested`, `dataReady` e `requirements`. Una funzione disabilitata nel manifest conserva anche l'elenco dei dati mancanti. Non vengono creati voti, prezzi o collazioni per renderla disponibile.

## Verifica ripetibile

Eseguire `python audit-expansion-capabilities.py` dalla radice del repository. Produce su standard output l'inventario JSON di tutte le espansioni registrate, le funzioni, i prodotti degli eventi e i dati mancanti. Usa soltanto i documenti locali e non modifica file. È complementare a `data/availability.json` e `data/runtime.json` pubblicati per ogni set.

Test aggiunti per identificatori evento nuovi, scelta di un prodotto Sealed pronto quando quello storico è incompleto e spiegazioni delle lacune anche per funzioni non richieste. Sono stati corretti due falsi rifiuti della validazione di collazione: esclusioni correlate e tre coppie distinte rappresentate da quattro fronti. Il validatore usa ora anche l'esecutore deterministico già presente in `collation_validation.py`; il controllo non equivale a una prova esaustiva di ogni percorso possibile.

Verifiche locali superate: `python -m unittest test_expansion_data.py` (35 test), `python verify-collation-contract.py`, controllo sintattico Node di `draft-pool.js`, `simulator.js` e `star-trek.js`. Le verifiche dell'interfaccia dopo l'integrazione dei template e del torneo sono responsabilità del controllo finale coordinato.

## Disponibilità dei dati rilevati

Reality Fracture dispone di catalogo, pool, guide, statistiche, sinergie, sentiment, discovery, simulazione delle buste e tavolo Draft. Il valore atteso del box resta indisponibile: servono prezzi verificati per tutte le stampe e finiture della collazione e un modello economico verificato. I riferimenti Cardmarket parziali non soddisfano questa dipendenza.

Star Trek dispone di catalogo parziale, pool manuale, analisi e regole degli eventi. Le lacune sono:

- Simulazione delle buste e tavolo Draft: catalogo completo, identificazione delle stampe ammesse, collazione verificata e valutazioni delle carte non base. Le probabilità pubblicate come minori dell'1% non diventano pesi inventati.
- Guida Sealed: contenuto strategico in `guides.fragments.gallery.strategy`, con dichiarazione `guides.sealed`.
- Guida Draft e pick: priorità, counterpick, rare condizionali, esempi di decisione e pacchetti di sinergie nei rispettivi campi strutturati di `guides.json`.
- Statistiche: snapshot per carta con campioni e metriche; per il confronto di contesti servono anche `statistics.draft.drill.contexts` e `retrieved`.
- Combo, sentiment e metagame: sequenze documentate, sintesi qualitative con fonti e osservazioni Constructed verificate, ciascuna nel proprio documento.
- Valore atteso del box: gli stessi requisiti economici di Reality Fracture, oltre alla collazione completa.

Questa è la disponibilità dei dati alla data dell'audit. L'inventario eseguibile resta il riferimento per gli aggiornamenti successivi. La verifica dell'interfaccia e dei percorsi di accesso è distinta e va eseguita sui template effettivamente pubblicati, secondo [le verifiche](../verification.md).
