Review del tavolo Draft visuale, 29 ottobre 2026.

Perimetro: interfaccia a viewport, pile, composizione del pool, revisione dei bot, anteprime, accessibilità, integrazione con la navigazione e recupero delle sessioni. Motore, collazione, voti e formato dei record restano invariati. La v4 conserva lo stato sperimentale. La review è distinta dalla successiva pubblicazione autorizzata dall’utente.

Modello richiesto: Opus. Le risposte confermano `claude-opus-5-5` in `modelUsage`. Ogni giro conserva prompt, risposta integrale, risultato JSON, HEAD e hash dei sorgenti, comprese le modifiche non committate. Sono stati esclusi `docs/local/` ed `ev-*`.

Stato: concluso, pronto per la produzione nel perimetro del tavolo Draft visuale. Quattro giri effettivi con Opus, dieci rilievi corretti e approvazione finale con `approved: true` e `findings: []`. Tutte le verifiche richieste sono concluse con esito positivo; nessun controllo pendente. Alla chiusura della review la versione era locale; commit e push sono stati autorizzati successivamente.

Rilievi e correzioni:

| Rilievo | Esito verificato |
| --- | --- |
| R1-01 | Rarità visibile sulla busta, copie foil conservate nelle pile e nomi accessibili completi. |
| R1-02 | Righe minime nella busta su finestre basse; modalità a viste anche su touch in orizzontale. |
| R1-03 | Anteprima collocata fuori dalla carta di origine; nessuna riapertura al ritorno dal dialogo touch. |
| R1-04 | Navigazione coperta sempre inerte durante il draft, anche attraversando il breakpoint della shell. |
| R1-05 | Export dalla configurazione e ripresa dalla memoria, anche con storage bloccato o worker terminato. Backup incompatibili ancora protetti. |
| R1-06 | Il pannello Analisi mostra l'errore della review invece di restare in calcolo. |
| R1-07 | Altezza delle pile misurata sullo spazio assegnato, indipendente dal proprio contenuto. |
| R1-08 | Regioni scorrevoli e gruppo delle basi dotati di ruolo e nome accessibile. |
| R1-09 | Test estesi a foil, viewport bassi, sovrapposizioni, viste v4, basi, errori e recupero. Indice delle verifiche aggiornato. |
| R2-01 | Worker terminato riconosciuto come errore della sessione; istruzioni di ricostruzione e avviso sul solo record esportabile. |

Risultati dei giri: [primo](round-1.review.json), [secondo](round-2.review.json), [terzo](round-3.review.json), [chiusura definitiva](round-4.review.json). Le verifiche e le motivazioni delle decisioni sono in [decisions.json](decisions.json).

Evidenze concluse: build di 21 espansioni e 290 pagine con link locali validi; 37 test di `test_expansion_data.py`; test dei riepiloghi visuali; suite browser del tavolo, recupero senza storage, replay classici v2/v3 e draft completo v4. I controlli della shell su home e Star Trek sono in [shell-checks.json](shell-checks.json). La nuova build dopo R2 è registrata in [checks-round-2-fix.json](checks-round-2-fix.json).

L'acquisizione [checks-production-candidate.json](checks-production-candidate.json) conserva un timeout del test di recupero: la simulazione di errore partiva prima della conferma della pick precedente. Il test ora aspetta il conteggio delle pick e la fine della mossa prima di iniettare l'errore. Non sono stati cambiati i sorgenti del sito per risolvere questo timeout. L'acquisizione successiva mantiene output e hash dei sorgenti e dei test.

Limiti: Opus ha eseguito una lettura statica; le prove browser sono dell'implementatore. Il crash è simulato invocando il gestore `onerror` del worker, che esegue lo stesso percorso di arresto del client. Nessuna misura di forza competitiva dei bot o di prestazioni su CPU di telefono viene dedotta da queste prove.

La suite definitiva è in [checks-production-confirmed.json](checks-production-confirmed.json): riepiloghi visuali, tavolo responsive, recupero senza storage, replay classici e draft v4 completo, tutti con exit code 0. La v4 verifica anche la terminazione del worker durante la revisione finale, l’avviso sull’export del solo record e la ricostruzione successiva. [checks.json](checks.json) collega questi esiti a build, unit, controlli della shell e hash degli asset generati. Il [manifest finale](round-4.manifest.json) coincide con i sorgenti correnti e con quelli verificati; Opus ha confermato questa corrispondenza nel quarto giro.

Per una futura pubblicazione vanno inclusi anche i nuovi sorgenti e test, oltre ai diff tracciati: `draft-visual.js`, `test-draft-visual.cjs`, `verify-draft-table-visual.cjs` e `verify-draft-table-recovery.cjs`. I file di altre attività non sono stati modificati o inclusi. Nessun file di pipeline o CI/CD è stato modificato.
