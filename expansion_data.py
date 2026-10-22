"""Versioned expansion documents and capability validation. No network or side effects."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATASETS = ('cards','printings','products','limited','ratings','archetypes','combos',
            'guides','statistics','sentiment','discovery','prices','sources','ui')
OPERATIONS = {'draw', 'replace', 'pair'}
FEATURES = {
    'catalog': ('Catalogo carte', 'gallery', ['cards']),
    'pool': ('Pool e costruzione del mazzo', 'pool', ['cards','limited']),
    'analysis': ('Analisi del set', 'analysis', ['cards']),
    'sealedGuide': ('Guida Sealed', 'strategy', ['guides:sealed']),
    'draftGuide': ('Guida Draft e archetipi', 'draft', ['archetypes','guides:draft']),
    'draftStatistics': ('Statistiche e confronto Draft', 'draft', ['statistics:draft']),
    'draftDrilldown': ('Confronto statistico per contesto', 'draft', ['statistics:drill']),
    'pickGuide': ('Pick subito e counterpick', 'draft', ['guides:pickGuide']),
    'pickBaits': ('Rare e mitiche: bait', 'draft', ['guides:pickBaits']),
    'pickDecisions': ('Situazioni di scelta', 'draft', ['guides:pickDecisions']),
    'draftCombos': ('Sinergie Draft', 'draft', ['guides:draftCombos']),
    'sealedSimulator': ('Apertura delle buste Sealed', 'simulator', ['completeCards','collation:sealed','catalogMapping:sealed','limited:sealed']),
    'draftTable': ('Tavolo Draft con bot', 'draft-engine', ['completeCards','collation','catalogMapping:draft','ratingsComplete','archetypes','limited:draft']),
    'combos': ('Combo e sinergie', 'combos', ['combos']),
    'sentiment': ('Sentiment', 'analysis', ['sentiment']),
    'discovery': ('Metagame documentato', 'discovery', ['discovery']),
    'boxEV': ('Ricavo atteso del box', 'analysis', ['prices','completeCards','collation','statistics:boxEV']),
    'rules': ('Regole del prodotto e del Draft', 'rules', ['limited','sources']),
}
REASONS = {
    'completeCards':'Catalogo completo delle carte ammesse al prodotto.',
    'collation':'Profilo di collazione completo, verificato e supportato dal motore.',
    'collation:sealed':'Profilo di collazione Sealed completo, verificato e supportato dal motore.',
    'catalogMapping:sealed':'Corrispondenza fra stampe della busta Sealed e carte del catalogo.',
    'catalogMapping:draft':'Corrispondenza fra stampe della busta Draft e carte del catalogo.',
    'ratingsComplete':'Valutazioni delle carte non base del prodotto.',
    'cards':'Catalogo delle carte.', 'limited':'Regole degli eventi Limited.',
    'limited:sealed':'Regole dell’evento Sealed.', 'limited:draft':'Regole dell’evento Draft.',
    'archetypes':'Archetipi e carte di supporto.', 'guides:sealed':'Guida Sealed in guides.fragments.gallery.strategy.',
    'guides:draft':'Guida Draft.', 'statistics:draft':'Statistiche Draft con data e contesto.',
    'statistics:drill':'Snapshot dei contesti Draft con campioni e data di rilevazione.',
    'guides:pickGuide':'Priorità dei pick e counterpick.', 'guides:pickBaits':'Valutazioni delle rare e mitiche condizionali.',
    'guides:pickDecisions':'Esempi di scelta fra carte.', 'guides:draftCombos':'Sequenze e sinergie Draft.',
    'combos':'Combo e sequenze documentate.', 'sentiment':'Sintesi qualitative con fonti.',
    'discovery':'Risultati e analisi del metagame.', 'prices':'Prezzi verificati con data e metrica.',
    'statistics:boxEV':'Modello economico e risultati verificati.', 'sources':'Fonti e date di verifica.',
}


def read_json(path):
    def invalid(value):raise ValueError('Numero JSON non valido: '+value)
    return json.loads(path.read_text(encoding='utf-8-sig'),parse_constant=invalid)


def confined(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError(f'Percorso esterno alla cartella: {relative}')
    return path


def normalize_card(source, document):
    if not isinstance(source,dict):raise ValueError(document+': carta non valida')
    card=dict(source)
    if document=='printings.json':card.setdefault('url','')
    identity=str(card.get('id','senza id'))
    def fail(field):raise ValueError(f'{document}/{identity}: campo carta mancante o non valido: {field}')
    for field in ('id','name','set','type','rarity','image','url'):
        if not isinstance(card.get(field),str):fail(field)
    if not card['id'] or not card['name']:fail('id / name')
    if type(card.get('number')) not in (int,str):fail('number')
    for field in ('colors','identity'):
        if not isinstance(card.get(field),list) or any(c not in list('WUBRG') for c in card[field]):fail(field)
    for canonical,alias,types in (('cost','mana',(str,)),('mv','cmc',(int,float)),('oracle','text',(str,))):
        value=card.get(canonical,card.get(alias))
        if type(value) not in types:fail(canonical+' / '+alias)
        card[canonical]=value;card[alias]=value
    card.setdefault('full',card['name']);card.setdefault('large',card['image'])
    card.setdefault('faces',[]);card.setdefault('keywords',[]);card.setdefault('prints',[]);card.setdefault('legalities',{})
    main_type=card['type'].split(' // ')[0]
    for field,default in (('basic',bool(re.search(r'\bBasic\b',main_type) and re.search(r'\bLand\b',main_type))),('land',bool(re.search(r'\bLand\b',main_type))),('creature',bool(re.search(r'\bCreature\b',main_type)))):
        card.setdefault(field,default)
        if type(card[field]) is not bool:fail(field)
    if not isinstance(card['full'],str):fail('full')
    if not isinstance(card['faces'],list) or any(not isinstance(f,dict) or not isinstance(f.get('name'),str) for f in card['faces']):fail('faces')
    card['faces']=[{'mana_cost':'','oracle_text':'','type_line':'','power':'','toughness':'',**face} for face in card['faces']]
    if not isinstance(card['keywords'],list) or any(not isinstance(k,str) for k in card['keywords']):fail('keywords')
    if not isinstance(card['prints'],list) or not isinstance(card['legalities'],dict):fail('prints / legalities')
    if any(not isinstance(p,dict) or not isinstance(p.get('finishes',[]),list) for p in card['prints']):fail('prints.finishes')
    card['prints']=[{'number':'','image':'','finishes':[],**printing} for printing in card['prints']]
    return card


class Expansion:
    def __init__(self, manifest_path):
        self.path = Path(manifest_path)
        self.directory = self.path.parent
        self.manifest = read_json(self.path)
        m = self.manifest
        if m.get('schemaVersion') != 1:
            raise ValueError(f'{self.path}: schemaVersion non supportata')
        if not re.fullmatch(r'[a-z0-9-]+', m.get('id','')):
            raise ValueError('Identificatore espansione non valido')
        for field in ('name','code','date','description','datasets','presentation','storage','features'):
            if not m.get(field): raise ValueError(f'{m["id"]}: manca {field}')
        for field in ('name','code','date','description'):
            if not isinstance(m[field],str):raise ValueError(f'{m["id"]}: {field} deve essere una stringa')
        self.data = {key: read_json(confined(self.directory, m['datasets'][key]))
                     for key in DATASETS if key in m['datasets']}
        missing = set(DATASETS) - self.data.keys()
        if missing: raise ValueError(f'{m["id"]}: documenti mancanti: {sorted(missing)}')
        for key in ('products','limited'):
            if self.data[key].get('schemaVersion')!=1:raise ValueError(f'{m["id"]}: versione {key} non supportata')
        for key in ('cards','printings'):
            if not isinstance(self.data[key].get('cards'),list):raise ValueError(f'{m["id"]}/{key}.json: manca cards')
            self.data[key]['cards']=[normalize_card(card,key+'.json') for card in self.data[key]['cards']]
        if type(self.data['cards'].get('complete',False)) is not bool:raise ValueError(m['id']+'/cards.json: complete deve essere booleano')
        self.data['cards'].setdefault('print_count',len(self.data['printings']['cards']) or sum(max(1,len(card['prints'])) for card in self.data['cards']['cards']))
        self.validate()
        self.availability = self.capabilities()

    @property
    def cards(self):
        ratings = self.data['ratings'].get('cards',{})
        sentiments = self.data['sentiment'].get('cards',{})
        result=[]
        for source in self.data['cards']['cards']:
            card={'score':None,'role':'','why':'','condition':'','evidence':[],'community':None,
                  'forum_note':'','forum_link':'','build':False,**source, **ratings.get(source['id'],{})}
            if source['id'] in sentiments: card['sentiment']=sentiments[source['id']]
            card['keywords']=list(source.get('keywords',[]))
            for alias in self.data['ui'].get('keywordAliases',[]):
                if re.search(alias['pattern'],card['oracle'],re.I) and alias['keyword'] not in card['keywords']:card['keywords'].append(alias['keyword'])
            found=[combo for combo in self.data['combos'] if card['id'] in combo['cards']]
            families={}
            for combo in found:
                q=.65*combo['practical']+.35*combo['power']
                families[combo['family']]=max(q,families.get(combo['family'],0))
            scores=sorted(families.values(),reverse=True)
            score=min(5,scores[0]+min(.5,.2*sum(max(0,x-2) for x in scores[1:4]))) if scores else None
            card.update(combos=[c['id'] for c in found],comboFamilies=len(families),comboScore=int(score*2+.5)/2 if score is not None else None)
            result.append(card)
        return result

    def product_for(self,event_id):
        event=self.data['limited']['events'].get(event_id)
        return self.data['products']['products'].get(event['product'],{}) if event else {}

    def product_printings(self,event_id):
        recipe=self.product_for(event_id).get('collation') or {}
        ids={id_ for rule in recipe.get('recipe',[]) for branch in rule['branches'] for id_ in recipe['groups'][branch['group']]}
        for a,b in recipe.get('partners',[]):
            if a in ids or b in ids:ids.update((a,b))
        return ids

    def printing_catalog(self):
        by_name={c.get('full',c['name']):c for c in self.cards}
        by_id={c['id']:c for c in self.cards}
        return {p['id']:(by_id.get(p['catalogId']) if p.get('catalogId') else by_name.get(p.get('full',p['name']))) for p in self.data['printings']['cards']}

    def validate(self):
        def fail(message): raise ValueError(f'{self.manifest["id"]}: {message}')
        for key in ('set','draft','discovery'):
            if key not in self.manifest['presentation'].get('pages',{}):fail('pagina richiesta dal catalogo espansioni: '+key)
        storage=self.manifest['storage']
        if any(not isinstance(value,str) or not value.strip() for value in storage.values()):fail('le chiavi storage devono essere stringhe non vuote')
        needed=set()
        for key,page in self.manifest['presentation']['pages'].items():
            template=page.get('template','')
            if '/preview/' in template:needed.update(('poolPrefix','mode','watch'))
            if '/atlas/' in template:
                needed.update({'gallery':('sealedPool',),'combos':('sealedPool',),'draft':('draftPool',),
                               'discovery':('watch',),'simulator':('sealedSimulator',),'draft-engine':('draftTable',)}.get(key,()))
        if self.manifest['features'].get('draftTable',{}).get('requested'):needed.add('draftTable')
        if needed-storage.keys():fail('chiavi storage mancanti: '+', '.join(sorted(needed-storage.keys())))
        for feature,setting in self.manifest['features'].items():
            if feature not in FEATURES:fail('funzionalità non supportata: '+feature)
            if type(setting.get('requested')) is not bool:fail('requested deve essere booleano: '+feature)
        ids = [c['id'] for c in self.data['cards']['cards']]
        if len(ids) != len(set(ids)): fail('identità carta duplicate')
        from statistics_data import validate_external_statistics
        validate_external_statistics(self.data['statistics'], self.data['cards']['cards'])
        if not set(self.data['ratings'].get('cards',{})) <= set(ids): fail('valutazione di carta inesistente')
        if not set(self.data['sentiment'].get('cards',{})) <= set(ids): fail('sentiment di carta inesistente')
        names = {c.get('full',c['name']) for c in self.cards} | {c['name'] for c in self.cards}
        for card in self.cards:
            names.update(f['name'] for f in card.get('faces',[]))
        ui=self.data['ui']
        if 'discoveryLevels' in ui and not {c['level'] for c in self.data['discovery'].get('cards',[])}<=set(ui['discoveryLevels']):fail('livello discovery assente da ui.discoveryLevels')
        if any(field not in {'set','color','colorMode','mana','type','rarity','keyword','role','lands','query'} for preset in ui.get('analysisPresets',{}).values() for field in preset):fail('campo non supportato in ui.analysisPresets')
        printing_names={p['name'] for p in self.data['printings']['cards']} | {p.get('full',p['name']) for p in self.data['printings']['cards']}
        examples={name for text in ui.get('botExamples',{}).values() for name in re.findall(r'\[\[([^\]]+)\]\]',text)}
        if not examples<=printing_names:fail('carte sconosciute in ui.botExamples: '+str(sorted(examples-printing_names)))
        referenced=set(ui.get('drilldownCompare',[])) | set(ui.get('cardAliases',{}).values()) | set(ui.get('packageAliases',{}).values())
        referenced.update(item['name'] for item in ui.get('drilldownFindings',[]))
        if not referenced<=names:fail('carte sconosciute in ui: '+str(sorted(referenced-names)))
        if any(item['pair'] not in self.data['archetypes'] for item in ui.get('drilldownFindings',[])):fail('archetipo sconosciuto in ui.drilldownFindings')
        for key, archetype in self.data['archetypes'].items():
            if not set(archetype['core'] + archetype['support']) <= names: fail(f'carte sconosciute in archetipo {key}')
        for combo in self.data['combos']:
            if not set(combo['cards']) <= set(ids): fail('carte sconosciute in combo')
            calculator=combo.get('calculator')
            if calculator and (calculator.get('kind')!='netMana' or type(calculator.get('netPerCycle')) not in (int,float) or any(not isinstance(calculator.get(field),str) for field in ('label','unit','note'))):fail('calcolatore combo non supportato o incompleto')
        for key, event in self.data['limited']['events'].items():
            if event.get('kind') not in ('draft','sealed'): fail(f'tipo evento non supportato: {key}')
            for field in ('packsPerPlayer','minDeckSize','picksPerTurn','seats'):
                if not isinstance(event.get(field),int) or isinstance(event[field],bool) or event[field] < (0 if field == 'picksPerTurn' else 1): fail(f'{key}: {field} non valido')
            if event['product'] not in self.data['products']['products']: fail(f'{key}: prodotto inesistente')
            if event['kind']=='draft' and (event['picksPerTurn']<1 or len(event.get('directions',[])) != event['packsPerPlayer'] or any(d not in [-1,1] for d in event['directions'])): fail(f'{key}: passaggi non validi')
            if event['kind']=='draft' and event['seats']<2:fail(f'{key}: servono almeno due posti')
            mulligan=event.get('mulligan',{})
            if mulligan.get('kind')!='london' or not isinstance(mulligan.get('handSize'),int) or mulligan['handSize']<1 or not isinstance(mulligan.get('freeMulligans'),int) or mulligan['freeMulligans']<0:fail(f'{key}: mulligan non supportato')
            if event.get('maxCopies') is not None and (type(event['maxCopies']) is not int or event['maxCopies']<1):fail(f'{key}: limite copie non valido')
            if not event.get('sources'):fail(f'{key}: fonti delle regole mancanti')
        printing_ids = [c['id'] for c in self.data['printings']['cards']]
        if len(printing_ids)!=len(set(printing_ids)): fail('stampe duplicate')
        for product in self.data['products']['products'].values():
            recipe = product.get('collation')
            if not recipe: continue
            if recipe.get('schemaVersion') != 1: fail('versione collazione non supportata')
            groups = recipe['groups']
            for group,count in recipe.get('expectedGroupCounts',{}).items():
                if len(groups.get(group,[]))!=count:fail(f'numerosità non valida per {group}')
            for group, members in groups.items():
                if not members or not set(members) <= set(printing_ids): fail(f'gruppo {group} vuoto o con stampe sconosciute')
                if len(members)!=len(set(members)):fail(f'stampe duplicate nel gruppo {group}')
            aliases = {}
            minimum_counts={}
            printings={c['id']:c for c in self.data['printings']['cards']}
            for a,b in recipe.get('partners',[]):
                if a==b or a not in printings or b not in printings or printings[a]['rarity']!=printings[b]['rarity']:fail('coppia non valida')
            length = 0
            for rule in recipe['recipe']:
                if rule['id'] in aliases:fail('identificatore slot duplicato')
                if rule['op'] not in OPERATIONS: fail(f'operazione collazione sconosciuta: {rule["op"]}')
                if rule.get('count',1)<1 or not isinstance(rule.get('count',1),int): fail('quantità slot non valida')
                if rule['op']=='replace':
                    if rule.get('target') not in aliases or not 0<=rule.get('chance',-1)<=1: fail('sostituzione slot non valida')
                    if rule['chance']>0:
                        if minimum_counts[rule['target']]<rule.get('count',1):fail('sostituzione senza carte sufficienti: '+rule['id'])
                        minimum_counts[rule['target']]-=rule.get('count',1)
                else: length += rule.get('count',1) * (2 if rule['op']=='pair' else 1)
                for previous in rule.get('exclude',[]):
                    if previous not in aliases: fail('esclusione di slot non ancora estratto')
                if abs(sum(b['weight'] for b in rule['branches'])-1)>1e-8: fail('pesi slot non normalizzati')
                for branch in rule['branches']:
                    if branch['weight']<0 or branch['group'] not in groups: fail('ramo slot non valido')
                    names_in_group={printings[id_]['full'] for id_ in groups[branch['group']]}
                    if rule.get('unique') and branch['weight']>0 and len(names_in_group)<rule.get('count',1):fail('gruppo insufficiente per estrazione unique: '+rule['id'])
                aliases[rule['id']]=rule
                minimum_counts[rule['id']]=(rule.get('count',1) if rule['op']=='replace' and rule['chance']==1 else 0) if rule['op']=='replace' else rule.get('count',1)*(2 if rule['op']=='pair' else 1)
            if length != product['packSize']: fail('ricetta incompatibile con dimensione busta')
            partners = dict(recipe.get('partners',[]))
            partners.update({b:a for a,b in recipe.get('partners',[])})
            for rule in recipe['recipe']:
                if rule['op']=='pair' and any(card not in partners for b in rule['branches'] for card in groups[b['group']]): fail('partner mancante')
            printings={c['id']:c for c in self.data['printings']['cards']}
            if recipe.get('verified') and not recipe.get('source'): fail('collazione verificata senza fonte')
            from collation_validation import validate_samples
            try:validate_samples(recipe,printings,product['packSize'])
            except ValueError as error:fail(str(error))
        for key in ('pickGuide','pickBaits'):
            guide=self.data['guides'].get(key)
            if not guide:continue
            referenced={c['name'] for group in guide['groups'] for c in group['cards']}
            if key=='pickGuide':referenced.update(name for c in guide['counters'] for name in [c['name'],*c['before'],*c['after']])
            if not referenced<=names:fail(f'carte sconosciute in {key}: {sorted(referenced-names)}')
        for group in self.data['guides'].get('pickDecisions',[]):
            for case in group['cases']:
                if not set(case['cards'])<=names:fail('carte sconosciute in una situazione di scelta')
        for package in self.data['guides'].get('draftCombos',{}).get('packages',[]):
            if not set(package['cards'])<=names:fail('carte sconosciute in un pacchetto Draft')
        for key, page in self.manifest['presentation']['pages'].items():
            if Path(page['url'].split('#')[0]).name != page['url'].split('#')[0]: fail(f'URL pagina non valido: {key}')
            if 'template' in page and not confined(ROOT,page['template']).is_file(): fail(f'template mancante: {key}')

    def draft_event_availability(self,event_id):
        event=self.data['limited']['events'].get(event_id)
        product=self.product_for(event_id)
        recipe=product.get('collation') or {}
        ids=self.product_printings(event_id)
        catalog=self.printing_catalog()
        missing=[]
        if not event or event['kind']!='draft':missing.append(REASONS['limited:draft'])
        if not self.data['cards'].get('complete'):missing.append(REASONS['completeCards'])
        if not recipe.get('verified'):missing.extend([REASONS['collation'],*product.get('missing',[])])
        if not ids or any(not catalog.get(id_) for id_ in ids):missing.append(REASONS['catalogMapping:draft'])
        if not ids or any(not catalog.get(id_) or not (catalog[id_].get('basic') or catalog[id_].get('score') is not None) for id_ in ids):missing.append(REASONS['ratingsComplete'])
        if not self.data['archetypes']:missing.append(REASONS['archetypes'])
        return {'available':not missing,'missing':list(dict.fromkeys(missing))}

    def capabilities(self):
        d = self.data
        product = self.product_for('draft')
        recipe = product.get('collation')
        ratings = d['ratings'].get('cards',{})
        catalog=self.printing_catalog()
        active_draft=self.product_printings('draft')
        present = {key: bool(value) for key,value in d.items()}
        present.update(cards=bool(self.cards), completeCards=d['cards'].get('complete',False),
                       collation=bool(recipe and recipe.get('verified')),
                       ratingsComplete=bool(active_draft) and all(catalog.get(id_) and (catalog[id_].get('basic') or catalog[id_].get('score') is not None) for id_ in active_draft),
                       prices=d['prices'].get('available',False),sentiment=bool(d['sentiment'].get('cards')),
                       discovery=bool(d['discovery'].get('cards')),limited=bool(d['limited']['events']))
        sealed=d['limited']['events'].get('sealed')
        sealed_product=d['products']['products'].get(sealed['product'],{}) if sealed else {}
        present['collation:sealed']=bool(sealed_product.get('collation',{}).get('verified')) if sealed_product.get('collation') else False
        for doc in ('limited','statistics','guides'):
            values = d[doc].get('events',{}) if doc=='limited' else d[doc]
            present.update({doc+':'+key:bool(value) for key,value in values.items()})
        stats=d['statistics'].get('draft') or {}
        present['statistics:draft']=bool(stats.get('cards')) and any(c.get('gih') is not None and c.get('n',0)>0 for c in stats.get('cards',[]))
        drill=stats.get('drill') or {}
        present['statistics:drill']=bool(present['statistics:draft'] and drill.get('contexts') and drill.get('retrieved'))
        guides=d['guides']
        present['guides:sealed']=bool(guides.get('sealed') and guides.get('fragments',{}).get('gallery.strategy'))
        present['guides:draft']=bool((guides.get('fragments',{}).get('draft.report-3') and present['statistics:draft']) or any((guides.get(key) or {}).get('groups') for key in ('pickGuide','pickBaits')) or guides.get('pickDecisions') or (guides.get('draftCombos') or {}).get('packages'))
        for key in ('pickGuide','pickBaits'):
            present['guides:'+key]=any(group.get('cards') for group in (guides.get(key) or {}).get('groups',[]))
        present['guides:pickDecisions']=any(group.get('cases') for group in guides.get('pickDecisions',[]))
        present['guides:draftCombos']=bool((guides.get('draftCombos') or {}).get('packages'))
        for event_id in ('draft','sealed'):
            ids=self.product_printings(event_id)
            present['catalogMapping:'+event_id]=bool(ids) and all(catalog.get(id_) for id_ in ids)
        result = {}
        for key,(label,page,requires) in FEATURES.items():
            setting = self.manifest['features'].get(key,self.manifest['features'].get('draftStatistics',{}) if key=='draftDrilldown' else {'requested':False})
            missing = [REASONS.get(item,item) for item in requires if not present.get(item)]
            extras=[]
            for item in requires:
                if present.get(item):continue
                if item in ('collation','collation:sealed'):
                    extras.extend(self.product_for('sealed' if item.endswith(':sealed') else 'draft').get('missing',[]))
                elif item=='prices':extras.extend(d['prices'].get('missing',[]))
                elif item.startswith('catalogMapping:'):
                    ids=self.product_printings(item.split(':')[1])
                    extras.extend('Stampa senza carta del catalogo: '+id_+'.' for id_ in sorted(ids) if not catalog.get(id_))
            missing=list(dict.fromkeys(missing+extras))
            result[key] = {'available': bool(setting.get('requested') and not missing), 'label':label,'page':page,
                           'missing':missing if setting.get('requested') else ['Funzionalità non prevista per questa espansione.']}
        if self.manifest['features'].get('draftTable',{}).get('requested'):
            events=[self.draft_event_availability(key) for key,event in d['limited']['events'].items() if event['kind']=='draft']
            ready=any(event['available'] for event in events)
            result['draftTable'].update(available=ready,missing=[] if ready else list(dict.fromkeys(reason for event in events for reason in event['missing'])) or [REASONS['limited:draft']])
        return result

    def draft_format(self, event_id='draft'):
        event = self.data['limited']['events'][event_id]
        product = self.data['products']['products'][event['product']]
        archetypes = self.data['archetypes']
        catalog = self.printing_catalog()
        cards=[]
        for printing in self.data['printings']['cards']:
            card = {**printing}
            review = catalog.get(card['id']) or {}
            card.update(score=review.get('score'),role=review.get('role',''))
            card['catalogId'] = review.get('id')
            card['archetypes'] = [k for k,a in archetypes.items() if card['name'] in a['core']+a['support']]
            cards.append(card)
        active=self.product_printings(event_id)
        engine_fields=('id','full','colors','identity','cost','mv','rarity','basic','land','creature','score','role','oracle','archetypes')
        spec=product.get('collation') or {}
        engine={'engineVersion':2,'event':{key:event.get(key) for key in ('id','seats','packsPerPlayer','picksPerTurn','directions')},
                'packSize':product['packSize'],
                'collation':{key:spec.get(key) for key in ('schemaVersion','groups','partners','recipe')},
                'cards':[{key:card.get(key) for key in engine_fields} for card in cards if card['id'] in active],
                'archetypeOrder':list(archetypes)}
        revision = hashlib.sha256(json.dumps(engine,sort_keys=True,ensure_ascii=True).encode()).hexdigest()
        compatibility=self.manifest.get('draftReplayCompatibility',{}).get(event_id,{})
        previous=compatibility.get('previousRevisions',[]) if compatibility.get('revision')==revision else []
        return {'version':1,'id':event['id'],'set':self.manifest['code'],'name':event['name'],
                'seats':event['seats'],'rounds':event['packsPerPlayer'],'packSize':product['packSize'],'productName':product['name'],
                'picksPerTurn':event['picksPerTurn'],'directions':event.get('directions',[]),
                'assumptions':product.get('assumptions',[]),'cards':cards,'archetypes':archetypes,
                'collation':product.get('collation'),'revision':revision,
                'compatibleRevisions':previous,
                'legacyReplay':event.get('legacyReplay',False) and self.manifest.get('legacyDraftRevision') in previous, 'ui':self.data['ui']}

    def runtime(self):
        return {'schemaVersion':1,'id':self.manifest['id'],'name':self.manifest['name'],'code':self.manifest['code'],
                'storage':self.manifest['storage'],'events':self.data['limited']['events'],
                'routes':{key:p['url'] for key,p in self.manifest['presentation']['pages'].items()},
                'availability':self.availability,'ui':self.data['ui']}


def load_expansions():
    expansions = [Expansion(confined(ROOT,entry['manifest'])) for entry in read_json(ROOT/'expansions.json')]
    if len({e.manifest['id'] for e in expansions}) != len(expansions): raise ValueError('Espansioni duplicate')
    storage={}
    for expansion in expansions:
        spec=expansion.manifest['storage']
        keys=[v for k,v in spec.items() if k!='poolPrefix']
        if 'poolPrefix' in spec:
            keys.extend(spec['poolPrefix']+mode+'-v1' for mode in expansion.data['limited']['events'])
        if 'draftTable' in spec:
            keys.extend(spec['draftTable']+'-'+mode for mode,event in expansion.data['limited']['events'].items() if event['kind']=='draft' and mode!='draft')
        for key in keys:
            if key in storage and storage[key]!=expansion.manifest['id']:raise ValueError(f'Chiave di salvataggio condivisa da espansioni diverse: {key}')
            storage[key]=expansion.manifest['id']
    return expansions
