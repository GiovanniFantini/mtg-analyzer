"""Acquire dated public sources. Raw third-party articles stay in temporary storage."""
import concurrent.futures
import tempfile
from pathlib import Path
import research_star_trek_20261102 as previous

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'research/star-trek-20261107'
CACHE = Path(tempfile.gettempdir()) / 'mtg-star-trek-research-20261107'
EXTRA = [
    ('edhrec-typal', 'EDHREC', 'commander-review', 'https://edhrec.com/articles/star-trek-typal-set-review'),
    ('edhrec-artifacts', 'EDHREC', 'commander-review', 'https://edhrec.com/articles/the-best-lands-and-artifacts-in-star-trek'),
    ('edhlab-review', 'EDH LAB', 'commander-review', 'https://blog.edhlab.gg/magic-star-trek-set-review/'),
    ('cardsrealm-pioneer', 'Cards Realm', 'pioneer-review', 'https://mtg.cardsrealm.com/en-us/articles/pioneer-star-trek-review-goes-live'),
    ('cardsrealm-legacy', 'Cards Realm', 'legacy-review', 'https://mtg.cardsrealm.com/en-us/articles/legacy-star-trek-set-review'),
    ('arenazone-historic', 'MTG Arena Zone', 'historic-review', 'https://mtgazone.com/historic-brewing-review-star-trek/'),
    ('limitedlibrary-data', 'Limited Library', 'limited-ratings', 'https://limitedlibrary.com/sets/star-trek/set-data.js'),
    ('limitedlibrary', 'Limited Library', 'limited-review-aggregation', 'https://limitedlibrary.com/sets/star-trek/'),
    ('limitedmtg', 'LimitedMTG', 'computed-card-analysis', 'https://limitedmtg.com/star-trek/'),
    ('mtgsold', 'MTGsold', 'limited-review', 'https://mtgsold.com/'),
    ('metagame-guide', 'Metagame', 'limited-guide', 'https://metagame.info/en-us/mtg/articles/limited-magic-star-trek-limited-a-complete-guide-to-draft-sealed-and-prerelease'),
    ('untapped-sealed', 'Untapped.gg', 'sealed-statistics', 'https://mtga.untapped.gg/limited/sealed/star-trek/card-data?eventType=SEALED'),
    ('untapped-draft', 'Untapped.gg', 'draft-statistics', 'https://mtga.untapped.gg/limited/draft/star-trek/card-data'),
    ('draftsim-review', 'Draftsim', 'limited-review', 'https://draftsim.com/mtg-trk-limited-set-review/'),
    ('cardsrealm-modern', 'Cards Realm', 'modern-review', 'https://mtg.cardsrealm.com/en-us/articles/modern-star-trek-set-review'),
]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    previous.OUT, previous.CACHE, previous.DATE = OUT, CACHE, '2026-11-07'
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(previous.fetch, previous.SOURCES + EXTRA))
    previous.save(OUT / 'source-audit.json', {'date': previous.DATE, 'sources': rows})
    print([(r['id'], r['status'], r.get('textCharacters', r.get('error'))) for r in rows])

if __name__ == '__main__':
    main()
