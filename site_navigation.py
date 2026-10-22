"""Shared navigation for the static website, without nested scroll areas."""
import re

PAGES = {
    'home': ('Home', 'index.html'),
    'set': ('Panoramica', 'index.html'),
    'gallery': ('Catalogo carte', 'Reality-Fracture-Sealed.html#gallery'),
    'analysis': ('Analisi del set', 'Reality-Fracture-Analisi.html'),
    'draft': ('Draft e pick', 'Reality-Fracture-Draft.html'),
    'draft-engine': ('Tavolo Draft con bot', 'Reality-Fracture-Draft-Engine.html'),
    'pool': ('Il mio pool Sealed', 'Reality-Fracture-Sealed.html#pool'),
    'strategy': ('Guida Sealed', 'Reality-Fracture-Sealed.html#strategy'),
    'simulator': ('Simulatore Sealed', 'Reality-Fracture-Simulatore.html'),
    'combos': ('Combo e sinergie', 'Reality-Fracture-Combo.html'),
    'discovery': ('Metagame e carte', 'Reality-Fracture-Discovery.html'),
    'method': ('Fonti e metodo', 'Reality-Fracture-Sealed.html#method'),
}
GROUPS = [('Carte e set', ['set','gallery','analysis']),
          ('Limited', ['draft','draft-engine','strategy','pool','simulator']),
          ('Sinergie', ['combos']), ('Constructed', ['discovery']),
          ('Approfondimenti', ['method'])]
FILES = {'Sealed':'gallery','Draft':'draft','Analisi':'analysis',
         'Simulatore':'simulator','Combo':'combos','Discovery':'discovery',
         'Draft-Engine':'draft-engine'}


def shell(content, key, root=False, expansion=None):
    if expansion is not None:
        return expansion_shell(content, key, expansion)
    home = 'index.html' if root else '../../index.html'
    prefix = 'sets/reality-fracture/' if root else ''
    asset = '' if root else '../../'
    groups = []
    for title, ids in GROUPS:
        links = []
        for id_ in ids:
            label, url = PAGES[id_]
            current = ' aria-current="page"' if key == id_ else ''
            links.append(f'<a data-page="{id_}" href="{prefix}{url}"{current}>{label}</a>')
        groups.append(f'<div class="site-nav-group"><p>{title}</p>{"".join(links)}</div>')
    navigation = f'''<a class="site-skip" href="#site-content">Vai al contenuto</a>
<div class="site-bar"><a class="site-brand" href="{home}"><span class="site-mark" aria-hidden="true">M<span>✦</span></span><span>MTG <b>Analyzer</b></span></a><span class="site-bar-note">Il tuo tavolo di Magic</span><button class="site-menu-toggle" type="button" aria-expanded="false" aria-controls="site-sidebar">☰ Menu</button></div>
<div class="site-backdrop" hidden></div><aside class="site-sidebar" id="site-sidebar" aria-label="Navigazione principale"><a class="site-home" href="{home}"{' aria-current="page"' if root else ''}>⌂ Home</a><div class="site-set-label"><span>ESPANSIONE</span><strong>Reality Fracture <small>FRA</small></strong></div><nav>{''.join(groups)}</nav><p class="site-storage-note">Pool e carte osservate si salvano in questo browser.</p></aside>
<div class="site-body"><nav class="site-breadcrumb" aria-label="Percorso">{('<span id="site-page-label">Home</span>' if root else f'<a href="{home}">Home</a><span aria-hidden="true">/</span><a href="index.html">Reality Fracture</a><span aria-hidden="true">/</span><span id="site-page-label">{PAGES[key][0]}</span>')}</nav>'''
    if key not in ['home', 'set']:
        if key in ['analysis', 'combos']:
            old_header = re.search(r'<header\b[^>]*>(.*?)</header>', content, re.S)
            h1 = re.search(r'<h1.*?</h1>', old_header[1], re.S)[0]
            intro = re.search(r'<p>.*?</p>', old_header[1], re.S)[0]
            local = ('<a href="#explorer">Esplora i dati</a><a href="#reports">Leggi i risultati</a><a href="#sentiment">Sentiment</a><a href="#method">Indicatori e fonti</a>' if key == 'analysis' else '<a href="#catalogo">Le combinazioni</a><a href="#metodo">Come leggere le stelle</a>')
            content = content.replace('<main>', f'<main><div class="site-page-intro">{h1}{intro}<nav class="site-local-nav" aria-label="In questa pagina">{local}</nav></div>', 1)
        content = re.sub(r'<header\b[^>]*>.*?</header>', '', content, count=1, flags=re.S)
        content = re.sub(r'<nav class="workspace-nav".*?</nav>', '', content, count=1, flags=re.S)
    if key == 'gallery':
        content = content.replace('href="#top"', 'href="#site-content"')
        # Keep search and sorting visible; move secondary filters into one panel.
        start = content.index('<div class="toolbar">', content.index('id="gallery"'))
        end = content.index('<noscript>', start)
        toolbar = content[start:end]
        search = re.search(r'<input id="search"[^>]*>', toolbar)[0]
        order = re.search(r'<select id="order".*?</select>', toolbar, re.S)[0]
        filters, status = toolbar.removeprefix('<div class="toolbar">').rsplit('<div class="statusrow">', 1)
        filters = filters.replace(search, '').replace(order, '')
        toolbar = f'<div class="toolbar"><div class="tools site-catalog-search">{search}{order}</div><details class="site-catalog-filters" open><summary>Filtra per colore, rarità e valutazione</summary>{filters}</details><div class="statusrow">{status}'
        content = content[:start] + toolbar + content[end:]
        content = content.replace('<title>Reality Fracture · Atlante Sealed completo</title>', '<title>Reality Fracture · Catalogo e pool Sealed</title>')
        redirects = ','.join(f"'{id_}':'{PAGES[id_][1]}'" for id_ in ['draft','analysis','simulator','combos','discovery'])
        content = content.replace('function openWorkspace(hash){', f"function openWorkspace(hash){{if(hash==='#site-content'){{if(workspaceSections.some(x=>x.hidden))return;hash='#gallery'}}const pages={{{redirects}}};const destination=pages[(hash||'').slice(1)];if(destination){{location.replace(destination);return}}")
        content = re.sub(r'<section id="(?:draft|analysis|simulator|combos|discovery)" class="workspace-embed">.*?</section>', '', content, flags=re.S)
        content = content.replace("$('combos').querySelector('iframe').src='Reality-Fracture-Combo.html?card='+encodeURIComponent(b.dataset.combo)+'#catalogo';location.hash='combos';openWorkspace('#combos')", "location.href='Reality-Fracture-Combo.html?card='+encodeURIComponent(b.dataset.combo)+'#catalogo'")
        content = content.replace("$('combos').querySelector('iframe').src=a.getAttribute('href');$('zoom').close();location.hash='combos';openWorkspace('#combos')", "location.href=a.getAttribute('href')")
        for section in ['gallery','pool','strategy','method']:
            content = re.sub(r'(<section\b[^>]*\bid="'+section+r'"[^>]*>.*?)<h2>(.*?)</h2>', r'\1<h1>\2</h1>', content, count=1, flags=re.S)
    if key == 'draft':
        content = re.sub(r'(<nav class="report-nav".*?</nav>)', r'<details class="site-page-index"><summary>In questa pagina: indice della guida Draft</summary>\1</details>', content, count=1, flags=re.S)
        content = content.replace('<a href="#pick-guide">Vai alla lista rapida: pick subito e counterpick ↓</a>', '<nav class="site-local-nav" aria-label="Accessi rapidi Draft"><a href="#pick-guide">Pick rapidi</a><a href="#draft-pool">Il mio pool Draft</a><a href="#draft-drilldown">Confronta le carte</a><a href="#card-statistics">Statistiche</a></nav>')
    change_set = 'sets/star-trek/index.html' if root else '../star-trek/index.html'
    navigation = navigation.replace('<nav>', f'<a href="{change_set}">Star Trek · anteprima</a><nav>', 1)
    content = content.replace('<main>', '<main id="site-content" tabindex="-1">', 1)
    content = content.replace('</head>', f'<link rel="stylesheet" href="{asset}site.css"></head>', 1)
    content = content.replace('<body>', f'<body class="site-layout site-page-{key}">{navigation}', 1)
    content = content.replace('</body>', f'</div><a class="site-to-top" href="#site-content" aria-label="Torna al contenuto">↑</a><script src="{asset}site.js"></script></body>', 1)
    return content


def expansion_shell(content, key, expansion):
    """Set-aware shell for new expansions; legacy FRA pages keep their adapters."""
    import html
    e = html.escape
    pages = expansion['pages']
    groups = []
    for title, ids in expansion['groups']:
        links = ''.join(f'<a data-page="{id_}" href="{pages[id_][1]}"' +
                        (' aria-current="page"' if key == id_ else '') +
                        f'>{e(pages[id_][0])}</a>' for id_ in ids)
        groups.append(f'<div class="site-nav-group"><p>{e(title)}</p>{links}</div>')
    nav = f'''<a class="site-skip" href="#site-content">Vai al contenuto</a>
<div class="site-bar"><a class="site-brand" href="../../index.html"><span class="site-mark" aria-hidden="true">M<span>✦</span></span><span>MTG <b>Analyzer</b></span></a><span class="site-bar-note">Il tuo tavolo di Magic</span><button class="site-menu-toggle" type="button" aria-expanded="false" aria-controls="site-sidebar">☰ Menu</button></div>
<div class="site-backdrop" hidden></div><aside class="site-sidebar" id="site-sidebar" aria-label="Navigazione principale"><a class="site-home" href="../../index.html">⌂ Home</a><div class="site-set-label"><span>ESPANSIONE</span><strong>{e(expansion['name'])}<small>{e(expansion['code'])} · Anteprima</small></strong></div><a href="../reality-fracture/index.html">Reality Fracture</a><nav>{''.join(groups)}</nav><p class="site-storage-note">Pool Star Trek separati da Reality Fracture. Esporta i salvataggi per conservarli.</p></aside>
<div class="site-body"><nav class="site-breadcrumb" aria-label="Percorso"><a href="../../index.html">Home</a><span>/</span><a href="index.html">Star Trek</a><span>/</span><span id="site-page-label">{e(pages[key][0])}</span></nav>'''
    content = content.replace('<main>', '<main id="site-content" tabindex="-1">', 1)
    content = content.replace('</head>', '<link rel="stylesheet" href="../../site.css"></head>', 1)
    content = content.replace('<body>', f'<body class="site-layout trk-page" data-page="{key}">{nav}', 1)
    return content.replace('</body>', '</div><a class="site-to-top" href="#site-content" aria-label="Torna al contenuto">↑</a><script src="../../site.js"></script></body>', 1)
