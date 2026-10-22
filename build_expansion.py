"""Shared offline feature renderer. Expansion-specific inputs are JSON documents."""
import html
import json
import re
import shutil
from pathlib import Path
from expansion_data import ROOT, FEATURES, confined
from site_navigation import shell


def js(value):
    return json.dumps(value, ensure_ascii=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')


def event_summary(expansion, key):
    event=expansion.data['limited']['events'][key]
    product=expansion.data['products']['products'][event['product']]
    directions=', '.join('sinistra' if d==1 else 'destra' for d in event['directions'])
    pick='una carta' if event['picksPerTurn']==1 else str(event['picksPerTurn'])+' carte'
    tokens='I token sono inclusi.' if product.get('tokensIncluded') else 'I token sono esclusi.'
    return f"{event['seats']} posti · {event['packsPerPlayer']} {product['name']} a testa · {product['packSize']} carte per busta · passaggio {directions}. Scegli {pick} a ogni passaggio. {tokens}"


def render_tokens(content, expansion):
    m = expansion.manifest
    fragments = expansion.data['guides'].get('fragments',{})
    pages = m['presentation']['pages']
    def replace(match):
        kind, _, key = match[1].partition(':')
        if kind == 'name': return html.escape(m['name'])
        if kind == 'setTitle':return fragments.get('set.title') or html.escape(m['name'])
        if kind == 'sourceGroup':
            items=expansion.data['sources'].get('groups',{}).get(key,[])
            if not items:return ''
            return '<p class="small">Fonti: '+' · '.join('<a href="'+html.escape(item['url'],quote=True)+'" target="_blank" rel="noopener">'+html.escape(item['label'])+'</a>' for item in items)+'.</p>'
        if kind == 'description':return html.escape(m['description'],quote=True)
        if kind == 'catalogStatus':return 'Catalogo completo' if expansion.data['cards'].get('complete') else 'Catalogo parziale'
        if kind == 'searchExample':return html.escape(expansion.data['ui'].get('searchExample','Nome, tipo o testo'),quote=True)
        if kind == 'analysisDate':return html.escape(expansion.data['statistics'].get('catalogDate') or expansion.data['cards'].get('date',''))
        if kind == 'ratingsDate':return html.escape(expansion.data['ratings'].get('date') or 'data non specificata')
        if kind == 'poolImportExample':return html.escape(expansion.data['ui'].get('poolImportExample','2 Nome carta\n1 Altra carta'),quote=True)
        if kind == 'sentimentLabel':return html.escape(expansion.data['ui'].get('sentimentLabels',{}).get(key,{'regional':'Ricontrollo internazionale','updated':'Ricontrollo esteso'}[key]))
        if kind == 'presetLabel':return html.escape(expansion.data['ui'].get('analysisPresetLabels',{}).get(key,'Esplora il tema'))
        if kind == 'analysisSetOptions':
            codes=[m['code']]+sorted({c['set'] for c in expansion.cards}-{m['code']})
            labels=expansion.data['ui'].get('setLabels',{})
            return '<option value="all">Tutto il catalogo</option>'+''.join('<option value="'+html.escape(code,quote=True)+'"'+(' selected' if code==m['code'] else '')+'>'+html.escape(labels.get(code,code))+'</option>' for code in codes)
        if kind == 'id': return m['id']
        if kind == 'draftSeed': return html.escape(expansion.data['ui'].get('draftSeed',m['id']+'-tavolo-1'),quote=True)
        if kind == 'draftDate': return html.escape(expansion.data['statistics'].get('draft',{}).get('date') or 'statistiche non ancora disponibili')
        if kind == 'pickDecisionCount':return str(sum(len(group['cases']) for group in expansion.data['guides'].get('pickDecisions',[])))
        if kind == 'packageCount':return str(len(expansion.data['guides'].get('draftCombos',{}).get('packages',[])))
        if kind == 'mainCardCount':return str(sum(c['set']==m['code'] for c in expansion.cards))
        if kind == 'bonusCardCount':return str(sum(c['set']!=m['code'] for c in expansion.cards))
        if kind == 'discoveryCount':return str(len(expansion.data['discovery'].get('cards',[])))
        if kind == 'discoveryFormatCount':return str(len({f for c in expansion.data['discovery'].get('cards',[]) for f in c.get('formats',[])}))
        if kind == 'eventValue':return html.escape(str(expansion.data['limited']['events'].get(key.split('.')[0],{}).get(key.split('.')[1],'N/D')))
        if kind == 'discoveryOptions':
            codes=sorted({c['product'] for c in expansion.data['discovery'].get('cards',[])})
            return '<option value="">Tutti i prodotti</option>'+''.join('<option value="'+html.escape(code,quote=True)+'">Solo '+html.escape(code)+'</option>' for code in codes)
        if kind == 'download':
            item=expansion.data['sources'].get('downloads',{}).get(key)
            if not item:return ''
            return '<a href="'+html.escape(item['url'],quote=True)+'" download>'+html.escape(item['label'])+'</a>'
        if kind == 'reportNav':
            if not expansion.availability['draftStatistics']['available']:return ''
            labels=expansion.data['ui'].get('reportLabels',{})
            return ''.join('<a href="#report-'+str(i)+'">'+html.escape(labels.get(str(i),'Sezione '+str(i+1)))+'</a>' for i in range(8) if 'draft.report-'+str(i) in fragments)
        if kind == 'cardCount': return str(len(expansion.cards))
        if kind == 'printingCount': return str(expansion.data['cards'].get('print_count',len(expansion.data['printings']['cards'])))
        if kind == 'code': return html.escape(m['code'])
        if kind in ('setCodes','setOptions'):
            codes=[m['code']]+sorted({c['set'] for c in expansion.cards}-{m['code']})
            if kind=='setCodes':return html.escape(' + '.join(codes))
            return '<option value="">'+html.escape(' e '.join(codes))+'</option>'+''.join('<option>'+html.escape(code)+'</option>' for code in codes)
        if kind == 'source':
            value=expansion.data['sources'].get('links',{}).get(key)
            if not value:raise ValueError(m['id']+': fonte mancante in sources.links: '+key)
            return html.escape(value,quote=True)
        if kind == 'eventSummary':
            if key=='defaultDraft':key=next(id_ for id_,event in expansion.data['limited']['events'].items() if event['kind']=='draft' and expansion.draft_event_availability(id_)['available'])
            return html.escape(event_summary(expansion,key))
        if kind == 'sealedSummary':
            event=expansion.data['limited']['events']['sealed']
            product=expansion.product_for('sealed')
            return html.escape(f"{event['packsPerPlayer']} {product['name']} · {event['packsPerPlayer']*product['packSize']} carte · mazzo da almeno {event['minDeckSize']}")
        if kind in ('sealedRules','sealedProductNote'):
            event=expansion.data['limited']['events']['sealed']
            if kind=='sealedProductNote':return html.escape('Simulazione del prodotto '+expansion.product_for('sealed')['name']+'. Non è una simulazione di partita o delle procedure di torneo.')
            words={1:'una',2:'due',3:'tre',4:'quattro',5:'cinque',6:'sei'}
            text=f"Apri {words.get(event['packsPerPlayer'],event['packsPerPlayer'])} buste e costruisci un mazzo di almeno {event['minDeckSize']} carte. "
            text+=('Puoi aggiungere liberamente Pianure, Isole, Paludi, Montagne e Foreste. ' if event.get('extraBasicLands') else 'Non aggiungere terre base oltre a quelle del pool. ')
            text+='Le altre carte del pool costituiscono la sideboard; '
            text+=('puoi usare più di quattro copie di una carta se le hai aperte.' if event.get('maxCopies') is None else f"le carte non base hanno un limite di {event['maxCopies']} copie per nome.")
            return html.escape(text)
        if kind == 'publishedTables':
            product=expansion.data['products']['products'][key]
            labels={'wildcard':'Wildcard','rare_or_mythic':'Rara o mitica','foil':'Foil tradizionale','land':'Terra'}
            rows=[]
            for slot,values in product.get('published',{}).get('published_percentages',{}).items():
                cells=''.join('<tr><td>'+html.escape(group)+'</td><td>'+('&lt;1' if rate is None else str(rate).replace('.',','))+'%</td></tr>' for group,rate in values.items())
                rows.append('<details><summary>'+html.escape(labels.get(slot,slot))+'</summary><div class="trk-table-wrap"><table><thead><tr><th>Gruppo</th><th>Frequenza pubblicata</th></tr></thead><tbody>'+cells+'</tbody></table></div></details>')
            return ''.join(rows)
        if kind == 'route': return html.escape(pages.get(key, {'url':key+'.html'})['url'],quote=True)
        if kind in ('fragment','optionalFragment'):
            value = fragments.get(key)
            if key=='gallery.strategy' and not expansion.availability['sealedGuide']['available']:
                return '<section id="strategy"><h2>Guida Sealed</h2>'+availability_notice(expansion,'strategy')+'</section>'
            if key=='gallery.method' and not value:
                return '<section id="method"><h2>Fonti e metodo</h2><p>Le fonti disponibili sono riportate nelle schede delle carte e nei documenti dell’espansione.</p>{{sourceGroup:gallery}}</section>'
            if value is None and (kind=='optionalFragment' or key.startswith('draft.report-')):return ''
            if key.startswith('draft.report-') and not expansion.availability['draftStatistics']['available']:
                return ''
            if value is None:raise ValueError(m['id']+': frammento mancante in guides.fragments: '+key)
            return value
        if kind == 'draftStatistics':
            section_id='draft-drilldown' if key=='drilldown' else 'card-statistics'
            feature='draftDrilldown' if key=='drilldown' else 'draftStatistics'
            if not expansion.availability[feature]['available']:
                return '<section id="'+section_id+'" class="report-section"><h2>'+('Confronto statistico Draft' if key=='drilldown' else 'Statistiche delle carte')+'</h2><p>Non disponibile: mancano statistiche Draft con campioni, data e contesto.</p></section>'
            return (ROOT/'templates/atlas'/('draft-'+key+'-statistics.html')).read_text(encoding='utf-8')
        if kind == 'guide':
            from render_guides import render
            return render(expansion,key)
        raise ValueError('Segnaposto sconosciuto: '+match[1])
    for _ in range(10):
        if not re.search(r'\{\{([^{}]+)\}\}',content): return content
        content = re.sub(r'\{\{([^{}]+)\}\}',replace,content)
    raise ValueError('Riferimenti circolari nei contenuti')


def catalog_data(expansion):
    d = expansion.data
    cards=expansion.cards
    covered=[c['sentiment'] for c in cards if c.get('sentiment')]
    meta={**(d['sentiment'].get('meta') or {}),'covered':len(covered),
          'userCards':sum(s.get('kind')=='utenti' for s in covered),
          'reviewCards':sum(s.get('kind')=='recensione' for s in covered),
          'mixedCards':sum(s.get('kind')=='misto' for s in covered)}
    return {'date':d['cards'].get('date',''),'cards':cards,
            'stats':d['statistics'].get('catalog',[]),'scale':d['ratings'].get('scale',{}),
            'combos':d['combos'],'sentimentMeta':meta}


def configured_routes(content, expansion):
    """Rebase exact historical URL literals, never substrings of configured filenames."""
    pages=expansion.manifest['presentation']['pages']
    legacy={'index.html':'set','catalogo.html':'gallery','draft.html':'draft','sealed.html':'pool',
            'simulatore.html':'simulator','sinergie.html':'combos','analisi.html':'analysis',
            'discovery.html':'discovery','regole.html':'rules','fonti.html':'method',
            'Reality-Fracture-Sealed.html':'gallery','Reality-Fracture-Draft.html':'draft',
            'Reality-Fracture-Draft-Engine.html':'draft-engine','Reality-Fracture-Simulatore.html':'simulator',
            'Reality-Fracture-Combo.html':'combos','Reality-Fracture-Analisi.html':'analysis',
            'Reality-Fracture-Discovery.html':'discovery',
            'Reality-Fracture-Sealed.html#pool':'pool','Reality-Fracture-Sealed.html#strategy':'strategy',
            'Reality-Fracture-Sealed.html#method':'method'}
    targets={url:pages[key]['url'] for url,key in legacy.items() if key in pages}
    if not targets:return content
    pattern=re.compile(r'([\'\"])('+ '|'.join(re.escape(url) for url in sorted(targets,key=len,reverse=True))+r')(?=[?#\'\"])')
    return pattern.sub(lambda match:match[1]+targets[match[2]],content)


def availability_notice(expansion, page):
    pages=expansion.manifest['presentation']['pages']
    host=pages.get(page,{}).get('url','').split('#')[0]
    def belongs(key,value):
        target=pages.get(value['page'],{})
        if value['page']=='rules' and not target:target=pages.get('method',{})
        return value['page']==page or page=='method' or (target.get('url','').split('#')[0]==host and bool(host)) or (page=='draft' and value['page']=='draft-engine') or (key=='sentiment' and page=='gallery')
    missing = [value for key,value in expansion.availability.items()
               if not value['available'] and belongs(key,value)]
    if not missing: return ''
    rows = ''.join('<li>'+html.escape(v['label'])+': non disponibile. Manca: '+html.escape(' '.join(v['missing']))+'</li>' for v in missing)
    return '<aside class="notice feature-availability" aria-label="Funzionalità non disponibili"><ul>'+rows+'</ul></aside>'


def data_for_page(expansion, key):
    if key == 'draft':
        source=expansion.data['statistics'].get('draft') or {}
        cards=[]
        for card in expansion.cards:
            cards.append({'name':card.get('full',card['name']),'cost':card['cost'],'mv':card['mv'],
                          'type':card['type'],'color':''.join(card['colors']),'oracle':card['oracle'],
                          'faces':card.get('faces',[]),'power':card.get('power'),'toughness':card.get('toughness'),
                          'image':card['image'],'url':card['url'],'set':card['set'],'number':card['number'],
                          'basic':card['basic'],'gih':None,'n':0,'alsa':None,'rarity':card['rarity']})
        result={'cards':cards,'poolCards':cards,'pairs':[],'baseline':None,'date':expansion.data['cards'].get('date',''),**source}
        result['cards']=source.get('cards') or cards
        result['poolCards']=source.get('poolCards') or cards
        result['drill']={'guides':expansion.data['archetypes'],'contexts':{},'fields':[],'colors':{},'retrieved':'',**(source.get('drill') or {})}
        return result
    if key == 'discovery': return expansion.data['discovery']
    if key == 'draft-engine':
        from expansion_data import load_expansions
        states={key:expansion.draft_event_availability(key) for key,event in expansion.data['limited']['events'].items() if event['kind']=='draft'}
        ready=[key for key,value in states.items() if value['available']]
        default='draft' if 'draft' in ready else ready[0]
        data=expansion.draft_format(default)
        data['defaultEvent']=default
        data['formats']={key:expansion.draft_format(key) for key in ready}
        words={1:'un',2:'due',3:'tre',4:'quattro',5:'cinque',6:'sei',7:'sette'}
        for key,profile in data['formats'].items():
            profile['summary']=event_summary(expansion,key)
            profile['intro']='Una sedia per te, '+str(words.get(profile['seats']-1,profile['seats']-1))+' avversari con un piano. Scegli come draftano e impara a leggere quello che ti lasciano.'
        data['unavailableFormats']=[{'name':expansion.data['limited']['events'][key]['name'],'missing':value['missing']} for key,value in states.items() if not value['available']]
        data['unavailableFormats'] += [{'name':other.manifest['name'],'missing':other.availability['draftTable']['missing']} for other in load_expansions() if other.manifest['id']!=expansion.manifest['id'] and not other.availability['draftTable']['available']]
        return data
    data = catalog_data(expansion)
    if key == 'simulator' and expansion.availability['sealedSimulator']['available']:
        data['format']=expansion.draft_format('sealed')
    return data


def render_page(expansion, key, page):
    content = confined(ROOT,page['template']).read_text(encoding='utf-8')
    content = render_tokens(content,expansion)
    data = {} if '/preview/' in page['template'] else data_for_page(expansion,key)
    for marker in ('__DATA__','__DRAFT_DATA__','__DISCOVERY_DATA__','__DRAFT_ENGINE__'):
        content = content.replace(marker,js(data))
    runtime = '<script>const EXPANSION_CONFIG='+js(expansion.runtime())+';</script>'
    if key in ('draft-engine','simulator'):
        runtime += '<script src="collation.js"></script>'
    content = content.replace('</head>',runtime+'</head>',1)
    if key=='simulator' and expansion.manifest['presentation']['style']=='atlas':
        content = content.replace('<script src="simulator.js">','<script src="draft-engine.js"></script><script src="simulator.js">')
    # Historical presentation adapters remain, but all identity and navigation are configured.
    presentation={**expansion.manifest['presentation'],'style':'atlas' if '/atlas/' in page['template'] else 'preview'}
    content = shell(content,key,expansion={**expansion.manifest,'presentation':presentation,'sentimentAvailable':expansion.availability['sentiment']['available'],'storageNote':expansion.data['ui'].get('storageNote','Pool e carte osservate si salvano in questo browser.')})
    content = configured_routes(content,expansion)
    notice = availability_notice(expansion,key)
    if notice:
        content = re.sub(r'(<main\b[^>]*>)',lambda m:m[0]+notice,content,count=1)
    if re.search(r'__(?:DATA|DRAFT_DATA|DISCOVERY_DATA|DRAFT_ENGINE)__|\{\{(?:fragment|route):',content):
        raise ValueError(f'{expansion.manifest["id"]}/{key}: segnaposti non risolti')
    return content


def unavailable_page(expansion,key,label,feature):
    return shell('<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(expansion.manifest['name']+' · '+label)+'</title></head><body><main><h1>'+html.escape(label)+'</h1>'+availability_notice(expansion,key)+'</main></body></html>',key,expansion={**expansion.manifest,'minimal':True})


def build(expansion, dest):
    dest.mkdir(parents=True,exist_ok=True)
    pages = expansion.manifest['presentation']['pages']
    # Every expansion exposes the same feature contract, including unavailable tools.
    if 'draft-engine' not in pages:
        pages['draft-engine']={'label':'Tavolo Draft con bot','url':'draft-engine.html','template':'templates/atlas/draft-engine.html'}
    page_requirement = {'draft-engine':'draftTable','simulator':'sealedSimulator',
                        'gallery':'catalog','analysis':'analysis','combos':'combos','discovery':'discovery'}
    written = set()
    for key,page in pages.items():
        if 'template' not in page: continue
        feature = page_requirement.get(key) if '/atlas/' in page['template'] else None
        if feature and not expansion.availability[feature]['available']:
            content = unavailable_page(expansion,key,page['label'],feature)
        else:
            content = render_page(expansion,key,page)
        filename = page['url'].split('#')[0]
        if filename in written: raise ValueError('Due pagine scrivono lo stesso URL: '+filename)
        (dest/filename).write_text(content,encoding='utf-8');written.add(filename)
    # Runtime preview data keeps its existing DOM contract; the document is the same catalog.
    preview = {**expansion.data['cards'],'cards':expansion.cards}
    (dest/'expansion-data.js').write_text('const DATA='+js(preview)+';\n',encoding='utf-8')
    for pattern in ('*.css','*.js'):
        for path in ROOT.glob(pattern):
            shutil.copy2(path,dest/path.name)
    # Publish only explicitly selected public documents and assets.
    public = dest/'data';public.mkdir()
    (public/'expansion.json').write_text(js({**expansion.manifest,'$schema':'../../../schemas/expansion.schema.json'}),encoding='utf-8')
    (public/'runtime.json').write_text(js(expansion.runtime()),encoding='utf-8')
    for key,path in expansion.manifest['datasets'].items():
        value=expansion.data.get(key)
        if isinstance(value,dict) and '$schema' in value:
            (public/(key+'.json')).write_text(js({**value,'$schema':'../../../schemas/'+key+'.schema.json'}),encoding='utf-8')
        elif key in ('cards','printings'):(public/(key+'.json')).write_text(js({'$schema':'../../../schemas/'+key+'.schema.json',**value}),encoding='utf-8')
        else:shutil.copy2(confined(expansion.directory,path),public/(key+'.json'))
    (public/'availability.json').write_text(js(expansion.availability),encoding='utf-8')
    for name in expansion.manifest.get('assets',[]):
        source = confined(ROOT,name)
        if source.is_dir(): shutil.copytree(source,dest/source.name)
        else: shutil.copy2(source,dest/source.name)
    return written
