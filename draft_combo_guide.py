"""Editorial draft packages: pick dependencies, practical sequences and limits."""
import html

PACKAGES = []


def add(title, colors, role, cards, mana, sequence, pick, risk):
    PACKAGES.append(dict(title=title, colors=colors, role=role, cards=cards,
                         mana=mana, sequence=sequence, pick=pick, risk=risk))


add('Surveil che pesca e fa crescere', 'U', 'Motore',
    ['Proft, Consulting Detective', 'Mindseeker Oculus'],
    'Proft: {1}{U}; Oculus: {2}{U}; poi {2} per ogni innescata pagata.',
    'Mindseeker Oculus fornisce Jace con quattro lealtà. Usa il −1 per surveil, poi paga {2}: Proft, Consulting Detective prende un segnalino e peschi. Puoi ripetere nei turni successivi finché hai lealtà.',
    'Con Proft, Consulting Detective già scelto, alza Mindseeker Oculus: sviluppa il campo e fornisce più attivazioni. Con il solo Mindseeker Oculus, Proft, Consulting Detective aggiunge il payoff. Non basta accumulare altre carte che fanno solo selezione.',
    'Il motore richiede mana libero e Jace difeso. Proft, Consulting Detective cresce ma non ha evasione: non trattarlo da solo come chiusura.')

add('Cadet e Thopter dalla stessa attivazione', 'W', 'Motore e chiusura',
    ['Saheeli, Consul of Oversight', 'Way of the Healer'],
    'Way: {3}{W}; Saheeli: {3}{W}{W}; ogni attivazione costa due lealtà.',
    'Con Saheeli, Consul of Oversight sul campo, usa il −2 concesso da Way of the Healer: crei un Cadet 2/2 e fai surveil. Saheeli, Consul of Oversight crea anche un Thopter 1/1 volante, se non ha già innescato quel turno.',
    'Con Saheeli, Consul of Oversight cerca Way of the Healer e fonti di empower come Keeper of the Quiet Hour: il primo pezzo produce corpi, il secondo ricarica Jace aggiungendo una creatura. Con Way of the Healer già presente, Saheeli, Consul of Oversight trasforma il valore a terra in pressione volante.',
    'Cinque lealtà finanziano due −2, non pedine per sempre. Saheeli, Consul of Oversight innesca al massimo una volta per turno; senza altre ricariche il motore si esaurisce.')

add('Ricaricare la Way senza consumare carte', 'W', 'Motore',
    ['Rescue Girl, First Responder', 'Way of the Healer'],
    'Rescue Girl: {2}{W}; Way: {3}{W}; ogni rilancio della Way costa quattro.',
    'In un tuo turno, tappa Rescue Girl, First Responder per riprendere Way of the Healer. Jace resta sul campo. Rilancia Way of the Healer per aggiungere cinque lealtà e usa il −2, se quel Jace non ha ancora attivato una fedeltà nel turno.',
    'Con Way of the Healer già scelta, Rescue Girl, First Responder sale perché rende ripetibile la ricarica. Prima del secondo pezzo assicurati di poter sviluppare il campo nei turni iniziali: il ciclo costa quattro mana ogni volta.',
    'Rescue Girl, First Responder deve poter tappare e può attivarsi soltanto nel tuo turno. Rigiocare la Way non azzera il limite di una fedeltà per Jace per turno.')

add('Un Drago volante a ogni rilancio', 'WR', 'Chiusura lenta',
    ['Kiora of Fire and Ashes', 'Rescue Girl, First Responder'],
    'Kiora: {4}{R}{R}; Rescue Girl: {2}{W}; ogni nuovo Drago tramite rilancio costa sei.',
    'Kiora of Fire and Ashes crea un Drago 5/5 volante entrando. In un tuo turno successivo, Rescue Girl, First Responder riprende Kiora of Fire and Ashes: il Drago resta. Rilancia Kiora of Fire and Ashes e crea un secondo Drago.',
    'Prendi Kiora of Fire and Ashes per la sua forza autonoma quando sostieni due rossi. Rescue Girl, First Responder sale se sei già bianco/rosso e hai altri ingressi da riutilizzare; non aggiungere un terzo colore soltanto per questo ciclo.',
    'È un investimento lento, con una rara. I nuovi Draghi non hanno rapidità; Rescue Girl, First Responder può essere rimossa prima di attivarsi.')

add('Un Cadet per turno, poi una squadra crescente', 'R', 'Motore e chiusura',
    ['Stingerquill Voxmancer', 'Command the Stage'],
    'Voxmancer: un mana rosso o nero; Command: {2}{R}; ogni ciclo in rosso costa quattro.',
    'Dal mantenimento successivo Stingerquill Voxmancer si prepara. Lancia Vicious Verse pagando {R}, poi Command the Stage pagando {2}{R}. Al mantenimento avversario recuperi Command the Stage. Ripeti: crei nuovi Cadet e metti segnalini sulle altre pedine Wizard.',
    'Con Command the Stage cerca Stingerquill Voxmancer per il danno ripetibile. Con Stingerquill Voxmancer cerca Command the Stage per trasformare il danno in campo e crescita. Il mana nero può pagare le magie ibride, ma Command the Stage richiede rosso.',
    'Stingerquill Voxmancer non entra preparato. Il ciclo richiede quattro mana per turno e non protegge automaticamente da un attacco avversario.')

add('Recuperare Command attaccando', 'BR', 'Motore',
    ['Screeching Soulbreaker', 'Command the Stage'],
    'Soulbreaker: {2}{B}; Command: {2}{R}.',
    'Attacca con Screeching Soulbreaker: la sua innescata infligge un danno senza dover colpire in combattimento. Nella seconda fase principale lancia Command the Stage; al mantenimento avversario lo recuperi.',
    'Con Command the Stage e mana nero, Screeching Soulbreaker offre un attivatore ripetibile già utile come volante e bloccante. Con Screeching Soulbreaker presente, Command the Stage aggiunge un motore per il finale.',
    'Devi poter attaccare: contro un volante più grande rischi di perdere Screeching Soulbreaker. Il danno dell’innescata avviene comunque prima dei blocchi.')

add('Danni ripetuti che fanno crescere la minaccia', 'B', 'Payoff',
    ['Massacre Girl, Most Wanted', 'Screeching Soulbreaker'],
    'Massacre Girl: {4}{B}; Soulbreaker: {2}{B}.',
    'Con Massacre Girl, Most Wanted sul campo, ogni attacco di Screeching Soulbreaker infligge un danno non da combattimento e mette un segnalino su Massacre Girl, Most Wanted prima dei blocchi.',
    'Con Massacre Girl, Most Wanted cerca Screeching Soulbreaker per una fonte ripetibile. Gideon the Oathless aggiunge danni quando l’avversario sviluppa creature o attiva fedeltà; Extended Absence rimuove e aggiunge un evento di danno.',
    'Massacre Girl, Most Wanted non ha evasione. Per superare i bloccanti cerca anche Medic’s Kitesail, oppure Tomik, Orzhov Lawmage se giochi bianco.')

add('Sacrifici, danni e crescita', 'WB', 'Motore e payoff',
    ['Edgar, Ancient Bloodlord', 'Massacre Girl, Most Wanted', 'Blessed Ghoul'],
    'Edgar: {W}{B}; Massacre Girl: cinque; ciclo completo del Ghoul: sei mana.',
    'Paga {2} a Edgar, Ancient Bloodlord e sacrifica Blessed Ghoul: Edgar, Ancient Bloodlord cresce e ottiene minaccia. Le morti attivano il guadagno vita e Massacre Girl, Most Wanted, che infligge un danno e cresce. Recuperare Blessed Ghoul costa tre, rilanciarlo uno.',
    'Con Edgar, Ancient Bloodlord cerca materiale sostituibile: Blessed Ghoul oppure Hexhaven Battalion, che fornisce tre Cadet. Massacre Girl, Most Wanted aggiunge danni al piano; non serve aspettare tutti e tre i pezzi per usare Edgar, Ancient Bloodlord.',
    'Il recupero costa molto mana. Non sacrificare una buona creatura soltanto per un segnalino se quel corpo ti serve per sopravvivere.')

add('La rimozione prepara un attacco volante', 'WB', 'Chiusura',
    ['Danitha, Spear of Agony', 'Tomik, Orzhov Lawmage', 'Your Fate Ends Here'],
    'Danitha: {2}{B}; Tomik: {1}{W}; rimozione: {2}{W}.',
    'Lancia Your Fate Ends Here su una creatura avversaria valida: Danitha, Spear of Agony prende un segnalino per il lancio. Con Tomik, Orzhov Lawmage pronto a tappare, dai volare a Danitha, Spear of Agony prima dei blocchi.',
    'Con Danitha, Spear of Agony, rimozioni mirate come Extended Absence aumentano sia controllo sia pressione. Con una minaccia che cresce ma resta bloccata, Tomik, Orzhov Lawmage risolve il problema dell’evasione.',
    'Bersagliare solo un planeswalker avversario non innesca Danitha, Spear of Agony. Tomik, Orzhov Lawmage richiede che il bersaglio abbia già un segnalino +1/+1.')

add('Vite che diventano crescita volante', 'W', 'Chiusura',
    ['Unflinching Hortimancer', "Medic's Kitesail"],
    'Creatura: {1}{W}; equipaggiamento: {2}; equipaggiare: {2}.',
    'Equipaggia Unflinching Hortimancer con Medic’s Kitesail. Attaccando guadagni una vita: Unflinching Hortimancer prende un segnalino prima dei blocchi e continua a crescere a ogni attacco.',
    'Con Unflinching Hortimancer cerca Medic’s Kitesail: fornisce sia attivatore ripetibile sia evasione. Con Medic’s Kitesail già presente, Unflinching Hortimancer sfrutta anche il guadagno vita, oltre al bonus di forza.',
    'Servono quattro mana complessivi per lanciare ed equipaggiare Medic’s Kitesail. Una rimozione in risposta a equipaggiare ti fa perdere tempo.')

add('Le creature successive fanno pescare', 'WG', 'Motore',
    ['Bloombrute', 'Greenhouse Propagator'],
    'Bloombrute: {2}{G}{W}; Propagator: {2}{G}.',
    'Con Bloombrute e Greenhouse Propagator sul campo, lancia un’altra creatura: guadagni una vita e peschi una carta. Greenhouse Propagator può anche aiutare a pagare le creature successive.',
    'Con Bloombrute cerca Greenhouse Propagator, una fonte ripetibile di vita. Con entrambi presenti, privilegia corpi utili come Vigorbloom Vanguard rispetto a solo guadagno vita: sviluppi il campo mentre alimenti il motore.',
    'Bloombrute pesca al massimo una volta per turno. Tre creature entrate nello stesso turno non significano tre pescate.')

add('Tre Cadet, tre eventi di crescita', 'WG', 'Payoff',
    ['Greenhouse Propagator', 'Unflinching Hortimancer', 'Hexhaven Battalion'],
    'Propagator: tre; Hortimancer: due; Battalion: {4}{W}{W}.',
    'Con Greenhouse Propagator e Unflinching Hortimancer sul campo, Hexhaven Battalion crea tre Cadet. Sono tre ingressi e quindi tre eventi di guadagno vita: Unflinching Hortimancer prende tre segnalini.',
    'Con il nucleo di guadagno vita, Hexhaven Battalion sale perché aggiunge tre corpi e tre attivazioni. Se hai già molti corpi ma nessun modo di passare, Medic’s Kitesail offre invece la chiusura volante.',
    'Sei mana e tre pezzi: valuta Hexhaven Battalion anche per i corpi autonomi. I nuovi Cadet non possono attaccare subito senza rapidità.')

add('Un battaglione che chiude lo stallo', 'W', 'Chiusura',
    ['Hexhaven Battalion', 'Shatterwing Pegasus'],
    'Battalion: {4}{W}{W}; Pegasus: {2}{W}; potenziamento: {4}{W}.',
    'Dopo aver creato tre Cadet con Hexhaven Battalion, in un turno successivo attiva Shatterwing Pegasus: i tre Cadet diventano 3/3 e Shatterwing Pegasus diventa 3/4 volante per il turno.',
    'Con Hexhaven Battalion e altri produttori di corpi, Shatterwing Pegasus aumenta il valore di tutta la squadra. Con Shatterwing Pegasus ma poche creature, prendi prima i corpi: il potenziamento non riempie il campo.',
    'Dodici danni sono soltanto il totale potenziale senza blocchi. Il potenziamento non dà volare né travolgere ai Cadet.')

add('Segnalini che mantengono il valore dopo uno scambio', 'W', 'Payoff',
    ['Yoshimaru, Beloved Companion', 'Graft Surgeon'],
    'Entrambi costano {2}{W}.',
    'Con Yoshimaru, Beloved Companion sul campo, Graft Surgeon entra con due segnalini anziché uno. Quando Graft Surgeon muore, i suoi due segnalini messi su Yoshimaru, Beloved Companion diventano tre.',
    'Con Yoshimaru, Beloved Companion cerca Graft Surgeon e Predictive Preparations: aumentano i segnalini per evento. Se il campo è già grande ma bloccato, Tomik, Orzhov Lawmage dà volare a una creatura con segnalini.',
    'Yoshimaru, Beloved Companion aggiunge uno, non raddoppia. Esilio e rimbalzo di Graft Surgeon evitano l’innescata di morte.')

add('Surveil prima del combattimento, crescita permanente', 'WU', 'Payoff',
    ['Desperate Futurescribe', 'Mindseeker Oculus'],
    'Futurescribe: {2}{W}{U}; Oculus: {2}{U}.',
    'Usa il −1 di Jace fornito da Mindseeker Oculus nella prima fase principale. All’inizio del combattimento Desperate Futurescribe mette un segnalino su un’altra tua creatura invece del solo +1/+1 temporaneo.',
    'Con Desperate Futurescribe cerca Mindseeker Oculus per selezione ripetuta e un corpo. Your Fate Ends Here può invece rimuovere un bloccante e fare surveil prima del combattimento.',
    'Il surveil deve essere avvenuto quando risolve l’innescata di Desperate Futurescribe. Non può potenziare se stesso.')

add('La pescata produce anche attaccanti', 'UR', 'Motore e chiusura',
    ['Saheeli, Jewel of Avishkar', 'Twinned Vision', "Chandra's Emberling"],
    'Saheeli: {2}{U}{R}; Vision: {1}{U/R}; flashback: {1}{U/R}{U/R} e uno scarto.',
    'Con Saheeli, Jewel of Avishkar sul campo, lancia Twinned Vision: crei un Thopter volante con rapidità e peschi. In un turno successivo il flashback crea un altro Thopter e pesca due scartando una carta come costo. Chandra’s Emberling, se presente, cresce a ogni lancio non creatura.',
    'Con Saheeli, Jewel of Avishkar cerca magie utili ed economiche come Twinned Vision e No Admittance. Chandra’s Emberling è un secondo payoff; senza minacce, un’altra magia di sola selezione non sostituisce il motore.',
    'Una copia creata direttamente in pila non è lanciata e non innesca queste abilità. Il flashback invece è un lancio.')

add('Rendere non bloccabile prima di potenziare', 'R', 'Chiusura',
    ['Tetsuko Umezawa, Pursuer', 'Eardrum Rattler', 'Blazing Crescendo'],
    'Tetsuko: {3}{R}; Rattler: {1}{R}; turno di chiusura: {1} più {1}{R}.',
    'Con le creature pronte, attiva Eardrum Rattler su Tetsuko Umezawa, Pursuer ancora con forza due. Lascia risolvere. Poi lancia Blazing Crescendo: fra prodezza e +3/+1, Tetsuko Umezawa, Pursuer diventa 6/6 con doppio attacco e non può essere bloccata.',
    'Con Tetsuko Umezawa, Pursuer già scelta, Eardrum Rattler risolve i blocchi e Blazing Crescendo aumenta molto il danno. Prendi i supporti se hanno altri bersagli utili: non costruire tutto su una sola copia di Tetsuko Umezawa, Pursuer.',
    'Dodici danni potenziali, non garantiti. Se potenzi prima che risolva Eardrum Rattler, la forza supera due e il bersaglio diventa illegale.')

add('Tocco letale che diventa rimozione', 'G', 'Interazione',
    ['Arcane Amphisbaena', 'Compel Brutality'],
    'Creatura: {1}{G}; istantaneo: {1}{G}.',
    'Scegli il modo creatura di Compel Brutality: Arcane Amphisbaena infligge il suo danno con tocco letale a una creatura avversaria. Non è una lotta: Arcane Amphisbaena non riceve danno dalla magia.',
    'Con Arcane Amphisbaena, Compel Brutality gestisce anche creature molto grandi. Con Compel Brutality, Arcane Amphisbaena offre difesa iniziale ed empower oltre alla sinergia; resta utile anche quando non peschi l’altro pezzo.',
    'Indistruttibile impedisce la distruzione da tocco letale. Se rimuovono Arcane Amphisbaena in risposta, non infligge danno. Tocco letale non distrugge i planeswalker.')

add('Empower che sviluppa risorse e minaccia', 'G', 'Payoff',
    ['Inspired Tethermage', "Tam's Resistance"],
    'Tethermage: tre; Resistance: due mana, pagabili con verde o blu.',
    'Con Inspired Tethermage sul campo, lancia Tam’s Resistance su di lui: un segnalino dalla magia e un altro dall’evento empower. Se Jace non era presente, entra con quattro lealtà e può spendere −3 per pescare, se non ha ancora attivato una fedeltà quel turno.',
    'Con Inspired Tethermage cerca carte empower che fanno già qualcosa di utile: Tam’s Resistance potenzia, Arcane Amphisbaena difende. Con molte fonti empower, Inspired Tethermage converte quelle risorse in forza sul campo.',
    'Empower quattro è un solo evento: Inspired Tethermage prende un segnalino dalla sua innescata, non quattro. Tam’s Resistance è una stregoneria.')

add('Accelerare e convertire Heartwood in Draghi', 'R', 'Chiusura lenta',
    ['Draconic Visitor', 'Woodwork Prodigy'],
    'Visitor: {3}{R}{R}; Prodigy: tre; Soul Tether: {2}{R}.',
    'Con Draconic Visitor sul campo e Woodwork Prodigy preparato, lancia Soul Tether: invece dell’Heartwood crei un Drago 5/5 volante. Nei mantenimenti successivi Woodwork Prodigy può prepararsi di nuovo.',
    'Con Draconic Visitor e rosso come colore principale, Woodwork Prodigy offre un produttore ripetibile. Prima di trovare Draconic Visitor, gli Heartwood accelerano le giocate costose: il supporto ha già un uso.',
    'Richiede una rara e tempo. Il Drago sostitutivo non produce mana; i nuovi Draghi non hanno rapidità. Non considerare questo l’unico piano del mazzo.')


def render(oracle):
    known = {name for c in oracle for name in [c['name'], c['name'].split(' // ')[0],
             *(f['name'] for f in c.get('card_faces', []))]}
    aliases = {'Chandra’s Emberling': "Chandra's Emberling", 'Medic’s Kitesail': "Medic's Kitesail", 'Tam’s Resistance': "Tam's Resistance"}
    names = sorted(known | set(aliases), key=len, reverse=True)
    import re
    pattern = re.compile('|'.join(re.escape(n) for n in names))

    def text(value):
        # Explicit preview targets for every named card, including spell faces.
        parts, last = [], 0
        for match in pattern.finditer(value):
            parts.append(html.escape(value[last:match.start()]))
            name = aliases.get(match[0], match[0])
            parts.append('<span class="card-reference" tabindex="0" role="button" data-card-preview="' +
                         html.escape(name, quote=True) + '" aria-label="Mostra ' + html.escape(name, quote=True) + '">' + html.escape(match[0]) + '</span>')
            last = match.end()
        return ''.join(parts) + html.escape(value[last:])

    rows = []
    for index, p in enumerate(PACKAGES):
        assert set(p['cards']) <= known, set(p['cards']) - known
        assert '\u2014' not in str(p)
        search = ' '.join([p['title'], p['colors'], p['role'], *p['cards'], p['pick']]).lower()
        fields = [('mana', 'Mana e tempi'), ('sequence', 'Sequenza di gioco'),
                  ('pick', 'Cosa prendere e quando sale'), ('risk', 'Limite da ricordare')]
        rows.append('<article class="draft-package" data-colors="' + p['colors'] + '" data-role="' + html.escape(p['role']) + '" data-search="' + html.escape(search, quote=True) + '"><h3>' + html.escape(p['title']) + '</h3><p class="small">' + html.escape(p['colors'] + ' · ' + p['role']) + '</p><p><strong>Hai uno di questi pezzi?</strong> ' + ' + '.join(text(c) for c in p['cards']) + '</p><p>' + text(p['pick']) + '</p><details' + (' open' if index == 0 else '') + '><summary>Sequenza, mana e limiti</summary>' + ''.join('<p><strong>' + label + ':</strong> ' + text(p[key]) + '</p>' for key, label in fields if key != 'pick') + '</details></article>')
    options = ''.join('<option value="' + pair + '">' + label + '</option>' for pair, label in [
        ('WU','Bianco/blu'),('WB','Bianco/nero'),('WR','Bianco/rosso'),('WG','Bianco/verde'),
        ('UB','Blu/nero'),('UR','Blu/rosso'),('UG','Blu/verde'),('BR','Nero/rosso'),('BG','Nero/verde'),('RG','Rosso/verde')])
    return _finish(rows, options, text)


def _finish(rows, options, text):
    # Keep all editorial paragraphs on the same card-preview path as package text.
    intro = text('Motore: produce risorse su più turni, come Proft, Consulting Detective con Mindseeker Oculus. Payoff: premia un’azione, come Massacre Girl, Most Wanted con il danno di Screeching Soulbreaker. Chiusura: converte il vantaggio in attacchi efficaci, come Tomik, Orzhov Lawmage con Danitha, Spear of Agony già provvista di un segnalino.')
    advice = text('Se hai già il motore e il problema sono i blocchi, Tomik, Orzhov Lawmage o Medic’s Kitesail possono servire più di un’altra carta che accumula risorse. Se hai Proft, Consulting Detective ma nessuna fonte affidabile di surveil, Mindseeker Oculus completa il piano. Senza i supporti, non prendere un payoff stretto sperando che tutto arrivi dopo.')
    return '<section id="draft-combos" class="report-section draft-combos"><div class="eyebrow">Dalla carta scelta al piano per vincere · 18 ottobre 2026</div><h2>Ho questa carta: quali combo cerco?</h2><p>Venti pacchetti da riconoscere mentre passano le buste. Cerca una carta che hai già, poi leggi quali pezzi aumentano di priorità. Valutazioni editoriali: confronta colori, curva, supporti già presi e qualità delle alternative.</p><p>' + intro + '</p><aside class="notice"><strong>Quando preferire il pezzo a un’altra buona carta?</strong> ' + advice + '</aside><div class="controls"><label>Ho questa carta / cerco un piano<input id="combo-search" type="search" placeholder="Proft, Kiora, sacrifici…"></label><label>I miei due colori<select id="combo-colors"><option value="">Tutti i colori</option>' + options + '</select></label><label>Mi manca<select id="combo-role"><option value="">Qualunque ruolo</option><option value="Motore">Un motore</option><option value="Payoff">Un payoff</option><option value="Chiusura">Una chiusura</option><option value="Interazione">Interazione</option></select></label><button type="button" id="combo-reset">Azzera filtri</button></div><p id="combo-count" role="status" aria-live="polite">20 pacchetti</p><div class="combo-grid">' + ''.join(rows) + '</div><p class="small">W bianco, U blu, B nero, R rosso, G verde. Il filtro mostra i pacchetti sostenibili nei due colori, inclusi quelli monocolore. Le sinergie non sono necessariamente combo infinite o vittorie garantite. Testi: snapshot Oracle del 16 ottobre 2026; riferimento per le interazioni: <a href="https://magic.wizards.com/en/news/feature/reality-fracture-release-notes" target="_blank" rel="noopener">note ufficiali Wizards</a>. Anteprime con mouse, tastiera e tocco. <a href="Reality-Fracture-Combo.html">Vedi anche la raccolta Combo del set</a>.</p></section>'
