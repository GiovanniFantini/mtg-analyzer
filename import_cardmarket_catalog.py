"""Normalize an offline capture of visible Cardmarket catalog rows.

From is a product minimum in EUR with finishFilter=any. Product rows do not
identify a Scryfall printing or certify nonfoil/foil prices. No network calls.
"""
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

def key(name):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower())

def dump(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def integrate(capture_path, expansion_path):
    capture_path=Path(capture_path);expansion_path=Path(expansion_path)
    capture=json.loads(capture_path.read_text(encoding='utf-8-sig'))
    date=capture.get('retrieved',capture.get('date'))
    if not date:raise ValueError('Data della rilevazione mancante')
    if capture.get('finishFilter','any')!='any':raise ValueError('Questo importatore supporta soltanto listini From senza filtro finitura')
    cards_doc=json.loads((expansion_path/'cards.json').read_text(encoding='utf-8-sig'))
    catalog=cards_doc['cards'];catalog_set=capture.get('catalogSet')
    if catalog_set:catalog_set=catalog_set.upper()
    lookup={}
    for card in catalog:
        names=[card['name'],card.get('oracleName',''),card.get('printedName','')]+[f['name'] for f in card.get('faces',[])]
        for name in names:
            if name:lookup.setdefault(key(name),{})[card['id']]=card
    observed={};unmatched=[];products=[];seen=set()
    for page in capture.get('pages',[]):
        for row in page.get('rows',[]):
            url=row.get('href',row.get('url',''))
            if url in seen:continue
            seen.add(url)
            if not url.startswith('https://www.cardmarket.com/'):raise ValueError('Provenienza diversa da Cardmarket')
            text=row.get('text','')
            name=row.get('name') or next((s.strip() for s in text.splitlines() if s.strip()),'')
            variant=re.search(r'\s*\(V\.\s*(\d+)\)\s*$',name)
            base_name=re.sub(r'\s*\(V\.\s*\d+\)\s*$','',name)
            price_match=re.search(r'From\s+([0-9][0-9.,\s]*)\s*€',text)
            amount=None
            if price_match:
                amount=float(price_match.group(1).replace(' ','').replace('.','').replace(',','.'))
            candidates=list(lookup.get(key(base_name),{}).values())
            if catalog_set:
                candidates=[c for c in candidates if c['set']==catalog_set]
            observation={'name':name,'from':amount,'currency':'EUR','metric':'From','finishFilter':'any','nonfoil':None,'foil':None,'date':date,'source':'Cardmarket','url':url,'listingUrl':page.get('url'),'variant':variant.group(1) if variant else None,'printingId':None,'filters':{'language':'any, non filtrata','condition':'any, non filtrata','sellerCountry':'any, non filtrato','shippingIncluded':False},'limitations':['Minimo del prodotto nel listino; finitura e corrispondenza alla singola stampa Scryfall non certificate.']}
            products.append(observation)
            if len(candidates)!=1:
                unmatched.append({'name':name,'url':url,'candidateIds':[c['id'] for c in candidates],'reason':'Nome non abbinato' if not candidates else 'Identità ambigua'})
                continue
            card=candidates[0]
            observed.setdefault(card['id'],{'catalogId':card['id'],'name':card['name'],'observations':[]})['observations'].append(observation)
    for row in observed.values():
        base=[o for o in row['observations'] if o['variant'] is None]
        # Do not collapse distinct variants into an invented canonical-print price.
        row['from']=base[0]['from'] if len(base)==1 else None
        row.update(nonfoil=None,foil=None,finishFilter='any',printingId=None)
    prices=json.loads((expansion_path/'prices.json').read_text(encoding='utf-8-sig'))
    prices['references']={'available':bool(observed),'date':date,'source':'Cardmarket','currency':'EUR','metric':'From','finishFilter':'any','cards':observed,'coverage':{'catalogCards':len(catalog),'matchedCards':len(observed),'productRows':len(products),'observedPages':len(capture.get('pages',[])),'missingCatalogIds':[c['id'] for c in catalog if c['id'] not in observed],'unmatchedProducts':unmatched},'limitations':['Acquisizione del listino principale; varianti, bonus e finiture possono richiedere listini separati.','Il minimo From non è un prezzo nonfoil o foil e non rende disponibile il valore atteso del box.'],'inputSha256':hashlib.sha256(capture_path.read_bytes()).hexdigest()}
    dump(expansion_path/'prices.json',prices)
    sources=json.loads((expansion_path/'sources.json').read_text(encoding='utf-8-sig'))
    source_id='cardmarket-browser-catalog'
    urls=[p['url'] for p in capture.get('pages',[]) if p.get('url')]
    sources.setdefault('links',{})[source_id]=urls[0] if urls else 'https://www.cardmarket.com/en/Magic'
    source={'id':source_id,'label':'Cardmarket: listino From acquisito nel browser','url':urls[0] if urls else 'https://www.cardmarket.com/en/Magic','retrieved':date,'status':'acquired_and_integrated' if observed else 'blocked_or_empty','coverage':prices['references']['coverage'],'metric':'From','currency':'EUR','finishFilter':'any'}
    sources.setdefault('research',{}).setdefault('sources',[])
    sources['research']['sources']=[s for s in sources['research']['sources'] if s.get('id')!=source_id]+[source]
    dump(expansion_path/'sources.json',sources)
    result={'date':date,'cards':len(observed),'products':len(products),'unmatched':len(unmatched),'coverage':prices['references']['coverage']}
    dump(capture_path.with_name(capture_path.stem+'-normalized.json'),result)
    return {k:result[k] for k in ['cards','products','unmatched']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture',type=Path);parser.add_argument('--expansion',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(integrate(args.capture,args.expansion),ensure_ascii=False))
