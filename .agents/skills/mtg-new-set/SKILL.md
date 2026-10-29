---
name: mtg-new-set
description: Integrare una nuova espansione MTG e riusare le fonti e le procedure dei set esistenti, con inventario delle lacune per funzionalità. Non serve per il solo aggiornamento di prezzi o recensioni di un set già presente.
---

# Nuova espansione senza motori dedicati

I percorsi dei comandi sono relativi alla radice del repository. Questa skill coordina l'inserimento di un set; per acquisire e interpretare le fonti applicare anche [mtg-research](../mtg-research/SKILL.md). Leggere [architettura](../../../docs/architecture.md), manifest e schemi correnti prima di creare i documenti. Il riferimento operativo delle fonti è [references/sources.md](references/sources.md).

## Prima di cercare

1. Identificare slug, codice, prodotti, stato delle anteprime e perimetro delle carte, distinguendo set principale, ospiti e Commander. Cercare i dati già presenti prima di acquisirli di nuovo.
2. Eseguire l'inventario offline dei registri e degli audit di tutte le espansioni. Include Reality Fracture, URL originali, posizione dei riferimenti, stato registrato delle acquisizioni e snapshot locali disponibili:

   ```sh
   python .agents/skills/mtg-new-set/scripts/inventory_sources.py --output /percorso/temporaneo/fonti.json
   ```

   Il percorso di output è scelto dall'agente. Senza `--output` il JSON va su stdout. Lo script non contatta i provider e non certifica disponibilità o aggiornamento online. Per riusare una fonte cercare la pagina effettiva del nuovo set sul provider: sostituire il nome nell'URL non prova che esista.
   Le cartelle riconosciute seguono `<slug>-AAAAMMGG` con un eventuale suffisso descrittivo. Fra slug registrati sovrapposti prevale quello completo più specifico, evitando di attribuire al set principale gli audit di un prodotto con slug più lungo.
3. Leggere solo le categorie della matrice fonti necessarie al set. Per ogni funzionalità annotare documento/campo atteso, fonte candidata, acquisizione disponibile, copertura e dato ancora necessario. Date e campioni dei vecchi set non sono trasferibili.

## Integrare

- Creare `expansions/<slug>/expansion.json` e i dataset previsti da `schemas/` e `expansion_data.py`; registrare il manifest in `expansions.json`. Usare Atlas, route univoche e chiavi storage proprie; i template preview rimangono compatibilità storica. I manifest esistenti sono esempi di struttura, non dati da copiare insieme a rating, collazione o statistiche.
- Collegare catalogo e stampe con identità stabili; registrare le date separatamente per catalogo, legalità, rating e statistiche. Acquisire tutte le pagine dei cataloghi e controllare ospiti, facce e varianti. Il flag `booster` da solo non certifica la collazione.
- Conservare acquisizioni datate in `research/<slug>-<AAAAMMGG>/`, con URL, contesto, data e copertura. Conservare i vecchi snapshot. Usare gli importatori solo quando le assunzioni documentate in [sources.md](references/sources.md) sono vere.
- Completare i dati effettivi richiesti da ogni funzione. Se mancano, mantenere la lacuna esplicita: `collation: null` per prodotto incompleto; `null` per misura assente; nessun rating inventato. `features.*.requested` esprime una richiesta, non la disponibilità. Valutare ogni evento con il proprio prodotto.
- Nell'inventario includere separatamente WR Draft, WR Sealed e prospettive Standard/Pioneer/Modern/Pauper, seguendo `docs/statistics.md`. Controllare che il metagame contenga osservazioni effettive e che le carte siano abbinate al catalogo; un `discovery.json` vuoto o la sola presenza dei filtri non completa la ricerca Constructed. Etichettare i profili con sole misure di torneo senza presentarli come recensioni strategiche complete.
- Non creare builder del set, condizioni sul suo nome nei motori, database o interfacce amministrative. Se una nuova procedura di gioco non rientra nelle operazioni esistenti, descrivere il limite e realizzare solo l'estensione condivisa necessaria nel perimetro autorizzato.

## Chiudere con evidenze

Eseguire i controlli pertinenti di [verification.md](../../../docs/verification.md), compresi build offline, contratto, collazione, isolamento e salvataggi se coinvolti. Leggere `sets/<slug>/data/availability.json` prodotto dalla build e visitare le route del nuovo manifest; i test con route FRA fisse non certificano il nuovo set. Verificare ricerca, filtri, anteprime con mouse/tastiera/tocco e messaggi sui dati mancanti.

Consegnare una tabella per funzionalità: disponibile, dato mancante preciso, fonte da consultare, limite di acquisizione e prossima azione. Separare fonte conosciuta, pagina letta, dato acquisito e integrazione verificata. Nuovo set registrato non significa copertura completa. Commit, push e modifica delle pipeline restano soggetti alle autorizzazioni della sessione.
