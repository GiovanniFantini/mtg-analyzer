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

Conservare i seguenti casi di regressione quando si modifica la politica, senza trasformarne i vecchi pesi in vincoli universali:

- A sostegno equivalente, l'ordine degli archetipi nei dati non assegna una preferenza iniziale a un colore o coppia.
- La compatibilità delle magie con costi ibridi usa i simboli effettivamente pagabili; le creature con X non valgono automaticamente come normali giocate iniziali in base al solo valore di mana.
- I supporti di sinergia distinti non vengono moltiplicati contando ripetutamente copie equivalenti della stessa carta.
- I replay compatibili continuano con la politica registrata, anche dopo ripresa ed esportazione. Versioni supportate e default si verificano in `draft-engine.js`, senza fissare per sempre la versione corrente nelle istruzioni.
- Durante il draft, l'esportazione ordinaria non rivela pool e log degli avversari; il resoconto dei bot viene aggiunto dall'interfaccia soltanto a sessione conclusa. Questa protezione dell'interfaccia non è una garanzia contro l'ispezione del codice o della memoria di un simulatore locale.

`verify-draft-bots.cjs` e `verify-draft-bots-browser.cjs` conservano i controlli pertinenti su politica, replay e flussi. Leggere codice e fixture prima di attribuire loro una copertura specifica.

Per scelte sospette o modifiche alla politica usare [mtg-draft-bots](../.agents/skills/mtg-draft-bots/SKILL.md). Per i comandi di verifica usare [verification.md](verification.md).

`node audit-draft-bots.cjs 200 reality-fracture draft mixed 3` simula tavoli completi; l'ultimo argomento seleziona la versione della politica, per esempio `2` per il confronto storico. Ispezionare la destinazione del rapporto prima di eseguirlo, per preservare acquisizioni precedenti. I parametri e il confronto v2/v3 del 22 ottobre sono nel [resoconto datato](history/2026-10-22.md).
