"""Rebuild the dated integration report and the factual coverage panels offline."""
import argparse
import html
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from expansion_data import Expansion, read_json

EXISTING = {'reality-fracture', 'star-trek'}
DATE = '2026-10-28'


def summarize(apply=False):
    report = {'schemaVersion': 1, 'date': DATE,
              'status': 'integrated_with_documented_gaps',
              'scope': '19 espansioni richieste; Commander separato dai cataloghi Limited salvo le eccezioni di prodotto documentate.',
              'sets': [], 'limitations': [
                  'Fine paginazione del catalogo e completezza del pool del prodotto sono verifiche distinte.',
                  'Le carte senza recensione conservano score null; nessuna WR viene ricavata dai voti.',
                  'I minimi Cardmarket senza filtro della finitura non sono prezzi non foil o foil.',
                  'Nessuna collazione eseguibile viene attivata senza tutti i dati necessari.',
                  'Gli snapshot API 17Lands soggetti al limite di riuso non vengono redistribuiti nei nuovi set.',
              ]}
    schema = read_json(ROOT/'schemas/prospects.schema.json')['$defs']
    for entry in read_json(ROOT/'expansions.json'):
        expansion = Expansion(ROOT/entry['manifest'])
        slug = expansion.manifest['id']
        if slug in EXISTING:
            continue
        data = expansion.data
        cards = data['cards']['cards']
        ratings = data['ratings'].get('cards', {})
        if apply:
            # The catalog's external-review filter reads community, while score
            # is also used by Limited tools. Expose the actual primary review,
            # without averaging publishers or estimating missing ratings.
            for rating in ratings.values():
                evidence = rating.get('evidence') or []
                primary = evidence[0] if evidence else {}
                value = primary.get('stars')
                if type(value) in (int, float) and 0 <= value <= 5:
                    rating['community'] = value
                    rating['communitySource'] = primary.get('url')
                    rating['communityMethod'] = 'Voto normalizzato della prima recensione attribuita in evidence; nessuna media fra fonti.'
            (expansion.directory/'ratings.json').write_text(json.dumps(data['ratings'], ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        rated = sum(ratings.get(card['id'], {}).get('score') is not None for card in cards)
        prospects = [card for card in cards if card.get('prospects')]
        errors = []
        registered_sources = {s['id'] for s in data['sources'].get('research', {}).get('sources', []) if 'id' in s}
        for card in prospects:
            p = card['prospects']
            for field in schema['cardProspects']['required']:
                if field not in p:
                    errors.append(card['name']+': manca prospects.'+field)
            for key, assessment in p.get('formats', {}).items():
                if set(schema['formatAssessment']['required'])-assessment.keys():
                    errors.append(card['name']+': formato incompleto '+key)
            unknown = set(p.get('sources', []))-registered_sources
            if unknown:
                errors.append(card['name']+': fonti sconosciute '+str(sorted(unknown)))
            price = p.get('price') or {}
            required_price = schema['cardProspects']['properties']['price']['required']
            if set(required_price)-price.keys():
                errors.append(card['name']+': contratto prezzo incompleto')
        if errors:
            raise ValueError(slug+': '+str(errors[:10]))
        references = data['prices'].get('references', {})
        research_dir = ROOT/'research'/f'{slug}-20261028'
        sources = data['sources'].get('research', {}).get('sources', [])
        row = {'id': slug, 'name': expansion.manifest['name'], 'code': expansion.manifest['code'],
               'manifest': entry['manifest'], 'researchDirectory': str(research_dir.relative_to(ROOT)).replace('\\', '/'),
               'catalogCards': len(cards), 'printings': len(data['printings']['cards']),
               'catalogBySet': dict(Counter(card['set'] for card in cards)),
               'productCatalogCertified': data['cards'].get('complete', False),
               'catalogCoverage': data['cards'].get('coverage', {}),
               'limitedRatings': rated, 'cardsWithoutLimitedRating': len(cards)-rated,
               'catalogReviewValues': sum(r.get('community') is not None for r in ratings.values()),
               'cardsWithProspects': len(prospects), 'archetypes': len(data['archetypes']),
               'priceReferences': references,
               'sources': sources, 'capabilities': expansion.availability,
               'prospectsRequiredFieldsAndReferences': 'passed'}
        report['sets'].append(row)
        if apply:
            coverage = ('Pool del prodotto certificato.' if row['productCatalogCertified'] else
                        'Catalogo acquisito consultabile; il perimetro completo del pool del prodotto resta da certificare.')
            intro = (f"<p>{len(cards)} carte e {row['printings']} stampe. {rated} carte con voto Limited attribuito; "
                     f"{len(cards)-rated} senza voto. {len(prospects)} carte con osservazioni e limiti per formato. {coverage}</p>")
            table = []
            for capability in expansion.availability.values():
                state = 'Disponibile' if capability['available'] else '; '.join(capability['missing'])
                table.append('<tr><th scope="row">'+html.escape(capability['label'])+'</th><td>'+html.escape(state)+'</td></tr>')
            guides = data['guides']
            guides.setdefault('fragments', {})['method.panel-0'] = (
                '<section class="trk-panel"><h2>Copertura effettiva dei dati</h2>'+intro+
                '<div class="trk-table-wrap"><table><thead><tr><th>Funzione</th><th>Stato o dato da completare</th></tr></thead><tbody>'+
                ''.join(table)+'</tbody></table></div></section>')
            (expansion.directory/'guides.json').write_text(json.dumps(guides, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    report['totals'] = {key: sum(s[key] for s in report['sets']) for key in
                        ('catalogCards', 'printings', 'limitedRatings', 'cardsWithoutLimitedRating', 'cardsWithProspects', 'archetypes')}
    report['totals']['expansions'] = len(report['sets'])
    destination = Path(__file__).with_name('integration-report.json')
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'report': str(destination), 'totals': report['totals']}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Update factual coverage panels as well as the report')
    summarize(parser.parse_args().apply)
