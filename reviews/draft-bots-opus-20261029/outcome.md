# Confronto con Opus sui requisiti dei bot Draft

Concluso il 29 ottobre 2026: cinque giri effettivi con `claude-opus-5-5`, confermato da `modelUsage` in tutte le risposte. Nei primi quattro giri sono stati valutati 22 rilievi. Il quinto restituisce `approved: true` e `findings: []`. Non rimangono criticità sostanziali aperte nel perimetro dei requisiti.

La [specifica approvata](../../docs/requirements.md#qualità-competitiva-dei-bot-draft) conserva 14 requisiti con priorità e criteri di accettazione. Le versioni esatte ricevute dal revisore sono nei manifest e nelle richieste di ogni giro. I file finali coincidono con gli hash dell'ultimo input approvato; i controlli sono in [verification.json](verification.json).

## Decisioni principali

- Il miglioramento parte dalle capacità comuni: main provvisorio, base di mana, valore marginale, sostituibilità delle carte, sinergie causali e lettura dei segnali. Gli specialisti aggiornati usano queste capacità; i replay mantengono la politica originaria.
- Un build-around può avere valore di opzione presto, senza presumere supporti garantiti. Un cambio di piano confronta i mazzi ancora costruibili, senza valorizzare le pick già spese come costo affondato.
- Le carte con usi alternativi occupano un solo slot. Il fixing dipende da terre ricercabili, costi e tempi nella configurazione candidata, comprese le basi aggiungibili dall'evento. Il costruttore considera insieme splash e mana, senza doppio credito pieno a fonte e minaccia.
- La qualità di base ha provenienza e contesto di riferimento dichiarati. Le correzioni contestuali sono scarti da quel riferimento, anche negativi; non sommano di nuovo vantaggi già compresi nel voto.
- La copertura non può diventare una preferenza per i piani meglio annotati. Componenti incomplete vengono disattivate uniformemente nell'evento; uso parziale solo diagnostico. Le soglie valgono per tutti i profili che usano le capacità condivise.
- Il confronto usa fixture motivate e congelate, casi riservati, revisione cieca e rubriche comuni. Le metriche condivise con il candidato sono coerenza interna, non prova indipendente della forza. Ogni sessione ha una sola versione; le versioni si confrontano su sessioni distinte con buste iniziali verificate da impronta.
- Versionamento, replay, banco di prova e casualità per posto vengono all'inizio del lavoro. L'implementazione mantiene il default originario fino alla valutazione del candidato.

## Serve un nuovo profilo?

La raccomandazione iniziale è stata rivista. Non è necessario aggiungere automaticamente un decimo profilo. Adattivo è prima di tutto la configurazione di riferimento del motore comune aggiornato, senza preferenza stilistica fissa.

Va esposto separatamente solo se una fixture motivata e il confronto riservato mostrano una distinzione materiale e utile rispetto a Lettura dei segnali aggiornata. Se la distinzione non emerge, i due vengono unificati nel profilo esposto, preservando gli identificatori storici per i replay. Non si introducono errori o rumore per giustificare un nome aggiuntivo.

## Verifiche e limiti

I collegamenti locali, gli identificativi BOT, i JSON, la sintassi dell'helper e il diff sono stati controllati. Gli hash dei sorgenti del motore e dei dati delle espansioni coincidono con la baseline. Non sono state modificate politica, voti, pipeline o interfaccia; nessun commit o push. La suite browser non è richiesta per questi soli documenti.

L'approvazione riguarda coerenza strategica, fattibilità e verificabilità dei requisiti. I bot restano da implementare e misurare. Non sono state giocate nuove partite e il confronto non attribuisce una WR né dimostra un ottimo matematico.

Il [registro delle decisioni](decisions.json) conserva ogni rilievo e la sua valutazione autonoma. Le proposte di Opus non sono state recepite automaticamente: per esempio non è stato imposto un divieto di sinergie fra copie omonime né un formato con versioni miste nella stessa sessione. I suggerimenti facoltativi dell'ultimo giro restano distinti dalle condizioni di chiusura.
