---
name: mtg-research
description: Ricercare e integrare aggiornamenti, recensioni, statistiche per carta e prospettive di gioco o prezzo delle espansioni MTG. Usare anche per aggiornare il valore di un box.
---

# Ricerca e arricchimento MTG

## Scegliere il percorso

- Aggiornamenti e recensioni: seguire il flusso comune e la sezione Recensioni.
- Statistiche per carta: leggere `docs/statistics.md` per il contratto e le definizioni.
- Prospettive complete: applicare la sezione Analisi complete; leggere `docs/economics.md` per i valori economici.
- Prezzi o box: leggere `docs/economics.md`. Per il box personale Reality Fracture leggere anche `docs/local/reality-fracture-box.md`, se presente.
- Consultazione per legalità: leggere `docs/requirements.md`; verificare se la vista richiesta esiste prima di descriverne il percorso.

I percorsi sono relativi alla radice del repository. Caricare soltanto i riferimenti pertinenti. Per cambiare il contratto leggere `docs/architecture.md`.

Per integrare analisi e prezzi leggere anche la sezione Analisi per carta e prezzi di `docs/architecture.md` e `schemas/prospects.schema.json`: i dati risiedono in `cards[].prospects`, con copertura dei riferimenti in `prices.json.references`. Per valutare l'idoneità al prodotto durante un'anteprima non usare il solo flag Scryfall `booster`; verificare fonti ufficiali, composizione e trattamenti del prodotto.

## Flusso comune

1. Partire dai JSON attivi e dagli snapshot più recenti, distinguendo copertura del catalogo, stampe, prodotto, evento e formato di gioco. Confrontare le nuove informazioni con quelle già presenti: novità, conferme e informazioni storiche ritrovate sono esiti diversi.
2. Cercare fonti ufficiali per annunci, meccaniche, date, prodotti, collazione, regole e legalità. Leggere anche testate specialistiche, autori delle anteprime, recensori e analisti pertinenti. Un link indicato come esempio è un punto di partenza. Ampliare la ricerca significa leggere e confrontare, non elencare siti.
3. Conservare URL, autore se disponibile, date di pubblicazione e acquisizione, contesto e copertura. Distinguere pagina letta, dato acquisito e informazione visibile solo nell'indice. Verificare nel browser tabelle dinamiche, paginazione e scorrimento virtuale quando il lettore web non basta; rispettare i limiti d'accesso e dichiarare ciò che resta indisponibile.
4. Per richieste di estrazione o aggiornamento di ogni carta, acquisire e abbinare sistematicamente le osservazioni all'intero catalogo pertinente, ospiti comprese. Controllare identità stabili, duplicati, varianti, corrispondenze, anomalie e copertura per metrica. Pochi esempi o la conferma che la fonte esiste non completano l'estrazione.
5. Se è richiesto l'aggiornamento del repository, salvare acquisizioni datate, provenienza e importazione riproducibile; integrare osservazioni sostanziali nei JSON appropriati. `sources.json` conserva provenienza, `sentiment.json` osservazioni e sintesi, `guides.json` contenuti e sequenze, `statistics.json` misure osservate. Riutilizzare campi equivalenti e preservare estensioni compatibili. La build resta offline.
6. Verificare le modifiche pertinenti con `docs/verification.md`. Dichiarare catalogo coperto, lacune, dati salvati, interfaccia aggiornata ed eventuale pubblicazione effettivamente verificata. Acquisire dati non modifica automaticamente modelli di valutazione o UI.

## Recensioni e ranking

Cercare separatamente ranking numerici e analisi qualitative, comprese recensioni parziali e senza voto. Registrare autore, data, carte trattate e contesto: Draft, Sealed, Standard, altri Constructed o Commander. Conservare scala e metodo dei punteggi, segnalando contraddizioni e campioni mancanti.

Verificare le argomentazioni contro Oracle e, quando necessario, fonti ufficiali: costi, bersagli, restrizioni, frequenza di attivazione, interazioni e legalità. Correggere errori concreti e precedenti valutazioni proprie troppo fiduciose, spiegando quali conclusioni restano utilizzabili.

Mantenere distinti risultati osservati, punteggi automatici, opinioni attribuite e giudizi editoriali propri. Popolarità e inclusioni non dimostrano prestazioni; un commento Commander o un punteggio Constructed non diventa un voto Limited o un peso dei bot. Usare `ratings.json` soltanto per valutazioni Limited coerenti con la scala del progetto. Una data recente dell'articolo non prova che il suo catalogo sia aggiornato.

## Analisi complete di utilizzo e valore

L'esito deve aiutare a decidere cosa giocare, osservare o vendere. Coprire l'intero catalogo pertinente quando è richiesto ogni carta, incluse le ospiti; trattare Commander in un'appendice distinta, esclusa dai pool Limited. Usare almeno dieci editori o servizi distinti e affidabili per uno studio esteso dell'espansione, non dieci pagine dello stesso editore né dieci fonti per carta. Per i prezzi resta esclusivo Cardmarket.

Per ogni carta distinguere Oracle e interazioni, ruolo e sinergie, legalità nei formati di gioco, adozione documentata e giudizio editoriale. Standard, Pioneer, Modern, Legacy, Vintage, Pauper, Commander e cEDH sono contesti di gioco, non l'espansione selezionata o l'evento Limited. Dichiarare dove mancano prove; legalità, inclusioni e risultati non sono equivalenti. Conservare date e fonti per le previsioni di ammissibilità all'uscita.

Nel contesto del sito rendere ogni analisi consultabile con accesso evidente, ricerca, filtri e dettagli per formato, prezzi e fonti. Una selezione editoriale affianca la vista completa. Mantenere esempi concreti delle carte anche su telefono e nelle versioni condivisibili. Per il requisito e le viste ancora mancanti vedere `docs/requirements.md`. Non aggiungere automaticamente confronti avanzati o altri ampliamenti al perimetro richiesto.
