---
name: mtg-site-ux
description: Migliorare layout, navigazione e accessibilità del sito MTG quando è richiesto un restyling UX o un'esperienza sensibilmente migliore.
---

# UX del sito MTG

Esaminare i percorsi dell'intero sito quando viene chiesto un miglioramento generale o un effetto wow. Gli esempi segnalati sono punti di partenza, non un elenco esaustivo. Una richiesta circoscritta resta circoscritta.

Se il perimetro è solo UX, conservare funzioni, contenuti utili, regole, valutazioni, dati e salvataggi. Intervenire su disposizione, gerarchia, esposizione, coerenza e feedback, distinguendo problemi di presentazione da funzioni mancanti o errori del motore.

1. Esaminare navigazione, densità, comandi e stati degli strumenti su desktop e telefono. Cercare riferimenti online pertinenti a UX, accessibilità e prestazioni e applicarli ai flussi concreti. Per requisiti GitHub Pages richiesti verificare la documentazione corrente; separare compatibilità tecnica, misure locali e traffico non verificato.
2. Intervenire su sorgenti e template condivisi, per le espansioni pertinenti. Preferire CSS e JavaScript nativi, dipendenze minime e animazioni brevi. Riservare spazio alle carte durante il caricamento e mantenere dimensioni stabili mentre il Draft avanza.
3. Curare leggibilità, allineamento dei comandi, dimensioni e spaziatura dei bersagli tattili, focus visibile, selezioni persistenti e `prefers-reduced-motion`. Valutare i comandi del telefono nei flussi reali, senza dedurre requisiti numerici permanenti dalle misure di un singolo restyling. Conservare esempi strategici concreti anche nelle versioni per telefono.
4. Verificare desktop, telefono, tastiera e tocco: anteprime di ogni riferimento a carta, filtri, dialoghi, tabelle scorrevoli, overflow, salvataggi e contenuti dinamici. Preservare la leggibilità dei contenuti editoriali statici senza JavaScript e la raggiungibilità da tastiera delle aree scorrevoli con tabelle. Le verifiche di pagine storiche non certificano pagine nuove. Usare i controlli pertinenti di `docs/verification.md`, relativo alla radice del repository.
5. Valutare se trovare, leggere e confrontare le informazioni è diventato più semplice. La sola presenza di ricerca e dettagli espandibili non dimostra una UX avanzata. Distinguere interventi conclusi e ampliamenti successivi senza aggiungere requisiti automatici.

Quando è richiesta una review indipendente applicare `.agents/skills/mtg-review/SKILL.md` dalla radice del repository e verificare autonomamente ciascun rilievo prima di correggerlo.
