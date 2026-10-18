"""Build the offline set explorer from the existing, attributed card database."""
import json
from pathlib import Path

ROOT = Path(__file__).parent

def build():
    data = json.loads((ROOT / 'sealed-database.json').read_text(encoding='utf-8'))
    raw = {c['name']: c for name in ['fra-all.json', 'fra-spg.json']
           for c in json.loads((ROOT / name).read_text(encoding='utf-8'))}
    for c in data['cards']:
        source = raw[c['full']]
        faces = source.get('card_faces') or [source]
        c['keywords'] = source.get('keywords', [])
        c['faces'] = [{k: f.get(k, '') for k in ['name', 'mana_cost', 'type_line', 'oracle_text', 'power', 'toughness']} for f in faces]
        c['power'] = faces[0].get('power', '')
        c['toughness'] = faces[0].get('toughness', '')
    html = (ROOT / 'analysis-template.html').read_text(encoding='utf-8')
    from sentiment_data import render_assets
    html = render_assets(html, ROOT)
    (ROOT / 'Reality-Fracture-Analisi.html').write_text(html.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/')), encoding='utf-8')
    print('Analisi: ' + str(len(data['cards'])) + ' carte, keyword e facce complete.')

if __name__ == '__main__':
    build()
