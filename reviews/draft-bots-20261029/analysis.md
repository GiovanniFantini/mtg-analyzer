# Analisi competitiva dei bot Draft, 29 ottobre 2026

Questo rapporto conserva la diagnosi iniziale. Le formulazioni progettuali sono state poi riesaminate con Opus: per la specifica corrente vedere [requisiti BOT](../../docs/requirements.md#qualità-competitiva-dei-bot-draft) e [registro delle decisioni](../draft-bots-opus-20261029/decisions.json), in particolare per landcycling, valore di opzione e ordine di lavoro.

## Giudizio

La v3 è una base euristica utile per esercitarsi contro avversari con preferenze diverse. Non basta ancora per rappresentare un tavolo di giocatori esperti: protegge la qualità individuale, ma non ricostruisce il mazzo che ogni pick dovrebbe migliorare. La lacuna principale è il valore contestuale delle carte, soprattutto sinergie, mana e necessità del main deck.

Raccomandazione: correggere il motore condiviso e aggiungere un profilo Adattivo competitivo che ragioni sul mazzo costruibile. Conservare i profili attuali come specialisti o controlli. Rifare da zero collazione, tavolo e replay non è giustificato dalle evidenze raccolte. Aggiungere soltanto un decimo insieme di pesi non risolve i problemi.

Questa attività produce analisi, baseline e requisiti. Nessuna modifica alla politica, ai voti, ai dati delle espansioni, all'interfaccia o alla pipeline; nessun commit o push. I requisiti da implementare sono in [docs/requirements.md](../../docs/requirements.md#qualità-competitiva-dei-bot-draft).

## Metodo e copertura

Revisione del repository: `3902b300db4a096769e6ce1c9cbdcb1b80c63d72`. Il [manifest](input-manifest.json) registra runtime e SHA-256 dei sorgenti e dei dati pertinenti. Lo [snapshot](formats.json) conserva i campi usati dall'evaluator per tre cataloghi; i conteggi riguardano stampe nel runtime, non carte uniche né copertura di un prodotto.

- 80 tavoli Reality Fracture Draft, 8 posti, 3 buste da 14, una carta per scelta. Semi `bot-audit-0` fino a `bot-audit-79`. Sette bot con profili diversi, un posto per profilo fisso: signals, bomb, synergy, aggro, control, fixing, denial. Totale 23.520 pick dei bot.
- 20 tavoli con sette bot Potenza pura, stessi primi 20 semi e dati: 5.880 pick.
- 10 tavoli con sette bot Archetipo forzato WU, semi `bot-force-audit-0` fino a `bot-force-audit-9`: 2.940 pick. È uno stress test con contesa intenzionale, non una misura di forza del profilo.
- Totale: 110 tavoli completi, 770 pool di bot, 32.340 pick dei bot. Ogni sessione controlla conservazione delle carte e replay identico.
- Giocatore simulato fisso: Lettura dei segnali v2, RNG separato con suffisso `-human`. È un controllo riproducibile, non un giocatore umano esperto.
- Prove sintetiche separate per isolare sinergia, fonti inaccessibili, memoria dei segnali e transizioni. Non sono carte reali, simulazioni di partite o osservazioni su tornei.

Nel registro di [disponibilità](availability.json), Reality Fracture è l'unico set con `draftTable.available=true`, su 21 espansioni registrate. Il primo tentativo di estendere l'audit a Bloomburrow si è fermato per collazione assente; non è stato completato alcun tavolo di quel set. Foundations e gli altri set non sono stati simulati. Pick-Two Star Trek ha un runtime senza carte e non è un evento utilizzabile per questo benchmark. Non sono state inventate buste per aggirare questi limiti.

Il benchmark non confronta forza in partita e non copre rotazione dei profili fra i posti, tutti gli archetipi forzati o tutti gli eventi. Gli 80 tavoli misti non sono indipendenti dai primi 20 tavoli Potenza pura: condividono intenzionalmente il seme e la collazione. Non è stato eseguito un confronto prima/dopo perché non è stata cambiata la politica.

## Cosa funziona già

Il motore distingue politica v2/v3, ha replay deterministici e non consulta pool avversari o buste future durante la valutazione. Usa memoria delle proprie pick, osservazioni delle buste, una fase e un piano di colori. La v3 limita i bonus tattici, gestisce diversi costi ibridi e riconosce alcune fonti di mana e landcycling.

Nei tavoli misti, 0 casi segnalati su 386 pick con almeno una rara/mitica da voto 4,5 o più interamente nei colori registrati: nessuna è stata passata per una magia inferiore di almeno un punto. Distribuzione delle occasioni: signals 65, bomb 65, synergy 55, aggro 41, control 50, fixing 54, denial 56. Potenza pura: 0 su 56 occasioni.

Questa misura rileva soltanto una famiglia stretta di anomalie rispetto ai voti presenti. Usa i colori dichiarati, non la piena pagabilità degli ibridi; esclude alcune scelte di terre e non valida i voti stessi. Non dimostra che tutte le altre pick siano corrette, che le rare siano bombe reali o che i mazzi siano forti.

## Lacune confermate e implicazioni di gioco

### 1. Manca un mazzo provvisorio

`context()` somma sostegno delle carte nel pool per coppia; `rankModern()` conta tutte le magie pagabili in quella coppia. Non seleziona un main deck e non identifica quale carta verrebbe sostituita. Un ventottesimo riempitivo può aumentare il sostegno al piano e incidere sulla curva pur non entrando mai nella lista.

Per un drafter esperto la domanda decisiva è: questa carta risolve un problema del mazzo o migliora uno slot che giocherò? Occorre distinguere qualità astratta, carta giocabile e miglioramento del main. Il conteggio delle creature nel pool non basta.

### 2. La sinergia è appartenenza a una lista editoriale

Il bonus usa `card.archetypes.includes(lane)` e il numero di nomi diversi con la stessa etichetta, fino a 0,35 prima del peso. Non verifica una relazione fra gli effetti delle carte. Cambiare il testo di un supporto sintetico da guadagno di vite a vigilance lascia identico il contributo di sinergia al payoff da lifegain: 0,126 nel profilo Sinergie.

Una o otto copie di quel supporto producono lo stesso contributo di sinergia, sempre 0,126; il totale cambia per la curva. La correzione storica che impedisce di moltiplicare ripetutamente lo stesso supporto è utile, ma non deve cancellare la densità reale. Copie e diversità sono due misure diverse.

Il tetto condiviso di 0,45 ai bonus tattici positivi impedisce di riconoscere combinazioni molto più forti della somma dei voti autonomi. È una protezione contro vecchi eccessi, non un modello di valutazione contestuale. Serve una stima del payoff supportato con limiti dichiarati, non alzare indiscriminatamente i pesi.

### 3. Le fonti di mana possono essere soltanto nominali

La prova sintetica dà a un bot WU due creature verdi da sei mana con abilità che produce mana di qualsiasi colore. Senza fonti verdi per lanciarle, queste carte riducono comunque la penalità di una bomba rossa da -2,64 a -0,264: il contributo del colore migliora di 2,376 senza una base di mana funzionante. La magia resta `playable:false` nel risultato dell'evaluator: autorizzazione dello splash e definizione di giocabile sono inoltre due valutazioni disallineate.

Il riconoscimento testuale non modella accessibilità, velocità, restrizioni o uso alternativo. Due landcycler non equivalgono automaticamente a due terre: richiedono mana e vengono scartati. Il mazzo deve scegliere fra la creatura e il fixing nello stesso impiego della carta.

### 4. I segnali non mantengono una memoria per lato

Le osservazioni sono conservate per numero di busta. `context(bot,3)` legge soltanto `signals[3]`, quindi non recupera direttamente `signals[1]` quando il verso torna uguale. Il pool e il piano mantengono indirettamente l'effetto delle pick precedenti; non si tratta di amnesia completa.

Il contributo osservato usa soprattutto il miglior voto per colore nella busta e il numero della pick. Mancano una stima esplicita della confidenza, la separazione della lettura per lato e il valore del wheel come prova distinta. In Pick-Two le due chiamate a `take()` osservano la stessa busta nello stesso turno: una futura politica deve evitare di trattarle come evidenze indipendenti.

### 5. Fasi casuali e soglie non spiegano il costo del pivot

Lo stato ha una catena di transizioni pesate, condizionata dal progresso; non è un modello addestrato di abilità competitiva. La fase influisce molto sull'impegno nei colori. In 500 prove sintetiche con 28 pick già fatte, partendo da esplorazione, la successiva estrazione resta in esplorazione 46 volte e passa a orientamento 51. Questo esperimento condizionato non misura la frequenza dello stesso stato nei tavoli completi.

L'ancora del profilo Bomba è la prima magia non terra con voto almeno 4. Il costo di abbandonarla è una soglia nel sostegno alle coppie; non rappresenta quante carte si perdono né quali supporti servono. Un build-around e una bomba autonoma richiedono decisioni diverse.

### 6. Ruoli e curva sono approssimazioni troppo uniformi

Rimozione e vantaggio dipendono da parole in `role`; aggro privilegia soprattutto mana value basso; la soglia delle creature economiche è condivisa. Mancano qualità offensiva/difensiva, tempi delle risposte, costo di attivazione, requisiti di bersaglio, riduzioni di costo e conversione del vantaggio in vittoria.

La copertura del runtime esaminato è 411/411 stampe con ruolo e 56/411 con etichetta di archetipo per Reality Fracture; 258/407 e 11/407 per Bloomburrow; 0/781 e 21/781 per Foundations. Questi ultimi cataloghi non attestano completezza del prodotto. Sono un avvertimento per il riuso futuro, non una diagnosi di bot oggi disponibili per quei set. Un motore migliore non può ricostruire automaticamente tutti i dati mancanti dalle descrizioni del set.

### 7. Il counterpick misura poco il costo della rinuncia

L'attivazione confronta soprattutto il miglior voto base giocabile con 2,7, nella parte tarda del draft e della busta. Il beneficio di negazione deriva da domanda cumulativa dei colori al wheel. Non confronta miglioramento del proprio main o sideboard e danno plausibile a un avversario. L'informazione disponibile è correttamente parziale: questa limitazione va conservata.

## Tre decisioni concrete da interpretare

Tavolo `bot-audit-0`, esportazione e pool integrali in [example-table.json](example-table.json). I testi citati sono quelli dello snapshot locale; questa analisi non certifica un aggiornamento Oracle alla data del rapporto e non introduce nuovi ruling.

1. Sinergie, B3P4: terza Undulating Witness invece di Proft, Consulting Detective. Il pool precedente contiene già due Witness, Mindseeker Oculus e due Infinite Coursework. Le alternative registrate danno Proft a 5,229 e Witness a 5,139; vince la casualità ammessa entro 0,2. Entrambe hanno bonus di sinergia nullo perché prive dell'etichetta pertinente. Non è dimostrato che scegliere Witness sia sbagliato: vola e può ciclarsi per una base. Il problema è che il bot non confronta il motore scry/surveil di Proft, il mana aggiuntivo richiesto per usarlo e il valore marginale della terza Witness. La spiegazione attuale non permette di attribuire la scelta a quel ragionamento.
2. Controllo, B3P3: Craftwork Crusher sopra Compel Brutality, con Verdant Kraken, Kiora of Fire and Ashes e Ghalta the Unstoppable già nel pool. Crusher costa sette con due simboli rossi e due verdi; Compel costa due ma richiede una propria creatura o planeswalker adatto. Il voto 4 contro 3,5 favorisce Crusher. Non è automaticamente un errore: Crusher produce impatto e risorse, e Ghalta ha una riduzione. Il bot dovrebbe però spiegare quanto manca alla stabilizzazione iniziale e se un'altra chiusura migliora davvero il main. Non lo può stabilire contando il mana value e parole nel ruolo.
3. Counterpick, B3P11: Last Gasp viene tolta da un bot WR. Alternative: Theoretical Necromancer, Rampart Hunter e Forest, tutte fuori piano. Il counterpick è plausibile e non sacrifica una propria magia pagabile. È un caso positivo da conservare; vedere una rimozione nera nel pool finale non dimostra da solo uno splash sbagliato.

## Decisione sul nuovo bot e criteri di confronto

Serve una politica adattiva che integri le capacità ora separate, invece di imporre una preferenza permanente per potenza, curva o sinergia. Conviene esporla come profilo aggiuntivo, senza sostituire gli specialisti o duplicare il motore. I requisiti BOT-01..14 e lo stato proposto sono nel documento dei requisiti.

L'ordine suggerito è dati e mazzo provvisorio, mana e sinergie, valore marginale, lettura dei segnali e pivot, poi validazione della politica adattiva. Il primo risultato misurabile deve essere risolvere controesempi strategici mantenendo replay e conservazione. Per giudicare i pool serve una lista costruita, non soltanto numero di carte nei colori o voto medio.

La validazione deve ruotare i posti, usare gli stessi semi, distinguere tavoli misti e omogenei e includere casi speculari e ordine dei dati permutato. Un insieme di scelte etichettate e motivate da un drafter competente può misurare accordo e disaccordi; non diventa una verità universale su tutte le pick. Il giudizio sui mazzi resta separato dai risultati di eventuali partite. La v3 non può essere dichiarata più debole in percentuale rispetto al profilo proposto: quel profilo non è implementato e non sono state giocate partite.

## Riproduzione e verifiche

Dalla radice del repository, con Python e Node disponibili:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python reviews/draft-bots-20261029/capture-inputs.py
node reviews/draft-bots-20261029/run-audit.cjs
node reviews/draft-bots-20261029/probes.cjs
```

I comandi riscrivono soltanto gli output di questa cartella datata; copiarla prima di una nuova acquisizione da conservare. Il wrapper verifica il percorso del vecchio audit e cambia soltanto la cartella di output in memoria, preservando i rapporti del 22 ottobre. Prima di confrontare esecuzioni verificare il manifest dei dati. Le prove sintetiche descrivono i limiti della v3 e non vanno promosse a test che impongano il mantenimento dei difetti.

Le simulazioni e i replay controllati sono passati. Per i soli documenti e strumenti diagnostici aggiunti non è stata eseguita la suite browser o di pubblicazione. Questi controlli restano obbligatori per la successiva implementazione secondo [verification.md](../../docs/verification.md).

## Fonti strategiche consultate

Queste fonti sostengono i criteri di valutazione; le lacune del software sono dimostrate dal codice e dalle prove locali, non dedotte dagli articoli.

- Reid Duke, [Signals in Booster Draft](https://magic.wizards.com/en/news/feature/signals-booster-draft-2015-01-19), 19 gennaio 2015, consultato il 29 ottobre 2026. Segnali come indizi cumulativi e scelte influenzate da qualità e flessibilità; l'articolo non fornisce soglie universali per i bot.
- Reid Duke, [Booster Draft, Part 3](https://magic.wizards.com/en/news/feature/booster-draft-part-3-2015-02-02), 2 febbraio 2015, consultato il 29 ottobre 2026. Costo e tempo residuo di un cambio di colori; le finestre descritte sono orientamenti nel contesto dell'articolo.
- Reid Duke, [The Basics of Booster Draft](https://magic.wizards.com/en/news/feature/basics-booster-draft-2015-08-03), 3 agosto 2015, consultato il 29 ottobre 2026. Sinergia tra carte e piano complessivo del mazzo.
- Reid Duke, [Building a Mana Base](https://magic.wizards.com/en/news/feature/building-mana-base-2014-11-24), 24 novembre 2014, consultato il 29 ottobre 2026. Necessità dei colori e costruzione congiunta di magie e fonti. Le indicazioni numeriche non sono state trasformate in regole rigide né in probabilità di vittoria.
