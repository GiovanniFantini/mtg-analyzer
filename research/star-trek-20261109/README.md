# Star Trek, aggiornamento del 9 novembre 2026

Catalogo attivo: 341 identità TRK/SDS e 616 stampe. Le 336 carte non base hanno fasce editoriali separate per Draft e Sealed, motivazione, ruolo previsto, condizioni, fiducia qualitativa e supporti. Le cinque terre base hanno funzione di mana esplicita e non un voto di potenza. Le 30 SDS sono analizzate subordinatamente alla loro ammissione nello specifico evento: nessuna probabilità di collazione è stata inventata.

La guida completa usa il renderer condiviso, ricerca e filtri per contesto, colore, rarità e fascia. Le analisi sono leggibili anche senza JavaScript. Il catalogo mostra gli stessi giudizi nelle schede delle carte, accanto alle recensioni attribuite.

## Prove e limiti

- J2SJosh: 306 voti Draft 0–5, tutti ricontrollati. Andrew Quinn: 336 voti Limited 0–10, tutti ricontrollati. Nessun cambiamento rispetto al 7 novembre e nessuna media fra autori. Il voto Limited condiviso non diventa un voto Sealed distinto.
- Limited Library: dataset datato 6 novembre, 793 voti espliciti su 306 carte TRK: Nizzahon 299, Limited Level-Ups 293, Limited Resources 201. Otto inferenze escluse. Aggregatore secondario; video originali collegati, non trascritti indipendentemente. L'indice ufficiale di Limited Resources conferma l'esistenza dell'episodio 878, non la trascrizione di ogni voto.
- Bryan Hohns (Veveil), Draftsim: recensione Sealed del 5 novembre, 135 categorie qualitative originali per rare, mitiche e SDS. Due valutazioni di cicli espanse sui membri verificati. Le categorie sono conservate senza convertirle in numeri o voti Draft. Gli alias SDS derivano dalla recensione che esplicita il nome canonico; il refuso Russel/Russell viene registrato nel normalizzatore.
- MTGsold: confronto supplementare con firma pseudonima, aggiornato il 6 novembre. Voti trascritti, senza riprodurre l'articolo o adottarli come consenso, dati di gioco o recensione di un esperto identificato.
- MTG Rocks: impressioni di Riley Hicks del 5 novembre sull'early access, non risultati del weekend né campioni statistici. La raccomandazione sulle terre e sui costi alti rimane un'ipotesi contestuale. Ensign Pavel Chekov esilia, non fa macinare: Bruvac non raddoppia quell'effetto.
- Wizards: calendario Arena, meccaniche e release notes ricontrollati. Station può tappare una creatura appena entrata, soltanto come stregoneria. Verificati i modi di Kobayashi Maru Scenario, il sacrificio obbligatorio di The City on the Edge of Forever e gli effetti copia di Gwyndala.
- Scryfall: verificate tutte le 341 identità, costi, forza/costituzione e legalità. Aggiornate 296 legalità rispetto al 2 novembre; questo non implica disponibilità su Arena o risultati di torneo. Conservata la correzione documentata del reminder di Mirror Universe Intrusion. Nessuna modifica ai testi funzionali, alle politiche dei bot o alla collazione.

Le acquisizioni dei siti non usate per nuove estrazioni restano acquisition_only. Una pagina scaricata non è una fonte letta o integrata. Le prove estese precedenti mantengono date e attribuzioni; questa acquisizione non dichiara un censimento completo di Internet o del metagame.

## Correzione delle WR

Rilette tutte le 322 righe Draft e 318 Sealed pubbliche di Untapped. WR in mano, WR nella mano iniziale e volume identici al 7 novembre. La fonte continua a indicare esclusivamente Early Access del 4 novembre: 1.800 e 890 partite complessive, nessun denominatore GIH esatto e margini molto ampi. La trascrizione corretta non rende i valori adatti a scegliere le carte.

Gli snapshot e i tier originali rimangono nei JSON pubblici con assessmentEligibility experimental_only. Sono esclusi da filtri e ordinamenti ordinari, anche nella vista WR compatibile. Il catalogo ne spiega il motivo. Nessun voto editoriale viene ricavato da queste WR e nessuna statistica mancante viene riempita con una stima. Le richieste HEAD ai dataset pubblici 17Lands rispondono 403: un limite d'accesso, non prova dell'inesistenza dei dati. Arena apre il 10 novembre, dopo questa acquisizione.

## Giudizi editoriali e revisione

Le 201 comuni e non comuni vengono riesaminate con le stesse ancore delle rare: il controllo iniziale aveva individuato un uso troppo largo della fascia Solida nelle schede del 3 novembre. I nuovi giudizi sostituiscono quelli precedenti; lo snapshot storico resta conservato. La distribuzione per rarità e contesto è dichiarata nella copertura, senza imporre quote artificiali alle fasce. Le 135 analisi mancanti sono contributi editoriali con Opus, successivamente controllati contro Oracle e fonti: il modello non è una fonte indipendente e non fornisce partite osservate. I contributi e il modello effettivo sono registrati in reviews/star-trek-20261109; prompt e risposte grezze restano nella cartella privata ignorata docs/local/reviews.

La fiducia indicata riguarda la solidità del giudizio editoriale e delle condizioni, non una probabilità di vittoria. Le fasce possono divergere fra autori o fra Draft e Sealed. Bassa fiducia e supporto necessario sono informazioni utilizzabili, non prestazioni certificate. La review Opus valuta la pubblicabilità di una guida editoriale completa, senza trasformarla in una classifica statisticamente validata.

Prezzi Cardmarket conservati al 27 ottobre. Il corpus dei tornei conserva la data del 28 ottobre e non è presentato come acquisizione del weekend. Le analisi Constructed e Commander precedenti mantengono il proprio contesto. La build resta offline; l'acquisizione di nuove prove è distinta dall'integrazione.

## Stato della review

Primo giro Opus: 16 rilievi, con decisioni tracciate e correzioni. Il blocco sui criteri diversi fra rarità ha portato al riesame integrale delle 201 comuni e non comuni. La richiesta finale sulla versione corretta è stata rifiutata dal servizio con HTTP429 usage_limit_reached, ripristino dichiarato alle 13:40 Europe/Rome del 9 novembre. Non è una review eseguita e non è un via libera. Il candidato resta locale; nessun push in produzione prima dell’esito Opus richiesto.

Per riprendere senza sovrascrivere acquisizioni o giri precedenti: `python reviews/star-trek-20261109/review.py 3`. Lo script seleziona l’ultima review effettivamente eseguita e include le decisioni di correzione; la chiamata rifiutata non viene contata come esito del modello. Il push resta subordinato alla chiusura dei rilievi fondati.
