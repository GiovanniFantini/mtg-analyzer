"""Audit the regenerated public datasets without rewriting historical evidence."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tournament_index import FORMATS,validate_index

out=ROOT/'research/production-opus-20261028/final-data-audit.json'
if out.exists():raise SystemExit('Audit already exists; preserve it and choose a new report.')
report={'scope':'Regenerated tournament/WR data after Opus corrections','expansions':[],
        'indices':0,'wrRows':0,'identityGroupsCompared':0,'fingerprints':{},'examples':[]}
oracle_observations={}
plan=json.loads((ROOT/'research/production-opus-20261028/wr-recovery-plan.json').read_text(encoding='utf-8'))
recovered=0
for registration in json.loads((ROOT/'expansions.json').read_text()):
    root=ROOT/Path(registration['manifest']).parent
    cards=json.loads((root/'cards.json').read_text(encoding='utf-8'))['cards']
    statistics=json.loads((root/'statistics.json').read_text(encoding='utf-8'))
    discovery=json.loads((root/'discovery.json').read_text(encoding='utf-8'))
    by_name={c['name']:c for c in cards}
    for c in cards:
        p=c['prospects']
        for f in FORMATS:
            index=p['formats'][f]['tournamentIndex'];validate_index(index)
            assert index['trend']['method']=='matched-cohort-v1',(root.name,c['id'],f)
            assert index.get('legalityDate')==c.get('legalitiesRetrieved')
            for period in ('previous','recent'):
                row=index['trend'][period]
                assert 'start' in row and 'end' in row
                assert (row['start'] is None)==(row['end'] is None)
                if row['start'] is None:assert row['reason']=='not_eligible_in_period' and row['decks']==0
                else:assert row['start']<=row['end']
            if c.get('oracleId'):
                key=(c['oracleId'],f)
                observed=(index['sample']['decks'],index['observed']['withCard'],index['observed']['mainCopies'],index['observed']['sideboardCopies'])
                if key in oracle_observations:
                    assert oracle_observations[key]==observed,(root.name,c['name'],f,'cross-catalog identity mismatch')
                    report['identityGroupsCompared']+=1
                oracle_observations[key]=observed
            report['indices']+=1
        if p.get('analysisCoverage')=='tournament_data_only' and p.get('price',{}).get('metric')=='non disponibile':assert p['price']['status']=='not_collected'
        if len(report['examples'])<3 and any(p['formats'][f]['tournamentIndex']['score'] for f in FORMATS):
            report['examples'].append({'expansion':root.name,'card':c['name'],'tournamentLevel':p.get('tournamentLevel'),'analysisCoverage':p.get('analysisCoverage'),'priceStatus':p.get('price',{}).get('status'),'standard':p['formats']['standard']['tournamentIndex']})
    for selected in discovery['cards']:
        card=by_name.get(selected['name'])
        if not card:continue
        for f,index in selected.get('tournamentIndices',{}).items():
            assert index==card['prospects']['formats'][f]['tournamentIndex'],(root.name,selected['name'],f,'stale discovery index')
    assert 'trendPeriods' in discovery['tournamentResearch']
    for kind in ('draft','sealed'):
        snapshot=statistics.get(kind,{}).get('externalSources',{}).get('17lands-public')
        if not snapshot:continue
        rows={r['catalogId']:r for r in snapshot['cards']}
        for row in rows.values():
            metrics=row['metrics'];n=metrics['games'];wins=metrics['wins'];rate=metrics['inHandWinRate']
            assert 0<=wins<=n
            assert rate is None if not n else abs(rate-100*wins/n)<1e-9
            report['wrRows']+=1
        for expected in plan:
            if expected['expansion']==root.name and expected['kind']==kind:
                for ident in expected['recoverableCards']:
                    assert ident in rows,(root.name,kind,ident,'recoverable card still missing')
                    recovered+=1
    for name in ('cards.json','statistics.json','discovery.json','sources.json','printings.json','expansion.json'):
        path=root/name
        report['fingerprints'][path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    report['expansions'].append({'id':root.name,'cards':len(cards),'selected':len(discovery['cards'])})
report['recoveredCardEventRows']=recovered
report['passed']=True
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('fingerprints','examples','expansions')},ensure_ascii=False))
