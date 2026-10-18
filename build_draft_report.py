"""Build the draft report from the dated research and editable report blocks."""
import html
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).parent
ASSETS = 'draft-report-assets-20261016'
PAIRS = ['WU','UB','BR','RG','WG','WB','BG','UG','UR','WR']


def can_cast(cost, pair):
    """Mana symbols in the front spell only, including alternatives on hybrids."""
    for symbol in re.findall(r'\{([^}]+)\}', cost):
        if symbol.isdigit() or symbol in ['X', 'Y', 'Z']:
            continue
        alternatives = symbol.split('/')
        if any(x in pair or x.isdigit() or x == 'P' for x in alternatives):
            continue
        return False
    return True


def drilldown_data():
    snapshot = json.loads((ROOT / 'draft-drilldown-20261016.json').read_text(encoding='utf-8'))
    assert not snapshot['errors'], snapshot['errors']
    contexts, color_contexts = {}, {}
    fields = ['ever_drawn_win_rate', 'ever_drawn_game_count', 'opening_hand_win_rate',
              'opening_hand_game_count', 'drawn_win_rate', 'drawn_game_count',
              'avg_seen', 'avg_pick', 'drawn_improvement_win_rate',
              'never_drawn_win_rate', 'never_drawn_game_count']
    for key, record in snapshot['contexts'].items():
        if key.endswith(':colors'):
            rows = record['value']
            color_contexts[key.split(':')[0]] = rows
        else:
            rows = record['value']['data']
            assert len({c['name'] for c in rows}) == len(rows)
            contexts[key] = {c['name']: [c.get(f) for f in fields] for c in rows}
    guides = json.loads((ROOT / 'draft-archetypes.json').read_text(encoding='utf-8'))
    return dict(contexts=contexts, colors=color_contexts, guides=guides,
                retrieved=snapshot['retrieved_at_utc'], fields=fields)


def inline(text):
    text = html.escape(text.replace('\u2014', ':'))
    text = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    return text


def markdown(block):
    block = block.strip()
    lines = block.splitlines()
    if block.startswith('>'):
        clean = '\n'.join(re.sub(r'^> ?', '', x) for x in lines if '[!CALLOUT]' not in x)
        return '<aside class="notice">' + markdown(clean) + '</aside>'
    parts = re.split(r'\n\s*\n', block)
    if len(parts) > 1:
        return ''.join(markdown(part) for part in parts if part.strip())
    if block.startswith('|'):
        rows = [[inline(c.strip()) for c in line.strip().strip('|').split('|')] for line in lines]
        head = '<tr>' + ''.join('<th scope="col">' + x + '</th>' for x in rows[0]) + '</tr>'
        body = ''.join('<tr>' + ''.join('<td>' + x + '</td>' for x in row) + '</tr>' for row in rows[2:])
        return '<div class="tablewrap"><table><thead>' + head + '</thead><tbody>' + body + '</tbody></table></div>'
    if all(not x.strip() or x.startswith('- ') for x in lines):
        return '<ul>' + ''.join('<li>' + inline(x[2:]) + '</li>' for x in lines if x.startswith('- ')) + '</ul>'
    if re.match(r'^\d+\. ', block):
        start = int(re.match(r'^(\d+)\.', block)[1])
        return f'<ol start="{start}">' + ''.join('<li>' + inline(re.sub(r'^\d+\. ', '', x)) + '</li>' for x in lines if x.strip()) + '</ol>'
    return ''.join('<p>' + inline(p).replace('\n', '<br>') + '</p>' for p in block.split('\n\n') if p.strip())


def pick_guide(cards):
    guide = json.loads((ROOT / 'draft-pick-guide.json').read_text(encoding='utf-8'))
    lookup = {c['name']: c for c in cards}
    def card(name):
        assert name in lookup, f'Carta non trovata nella lista rapida: {name}'
        return '<button type="button" class="dd-card-link" data-name="' + html.escape(name, quote=True) + '">' + html.escape(name) + '</button>'
    def stat(name):
        c = lookup[name]
        rate = f"{c['gih'] * 100:.1f}".replace('.', ',') + '%' if c['gih'] is not None else 'N/D'
        sample = f"{c['n']:,}".replace(',', '.')
        return f'<small data-pick-stat hidden>GIH {rate} · {sample} osservazioni · {html.escape(c["cost"])}</small>'
    left = []
    for group in guide['groups']:
        rows = ''.join('<li>' + card(c['name']) + '<p>' + inline(c['why']) + '</p>' + stat(c['name']) + '</li>' for c in group['cards'])
        left.append('<section class="pick-tier"><h4>' + inline(group['title']) + '</h4><p class="small">' + inline(group['note']) + '</p><ul class="pick-list">' + rows + '</ul></section>')
    right = []
    for c in guide['counters']:
        right.append('<li>' + card(c['name']) + '<p>' + inline(c['why']) + '</p>' + stat(c['name']) + '<details><summary>Quali risposte prendere</summary><p><strong>Prima che risolva:</strong> ' + ', '.join(card(n) for n in c['before']) + '.</p><p><strong>Dopo la risoluzione:</strong> ' + ', '.join(card(n) for n in c['after']) + '.</p><p>' + inline(c['timing']) + '</p></details></li>')
    return '''<section id="pick-guide" class="report-section pick-guide">
<div class="eyebrow">La lista da tenere aperta mentre scegli</div><h2>Pick subito e counterpick</h2>
<p><strong>Prima migliora il tuo mazzo. Poi valuta cosa negare.</strong> Lista essenziale delle carte FRA: gruppi di priorità editoriali, basati su ruolo, testo delle carte e snapshot Premier del 16 ottobre 2026. Non è un ordine automatico generato dal win rate. Le Special Guests sono trattate nel report esteso.</p>
<div class="pick-controls"><label>Dove giochi?<select id="pick-environment"><option value="arena">Arena: avversari fuori dal tavolo di draft</option><option value="pod">Draft individuale contro lo stesso tavolo</option></select></label><label class="pick-stat-toggle"><input type="checkbox" id="pick-show-stats"> Mostra percentuali, campioni e costi</label></div>
<div id="pick-policy-arena" class="notice"><strong>Su Arena:</strong> prendi queste bombe per giocarle, se il tuo pool può sostenerle. Sceglierle soltanto per negarle al giocatore accanto non dà il normale vantaggio del counterpick, perché non affronti necessariamente il tuo tavolo. Le risposte sotto restano pick utili.</div>
<div id="pick-policy-pod" class="notice" hidden><strong>Contro lo stesso tavolo:</strong> valuta di negare le minacce elencate nei counterpick soltanto quando nella busta non resta un miglioramento significativo per il mazzo o la sideboard e un avversario plausibile può giocarle. Se puoi usarle tu, sono normali pick forti. Per il team draft servono valutazioni diverse.</div>
<p class="pick-jumps"><a href="#pick-now">Vai ai pick subito</a> · <a href="#counter-now">Vai ai counterpick</a></p><div class="pick-columns"><div><h3 id="pick-now">Pick subito</h3>''' + ''.join(left) + '''</div><div><h3 id="counter-now">Counterpick: le minacce da negare</h3><p class="small">Se il counterpick è giustificato, queste sono le priorità principali. Prima le bombe che possono dominare da sole, poi i finisher con valore immediato. Apri una voce per vedere le risposte da cercare nei tuoi colori.</p><ul class="pick-list pick-counter-list">''' + ''.join(right) + '''</ul><aside class="pick-rule"><h4>Quando sei indeciso fra due carte</h4><p>Nei primi pick: potenza autonoma e flessibilità. A colori definiti: riempi il ruolo mancante. Una rimozione giocabile o una risposta da sideboard utile viene normalmente prima di un counterpick marginale. Esempio: in bianco/blu, Surveillance Phantasm copre il turno due, Your Fate Ends Here risponde alle minacce da tre mana in su e Fatehold Annex aiuta i colori. In verde, Budding Insurgent può servire contro Way of the Healer.</p><p><a href="#pick-decisions">Leggi 20 situazioni di scelta ↓</a></p><a href="#draft-drilldown">Controlla la coppia e confronta due carte ↓</a></aside></div></div>
<p class="small">Ogni nome apre i dettagli e mostra l'immagine al passaggio del mouse. Le liste restano indipendenti dai filtri del drilldown. Fonti: <a href="draft-drilldown-20261016.json" download>snapshot 17Lands del 16 ottobre</a>, <a href="https://scryfall.com/sets/fra" target="_blank" rel="noopener">testi Oracle</a> e <a href="https://magic.wizards.com/en/news/feature/reality-fracture-release-notes" target="_blank" rel="noopener">note ufficiali Wizards</a>.</p></section>'''


def pick_baits(cards):
    guide = json.loads((ROOT / 'draft-pick-baits.json').read_text(encoding='utf-8'))
    lookup = {c['name']: c for c in cards}
    columns = []
    for group in guide['groups']:
        rows = []
        for entry in group['cards']:
            c = lookup[entry['name']]
            assert c['rarity'] in ('rare', 'mythic')
            rate = f"{c['gih'] * 100:.1f}".replace('.', ',') + '%' if c['gih'] is not None else 'N/D'
            sample = f"{c['n']:,}".replace(',', '.')
            caution = ' · campione sotto 2.000, maggiore cautela' if c['n'] < 2000 else ''
            rarity = 'Mitica' if c['rarity'] == 'mythic' else 'Rara'
            rows.append('<li><button type="button" class="dd-card-link" data-name="' + html.escape(c['name'], quote=True) + '">' + html.escape(c['name']) + '</button><small>' + rarity + ' · GIH WR ' + rate + ' · ' + sample + ' osservazioni' + caution + '</small><p>' + inline(entry['why']) + '</p><details><summary>Quando la prenderei</summary><p>' + inline(entry['when']) + '</p></details></li>')
        columns.append('<div><h3>' + inline(group['title']) + '</h3><p class="small">' + inline(group['note']) + '</p><ul class="pick-list">' + ''.join(rows) + '</ul></div>')
    return '''<section id="pick-baits" class="report-section pick-baits">
<div class="eyebrow">Prima il mazzo, poi il simbolo di rarità</div><h2>Rare e mitiche: i bait del draft</h2>
<p><strong>Valuta il risultato abituale, non soltanto lo scenario migliore.</strong> Queste otto carte possono indurti a spendere un pick troppo alto o a forzare un piano poco affidabile. Le indicazioni sono valutazioni strategiche: la qualità delle alternative e il pool già scelto restano decisivi.</p>
<p class="small">Premier Draft Arena · snapshot del 16 ottobre 2026. GIH WR: vittorie nelle partite in cui la carta era nella mano iniziale o è stata pescata. Le percentuali non misurano l'effetto causale del pick e dipendono anche da mazzi e giocatori. I campioni sotto 2.000 sono segnalati; per BO3 e tavoli cartacei rivaluta il contesto.</p>
<div class="pick-columns">''' + ''.join(columns) + '''</div>
<aside class="pick-rule"><h3>Il controllo prima di scegliere</h3><p>Se la pesco mentre sto perdendo, cosa fa? Ho già il supporto o spero che arrivi? Quale buona carta sto lasciando passare per prenderla?</p><p>Passare una rara condizionale per una buona rimozione o una non comune adatta al tuo mazzo è spesso corretto. Anche il counterpick segue lo stesso criterio: una carta appariscente ma poco efficace non diventa una priorità da negare. Esempio: in bianco, Your Fate Ends Here utile al tuo mazzo viene prima di Flickering Hound preso solo per negarlo.</p></aside>
<p class="small">Dati: <a href="draft-drilldown-20261016.json" download>snapshot 17Lands</a> e <a href="https://www.17lands.com/card_data?expansion=FRA&amp;format=PremierDraft" target="_blank" rel="noopener">statistiche del formato</a>. Testi: <a href="draft-oracle-20261016.json" download>snapshot Oracle del 16 ottobre</a>. Apri il nome di una carta per testo, immagine e confronti nei diversi archetipi. <a href="#draft-drilldown">Confronta due possibili pick ↓</a></p></section>'''


def pick_decisions(known_names):
    groups = json.loads((ROOT / 'draft-pick-decisions.json').read_text(encoding='utf-8'))
    total = sum(len(g['cases']) for g in groups)
    content = []
    for index, group in enumerate(groups):
        content.append('<section class="decision-group"><h4>' + inline(group['group']) + '</h4>')
        for offset, case in enumerate(group['cases']):
            assert set(case['cards']) <= known_names, f'Carta sconosciuta: {case["title"]}'
            opened = ' open' if index == 0 and offset == 0 else ''
            content.append('<details class="pick-decision"' + opened + '><summary>' + inline(case['title']) + '</summary><div>')
            for key, label in [('context', 'Il pool e il confronto'), ('choose', 'Cosa sceglierei'), ('why', 'Perché'), ('change', 'Quando cambia')]:
                content.append('<p><strong>' + label + ':</strong> ' + inline(case[key]) + '</p>')
            content.append('</div></details>')
        content.append('</section>')
    return '<div id="pick-decisions" class="pick-decisions"><p><strong>Il pick migliore risolve il problema più importante del tuo pool.</strong> Prima chiediti: come vinco, cosa mi impedisce di arrivarci, quale carta sostituirei e posso lanciare questa magia quando serve?</p><p>Questi ' + str(total) + ' casi sono esempi di valutazione strategica, non una lista esaustiva o un algoritmo. Le quantità e i pool descritti sono ipotetici. Salvo i casi sul mana, presuppongo carte lanciabili nei tuoi colori e alternative di qualità adeguata.</p><div class="decision-controls"><button type="button" data-decisions="open">Apri tutti i ' + str(total) + ' casi</button><button type="button" data-decisions="close">Chiudi tutti</button></div>' + ''.join(content) + '<p class="small">I confronti restano indipendenti dai filtri del drilldown. Strategie editoriali; per costi e interazioni vedi <a href="https://scryfall.com/sets/fra" target="_blank" rel="noopener">testi Oracle</a> e <a href="https://magic.wizards.com/en/news/feature/reality-fracture-release-notes" target="_blank" rel="noopener">note ufficiali Wizards</a>. Per il risultato osservato nel tuo archetipo usa il <a href="#draft-drilldown">confronto fra due carte</a>.</p></div>'


def build():
    report = json.loads((ROOT / 'draft-report-content-20261016.json').read_text(encoding='utf-8'))
    snapshot = json.loads((ROOT / 'draft-drilldown-20261016.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256((ROOT / 'draft-drilldown-20261016.json').read_bytes()).hexdigest()
    assert report['snapshot_sha256'] == digest, 'Snapshot cambiato: aggiornare e verificare anche il report narrativo.'
    oracle = json.loads((ROOT / 'draft-oracle-20261016.json').read_text(encoding='utf-8'))
    def index(rows):
        return {name: c for c in rows for name in {c['name'], c['name'].split(' // ')[0], *(f['name'] for f in c.get('card_faces', []))}}
    by_name = index(oracle)
    spg = index(json.loads((ROOT / 'fra-spg.json').read_text(encoding='utf-8')))
    # Adjacent list items exported as separate blocks form a single semantic list.
    blocks = []
    metrics = {c['name']: c for c in snapshot['contexts']['ALL_TIME:all']['value']['data']}
    def number(value, decimals=1):
        if value is None:
            return 'N/D'
        return f'{value:,.{decimals}f}'.replace(',', '_').replace('.', ',').replace('_', '.')
    for block in report['blocks']:
        if block.startswith('| Carta | GIH WR |'):
            rows = [x.strip().strip('|').split('|') for x in block.splitlines()]
            caution = 'Come valutarla' in rows[0][-1]
            if caution:
                block = '| Carta | GIH WR | Osservazioni GIH | ATA globale | Come valutarla |\n| --- | ---: | ---: | ---: | --- |'
            else:
                block = '| Carta | GIH WR | Osservazioni GIH | ALSA |\n| --- | ---: | ---: | ---: |'
            for row in rows[2:]:
                name = row[0].strip()
                c = metrics[name]
                values = [name, number(c['ever_drawn_win_rate'] * 100) + '%', number(c['ever_drawn_game_count'], 0), number(c['avg_pick'] if caution else c['avg_seen'])]
                if caution:
                    values.append(row[-1].strip())
                block += '\n| ' + ' | '.join(values) + ' |'
        kind = lambda value: 'ul' if value.startswith('- ') else 'ol' if re.match(r'^\d+\. ', value) else None
        if blocks and kind(block) and kind(block) == kind(blocks[-1]):
            blocks[-1] += '\n' + block
        else:
            blocks.append(block)
    headings, body = [], []
    section = -1
    for block in blocks:
        if block.startswith('# '):
            if section >= 0:
                body.append('</section>')
            section += 1
            title = block[2:]
            headings.append((f'report-{section}', title))
            body.append(f'<section id="report-{section}" class="report-section"><h2>{inline(title)}</h2>')
        elif block.startswith('## '):
            body.append('<h3>' + inline(block[3:]) + '</h3>')
        elif block == '[[PICK_DECISIONS]]':
            body.append(pick_decisions(set(by_name) | set(spg)))
        elif block.startswith('!['):
            if '](visualize:' in block:
                body.append('<div id="archetype-chart" class="chart" role="group" aria-label="Scarto dalla media per archetipo"></div>')
            else:
                name = re.match(r'!\[([^\]]+)\]', block)[1]
                c = by_name[name]
                path = f'{ASSETS}/{c["collector_number"]}.jpg'
                assert (ROOT / path).exists()
                body.append(f'<figure class="card-figure"><button type="button" data-name="{html.escape(name)}" aria-label="Ingrandisci {html.escape(name)}"><img src="{path}" alt="{html.escape(name)}" width="488" height="680" loading="lazy"></button><figcaption>{html.escape(name)} · clicca per ingrandire</figcaption></figure>')
        else:
            body.append(markdown(block))
    body.append('</section>')
    cards = []
    source_cards = snapshot['contexts']['ALL_TIME:all']['value']['data']
    missing = [c['name'] for c in source_cards if c['name'] not in by_name and c['name'] not in spg]
    assert not missing, f'Oracle mancante: {missing}'
    for c in source_cards:
        o = by_name.get(c['name']) or spg.get(c['name'])
        image = c['url']
        if o and (ROOT / ASSETS / (o['collector_number'] + '.jpg')).exists():
            image = f'{ASSETS}/{o["collector_number"]}.jpg'
        front = (o.get('card_faces') or [o])[0] if o else {}
        cost = front.get('mana_cost', '')
        cards.append(dict(name=c['name'], color=c['color'], rarity=c['rarity'],
                          gih=c.get('ever_drawn_win_rate'), n=c.get('ever_drawn_game_count', 0),
                          alsa=c.get('avg_seen'), image=image,
                          url=o['scryfall_uri'] if o else 'https://scryfall.com/search?q=' + quote_plus(c['name']),
                          oracle=o.get('oracle_text', '') if o else '',
                          faces=o.get('card_faces', []) if o else [],
                          cost=cost, mv=o.get('cmc') if o else None,
                          type=front.get('type_line', ''),
                          playable=[pair for pair in PAIRS if can_cast(cost, pair)] if o else [],
                          set=o['set'].upper() if o else 'N/D'))
    colors = snapshot['contexts']['ALL_TIME:colors']['value']
    pairs = []
    for c in colors:
        code = c['short_name']
        if isinstance(code, str) and len(code) == 2 and '+' not in code:
            splash = next(x for x in colors if x['short_name'] == code + '+')
            pairs.append(dict(name=c['color_name'], wins=c['wins'] + splash['wins'], games=c['games'] + splash['games']))
    baseline = sum(c['wins'] for c in pairs) / sum(c['games'] for c in pairs)
    nav = ''.join(f'<a href="#{id}">{inline(title)}</a>' for id, title in headings)
    template = (ROOT / 'draft-report-template.html').read_text(encoding='utf-8')
    drill = drilldown_data()
    known = {c['name'] for c in cards}
    for guide in drill['guides'].values():
        assert set(guide['core'] + guide['support']) <= known
    pool_cards = []
    for o in oracle + list({c['id']: c for c in spg.values()}.values()):
        front = (o.get('card_faces') or [o])[0]
        stat = next((c for c in cards if c['name'] in [o['name'], front['name']]), {})
        pool_cards.append(dict(name=o['name'], cost=front.get('mana_cost', ''),
            mv=o.get('cmc'), type=o.get('type_line', front.get('type_line', '')),
            color=''.join(o.get('colors', front.get('colors', []))),
            oracle=o.get('oracle_text', ''), faces=o.get('card_faces', []),
            power=o.get('power'), toughness=o.get('toughness'), loyalty=o.get('loyalty'), defense=o.get('defense'),
            image=stat.get('image') or (o.get('image_uris') or front.get('image_uris', {})).get('normal', ''),
            url=o['scryfall_uri'], set=o['set'].upper(), number=o['collector_number'],
            basic='Basic' in o.get('type_line', ''), gih=stat.get('gih'), n=stat.get('n', 0)))
    data = dict(cards=cards, poolCards=pool_cards, pairs=pairs, baseline=baseline, date='16 ottobre 2026', drill=drill)
    drill_html = (ROOT / 'draft-drilldown-section.html').read_text(encoding='utf-8')
    result = template.replace('__DRAFT_POOL__', (ROOT / 'draft-pool-section.html').read_text(encoding='utf-8')).replace('__PICK_GUIDE__', pick_guide(cards)).replace('__PICK_BAITS__', pick_baits(cards)).replace('__DRILLDOWN_SECTION__', drill_html).replace('__REPORT__', ''.join(body)).replace('__REPORT_NAV__', nav)
    result = result.replace('\u2014', ':')
    # Preserve the source Oracle in data instead of editing it with a global replacement.
    result = result.replace('__DRAFT_DATA__', json.dumps(data, ensure_ascii=True).replace('</', '<\\/'))
    (ROOT / 'Reality-Fracture-Draft.html').write_text(result, encoding='utf-8')
    images = sum(1 for c in cards if c['image'].startswith(ASSETS + '/'))
    print(f'Draft: {len(cards)} carte, {len(pairs)} archetipi, {images} immagini locali, {len(headings)} sezioni. Oracle completi.')


if __name__ == '__main__':
    build()
