"""Build isolated review scenarios and test them in a temporary local website."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from expansion_data import ROOT, Expansion, load_expansions
from build_expansion import build


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


with tempfile.TemporaryDirectory(prefix='mtg-review-') as temporary:
    directory=Path(temporary)
    if os.environ.get('MTG_REVIEW_FIXTURE_DIR'):
        directory=Path(os.environ['MTG_REVIEW_FIXTURE_DIR'])
        directory.mkdir(parents=True,exist_ok=True)
        if any(directory.iterdir()):raise ValueError('La cartella delle fixture deve essere vuota')
    originals=load_expansions()
    fixtures={}
    def fixture(name,source_index,mutate):
        original=originals[source_index]
        manifest=copy.deepcopy(original.manifest);data=copy.deepcopy(original.data)
        if source_index==1:
            # Explicitly retain historical preview fixtures after the live sets
            # move to Atlas. These scenarios still exercise old saved records.
            pages=manifest['presentation']['pages']
            if 'practice' in pages:pages['simulator']['url']=pages['practice']['url']
            for key in ('set','gallery','draft','pool','simulator','combos','analysis','discovery','rules','method'):
                pages[key]['template']='templates/preview/'+key+'.html'
                pages[key].pop('manualPool',None)
            for key in ('practice','workbench'):pages.pop(key,None)
            manifest['presentation']['style']='preview'
            for _,members in manifest['presentation']['groups']:
                members[:]=[key for key in members if key in pages]
        manifest['id']='review-'+name
        manifest['storage']={k:'review-'+name+'-'+v for k,v in manifest['storage'].items()}
        mutate(manifest,data)
        source=directory/'source'/name;source.mkdir(parents=True)
        for key,path in manifest['datasets'].items():(source/path).write_text(json.dumps(data[key]),encoding='utf-8')
        path=source/'expansion.json';path.write_text(json.dumps(manifest),encoding='utf-8')
        expansion=Expansion(path);build(expansion,directory/'sets'/manifest['id'])
        fixtures[name]={'base':'sets/'+manifest['id']+'/','routes':{k:v['url'] for k,v in expansion.manifest['presentation']['pages'].items()}}
    def renamed(m,d):
        m.update(name='Review Atlas',code='TST')
        for card in d['discovery']['cards']:
            if card['product']=='FRA':card['product']='TST'
        for page in m['presentation']['pages'].values():
            filename,*anchor=page['url'].split('#');page['url']='review-'+filename+('#'+anchor[0] if anchor else '')
        d['limited']['events']['draft'].update(minDeckSize=45,maxCopies=2,extraBasicLands=False)
        d['limited']['events']['sealed'].update(packsPerPlayer=4,minDeckSize=35,maxCopies=1,extraBasicLands=False)
        d['products']['products']['play']['name']='Test Booster'
    fixture('atlas',0,renamed)
    fixture('no-statistics',0,lambda m,d:d.update(statistics={}))
    fixture('no-guide',0,lambda m,d:d['guides'].pop('pickGuide'))
    fixture('no-sentiment',0,lambda m,d:d.update(sentiment={'meta':None,'cards':{}}))
    fixture('no-draft',0,lambda m,d:d['limited']['events'].pop('draft'))
    fixture('empty-discovery',0,lambda m,d:d.update(discovery={'cards':[],'previews':[]}))
    def preview(m,d):
        d['limited']['events']['sealed'].update(maxCopies=1,extraBasicLands=False)
        d['limited']['events']['sealed-extra']={**d['limited']['events']['sealed'],'id':'alternate-sealed','name':'Alternate Sealed'}
        for page in m['presentation']['pages'].values():page['url']='review-'+page['url']
    fixture('preview',1,preview)
    fixture('no-events',1,lambda m,d:d['limited'].update(events={}))
    fixture('no-sealed-guide',0,lambda m,d:d['guides'].pop('sealed'))
    def no_downloads(m,d):
        m['assets']=[p for p in m['assets'] if not p.endswith('.json')]
        d['sources'].pop('downloads',None)
    fixture('no-downloads',0,no_downloads)
    fixture('statistics-only',0,lambda m,d:d['statistics']['draft'].pop('drill'))
    def alternate(m,d):
        d['products']['products']['unready']={'name':'Unready Booster','packSize':14,'collation':None,'missing':['Probabilità non pubblicate.']}
        d['limited']['events']['picktwo']={**d['limited']['events']['draft'],'id':'test-picktwo','name':'Test Pick-Two','product':'unready','picksPerTurn':2,'seats':4}
    fixture('alternate-event',0,alternate)
    def structured(m,d):
        d['guides']['fragments']={k:v for k,v in d['guides']['fragments'].items() if not k.startswith('draft.report-')}
    fixture('structured-guide',0,structured)
    def discovery(m,d):
        for card in d['discovery']['cards'][1:]:card['formats']=[fmt for fmt in card['formats'] if fmt!='Standard']
        d['discovery']['cards'][0].update(formats=['Standard'],level='Verificata')
        d['ui']['discoveryLevels']=['Verificata','Confermata','Emergente','Preliminare']
        d['ui']['bonusCode']='XYZ'
        for c in d['cards']['cards']:
            if c['set']=='SPG':c['set']='XYZ'
        for c in d['printings']['cards']:
            if c['set']=='SPG':c['set']='XYZ'
    fixture('custom-discovery',0,discovery)
    def complete_preview(m,d):
        card=d['cards']['cards'][0]
        d['cards']['complete']=True
        printing={**card,'id':'test-print','full':card.get('full',card['name'])}
        d['printings']['cards']=[printing]
        d['ratings']['cards']={card['id']:{'score':3,'role':'Giocabile'}}
        d['archetypes']={'WU':{'name':'Bianco blu','theme':'Esempio di controllo','plan':'Gioca carte dei tuoi colori.','core':[card['name']],'support':[]}}
        product=d['products']['products'][d['limited']['events']['draft']['product']]
        product.update(packSize=1,collation={'schemaVersion':1,'verified':True,'source':'https://example.test/fixture','groups':{'all':['test-print']},'recipe':[{'id':'test','op':'draw','count':1,'branches':[{'weight':1,'group':'all'}]}]})
    fixture('complete-preview',1,complete_preview)
    def no_guide_templates(m,d):
        d['guides'].pop('templates',None)
    fixture('default-guides',0,no_guide_templates)
    def clean_atlas(m,d):
        d['guides']['fragments']={}
        d['guides'].pop('templates',None)
        d['sources']={'groups':{}}
    fixture('clean-atlas',0,clean_atlas)
    def generic_preview(m,d):
        m.update(name='Generic Preview',code='ABC',status='released')
        d['cards'].update(complete=True,date='Snapshot 2099-01-02',legalityDate='2099-01-02')
        for card in d['cards']['cards']:card.pop('legalitiesRetrieved',None)
        # Keep this historical fallback fixture independent of live tournament
        # research, which would correctly promote discovery to the shared view.
        d['discovery']={'cards':[],'previews':[]}
        d['guides']['fragments']={}
        d['ui'].pop('searchExample',None)
    fixture('generic-preview',1,generic_preview)
    def shared_preview(m,d):
        hero=d['guides'].get('fragments',{}).get('set.hero','')
        d.update(copy.deepcopy(originals[0].data))
        d['guides']['fragments']['set.hero']=hero
        d['guides']['fragments']['gallery.strategy']+='<p>'+d['cards']['cards'][0]['name']+'</p>'
        d['discovery'].pop('previews',None)
        m['code']=originals[0].manifest['code']
    fixture('shared-preview',1,shared_preview)
    for file in ('site.css','site.js'):shutil.copy2(ROOT/file,directory/file)
    (directory/'fixtures.json').write_text(json.dumps(fixtures),encoding='utf-8')
    handler=partial(QuietHandler,directory=str(directory))
    server=ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        env={**os.environ,'MTG_REVIEW_FIXTURE_URL':f'http://127.0.0.1:{server.server_port}/'}
        result=subprocess.run(['node','verify-expansion-review.cjs'],cwd=ROOT,env=env)
    finally:server.shutdown();server.server_close();thread.join()
    raise SystemExit(result.returncode)
