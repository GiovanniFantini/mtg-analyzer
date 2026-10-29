"""Transparent format-specific tournament indices; no inferred card win rates."""
import math,unicodedata
from datetime import date,timedelta
from collections import Counter,defaultdict
FORMATS=('standard','pioneer','modern','pauper')
METHOD='published-deck-share-v1'
START='2026-10-01';END='2026-10-28';MID='2026-10-15'

def name_key(name):
 return ' '.join(unicodedata.normalize('NFKC',name or '').replace('\u2019',"'").replace('\u2018',"'").casefold().split())

def merge_events(records):
 events={}
 for r in records:
  if r.get('status')=='unavailable':continue
  e=events.setdefault(r['id'],{**r,'decks':[],'pages':[]})
  if (e['date'],e['format'])!=(r['date'],r['format']):raise ValueError('Event identity mismatch')
  if r['url'] not in e['pages']:e['pages'].append(r['url'])
  known={d['id']:d for d in e['decks']}
  for d in r['decks']:
   if d['id'] in known:
    if d!=known[d['id']]:raise ValueError('Conflicting duplicate deck')
   else:e['decks'].append(d);known[d['id']]=d
 return sorted(events.values(),key=lambda e:(e['date'],e['id']))

def prepare_events(events):
 for e in events:
  if e.get('kind')=='recent-mtgo-challenge':
   label=e.get('name','').casefold()
   e['trendKind']='recent-mtgo-qualifier' if 'qualifier' in label else 'recent-mtgo-showcase' if 'showcase' in label else e['kind']
  for d in e['decks']:
   for section in ('main','sideboard'):
    d[section+'Keys']={name_key(n):qty for n,qty in d[section].items()}
 return events

def identity_aliases(card):
 return set(filter(None,[name_key(card.get('full')),name_key(card['name']),name_key(card.get('oracleName')),*[name_key(f.get(k)) for f in (card.get('faces') or [])[:1] for k in ('name','oracleName')]]))

def section_copies(deck,aliases,section):
 return sum(qty for name,qty in deck[section+'Keys'].items() if name in aliases)

def summarize(events,aliases):
 stats={'decks':sum(len(e['decks']) for e in events),'events':len(events),'withCard':0,'mainDecks':0,'sideboardDecks':0,'mainCopies':0,'sideboardCopies':0,'eventsWithCard':0,'top8Lists':0,'winningLists':0}
 examples=[];archetypes=Counter();seen_events=[]
 for e in events:
  present=False
  for d in e['decks']:
   main=section_copies(d,aliases,'main');side=section_copies(d,aliases,'sideboard')
   if not main+side:continue
   present=True;stats['withCard']+=1;stats['mainDecks']+=bool(main);stats['sideboardDecks']+=bool(side);stats['mainCopies']+=main;stats['sideboardCopies']+=side
   if d['rank'] is not None:stats['top8Lists']+=d['rank']<=8;stats['winningLists']+=d['rank']==1
   if d.get('archetype'):archetypes[d['archetype']]+=1
   examples.append({'event':e['name'],'eventId':e['id'],'date':e['date'],'player':d['player'],'url':d['sourceUrl'],'archetype':d.get('archetype',''),'main':main,'sideboard':side,'rank':d['rank'],'wins':d.get('wins'),'losses':d.get('losses')})
  if present:stats['eventsWithCard']+=1;seen_events.append(e['id'])
 stats['sharePct']=100*stats['withCard']/stats['decks'] if stats['decks'] else None
 examples.sort(key=lambda x:(x['rank'] is None,x['rank'] if x['rank'] is not None else 999,-int(x['date'].replace('-',''))))
 return stats,examples[:3],archetypes.most_common(3),seen_events

def trend_samples(events,aliases,start,end):
 # Compare a single publication cohort present in both periods. Select the
 # largest balanced cohort by denominator, never by the card's observed trend.
 groups=defaultdict(list)
 for e in events:groups[(e.get('trendKind',e.get('kind','unknown')),e.get('publishedCoverage','unknown'))].append(e)
 candidates=[]
 for key,rows in groups.items():
  previous=[e for e in rows if e['date']<MID];recent=[e for e in rows if e['date']>=MID]
  n1=sum(len(e['decks']) for e in previous);n2=sum(len(e['decks']) for e in recent)
  if n1 and n2:candidates.append((min(n1,n2),key,previous,recent))
 chosen=max(candidates,key=lambda c:(c[0],c[1])) if candidates else None
 old,_,_,_=summarize(chosen[2] if chosen else [],aliases);new,_,_,_=summarize(chosen[3] if chosen else [],aliases)
 cohort={'kind':chosen[1][0],'publishedCoverage':chosen[1][1]} if chosen else None
 previous_end=min(end,(date.fromisoformat(MID)-timedelta(days=1)).isoformat())
 previous_period={'start':start,'end':previous_end} if start<=previous_end else {'start':None,'end':None,'reason':'not_eligible_in_period'}
 return old,new,cohort,previous_period,{'start':min(end,max(start,MID)),'end':end}

def calculate_index(card,format,events,first_release,as_of=END,aliases=None):
 aliases=aliases or identity_aliases(card);legality=card.get('legalities',{}).get(format,'unknown')
 matching=[e for e in events if e['format']==format]
 # Earlier positive sightings can establish that a reprinted identity already existed.
 sightings=[e['date'] for e in matching if any(section_copies(d,aliases,'main')+section_copies(d,aliases,'sideboard') for d in e['decks'])]
 eligible_from=min([first_release or '9999-12-31',*sightings])
 recent=[e for e in matching if START<=e['date']<=as_of and e['date']>=eligible_from]
 historical=[e for e in matching if e['date']<START and e['date']>=eligible_from]
 observed,examples,archetypes,seen_events=summarize(recent,aliases);history,historical_examples,_,_=summarize(historical,aliases)
 sample_start=min(as_of,max(START,eligible_from))
 old,new,cohort,previous_period,recent_period=trend_samples(recent,aliases,sample_start,as_of)
 reason='not_legal' if legality in ('not_legal','banned') else 'legality_unknown' if legality not in ('legal','restricted') else 'basic_land' if card.get('basic') or ('Basic' in card.get('type','').split() and 'Land' in card.get('type','')) else 'no_post_release_sample' if not observed['decks'] else None
 score=round(observed['sharePct'],4) if reason is None else None
 status='unavailable' if score is None else 'not_observed' if not observed['withCard'] else 'repeated' if observed['eventsWithCard']>=3 and observed['withCard']>=5 else 'first_sightings'
 delta=new['sharePct']-old['sharePct'] if new['decks']>=50 and old['decks']>=50 else None
 trend='insufficient_data' if delta is None else 'rising' if delta>=1 and new['withCard']>=3 else 'falling' if delta<=-1 and old['withCard']>=3 else 'stable'
 outlook='not_assessed' if score is None else 'watch' if observed['withCard'] and (trend=='rising' or status=='first_sightings') else 'repeated_use' if status=='repeated' else 'no_signal'
 return {'schemaVersion':1,'method':METHOD,'date':as_of,'score':score,'reason':reason,'status':status,'legality':legality,'legalityDate':card.get('legalitiesRetrieved'),'legalitySource':card.get('legalitySource'),'eligibleFrom':None if eligible_from=='9999-12-31' else eligible_from,
  'sample':{'start':sample_start,'end':as_of,'decks':observed.pop('decks'),'events':observed.pop('events')},'observed':observed,
  'trend':{'method':'matched-cohort-v1','cohort':cohort,'status':trend,'deltaPoints':round(delta,4) if delta is not None else None,'previous':{**previous_period,'decks':old['decks'],'withCard':old['withCard']},'recent':{**recent_period,'decks':new['decks'],'withCard':new['withCard']}},
  'outlook':{'status':outlook,'kind':'observational_signal_not_forecast'},'history':{'decks':history['decks'],'withCard':history['withCard'],'events':history['eventsWithCard'],'sharePct':round(history['sharePct'],4) if history['sharePct'] is not None else None},'eventsWithCard':seen_events,'examples':examples,'historicalExamples':historical_examples,'archetypes':[{'name':n,'decks':count} for n,count in archetypes]}

def signal_level(indices):
 positive=[i for i in indices if i.get('score') is not None and i['score']>0]
 if any(i['status']=='repeated' for i in positive):return 'Confermata'
 if any(i['observed']['eventsWithCard']>=2 for i in positive):return 'Emergente'
 return 'Preliminare' if positive else None

def validate_index(index):
 if index.get('schemaVersion')!=1 or index.get('method')!=METHOD:raise ValueError('Unsupported tournament index')
 score=index.get('score');sample=index['sample'];o=index['observed']
 for field in ['date']:
  date.fromisoformat(index[field])
 for field in ['start','end']:
  date.fromisoformat(sample[field])
 if sample['end']<sample['start'] or any(type(sample[k]) is not int or sample[k]<0 for k in ['decks','events']):raise ValueError('Invalid sample')
 if score is not None:
  if type(score) not in (float,int) or not math.isfinite(score) or not 0<=score<=100 or sample['decks']<=0 or index.get('reason') is not None:raise ValueError('Invalid tournament score')
  if abs(score-100*o['withCard']/sample['decks'])>0.000051:raise ValueError('Tournament score inconsistent with deck counts')
 elif index.get('reason') is None:raise ValueError('Missing tournament score reason')
 if score==0 and index['status']!='not_observed' or score is not None and score>0 and index['status'] not in ['repeated','first_sightings']:raise ValueError('Inconsistent observed status')
 if index['outlook'].get('kind')!='observational_signal_not_forecast':raise ValueError('Unsupported outlook kind')
 for field in ['withCard','mainDecks','sideboardDecks','top8Lists','winningLists']:
  if type(o[field]) is not int or not 0<=o[field]<=sample['decks']:raise ValueError('Invalid deck count')
 if max(o['mainDecks'],o['sideboardDecks'])>o['withCard'] or o['mainDecks']+o['sideboardDecks']<o['withCard'] or o['top8Lists']>o['withCard'] or o['winningLists']>o['top8Lists']:raise ValueError('Invalid card-presence bounds')

def validate_card_indices(cards):
 for c in cards:
  for f,a in c.get('prospects',{}).get('formats',{}).items():
   if 'tournamentIndex' in a:
    try:validate_index(a['tournamentIndex'])
    except (KeyError,ValueError,TypeError) as exc:raise ValueError('Invalid tournament index '+c['id']+' / '+f+': '+str(exc)) from exc
