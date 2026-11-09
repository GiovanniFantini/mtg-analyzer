"""Compare actual v2/v4 replay fingerprints with the pre-update Git baseline."""
import copy,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from expansion_data import Expansion,normalize_card
from bot_statistics import semantic
OUT=Path(__file__).resolve().parent
target=OUT/'functional-input-audit.json'
audit=json.loads(target.read_text(encoding='utf-8'))
commit=audit.get('baselineCommit') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def old(name):return json.loads(subprocess.check_output(['git','show',commit+':expansions/star-trek/'+name],cwd=ROOT,encoding='utf-8'))
current=Expansion(ROOT/'expansions/star-trek/expansion.json')
baseline=copy.deepcopy(current);baseline.manifest=old('expansion.json')
baseline.data={k:old(v) for k,v in baseline.manifest['datasets'].items()}
for k in ['cards','printings']:baseline.data[k]['cards']=[normalize_card(c,k+'.json') for c in baseline.data[k]['cards']]
baseline.availability=baseline.capabilities()
events={}
for event_id,event in current.data['limited']['events'].items():
 if event['kind']!='draft':continue
 before=baseline.draft_format(event_id);after=current.draft_format(event_id)
 row=dict(baselineRevision=before['revision'],currentRevision=after['revision'],baselineBotPolicyRevision=before['botPolicy']['revision'],currentBotPolicyRevision=after['botPolicy']['revision'],statisticsReference=event.get('botPolicy',{}).get('statisticsReference'),beforeEmpiricalAvailable=before['botPolicy']['empirical']['available'],afterEmpiricalAvailable=after['botPolicy']['empirical']['available'],empiricalSemanticIdentical=semantic(before['botPolicy']['empirical'])==semantic(after['botPolicy']['empirical']))
 assert row['baselineRevision']==row['currentRevision']
 assert row['baselineBotPolicyRevision']==row['currentBotPolicyRevision']
 assert row['empiricalSemanticIdentical']
 events[event_id]=row
audit.update(baselineCommit=commit,replayEvents=events,untappedEligibility=dict(provider='Untapped.gg',eligible=False,reasons=['filters.event is Early Access 2026-11-04, not one of the referenced canonical event labels.','No public wins count or documented exact WR denominator.','No licensed CC BY 4.0 17Lands S3 derivation.','bot_statistics.payload rejects it before fitting; empty eligible modes are preserved.']),replayFingerprintsIdentical=True)
target.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Identical replay fingerprints:',list(events))
