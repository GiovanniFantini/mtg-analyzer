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
    files = ['bot_profiles.py','test_bot_profiles.py','draft-table.js','draft-worker.js','draft-worker-client.js',
             'verify-draft-worker.cjs','verify-draft-worker-client.cjs','verify-draft-worker-browser.cjs','verify-draft-policy-browser.cjs',
             'verify-draft-performance.cjs','docs/requirements.md','docs/draft-engine.md',
             'reviews/draft-bots-production-20261029/interaction-audit-input.json',
             'reviews/draft-bots-production-20261029/core-since-review4-after-transport.json',
             'reviews/draft-bots-production-20261029/code-review-4.review.json',
             'reviews/draft-bots-production-20261029/status.json']
    evidence = DEST / 'local-verification.json'
    if evidence.exists():
        files += ['reviews/draft-bots-production-20261029/local-verification.json',
                  'reviews/draft-bots-production-20261029/report.md']
    focused = len(sys.argv) > 3 and sys.argv[3] == 'focused'
    if focused:
        files = ['draft-policy.js', 'bot_profiles.py', 'draft-table.js',
                 'verify-draft-policy.cjs', 'verify-draft-policy-regressions.cjs',
                 'docs/requirements.md']
    instructions = """Agisci come revisore indipendente Opus senior software developer con competenza Magic Limited. Il cliente chiede code review e cicli di correzione fino a essere entrambi convinti della prontezza per produzione. Ricevi requisiti aggiornati completi, implementazione e rapporto empirico. Non hai strumenti e non devi dichiarare test eseguiti da te.
I primi quattro giri di questa review sono registrati in code-decisions fornito. Questo giro e mirato alla chiusura di PROD-31/32/33. Policy, motore, worker e client sono byte-identici al giro4, gia controllati integralmente senza nuovi P1: manifest verificato fornito. Sono cambiati soltanto classificazione dei ruoli, UI della revisione e criteri della prova. Verifica le decisioni Oracle 75/8 contro il testo reale fornito, comprese risposte condizionate e scarto mirato. Non considerare danni solo al giocatore come rimozione. Il helper e conservativo e il resto delle meccaniche non modellate resta dichiarato. Ricontrolla le correzioni sui moduli attuali, senza assumere ancora presente il vecchio codice. Loader e collator sono invariati rispetto ai giri 1 e 2. Le misure nel status sono esplicitamente della versione precedente e verranno rifatte prima del via libera finale. Non confondere emulazione viewport touch su desktop con hardware mobile o throttling del worker. Non rendere requisiti di promozione generale condizioni per il rilascio sperimentale. La precedente review storica ha chiuso 28 difetti nel perimetro opt-in sperimentale. Ora valuta realmente la prontezza del rilascio con default v3 e opzione v4, distinta dalla promozione competitiva/default v4. Non attenuare bug perche sperimentale. Esamina in particolare allocazione mana senza fonti possedute nel denominatore, turno utile splash +2 che puo favorire artificialmente una lane rispetto alla stessa magia in colore principale, prestazioni UI sincrone p95 3-5 secondi e ripresa completa. Conferma cause precise e proponi correzioni bounded concretamente implementabili, compatibili con vecchi replay. I dati causali incompleti non vanno inventati: disattivazione uniforme e lacune visibili sono requisito esplicito, non pretesto per promettere competenza generale. Non richiedere interpretazione completa di Oracle o WR non misurata. Cerca anche altri bug concreti nel codice e nei contratti. Ogni rilievo deve avere scenario, evidenza, conseguenza e fix verificabile. Nessuna preferenza estetica o ampliamento generico. Specifica requisiti obbligatori per il rilascio e separatamente condizioni per cambiare default.
I P2 opzionali sono stati esplicitamente decisi nel registro. Segnala come nuovi blocchi solo problemi concreti di correttezza o criteri obbligatori violati nel perimetro del rilascio sperimentale. Non trasformare ottimizzazioni facoltative o la promozione a default in condizioni di rilascio. Valuta gli esiti finali quando local-verification.json e presente. Se manca, le prove complete rimangono pending. Non attribuire una review al tentativo 5, rifiutato per quota.
Restituisci solo JSON {"findings":[{"id":"PROD-...","priority":"P1/P2","file":"...","scenario":"...","evidence":"...","impact":"...","fix":"..."}],"releaseReady":false,"promotionReady":false,"summary":"...","acceptance":["..."]}. Findings vuoto solo se non restano difetti concreti. Italiano senza grassetto o trattino lungo.
"""
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
