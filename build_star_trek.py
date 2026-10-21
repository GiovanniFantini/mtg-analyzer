"""Offline Star Trek pages, built from dated and versioned preview inputs."""
import html
import json
import shutil
from pathlib import Path
from site_navigation import shell

ROOT = Path(__file__).resolve().parent
PAGES = {
    'set': ('Panoramica', 'index.html'),
    'gallery': ('Catalogo carte', 'catalogo.html'),
    'draft': ('Draft e pick', 'draft.html'),
    'pool': ('Pool e mazzo Sealed', 'sealed.html'),
    'simulator': ('Prova il mazzo', 'simulatore.html'),
    'combos': ('Sinergie e sequenze', 'sinergie.html'),
    'analysis': ('Analisi e box', 'analisi.html'),
    'discovery': ('Constructed', 'discovery.html'),
    'rules': ('Regole del formato', 'regole.html'),
    'method': ('Fonti e aggiornamenti', 'fonti.html'),
}
EXPANSION = {'name': 'Star Trek', 'code': 'TRK', 'pages': PAGES, 'groups': [
    ('Carte e set', ['set', 'gallery', 'analysis']),
    ('Limited', ['draft', 'pool', 'simulator', 'combos']),
    ('Constructed', ['discovery']), ('Riferimenti', ['rules', 'method'])]}
SOURCES = {
    'Contenuto e probabilità delle buste': 'https://magic.wizards.com/en/news/feature/collecting-star-trek',
    'Meccaniche Star Trek': 'https://magic.wizards.com/en/news/feature/star-trek-mechanics',
    'Booster Draft': 'https://magic.wizards.com/en/formats/booster-draft',
    'Pick-Two Draft': 'https://magic.wizards.com/en/formats/pick-two-draft',
    'Sealed Deck': 'https://magic.wizards.com/en/formats/sealed-deck',
    'Comprehensive Rules, 25 settembre 2026': 'https://media.wizards.com/2026/downloads/MagicCompRules%2020260925.txt',
    'Magic Tournament Rules, documento collegato da WPN': 'https://media.wizards.com/ContentResources/WPN/MTG_MTR_2026_Feb27_EN.pdf',
    'Policy di torneo e documenti WPN': 'https://wpn.wizards.com/en/rules-documents',
    'Galleria ufficiale': 'https://magic.wizards.com/en/products/star-trek/card-image-gallery',
    'Catalogo e testo delle carte, Scryfall': 'https://scryfall.com/sets/trk',
    'Stardates, Scryfall': 'https://scryfall.com/sets/sds',
}


def panel(title, body):
    return f'<section class="trk-panel"><h2>{title}</h2>{body}</section>'


def rules_compact():
    return '''<div class="trk-notice">Limited: almeno 40 carte, nessun limite di quattro copie se provengono dal tuo pool. Puoi aggiungere terre base normali. Le carte restanti sono il sideboard. <a href="regole.html">Regole e fonti</a></div>'''


def filters(discovery=False):
    return '''<div class="trk-controls"><label>Cerca nome, tipo o testo<input id="trk-search" type="search" placeholder="Es. station, Spock, draw"></label>
<label>Colore<select id="trk-color"><option value="">Tutti</option><option value="W">Bianco</option><option value="U">Blu</option><option value="B">Nero</option><option value="R">Rosso</option><option value="G">Verde</option><option value="C">Incolore</option><option value="M">Multicolore</option></select></label>
<label>Rarità<select id="trk-rarity"><option value="">Tutte</option><option value="common">Comune</option><option value="uncommon">Non comune</option><option value="rare">Rara</option><option value="mythic">Mitica</option></select></label>
<label>Gruppo<select id="trk-set"><option value="">TRK e SDS</option><option>TRK</option><option>SDS</option></select></label>
<label>Ordina<select id="trk-order"><option value="number">Numero</option><option value="name">Nome</option><option value="cmc">Valore di mana</option></select></label>
<button id="trk-reset" type="button">Azzera filtri</button></div>''' + ('''<label>Stato Scryfall al 21 ottobre<select id="trk-legality"><option value="">Nessun filtro</option><option value="standard">Standard</option><option value="pioneer">Pioneer</option><option value="modern">Modern</option><option value="commander">Commander</option></select></label>''' if discovery else '')


def catalog(discovery=False):
    return filters(discovery) + '''<p id="trk-count" role="status" aria-live="polite"></p><div id="trk-cards" class="trk-cards"></div><div class="trk-pager"><button id="trk-prev" type="button">Precedenti</button><span id="trk-page"></span><button id="trk-next" type="button">Successive</button></div>'''


def deck_tools():
    return '''<section class="trk-panel"><h2>Il tuo banco di costruzione</h2>
<label>Pool separato per attività<select id="trk-mode"><option value="sealed">Sealed</option><option value="draft">Draft</option><option value="picktwo">Pick-Two Draft</option></select></label>
<p>Aggiungi le copie dal catalogo. Usa i comandi Mazzo per scegliere quali giocare. Le carte del catalogo sono anteprime: verifica sul prodotto aperto quali appartengono al tuo evento.</p>
<div class="trk-controls" id="trk-basics"></div><p id="trk-deck-status" role="status" aria-live="polite"></p>
<div id="trk-curve" class="trk-curve" aria-label="Curva delle non terre"></div><p id="trk-sources"></p>
<div class="trk-controls"><button id="trk-export" type="button">Esporta pool e mazzo</button><label class="trk-file">Importa salvataggio JSON<input type="file" id="trk-import" accept="application/json,.json"></label></div>
<p id="trk-storage-status" role="status" aria-live="polite"></p><div id="trk-deck"></div></section>'''


def examples():
    return '''<div class="trk-example"><h3>Bianco e blu: riutilizzare un ingresso</h3><p>Con Open Communications nel cimitero, paga {2}{U} e riprendi Emergency Medical Hologram in mano. Peschi una carta, poi puoi rilanciare Emergency Medical Hologram per {W}: un altro segnalino +1/+1 e un punto vita. Sono quattro mana totali e una sequenza da fase principale, perché Open Communications è una stregoneria. Riprendere la creatura fa parte del costo: non puoi aspettare la risposta avversaria per scegliere se pagarla.</p></div>
<div class="trk-example"><h3>Blu e nero, con bianco: un dilemma che fa pescare</h3><p>Controlli Seven of Nine ({2}{U}{B}). Lanci Set Phasers to . . . ({W}) scegliendo un modo e un bersaglio legale. L’abilità di Seven of Nine si innesca durante il lancio; dopo il lancio viene messa sopra la magia, quindi normalmente peschi prima che questa risolva. Il bianco è un terzo colore: la sinergia va valutata insieme alle fonti disponibili, non basta possedere le due carte.</p></div>
<div class="trk-example"><h3>Qualsiasi colore: caricare una nave</h3><p>U.S.S. Enterprise-D, Galaxy-Class costa {3}. Con station puoi tappare un’altra tua creatura, anche appena entrata: i segnalini aggiunti sono pari alla sua forza. La prima aggiunta del turno attiva la nave e ti permette di giocare per quel turno la carta esiliata, pagando i costi e rispettando i normali tempi. A sette segnalini diventa una 4/5 con volare e cautela. Valuta se tappare la creatura ti lascia senza bloccanti.</p></div>'''


def rules_body():
    return panel('Scegli il formato del tavolo', '''<div class="trk-table-wrap"><table><thead><tr><th>Formato</th><th>Prodotto per giocatore</th><th>Scelte</th><th>Mazzo</th></tr></thead><tbody>
<tr><td>Booster Draft</td><td>3 Play Booster</td><td>Una carta per pick; passaggi sinistra, destra, sinistra</td><td>Almeno 40</td></tr>
<tr><td>Pick-Two Draft</td><td>3 Play Booster</td><td>Due carte per pick, o l’ultima rimasta; stessi passaggi. Pensato per quattro giocatori</td><td>Almeno 40</td></tr>
<tr><td>Sealed</td><td>6 Play Booster</td><td>Costruisci con il pool aperto, senza draft</td><td>Almeno 40</td></tr></tbody></table></div>
<p>Le terre base normali si possono aggiungere liberamente. In Limited puoi usare tutte le copie aperte o draftate di una carta. Il resto del pool costituisce il sideboard: il limite di 15 non si applica. Riferimenti: CR 100.2b e 100.4b; MTR 7.1 e 7.2.</p>
<p>Le Stardates SDS aperte nei Play Booster sono utilizzabili in quel Draft o Sealed. Questo non le rende automaticamente legali in Standard. Promo e carte di altri prodotti non entrano nel pool soltanto perché riportano Star Trek: segui il prodotto previsto dall’evento. Il Prerelease Pack include anche una rara o mitica promo; verifica le istruzioni dell’evento.</p>''') + panel('Meccaniche del set', '''<dl class="trk-definitions">
<dt>Beam me up</dt><dd>Rilanci dal cimitero pagando il costo indicato e riprendendo una tua creatura. La magia viene poi esiliata. Restano validi i tempi del suo tipo.</dd>
<dt>Face a dilemma</dt><dd>Scegliere uno o più modi fa affrontare un dilemma. Scegliere soltanto un bersaglio non basta.</dd>
<dt>Federation</dt><dd>Conta i tipi di creatura tra le tue creature non Borg, non il numero di creature. Hoshi Sato, Exolinguist usa questo conteggio quando risolve la sua abilità.</dd>
<dt>Strange new worlds</dt><dd>Conta i nomi diversi delle terre che controlli. Tre Forest e una Island danno due nomi; The Traveler usa questo conteggio.</dd>
<dt>Station</dt><dd>Attiva nella tua fase principale, a pila vuota. Tappi un’altra creatura; i segnalini restano e le soglie non li consumano. CR 702.184 e 721.</dd>
<dt>Assimilate</dt><dd>Segui l’effetto per acquisire la creatura, aggiungere un segnalino e renderla una creatura artefatto Borg, perdendo gli altri tipi di creatura.</dd></dl>
<p>Battlefront e seek out sono presentate nella guida ufficiale come meccaniche Commander: non sono archetipi Limited da presumere presenti nei Play Booster.</p><p><a href="sinergie.html">Leggi gli esempi con carte e sequenze</a>.</p>''') + panel('Mulligan, regole e torneo', '''<p>Il London mulligan fa rimescolare e pescare sette carte. Quando tieni, metti in fondo un numero di carte pari ai mulligan effettuati. Nel Limited uno contro uno il primo non è gratuito. CR 103.5.</p>
<p>Nei tornei Limited senza liste, MTR 7.3 consente normalmente di modificare il mazzo fra incontri, salvo diversa indicazione iniziale dell’organizzatore. Questo non vale a REL Competitive o Professional. MTR 7.7 disciplina la procedura di Draft tradizionale: il Pick-Two è una procedura distinta.</p><p>Le Comprehensive Rules descrivono il gioco. Le Magic Tournament Rules regolano il torneo. Per errori e rimedi, Regular usa JAR; Competitive e Professional usano IPG. In un evento chiama il judge: questo strumento controlla quantità e curva, senza assegnare penalità né certificare l’idoneità del pool.</p>
<p><a href="fonti.html">Apri i documenti e le fonti ufficiali</a>.</p><p>Riferimenti generali: CR 601.2 per il lancio e CR 603 per le innescate. Le CR collegate sono del 25 settembre, precedenti al set; per le nuove parole chiave usiamo la spiegazione ufficiale del 20 ottobre, in attesa del documento aggiornato.</p>''')


def analysis_body(collation):
    rows = []
    names = {'wildcard': 'Wildcard', 'rare_or_mythic': 'Rara o mitica', 'foil': 'Foil tradizionale', 'land': 'Terra'}
    for slot, values in collation['published_percentages'].items():
        cells = ''.join(f'<tr><td>{html.escape(group)}</td><td>{"&lt;1" if rate is None else str(rate).replace(".", ",")}%</td></tr>' for group, rate in values.items())
        rows.append(f'<details><summary>{names[slot]}</summary><div class="trk-table-wrap"><table><thead><tr><th>Gruppo</th><th>Frequenza pubblicata</th></tr></thead><tbody>{cells}</tbody></table></div></details>')
    return panel('Analisi del catalogo disponibile', '<p>Le distribuzioni descrivono soltanto le carte già pubblicate, incluse varianti e prodotti diversi. Non sono frequenze nelle buste.</p><div id="trk-statistics"></div>') + panel('Box Play: dati per il modello', '''<p>30 buste da 14 carte. Una Stardates non foil ogni 25 buste, cioè 1,2 in media per box. Il numero medio non garantisce una carta in ogni box.</p>
<p>Valore atteso e probabilità di profitto: non disponibili. Mancano prezzi e catalogo completo. La soglia di vendita prevista è strettamente &gt;0,10 €. I prezzi mancanti non valgono zero.</p>
<p>Le percentuali sono arrotondate. &lt;1% è un limite, non 0% e non 1%. Non convertiamo gli intervalli di sensibilità in probabilità di guadagno.</p>
<p>Due punti da verificare: l’ambito delle percentuali degli slot comuni/non comuni e la presenza delle terre Away Team foil. La descrizione del trattamento e lo slot terra non concordano su queste ultime. L’apertura simulata delle buste resta sospesa.</p>
<p>Legenda: main = cornice ordinaria; C = comune; U = non comune; R = rara; M = mitica. Le frequenze seguenti si riferiscono a ciascuno slot indicato.</p>''' + ''.join(rows))


def build(dest):
    data = json.loads((ROOT/'star-trek-cards-20261021.json').read_text(encoding='utf-8'))
    collation = json.loads((ROOT/'star-trek-format-20261021.json').read_text(encoding='utf-8'))
    n = len(data['cards'])
    tasks = ''.join(f'<a class="site-task" href="{url}"><span class="site-task-number">TRK / {html.escape(label)}</span><h3>{html.escape(label)}</h3><p>{description}</p><span class="site-task-link">Apri lo strumento →</span></a>' for key, description in [
        ('gallery', 'Cerca testo, colori e varianti nelle carte già rivelate.'), ('draft', 'Registra i pick, confronta le carte e costruisci il mazzo.'),
        ('pool', 'Separa pool e mazzo, aggiungi terre e controlla la curva.'), ('simulator', 'Prova una mano iniziale del mazzo che hai costruito.'),
        ('combos', 'Leggi sequenze concrete e i colori necessari.'), ('analysis', 'Distribuzioni del catalogo e dati ufficiali per il box.'),
        ('discovery', 'Controlla lo stato per formato e salva carte da seguire.'), ('rules', 'Draft, Pick-Two, Sealed e nuove meccaniche.'),
        ('method', 'Fonti, data degli snapshot e limiti degli strumenti.')]
        for label, url in [PAGES[key]])
    bodies = {
        'set': f'''<section class="site-hero"><div><p class="site-eyebrow">UN NUOVO SET AL TAVOLO</p><h1>Star Trek</h1><p class="site-lead">Dalle prime carte al tuo prossimo mazzo. Esplora l’espansione e prepara Draft e Sealed con gli strumenti dedicati.</p><a class="site-button" href="catalogo.html">Esplora le carte →</a></div><aside class="site-hero-note"><p>ANTEPRIMA / 21 OTTOBRE 2026</p><p>{n} carte distinte, {data['print_count']} stampe disponibili. Il catalogo è parziale.</p><p>Prerelease dal 6 novembre. Uscita il 13 novembre.</p></aside></section><div class="site-section-heading"><h2>Scegli il tuo percorso</h2></div><div class="site-task-grid">{tasks}</div>''',
        'gallery': panel('Le carte rivelate', '<p>Una voce per carta, con varianti nei dettagli. I nomi mostrano un’anteprima al passaggio del mouse, con la tastiera o al tocco. Puoi già registrare un pool di studio.</p><label>Aggiungi le copie a<select id="trk-mode"><option value="sealed">Pool Sealed</option><option value="draft">Pool Draft</option><option value="picktwo">Pool Pick-Two</option></select></label><p><a href="sealed.html">Apri il banco di costruzione</a></p>' + catalog()),
        'draft': rules_compact() + panel('Draft tradizionale o Pick-Two', '<p>Tre buste a testa. Nel Draft prendi una carta per passaggio; nel Pick-Two ne prendi due. Non scambiare le due procedure. Seleziona il pool Draft o Pick-Two qui sotto.</p><p>Non ci sono ancora statistiche di vittoria o una graduatoria dei pick. Il confronto mostra testo e costi: le valutazioni restano da costruire sul set completo.</p>') + panel('Confronta due carte', '<div class="trk-controls"><label>Prima carta<select id="trk-compare-a"></select></label><label>Seconda carta<select id="trk-compare-b"></select></label></div><div id="trk-compare" class="trk-cards"></div>') + deck_tools() + panel('Aggiungi i tuoi pick', catalog()) + panel('Prime linee da studiare', examples()),
        'pool': rules_compact() + deck_tools() + panel('Aggiungi le copie al pool', catalog()),
        'simulator': rules_compact() + panel('Prova le mani del tuo mazzo', '''<p>Questa prova mescola il mazzo costruito nel pool scelto. Non apre buste e non simula una partita o un avversario.</p><label>Usa il mazzo<select id="trk-mode"><option value="sealed">Sealed</option><option value="draft">Draft</option><option value="picktwo">Pick-Two Draft</option></select></label><p id="trk-deck-status" role="status"></p><a href="sealed.html">Modifica pool e mazzo</a><div class="trk-controls"><button id="trk-new-hand" type="button">Mescola e pesca sette</button><button id="trk-mulligan" type="button" disabled>Mulligan</button><button id="trk-keep" type="button" disabled>Tieni la mano</button><button id="trk-draw" type="button" disabled>Pesca una carta</button></div><p id="trk-hand-status" role="status" aria-live="polite">Costruisci un mazzo di almeno 40 carte per iniziare.</p><div id="trk-hand" class="trk-cards"></div><p>Per il mulligan scegli le carte da mettere in fondo, nell’ordine desiderato, poi tieni. La pesca successiva è manuale: se inizi tu, salta normalmente la prima sottofase di acquisizione.</p>''') + panel('Apertura delle buste', '<p>In attesa del catalogo completo e della verifica delle ambiguità di collazione. Una selezione casuale dalle sole anteprime non rappresenterebbe un Play Booster.</p>'),
        'combos': panel('Sinergie documentate dalle carte', '<p>Prime linee di gioco basate sul testo disponibile al 21 ottobre. Non sono combo infinite né archetipi completi del formato.</p>' + examples()),
        'analysis': analysis_body(collation),
        'discovery': panel('Carte da seguire per il Constructed', '<p>Il set non è ancora uscito. TRK è annunciato per Standard e gli altri formati principali; SDS e TRC non conferiscono da soli legalità in Standard o Pioneer. Le ristampe possono essere già legali tramite altre edizioni.</p><p>Il filtro mostra solo le carte che Scryfall indica già come legal o restricted nel formato scelto, alla data dello snapshot. Non è una previsione della legalità all’uscita. Non abbiamo ancora risultati di torneo del nuovo set.</p>' + catalog(True)),
        'rules': rules_body(),
        'method': panel('Stato dei contenuti', f'''<p>Rilevazione del 21 ottobre 2026: {n} carte distinte, {data['print_count']} stampe. Catalogo TRK e SDS incompleto. Ogni carta include un collegamento al testo Scryfall.</p><ul><li>Disponibili: ricerca, confronto, pool distinti per formato, costruzione, curva, importazione ed esportazione, mani iniziali e osservate.</li><li>In attesa: apertura fedele delle buste, graduatorie dei pick, archetipi completi, metagame osservato e ricavo atteso del box.</li><li>Prezzi: nessun valore EUR negli snapshot. Nessun minimo Cardmarket verificato in questa rilevazione.</li></ul><p>I dati rimangono nel browser: l’esportazione contiene versione, set e modalità. Il sito non invia il pool a un server.</p><p>Idoneità Limited delle singole carte ancora da verificare sul prodotto: in anteprima il campo booster di Scryfall non è sufficiente. Il controllo del mazzo verifica solo le quantità registrate e il minimo di 40 carte.</p>''') + panel('Fonti verificate', '<ul>' + ''.join(f'<li><a href="{url}" target="_blank" rel="noopener">{html.escape(label)}</a></li>' for label, url in SOURCES.items()) + '</ul><p>Le fonti ufficiali discordano sulla data della galleria completa: il calendario anteprime indica 30 ottobre, Collecting riporta 30 novembre. La discrepanza resta aperta.</p><p><a href="star-trek-cards-20261021.json" download>Scarica lo snapshot carte</a> · <a href="star-trek-format-20261021.json" download>Scarica i dati di collazione</a></p>'),
    }
    for key, (title, filename) in PAGES.items():
        intro = '' if key == 'set' else f'<div class="site-page-intro"><p class="site-eyebrow">STAR TREK / TRK + SDS</p><h1>{html.escape(title)}</h1><p>Anteprima aggiornata al 21 ottobre 2026.</p></div>'
        notice = '<div class="trk-banner">Catalogo parziale · I dati mancanti non sono valutazioni negative. <a href="fonti.html">Disponibilità e fonti</a></div>'
        content = f'''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Star Trek · {html.escape(title)} | MTG Analyzer</title><meta name="description" content="Star Trek: {html.escape(title)}. Strumenti Limited e regole con dati di anteprima del 21 ottobre 2026."><link rel="stylesheet" href="star-trek.css"><link rel="stylesheet" href="card-hover.css"></head><body><main>{intro}{notice}{bodies[key]}<noscript><p>Le regole e le guide sono leggibili senza JavaScript. Catalogo e strumenti interattivi richiedono JavaScript.</p></noscript></main><footer>Progetto indipendente. Magic: The Gathering e Star Trek appartengono ai rispettivi titolari. <a href="fonti.html">Fonti e metodo</a></footer><script src="star-trek-data.js"></script><script src="star-trek.js"></script><script src="card-hover.js"></script></body></html>'''
        (dest/filename).write_text(shell(content, key, expansion=EXPANSION), encoding='utf-8')
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    (dest/'star-trek-data.js').write_text('const DATA = '+payload+';\n', encoding='utf-8')
    for filename in ['star-trek.css', 'star-trek.js', 'card-hover.css', 'card-hover.js', 'star-trek-cards-20261021.json', 'star-trek-format-20261021.json']:
        shutil.copy2(ROOT/filename, dest/filename)
