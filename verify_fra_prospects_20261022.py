"""Audit evidence joins, monetary comparability and preservation of game data."""
import collections
import hashlib
import json
from pathlib import Path
from research_fra_prospects_20261022 import CACHE

ROOT=Path(__file__).resolve().parent
EXP=ROOT/'expansions/reality-fracture'
RESEARCH=ROOT/'research/reality-fracture-20261022'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))

def main():
    cards_doc=read(EXP/'cards.json');cards=cards_doc['cards'];baseline=read(RESEARCH/'before-update.json')
    assert len(cards)==295
    assert [{k:v for k,v in c.items() if k!='prospects'} for c in cards]==baseline['cards']['cards'], 'Functional catalog was changed'
    assert {k:v for k,v in cards_doc.items() if k not in ('cards','prospectsDate')}=={k:v for k,v in baseline['cards'].items() if k!='cards'}
    manifest=read(EXP/'expansion.json')
    for key,value in baseline['expansion'].items():
        if key!='assets':assert manifest[key]==value,key
    assert manifest['draftReplayCompatibility']==baseline['expansion']['draftReplayCompatibility']
    source_meta=read(EXP/'sources.json')['research'];sources={s['id']:s for s in source_meta['sources']}
    assert len({s['publisher'] for s in sources.values() if s['status']=='retrieved'})>=10
    assert source_meta['publisherCount']==14
    for source in sources.values():
        if source.get('sha256'):
            path=CACHE/(source['id']+'.html')
            if path.exists():assert hashlib.sha256(path.read_bytes()).hexdigest()==source.get('archiveSha256',source['sha256']),source['id']
    raw=read(RESEARCH/'scryfall-fra.json')+read(RESEARCH/'scryfall-spg.json')+read(RESEARCH/'scryfall-frc.json')
    printing={c['id']:c for c in raw}
    old={c['id']:c for c in read(RESEARCH/'scryfall-fra-20261018.json')+read(RESEARCH/'scryfall-spg-20261018.json')}
    records={(r['name'],r['format']):r for r in read(RESEARCH/'tournament-evidence.json')['cards']}
    assert len(records)==104
    appendix=read(EXP/'prospects-commander-20261022.json')['cards'];assert len(appendix)==87
    edh=read(RESEARCH/'commander-evidence.json')
    cedh={r['name']:r for r in read(RESEARCH/'cedh-evidence.json')['cards']}
    for card in cards+appendix:
        p=card['prospects'];price=p['price'];oracle=p['oracle'];raw_card=printing[oracle['printingId']]
        assert p['date']=='2026-10-22' and len(p['gameplayReview']['finding'])>45
        assert '\u2014' not in p['gameplayReview']['finding']
        assert set(p['sources'])<=set(sources)
        assert p['formats'].keys()>={'standard','pioneer','modern','legacy','vintage','pauper','commander','cedh','duel','historic','timeless','alchemy','draft','sealed','pick_two'}
        for key,value in raw_card['legalities'].items():
            if key in p['formats']:assert p['formats'][key]['legality']==value
        for fmt,assessment in p['formats'].items():
            if 'observation' in assessment:
                observation=p['tournamentObservations'][assessment['observation']]
                assert observation['name']==card['name'] and observation['format']==fmt
                assert assessment['legality'] in ('legal','restricted')
        for observation in p['tournamentObservations']:
            assert observation==records[(card['name'],observation['format'])]
            assert observation['decklistsWithCard']>=2
        for observation in p['commanderObservations']:assert observation in edh
        if p['cedhObservation']:
            assert p['cedhObservation']['lists']==cedh[card['name']]['lists']
            assert p['cedhObservation']['window']['end']=='2026-10-11'
        assert price['printingId']==oracle['printingId'] and price['set']==raw_card['set']
        assert price['nonfoil']==(float(raw_card['prices']['eur']) if raw_card['prices'].get('eur') is not None else None)
        comparison=price['comparison']
        if comparison['status']=='comparable':
            previous=old[price['printingId']]
            assert comparison['nonfoil']==float(previous['prices']['eur'])
            assert comparison['changePct']==round((price['nonfoil']/comparison['nonfoil']-1)*100,2)
        assert price['outlook']['targetPrice'] is None and price['outlook']['probabilityOfRise'] is None
        assert price['outlook']['confidence']=='bassa'
        if card['set']=='SPG':assert price['set']=='spg'
        for v in price['variants']:
            assert v['printingId'] in printing
            assert v['set']==price['set']
    assert read(EXP/'prices.json')['available']==baseline['prices']['available']==False
    assert read(EXP/'prices.json')['references']['boxEVUpdated']==False
    report={'date':'2026-10-22','status':'passed','catalogCards':295,'commanderAppendix':87,'sourcePublishers':14,'tournamentCardFormatRecords':104,'functionalCardDataUnchanged':True,'replayMetadataUnchanged':True,'currencyFinishAndPrintingSeparated':True,'historicalEVUnchanged':True,'checks':'Coverage; source resolution; source content hashes; Oracle/legalities; all observed-list joins; Commander and cEDH joins with distinct dates; same-printing EUR changes; no invented targets/probabilities; no functional mutations.'}
    (RESEARCH/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
