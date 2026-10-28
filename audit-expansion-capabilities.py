"""Offline capability inventory for every registered set. Prints JSON, writes nothing."""
import json
from expansion_data import load_expansions


def inventory():
    return {'schemaVersion':1,'expansions':[
        {'id':expansion.manifest['id'],'name':expansion.manifest['name'],
         'catalogComplete':expansion.data['cards'].get('complete',False),
         'defaultEvents':expansion.runtime()['defaultEvents'],
         'features':expansion.availability,
         'events':{key:{'name':event['name'],'kind':event['kind'],'product':event['product'],
                        **expansion.event_availability(key)}
                   for key,event in expansion.data['limited']['events'].items()}}
        for expansion in load_expansions()]}


if __name__=='__main__':
    print(json.dumps(inventory(),ensure_ascii=False,indent=2))
