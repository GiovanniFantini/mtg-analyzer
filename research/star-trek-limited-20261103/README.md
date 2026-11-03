# Star Trek: analisi Limited completa delle comuni e non comuni

Studio editoriale del 3 novembre 2026. Completa la parte Limited rimasta fuori dai [dodici approfondimenti campione](../star-trek-decisions-20261103/README.md). Non misura risultati di gioco e non assegna nuovi pesi ai bot.

## Copertura e uso nel sito

- 201 identità TRK non base: 91 comuni e 110 non comuni. Ogni carta ha una nota e una fascia qualitativa per Draft e una nota e fascia per Sealed, con supporti e confronti specifici. Le cinque terre base sono escluse. Le differenze fra i due contesti non sono un incremento automatico per il solo fatto che il Sealed possa durare più a lungo.
- 336 voti Limited di Andrew Quinn, Draftsim: 306 TRK non base e 30 SDS. Tutte le righe sono abbinate al catalogo. Quattro voti di ciclo sono estesi ai membri verificati; le SDS usano il nome canonico esplicitato fra parentesi. Non sono 336 recensioni Sealed separate.
- I 306 voti adottati di J2SJosh restano invariati. Il confronto usa le scale originali 0–5 e 0–10, senza media. Il valore zero è conservato e non diventa N/D. La divisione per due nell'evidenza a stelle serve alla presentazione della scala Draftsim, non ai modelli di scelta.
- 42 schede su carte che possono cambiare il campo o il piano della partita: effetti immediati, motori, chiusure condizionate e risposte, con costi, limiti e differenze Draft/Sealed. È una selezione ragionata, non una classificazione individuale di tutte le rare. Include ospiti e non comuni, senza assegnare automaticamente la qualifica di bomba a una rarità.
- 26 pacchetti strutturati di sinergie, inclusi 16 nuovi pacchetti composti da comuni e non comuni. Sono consultabili anche nella pagina Sinergie, con ricerca per carte e filtri. Non sono stati inventati indici di potenza, praticità o frequenze per riempire il catalogo numerico delle combo.
- Otto rare condizionate nella sezione delle scelte da valutare con cautela, con una ragione concreta per inserirle invece di un declassamento basato sul simbolo.

Draft e Guida Sealed mostrano la rassegna completa con ricerca, colore/identità, rarità, contesto e fascia editoriale. Cambiare contesto cambia note e ordinamento. Senza JavaScript entrambe le analisi restano leggibili. Le schede nel catalogo e nella consultazione Constructed espongono le stesse valutazioni e i pareri attribuiti; questi giudizi restano Limited e non diventano prospettive Constructed. I nomi delle carte mantengono anteprime da mouse, tastiera e tocco.

## Metodo e fonti

[editorial.json](editorial.json) conserva le 201 valutazioni scritte sul testo delle carte. Le fasce indicano priorità, solidità, dipendenza dai supporti, riempimento, riserva mirata o esclusione di base. Non sono probabilità, WR o conversioni dei modelli automatici. Il Draft considera il costo opportunità del pick e i supporti ancora da costruire; il Sealed considera le carte effettivamente aperte, il fixing, la curva, la stabilizzazione e le risposte. I giudizi devono essere rivisti alla luce di partite e pool reali, senza trattare il contesto più lento come una certezza.

[draftsim-reviews.json](draftsim-reviews.json) conserva i voti, l'autore, la data di pubblicazione del 2 novembre, la rilettura del 3 novembre, la copertura e l'hash della cattura. Gli articoli integrali restano nella cache temporanea. [source-audit.json](source-audit.json) registra anche release notes Wizards, archetipi ufficiali e riletture pertinenti. La base di recensioni precedente rimane in [ricerca del 2 novembre](../star-trek-20261102/README.md).

[oracle-check.json](oracle-check.json) confronta le 311 identità TRK con l'API Scryfall del 3 novembre. Tutte sono abbinate; la sola differenza di testo è il reminder di Mirror Universe Intrusion, già corretto localmente sull'immagine della carta e documentato nell'audit del 28 ottobre. Non è una nuova errata e il catalogo non è stato sovrascritto. Le SDS conservano identità e legalità proprie; la loro presenza nel catalogo non certifica tutte le stampe ammesse al prodotto.

[disagreements.json](disagreements.json) approfondisce sette divergenze, fra cui Support Mission, Conquest Mission e Mirror Universe Intrusion. Per Cloak and Phaser il costo verificato è nove meno il numero di nomi: servono quattro nomi per arrivare a cinque mana. Si conserva il voto dell'autore senza trasformare un'argomentazione di anteprima in prova di rendimento.

[impact.json](impact.json), [synergies.json](synergies.json) e [baits.json](baits.json) conservano le selezioni e le sequenze. Ogni pacchetto dichiara stato, mana, beneficio e limiti: per esempio Boimler aggiunge valore a station prima delle cariche, Vash trasforma un'uscita dal cimitero in pescata una volta per turno, e i segnalini di Phlox devono diventare danni al giocatore per produrre carte. I costi di mana, tap, sacrificio, ritorno in mano e perdita temporanea di bloccanti restano parte della valutazione.

WR Draft e Sealed restano N/D. Non sono stati acquisiti prezzi, risultati post-uscita o frequenze di collazione. Oracle, legalità, osservazioni di torneo e Commander precedenti, prezzi con date, chiavi dei salvataggi e le dodici schede precedenti sono conservati. Le prove di conservazione e copertura sono in [coverage.json](coverage.json).

## Riproduzione e verifiche

L'integrazione ordinaria è offline:

```sh
python integrate_limited_study.py --expansion expansions/star-trek --study research/star-trek-limited-20261103
python -m unittest test_limited_study.py test_star_trek_research.py test_expansion_data.py test_editorial_decisions.py
python build_site.py
```

Una nuova acquisizione della recensione richiede un HTML pubblico ottenuto esplicitamente e una nuova cartella datata. `extract_reviews.py <cattura.html>` normalizza la cattura, rifiutando identità mancanti o duplicate; non viene eseguito dalla build. Non riutilizzare una data vecchia per contenuti nuovi.

Per il browser configurare `MTG_SITE_URL`, `MTG_PLAYWRIGHT_MODULE`, `MTG_BROWSER_CHANNEL` e `MTG_QA_DIR` come in [verification.md](../../docs/verification.md), quindi eseguire `node verify-limited-study.cjs`. Il controllo verifica le 201 schede, filtri combinati, reset, zero della recensione, dissensi, fonti, 42 carte decisive, 26 pacchetti, anteprime e assenza di errori su desktop e telefono; verifica anche la consultazione senza JavaScript. Le regressioni di disponibilità e salvataggi sono coperte da `python verify-expansion-review.py` e `node verify-expansion-browser.cjs`.

Gli esiti effettivi sono registrati in [verification.json](verification.json). Nessuna modifica alla pipeline. Preparazione locale, push e pubblicazione sul workflow vengono verificati separatamente.
