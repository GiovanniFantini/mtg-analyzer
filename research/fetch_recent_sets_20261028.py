"""Acquisizione riproducibile del gruppo di espansioni 2025-2026."""
import hashlib, json, pathlib, time, urllib.request, urllib.error
DATE='2026-10-28'
ROOT=pathlib.Path(__file__).resolve().parent.parent
SETS=[('the-hobbit','hob',['hoc']),('marvel-super-heroes','msh',['mar','msc']),('secrets-of-strixhaven','sos',['soa','soc']),('teenage-mutant-ninja-turtles','tmt',['pza','tmc']),('lorwyn-eclipsed','ecl',['ecc']),('avatar-the-last-airbender','tla',['tle'])]
def acquire(url, dest, audit):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'MTGAnalyzer/1.0 research','Accept':'application/json,text/html;q=0.9,*/*;q=0.8'})
        with urllib.request.urlopen(req,timeout=90) as response: raw=response.read()
        dest.write_bytes(raw)
        audit.append({'url':url,'retrieved':DATE,'file':dest.name,'status':'acquired','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        time.sleep(.12)
        return raw
    except Exception as exc:
        audit.append({'url':url,'retrieved':DATE,'status':'failed','error':str(exc)})
        return None
def main():
    for slug, code, related in SETS:
        folder=ROOT/'research'/f'{slug}-20261028'; folder.mkdir(exist_ok=True)
        audit=[]
        for current in [code]+related:
            raw=acquire('https://api.scryfall.com/sets/'+current,folder/f'scryfall-{current}-set.json',audit)
            if not raw: continue
            meta=json.loads(raw); url=meta['search_uri']; cards=[]; page=0
            while url:
                page+=1; raw=acquire(url,folder/f'scryfall-{current}-page-{page}.json',audit)
                if not raw: break
                data=json.loads(raw); cards.extend(data.get('data',[])); url=data.get('next_page') if data.get('has_more') else None
            (folder/f'scryfall-{current}-cards.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2),encoding='utf-8')
            print(slug,current,len(cards),flush=True)
        draft_code='tmnt' if code=='tmt' else code
        for key,url in [('collecting',f'https://magic.wizards.com/en/news/feature/collecting-{slug}'),('mechanics',f'https://magic.wizards.com/en/news/feature/{slug}-mechanics'),('product',f'https://magic.wizards.com/en/products/{slug}'),('draft-guide',f'https://draftsim.com/mtg-{draft_code}-draft-guide/'),('sealed-guide',f'https://draftsim.com/mtg-{draft_code}-sealed-guide/'),('limited-review',f'https://draftsim.com/mtg-{draft_code}-limited-set-review/')]:
            acquire(url,folder/f'{key}.html',audit)
        (folder/'fetch-audit.json').write_text(json.dumps({'date':DATE,'acquisitions':audit},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__': main()
