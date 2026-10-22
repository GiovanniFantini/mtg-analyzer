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
