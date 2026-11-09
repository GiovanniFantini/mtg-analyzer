"""Dated public acquisitions; raw articles remain outside the repository."""
import concurrent.futures
import tempfile
from pathlib import Path
import research_star_trek_20261102 as base
import research_star_trek_20261107 as previous

OUT = Path(__file__).resolve().parent / 'research/star-trek-20261109'
CACHE = Path(tempfile.gettempdir()) / 'mtg-star-trek-research-20261109'

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    base.OUT, base.CACHE, base.DATE = OUT, CACHE, '2026-11-09'
    sources = base.SOURCES + previous.EXTRA + [
        ('mtgsold-limited', 'MTGsold', 'limited-review', 'https://mtgsold.com/blog/editorials/star-trek-limited-set-review/'),
        ('wpn-dates', 'Wizards of the Coast', 'official-calendar', 'https://wpn.wizards.com/en/news/star-trek-dates-and-details'),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(base.fetch, sources))
    base.save(OUT / 'source-audit.json', {'date': base.DATE, 'sources': rows})
    print([(r['id'], r['status'], r.get('textCharacters', r.get('error'))) for r in rows])

if __name__ == '__main__':
    main()
