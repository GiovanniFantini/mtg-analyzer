"""Compatibility entry point. Edit expansion JSON documents, then build the site."""
from expansion_data import ROOT, Expansion
from build_expansion import render_page


def build(expansion_id='reality-fracture'):
    expansion=Expansion(ROOT/'expansions'/expansion_id/'expansion.json')
    page=expansion.manifest['presentation']['pages']['discovery']
    content=render_page(expansion,'discovery',page)
    (ROOT/page['url'].split('#')[0]).write_text(content,encoding='utf-8')
    return content


if __name__=='__main__':
    build()
