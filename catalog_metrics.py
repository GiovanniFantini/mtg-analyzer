"""Catalog-only views of observed WR snapshots; populations are never averaged."""

def catalog_performance(statistics):
    result={}
    for kind in ('draft','sealed'):
        snapshots=[]
        for key,snapshot in (statistics.get(kind) or {}).get('externalSources',{}).items():
            metric=snapshot.get('metrics',{}).get('inHandWinRate',{})
            if metric.get('status')!='public' or metric.get('unit')!='percent':continue
            public_games=snapshot.get('metrics',{}).get('games',{}).get('status')=='public'
            snapshots.append({'id':key,'provider':snapshot['provider'],'retrieved':snapshot['retrieved'],
                'url':snapshot['url'],'filters':snapshot.get('filters',{}),'metric':metric['label'],
                'limitations':snapshot.get('limitations',[]),'derivation':snapshot.get('derivation'),
                'cards':{row['catalogId']:{'value':row['metrics']['inHandWinRate'],
                  'games':row['metrics'].get('games') if public_games else None,'url':row.get('sourceUrl',snapshot['url'])} for row in snapshot['cards']}})
        # Preserve the existing Untapped WR default and its deep links.
        snapshots.sort(key=lambda s:(s['id']!='untapped',s['id']))
        result[kind]=snapshots
    return result
