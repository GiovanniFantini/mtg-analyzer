"""Offline import of acquired Scryfall printings into the shared expansion contract.

Research scripts acquire and audit sources separately. This importer never downloads
data, imports marketplace prices, or infers booster collation from Scryfall flags.
"""
import argparse
import copy
import html
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATE = '2026-10-28'


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def apply_printed_identity(card, raw):
    """Use an explicitly selected printing's display identity, retaining Oracle.

    Some digital counterparts store printed names only on individual faces.
    This is opt-in: ordinary imports continue to use the canonical Oracle name.
    """
    raw_faces = raw.get('card_faces', [])
    printed_names = [face.get('printed_name') for face in raw_faces]
    display_name = raw.get('printed_name')
    if not display_name and printed_names and all(printed_names):
        display_name = ' // '.join(printed_names)
    if not display_name:
        return card
    card['oracleName'] = raw['name']
    card['canonicalOracleText'] = raw.get('oracle_text') or '\n//\n'.join(face.get('oracle_text', '') for face in raw_faces)
    card['printedName'] = display_name
    card['name'] = card['full'] = display_name
    display_text = raw.get('printed_text')
    if display_text is None and raw_faces:
        display_text = '\n//\n'.join(face.get('printed_text', face.get('oracle_text', '')) for face in raw_faces)
    if display_text is not None:
        card['printedText'] = display_text
        card['text'] = card['oracle'] = display_text
    for face, source in zip(card.get('faces', []), raw_faces):
        face['oracleName'] = source['name']
        face['canonicalOracleText'] = source.get('oracle_text', '')
        for original, alias in (('printed_name', 'printedName'), ('printed_text', 'printedText'), ('printed_type_line', 'printedType')):
            if original in source:
                face[original] = face[alias] = source[original]
        if source.get('printed_name'):
            face['name'] = source['printed_name']
        if 'printed_text' in source:
            face['oracle_text'] = source['printed_text']
    return card


def normalize_printing(raw):
    faces = raw.get('card_faces', [])
    face_oracles={f.get('oracle_id') for f in faces if f.get('oracle_id')}
    oracle_id=raw.get('oracle_id')
    if raw.get('layout')=='reversible_card' and len(face_oracles)==1 and all(f.get('oracle_id') for f in faces):
        oracle_id=oracle_id or next(iter(face_oracles))
    first = faces[0] if faces else raw
    images = raw.get('image_uris') or first.get('image_uris', {})
    return {
        'id': raw['id'], 'oracleId': oracle_id,
        'name': raw['name'], 'full': raw['name'],
        'set': raw['set'].upper(), 'number': raw['collector_number'],
        'mana': raw.get('mana_cost', first.get('mana_cost', '')),
        'cmc': raw.get('cmc', 0),
        'colors': raw.get('colors', first.get('colors', [])),
        'identity': raw.get('color_identity', []),
        'type': raw.get('type_line', first.get('type_line', '')),
        'text': raw.get('oracle_text') or '\n//\n'.join(f.get('oracle_text', '') for f in faces),
        'rarity': raw['rarity'], 'image': images.get('normal', ''),
        'large': images.get('large', images.get('normal', '')),
        'url': raw.get('scryfall_uri', ''), 'legalities': raw.get('legalities', {}),
        'keywords': raw.get('keywords', []), 'layout': raw.get('layout', ''),
        'power': first.get('power', ''), 'toughness': first.get('toughness', ''),
        'loyalty': first.get('loyalty', ''),
        'faces': [{k: f[k] for k in ('name', 'oracle_id', 'printed_name', 'mana_cost', 'oracle_text', 'printed_text', 'type_line', 'printed_type_line', 'power', 'toughness', 'loyalty', 'colors', 'image_uris') if k in f} for f in faces],
        'finishes': raw.get('finishes', []), 'booster': raw.get('booster'),
        'games': raw.get('games', []), 'releasedAt': raw.get('released_at'),
        'digital': raw.get('digital', False), 'promo': raw.get('promo', False),
    }


def create_expansion(slug, name, code, raw_cards, *, complete=False,
                     release_date=None, digital=False, sources=None, description=None):
    """Create a new expansion. Refuse to overwrite existing research/enrichment.

    raw_cards contains the exact, researched catalog scope. Commander belongs in a
    separate research snapshot, never in this list merely due to the release name.
    complete means the product scope was checked, not just that pagination ended.
    """
    directory = ROOT / 'expansions' / slug
    if directory.exists():
        raise FileExistsError(directory)
    manifest = copy.deepcopy(json.loads((ROOT / 'expansions/star-trek/expansion.json').read_text(encoding='utf-8')))
    manifest.update(id=slug, name=name, code=code.upper(), date=DATE,
                    description=description or 'Catalogo, legalità, pool e fonti dell’espansione.',
                    status='released' if release_date and release_date <= DATE else 'preview', assets=[])
    manifest.pop('home', None)
    manifest['storage'] = {key: f'mtg-{slug}-{key}-v1' for key in
                           ('poolPrefix', 'mode', 'watch', 'draftTable', 'sealedSimulator', 'draftPool', 'sealedPool')}
    manifest['storage']['poolPrefix'] = f'mtg-{slug}-'
    from expansion_data import FEATURES
    manifest['features'] = {key: {'requested': True} for key in FEATURES}
    # Empty events for digital/non-Limited products remain an explicit absence.
    grouped = defaultdict(list)
    unique = {raw['id']: raw for raw in raw_cards}
    for raw in unique.values():
        grouped[(raw['set'], raw.get('oracle_id') or raw['name'])].append(raw)
    cards, printings = [], []
    for entries in grouped.values():
        entries.sort(key=lambda r: (r.get('promo', False), r.get('variation', False), not r.get('booster', False), len(r['collector_number']), r['collector_number']))
        card = normalize_printing(entries[0])
        card['prints'] = []
        for entry in entries:
            printing = normalize_printing(entry)
            printing['catalogId'] = card['id']
            printings.append(printing)
            card['prints'].append({'id': printing['id'], 'number': printing['number'],
                                   'image': printing['image'], 'finishes': printing['finishes'],
                                   'url': printing['url'], 'set': printing['set']})
        cards.append(card)
    cards.sort(key=lambda c: (c['set'] != code.upper(), c['set'], len(c['number']), c['number']))
    safe_name = html.escape(name)
    catalog_note = ('Catalogo completo nel perimetro documentato.' if complete else
                    'Copertura del prodotto ancora da certificare. Le stampe acquisite sono consultabili nel catalogo.')
    gaps = [
        ('Catalogo e legalità', 'cards.json / printings.json', 'Scryfall e galleria ufficiale', catalog_note),
        ('Simulazione delle buste', 'products.json: collation', 'Wizards, Collecting e prodotti', 'Ricetta eseguibile con probabilità e trattamenti da verificare.'),
        ('Voti e guide Limited', 'ratings.json / archetypes.json / guides.json', 'Recensioni Limited attribuite', 'Acquisizione e abbinamento al catalogo da completare.'),
        ('Statistiche osservate', 'statistics.json: draft', '17Lands e Untapped', 'Snapshot con contesto, date e campioni da integrare, se disponibili.'),
        ('Constructed e Commander', 'discovery.json / cards[].prospects', 'Magic.gg, risultati e analisi specialistiche', 'Prove di adozione e analisi per carta da integrare.'),
        ('Prezzi e box', 'prices.json', 'Cardmarket', 'Prezzi per stampa e finitura da acquisire; nessuna stima del box senza collazione verificata.'),
    ]
    rows = ''.join('<tr>' + ''.join('<td>'+html.escape(v)+'</td>' for v in row) + '</tr>' for row in gaps)
    source_list = sources or []
    source_html = ''.join('<li><a href="'+html.escape(s['url'], quote=True)+'">'+html.escape(s.get('label', s.get('title', s.get('id', s['url']))))+'</a></li>' for s in source_list)
    fragments = {
        'set.hero': '<section class="site-hero"><div><h1>'+safe_name+'</h1><p>Esplora le carte, le legalità e le stampe documentate.</p><a class="site-button" href="catalogo.html">Apri il catalogo</a></div><aside><p>{{cardCount}} carte, {{printingCount}} stampe.</p><p>'+catalog_note+'</p></aside></section>',
        'method.copy-0': 'Ricerca del '+DATE+'. Le date dei cataloghi sono distinte da quelle delle statistiche e delle recensioni.',
        'method.panel-0': '<section class="trk-panel"><h2>Copertura per funzionalità</h2><div class="trk-table-wrap"><table><thead><tr><th>Funzione</th><th>Dato</th><th>Fonte</th><th>Stato</th></tr></thead><tbody>'+rows+'</tbody></table></div></section>',
        'method.panel-1': '<section class="trk-panel"><h2>Fonti della ricerca</h2><ul>'+source_html+'</ul><p>Una pagina disponibile non implica che tutte le sue misure siano state acquisite. Gli audit distinguono letture, acquisizioni e limiti.</p></section>',
        'analysis.copy-0': 'Distribuzioni del catalogo e copertura dei dati. Prezzi e statistiche assenti rimangono mancanti.',
        'draft.copy-0': 'Confronta le carte e registra il pool. La presenza nel catalogo non certifica l’apertura nel prodotto.',
        'pool.copy-0': 'Registra il pool effettivamente aperto e costruisci il mazzo.',
        'rules.copy-0': 'Espansione, prodotto ed evento sono distinti. Consulta le fonti ufficiali per il prodotto scelto.',
        'rules.panel-0': '<section class="trk-panel"><h2>Perimetro del prodotto</h2><p>'+('Espansione esclusivamente digitale. Non viene definita una busta cartacea né un evento cartaceo.' if digital else 'La composizione delle buste e i profili degli eventi vengono documentati separatamente. Nessuna estrazione simulata è disponibile senza collazione verificata.')+'</p></section>',
    }
    values = {
        'expansion': manifest,
        'cards': {'$schema': '../../schemas/cards.schema.json', 'date': DATE, 'legalityDate': DATE,
                  'complete': complete, 'partial': not complete, 'print_count': len(printings), 'cards': cards,
                  'coverage': {'mainSet': code.upper(), 'sets': sorted({c['set'] for c in cards}), 'note': catalog_note}},
        'printings': {'$schema': '../../schemas/printings.schema.json', 'date': DATE, 'cards': printings},
        'products': {'$schema': '../../schemas/products.schema.json', 'schemaVersion': 1, 'products': {}},
        'limited': {'$schema': '../../schemas/limited.schema.json', 'schemaVersion': 1, 'events': {}},
        'ratings': {'date': None, 'cards': {}}, 'archetypes': {}, 'combos': [],
        'guides': {'fragments': fragments},
        'statistics': {'catalogDate': DATE}, 'sentiment': {'cards': {}}, 'discovery': {},
        'prices': {'available': False, 'missing': [gaps[-1][3]]},
        'sources': {'date': DATE, 'links': {s.get('id', str(i)): s['url'] for i, s in enumerate(source_list)},
                    'research': {'date': DATE, 'sources': source_list}},
        'ui': {'storageNote': 'Pool separati per espansione. Esporta i salvataggi per conservarli.',
               'setLabels': {code.upper(): name}},
    }
    for key, value in values.items():
        write_json(directory / (key+'.json'), value)
    return directory


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path, help='JSON with slug, name, code, snapshots and optional release_date, complete, digital, sources')
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding='utf-8-sig'))
    raw = []
    for snapshot in config.pop('snapshots'):
        data = json.loads(Path(snapshot).read_text(encoding='utf-8-sig'))
        raw.extend(data if isinstance(data, list) else data.get('data', data.get('cards', [])))
    print(create_expansion(raw_cards=raw, **config))
