# Torneo Draft locale

`tournament.html` è una pagina trasversale generata dalla build. Non richiede cataloghi, prezzi, voti o collazione. Funziona con qualsiasi espansione o mix, anche non registrati nel sito.

## Uso

1. Creare il torneo, annunciare turni e durata e iscrivere da 2 a 8 persone con nomi distinti.
2. Chiudere le iscrizioni: il primo turno è sorteggiato. Avviare separatamente il timer quando il tavolo è pronto.
3. Registrare vittorie dei due giocatori e game patte. Una patta intenzionale senza game giocati si registra 0-0 con zero game patte; un game concluso in patta conta separatamente. Una vittoria allo scadere può essere 1-0. I game non giocati non diventano patte.
4. Completare tutti i risultati prima del turno successivo. È possibile correggere il turno corrente fino alla generazione del successivo; i turni storici restano bloccati per preservare gli abbinamenti.
5. Concludere dopo l'ultimo turno annunciato ed esportare il JSON.

Ritiro e riammissione incidono sui turni futuri. Un incontro già assegnato resta da completare. Nessun risultato è assegnato automaticamente dalla scadenza del timer.

Se restano meno di due giocatori attivi, dopo avere registrato i risultati del turno corrente si può concludere anticipatamente. Il JSON conserva `endedEarly: true` insieme ai turni annunciati originariamente, senza inventare incontri o riammettere chi si è ritirato. La classifica tratta come uguali differenze inferiori a un miliardesimo nelle percentuali, evitando falsi spareggi dovuti alla rappresentazione numerica.

## Modello e limiti

`tournament-engine.js` contiene validazione, abbinamenti e classifica; `tournament-ui.js` gestisce la pagina e il salvataggio. Nessuna dipendenza aggiuntiva, server o account. È un solo gruppo di abbinamento da 2 a 8 persone, senza playoff o più pod. Non registra eventi ufficiali e non sincronizza dispositivi; per eventi sanzionati si usa [Wizards EventLink](https://eventlink.wizards.com/).

Gli abbinamenti minimizzano prima le rivincite, poi la distanza di punti. Il bye è assegnato fra chi ne ha meno, privilegiando chi è più basso in classifica. Le rivincite possono diventare inevitabili se si annunciano molti turni o si ritirano giocatori. Questo algoritmo locale non è una replica di quello proprietario di EventLink.

Punti e spareggi seguono [Magic Tournament Rules](https://wpn.wizards.com/en/rules-documents), versione del 27 febbraio 2026 collegata dal WPN e consultata il 28 ottobre 2026: §3.1 e appendice C. Ordine: punti, OMW, GW, OGW; minimo percentuale 0,33; bye 2-0 senza avversario. Le parità residue sono mostrate ex aequo. Il timer è configurabile; 50 minuti è il valore iniziale per i match, da adattare all'evento.

## JSON e conservazione

Contratto v1 identificato da `schemaVersion: 1` e `kind: mtg-local-tournament`, descritto in [tournament.schema.json](../schemas/tournament.schema.json). `set` è un'etichetta facoltativa senza dipendenza dal manifest; gli ID giocatore rimangono stabili fra turni. I risultati e la classifica non sono salvati nello stesso campo: la classifica si ricalcola dai match, evitando duplicazioni divergenti.

La chiave `mtg-local-tournament-v1` conserva un solo torneo corrente. Prima di importare o creare un torneo sostitutivo si salva integralmente il record precedente in una chiave backup univoca; se il backup fallisce non si sostituisce l'originale. È disponibile anche il download del precedente durante la sessione. I backup locali restano nello spazio del browser. I JSON incompatibili non sono sovrascritti automaticamente. Le scritture controllano modifiche da altre schede; in caso di conflitto si richiede di ricaricare.

Il timer salva una scadenza assoluta quando corre e i millisecondi rimanenti quando è in pausa. Riaprendo la pagina il tempo trascorso viene conteggiato, senza dipendere dal numero di tick JavaScript.

Verifiche: `node test-tournament.cjs`, `node verify-tournament-browser.cjs` con le variabili browser descritte in [verification.md](verification.md), più build offline e suite espansioni.
