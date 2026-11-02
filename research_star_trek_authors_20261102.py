"""Integrate the attributed author research offline, without changing grades/prices.

Input: the curated, dated evidence ledger beside the report. Repeated imports
replace only notes owned by this import. No network is used.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'research/star-trek-authors-20261102'
BASE = ROOT / 'expansions/star-trek'
ORIGIN = 'author-feedback-20261102'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    evidence = read(OUT / 'evidence.json')
    doc = read(BASE / 'cards.json')
    sources = {s['id']: s for s in evidence['sources']}
    by_card = defaultdict(list)
    for row in evidence['observations']:
        by_card[row['catalogId']].append(row)
    coverage = []
    for card in doc['cards']:
        p = card['prospects']
        rows = by_card.get(card['id'], [])
        p['researchNotes'] = [n for n in p.get('researchNotes', []) if n.get('origin') != ORIGIN]
        for row in rows:
            src = sources[row['source']]
            published = row.get('published', src.get('published'))
            date_label = 'pubblicato ' + published if published else 'data originale non verificata'
            p['researchNotes'].append({
                'id': row['id'], 'origin': ORIGIN, 'date': evidence['date'],
                'published': published,
                'author': row['author'], 'context': row['author'] + ' / ' + row['context'] + ' / ' + date_label,
                'finding': row['finding'], 'sources': [row['source']],
                'kind': row['kind'], 'url': row.get('url', src['url']),
            })
        p['sources'] = sorted(set(p['sources']) | {r['source'] for r in rows})
        status = {
            'date': evidence['date'], 'scope': ORIGIN,
            'status': 'attributed_opinion' if rows else 'not_found_in_this_collection',
            'observations': len(rows), 'authors': sorted({r['author'] for r in rows}),
            'contexts': sorted({r['context'] for r in rows}),
            'financialForecastVerified': False,
        }
        p['humanReviewCoverage'] = status
        coverage.append({'id': card['id'], 'name': card['name'], **status})
    write(BASE / 'cards.json', doc)
    # References are for previews only. They never enter the game catalog/pools.
    discovery = read(BASE / 'discovery.json')
    previews = {r['id']: r for r in discovery.get('previews', [])}
    previews.update({r['id']: r for r in evidence.get('previewReferences', [])})
    discovery['previews'] = list(previews.values())
    write(BASE / 'discovery.json', discovery)
    registry = read(BASE / 'sources.json')
    existing = {s['id']: s for s in registry['research']['sources']}
    existing.update(sources)
    registry['research']['sources'] = list(existing.values())
    summary = {
        'date': evidence['date'], 'scope': ORIGIN, 'catalogCards': len(coverage),
        'cardsWithOpinion': sum(bool(r['observations']) for r in coverage),
        'cardsWithoutOpinion': sum(not r['observations'] for r in coverage),
        'observations': sum(r['observations'] for r in coverage),
        'authors': sorted({r['author'] for r in evidence['observations']}),
        'contextObservations': dict(Counter(r['context'] for r in evidence['observations'])),
        'trcObservations': len(evidence['commanderAppendixObservations']),
        'verifiedFinancialTrackRecords': 0,
        'report': 'research/star-trek-authors-20261102/README.md',
    }
    registry['research']['authorFeedback'] = summary
    write(BASE / 'sources.json', registry)
    write(OUT / 'coverage.json', {'summary': summary, 'cards': coverage})
    guide = read(BASE / 'guides.json')
    fragment = guide['fragments']['analysis.panel-1']
    start, end = '<!-- author-feedback -->', '<!-- /author-feedback -->'
    if start in fragment:
        fragment = fragment.split(start)[0] + fragment.split(end, 1)[1]
    guide['fragments']['analysis.panel-1'] = fragment
    fragment = guide['fragments'].get('analysis.copy-0', '')
    if start in fragment:
        fragment = fragment.split(start)[0] + fragment.split(end, 1)[1]
    fragment += start + '<section class="trk-panel"><h2>Giudizi degli autori e dissensi</h2>'
    fragment += '<p>' + str(summary['cardsWithOpinion']) + ' carte TRK/SDS con nuovi pareri attribuiti; ' + str(summary['cardsWithoutOpinion']) + ' senza pareri trovati in questa raccolta. Leggi autore, contesto e motivazione nelle schede del catalogo, sotto “Previsioni automatiche e letture delle fonti”.</p>'
    fragment += '<p>Steve, Usman e Kai avevano già valutato Jace in FRA. I loro giudizi Cube su Star Trek divergono: Dr. Leonard &quot;Bones&quot; McCoy è una priorità per Usman ma medio-basso per Steve; Holo-Engineer e Voq, Torchbearer mostrano il dissenso opposto. Salt Vampire piace in Cube, con riserve specifiche su Modern. Questi segnali non certificano un rialzo di prezzo.</p>'
    fragment += '<p>Su Reddit è stata rintracciata una previsione esplicita di Cautious_Handle2547 su Jace; il timestamp assoluto non è verificato e non sono stati trovati suoi pareri TRK. Non è stato assegnato alcun indice di affidabilità economica.</p>'
    fragment += '<p><a href="author-feedback-evidence.json" download>Autori, osservazioni e provenienza</a> · <a href="author-feedback-coverage.json" download>Copertura e lacune per tutte le carte</a></p></section>' + end
    guide['fragments']['analysis.copy-0'] = fragment
    write(BASE / 'guides.json', guide)
    manifest = read(BASE / 'expansion.json')
    for asset in ('research/star-trek-authors-20261102/author-feedback-evidence.json', 'research/star-trek-authors-20261102/author-feedback-coverage.json'):
        if asset not in manifest['assets']:
            manifest['assets'].append(asset)
    write(BASE / 'expansion.json', manifest)
    write(OUT / 'author-feedback-evidence.json', evidence)
    write(OUT / 'author-feedback-coverage.json', {'summary': summary, 'cards': coverage})
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
