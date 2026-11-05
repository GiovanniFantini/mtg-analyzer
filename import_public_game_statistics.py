"""Derive per-game GIH WR from the CC BY 4.0 17Lands public game datasets.

Run with pandas/numpy available. The static build does not use these packages.
Only derived counts, rates and acquisition metadata are kept in the repository.
"""
import argparse, concurrent.futures, csv, gzip, hashlib, io, json, os, tempfile, time, urllib.request
from datetime import date
from pathlib import Path
from tournament_index import identity_aliases,name_key
MATCHING_VERSION=4
MISSING_PUBLIC_DATA_NOTE='Statistiche 17Lands non integrate: gli aggregati API non sono riutilizzati in attesa di derivazione dai dataset pubblici con licenza verificata.'

def write_json_atomic(path,value):
    """A rejected replacement never truncates the currently usable snapshot."""
    path=Path(path)
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,prefix='.'+path.name+'-',suffix='.tmp',delete=False) as stream:
        temporary=Path(stream.name);json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
    try:
        for attempt in range(4):
            try:os.replace(temporary,path);break
            except OSError:
                if attempt==3:raise
                time.sleep(.2)
    finally:
        temporary.unlink(missing_ok=True)

def updated_limitations(notes):
    return [note for note in notes if note!=MISSING_PUBLIC_DATA_NOTE]

def matching_fingerprint(cards):
    identities=sorted((c['id'],c.get('oracleId'),sorted(identity_aliases(c))) for c in cards)
    return hashlib.sha256(json.dumps(identities,ensure_ascii=False).encode('utf-8')).hexdigest()

def match_card_rows(cards,totals):
    names={name_key(n):n for n in totals['cards']};rows=[];matched=set();owners={}
    for c in cards:
        candidates=[names[k] for k in sorted(identity_aliases(c)) if k in names]
        if not candidates:continue
        if len(candidates)>1:raise ValueError('Ambiguous game-data aliases: '+c['id'])
        name=candidates[0];identity=c.get('oracleId') or name_key(c.get('full') or c['name'])
        if name in owners and owners[name]!=identity:raise ValueError('Game-data column matches different card identities: '+name)
        owners[name]=identity;matched.add(name);v=totals['cards'][name]
        rows.append({'catalogId':c['id'],'name':c['name'],'sourceName':name,'sourceUrl':'https://www.17lands.com/public_datasets','metrics':{'inHandWinRate':100*v['wins']/v['games'] if v['games'] else None,'games':v['games'],'wins':v['wins']}})
    return rows,matched

def aggregate(path,event=None):
    import numpy as np
    import pandas as pd
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        columns=next(csv.reader(stream))
    names=[c[len('opening_hand_'):] for c in columns if c.startswith('opening_hand_') and 'drawn_'+c[len('opening_hand_'):] in columns]
    opening=['opening_hand_'+n for n in names]; drawn=['drawn_'+n for n in names]
    counts=np.zeros(len(names),dtype='int64'); wins=counts.copy(); games=0; total_wins=0; contexts={}
    has_colors='main_colors' in columns
    game_one=event=='TradDraft' and 'game_number' in columns
    first={'counts':counts.copy(),'wins':wins.copy(),'games':0,'won':0,'contexts':{}}
    def add_contexts(target,observed,won,colors):
        for raw in np.unique(colors):
            if not raw or any(c not in 'WUBRG' for c in raw):continue
            color=''.join(c for c in 'WUBRG' if c in raw)
            row=target.setdefault(color,{'counts':np.zeros(len(names),dtype='int64'),'wins':np.zeros(len(names),dtype='int64'),'games':0,'won':0})
            selected=colors==raw;row['counts']+=observed[selected].sum(axis=0);row['wins']+=observed[selected&won].sum(axis=0)
            row['games']+=int(selected.sum());row['won']+=int((selected&won).sum())
    for chunk in pd.read_csv(path,usecols=['won',*(['game_number'] if game_one else []),*(['main_colors'] if has_colors else []),*opening,*drawn],chunksize=4000):
        outcome=chunk['won']
        if not outcome.isin([True,False]).all():raise ValueError('Invalid game outcome')
        observed=(chunk[opening].to_numpy()+chunk[drawn].to_numpy())>0
        won=outcome.to_numpy(dtype=bool)
        counts+=observed.sum(axis=0);wins+=observed[won].sum(axis=0)
        games+=len(chunk);total_wins+=int(won.sum())
        if has_colors:
            colors=chunk['main_colors'].fillna('').astype(str).to_numpy()
            add_contexts(contexts,observed,won,colors)
        if game_one:
            if (chunk['game_number']<1).any():raise ValueError('Unexpected game_number encoding')
            selected=chunk['game_number'].to_numpy()==1;seen=observed[selected];outcome=won[selected]
            first['counts']+=seen.sum(axis=0);first['wins']+=seen[outcome].sum(axis=0);first['games']+=int(selected.sum());first['won']+=int(outcome.sum())
            if has_colors:add_contexts(first['contexts'],seen,outcome,colors[selected])
    def serialize_contexts(contexts):
        return {color:{'games':row['games'],'wins':row['won'],'cards':{n:{'games':int(g),'wins':int(w)} for n,g,w in zip(names,row['counts'],row['wins'])}} for color,row in contexts.items()}
    result={'games':games,'wins':total_wins,'cards':{n:{'games':int(g),'wins':int(w)} for n,g,w in zip(names,counts,wins)},'contexts':serialize_contexts(contexts)}
    if game_one:result['gameOne']={'games':first['games'],'wins':first['won'],'cards':{n:{'games':int(g),'wins':int(w)} for n,g,w in zip(names,first['counts'],first['wins'])},'contexts':serialize_contexts(first['contexts'])}
    return result

def acquire(manifest,event,out):
    root=Path(manifest).parent;m=json.loads(Path(manifest).read_text(encoding='utf-8'));code=m['code']
    result_path=out/(m['id']+'-'+event+'.json')
    if result_path.exists():
        cached=json.loads(result_path.read_text(encoding='utf-8'))
        if cached.get('status')=='unavailable':return cached
        if cached.get('matchingVersion')==MATCHING_VERSION:
            cards=json.loads((root/'cards.json').read_text(encoding='utf-8'))['cards']
            if cached.get('matchingFingerprint')==matching_fingerprint(cards):return cached
        raise ValueError('Cached card matching predates the current method. Use a new dated --output directory; previous snapshots are preserved.')
    url=f'https://17lands-public.s3.amazonaws.com/analysis_data/game_data/game_data_public.{code}.{event}.csv.gz'
    try:
        with urllib.request.urlopen(url,timeout=60) as response, tempfile.NamedTemporaryFile(suffix='.csv.gz',delete=False) as dest:
            digest=hashlib.sha256();size=0;last=response.headers.get('Last-Modified')
            while data:=response.read(1024*1024):digest.update(data);dest.write(data);size+=len(data)
            path=Path(dest.name)
    except urllib.error.HTTPError as e:
        if e.code not in (403,404):raise
        result={'expansion':m['id'],'code':code,'event':event,'status':'unavailable','url':url,'retrieved':date.today().isoformat(),'httpStatus':e.code}
        result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return result
    try:totals=aggregate(path,event)
    finally:path.unlink(missing_ok=True)
    cards=json.loads((root/'cards.json').read_text(encoding='utf-8'))['cards'];rows,matched=match_card_rows(cards,totals)
    result={'schemaVersion':1,'matchingVersion':MATCHING_VERSION,'matchingFingerprint':matching_fingerprint(cards),'provider':'17Lands public datasets','url':'https://www.17lands.com/public_datasets','retrieved':date.today().isoformat(),'rateUnit':'percent',
      'filters':{'event':event,'ranks':'Tutti i ranghi nel dataset','archetype':'Tutti gli archetipi','period':'Intero dataset pubblico; aggiornamento '+str(last)},
      'metrics':{'inHandWinRate':{'label':'GIH WR: partite vinte quando la carta era nella mano iniziale o pescata','unit':'percent','status':'public'},'games':{'label':'Partite con la carta nella mano iniziale o pescata','unit':'games','status':'public'},'wins':{'label':'Vittorie nelle partite del campione GIH','unit':'games','status':'public'}},
      'cards':rows,'coverage':{'catalogCards':len(cards),'matchedCards':len(rows),'withWinRate':sum(r['metrics']['inHandWinRate'] is not None for r in rows),'missingCatalogIds':[c['id'] for c in cards if c['id'] not in {r['catalogId'] for r in rows}],'unmatchedSourceNames':sorted(set(totals['cards'])-matched)},
      'derivation':{'datasetUrl':url,'sha256':digest.hexdigest(),'compressedBytes':size,'lastModified':last,'games':totals['games'],'wins':totals['wins'],'license':'CC BY 4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/','method':'Each game counts once per card if opening_hand + drawn > 0, irrespective of copies. Rate = wins / observed games * 100. Includes all ranks and archetypes in this complete public file; not the current live aggregate.'},
      'limitations':['La WR descrive le partite osservate, non la probabilità causale di vittoria della carta.','Nessuna soglia minima applicata: consultare il campione, soprattutto quando è piccolo.','Carte assenti o mai viste in mano conservano WR null. Il dataset pubblico ha una propria finestra storica.']}
    result['colorContexts']={color:{'games':context['games'],'wins':context['wins'],'cards':match_card_rows(cards,context)[0]} for color,context in sorted(totals['contexts'].items())}
    result['derivation']['contextMethod']='Source main_colors field, primary colors only; splash_colors is not merged. Same GIH observation rule within each context.'
    if 'gameOne' in totals:
        first=totals['gameOne'];result['gameOne']={'games':first['games'],'wins':first['wins'],'cards':match_card_rows(cards,first)[0],
            'colorContexts':{color:{'games':context['games'],'wins':context['wins'],'cards':match_card_rows(cards,context)[0]} for color,context in sorted(first['contexts'].items())}}
        result['derivation']['gameOneMethod']='TradDraft game_number == 1, before between-game sideboarding; same GIH observation rule. All-game rows remain separate.'
    result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--apply',action='store_true');p.add_argument('--workers',type=int,default=3);p.add_argument('--slug',action='append');p.add_argument('--event',action='append',choices=['PremierDraft','TradDraft','QuickDraft','PickTwoDraft','Sealed']);p.add_argument('--reverse',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    rows=json.loads(Path('expansions.json').read_text());manifests=[r['manifest'] for r in rows if not a.slug or Path(r['manifest']).parent.name in a.slug]
    tasks=[]
    for m in manifests:
        events=json.loads((Path(m).parent/'limited.json').read_text(encoding='utf-8'))['events']
        # Pick-Two is a separate Draft population; use the event in that expansion.
        draft_events=[v for v in events.values() if v.get('kind')=='draft']
        draft='PickTwoDraft' if draft_events and all(v.get('picksPerTurn')==2 for v in draft_events) else 'PremierDraft'
        allowed={draft,'Sealed',*(['TradDraft','QuickDraft'] if draft_events and draft=='PremierDraft' else [])}
        tasks.extend((m,event) for event in dict.fromkeys(a.event or [draft,'Sealed']) if event in allowed)
    results=[]
    if a.reverse:tasks.reverse()
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        future_map={pool.submit(acquire,m,e,a.output):(m,e) for m,e in tasks}
        for f in concurrent.futures.as_completed(future_map):
            m,e=future_map[f];result=f.result();results.append((m,e,result));print(Path(m).parent.name,e,result.get('status','ok'),result.get('coverage',{}).get('withWinRate',0),flush=True)
    if a.apply:
        for m,e,r in results:
            if r.get('status')=='unavailable':continue
            root=Path(m).parent;path=root/'statistics.json';s=json.loads(path.read_text(encoding='utf-8'));kind='sealed' if e=='Sealed' else 'draft';suffix={'TradDraft':'-traditional','QuickDraft':'-quick'}.get(e,'');s.setdefault(kind,{}).setdefault('externalSources',{})['17lands-public'+suffix]=r
            if kind=='draft' and 'limitations' in s[kind]:s[kind]['limitations']=updated_limitations(s[kind]['limitations'])
            s['limitations']=updated_limitations(s.get('limitations',[]))
            write_json_atomic(path,s)
            sp=root/'sources.json';sources=json.loads(sp.read_text(encoding='utf-8'));sources.setdefault('externalStatistics',{})[kind+'17landsPublic'+suffix]={k:r[k] for k in ['provider','url','retrieved','filters','derivation','coverage']};write_json_atomic(sp,sources)
    (a.output/'coverage.json').write_text(json.dumps([{'expansion':Path(m).parent.name,'event':e,'status':r.get('status','ok'),'coverage':r.get('coverage')} for m,e,r in results],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
