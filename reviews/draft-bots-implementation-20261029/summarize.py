"""Descriptive counts only: these diagnostics are not estimates of win rate."""
import json
from pathlib import Path
import statistics
import sys

folder = Path(sys.argv[1])
acquisition = json.loads((folder / 'results.json').read_text(encoding='utf-8'))
rows = acquisition['results']
groups = {}
for version in (3, 4):
    subset = [r for r in rows if r['version'] == version]
    decks = [d for r in subset for d in r['decks']]
    groups[str(version)] = {
        'tables': len(subset), 'botPicks': sum(len(d['pool']) for d in decks), 'decks': len(decks),
        'completeSize': sum(d['slots'] == 40 for d in decks),
        'withSpellHoles': sum(d['holes']['spells'] > 0 for d in decks),
        'manaErrors': sum(d['manaErrors'] for d in decks),
        'averageEarlyPlays': statistics.mean(d['early'] for d in decks),
        'averageInteraction': statistics.mean(d['interaction'] for d in decks),
        'medianTableRuntimeSeconds': statistics.median(r['runtimeMs']/1000 for r in subset),
        'tableMoveP95SecondsRange': [min(r['decisionTimesMs']['p95']/1000 for r in subset),
                                    max(r['decisionTimesMs']['p95']/1000 for r in subset)],
    }
output = {'manifest': acquisition['manifest'], 'groups': groups,
          'collationIdenticalWithinSeeds': all(len({r['collationHash'] for r in rows if r['seed'] == seed}) == 1 for seed in {r['seed'] for r in rows}),
          'caveat': 'V3 and v4 samples include different additional scenarios. Compare paired mixed/homogeneous tables, not group averages as a causal effect.'}
(folder / 'summary.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(output, ensure_ascii=False, indent=2))
