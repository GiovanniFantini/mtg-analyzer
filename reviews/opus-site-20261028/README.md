# Review Opus del 28 ottobre 2026

Il ciclo non è ancora concluso. Opus 5.5 ha completato cinque giri; il sesto tentativo è stato rifiutato per il limite di sessione di Claude. Il ripristino comunicato è alle 16:50, ora di Roma. Non esiste un responso finale a zero segnalazioni.

## Esiti verificati

| Giro | Modello effettivo | Segnalazioni | Esito |
| --- | --- | --- | --- |
| 1 | claude-opus-5-5 | 5 | Confermate e corrette |
| 2 | claude-opus-5-5 | 6 | Confermate e corrette; riprodotta anche l'ipotesi sugli spareggi |
| 3 | claude-opus-5-5 | 4 | Tre confermate; una parzialmente fondata, corretta per il caso reale senza JavaScript |
| 4 | claude-opus-5-5 | 5 | Confermate e corrette |
| 5 | claude-opus-5-5 | 4 | Confermate e corrette |
| 6 | Nessuna esecuzione del modello | Nessun responso | Limite di sessione |

Le decisioni e le riproduzioni sono in [decisions.json](decisions.json). Gli hash degli input, delle risposte e dei sorgenti correnti sono in [manifest.json](manifest.json). Prompt e risposte integrali restano nei registri locali esclusi da Git. Nessun commit, push o intervento sulla pipeline.

## Correzioni principali

- Protezione dei pool e delle simulazioni Sealed incompatibili: originale scaricabile, backup integrale verificato prima della sostituzione e blocco se il backup fallisce.
- Memoria non accessibile distinta da un record incompatibile, senza affermare l'esistenza di un salvataggio precedente.
- Percorsi corretti fra catalogo, banco manuale e viste condivise; selezione degli eventi limitata al tipo della pagina e mantenuta al ricaricamento.
- Chiavi isolate anche per il simulatore attivato in una presentazione di anteprima; osservate compatibili fra ID e nomi, mantenendo i token sconosciuti.
- Ricerca per tipo e sottotipo indipendente dal formato Oracle; testo Oracle visibile anche senza facce separate; anteprime disponibili dopo il caricamento dei dati.
- Attribuzioni statistiche condizionate ai dati effettivi; contenuti editoriali di Reality Fracture conservati nei dati del set; avvisi non duplicati.
- Torneo: risultati non salvati conservati durante gli aggiornamenti degli altri tavoli, chiusura anticipata dopo ritiri e parità correttamente riconosciute negli spareggi.
- Inventario delle fonti separato per slug completo, compresi i suffissi degli audit.

È stata inoltre riprodotta e corretta l'assenza del catalogo necessario alle anteprime nella guida Sealed condivisa.

## Verifiche locali

Build offline e collegamenti di 22 pagine, 47 test Python, 19 fixture browser per espansioni alternative, simulazioni e replay Draft/Sealed, torneo completo desktop e tocco, filtri e anteprime condivise. Controlli mirati su backup riuscito/fallito, dati non leggibili, memoria bloccata, compatibilità delle osservate, Oracle e tipo su telefono e anteprime inizialmente vuote.

Le verifiche locali non sostituiscono il giro Opus ancora necessario sulla versione corretta.

## Ripresa

Nello stesso workspace il runner locale è `docs/local/reviews/opus-20261028/review.py`; il prossimo argomento libero è `7`, perché il tentativo `6` è conservato come fallimento per quota. Dopo il ripristino eseguire un nuovo giro sui sorgenti correnti, verificare ogni eventuale rilievo e continuare fino a un responso effettivo senza segnalazioni.

Il runner e i verbali grezzi sono locali: in un altro clone applicare la [skill mtg-review](../../.agents/skills/mtg-review/SKILL.md), usare il modello `opus` e leggere prima le decisioni condivise. La skill richiede: «Dichiarare zero rilievi soltanto dopo un esito effettivo della review finale».
