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


def icon_links(prefix):
    return f'<link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">'


def shell(content, key, root=False, expansion=None, expansions=None):
    if root and expansions is not None:
        import html
        e=html.escape
        output=shell(content,key,root=True)
        groups=[]
        for index,item in enumerate(expansions):
            base='sets/'+item['id']+'/'
            pages=item['presentation']['pages']
            if index==0:
                groups.append('<div class="site-set-label"><span>ESPANSIONE</span><strong>'+e(item['name'])+' <small>'+e(item['code'])+'</small></strong></div>')
                others=''.join('<a href="sets/'+other['id']+'/'+e(other['presentation']['pages']['set']['url'],quote=True)+'">'+e(other['name'])+(' · anteprima' if other.get('status')=='preview' else '')+'</a>' for other in expansions[1:])
                groups.append(others+'<nav>')
                for title,keys in item['presentation']['groups']:
                    links=''.join('<a data-page="'+id_+'" href="'+base+e(pages[id_]['url'],quote=True)+'">'+e(pages[id_]['label'])+'</a>' for id_ in keys if id_ in pages)
                    groups.append('<div class="site-nav-group"><p>'+e(title)+'</p>'+links+'</div>')
                groups.append('</nav>')
        aside='<aside class="site-sidebar" id="site-sidebar" aria-label="Navigazione principale"><a class="site-home" href="index.html" aria-current="page">⌂ Home</a>'+''.join(groups)+'<p class="site-storage-note">Pool e carte osservate si salvano in questo browser.</p></aside>'
        return re.sub(r'<aside class="site-sidebar".*?</aside>',lambda _:aside,output,count=1,flags=re.S)
    if expansion is not None:
        return configured_shell(content, key, expansion)
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
    content = content.replace('</head>', icon_links(asset) + f'<link rel="stylesheet" href="{asset}site.css"></head>', 1)
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
    content = content.replace('</head>', icon_links('../../') + '<link rel="stylesheet" href="../../site.css"></head>', 1)
    content = content.replace('<body>', f'<body class="site-layout trk-page" data-page="{key}">{nav}', 1)
    return content.replace('</body>', '</div><a class="site-to-top" href="#site-content" aria-label="Torna al contenuto">↑</a><script src="../../site.js"></script></body>', 1)


def configured_shell(content, key, expansion):
    """Keep existing page layouts while obtaining all navigation from the manifest."""
    import html
    e = html.escape
    presentation = expansion['presentation']
    pages = presentation['pages']
    adapt_atlas = presentation['style'] == 'atlas' and not expansion.get('minimal')
    if adapt_atlas:
        content = shell(content,key if key in PAGES else 'set')
        ids=set(re.findall(r'\bid=[\'"]([^\'"]+)[\'"]',content))
        if not expansion.get('sentimentAvailable',True):ids.discard('sentiment')
        def local_nav(match):
            return re.sub(r'<a\b[^>]*href="\#([^\"]+)"[^>]*>.*?</a>',lambda link:link[0] if link[1] in ids else '',match[0],flags=re.S)
        content=re.sub(r'<nav class="site-local-nav".*?</nav>',local_nav,content,flags=re.S)
    else:
        content = content.replace('<main>', '<main id="site-content" tabindex="-1">',1)
        content = content.replace('</head>', icon_links('../../') + '<link rel="stylesheet" href="../../site.css"></head>',1)
        body_class='site-layout site-page-'+key if presentation['style']=='atlas' else 'site-layout trk-page'
        content = content.replace('<body>', '<body class="'+body_class+'" data-page="'+key+'">',1)
        if 'class="site-to-top"' not in content:
            content=content.replace('</body>','<a class="site-to-top" href="#site-content" aria-label="Torna al contenuto">↑</a></body>',1)
        content = content.replace('</body>', '<script src="../../site.js"></script></body>',1)
    groups=[]
    for title, keys in presentation['groups']:
        links=''.join('<a data-page="'+id_+'" href="'+e(pages[id_]['url']+('#gallery' if presentation['style']=='atlas' and id_=='gallery' else ''),quote=True)+'"'+(' aria-current="page"' if id_==key else '')+'>'+e(pages[id_]['label'])+'</a>' for id_ in keys if id_ in pages)
        groups.append('<div class="site-nav-group"><p>'+e(title)+'</p>'+links+'</div>')
    from expansion_data import read_json, ROOT, confined
    others=[]
    for entry in read_json(ROOT/'expansions.json'):
        other=read_json(confined(ROOT,entry['manifest']))
        if other['id']!=expansion['id']:
            others.append('<a href="../'+other['id']+'/'+other['presentation']['pages']['set']['url']+'">'+e(other['name'])+(' · anteprima' if other.get('status')=='preview' else '')+'</a>')
    overview_url=pages['set']['url']
    storage_note=expansion.get('storageNote','Pool e carte osservate si salvano in questo browser.')
    nav=f'''<a class="site-skip" href="#site-content">Vai al contenuto</a>
<div class="site-bar"><a class="site-brand" href="../../index.html"><span class="site-mark" aria-hidden="true">M<span>✦</span></span><span>MTG <b>Analyzer</b></span></a><span class="site-bar-note">Il tuo tavolo di Magic</span><button class="site-menu-toggle" type="button" aria-expanded="false" aria-controls="site-sidebar">☰ Menu</button></div>
<div class="site-backdrop" hidden></div><aside class="site-sidebar" id="site-sidebar" aria-label="Navigazione principale"><a class="site-home" href="../../index.html">⌂ Home</a><div class="site-set-label"><span>ESPANSIONE</span><strong>{e(expansion['name'])}<small>{e(expansion['code'])}{' · Anteprima' if expansion.get('status')=='preview' else ''}</small></strong></div>{''.join(others)}<nav>{''.join(groups)}</nav><p class="site-storage-note">{e(storage_note)}</p></aside>
<div class="site-body"><nav class="site-breadcrumb" aria-label="Percorso"><a href="../../index.html">Home</a><span aria-hidden="true">/</span><a href="{e(overview_url,quote=True)}">{e(expansion['name'])}</a><span aria-hidden="true">/</span><span id="site-page-label">{e(pages[key]['label'])}</span></nav>'''
    if adapt_atlas:
        content=re.sub(r'<a class="site-skip".*?(?=<main)',lambda _:nav,content,count=1,flags=re.S)
    else:
        content=content.replace('<main',nav+'<main',1)
        content=content.replace('</body>','</div></body>',1)
    return content
