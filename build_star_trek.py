"""Historical entry point; Star Trek uses the shared expansion builder."""
from expansion_data import ROOT, Expansion
from build_expansion import build as build_expansion


def build(dest):
    return build_expansion(Expansion(ROOT/'expansions/star-trek/expansion.json'),dest)
