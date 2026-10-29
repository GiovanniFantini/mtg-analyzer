# Motore Draft e qualità dei bot

## Confini del motore

`collation.js` esegue la ricetta del prodotto per Draft e Sealed. `draft-engine.js` gestisce stato, osservazioni, transizioni e politica dei bot senza DOM, rete o salvataggi; `draft-table.js` gestisce l'interfaccia. `build_draft_engine.py` è un adattatore del renderer comune. Gli input attivi sono i documenti dell'espansione, in particolare `products.json`, `limited.json`, `printings.json`, `ratings.json` e `archetypes.json`.

Posti, buste, carte per scelta e versi di passaggio derivano dall'evento. Slot, rarità, coppie, sostituzioni e finiture derivano dal prodotto. Otto posti, tre buste e 14 carte sono un'applicazione specifica, non il contratto universale. Per collazione e dati mancanti vedere [architecture.md](architecture.md).

## Requisiti dei profili

Prima di iniziare, l'utente deve poter assegnare un profilo distinto a ciascun bot. Le strategie hanno priorità, condizioni di cambio piano e costi di rinuncia effettivamente diversi:

- Potenza pura: privilegia il valore individuale della carta, accettando il rischio di un pool incoerente.
- Bomba e costruzione attorno: usa una carta forte come incentivo per colori e supporti, con condizioni esplicite per cambiare piano.
- Lettura dei segnali: accumula indizi dalle buste ricevute e consolida i colori quando il sostegno è sufficiente.
- Archetipo forzato: segue la combinazione scelta prima di iniziare, anche quando è contesa.
- Sinergie: valorizza enabler e payoff in funzione dei supporti già acquisiti e di quelli ancora necessari.
- Aggro e tempo: cerca giocate iniziali, pressione e interazione coerenti con la curva.
- Controllo e vantaggio: cerca risposte, difesa, risorse e condizioni di vittoria sostenibili.
- Fixing e splash: valuta le fonti e i simboli richiesti prima di aggiungere colori.
- Counterpick: confronta il beneficio dedotto di sottrarre una carta con il costo di rinunciare a una propria giocabile; non conosce i pool avversari.

## Stato, informazione e riproducibilità

Le pick precedenti influenzano colori, piano, curva, mana e supporti. Ogni bot conosce soltanto buste e informazioni osservate. Segnali e counterpick sono deduzioni; non accedono a pool avversari o buste future. Il counterpick considera il costo di rinunciare a una propria giocabile.

Un modello markoviano deve esplicitare stato, osservazioni, azioni, transizioni e politica, conservando la memoria necessaria. Le euristiche attuali non sono un modello addestrato o validato sulle partite e non stimano percentuali di vittoria. Le scelte devono essere riproducibili e spiegabili nella revisione finale con esempi di carte dell'espansione.

La versione dell'algoritmo è distinta dall'impronta funzionale dei dati. Conservare la politica originaria dei record compatibili anche dopo ripresa ed esportazione. Non invalidare replay per sole immagini, fonti o testi. Un record incompatibile deve essere salvato integralmente prima di scrivere quello nuovo; se il backup fallisce non sovrascrivere l'originale.

## Indagine e controlli

### Tavolo visuale

Durante il draft il tavolo occupa il viewport: busta in alto, pick impilate per valore di mana in basso e riepilogo laterale. `draft-visual.js` genera soltanto presentazione e conteggi, senza modificare voti, politica o record. La curva usa il valore di mana stampato delle magie; i tipi assegnano una sola categoria principale per carta e i colori contano una multicolore in ciascun colore. Questi conteggi descrivono il pool, non un main già scelto o le fonti di mana. Le pile adattano l'altezza allo spazio disponibile e possono essere ingrandite; gli accumuli più lunghi mantengono lo scorrimento interno. Sul telefono Busta, Pick e Analisi sono viste separate, con immagini più grandi e scorrimento della sola zona di lavoro.

Rarità e copie foil rimangono leggibili nella busta e nelle pile, anche nei nomi accessibili. Le anteprime flottanti evitano la carta di origine e vengono chiuse durante scorrimento, ridimensionamento e ritorno dal dialogo. Il layout a viste vale anche per schermi tattili bassi in orizzontale. La shell coordina `inert` con l'evento `draft-table-mode-change`, mantenendo esclusa la navigazione coperta e ricalcolando il menu all'uscita. Se lo storage non è accessibile, la configurazione permette di esportare e riprendere la sessione ancora in memoria; dopo un errore del worker può ricostruire il suo ultimo record completato senza sovrascrivere record incompatibili privi di backup.

A sessione conclusa il selettore comprende ogni bot e il giocatore. I classici mostrano il pool completo, senza dichiararlo un mazzo costruito. La v4 espone separatamente main proposto, basi da aggiungere, riserve e pool; il riepilogo segue la vista selezionata. Le basi disponibili nel catalogo conservano l'anteprima. Le motivazioni delle singole pick sono raccolte in un dettaglio espandibile. Durante la sessione i pool avversari restano nascosti.

`verify-draft-table-visual.cjs` verifica ingombri del viewport, busta e riepiloghi su desktop, pile, ingrandimento senza scritture, revisione classica, salvataggio, anteprime e viste per telefono. Salva screenshot nella directory temporanea o in `MTG_QA_DIR`. Il flusso completo v4 rimane coperto da `verify-draft-policy-browser.cjs`.

Conservare i seguenti casi di regressione quando si modifica la politica, senza trasformarne i vecchi pesi in vincoli universali:

- A sostegno equivalente, l'ordine degli archetipi nei dati non assegna una preferenza iniziale a un colore o coppia.
- La compatibilità delle magie con costi ibridi usa i simboli effettivamente pagabili; le creature con X non valgono automaticamente come normali giocate iniziali in base al solo valore di mana.
- I supporti di sinergia distinti non vengono moltiplicati contando ripetutamente copie equivalenti della stessa carta.
- Le asserzioni sui pesi e sui bonus della v3, compreso il bonus nullo per copie ripetute di certi esempi, descrivono quella politica e devono indicarne esplicitamente la versione prima di cambiare il default. Le nuove politiche seguono i [requisiti competitivi](requirements.md#qualità-competitiva-dei-bot-draft): distinguono densità e diversità, possono riconoscere sinergie reali fra copie dello stesso nome e non assegnano credito duplicato senza un'interazione effettiva. Questa è una richiesta per l'evoluzione, non un comportamento già implementato.
- I replay compatibili continuano con la politica registrata, anche dopo ripresa ed esportazione. Versioni supportate e default si verificano in `draft-engine.js`, senza fissare per sempre la versione corrente nelle istruzioni.
- Durante il draft, l'esportazione ordinaria non rivela pool e log degli avversari; il resoconto dei bot viene aggiunto dall'interfaccia soltanto a sessione conclusa. Questa protezione dell'interfaccia non è una garanzia contro l'ispezione del codice o della memoria di un simulatore locale.

`verify-draft-bots.cjs` e `verify-draft-bots-browser.cjs` conservano i controlli pertinenti su politica, replay e flussi. Leggere codice e fixture prima di attribuire loro una copertura specifica.

Per scelte sospette o modifiche alla politica usare [mtg-draft-bots](../.agents/skills/mtg-draft-bots/SKILL.md). Per i comandi di verifica usare [verification.md](verification.md).

`node audit-draft-bots.cjs 200 reality-fracture draft mixed 3` simula tavoli completi; l'ultimo argomento seleziona la versione della politica, per esempio `2` per il confronto storico. Ispezionare la destinazione del rapporto prima di eseguirlo, per preservare acquisizioni precedenti. I parametri e il confronto v2/v3 del 22 ottobre sono nel [resoconto datato](history/2026-10-22.md).

## Politica contestuale v4

La nuova politica è selezionabile come `Bot contestuali (sperimentali)` negli eventi con dati minimi pronti. Il default rimane v3. Non è stata dichiarata una forza competitiva o una WR. Adattivo esiste come configurazione interna di riferimento del benchmark; non aggiunge un decimo profilo nell'interfaccia finché il confronto non dimostra una distinzione utile da Lettura dei segnali aggiornata.

`draft-policy.js` implementa la valutazione pura e limitata per piani, separata dal motore storico. `bot_profiles.py` produce i descrittori offline da costi, tipi, caratteristiche e testo Oracle del catalogo. `expansion_data.py` li collega alle stampe attive e all'evento, senza condizioni sul nome del set e senza modificare i voti. La build richiede ancora soltanto Python e i file del repository; Node serve alle verifiche, non alla build.

### Dati, copertura e annotazioni

Il runtime `format.botPolicy` contiene versione dei descrittori, impronta dei dati, impronta dell'algoritmo, disponibilità, lacune, copertura per piano, profili e relazioni. Le proprietà aggiunte non cambiano il contratto storico di `format.revision` usato dai replay v2/v3.

Il profilo minimo descrive ruoli funzionali, simboli da pagare, fonti riconosciute, cycling tipizzato o base, fetch di terre base, eventuale faccia terra alternativa, curva e caratteristiche stampate. Il riferimento editoriale del voto e le relazioni causali non vengono dedotti da una semplice parola o dall'appartenenza a un archetipo. Simboli non supportati, costi compositi con `//` e carte senza costo normale richiedono dati/supporto espliciti prima di abilitare la nuova politica.

Le annotazioni compatibili e facoltative sono in `limited.events.<evento>.botPolicy`, secondo [bot-policy.schema.json](../schemas/bot-policy.schema.json): `schemaVersion: 1`, `match`, `relations`, `planCoverage` e `cards` indicizzate per stampa. Un override riporta stato e provenienza; i descrittori di mana, curva, sinergia e riferimento si uniscono ai rispettivi campi inferiti. Riferimenti per carta possono specificare `reference.support` e `reference.payoffs` per asse, sostituendo il riferimento comune della relazione senza alterare il voto originale.

Una relazione dichiara identità, supporto di riferimento, soglia, saturazione e forza del contributo; può dichiarare una risorsa consumata e relativo budget. I profili riportano quantità di enabler e payoff per asse. Ogni piano dell'evento ha uno stato esplicito con provenienza e relazioni pertinenti. La componente di sinergie è attiva soltanto con copertura completa dei piani, stati delle carte e riferimenti dei voti; una lacuna spegne sia bonus sia penalità nell'intero evento. Il risultato è riportato nel runtime e nelle spiegazioni, non mascherato da un voto medio.

I descrittori minimi sono una classificazione conservativa di funzioni riconoscibili, non un interprete completo di Oracle. Costi, fonti e meccaniche non modellati restano limiti dichiarati. Le relazioni incomplete di Reality Fracture sono disattivate: non sono state inventate annotazioni per esporre una funzione apparentemente completa.

### Mazzo e decisione

Il costruttore esplora un insieme limitato di colori e configurazioni di splash, sceglie un main provvisorio e identifica le carte escluse. Le basi aggiungibili derivano dall'evento e sono considerate insieme allo splash. La dimensione obiettivo è quella minima dell'evento, non una costante universale. Alla fine completa con basi ammesse un main corto, conservando la diagnosi delle magie mancanti; se non può aggiungere basi usa soltanto carte possedute, con segnalazione dei ripieghi e dei buchi ancora impossibili da colmare. Rispetta il limite di copie quando previsto.

La qualità marginale confronta il mazzo dopo la carta con il migliore piano precedente, usando la stessa prospettiva temporale e lo stesso contributo dei segnali. Le carte del main conservano il valore assoluto: la media del loro colore nel catalogo non viene sottratta. Soltanto i posti scoperti ricevono un valore di riempimento atteso, derivato da qualità e massa delle marginali pubbliche per ruolo e colore, pick restanti e un fattore prudenziale dichiarato di 0,35. A draft concluso questa attesa vale zero. Esclusioni e dipendenze della collazione sono approssimate solo per queste attese, mentre le buste continuano a usare la ricetta originale. Posti futuri da riempire sono conteggi, mai carte che il bot conosce in anticipo.

I contributi di sinergia sono scarti dal sostegno di riferimento, con valore di opzione iniziale limitato dalla disponibilità attesa e dalle pick restanti. Copie e varietà sono distinte; payoff che consumano la stessa risorsa se ne dividono il budget. Gli enabler ricevono valore anche dai beneficiari presenti. Nei dati parziali questo intero contributo resta zero.

Le fonti vengono valutate al turno pertinente: colori per lanciarle, costo di attivazione, rapidità, ingressi tappati e terre effettivamente ricercabili nella configurazione. Landcycler che competono per poche terre si dividono il contributo. Facce terra e cycling conservano un solo slot e un contributo frazionario alternativo alla minaccia; non contano come due carte. Fonti condizionate non riconosciute non diventano fonti universali. I costi ibridi usano insiemi di fonti pagabili senza contare due volte una terra doppia.

Le stime di accesso al mana usano code ipergeometriche con interpolazione per fonti indirette frazionarie e vincoli di pagamento approssimati separatamente. Gli splash possono usare basi aggiungibili anche senza fixing posseduto; il controllo di accesso ammette fino a due turni di ritardo, mentre il punteggio misura il rischio al turno nominale, senza regalare pescate aggiuntive al solo colore chiamato splash. Terre possedute e basi aggiungibili competono per gli stessi posti. L’allocazione usa il guadagno marginale della somma dei voti pesati per accesso ai simboli al turno della carta, compresi i costi ibridi. Una seconda passata include le fonti indirette stimate dalla prima configurazione; il punteggio e il controllo finale ricalcolano sempre le fonti effettive. Questa approssimazione limitata non è una ricerca esaustiva. Tutti i colori richiesti ricevono lo stesso avvio prudenziale, con fonti già possedute, doppi simboli e tempi delle terre tappate; una rifinitura limitata scambia le basi soltanto se migliora quel surrogato. Il risultato viene riusato solo per richieste funzionalmente identiche. Tutti i colori fuori piano pertinenti sono candidati. Uno slot solo fixing privilegia le fonti dei colori che deve sbloccare; il confronto marginale conserva sempre la possibilità di mantenere la configurazione precedente. Non sono inclusi mulligan o simulazione completa dei turni; le stime non sono WR. Le riduzioni di costo riconosciute dipendono da risorse plausibili del proprio main e non creano automaticamente una giocata iniziale garantita.

I segnali conservano memoria per verso di passaggio e confrontano qualità e profondità residue con un'attesa pubblica dichiarata. Il ritorno della stessa busta e le scelte multiple nello stesso turno non generano osservazioni indipendenti. Nessun pool avversario o busta futura entra nell'evaluator. Fase e cambi di piano seguono progresso, confidenza e mazzi costruibili, senza il costo affondato delle pick già spese. Un miglioramento di un piano alternativo vicino conserva un valore di opzione anche prima di superare il piano corrente: contributo limitato a 0,35, pesato per distanza fra i piani risultanti e pick restanti, nullo all'ultima pick. Il piano già realizzato non riceve nuovamente questo credito. Sono pesi euristici, non probabilità calibrate.

Aggro privilegia pressione e giocate iniziali, Controllo difesa e risposte. Bomba mantiene un incentivo soltanto se l'ancora resta nel main. Segnali dà più peso agli indizi e mantiene più a lungo piani alternativi; Fixing accetta configurazioni aggiuntive solo col mana verificato. Potenza pura rimane il controllo individuale. Counterpick non prevale su un miglioramento proprio o una riserva utile di sideboard; il beneficio dedotto rimane limitato e incerto. BO1 non attribuisce valore al sideboarding; BO3 è l'assunzione predefinita dichiarata del nuovo valutatore.

Pick-Two usa una ricerca limitata sulle combinazioni della stessa busta e registra la motivazione congiunta. Il modello non promette l'ottimo combinatorio. Il sorteggio è ristretto a copie della stessa stampa con uguale funzione nel piano: un punteggio vicino non rende intercambiabili carte diverse. La modalità API `deterministic: true` elimina quel sorteggio.

### Replay e spiegazioni

```javascript
DraftEngine.createSession(format, seed, configs, 4, {match: 'BO3', deterministic: false});
```

Ogni sessione ha una sola versione. I record storici mantengono formato ed estrazione originari; i nuovi record hanno `version: 3`, `engineVersion: 4`, `randomSchema: 'seat-pick-v1'`, opzioni, `policyRevision` e `algorithmRevision`. Il confronto fra versioni avviene su sessioni diverse con impronte delle buste verificate. Collazione e RNG storici restano invariati; la nuova scelta ha flussi derivati da seme, posto, giro e pick. Le transizioni v4 sono deterministiche, quindi non consumano il flusso della scelta.

L'impronta dei dati include soltanto i descrittori funzionali e le regole usate dalla politica. Immagini, provenienza e testi esplicativi del riferimento non la cambiano. L'impronta dell'algoritmo protegge anche i salvataggi sperimentali da reinterpretazioni dopo modifiche del codice. Un record incompatibile passa per lo stesso backup integrale già presente; un backup fallito impedisce di sostituire l'originale.

A draft concluso `finalBuild` sceglie il main fra tutti i piani sul solo valore del pool completo, senza segnali o ancora del draft; Archetipo forzato mantiene il vincolo richiesto. La revisione mostra magie, terre possedute, basi da aggiungere, carte usate solo come fixing, fonti, alternative, migliore stimata, eventuale sorteggio o combinazione, busta osservata, pool precedente, carte sostituite e lacune. Il turno utile di accesso al mana è distinto dal numero di fonti richieste dal costo. Le anteprime sono delegate anche per i nuovi contenuti. L'esportazione in corso contiene soltanto il record del giocatore e non i pool/log dei bot.

### Verifiche e confronto

`tests/fixtures/draft-policy-v4-cases.json` conserva aspettative, rubriche e semi separati prima dell'implementazione. `tests/fixtures/draft-bots-v3.json` congela digest storici oltre alle fixture v2 già presenti. `verify-draft-policy.cjs`, `verify-draft-policy-regressions.cjs`, `test_bot_profiles.py` e `verify-draft-policy-browser.cjs` verificano i nuovi contratti, le correzioni della review e i flussi; usare anche la suite pertinente di [verification.md](verification.md).

`node benchmark-draft-policy.cjs training` usa soltanto i semi di taratura. `reserved` usa i casi riservati e produce input anonimi e mappa separata per la revisione. Ogni acquisizione conserva impronte di codice, fixture, dati, buste, record e sorgenti della politica; non sovrascrive risultati già registrati. Il costruttore diagnostico finale è identico per tutte le politiche: le sue metriche sono coerenza interna, non prova indipendente di forza. La [relazione di implementazione](../reviews/draft-bots-implementation-20261029/report.md) distingue verifiche, confronto, revisione cieca e limiti effettivi.

### Reattività del tavolo v4

All’apertura vengono controllati intestazione, opzioni e impronte del salvataggio; la ricostruzione v4 parte soltanto premendo Riprendi, mostra l’avanzamento e può essere annullata. Un record non ancora ricostruito viene comunque conservato integralmente prima di sostituirlo con un nuovo draft. Nel browser la v4 calcola pick, replay e liste finali in `draft-worker.js`, tramite `draft-worker-client.js`. La UI conserva soltanto snapshot completati e blocca i comandi di modifica durante una mossa. Anteprime e navigazione della pagina restano disponibili durante il calcolo. Il worker non accede a salvataggi o DOM. Un errore termina quel worker e conserva lo snapshot precedente esportabile; nessuna mossa incompleta viene salvata. Le liste finali sono memorizzate per posto nel worker. Il costo CPU della ricerca e della ripresa resta una misura distinta dalla reattività della pagina.

Il worker verifica i byte dei tre sorgenti contro `algorithmRevision` prima di eseguirli e usa URL con revisione. Un caricamento incoerente viene rifiutato senza sovrascrivere salvataggi. Il selettore avverte che un aggiornamento può impedire la continuazione della v4 sperimentale; l’archivio degli eseguibili storici non è implementato. Gli eventi con più scelte per turno rimangono utilizzabili nel banco diagnostico, ma non espongono v4 nel browser finché i tempi non sono verificati. Il completamento futuro delle annotazioni causali richiede anche la misura della componente attiva.

Per le mosse v4 il worker principale distribuisce solo stato proprio e busta osservata di ciascun bot a un numero limitato di worker ausiliari (massimo quattro). Il limite riserva due CPU logiche indicate dal browser al resto del lavoro, mantenendo comunque almeno un worker. `stepAsync` valida i risultati prima di applicarli nell’ordine dei posti e riusa la stessa transizione sequenziale. Errori o risultati non coerenti non modificano lo stato completato. `workerRevision` versiona separatamente il trasporto e il codice della revisione, senza rendere compatibili algoritmi differenti. La lettura delle buste future resta esclusa dal valutatore.

I log completi rimangono nel worker fino all'esportazione, che viene serializzata nello stesso worker. L'interfaccia riceve riepiloghi e carica la revisione del solo bot selezionato, senza trasferire le copie dei mazzi intermedi che non visualizza. L'export mantiene tutti i log originali; il record di ripresa rimane leggero. Dopo un errore del worker resta esportabile il record dell'ultimo stato completato.

La [review tecnica del 29 ottobre](../reviews/draft-bots-production-20261029/report.md) conserva correzioni, misure ed eventuali approvazioni pendenti. Il protocollo di latenza sperimentale misura 126 scelte predefinite su tre semi sul desktop, con p95 entro 5 secondi; le 42 scelte Potenza pura sono un controllo separato. I test a 390 pixel coprono il funzionamento con tocco, senza simulare la CPU di un telefono. La promozione a default richiede evidenze competitive ulteriori.
