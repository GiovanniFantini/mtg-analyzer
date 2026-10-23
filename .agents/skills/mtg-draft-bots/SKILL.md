---
name: mtg-draft-bots
description: Indagare scelte poco credibili dei bot Draft o modificare e validare le loro politiche decisionali. Usare per simulazioni complete e confronti riproducibili prima e dopo una correzione.
---

# Politiche e diagnosi dei bot Draft

Leggere `docs/draft-engine.md` per confini, profili e memoria dello stato; `docs/architecture.md` quando cambiano collazione, eventi o compatibilità. I percorsi sono relativi alla radice del repository.

Una segnalazione di comportamento scorretto richiede riproduzione e correzione dei difetti confermati, salvo richiesta esplicita di sola analisi. Non attendere un export dell'utente: generare tavoli completi riproducibili con semi e configurazioni registrati.

1. Conservare una baseline prima delle modifiche. Esaminare le singole pick con busta, pool precedente, colori, fase, curva, mana, piano e alternative. Distinguere voto base, contributi al punteggio, casualità e transizioni. Un riferimento alla catena di Markov è un'ipotesi da verificare.
2. Separare difetti dei dati e dei voti da quelli della politica. Per rare e mitiche arrivate tardi, verificare qualità Limited, giocabilità nei colori e alternative preferite. Fuori colore o senza supporti una carta può essere passata correttamente; la rarità non assegna priorità automatica.
3. Correggere la causa confermata nel motore condiviso. Non cambiare voti o probabilità per mascherare un errore dell'algoritmo. Preservare osservazioni parziali dei bot, costo del counterpick e distinzione reale fra i profili. Se si sviluppa un modello markoviano, esplicitare stato, osservazioni, azioni, transizioni e politica.
4. Confrontare prima/dopo con stessi semi, dati e giocatore simulato. Verificare più profili e situazioni simmetriche, compreso l'ordine dei dati. Affiancare conteggi con denominatori espliciti ed esempi concreti; le frequenze delle scelte non provano forza del mazzo o WR.
5. Proteggere replay e salvataggi con politica originaria, versione dell'algoritmo e impronta funzionale. Preservare record incompatibili e snapshot. Controllare anche conservazione di carte e buste con `node verify-draft-engine.cjs`, replay storici e nuovi, continuazione dei salvataggi e flussi nel browser. Aggiungere controlli mirati ai difetti verificati ed eseguire le verifiche pertinenti di `docs/verification.md`.
6. Salvare rapporto datato con configurazione, revisione del codice, dati, evidenze e limiti. Distinguere diagnosi, correzione locale, push autorizzato e disponibilità verificata sul sito. Conservare le modifiche di altre attività.

Per una review richiesta con Sonnet applicare `.agents/skills/mtg-review/SKILL.md` dalla radice del repository. I test locali non sostituiscono quella revisione.
