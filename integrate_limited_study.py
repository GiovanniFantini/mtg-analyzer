"""Integrate attributed reviews and independent qualitative Draft/Sealed analysis."""
import argparse
import copy
import json
import re
from pathlib import Path


TIERS={'P':'Prioritaria','S':'Solida','Y':'Dipende dalle sinergie','F':'Riempitivo','B':'Riserva mirata','N':'Eviterei di base'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def integrate(folder, study_dir):
    docs={name:read(folder/(name+'.json')) for name in ['cards','ratings','sources','guides']}
    cards=docs['cards']['cards'];by_id={c['id']:c for c in cards}
    printing={(c['set'],c['number']):c for c in cards}
    study=read(study_dir/'editorial.json');reviews=read(study_dir/'draftsim-reviews.json')
    impact=read(study_dir/'impact.json');synergies=read(study_dir/'synergies.json')
    set_code=study['catalogSet'];date=study['date'];origin='limited-study-'+date
    def lookup(number, code=set_code):
        return printing[(code,str(number))]
    expected={c['number'] for c in cards if c['set']==set_code and c['rarity'] in ('common','uncommon') and not c['basic']}
    found={r['number'] for r in study['cards']}
    if found!=expected or len(found)!=len(study['cards']):
        raise ValueError('The common/uncommon catalog must be covered exactly once.')
    for row in study['cards']:
        if any(row[k]['tier'] not in TIERS or not row[k]['note'] for k in ('draft','sealed')):
            raise ValueError('Missing qualitative assessment')
        for number in row['partners']:lookup(number)
    seen=set()
    for row in reviews['cards']:
        if row['catalogId'] not in by_id or row['catalogId'] in seen or not 0<=row['value']<=row['scaleMax']:
            raise ValueError('Invalid review identity or scale')
        seen.add(row['catalogId'])
    if seen!={c['id'] for c in cards if not c['basic']}:
        raise ValueError('External review coverage is incomplete')
    for row in impact['cards']:
        lookup(row['number'],row['set'])
        for key in ('before','after'):
            for number in row[key]:lookup(number)
    for package in synergies['packages']:
        for number in package['numbers']:lookup(number)
    # All references have been checked before any document is written.
    for row in study['cards']:
        card=lookup(row['number'])
        card['prospects']['limitedAnalysis']={'date':date,'kind':'qualitative_editorial_prerelease',
            'draft':copy.deepcopy(row['draft']),'sealed':copy.deepcopy(row['sealed']),
            'partners':[lookup(n)['name'] for n in row['partners']],
            'observedWinRates':False,'method':'Independent judgments for pick opportunity cost and closed-pool deck construction; no numerical bot score.'}
    source_id=reviews['source']
    for row in reviews['cards']:
        card=by_id[row['catalogId']];p=card['prospects'];rating=docs['ratings']['cards'][card['id']]
        if any(r.get('author')==reviews['author'] and r.get('url')==reviews['url'] and r.get('date','')>reviews['date'] for r in p.get('limitedReviews',[])):
            continue  # A historical import must not replace a later attributed review.
        prior=p.get('limitedReview')
        base=[]
        if prior:
            base.append({'source':prior['source'],'author':prior['author'],'value':prior['value'],
                         'scaleMax':prior['scaleMax'],'url':prior['url'],'context':prior['context'],
                         'date':prior['retrieved'],'published':prior['published'],
                         'groupAssessment':prior.get('groupAssessment')})
        base.extend(r for r in p.get('limitedReviews',[]) if r.get('source') not in {source_id,prior.get('source') if prior else None})
        base.append({'source':source_id,'author':reviews['author'],'value':row['value'],
                     'scaleMax':row['scaleMax'],'url':reviews['url'],'context':reviews['context'],
                     'date':reviews['date'],'published':reviews['published'],'groupAssessment':row['groupAssessment']})
        p['limitedReviews']=base
        if source_id not in p['sources']:p['sources'].append(source_id)
        evidence=[e for e in rating.get('evidence',[]) if e.get('url')!=reviews['url']]
        evidence.append({'author':reviews['author'],'original':str(row['value'])+'/10',
                         'stars':row['value']/2,'url':reviews['url'],
                         'kind':'Recensione Limited prima dell’uscita, scala originale 0–10; divisione per due solo per visualizzazione.'+(' Valutazione del ciclo '+row['groupAssessment']+'.' if row['groupAssessment'] else ''),
                         'published':reviews['published'],'retrieved':date})
        rating['evidence']=evidence
        # community and score intentionally remain the adopted historical values.
    docs['ratings']['externalReviewsDate']=date
    docs['ratings']['method']='I voti esterni conservano autore e scala. community mantiene la recensione adottata di J2SJosh; Draftsim è un confronto distinto. Nessuna media, score interno o conversione di modelli Constructed.'
    for row in impact['cards']:
        card=lookup(row['number'],row['set'])
        card['prospects']['limitedImpact']={k:copy.deepcopy(v) for k,v in row.items() if k not in ('set','number','before','after')}
        card['prospects']['limitedImpact'].update(date=date,kind='editorial_game_changer',
            before=[lookup(n)['name'] for n in row['before']],after=[lookup(n)['name'] for n in row['after']])
    guides=docs['guides']
    package_ids={p['id'] for p in synergies['packages']}
    existing=[p for p in guides.get('draftCombos',{}).get('packages',[]) if p.get('id') not in package_ids]
    for row in synergies['packages']:
        item={k:copy.deepcopy(v) for k,v in row.items() if k!='numbers'}
        item['cards']=[lookup(n)['name'] for n in row['numbers']];existing.append(item)
    guides['draftCombos']={'packages':existing}
    guides['limitedReview']={'date':date,'origin':origin,
        'method':'Valutazioni editoriali prima dell’uscita. Draft considera priorità e costo del pick; Sealed valuta il contributo nel pool aperto. Le fasce sono qualitative, senza WR, medie tra autori o voti nuovi per i bot.',
        'coverageNote':str(len(found))+' comuni e non comuni non base coperte. Le cinque terre base sono escluse. Le recensioni esterne restano attribuite: J2SJosh 0–5 e Andrew Quinn 0–10; non sono voti Sealed distinti.'}
    guides['limitedReview']['disagreements']=[]
    for row in read(study_dir/'disagreements.json')['cards']:
        card=lookup(row['number']);opinions=card['prospects']['limitedReviews']
        guides['limitedReview']['disagreements'].append({'name':card['name'],'finding':row['finding'],
            'opinions':[{'author':r['author'],'value':r['value'],'scaleMax':r['scaleMax'],'url':r['url']} for r in opinions]})
    guides['fragments']['draft.limited-link']='<a href="#limited-review">Comuni e non comuni</a><a href="#limited-impact">Carte decisive</a>'
    guides['fragments']['sealed.review-links']='<nav aria-label="Approfondimenti Sealed"><a href="#limited-review">Valutazioni di comuni e non comuni</a> · <a href="#limited-impact">Carte decisive e risposte</a></nav>'
    intro=guides['fragments'].get('draft.copy-0','')
    intro=re.sub(r'<span data-limited-summary>.*?</span>','',intro,flags=re.S)
    guides['fragments']['draft.copy-0']=intro+'<span data-limited-summary> '+str(len(found))+' valutazioni separate Draft/Sealed, '+str(len(impact['cards']))+' carte decisive e '+str(len(existing))+' pacchetti di sinergie. Voti dei recensori e statistiche di gioco sono prove distinte.</span>'
    sealed=guides['fragments'].get('gallery.strategy','')
    sealed=re.sub(r'<p data-limited-study>.*?</p>','',sealed,flags=re.S)
    guides['fragments']['gallery.strategy']=sealed+'<p data-limited-study>Lo studio del '+date+' aggiunge il confronto Draftsim su '+str(len(seen))+' identità e giudizi Sealed specifici su tutte le comuni e non comuni non base. Nessun voto Draft viene trasferito automaticamente al Sealed; le valutazioni sono editoriali prima dell’uscita.</p>'
    # Editorial selections point into the complete, independently reviewed catalog.
    selections=[('Bianco: rimozione e sviluppo',[22,34,17],[1,44]),
                ('Blu: corpi, carte e tempo',[50,51,83],[54,62]),
                ('Nero: risposte e continuità',[114,105,131],[125,94]),
                ('Rosso: pressione con interazione',[162,164,139],[178,158]),
                ('Verde: mana, stabilizzazione e chiusura',[190,224,194],[208,218])]
    notes={r['number']:r for r in study['cards']}
    guides['pickGuide']['groups']=[{'title':title,'note':'Selezione editoriale di tre comuni e due non comuni. Valuta curva, colori e piano prima di applicare la priorità; tutte le 201 valutazioni sono consultabili sotto.',
        'cards':[{'name':lookup(n)['name'],'why':notes[str(n)]['draft']['note']} for n in common+uncommon]} for title,common,uncommon in selections]
    # Baits are explicit conditional evaluations, not a rarity penalty.
    bait=read(study_dir/'baits.json')
    guides['pickBaits']={'groups':[{'title':'Rare che richiedono una ragione concreta','note':'Valutazione del testo e della struttura del mazzo, senza classifica di risultati osservati.',
        'cards':[{'name':lookup(r['number'])['name'],'why':r['why'],'when':r['when']} for r in bait['cards']]}]}
    guides['fragments']['pick-baits-section.copy-0']='Anteprima del '+date+'. Le riserve dipendono dal piano, non dal simbolo di rarità.'
    sources=docs['sources']['research']
    sources['sources']=[s for s in sources['sources'] if s['id']!=source_id]+[{
        'id':source_id,'publisher':'Draftsim','author':reviews['author'],'url':reviews['url'],
        'published':reviews['published'],'retrieved':date,'coverage':reviews['matchedCards'],
        'context':reviews['context'],'method':reviews['method'],'captureSha256':reviews['captureSha256']}]
    sources['limitedStudy']={'date':date,'editorialCommonUncommon':len(found),
        'draftsimCards':len(seen),'gameChangers':len(impact['cards']),'packages':len(existing),
        'newPackages':len(synergies['packages']),'numericEngineScoresChanged':False,
        'observedStatisticsAdded':False,'sourceAudit':(study_dir/'source-audit.json').as_posix()}
    for name,value in docs.items():write(folder/(name+'.json'),value)
    return sources['limitedStudy']


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expansion',required=True,type=Path)
    parser.add_argument('--study',required=True,type=Path)
    args=parser.parse_args();print(json.dumps(integrate(args.expansion,args.study),ensure_ascii=False))
