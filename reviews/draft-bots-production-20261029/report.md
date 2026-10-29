# Review tecnica dei bot Draft, 29 ottobre 2026

## Stato

Quattro giri effettivi con Opus come senior developer (modello restituito: `claude-opus-5-5` in tutti i giri) hanno prodotto 33 rilievi, verificati e decisi nel [registro](code-decisions.json). Il quarto giro non ha individuato nuovi P1. Le ultime correzioni dei profili delle carte e del cambio di bot nella revisione sono successive a quel giro. Il quinto tentativo non è stato eseguito dal modello: il servizio ha restituito `usage_limit_reached`, con ripristino indicato alle 17:30 di Roma. [Risposta originale](code-review-5.response.json).

Giovanni ha chiesto di proseguire con il lavoro locale e gestirà personalmente la ripresa. Non è stata programmata alcuna automazione. L'approvazione finale congiunta rimane pendente. I test locali non equivalgono a quella approvazione.

La v3 resta predefinita. La v4 resta una scelta sperimentale esplicita, per eventi con una scelta per turno nel browser. La preparazione e review non includevano commit o push. La successiva richiesta di Giovanni «push» autorizza il commit e il push di queste modifiche, mantenendo v3 predefinita e v4 sperimentale. Nessuna promozione competitiva, stima di WR o modifica delle pipeline. Il workflow esistente pubblica ogni push su main.

## Correzioni

- La costruzione del mana considera insieme terre possedute, basi aggiungibili, fonti indirette, costi ibridi e tempi delle terre tappate. La valutazione usa il turno nominale della carta; il ritardo ammesso per accettare uno splash non aumenta artificialmente il suo valore.
- Le scelte dei sette bot sono distribuite fra un massimo di quattro worker ausiliari. L'applicazione dei risultati rimane deterministica e transazionale. Un errore conserva lo stato precedente.
- Pick, ricostruzione e liste finali vengono calcolate fuori dal thread dell'interfaccia. Doppio clic, worker interrotti, annullamento e fallimenti del salvataggio hanno controlli dedicati.
- Il worker verifica i byte effettivi del codice prima di eseguirli. Codice e pagina di revisioni diverse sono rifiutati conservando il salvataggio. I replay incompatibili vengono salvati integralmente prima di qualsiasi sostituzione, che viene bloccata se il backup fallisce.
- I profili distinguono interazione contro l'avversario da effetti su carte proprie, costi nel cimitero e danni solo al giocatore. L'audit manuale comprende 83 stampe con hash Oracle, 75 positive e 8 negative. Il classificatore rimane conservativo, senza pretendere di interpretare ogni testo Oracle.
- Il cambio di bot nella revisione elimina subito la lista precedente e mostra il nuovo bot in calcolo. I risultati asincroni superati non vengono attribuiti al posto sbagliato.
- Potenza pura evita la ricerca contestuale. Le sinergie causali prive di annotazioni affidabili restano disattivate e dichiarate nell'interfaccia.

La prima acquisizione completa ha rilevato un task di 2109 ms e un intervallo del battito di 2121 ms. Il criterio ha bloccato quella versione. Il trasporto successivo conserva i log completi nel worker, trasferisce solo la revisione selezionata e serializza l’export nel worker. Il tentativo fallito resta nella cartella qa-44fe0a16880b. Una seconda acquisizione ha poi rilevato un task da 371 ms sul terzo tavolo. La traccia diagnostica non mostra un equivalente punto pesante nel JavaScript della pagina; la contesa CPU resta un’ipotesi. Il limite dei worker ausiliari riserva ora due CPU logiche pubblicizzate dal browser anziché una, mantenendo almeno un worker e al massimo quattro. Il confronto è stato ripetuto con gli stessi limiti e ha superato tutti i criteri locali. Le due acquisizioni fallite sono conservate. La logica delle scelte non è cambiata.

I dettagli, comprese le decisioni parzialmente accolte e le estensioni rimandate, sono nel registro. La ricerca del mana è limitata, non esaustiva. Non sono implementati checkpoint persistenti o un archivio eseguibile delle vecchie revisioni v4. La ripresa completa può essere costosa: mostra avanzamento, stima del tempo e annullamento.

## Evidenze finali

Build offline completata: 21 espansioni, 290 pagine HTML e collegamenti locali. Passate le 43 prove Python, il controllo del contratto di collazione, tutte le 10 verifiche Node del motore e dei worker, i controlli browser v4 e storici, e le 19 fixture isolate del contratto. La sola modifica successiva alla suite completa riserva una CPU aggiuntiva alla pagina riducendo il numero di worker. Cinque sorgenti runtime sono identici; la differenza del sesto è verificata byte per byte e registrata in cpu-reserve-decision.json. Sul worker aggiornato sono ripassati parità ed export, gestione degli errori nel client, flussi browser dei worker e acquisizione completa con replay.

Le 126 scelte predefinite hanno p50 1255 ms, p95 2896 ms e massimo 5389 ms. Il controllo separato Potenza pura comprende 42 scelte, p95 525 ms. Task massimo dell'interfaccia, comprese le riprese, 62 ms; intervallo massimo del battito 327.0 ms.

Le riprese complete sul primo seme: 41 scelte in 64.3 secondi; 42 scelte in 47.4 secondi. L’export dopo ripresa completa coincide con quello originale.

I quattro tavoli reali nel browser coincidono esattamente con il replay sequenziale per tutti i pool e log. Il confronto esatto usa lo stesso Chromium e byte verificati dei sorgenti. Il primo confronto con Node aveva differenze nelle ultime cifre decimali dei punteggi: quel tentativo non è stato accettato come parità esatta e il limite è conservato in node-cross-runtime-limitation.json. Ogni tavolo conserva tutte le 336 carte della collazione iniziale. Il confronto v3 usa la stessa collazione; la diagnosi condivisa costruisce 56 mazzi da 40 slot usando soltanto carte possedute e basi ammesse. Errori di mana e carenze rimangono registrati come diagnosi, senza sostituirli con un giudizio di forza. Vedere [evidenze locali complete](local-verification.json), [prestazioni](qa-05bca7a673a4/performance.json) e [parità sequenziale](qa-05bca7a673a4/sequential-parity.json).

Nei tre tavoli predefiniti, tutti i 21 mazzi v3 e i 21 mazzi v4 hanno 40 slot, nessun posto magia scoperto e nessun errore di mana secondo la diagnosi interna condivisa. Nel controllo Potenza pura, due mazzi su sette per ciascuna politica hanno posti magia scoperti: tre complessivi per v3 e quattro per v4, riempiti con basi secondo il contratto. Questi risultati del controllo restano espliciti e non vengono mescolati ai tavoli predefiniti.

Il protocollo prestazionale è stato fissato [prima dell'acquisizione](protocol-decision.json): 126 scelte predefinite su tre semi, controllo separato di 42 scelte Potenza pura, p95 entro 5 secondi sul desktop misurato, task dell'interfaccia entro 200 ms e intervalli del battito entro 500 ms. Comprende ultima pick, lista finale, export e ripresa di 41 e 42 scelte. Il viewport tattile a 390 pixel verifica l'uso dell'interfaccia, senza rappresentare la CPU di un telefono. Nessuna promessa di prestazioni su dispositivo mobile fisico o rallentamento artificiale dei worker.

Le vecchie acquisizioni da cinque scelte restano storiche e non costituiscono l'accettazione finale. I semi riservati ora utilizzati sono evidenza funzionale e prestazionale del rilascio sperimentale, non una valutazione cieca della forza dei mazzi. Il confronto v3/v4 usa la stessa collazione e il giocatore che prende la prima carta visibile. La diagnosi finale condivisa verifica costruzione e proprietà delle carte, senza dimostrare superiorità competitiva.

## Ripresa della review

Il comando per un nuovo giro, senza sovrascrivere il tentativo fallito, è `python reviews/draft-bots-production-20261029/review.py code 6`. Il revisore deve ricevere le evidenze finali e le correzioni successive al quarto giro. Solo una risposta effettiva sulla versione aggiornata può chiudere la review richiesta.

Procedura applicata: [mtg-review](../../.agents/skills/mtg-review/SKILL.md), che richiede: «Se quota, accesso o browser impediscono il controllo, conservare richiesta, esito e parte ancora pendente». Richiesta, risposta e manifest del tentativo interrotto sono conservati.

## Preparazione del push autorizzato

Il controllo finale [push-preflight](push-preflight.json) ricostruisce il sito offline da una copia isolata dei soli file nell’indice Git, con terminazioni LF come nel checkout Linux del workflow. Verifica i byte dei sei sorgenti runtime contro l’indice. Gli hash delle acquisizioni locali precedenti identificano i byte presenti su Windows durante quelle prove; la normalizzazione Git delle terminazioni di riga può cambiare le impronte dei sorgenti. La build calcola le impronte dei byte effettivamente pubblicati. Il preflight conserva l’esito della build e gli hash dell’indice. I file estranei all’attività e la traccia diagnostica integrale timeline.json rimangono locali.
