"""Independent implementation or anonymized deck review through actual Opus."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
DEST = Path(__file__).resolve().parent
mode, number = sys.argv[1:3]
prefix = DEST / (mode + '-review-' + number)
if prefix.with_suffix('.request.txt').exists():
    raise SystemExit('Review already recorded')
if mode == 'code':
    files = ['draft-policy.js', 'bot_profiles.py', 'draft-engine.js', 'draft-table.js',
             'expansion_data.py', 'verify-draft-policy.cjs', 'test_bot_profiles.py',
             'verify-draft-policy-regressions.cjs', 'collation.js',
             'schemas/bot-policy.schema.json', 'docs/requirements.md']
    focused = len(sys.argv) > 3 and sys.argv[3] == 'focused'
    if focused:
        files = ['draft-policy.js', 'bot_profiles.py', 'draft-table.js',
                 'verify-draft-policy.cjs', 'verify-draft-policy-regressions.cjs',
                 'docs/requirements.md']
    instructions = '''Agisci come revisore indipendente Opus, software developer senior con competenza Magic Limited.
Controlla l'implementazione v4 dei requisiti BOT forniti. Non devi modificare file e non hai strumenti.
Focalizzati su bug concreti di correttezza, main costruibile, mana, alternative, sinergie causali, pivot, informazione parziale, replay e disponibilita. Ogni rilievo deve avere scenario dimostrabile dal codice e conseguenza concreta, senza pretendere implementazione di ogni meccanica di Magic.
Il default resta v3; v4 e opt-in sperimentale. Le relazioni incomplete sono volutamente disattivate nell'intero evento e non sono dati da inventare. I profili minimi inferiti da Oracle sono una classificazione funzionale conservativa, non una completa interpretazione delle regole. Il modello di mana e probabilistico/euristico dichiarato, non una partita. Non richiedere promozione, WR o dati fittizi; non fare review generale del caricatore fuori dalle modifiche.
Le fixture legacy e nuove sono gia eseguite, ma puoi rilevare casi non coperti. Non dichiarare tu di aver eseguito test, letto fonti esterne o visto il browser. Valuta ogni ipotesi contro il codice completo, non inferire un bug da una parola isolata. Non segnalare preferenze estetiche o ampliamenti. Se la specifica richiede una capacita disattivata con dati incompleti, non chiamare quella disattivazione un difetto.
Restituisci solo JSON: {"findings":[{"id":"CODE-...","priority":"P1/P2","file":"...","scenario":"...","evidence":"...","impact":"...","fix":"..."}],"summary":"..."}. Findings vuoto se non restano difetti concreti. Italiano, senza grassetto o trattino lungo.
'''
    if focused:
        instructions += '\nRound mirato finale: motore storico, collazione, caricatore e schema non sono cambiati dagli input del round 4. Ricontrolla le correzioni CODE-21/24 e le altre decisioni contro i moduli completi forniti, incluso il limite copie con manaOnly corretto dopo la richiesta precedente. Cerca regressioni concrete nel perimetro modificato. Non riaprire funzionalita disattivate o meccaniche non dichiarate come supportate.\n'
else:
    files = [sys.argv[3]]
    instructions = '''Agisci come secondo analista esperto di Magic Limited, senza attribuirti qualifiche personali reali.
Esamina alla cieca i mazzi e le pick anonimizzati forniti, costruiti da pool di un draft simulato. Non sai quale politica li ha draftati. Non cercare di dedurla e non usare conoscenze di risultati esterni non forniti. Usa testo e statistiche stampate delle carte fornite nel catalogo cards: main, lands, poolBefore, observed e selected lo referenziano per id. manaOnly identifica carte usate solo come fixing, non come minacce.
Valuta piano di vittoria, giocate iniziali, interazione, base di mana e sinergie plausibili. Se manca un dato non inventarlo e segnala il limite. Non dedurre forza in partita o WR. Sono liste diagnostiche costruite dallo stesso algoritmo per tutte le politiche, quindi potrebbero avere difetti di costruzione oltre a quelli del draft. Distinguili dove possibile. Per le pick sono forniti pool precedente e busta osservata: giudica opportunita, piano e alternativa concreta senza conoscere le buste future o i pool altrui.
Per ogni lista indica giudizio qualitativo, criticita concrete e limiti. Usa la stessa rubrica per tutti. Non trasformare preferenze di archetipo in errori.
Valuta soltanto le sezioni presenti nell'input. La valutazione delle pick viene acquisita separatamente da quella dei mazzi finali, per evitare informazioni sul futuro: se non sono presenti decks restituisci decks vuoto, e analogamente per picks. Non collegare le pick ad altre acquisizioni.
Nelle pick non hai la sequenza completa delle buste precedenti ne il profilo stilistico: considera questi limiti quando una scelta potrebbe dipendere da segnali o preferenze del bot. Distingui una scelta discutibile da un errore dimostrabile sul solo pool e sulla busta osservata.
Restituisci solo JSON {"decks":[{"id":"...","assessment":"...","issues":["..."],"uncertainties":["..."]}],"picks":[{"id":"...","assessment":"...","preferred":"id della scelta preferita oppure uncertain","reason":"..."}],"summary":"...","promotionEvidence":"sufficient/insufficient"}. Italiano, senza grassetto o trattino lungo. L'assenza di dati comparativi e un motivo per non attestare miglioramento.
'''
manifest = {'mode': mode, 'requestedModel': 'opus', 'files': {
    name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}}
prompt = instructions + '\nMANIFEST\n' + json.dumps(manifest)
for name in files:
    prompt += '\nFILE ' + name + '\n' + (ROOT / name).read_text(encoding='utf-8')
decisions = DEST / 'code-decisions.json'
if mode == 'code' and decisions.exists():
    prompt += '\nPREVIOUS DECISIONS TO RECHECK\n' + decisions.read_text(encoding='utf-8')
prefix.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
prefix.with_suffix('.request.txt').write_text(prompt, encoding='utf-8')
cli = shutil.which('claude')
if not cli:
    raise SystemExit('Claude CLI unavailable')
result = subprocess.run([cli, '--print', '--model', 'opus', '--effort', 'high',
    '--output-format', 'json', '--tools', '', '--strict-mcp-config',
    '--no-session-persistence', '--safe-mode'], cwd=ROOT, input=prompt,
    encoding='utf-8', text=True, capture_output=True)
prefix.with_suffix('.response.json').write_text(result.stdout, encoding='utf-8')
prefix.with_suffix('.stderr.txt').write_text(result.stderr, encoding='utf-8')
data = json.loads(result.stdout)
assert not data.get('is_error') and not result.returncode, data.get('result')
assert any('opus' in key for key in data.get('modelUsage', {})), 'Opus not confirmed'
content = data['result'].strip()
if content.startswith('```'):
    content = content.split('\n', 1)[1].rsplit('```', 1)[0].strip()
review = json.loads(content)
prefix.with_suffix('.review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'models': list(data['modelUsage']), 'review': review}, ensure_ascii=True))
