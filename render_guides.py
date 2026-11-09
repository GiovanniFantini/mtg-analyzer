"""Shared renderers for structured editorial data; no set names or card lists."""
import html
import re
from expansion_data import ROOT, confined


def inline(text):
    text=html.escape(text.replace('\u2014',':'))
    text=re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)',r'<a href="\2" target="_blank" rel="noopener">\1</a>',text)
    return re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',text)


def render(expansion, feature):
    guides=expansion.data['guides']
    if feature in ('limitedReview', 'sealedReview'):
        return render_limited(expansion, 'sealed' if feature=='sealedReview' else 'draft')
    if feature=='limitedImpact':
        return render_impacts(expansion)
    if feature=='synergyReview':
        return render(expansion,'draftCombos') if guides.get('limitedReview') else ''
    availability=expansion.availability[feature]
    if not availability['available']:
        id_={'pickGuide':'pick-guide','pickBaits':'pick-baits','pickDecisions':'pick-decisions','draftCombos':'draft-combos'}[feature]
        return '<section id="'+id_+'" class="report-section"><h2>'+html.escape(availability['label'])+'</h2><p>Non disponibile: '+html.escape(' '.join(availability['missing']))+'</p></section>'
    defaults={'pickGuide':'pick-guide','pickBaits':'pick-baits','pickDecisions':'pick-decisions','draftCombos':'draft-combos'}
    path=guides.get('templates',{}).get(feature,'templates/atlas/'+defaults[feature]+'-section.html')
    template=confined(ROOT,path).read_text(encoding='utf-8')
    data=guides[feature]
    stats={c['name']:c for c in expansion.data['statistics'].get('draft',{}).get('cards',[])}
    catalog={name:c for c in expansion.cards for name in (c['name'],c.get('full',c['name']))}
    for c in expansion.cards:
        catalog.update({face['name']:c for face in c.get('faces',[])})
    def card(name):
        return '<button type="button" class="dd-card-link" data-name="'+html.escape(name,quote=True)+'">'+html.escape(name)+'</button>'
    def stat(name):
        c=stats.get(name,{})
        rate=f"{c['gih']*100:.1f}".replace('.',',')+'%' if c.get('gih') is not None else 'N/D'
        sample=f"{c.get('n',0):,}".replace(',','.')
        return c,rate,sample
    if feature=='pickGuide':
        groups=[]
        for group in data['groups']:
            rows=[]
            for entry in group['cards']:
                c,rate,sample=stat(entry['name'])
                rows.append('<li>'+card(entry['name'])+'<p>'+inline(entry['why'])+'</p><small data-pick-stat hidden>GIH '+rate+' · '+sample+' osservazioni · '+html.escape(c.get('cost',''))+'</small></li>')
            groups.append('<section class="pick-tier"><h4>'+inline(group['title'])+'</h4><p class="small">'+inline(group['note'])+'</p><ul class="pick-list">'+''.join(rows)+'</ul></section>')
        counters=[]
        for entry in data['counters']:
            c,rate,sample=stat(entry['name'])
            counters.append('<li>'+card(entry['name'])+'<p>'+inline(entry['why'])+'</p><small data-pick-stat hidden>GIH '+rate+' · '+sample+' osservazioni · '+html.escape(c.get('cost',''))+'</small><details><summary>Quali risposte prendere</summary><p><strong>Prima che risolva:</strong> '+', '.join(card(n) for n in entry['before'])+'.</p><p><strong>Dopo la risoluzione:</strong> '+', '.join(card(n) for n in entry['after'])+'.</p><p>'+inline(entry['timing'])+'</p></details></li>')
        return template.replace('__GROUPS__',''.join(groups)).replace('__COUNTERS__',''.join(counters))
    if feature=='pickBaits':
        groups=[]
        for group in data['groups']:
            rows=[]
            for entry in group['cards']:
                c,rate,sample=stat(entry['name'])
                rarity='Mitica' if catalog[entry['name']].get('rarity')=='mythic' else 'Rara'
                caution=' · campione sotto 2.000, maggiore cautela' if c.get('n',0)<2000 else ''
                sample_text=' · GIH WR '+rate+' · '+sample+' osservazioni'+caution if expansion.availability['draftStatistics']['available'] and c else ''
                rows.append('<li>'+card(entry['name'])+'<small>'+rarity+sample_text+'</small><p>'+inline(entry['why'])+'</p><details><summary>Quando la prenderei</summary><p>'+inline(entry['when'])+'</p></details></li>')
            groups.append('<div><h3>'+inline(group['title'])+'</h3><p class="small">'+inline(group['note'])+'</p><ul class="pick-list">'+''.join(rows)+'</ul></div>')
        return template.replace('__GROUPS__',''.join(groups))
    if feature=='pickDecisions':
        groups=[]
        for index,group in enumerate(data):
            rows=['<section class="decision-group"><h4>'+inline(group['group'])+'</h4>']
            for offset,case in enumerate(group['cases']):
                rows.append('<details class="pick-decision"'+(' open' if index==0 and offset==0 else '')+'><summary>'+inline(case['title'])+'</summary><div>')
                for key,label in [('context','Il pool e il confronto'),('choose','Cosa sceglierei'),('why','Perché'),('change','Quando cambia')]:
                    rows.append('<p><strong>'+label+':</strong> '+inline(case[key])+'</p>')
                rows.append('</div></details>')
            groups.append(''.join(rows)+'</section>')
        return template.replace('__CASES__',''.join(groups)).replace('__CASE_COUNT__',str(sum(len(g['cases']) for g in data)))
    if feature=='draftCombos':
        aliases=expansion.data['ui'].get('packageAliases',{})
        names=set()
        for c in expansion.cards:
            names.update([c['name'],c['name'].split(' // ')[0],*(f['name'] for f in c.get('faces',[]))])
        pattern=re.compile('|'.join(re.escape(n) for n in sorted(names|set(aliases),key=len,reverse=True))) if names else None
        def text(value):
            parts=[];last=0
            for match in pattern.finditer(value) if pattern else []:
                parts.append(html.escape(value[last:match.start()]))
                name=aliases.get(match[0],match[0])
                parts.append('<span class="card-reference" tabindex="0" role="button" data-card-preview="'+html.escape(name,quote=True)+'" aria-label="Mostra '+html.escape(name,quote=True)+'">'+html.escape(match[0])+'</span>')
                last=match.end()
            return ''.join(parts)+html.escape(value[last:])
        rows=[]
        for index,p in enumerate(data['packages']):
            search=' '.join([p['title'],p['colors'],p['role'],*p['cards'],p['pick']]).lower()
            fields=[('mana','Mana e tempi'),('sequence','Sequenza di gioco'),('risk','Limite da ricordare')]
            rows.append('<article class="draft-package" data-colors="'+html.escape(p['colors'])+'" data-role="'+html.escape(p['role'])+'" data-search="'+html.escape(search,quote=True)+'"><h3>'+html.escape(p['title'])+'</h3><p class="small">'+html.escape(p['colors']+' · '+p['role'])+'</p><p><strong>Hai uno di questi pezzi?</strong> '+' + '.join(text(c) for c in p['cards'])+'</p><p>'+text(p['pick'])+'</p><details'+(' open' if index==0 else '')+'><summary>Sequenza, mana e limiti</summary>'+''.join('<p><strong>'+label+':</strong> '+text(p[key])+'</p>' for key,label in fields)+'</details></article>')
        return template.replace('__PACKAGES__',''.join(rows))
    raise ValueError('Renderer guida non supportato: '+feature)


LIMITED_TIERS={'P':'Prioritaria','S':'Solida','Y':'Dipende dalle sinergie','F':'Riempitivo','B':'Riserva mirata','N':'Eviterei di base'}


def render_impacts(expansion):
    cards=[c for c in expansion.cards if c.get('prospects',{}).get('limitedImpact')]
    if not cards:return ''
    e=html.escape
    rows=[]
    for card in cards:
        a=card['prospects']['limitedImpact']
        rows.append('<article class="lr-card"><h3>'+e(card['name'])+'</h3><p>'+e(a['label'])+'</p><p>'+e(a['why'])+'</p><details><summary>Quando sceglierla e come rispondere</summary><p>Draft: '+e(a['draft'])+'</p><p>Sealed: '+e(a['sealed'])+'</p><p>Prima che risolva: '+e(', '.join(a['before']))+'.</p><p>Dopo la risoluzione: '+e(', '.join(a['after']))+'.</p><p>'+e(a['limit'])+'</p></details></article>')
    return '<section id="limited-impact" class="limited-review"><h2>Carte capaci di cambiare la partita</h2><p>'+str(len(rows))+' valutazioni editoriali: impatto, mana, supporti e risposte. Una carta condizionata non diventa una bomba per il solo simbolo di rarità. Le ospiti mantengono identità e legalità proprie; presenza nel catalogo non certifica la collazione delle stampe.</p><div class="lr-results">'+''.join(rows)+'</div></section>'


def render_limited(expansion, event):
    study=expansion.data['guides'].get('limitedReview')
    if not study:return ''
    cards=[c for c in expansion.cards if c.get('prospects',{}).get('limitedAnalysis')]
    if not cards:return ''
    e=html.escape
    rows=[]
    for c in cards:
        analysis=c['prospects']['limitedAnalysis']
        tiers={context:analysis[context]['tier'] for context in ('draft','sealed')}
        usage=analysis.get('usage',{})
        usage_text=' '.join(str(usage.get(k,'')) for k in ('role','plan','conditions'))
        search=' '.join([c['name'],c['type'],analysis['draft']['note'],analysis['sealed']['note'],usage_text,*analysis['partners']]).lower()
        attrs=' '.join('data-'+context+'-'+kind+'="'+e(value,quote=True)+'"' for context in tiers for kind,value in [('tier',tiers[context]),('order',str(list(LIMITED_TIERS).index(tiers[context])))])
        reviews=c['prospects'].get('limitedReviews',[])
        opinions=' · '.join(e(r['author'])+': '+str(r['value'])+'/'+str(r['scaleMax'])+(' (ciclo)' if r.get('groupAssessment') else '') for r in reviews)
        opinions+=''.join(' · <a href="'+e(r['url'],quote=True)+'" target="_blank" rel="noopener">'+e(r['label'])+'</a>' for r in analysis.get('ruleSources',[]))
        assessments=''.join('<div data-lr-context="'+context+'"><p>'+label+': '+LIMITED_TIERS[tiers[context]]+'</p><p>'+e(analysis[context]['note'])+'</p></div>' for context,label in [('draft','Draft'),('sealed','Sealed')])
        conditions=usage.get('conditions','')
        condition_html='<p>'+e(conditions)+'</p>' if conditions not in [analysis[k]['note'] for k in ('draft','sealed')] else ''
        usage_html=('<h4>Utilizzo previsto: '+e(usage.get('role',''))+'</h4><p>'+e(usage.get('plan',''))+'</p>'+condition_html+'<p class="lr-meta">Fiducia nel giudizio editoriale: '+e(usage.get('confidence','bassa'))+'.</p>') if usage else ''
        rarity={'common':'Comune','uncommon':'Non comune','rare':'Rara','mythic':'Mitica'}.get(c['rarity'],c['rarity'])
        rows.append('<article class="lr-card" data-lr-card data-lr-name="'+e(c['name'],quote=True)+'" data-search="'+e(search,quote=True)+'" data-colors="'+''.join(c['identity'])+'" data-rarity="'+e(c['rarity'])+'" '+attrs+'><h3>'+e(c['name'])+'</h3><p class="lr-meta">'+e(rarity)+' · '+e(c['cost'] or 'Terra')+' · '+e(c['set'])+'</p>'+assessments+usage_html+'<details><summary>Supporti e recensioni</summary><p>'+e(', '.join(analysis['partners']))+'</p><p>'+opinions+'</p><a href="'+e(expansion.manifest['presentation']['pages']['gallery']['url'])+'?card='+e(c['id'])+'#gallery">Apri scheda e fonti</a></details></article>')
    basics=[c for c in expansion.cards if c.get('prospects',{}).get('limitedApplicability')]
    basics_html=('<details><summary>Terre base: base di mana, senza voto di potenza</summary><p>'+e(', '.join(c['name'] for c in basics))+'</p><p>'+e(basics[0]['prospects']['limitedApplicability']['note'])+'</p></details>') if basics else ''
    options=''.join('<option value="'+code+'">'+label+'</option>' for code,label in LIMITED_TIERS.items())
    contexts=''.join('<option value="'+key+'"'+(' selected' if key==event else '')+'>'+label+'</option>' for key,label in [('draft','Draft'),('sealed','Sealed')])
    disagreements='<details class="lr-disagreements"><summary>Dove i recensori divergono e cosa verificare</summary>'+''.join('<h3>'+e(r['name'])+'</h3><p>'+' · '.join('<a href="'+e(o['url'],quote=True)+'" target="_blank" rel="noopener">'+e(o['author'])+'</a>: '+str(o['value'])+'/'+str(o['scaleMax']) for o in r['opinions'])+'</p><p>'+e(r['finding'])+'</p>' for r in study.get('disagreements',[]))+'</details>'
    return '<section id="limited-review" class="limited-review" data-limited-review data-default-context="'+event+'"><h2>'+e(study.get('title','Draft e Sealed: valutazioni disponibili'))+'</h2><p>'+e(study['method'])+'</p><p>'+e(study['coverageNote'])+'</p>'+basics_html+disagreements+'<div class="lr-controls"><label>Cerca carta, supporto o funzione<input type="search" data-lr-filter="query"></label><label>Contesto<select data-lr-filter="context">'+contexts+'</select></label><label>Colore / identità<select data-lr-filter="color"><option value="">Tutti</option><option value="W">Bianco</option><option value="U">Blu</option><option value="B">Nero</option><option value="R">Rosso</option><option value="G">Verde</option><option value="M">Multicolore</option><option value="C">Incolore</option></select></label><label>Rarità<select data-lr-filter="rarity"><option value="">Tutte</option><option value="common">Comuni</option><option value="uncommon">Non comuni</option><option value="rare">Rare</option><option value="mythic">Mitiche</option></select></label><label>Giudizio<select data-lr-filter="tier"><option value="">Tutti</option>'+options+'</select></label><button type="button" data-lr-reset>Azzera filtri</button></div><p data-lr-count role="status" aria-live="polite">'+str(len(rows))+' carte</p><div class="lr-results" data-lr-results>'+''.join(rows)+'</div><p data-lr-empty hidden>Nessuna carta con questi filtri.</p></section>'
