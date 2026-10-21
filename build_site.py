"""Offline, dependency-free static build for GitHub Pages."""
import html
import json
import re
import runpy
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from site_navigation import shell, FILES

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'

def homepage(expansions):
    cards=[]
    for item in expansions:
        slug=item['slug']
        if not re.fullmatch(r'[a-z0-9-]+',slug):
            raise ValueError('Invalid expansion slug')
        url=f'sets/{slug}/index.html'
        e=html.escape
        base=f'sets/{slug}/'
        discovery=item.get('discovery', 'Reality-Fracture-Discovery.html')
        draft=item.get('draft', 'Reality-Fracture-Draft.html')
        cards.append(f'''<article class="set" data-set="{e((item['name']+' '+item['code']).lower())}"><div class="set-head"><span>{e(item['code'])}</span><h3>{e(item['name'])}</h3></div><div class="set-body"><p>{e(item['description'])}</p><p class="small">Ultimo aggiornamento dei contenuti: {e(item['date'])}. Le singole sezioni riportano le proprie date.</p><div class="links"><a class="primary" href="{url}">Esplora il set →</a><a href="{base}{discovery}">Metagame e carte</a><a href="{base}{draft}">Guida Draft</a></div></div></article>''')
    return shell((ROOT/'home-template.html').read_text(encoding='utf-8-sig').replace('__EXPANSIONS__',''.join(cards)), 'home', root=True)

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
    runpy.run_path(str(ROOT/'build_database.py'),run_name='__main__')
    from build_draft_engine import build as build_draft_engine
    (ROOT/'Reality-Fracture-Draft-Engine.html').write_text(build_draft_engine(),encoding='utf-8')
    expansions=json.loads((ROOT/'expansions.json').read_text(encoding='utf-8'))
    home=homepage(expansions)
    (ROOT/'index.html').write_text(home,encoding='utf-8')
    # Delete only this builder's output, confined to the checkout.
    if DIST.exists():
        if DIST.is_symlink() or DIST.resolve().parent!=ROOT.resolve():
            raise ValueError('Unsafe output path')
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST/'index.html').write_text(home,encoding='utf-8')
    (DIST/'.nojekyll').touch()
    for name in ['site.css','site.js']:
        shutil.copy2(ROOT/name,DIST/name)
    for expansion in expansions:
        dest=DIST/'sets'/expansion['slug'];dest.mkdir(parents=True)
        if expansion['code']=='TRK':
            from build_star_trek import build as build_star_trek
            build_star_trek(dest)
            continue
        if expansion['code']!='FRA':
            raise ValueError('Add the new expansion build and asset list before publishing it')
        for page in ROOT.glob('Reality-Fracture-*.html'):
            content=page.read_text(encoding='utf-8')
            key=FILES[page.stem.removeprefix('Reality-Fracture-')]
            content=shell(content,key)
            (dest/page.name).write_text(content,encoding='utf-8')
        for pattern in ['*.css','*.js']:
            for asset in ROOT.glob(pattern):
                shutil.copy2(asset,dest/asset.name)
        for name in ['draft-drilldown-20261016.json','draft-oracle-20261016.json']:
            shutil.copy2(ROOT/name,dest/name)
        asset_dest=dest/'draft-report-assets-20261016';asset_dest.mkdir()
        for image in (ROOT/'draft-report-assets-20261016').glob('*.jpg'):
            shutil.copy2(image,asset_dest/image.name)
        overview=shell((ROOT/'set-template.html').read_text(encoding='utf-8-sig'),'set')
        (dest/'index.html').write_text(overview,encoding='utf-8')
    validate_site()
    print(f'Site built: {len(expansions)} expansion(s), {len(list(DIST.rglob("*.html")))} HTML pages. Local links verified.')

if __name__=='__main__':
    build()
