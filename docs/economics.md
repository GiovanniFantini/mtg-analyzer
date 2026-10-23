# Prezzi e valore atteso dei box

Procedura da leggere per aggiornamenti economici e calcoli di ricavo. Il contratto per l'analisi completa delle carte parte dalla skill [mtg-research](../.agents/skills/mtg-research/SKILL.md).

Per integrare i dati usare il [contratto di prospects e prezzi](architecture.md#analisi-per-carta-e-prezzi): `cards[].prospects.price`, `prices.json.references` e registro delle fonti hanno ruoli distinti. Non usare il resoconto storico come definizione dei campi correnti.

## Rilevazione dei prezzi

Usare esclusivamente Cardmarket per nuove valutazioni e aggiornamenti. Di norma acquisire il minimo richiesto `From` in euro; conservare prodotto/stampa, variante, finitura, data, URL e filtri effettivi. Tenere distinti `From`, Price Trend, medie e ricavo realizzato. Un minimo senza filtro di finitura non è un prezzo non foil o foil. Lingua, condizioni, paese del venditore e spedizione restano espliciti; non attribuire filtri non applicati.

Se il lettore web riceve 403, provare la normale navigazione nel browser, rispettando i limiti di accesso. Dati ancora bloccati restano mancanti. Scryfall può fornire Oracle, immagini, identità e legalità, mai sostituire un prezzo Cardmarket mancante. Gli snapshot economici storici misti restano archiviati con la propria metodologia.

Confrontare soltanto prodotto, metrica e filtri omogenei. Valori storici esclusi da una soglia e finiture non rilevate restano mancanti, non zero. Separare cambiamenti di prezzi, fonti e modello. Dove il confronto non è possibile dichiararlo.

Quando la scheda prodotto viene letta dopo il listino, a parità verificata di prodotto, metrica e filtri, usare quella lettura diretta successiva come riferimento attivo e conservare entrambe le osservazioni negli snapshot. Registrare l'ordine delle acquisizioni: questa precedenza non vale automaticamente per una scheda più vecchia di un listino nuovo, né consente confronti fra finiture o metriche diverse. Se identità, filtri o cronologia non sono verificabili, mantenere esplicita l'incertezza.

## Calcolo del box

1. Cercare e leggere snapshot e JSON più recenti, comprese osservazioni e analisi per carta, senza limitarsi a una proprietà chiamata `findings`. La data di ricerca non attesta un aggiornamento completo del modello.
2. Identificare prodotto, numero di buste, lingua, costo totale confermato e soglia di vendita. Per il contesto personale Reality Fracture leggere `docs/local/reality-fracture-box.md`, se presente, senza richiedere di nuovo i dati già registrati.
3. Verificare la collazione ufficiale e separare percentuali pubblicate da ipotesi. Escludere trattamenti appartenenti ad altri prodotti. Controllare copertura di base, varianti ammesse, foil e carte ospiti.
4. Non aggiornare il valore atteso del box con una rilevazione che non copre le finiture e varianti necessarie. Mantenere mancanti, zeri osservati e valori esclusi dalla soglia distinti.
5. Verificare le commissioni correnti; calcolare lordo, commissioni, netto e differenza dal costo. Dichiarare ipotesi di vendita, costi esclusi e arrotondamenti. Il modello storico assume vendita di tutte le carte sopra soglia e non include materiali o tempo.
6. Spiegare scarti inattesi verificando calcolo e copertura, con esempi di carte e versioni. Gli intervalli di sensibilità del valore atteso non sono intervalli di confidenza sul ricavo di un box e non dimostrano probabilità di profitto.
7. Salvare input e risultati datati senza sovrascrivere gli snapshot precedenti, con procedimento riproducibile. Distinguere analisi privata, integrazione nel sito e pubblicazione verificata. I file `ev-*` sono esclusi da Git.

## Prospettive delle singole

Collegare gli scenari a domanda di gioco documentata, offerta delle ristampe e movimenti Cardmarket verificati. Separare osservazioni e scenari condizionali con orizzonte e confidenza espliciti. Non inventare target, liquidità, volumi o probabilità di rialzo/profitto. Aggiornare prezzi delle schede, ricalcolare il box e pubblicare sono risultati distinti.

Quando viene chiesto se tutti i prezzi sono aggiornati, riportare copertura per base, varianti, foil e ospiti, date, filtri e lacune, specificando la destinazione dell'aggiornamento. Un prezzo di prodotto senza filtro non certifica entrambe le finiture.
