"""Acquire external card identities for previews only, outside playable catalogs."""
import json,time,urllib.request,urllib.parse
from pathlib import Path
OUT=Path(__file__).resolve().parent
names=['Birthing Ritual','Scapeshift','Academy Manufactor',"Agatha's Soul Cauldron",'Gor Muldrak, Amphinologist','Food Chain','Life from the Loam','Planar Nexus']
rows=[]
for name in names:
 url='https://api.scryfall.com/cards/named?'+urllib.parse.urlencode({'exact':name})
 request=urllib.request.Request(url,headers={'User-Agent':'MTG-Analyzer-Research/1.0','Accept':'application/json'})
 with urllib.request.urlopen(request,timeout=30) as response:d=json.load(response)
 rows.append(dict(id=d['id'],oracleId=d['oracle_id'],name=d['name'],full=d['name'],image=d.get('image_uris',{}).get('normal'),url=d['scryfall_uri'],type=d['type_line'],oracle=d.get('oracle_text',''),colors=d.get('colors',[]),faces=d.get('card_faces',[])))
 time.sleep(.15)
(OUT/'preview-references.json').write_text(json.dumps(dict(date='2026-11-07',source='Scryfall API exact-name lookup',cards=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Preview-only cards',len(rows))
