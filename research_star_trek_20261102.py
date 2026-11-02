"""Acquire public TRK research separately from the offline build.

HTML stays in a temporary cache; the repository keeps hashes, factual extracts,
coverage and original analysis. Never bypass authentication or access controls.
"""
import concurrent.futures
import hashlib
import json
import tempfile
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'research/star-trek-20261102'
CACHE = Path(tempfile.gettempdir()) / 'mtg-star-trek-research-20261102'
DATE = '2026-11-02'
SOURCES = [
    ('wizards-collecting', 'Wizards of the Coast', 'official-product', 'https://magic.wizards.com/en/news/feature/collecting-star-trek'),
    ('wizards-mechanics', 'Wizards of the Coast', 'official-rules', 'https://magic.wizards.com/en/news/feature/star-trek-mechanics'),
    ('wizards-release-trk', 'Wizards of the Coast', 'official-rules', 'https://magic.wizards.com/en/news/feature/star-trek-release-notes'),
    ('preview-calendar', 'Wizards of the Coast', 'official-calendar', 'https://magic.wizards.com/en/news/announcements/where-to-find-star-trek-previews'),
    ('wizards-arena', 'Wizards of the Coast', 'official-calendar', 'https://magic.wizards.com/en/news/mtg-arena/star-trek-event-schedule'),
    ('scg-gallery', 'Star City Games', 'preview-gallery', 'https://articles.starcitygames.com/magic-the-gathering/every-card-revealed-so-far-from-magic-the-gathering-star-trek/'),
    ('draftsim-set', 'Draftsim', 'set-overview', 'https://draftsim.com/mtg-star-trek/'),
    ('draftsim-prerelease', 'Draftsim', 'sealed-guide', 'https://draftsim.com/mtg-star-trek-prerelease/'),
    ('edhrec-debut', 'EDHREC', 'commander-editorial', 'https://edhrec.com/articles/star-trek-debut-stream-preview-recap'),
    ('edhrec-borg-queen', 'EDHREC', 'commander-deck-tech', 'https://edhrec.com/articles/star-trek-deck-tech-borg-queen-perfection-manifest'),
    ('edhrec-set', 'EDHREC', 'commander-aggregation', 'https://edhrec.com/sets/trk'),
    ('goldfish-previews', 'MTGGoldfish', 'preview-gallery', 'https://www.mtggoldfish.com/articles/star-trek-spoilers-october-21-26-borg-commander-precon'),
    ('card-kingdom', 'Card Kingdom', 'product-overview', 'https://blog.cardkingdom.com/star-trek-first-look/'),
    ('collectorunion-review', 'CollectorUnion', 'commander-editorial', 'https://collectorunion.com/blog/magic-star-trek-revealed-cards-first-impressions'),
    ('deathmarked-cruiser', 'Deathmarked', 'constructed-editorial', 'https://deathmarked.info/d-7-battle-cruiser-magic-the-gathering-card-preview-standard-potential/'),
    ('deathmarked-munitions', 'Deathmarked', 'constructed-editorial', 'https://deathmarked.info/munitions-enthusiast-star-trek-mtg-card-review-and-potential/'),
    ('standard-preview-ratings', 'MTG-Standard', 'automated-constructed-ratings', 'https://www.mtg-standard.com/powerating/TRK'),
    ('meta-limited-preview', 'MTGMeta', 'prediction-not-observed-games', 'https://mtgmeta.com/limited/trk'),
    ('untapped-pick-order', 'Untapped.gg', 'limited-ranking-availability', 'https://mtga.untapped.gg/limited/draft/star-trek/pick-order'),
    ('mylimitedgrades-trk', 'myLimitedGrades', 'limited-review-availability', 'https://mylimitedgrades.com/games/magic-the-gathering/sets/TRK'),
    ('cardmarket-spoiler', 'Cardmarket', 'marketplace', 'https://www.cardmarket.com/en/Magic/Spoilers/Star-Trek'),
    ('17lands-trk-draft', '17Lands', 'limited-statistics-availability', 'https://www.17lands.com/card_data?expansion=TRK&format=PremierDraft'),
    ('postboard-trk', 'Postboard', 'constructed-availability', 'https://www.postboard.gg/sets/trk'),
    ('wizards-commander-lists', 'Wizards of the Coast', 'official-decklists', 'https://magic.wizards.com/en/news/announcements/star-trek-commander-decklists'),
    ('cardsrealm-pauper-trk', 'Cards Realm', 'pauper-review', 'https://mtg.cardsrealm.com/en-us/articles/pauper-star-trek-set-review'),
    ('rocks-best-trk', 'MTG Rocks', 'constructed-commander-review', 'https://mtgrocks.com/mtg-star-trek-best-cards/'),
    ('nerdsnack-draft-trk', 'NerdSnack', 'limited-guide', 'https://nerdsnack.com/mtg-star-trek-draft-guide/'),
    ('turnzero-draft-trk', 'TurnZero HQ', 'limited-guide', 'https://turnzerohq.com/guides/star-trek-draft-guide'),
    ('preconforge-limited-trk', 'PreconForge', 'limited-guide', 'https://preconforge.com/mtg-star-trek-draft-sealed-guide/'),
    ('cardkingdom-klingon', 'Card Kingdom', 'commander-upgrade', 'https://blog.cardkingdom.com/star-trek-klingon-fury-commander-deck-upgrade-guide/'),
    ('cardsrealm-standard-trk', 'Cards Realm', 'standard-review', 'https://mtg.cardsrealm.com/en-us/articles/standard-star-trek-review-for-the-format'),
    ('cardsrealm-commander-trk', 'Cards Realm', 'commander-product-review', 'https://mtg.cardsrealm.com/en-us/articles/star-trek-which-precon-is-right-for-you'),
]
for color in ['white', 'blue', 'black', 'red', 'green', 'multicolor', 'artifacts-and-lands']:
    SOURCES.append(('arenazone-trk-' + color, 'MTG Arena Zone', 'limited-review',
                    'https://mtgazone.com/star-trek-trk-limited-set-review-' + color + '/'))


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if tag in ('p', 'div', 'li', 'tr', 'td', 'h1', 'h2', 'h3', 'a', 'br'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
        if tag in ('p', 'div', 'li', 'tr', 'td', 'h1', 'h2', 'h3', 'a'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def text(self):
        return '\n'.join(x.strip() for x in ''.join(self.parts).splitlines() if x.strip())


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def fetch(source):
    ident, publisher, kind, url = source
    record = dict(id=ident, publisher=publisher, kind=kind, url=url, retrieved=DATE)
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'MTG-Analyzer-Research/1.0', 'Accept': 'text/html'})
        with urllib.request.urlopen(request, timeout=40) as response:
            raw = response.read()
            record['finalUrl'] = response.url
        parser = Parser()
        parser.feed(raw.decode('utf-8', errors='replace'))
        content = parser.text()
        (CACHE / (ident + '.html')).write_bytes(raw)
        (CACHE / (ident + '.txt')).write_text(content, encoding='utf-8')
        record.update(status='retrieved_unreviewed', bytes=len(raw), textCharacters=len(content), sha256=hashlib.sha256(raw).hexdigest())
    except Exception as error:
        record.update(status='unavailable', error=str(error))
    return record


def catalog(query_text='(set:trk or set:sds)', filename='scryfall.json'):
    url = 'https://api.scryfall.com/cards/search?' + urllib.parse.urlencode({'q': query_text, 'unique': 'prints', 'order': 'set'})
    query = url
    rows, pages = [], []
    while url:
        request = urllib.request.Request(url, headers={'User-Agent': 'MTG-Analyzer-Research/1.0', 'Accept': 'application/json'})
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
        page = json.loads(raw)
        pages.append({'url': url, 'rows': len(page['data']), 'totalCards': page['total_cards'], 'sha256': hashlib.sha256(raw).hexdigest()})
        rows.extend(page['data'])
        url = page.get('next_page')
        time.sleep(0.12)
    assert len(rows) == pages[0]['totalCards']
    assert len({r['id'] for r in rows}) == len(rows)
    save(OUT / filename, {'date': DATE, 'source_query': query, 'pages': pages, 'data': rows})
    print('Scryfall:', len(rows), 'printings,', len({r['oracle_id'] for r in rows}), 'identities')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(fetch, SOURCES))
    save(OUT / 'source-audit.json', {'date': DATE, 'sources': records, 'rawHtmlLocation': 'temporary cache, not versioned'})
    for r in records:
        print(r['id'], r['status'], r.get('textCharacters', r.get('error')))
    catalog()
    catalog('set:trc', 'scryfall-commander.json')


if __name__ == '__main__':
    main()
