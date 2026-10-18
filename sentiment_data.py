"""Attributed qualitative snapshot; never converted into numeric card ratings."""
SOURCES = {
    'oculus': ('Reddit · discussione Mindseeker Oculus', 'https://www.reddit.com/r/magicTCG/comments/1wh6531/fra_mindseeker_oculus_weeklymtg/', 'utenti'),
    'cyclers': ('Reddit · landcycler comuni', 'https://www.reddit.com/r/magicTCG/comments/1wgbfue/fra_common_basic_landcyclers_hexhaven_battalion/', 'utenti'),
    'colors': ('Reddit · prime impressioni sui colori', 'https://www.reddit.com/r/lrcast/comments/1wkrclc/pre_prerelease_talk_what_are_the_best_and_worst/', 'utenti'),
    'unsummon': ('Reddit · Unsummon e Battalion', 'https://www.reddit.com/r/magicTCG/comments/1wh6sua/fra_cryotheory_adept_unsummon_hexhaven_battalion/', 'utenti'),
    'twin': ('Reddit · discussione Twin', 'https://www.reddit.com/r/lrcast/comments/1wh9gkq/you_can_literally_splinter_twin_combo_people_in/', 'utenti'),
    'hosers': ('Reddit · rimozioni vincolate ai colori', 'https://www.reddit.com/r/lrcast/comments/1wgclrw/so_reality_fracture_has_a_circle_of_removal/', 'utenti'),
    'pia': ('Reddit · entusiasmo Commander', 'https://www.reddit.com/r/EDH/comments/1wnibi7/reality_fractures_uncommons_are_seriously_pushed/', 'utenti'),
    'draftsim': ('Andrew Quinn · Draftsim', 'https://draftsim.com/mtg-fra-limited-set-review/', 'recensione'),
    'black': ('J2SJosh · Arena Zone, nero', 'https://mtgazone.com/reality-fracture-fra-limited-set-review-black/', 'recensione'),
    'gold': ('J2SJosh · Arena Zone, multicolore', 'https://mtgazone.com/reality-fracture-fra-limited-set-review-multicolor/', 'recensione'),
    'removal': ('LimitedMTG · rimozioni', 'https://limitedmtg.com/reality-fracture/removal-guide/', 'recensione'),
    'precon': ('PreconForge · guida Limited', 'https://preconforge.com/reality-fracture-draft-sealed-guide-best-archetypes-commons-and-uncommons/', 'recensione'),
}
# name | sentiment | breadth | summary | source ids | editorial attention
ROWS = [
    ('Mindseeker Oculus', 'molto-positivo', 'Giudizi favorevoli ripetuti', 'Candidata fra le migliori comuni; apprezzati vantaggio carte e Jace. Alcuni ridimensionano i paragoni con creature volanti.', ['oculus'], True),
    ('Hexhaven Battalion', 'molto-positivo', 'Giudizi favorevoli ripetuti', 'Paragoni favorevoli con Imperial Oath; piacciono pedine e landcycling. Il doppio bianco invita a cautela sullo splash.', ['cyclers'], True),
    ('Surgical Precision', 'positivo', 'Pochi riscontri', 'Rimozione promettente anche per lifegain: previsione preliminare, non consenso consolidato.', ['colors'], True),
    ('Campus Crier', 'positivo', 'Riscontri preliminari', 'Apprezzata come giocata iniziale proattiva e per mettere pressione ai Jace avversari.', ['colors'], False),
    ('Unflinching Hortimancer', 'condizionato', 'Pochi riscontri', 'Buon costo due se il pool sostiene il guadagno di punti vita.', ['colors'], False),
    ('Awaken the Inferno', 'positivo', 'Riscontri preliminari', 'Il landcycling aumenta la flessibilità della rimozione costosa.', ['cyclers'], False),
    ('Undulating Witness', 'positivo', 'Evidenza debole', 'Alcuni apprezzamenti sulla giocabilità; esclusi i commenti sulla sola illustrazione.', ['cyclers'], False),
    ('Vinelasher Adept', 'misto', 'Opinioni contrastanti', 'Dubbi sull’efficienza, apprezzamenti per flessibilità e impiego nei mazzi ramp.', ['cyclers'], False),
    ('Apex Witchstalker', 'misto', 'Pochi riscontri', 'Accoglienza tiepida: dubbi sulla potenza nonostante l’interesse per il ciclo.', ['cyclers'], False),
    ('Unsummon', 'misto', 'Opinioni contrastanti', 'Piacciono i bersagli propri da riutilizzare; dubbi sul supporto al piano tempo.', ['unsummon', 'colors'], False),
    ('Divining Duelist', 'condizionato', 'Discussione centrata sulla combo', 'Interesse per Twin, ma giudizio ordinario da sola: l’entusiasmo per la combo non prova forza generale.', ['twin'], False),
    ('Refute Destiny', 'misto', 'Discussione sul ciclo', 'Dibattito sul main deck per i Jace; prevale prudenza. Considerarla soprattutto per il sideboard.', ['hosers'], False),
    ('Terminal Criticism', 'misto', 'Discussione sul ciclo', 'Bersagli potenzialmente frequenti, ma rischio di carta morta; valutare il matchup.', ['hosers'], False),
    ('Precise Redaction', 'sideboard', 'Discussione sul ciclo', 'Orientamento sfavorevole al main deck alla cieca; considerare dopo aver visto i bersagli.', ['hosers'], False),
    ('Essence Burn', 'sideboard', 'Discussione sul ciclo', 'Non trattarla come rimozione universale: il valore dipende dai bersagli avversari.', ['hosers'], False),
    ('Flourishing Grapple', 'sideboard', 'Discussione sul ciclo', 'Da considerare per il sideboard in funzione dei colori avversari.', ['hosers'], False),
    ('Pia, Aether Ascetic', 'insufficiente', 'Entusiasmo soprattutto Commander', 'Apprezzamento Commander e un giudizio critico Limited: sentiment Sealed insufficiente.', ['pia'], False),
    ('No Admittance', 'positivo', 'Recensione, non consenso social', 'Apprezzata per rimozione economica e contributo a Jace.', ['draftsim'], True),
    ('Last Gasp', 'positivo', 'Recensione, non consenso social', 'Interazione efficiente, utile anche durante il combattimento.', ['black'], True),
    ('Rank Rat', 'condizionato', 'Recensione, non consenso social', 'Sale nei mazzi sacrificio; meno convincente per aggredire.', ['black'], False),
    ('Void Extrapolator', 'condizionato', 'Recensione, non consenso social', 'Richiede supporto al cimitero; non è automaticamente un buon costo due.', ['black'], False),
    ('Theorix Metamage', 'condizionato', 'Recensione, non consenso social', 'Segnalata per alimentare il piano Dimir.', ['precon'], False),
    ('Prophesied End', 'molto-positivo', 'Recensione, non consenso social', 'Fra le prime rimozioni nella graduatoria dell’autore.', ['removal'], True),
    ('Multiply by Zero', 'molto-positivo', 'Recensione, non consenso social', 'Efficienza elevata; verificare i limiti sui bersagli nel testo della carta.', ['black'], True),
    ('Woodwork Prodigy', 'positivo', 'Recensione, non consenso social', 'Motore di accelerazione ripetibile.', ['draftsim'], False),
    ('Pia, Determined Rebuilder', 'positivo', 'Recensione, non consenso social', 'Più corpi e ulteriore utilità nei mazzi artefatti.', ['draftsim'], False),
    ('Way of the Healer', 'positivo', 'Recensione, non consenso social', 'Valorizza Jace producendo presenza sul campo.', ['draftsim'], False),
    ('Way of the Mentor', 'cauto', 'Recensione, non consenso social', 'Dubbi sulla possibilità di trovare una collocazione efficace.', ['draftsim'], False),
    ('Plan for All Outcomes', 'positivo', 'Recensione, non consenso social', 'Apprezzata l’unione di interazione e valore successivo.', ['draftsim'], False),
    ('Perfected Theory', 'cauto', 'Recensione, non consenso social', 'Ritenuta adatta soprattutto a un blu particolarmente aggressivo.', ['draftsim'], False),
    ('Craftwork Crusher', 'condizionato', 'Recensione, non consenso social', 'Impatto notevole, ma costo e requisiti di mana impegnativi.', ['gold'], False),
    ('Clash of Elements', 'positivo', 'Recensione, non consenso social', 'Apprezzata l’interazione a velocità istantaneo.', ['gold'], False),
    ('Primal Witchstalker', 'positivo', 'Recensione, non consenso social', 'Valore e sinergia cimitero senza richieste eccessive.', ['gold'], False),
    ('Mind Meanderer', 'positivo', 'Recensione, non consenso social', 'Piace la combinazione di interazione e minaccia evasiva.', ['gold'], False),
]

def enrich(cards):
    catalog = {c['name']: c for c in cards if c['set'] == 'FRA'}
    assert len({r[0] for r in ROWS}) == len(ROWS)
    for name, tone, breadth, summary, refs, attention in ROWS:
        card = catalog[name]
        assert card['rarity'] in ('common', 'uncommon') and not card['basic']
        sources = [dict(id=ref, label=SOURCES[ref][0], url=SOURCES[ref][1], kind=SOURCES[ref][2]) for ref in refs]
        card['sentiment'] = dict(tone=tone, breadth=breadth, summary=summary,
                                 sources=sources, kind=sources[0]['kind'], attention=attention)
    from international_sentiment import enrich as enrich_international
    observations = enrich_international(cards)
    from sentiment_update_20260924 import enrich as enrich_update
    refresh = enrich_update(cards)
    from sentiment_update_20260925 import enrich as enrich_regional
    regional = enrich_regional(cards)
    from sentiment_score import enrich as enrich_score
    enrich_score(cards)
    covered = [c['sentiment'] for c in cards if c.get('sentiment')]
    return dict(date='25 settembre 2026', isoDate='2026-09-25', covered=len(covered),
                regional=regional, scored=sum(s['index'] is not None for s in covered),
                userCards=sum(s['kind']=='utenti' for s in covered),
                reviewCards=sum(s['kind']=='recensione' for s in covered),
                mixedCards=sum(s['kind']=='misto' for s in covered),
                japaneseCards=sum('ja' in s['languages'] for s in covered),
                internationalObservations=observations + refresh['observations'] + regional['observations'], refresh=refresh,
                sourceCount=len({x['id'] for s in covered for x in s['sources']}))


def render_assets(html, root):
    for token, filename in [('STYLE', 'sentiment-style.css'), ('SCRIPT', 'sentiment-ui.js'), ('SECTION', 'sentiment-section.html')]:
        marker = '__SENTIMENT_' + token + '__'
        assert marker in html, marker
        html = html.replace(marker, (root / filename).read_text(encoding='utf-8'))
    return html
