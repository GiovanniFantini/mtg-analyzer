---
name: mtg-review
description: Eseguire una review indipendente richiesta sul sito MTG, anche con Sonnet e cicli di correzione, conservando evidenze, decisioni ed esito sulla versione aggiornata.
---

# Review indipendente verificabile

Usare effettivamente il modello richiesto. Non sostituire Sonnet con una propria review o con un altro modello senza dichiarare il limite. Verificare la disponibilità degli strumenti prima di promettere il ciclo; una chiamata rifiutata non è una review.

## Input e verbali

Selezionare solo materiale pertinente al perimetro autorizzato. `docs/local/` ed `ev-*` possono contenere memoria personale: ometterli quando non servono e minimizzare gli estratti quando servono alla review richiesta. Conservare input, risposte e log contenenti materiale privato in `docs/local/`, già ignorato da Git, anche se l'invio al revisore rientra nella richiesta. Nei registri condivisibili lasciare hash, decisioni ed evidenze prive dei valori personali. Una copia sotto `reviews/` non eredita le esclusioni del file originale.

## Esecuzione

Gli helper disponibili nella cartella di lavoro sono `review-expansions-sonnet.py` per l'architettura e, se presente, `review-ux-sonnet.py` per il restyling. Quest'ultimo può essere un artefatto locale non tracciato: verificarne disponibilità e tracciamento senza presumerne la presenza in un altro clone. Sono script datati, con liste di input e destinazioni proprie: non riusarli senza verificare documenti tematici, esclusioni e numero di giro, né sovrascrivere un giro precedente. La review documentale avviata il 22 ottobre usa `reviews/docs-reorganization-20261022/review.py`, con verbali grezzi in `docs/local/reviews/` e manifest condivisibili. Questi strumenti non sostituiscono la definizione del perimetro corrente.

Il meccanismo disponibile in questo ambiente è Claude CLI. Come negli helper Python, risolvere `claude` dall'ambiente e invocarlo con `subprocess.run` e una lista di argomenti: `['--print', '--model', 'sonnet', '--effort', 'high', '--output-format', 'json', '--tools', '', '--strict-mcp-config', '--no-session-persistence', '--safe-mode']`. Passare il prompt tramite standard input e preservare la stringa vuota dopo `--tools`; non convertire la lista in una stringa di shell, che può perdere argomenti vuoti in alcune versioni di PowerShell. Registrare il modello effettivo restituito in `modelUsage`. Non presumere disponibilità o quota in altri ambienti.

## Ciclo

1. Registrare perimetro, modello effettivo e versione esatta del codice. Un SHA non descrive le modifiche non committate: conservare anche diff o hash dei file rilevanti. Fornire al revisore sorgenti, documentazione pertinente ed evidenze, distinguendo lettura e prove nel browser. Gli helper datati possono avere liste fisse di input: verificarle e includere i documenti tematici necessari, senza presumere che il solo README contenga ancora il contratto completo.
2. Verificare autonomamente scenario, causa e conseguenza di ogni rilievo con riproduzioni, stili effettivi o controlli mirati. Conservare evidenze e decisione: confermato, parzialmente fondato, scartato o fuori perimetro, con motivazione.
3. Correggere i difetti confermati e provare le correzioni. Preferenze estetiche e ampliamenti non diventano automaticamente bug. Usare i controlli pertinenti di `docs/verification.md`, relativo alla radice del repository; una sola modifica documentale non richiede l'intera suite.
4. Se è richiesto di ciclare, chiedere nuovi giri sul codice corretto fino alla chiusura dei rilievi fondati nel perimetro concordato. Registrare ogni versione e risultato. Dichiarare zero rilievi soltanto dopo un esito effettivo della review finale.
5. Se quota, accesso o browser impediscono il controllo, conservare richiesta, esito e parte ancora pendente. Distinguere verifiche locali concluse e review bloccata senza presentare il lavoro come certificato.

Tenere separati i registri delle diverse attività. `sonnet-ux-decisions-20261022.json` riguarda il restyling UX e può essere disponibile solo nella cartella di lavoro, non in ogni clone; `reviews/expansions-20261022/decisions.json` riguarda l'architettura. Leggere il relativo registro prima di riferirne lo stato; se manca, dichiarare l'esito non consultabile in quell'ambiente. La riorganizzazione della documentazione non chiude review precedenti. Per un commit autorizzato verificare le dipendenze documentali come indicato in `docs/verification.md`, senza includere automaticamente artefatti di altre attività.
