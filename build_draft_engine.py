"""Compatibility entry point for the shared, JSON-driven Draft renderer."""
from expansion_data import ROOT, Expansion
from build_expansion import render_page


def build(expansion_id='reality-fracture'):
    expansion=Expansion(ROOT/'expansions'/expansion_id/'expansion.json')
    return render_page(expansion,'draft-engine',expansion.manifest['presentation']['pages']['draft-engine'])


if __name__ == '__main__':
    (ROOT/'Reality-Fracture-Draft-Engine.html').write_text(build(),encoding='utf-8')
