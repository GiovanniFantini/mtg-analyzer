"""Offline, dependency-free static build for GitHub Pages."""
import html
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from site_navigation import shell

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'

def homepage(expansions):
    cards=[]
    for item in expansions:
        slug=item['slug']
        if not re.fullmatch(r'[a-z0-9-]+',slug):
            raise ValueError('Invalid expansion slug')
        url=f"sets/{slug}/{item['presentation']['pages']['set']['url']}"
        e=html.escape
        base=f'sets/{slug}/'
        discovery=item['presentation']['pages']['discovery']['url']
        draft=item['presentation']['pages']['draft']['url']
        cards.append(f'''<article class="set" data-set="{e((item['name']+' '+item['code']).lower())}"><div class="set-head"><span>{e(item['code'])}</span><h3>{e(item['name'])}</h3></div><div class="set-body"><p>{e(item['description'])}</p><div class="links"><a class="primary" href="{url}">Esplora il set →</a><a href="{base}{discovery}">{e(item['presentation']['pages']['discovery']['label'])}</a><a href="{base}{draft}">{e(item['presentation']['pages']['draft']['label'])}</a></div></div></article>''')
    primary=next((item for item in expansions if item.get('home',{}).get('quickTools')),expansions[0] if expansions else None)
    featured=next((item for item in expansions if item.get('home',{}).get('featured')),expansions[-1] if expansions else None)
    def route(item,key):
        if not item:return '#sets-heading'
        return 'sets/'+item['id']+'/'+item['presentation']['pages'].get(key,item['presentation']['pages']['set'])['url']
    tokens={'__EXPANSIONS__':''.join(cards),
            '__FEATURED_NAME__':html.escape(featured['name']) if featured else 'Le espansioni',
            '__FEATURED_CODE__':html.escape(featured['code']) if featured else '',
            '__FEATURED_STATUS__':'ANTEPRIMA' if featured and featured.get('status')=='preview' else 'ESPANSIONE',
            '__FEATURED_LEAD__':'Il nuovo set arriva al tavolo.' if featured and featured.get('status')=='preview' else 'Esplora le carte e gli strumenti del set.',
            '__FEATURED_DATE__':html.escape(featured['date']) if featured else '',
            '__FEATURED_URL__':html.escape(route(featured,'set'),quote=True),
            '__FEATURED_RULES_URL__':html.escape(route(featured,'rules'),quote=True),
            '__PRIMARY_NAME__':html.escape(primary['name']) if primary else 'Le espansioni',
            '__PRIMARY_URL__':html.escape(route(primary,'set'),quote=True),
            '__PRIMARY_DRAFT_URL__':html.escape(route(primary,'draft'),quote=True),
            '__PRIMARY_POOL_URL__':html.escape(route(primary,'pool'),quote=True),
            '__PRIMARY_DISCOVERY_URL__':html.escape(route(primary,'discovery'),quote=True)}
    content=(ROOT/'home-template.html').read_text(encoding='utf-8-sig')
    for token,value in tokens.items():content=content.replace(token,value)
    return shell(content,'home',root=True,expansions=expansions)

class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.refs=[]
    def handle_starttag(self, tag, attrs):
        for key,value in attrs:
            if key in ['src','href'] and value:
                self.refs.append(value)

def validate_site():
    errors=[]
    for page in DIST.rglob('*.html'):
        content=page.read_text(encoding='utf-8')
        if re.search(r'</option\s+[^>]+>',content):errors.append(f'Malformed option closing tag: {page.name}')
        if 'portable-share' in content or 'WhatsApp' in content:
            errors.append(f'Obsolete sharing UI: {page.name}')
        parser=Links();parser.feed(content)
        for ref in parser.refs:
            url=urlsplit(ref)
            if url.scheme or url.netloc or not url.path:
                continue
            target=(page.parent/unquote(url.path)).resolve()
            if not target.is_relative_to(DIST.resolve()) or not target.exists():
                errors.append(f'{page.relative_to(DIST)}: missing {ref}')
    if errors:
        raise ValueError('\n'.join(errors))

def build():
    from expansion_data import load_expansions
    from build_expansion import build as build_expansion
    loaded=load_expansions()
    expansions=[{**item.manifest, 'slug':item.manifest['id'],
                 'draft':item.manifest['presentation']['pages']['draft']['url'],
                 'discovery':item.manifest['presentation']['pages']['discovery']['url']}
                for item in loaded]
    home=homepage(expansions)
    (ROOT/'index.html').write_text(home,encoding='utf-8')
    if DIST.exists():
        if DIST.is_symlink() or DIST.resolve().parent!=ROOT.resolve():
            raise ValueError('Unsafe output path')
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST/'index.html').write_text(home,encoding='utf-8')
    (DIST/'.nojekyll').touch()
    for name in ['site.css','site.js','favicon.svg']:
        shutil.copy2(ROOT/name,DIST/name)
    shutil.copytree(ROOT/'schemas',DIST/'schemas')
    for expansion in loaded:
        build_expansion(expansion,DIST/'sets'/expansion.manifest['id'])
    validate_site()
    print(f'Site built: {len(expansions)} expansion(s), {len(list(DIST.rglob("*.html")))} HTML pages. Local links verified.')

if __name__=='__main__':
    build()
