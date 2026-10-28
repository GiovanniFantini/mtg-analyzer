# Lettura delle sinergie del pool, 28 ottobre 2026

## Modifiche

- L'assistente mostra `Come funziona il pool`, con collegamenti fra guadagno di vite e beneficiari, selezione e ricompense, accesso ad abilità di lealtà e condizioni di attacco. Le carte citate hanno anteprime dinamiche.
- Conta separatamente carte preparate, creazione di pedine creatura e flashback, senza sommarli alle creature iniziali.
- Elenca cicloterra base, produttori di mana di qualsiasi colore e simboli fuori piano. La faccia principale e i costi ibridi guidano il controllo; non viene certificata automaticamente la sostenibilità dello splash.
- Il prompt esportabile richiede una valutazione del percorso fra sviluppo, stabilizzazione, risorse e chiusure, del ruolo delle bombe e dei costi effettivi del fixing. Richiede di distinguere liste proposte e giocate e contesti Quick, Premier e Traditional.
- Nessuna modifica a voti, win rate, politiche dei bot, replay o formato dei salvataggi. Nessun risultato personale importato nei dataset. Il riconoscimento Oracle rimane parziale ed esplicito.

Il contratto e i limiti sono descritti in [architecture.md](../architecture.md#lettura-delle-sinergie-del-pool).

## Verifiche

- `python build_site.py`: riuscita, due espansioni e collegamenti locali verificati.
- `python -m unittest test_draft_assistant.py`: tre test riusciti, compresa la conservazione dell'Oracle canonico.
- `node verify-pool-analysis.cjs`: riuscito. Comprende modi alternativi, reminder, quantità, costi ibridi e doppi, fixing, risorse future, carte fuori piano e dati mancanti.
- `node verify-pool-analysis-browser.cjs`: riuscito con Edge e sito servito da `dist/`. Verificati aggiornamento dinamico, anteprime con mouse, tastiera e tocco, larghezze 320/390/768/1440, apertura del pannello senza scritture sui salvataggi e contenuto del prompt. Screenshot desktop e telefono ispezionati in una cartella temporanea dedicata.
- Controllo sintattico JavaScript e `git diff --check` sui sorgenti coinvolti riusciti.
- Suite combinata Python: 35 test, due errori in `test_correlated_exclusions_are_not_rejected_by_upper_bounds` e `test_pair_unique_counts_use_actual_pair_members`. Entrambi riprodotti caricando in memoria `build_expansion.py` da HEAD, mantenendo l'`expansion_data.py` del workspace, non modificato da questa attività. La suite completa non è verde.
- `verify-draft-assistant.cjs`: non concluso con successo. Un'esecuzione si ferma per timeout passando alla vista pool; una seconda arriva al caso di storage negato e segnala `DraftPool is not defined`. Questi esiti non sono presentati come verifiche riuscite né risolti in questa attività.

Modifiche locali, senza commit, push o pubblicazione. Conservate le modifiche già presenti nel workspace.
