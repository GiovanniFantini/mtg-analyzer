# Star Trek, aggiornamento del 7 novembre 2026

Catalogo attivo: 341 identità, 311 TRK e 30 SDS. La nuova acquisizione Scryfall
conferma le stesse identità e legalità e integra 616 stampe contro le 611 dello
snapshot precedente. Le cinque aggiunte sono varianti grafiche inverted TRK
327-331 di Uhura, Scotty, Bones, Kirk e Spock, abbinate alle identità esistenti.
Non si certifica il censimento completo dei trattamenti o la loro collazione.
La sola differenza Oracle rilevata è il reminder di Mirror Universe Intrusion,
già corretto localmente sull'immagine: la correzione precedente è conservata.
Nessuna identità del pool personale viene sostituita.

## Dati disponibili nel sito

| Area | Copertura e significato |
| --- | --- |
| WR Draft | 322 righe Untapped, 280 con WR in mano, 42 senza valore |
| WR Sealed | 318 righe Untapped, 253 con WR in mano, 65 senza valore |
| Tier Draft Untapped | 268 carte classificate e 54 con campione insufficiente |
| Voti Limited nuovi | 498 valutazioni esplicite riportate da Limited Library: Nizzahon e Limited Level-Ups |
| Community separata | 125 carte con aggregati myLimitedGrades, numero di valutatori conservato; 336 carte controllate su quattro pagine |
| Voti conservati e riletti | 306 J2SJosh e 336 Andrew Quinn; nella rilettura Draftsim cambiano due punteggi |
| Analisi Draft/Sealed separate | 201 comuni e non comuni, studio editoriale del 3 novembre conservato |
| Nuove letture per formato | 75 osservazioni attribuite Commander, Pioneer e Legacy |
| Modern | Otto nuovi scenari editoriali su Oracle, insieme ai pareri precedenti |
| Pauper | Review di Romeu riletta e osservazioni precedenti conservate; nessun risultato TRK post-uscita inventato |
| Commander TRC | Appendice esistente separata dal pool Limited; questa attività non recensisce individualmente tutte le carte TRC |

Le WR provengono dall'early access del 4 novembre: 1.800 partite Draft e 890
Sealed dichiarate dalla fonte, filtri conservati negli snapshot. Arena apre
pubblicamente il 10 novembre, mentre l'uscita cartacea è il 13 novembre.
Non sono risultati del metagame stabilizzato. Games è il conteggio mostrato
dalla fonte, non un denominatore verificato della WR in mano. Il filtro di
campione minimo rimane disattivato quando il denominatore manca. I margini di
confidenza pubblicati rimangono nei JSON. Included WR è sospetta, sempre zero
nelle righe disponibili, e viene esclusa dagli indici; le metriche Premium
restano null. Nessuna WR è stata convertita in stelle o in peso dei bot.

Le righe assenti sono elencate separatamente nei due snapshot. La fonte
include le SDS che ha osservato, senza attribuire dati alle altre carte ospiti.
La normalizzazione di `All Good Things . . .` verso `All Good Things...` usa
l'identità del catalogo; non crea una nuova carta. I valori N/A restano null.

Nel Catalogo si selezionano fonte ed evento WR Draft/Sealed, ordinamento,
campione minimo e filtri. Il tier ha il proprio ordinamento. Aprendo una carta,
Utilizzo e prospettive mostra i nuovi voti nel blocco Limited delle carte TRK,
rare comprese, con collegamento al video e attribuzione secondaria. Le SDS mantengono
i voti numerici Draftsim nel blocco Limited. Le nuove letture per
formato restano distinte. Le guide conservano valutazioni e piani
Limited separati. Panoramica, Analisi e Fonti indicano l'aggiornamento e i limiti.

## Attribuzioni e controlli

[attributed-grades.json](attributed-grades.json) contiene soltanto voti che
Limited Library dichiara espliciti. Otto valutazioni inferite sono conservate
nella sezione esclusa e non importate. Le doppie valutazioni e gli intervalli
rimangono testuali, senza medie, conversioni numeriche o consenso costruito.
I video originali sono collegati, ma non sono stati trascritti e verificati
indipendentemente. Limited Resources compare nell'elenco dei creatori della
fonte, ma non ha osservazioni acquisite: nessun voto gli viene attribuito.
La data del dataset Limited Library è il 3 novembre, distinta dall'acquisizione.

[format-notes.json](format-notes.json) conserva le letture EDHREC di Jeremy Rowe
del 6 novembre e Nicholas Lucchesi del 4 novembre, e le review Pioneer/Legacy
di Cards Realm. Le note Modern nuove sono scenari editoriali, non giudizi
attribuiti agli autori di un altro formato. I dissensi su Starfleet Academy e
sulle terre Anomaly rimangono leggibili, senza eliminare uno dei due pareri.

Controlli sul testo e correzioni sostanziali:

- Engineered Explosives è TRK 264. La review Pioneer valuta l'aggiunta futura;
  la legalità corrente resta distinta dall'ammissibilità prevista al 13 novembre.
  La prima ipotesi di questo aggiornamento, che la trattava come SDS, è stata
  scartata dopo il confronto con catalogo e acquisizione Scryfall.
- Starfleet Academy richiede sei tipi non-Borg per produrre più mana dei
  cinque pagati. Considerando il mana incolore a cui si rinuncia tappandola,
  sei tipi pareggiano le risorse, sette producono guadagno netto.
- Genesis Device richiede tre mana per il lancio, cinque per attivare, tap e
  tempistica da stregoneria. Il paragone con Scapeshift non cancella questi costi.
- The Holodeck non rianima gratuitamente: bisogna giocare le carte rispettando
  costi e tempi. Fuori dal gioco non significa riserva libera nel Commander
  ordinario. Nei tornei Constructed l'accesso è invece alla sideboard, come
  precisato dalle release notes ufficiali.
- Le descrizioni automatiche delle meccaniche non sostituiscono Oracle.
  Non ogni scelta è una modalità e Dilemma non significa semplicemente
  lanciare una qualsiasi carta con più opzioni.

## Ricerca e lacune

[source-audit.json](source-audit.json) distingue acquisizione HTTP, hash e accesso
negato. [source-assessments.json](source-assessments.json) assegna a ognuna delle
54 acquisizioni uno stato d'integrazione e una motivazione, distinguendo
`confirmed`, `integrated`, `acquisition_only`, `excluded_or_context_only` e
`unavailable` e `not_acquired_local_tls`.
`retrieved_unreviewed` significa solo cattura riuscita, non lettura o
approvazione. Le estrazioni realmente integrate sono nei file normalizzati;
non si conta ogni pagina scaricata come nuova prova.

La ricerca ha considerato fonti ufficiali Wizards, Scryfall, Untapped,
17Lands, MTG Arena Zone, Draftsim, Limited Library, EDHREC, Cards Realm,
MTG Rocks, Card Kingdom, MTGGoldfish, CollectorUnion, Deathmarked,
MTG-Standard, MTGMeta, myLimitedGrades, Postboard, NerdSnack, TurnZero,
PreconForge, LimitedMTG, Metagame e altri indici individuati. La raccolta
precedente documenta già più di dieci editori letti; questo aggiornamento
non presenta tutti i download come nuove recensioni indipendenti.

Cardmarket restituisce 403: conservati i prezzi del 27 ottobre, senza altri
mercati o prezzi zero. EDH LAB non è stato acquisito per un errore TLS locale
di urllib; questo non dimostra indisponibilità della fonte. La pagina Modern
ipotizzata su Cards Realm non contiene una review utile e non viene citata
come prova. Il podcast Common Ground 151 del 5 novembre è stato individuato,
ma senza trascrizione primaria acquisita non gli vengono attribuiti giudizi
per carta. Le sintesi Historic, i modelli MTGMeta/MTG-Standard e le guide
automatiche non diventano risultati Modern, Pauper o statistiche osservate.
Individuato anche il video Pauper StrataGames del 6 novembre, senza ottenere
una trascrizione primaria utilizzabile. La rilettura Draftsim conferma 334
voti e aggiorna 70,000 Light-Years from Home a 7/10 e Pure Energy a 2/10;
lo snapshot del 3 novembre rimane intatto.
Anche le sette review MTG Arena Zone sono state estratte integralmente:
306 voti confrontati e confermati senza modifiche. myLimitedGrades non offre
ancora benchmark 17Lands, ma mostra aggregati Community: questi rimangono
separati dai pareri degli esperti, con i piccoli campioni di valutatori visibili.

Restano mancanti un campione stabile successivo all'apertura pubblica,
una recensione Modern autonoma completa acquisita, voti Sealed separati
per tutte le rare/SDS, copertura individuale completa TRC/cEDH e nuove
letture Cardmarket. Nessuna di queste lacune viene riempita con stime.
Non si pretende di aver esaurito ogni fonte possibile del web.

## Riproduzione

L'integrazione è offline:

```sh
python integrate_star_trek_20261107.py
python build_site.py
python -m unittest test_star_trek_update.py test_expansion_data.py test_star_trek_research.py test_catalog_statistics.py test_catalog_metrics.py
```

`research_star_trek_20261107.py` è l'acquisizione online esplicita e separata
dalla build. `capture.cjs` usa Playwright e `MTG_PLAYWRIGHT_MODULE` e
`MTG_BROWSER_CHANNEL` configurati dall'ambiente, scorre le tabelle virtuali
e conserva soltanto le celle pubbliche; non sblocca metriche Premium.
Gli articoli integrali e il DOM restano nella cache temporanea.
`normalize.py --capture` salva solo celle e voti fattuali in `captures/`, con
hash delle fonti. Senza argomenti normalizza questi input dal repository, senza
rete o cache temporanea. Le osservazioni normalizzate consentono l'integrazione
offline; `audit.py` conserva il confronto Oracle e lo stato di ogni fonte.
Le acquisizioni storiche rimangono intatte.

`audit-replays.py` confronta le impronte v2 e della politica v4 con il commit
precedente registrato. Draft e Pick-Two mantengono le stesse revisioni, anche
nel percorso `statisticsReference`: Untapped non soddisfa i requisiti dei
dataset pubblici 17Lands ammessi per i bot. I due voti Draftsim cambiati sono
confronti di presentazione; i valori adottati `score` e `community` restano
invariati. Le letture precedenti delle due carte rimangono nei dati.

Review Opus, decisioni, versione e modello effettivo sono registrati in
`reviews/star-trek-20261107/`; gli input completi e le risposte grezze restano
in `docs/local/reviews/star-trek-20261107/`. Un rifiuto tecnico non viene contato
come review. Nessuna modifica alla pipeline.

Gli esiti locali e i limiti sono in [verification.json](verification.json).
`captures/selected-filters.json` verifica le etichette dei controlli chiusi
Untapped: Premier Draft, Sealed, Latest Event e i ranghi attivi, escludendo
le opzioni dei menu. Non si deduce il filtro dalla presenza di parole nel corpo.
I rapporti `qa-*.json` e le due immagini `browser-genesis-*.png` documentano
i controlli browser di questa versione; non sono misure di forza competitiva.
