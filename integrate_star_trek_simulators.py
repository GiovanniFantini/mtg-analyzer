"""Offline integration of sourced printing, bot-rating and booster-model facts."""
import argparse,copy,csv,hashlib,io,json,re,unicodedata
from pathlib import Path
from import_expansion_catalogs import normalize_printing
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def key(s):return ''.join(c for c in unicodedata.normalize('NFKD',s).casefold() if c.isalnum())

def integrate(folder,research):
    docs={n:read(folder/(n+'.json')) for n in ['cards','ratings','products','sources','guides','expansion']}
    cards=docs['cards']['cards'];by_id={c['id']:c for c in cards};by_name={key(c['name']):c for c in cards}
    raw=read(research/'printings-source.json')['data']
    ratings=read(research/'bot-ratings.json');model=read(research/'booster-model.json')
    assert len(ratings['cards'])==len(cards)==341
    assert {r['catalogId'] for r in ratings['cards']}==set(by_id)
    for row in ratings['cards']:
        assert row['name']==by_id[row['catalogId']]['name']
        assert row['value']==-1 if by_id[row['catalogId']]['basic'] else 0<=row['value']<=5
    printings=[]
    for r in raw:
        c=by_id.get(r.get('oracle_id'))
        if not c:raise ValueError('Unmapped printing '+r['name'])
        p=normalize_printing(r);p['catalogId']=c['id']
        # Keep the catalog's verified Oracle correction and functional aliases.
        p.update(name=c['name'],full=c.get('full',c['name']),text=c['text'],oracle=c['text'])
        printings.append(p)
    groups={};source_groups=model['groups']
    for name,definition in source_groups.items():
        result=[]
        for r in raw:
            if r['set'].upper()!=definition['set']:continue
            number=r['collector_number']
            if not number.isdigit() or not definition['min']<=int(number)<=definition['max']:continue
            if definition.get('rarity') and r['rarity']!=definition['rarity']:continue
            dual='Land' in r['type_line'] and r['rarity']=='common' and len(r.get('color_identity',[]))==2
            if name=='main-common' and dual:continue
            if name=='duals' and not dual:continue
            result.append(r['id'])
        if len(result)!=definition['count']:raise ValueError((name,len(result),definition['count']))
        groups[name]=result
    recipe=copy.deepcopy(model['recipe'])
    active={id_ for rule in recipe for b in rule['branches'] for id_ in groups[b['group']]}
    printed={p['id']:p for p in printings}
    assert all(p in printed for p in active)
    for row in ratings['cards']:
        c=by_id[row['catalogId']];r=docs['ratings']['cards'][c['id']]
        if not c['basic']:
            r.update(score=row['value'],role=c['prospects']['limitedAnalysis']['usage']['role'],engineSource='draftsim-bot-20261109',engineScaleMax=5,engineRetrieved='2026-11-09')
    source='https://github.com/Senryoku/Draftmancer/blob/'+model['sourceCommit']+'/src/BoosterFactory.ts'
    assumptions=model['limitations']
    collation=dict(schemaVersion=1,verified='2026-11-09',verificationScope='Implementation checked against the documented Draftmancer simulation model, not measured physical print sheets.',source=source,model='draftmancer-trk-20261109',groups=groups,expectedGroupCounts={k:len(v) for k,v in groups.items()},recipe=recipe)
    product=docs['products']['products']['play']
    product.update(name='Play Booster · modello di simulazione',collation=collation,assumptions=assumptions,missing=[])
    product['modelNotice']='Simulazione di allenamento basata sui pesi del modello pubblico Draftmancer, con gestione dei duplicati semplificata. Le frequenze non specificate esattamente da Wizards sono stime del modello; non riproduce i fogli di stampa o le correlazioni fra buste. Non usare queste aperture per stimare rendimenti economici.'
    docs['sources']['collationIntegration']={'date':'2026-11-09','source':source,'model':collation['model'],'physicalExactnessClaimed':False,'ratingsSource':ratings['url'],'activePrintings':len(active),'printingSnapshot':research.relative_to(ROOT).as_posix()+'/printings-source.json','limitations':assumptions}
    docs['ratings']['engineMethod']='Voti originali 0–5 della tabella usata dai bot Draftsim, acquisita il 9 novembre 2026. Nessuna media con J2SJosh o Andrew Quinn, nessuna WR e nessuna conversione da tier editoriali. Terre base senza voto di potenza.'
    docs['ratings']['engineDate']='2026-11-09'
    registry=docs['sources']['research']['sources']
    new=[dict(id='draftsim-bot-20261109',publisher='Draftsim',url=ratings['url'],retrieved='2026-11-09',context='Voti della propria simulazione Draft, scala originale 0–5; distinti dalla recensione Andrew Quinn.'),dict(id='draftmancer-collation-20261109',publisher='Draftmancer',url=source,retrieved='2026-11-09',context='Modello pubblico di simulazione, con stime esplicite delle frequenze non pubblicate esattamente; licenza MIT.')]
    docs['sources']['research']['sources']=[s for s in registry if s['id'] not in {r['id'] for r in new}]+new
    f=docs['guides']['fragments']
    f['draft-engine.productDescription']='<p>'+product['modelNotice']+'</p>'
    f['draft-engine.copy-1']='Tre buste da 14 carte per otto giocatori, oppure Pick-Two per quattro. I bot usano voti Draftsim attribuiti e le politiche condivise del sito.'
    f['draft-engine.copy-2']='Le stime del modello rimangono distinte dalle percentuali ufficiali pubblicate. Le WR early access restano escluse.'
    f['simulator.copy-2']=product['modelNotice']
    f['simulator.copy-0']='Star Trek · Sealed da sei Play Booster'
    f['set.hero']=f['set.hero'].replace('Anteprima del set','Set in prerelease').replace('{{cardCount}} carte distinte, {{printingCount}} stampe disponibili. Il catalogo è parziale.','{{cardCount}} carte distinte TRK e Stardates, {{printingCount}} stampe censite. Draft e Sealed disponibili per allenarsi.')
    f['analysis.panel-0']=f['analysis.panel-0'].replace('ma mancano copertura completa delle stampe e finiture, catalogo completo e collazione eseguibile verificata.','ma mancano prezzi completi per stampa e finitura e una collazione fisica con frequenze esatte verificate.').replace('L’apertura simulata delle buste resta sospesa.','L’apertura simulata è disponibile con un modello di allenamento derivato da Draftmancer, con frequenze stimate e limiti dichiarati; non certifica il valore economico del box.')
    # The product is playable at prerelease; the retail release remains November 13.
    docs['expansion']['status']='prerelease'
    docs['expansion']['releasePhase']={'prerelease':'2026-11-06','arena':'2026-11-10','tabletop':'2026-11-13','source':'https://magic.wizards.com/en/news/feature/collecting-star-trek'}
    for name,d in docs.items():save(folder/(name+'.json'),d)
    save(folder/'printings.json',{'$schema':'../../schemas/printings.schema.json','date':'2026-11-09','cards':printings})
    return dict(identities=len(cards),printings=len(printings),activePrintings=len(active),nonbasicEngineRatings=sum(not c['basic'] for c in cards),model=collation['model'],physicalExactnessClaimed=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--expansion',type=Path,default=ROOT/'expansions/star-trek');p.add_argument('--research',type=Path,default=ROOT/'research/star-trek-integration-20261109');args=p.parse_args()
    print(json.dumps(integrate(args.expansion,args.research),ensure_ascii=False))
