import csv, json, pathlib, statistics

ROOT=pathlib.Path(__file__).parent
def read_reviews(file):
    out={}
    for line in (ROOT/file).read_text(encoding='utf-8').splitlines():
        num,score,role,why,condition=line.split('|')
        assert int(num) not in out
        out[int(num)]=dict(score=float(score),role=role,why=why,condition=condition)
    return out

reviews=read_reviews('sealed-reviews.tsv')
spg_reviews=read_reviews('spg-reviews.tsv')
assert set(reviews)==set(range(1,281))
rows=list(csv.reader((ROOT/'community-review.csv').open(encoding='utf-8-sig')))[9:]
community={r[3]:dict(num=int(r[0]),grade=r[10].strip(),row=i+10,build=r[12]=='y') for i,r in enumerate(rows) if r[0].isdigit()}
scale={'F':1,'D-':1.5,'D':2,'D+':2.25,'C-':2.5,'C':3,'C+':3.25,'B-':3.5,'B':4,'B+':4.25,'A-':4.5,'A':4.75,'A+':5}
sheet='https://docs.google.com/spreadsheets/d/1b3UH-0hN7DjLhWFp7GMMe8fRDY2801tAZ4X4bF_EqFo/edit?gid=265411862'
white='https://www.reddit.com/r/spikes/comments/1wk4oip/draft_reality_fracture_set_review_white/'
blue='https://www.reddit.com/r/spikes/comments/1wk8zem/draft_reality_fracture_limited_set_review_blue/'
extra={
 'Campus Crier': [('LOR_Fei','B/B+',white),('justinwrite2','B-',white)],
 'Shatterwing Pegasus':[('LOR_Fei','B/B+',white),('justinwrite2','C+',white)],
 'Germinate Recruits':[('LOR_Fei','D+',white)],
 'Kindred Judgment':[('LOR_Fei','D+',white)],
 'Guiding Hydra':[('LOR_Fei','A',white)],
 'Flickering Hound':[('LOR_Fei','B',white)],
 'Thalia, the Survivor':[('LOR_Fei','D+',white)],
 'Yoshimaru, Beloved Companion':[('LOR_Fei','B/B+',white)],
 'Return to the Light Realms':[('LOR_Fei','F',white)],
 'Memory Trap':[('LOR_Fei','C+',white)],
 'Hexhaven Battalion':[('LOR_Fei','C+',white)],
 'Mindseeker Oculus':[('LOR_Fei','B-',blue)],
 'Divining Duelist':[('LOR_Fei','C+/B-',blue)],
 'The Theorist, Jace Beleren':[('LOR_Fei','A+',blue)],
 'Lyra, Tolarian Archangel':[('LOR_Fei','A',blue)],
 'Cruel Calculations':[('LOR_Fei','F',blue)],
 'Way of the Mind Sculptor':[('LOR_Fei','F',blue)],
}
def convert(g):
    return statistics.mean(scale[x.strip()] for x in g.split('/'))

all_cards=[]
for setcode,file in [('fra','fra-all.json'),('spg','fra-spg.json')]:
    raw=json.loads((ROOT/file).read_text(encoding='utf-8'))
    for c in raw:
        name=c['name'].split(' // ')[0]
        faces=c.get('card_faces') or [c]
        front=faces[0]
        basic='Basic Land' in c['type_line']
        cr=community.get(c['name']) if setcode=='fra' else None
        num=cr['num'] if cr else int(c['collector_number'])
        if basic:
            r=dict(score=None,role='Terra base',why='Fonte di mana essenziale, disponibile anche oltre alle copie aperte nelle buste.',condition='La quantità dipende dai simboli colorati e dalla curva del mazzo. Non ha senso confrontarla con una bomba mediante le stelle.')
        else:
            r=(reviews if setcode=='fra' else spg_reviews)[num].copy()
        evidence=[]
        if cr:
            evidence.append(dict(author='Casual Spike',original=cr['grade'],stars=convert(cr['grade']),url=sheet+'&range=D'+str(cr['row'])+':K'+str(cr['row']),kind='Recensione Limited condivisa su r/spikes'))
        for author,grade,url in extra.get(name,[]):
            evidence.append(dict(author=author,original=grade,stars=convert(grade),url=url,kind='Recensione Draft' if author=='LOR_Fei' else 'Commento alla recensione'))
        forum_note=''
        forum_link=''
        if name in ['Splinter Twin','Divining Duelist']:
            forum_note='Su r/lrcast viene discussa la combo Twin + Divining Duelist. È un feedback qualitativo: non viene trasformato in un voto numerico.'
            forum_link='https://www.reddit.com/r/lrcast/comments/1wh9gkq/you_can_literally_splinter_twin_combo_people_in/'
        if name=='Divining Duelist':
            r['condition']+=' Se apri anche Splinter Twin, la coppia può creare arbitrariamente molte pedine rapide: non presupporre di trovarla.'
        all_cards.append(dict(id=f'{setcode}-{num}',set=setcode.upper(),number=num,printing=c['collector_number'],name=name,full=c['name'],colors=front.get('colors',c.get('colors',[])),identity=c.get('color_identity',[]),cost=front.get('mana_cost',''),mv=c['cmc'],type=front['type_line'],rarity=c['rarity'],basic=basic,land='Land' in front['type_line'],creature='Creature' in front['type_line'],image=c['image_uris']['normal'],large=c['image_uris']['large'],url=c['scryfall_uri'],oracle='\n\n'.join(f['name']+' '+f.get('mana_cost','')+'\n'+f['type_line']+'\n'+f.get('oracle_text','') for f in faces),evidence=evidence,community=round(statistics.mean(e['stars'] for e in evidence),2) if evidence else None,forum_note=forum_note,forum_link=forum_link,build=cr['build'] if cr else False,**r))

assert len(all_cards)==295 and len({c['full'] for c in all_cards})==295
assert sum(bool(c['evidence']) for c in all_cards)==280
stats=[]
for color in 'WUBRG':
    pool=[c for c in all_cards if c['set']=='FRA' and c['rarity']=='common' and c['colors']==[color] and c['creature']]
    stats.append(dict(color=color,curve=[sum(c['mv']==n for c in pool) for n in range(1,7)],names=[c['name'] for c in pool if c['mv']<=2]))
from combo_data import enrich
combos=enrich(all_cards)
from sentiment_data import enrich as enrich_sentiment, render_assets
sentiment_meta=enrich_sentiment(all_cards)
payload=dict(date='22 settembre 2026',sentimentMeta=sentiment_meta,cards=sorted(all_cards,key=lambda c:(c['set'],c['number'])),stats=stats,scale=scale,combos=combos)
(ROOT/'sealed-database.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
html=(ROOT/'database-template.html').read_text(encoding='utf-8').replace('__DATA__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
html=render_assets(html, ROOT)
(ROOT/'Reality-Fracture-Sealed.html').write_text(html,encoding='utf-8')
combo_html=(ROOT/'combo-template.html').read_text(encoding='utf-8').replace('__DATA__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
(ROOT/'Reality-Fracture-Combo.html').write_text(combo_html,encoding='utf-8')
print(f"Database: {len(all_cards)} schede; {sum(bool(c['evidence']) for c in all_cards)} con voto esterno; {sum(c['score'] is not None for c in all_cards)} con voto Sealed; {len(extra)} confrontate con ulteriori giudizi.")
print('Curve comuni:',stats)

from build_analysis import build as build_analysis
build_analysis()

from build_simulator import build as build_simulator
build_simulator()

from build_draft_report import build as build_draft_report
build_draft_report()

from build_discovery import build as build_discovery
build_discovery()
