# Ristrutturazione e strumenti trasversali, 28 ottobre 2026

## Esito

Lavoro suddiviso fra UX, contratto dati e fonti, con integrazione e nuovo torneo coordinati nell'attività principale. Nessuna modifica alle pipeline. Nessun commit o push; conservate le modifiche già presenti di altre attività.

Il [resoconto architetturale](2026-10-28-architecture.md) distingue struttura generica dei JSON, funzionalità pronte e dati ancora mancanti. Ogni set espone la matrice nella propria panoramica. I requisiti sono leggibili nelle pagine e nei JSON pubblici; la build non inventa dati per attivare strumenti. Chiavi degli eventi, ID dei profili e tipo di evento restano concetti distinti.

## Percorsi e filtri

La home parte dall'espansione. Dalle pagine del set si cerca direttamente nel catalogo; la ricerca locale del catalogo evita un doppione. Colore, rarità, tipo e mana sono filtri generali. Identità di colore riguarda la costruzione Commander; valutazioni Sealed, ranking Draft e win rate hanno il proprio contesto e vengono separati dai filtri generali. Le metriche mancanti non diventano zero.

Analisi, combo e discovery espongono prima le azioni principali e racchiudono filtri secondari, legenda e metodo in sezioni espandibili. Le pagine lunghe hanno un indice locale. L'analisi Star Trek usa lo stesso renderer delle altre espansioni, conservando i contenuti editoriali negli approfondimenti.

Le viste avanzate diventano condivise quando arrivano i dati: una presentazione di anteprima non è più un vincolo permanente alle funzionalità. I banchi manuali e le prove di mano precedenti mantengono accessi separati e chiavi di salvataggio preservate. Le chiavi opzionali del nuovo pool sono derivate dall'espansione e controllate per collisioni.

Riferimento UX consultato: [W3C, Page Structure](https://www.w3.org/WAI/tutorials/page-structure/).

## Nuovi set e torneo

La [skill mtg-new-set](../../.agents/skills/mtg-new-set/SKILL.md) documenta fonti, procedure, importatori realmente riutilizzabili e passaggi ancora manuali. L'inventario offline parte dai registri effettivi, compresi quelli di Reality Fracture. La presenza dell'URL storico non certifica una fonte disponibile per il nuovo set.

Il [torneo locale](../tournament.md) gestisce da 2 a 8 iscritti, sorteggio iniziale, turni svizzeri, bye, ritiri, risultati, classifica con spareggi e timer persistente. Esportazione e importazione usano un JSON versionato indipendente dall'espansione. Backup integrale prima della sostituzione, blocco su errore del backup e recupero dei record incompatibili. Limiti espliciti: un tavolo, nessun playoff, nessuna sincronizzazione fra dispositivi o registrazione ufficiale EventLink.

## Verifiche

- Build offline e collegamenti locali di 22 pagine verificati.
- Test del contratto espansioni e dei renderer condivisi, incluse chiavi evento rinominate e dati pronti nelle anteprime.
- Suite finale Python: 40 test superati. Regressioni browser su 18 fixture isolate superate; test riallineati alle viste del workspace, ai pannelli espandibili e al completamento asincrono dei salvataggi. La fixture del filtro Standard isola ora il dato che intende verificare.
- Verifiche motore: 3.000 buste storiche, 30.000 buste campionate, conservazione, replay e Pick-Two; contratto collazione.
- Suite UX: 95 controlli responsive; matrice aggiuntiva delle 22 pagine su quattro larghezze, senza overflow o errori JavaScript. Tre Draft completi con ripresa e review, movimento ridotto e contenuti senza JavaScript.
- Cataloghi: filtri combinati, ordinamenti, reset, assenze e anteprime mouse/tastiera/tocco; ricerca tra pagine di entrambi i set.
- Nuova Analisi Star Trek: ricerca, filtri, reset, anteprime e layout a 1440 e 390 px.
- Torneo: abbinamenti da 2 a 8, punti e spareggi, bye, ritiri, validazione, timer dopo ricaricamento; flusso completo desktop/tocco, export/import, record incompatibile e backup fallito.

I dati di Star Trek restano parziali e il valore atteso del box non è attivato dai soli prezzi di riferimento. L'intervento rende esplicite e gestibili queste lacune; non è un'acquisizione integrale di nuovi dati di ricerca.
