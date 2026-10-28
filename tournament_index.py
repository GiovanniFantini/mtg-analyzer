"""Transparent format-specific tournament indices; no inferred card win rates."""
import math,unicodedata
from datetime import date
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
  for d in e['decks']:
   for section in ('main','sideboard'):
    d[section+'Keys']={name_key(n):qty for n,qty in d[section].items()}
 return events

def identity_aliases(card):
 return set(filter(None,[name_key(card.get('full')),name_key(card['name']),name_key(card.get('oracleName')),*[name_key(f.get('name')) for f in (card.get('faces') or [])[:1]]]))

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

def calculate_index(card,format,events,first_release,as_of=END):
 aliases=identity_aliases(card);legality=card.get('legalities',{}).get(format,'unknown')
 matching=[e for e in events if e['format']==format]
 # Earlier positive sightings can establish that a reprinted identity already existed.
 sightings=[e['date'] for e in matching if any(section_copies(d,aliases,'main')+section_copies(d,aliases,'sideboard') for d in e['decks'])]
 eligible_from=min([first_release or '9999-12-31',*sightings])
 recent=[e for e in matching if START<=e['date']<=as_of and e['date']>=eligible_from]
 historical=[e for e in matching if e['date']<START and e['date']>=eligible_from]
 observed,examples,archetypes,seen_events=summarize(recent,aliases);history,historical_examples,_,_=summarize(historical,aliases)
 old,_,_,_=summarize([e for e in recent if e['date']<MID],aliases);new,_,_,_=summarize([e for e in recent if e['date']>=MID],aliases)
 reason='not_legal' if legality in ('not_legal','banned') else 'legality_unknown' if legality not in ('legal','restricted') else 'basic_land' if card.get('basic') or ('Basic' in card.get('type','').split() and 'Land' in card.get('type','')) else 'no_post_release_sample' if not observed['decks'] else None
 score=round(observed['sharePct'],4) if reason is None else None
 status='unavailable' if score is None else 'not_observed' if not observed['withCard'] else 'repeated' if observed['eventsWithCard']>=3 and observed['withCard']>=5 else 'first_sightings'
 delta=new['sharePct']-old['sharePct'] if new['decks']>=50 and old['decks']>=50 else None
 trend='insufficient_data' if delta is None else 'rising' if delta>=1 and new['withCard']>=3 else 'falling' if delta<=-1 and old['withCard']>=3 else 'stable'
 outlook='not_assessed' if score is None else 'watch' if observed['withCard'] and (trend=='rising' or status=='first_sightings') else 'repeated_use' if status=='repeated' else 'no_signal'
 return {'schemaVersion':1,'method':METHOD,'date':as_of,'score':score,'reason':reason,'status':status,'legality':legality,'eligibleFrom':None if eligible_from=='9999-12-31' else eligible_from,
  'sample':{'start':START,'end':as_of,'decks':observed.pop('decks'),'events':observed.pop('events')},'observed':observed,
  'trend':{'status':trend,'deltaPoints':round(delta,4) if delta is not None else None,'previous':{'decks':old['decks'],'withCard':old['withCard']},'recent':{'decks':new['decks'],'withCard':new['withCard']}},
  'outlook':{'status':outlook,'kind':'observational_signal_not_forecast'},'history':{'decks':history['decks'],'withCard':history['withCard'],'events':history['eventsWithCard'],'sharePct':round(history['sharePct'],4) if history['sharePct'] is not None else None},'eventsWithCard':seen_events,'examples':examples,'historicalExamples':historical_examples,'archetypes':[{'name':n,'decks':count} for n,count in archetypes]}

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
