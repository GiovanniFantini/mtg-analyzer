"""Build the standalone simulator from the existing catalog; no network needed."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def build():
    data = json.loads((ROOT / 'sealed-database.json').read_text(encoding='utf-8'))
    html = (ROOT / 'simulator-template.html').read_text(encoding='utf-8')
    html = html.replace('__DATA__', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
    (ROOT / 'Reality-Fracture-Simulatore.html').write_text(html, encoding='utf-8')

if __name__ == '__main__':
    build()
