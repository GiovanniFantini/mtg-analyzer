"""Repair face-only digital aliases using the acquired Scryfall crosswalk."""
import json
from pathlib import Path
from import_expansion_catalogs import apply_printed_identity, write_json

def main():
    folder=Path('expansions/through-the-omenpaths')
    research=Path('research/through-the-omenpaths-20261028')
    raw=json.loads((research/'om1-cards.json').read_text(encoding='utf-8'))['cards']
    by_id={c['id']:c for c in raw}
    counterpart=json.loads(Path('research/marvel-spider-man-20261028/spm-cards.json').read_text(encoding='utf-8'))['cards']
    by_oracle={}
    for card in counterpart:
        by_oracle.setdefault(card.get('oracle_id'),[]).append(card)
    crosswalk=[]
    for card in raw:
        peers=by_oracle.get(card.get('oracle_id'),[])
        crosswalk.append({'printingId':card['id'],'oracleId':card.get('oracle_id'),
                          'oracleName':card['name'],
                          'displayName':card.get('printed_name') or ' // '.join(f.get('printed_name',f['name']) for f in card.get('card_faces',[])) or card['name'],
                          'counterpartPrintingIds':[p['id'] for p in peers],
                          'verifiedSharedOracleId':bool(peers),
                          'faces':[{'oracleName':f['name'],'printedName':f.get('printed_name',f['name'])} for f in card.get('card_faces',[])]})
    for dataset in ['cards','printings']:
        doc=json.loads((folder/(dataset+'.json')).read_text(encoding='utf-8'))
        changed=0
        for card in doc['cards']:
            source=by_id.get(card['id'])
            if not source:continue
            apply_printed_identity(card,source)
            for face,raw_face in zip(card.get('faces',[]),source.get('card_faces',[])):
                assert face['name']==raw_face.get('printed_name',raw_face['name'])
                assert face['oracleName']==raw_face['name']
            changed+=bool(source.get('card_faces'))
        write_json(folder/(dataset+'.json'),doc)
        print(dataset,'digital DFC checked',changed)
    write_json(research/'digital-identity-crosswalk.json',{'date':'2026-10-28','method':'Printing ID lega la stampa digitale al raw Scryfall; oracle_id condiviso lega le controparti OM1/SPM. I titoli della review SPM sono abbinati ai nomi Oracle conservati, non ai nomi digitali visualizzati. Nessun voto trasferito per somiglianza testuale fra nomi diversi.','sourceSnapshots':['om1-cards.json','../marvel-spider-man-20261028/spm-cards.json'],'rows':crosswalk,'sharedOracleIdsVerified':sum(row['verifiedSharedOracleId'] for row in crosswalk)})
    ratings=json.loads((folder/'ratings.json').read_text(encoding='utf-8'))
    ratings['method']='Per OM1, identità digitale e controparte SPM sono collegate dallo stesso oracle_id Scryfall, verificato nello snapshot digital-identity-crosswalk.json. I titoli della recensione sono abbinati esattamente a oracleName o ai nomi Oracle delle facce. I voti originali 0-10 sono divisi per due; nessuna stima per carte prive di voto.'
    ratings['identityCrosswalk']='research/through-the-omenpaths-20261028/digital-identity-crosswalk.json'
    write_json(folder/'ratings.json',ratings)
    sources=json.loads((folder/'sources.json').read_text(encoding='utf-8'))
    for source in sources['research']['sources']:
        if source['id']=='limited-review':source['identityMapping']='Controparti OM1/SPM verificate tramite oracle_id condiviso; nomi Oracle e nomi digitali preservati separatamente. Crosswalk datato conservato in ricerca.'
    write_json(folder/'sources.json',sources)
    print('Oracle crosswalk',sum(row['verifiedSharedOracleId'] for row in crosswalk),'/',len(crosswalk))

if __name__=='__main__':main()
