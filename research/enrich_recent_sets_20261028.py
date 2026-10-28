"""Importazione offline e arricchimenti documentati, senza inferire collazione."""
import concurrent.futures, html, json, pathlib, re, sys, urllib.parse
from html.parser import HTMLParser
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from import_expansion_catalogs import create_expansion,write_json,normalize_printing
from fetch_recent_sets_20261028 import SETS,acquire,ROOT,DATE
NAMES=['Magic: The Gathering | Lo Hobbit','Magic: The Gathering | Marvel Super Heroes','I Segreti di Strixhaven','Magic: The Gathering | Teenage Mutant Ninja Turtles','Eclissi di Lorwyn','Magic: The Gathering | Avatar: La leggenda di Aang']
class Blocks(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0;self.current=[];self.blocks=[];self.kind=None
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('h1','h2','h3','h4','h5','p','li'):
            self.flush();self.kind=tag
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if tag in ('h1','h2','h3','h4','h5','p','li'): self.flush()
    def handle_data(self,data):
        if not self.skip:self.current.append(data)
    def flush(self):
        text=' '.join(' '.join(self.current).split());self.current=[]
        if text:self.blocks.append((self.kind,text))
def blocks(path):
    parser=Blocks();parser.feed(path.read_text(encoding='utf8'));parser.flush();return parser.blocks
def key(value):return re.sub(r'[^a-z0-9]','',value.lower())
def supplement(item):
    slug,code,related=item; folder=ROOT/'research'/f'{slug}-20261028';audit=[]
    # Statistical API responses are not downloaded for redistribution. Consult
    # the provider's public datasets and usage terms before any future import.
    urls=[('17lands-usage','https://www.17lands.com/usage_guidelines'),('cardmarket',f'https://www.cardmarket.com/en/Magic/Expansions/{"The-Hobbit" if code=="hob" else "-".join(w.title() for w in slug.split("-"))}'),('edhrec',f'https://edhrec.com/sets/{code}'),('mtggoldfish',f'https://www.mtggoldfish.com/sets/{"+".join(w.title() for w in slug.split("-"))}'),('mtgdecks',f'https://mtgdecks.net/prices/{code}'),('untapped',f'https://mtga.untapped.gg/limited/draft/{slug}/card-data'),('cardkingdom',f'https://blog.cardkingdom.com/{slug}-draft-guide/'),('mtgazone-archetypes',f'https://mtgazone.com/{slug}-{code}-limited-archetypes-guide-and-example-decks/'),('cardsrealm',f'https://mtg.cardsrealm.com/en-us/sets/{code}-{slug}')]
    for label,url in urls: acquire(url,folder/(label+('.json' if label=='17lands-card-data' else '.html')),audit)
    write_json(folder/'supplemental-fetch-audit.json',{'date':DATE,'acquisitions':audit})
    return slug
def integrate(index,item):
    slug,code,related=item;folder=ROOT/'research'/f'{slug}-20261028';dest=ROOT/'expansions'/slug
    primary=json.loads((folder/f'scryfall-{code}-cards.json').read_text(encoding='utf8'))
    extra_codes={'msh':['mar'],'sos':['soa','spg'],'tmt':['pza'],'tla':['tle'],'ecl':['spg']}.get(code,[])
    # TLE contains both source-material and non-Limited scene cards. Retain all
    # printings in catalog with explicit scope, not as certified booster groups.
    for extra in extra_codes:primary+=json.loads((folder/f'scryfall-{extra}-cards.json').read_text(encoding='utf8'))
    meta=json.loads((folder/f'scryfall-{code}-set.json').read_text(encoding='utf8'))
    audit=json.loads((folder/'fetch-audit.json').read_text(encoding='utf8'))['acquisitions']
    corrected=folder/'corrected-draftsim-audit.json'
    if corrected.exists():
        corrected_rows=json.loads(corrected.read_text(encoding='utf8'));audit=[r for r in audit if r.get('file') not in {r.get('file') for r in corrected_rows}]+corrected_rows
    supplement_path=folder/'supplemental-fetch-audit.json'
    if supplement_path.exists():audit+=json.loads(supplement_path.read_text(encoding='utf8'))['acquisitions']
    sources=[{'id':'scryfall-'+code,'url':'https://api.scryfall.com/sets/'+code,'label':'Scryfall: catalogo e Oracle','retrieved':DATE,'status':'acquired','coverage':'Tutte le pagine del catalogo delle stampe, varianti incluse.'}]
    for row in audit:
        if row['url'].startswith('https://api.scryfall.com'):continue
        ident=pathlib.Path(row.get('file',urllib.parse.urlparse(row['url']).path.split('/')[-1])).stem
        if any(s['id']==ident for s in sources):continue
        sources.append({'id':ident,'url':row['url'],'label':ident,'retrieved':DATE,'status':row['status'],'limitation':row.get('error','Una pagina acquisita non implica analisi completa di tutti i contenuti.')})
    if not dest.exists():create_expansion(slug,NAMES[index],code,primary,complete=False,release_date=meta['released_at'],sources=sources)
    catalog=json.loads((dest/'cards.json').read_text(encoding='utf8'));cards=catalog['cards']
    printing_doc=json.loads((dest/'printings.json').read_text(encoding='utf8'));printings=printing_doc['cards'];known={p['id'] for p in printings}
    for raw in primary:
        if raw['id'] in known:continue
        card=next((c for c in cards if c['set']==raw['set'].upper() and c.get('oracleId')==raw.get('oracle_id')),None)
        if card is None:card=normalize_printing(raw);card['prints']=[];cards.append(card)
        printing=normalize_printing(raw);printing['catalogId']=card['id'];printings.append(printing);known.add(raw['id'])
        card['prints'].append({'id':printing['id'],'number':printing['number'],'image':printing['image'],'finishes':printing['finishes'],'url':printing['url'],'set':printing['set']})
    catalog['print_count']=len(printings);catalog['coverage']['sets']=sorted({c['set'] for c in cards});write_json(dest/'cards.json',catalog);write_json(dest/'printings.json',printing_doc)
    lookup={key(c['name']):c for c in cards}
    for c in cards:
        for face in c.get('faces',[]):lookup[key(face['name'])]=c
    observations={}; matched=[];ratings={}
    for filename in ['draft-guide.html','sealed-guide.html','limited-review.html']:
        path=folder/filename
        if not path.exists():continue
        heading=None
        for tag,text in blocks(path):
            if tag in ('h2','h3','h4','h5'):
                candidate=re.sub(r'^#?\d+\.\s*','',text);candidate=re.sub(r'\s*\([^)]*\)\s*$','',candidate)
                heading=lookup.get(key(candidate))
                if heading:
                    observations.setdefault(heading['id'],{'tone':'condizionato','breadth':'Recensione Limited attribuita, copertura parziale','summary':'La fonte contiene una valutazione specifica della carta. Consulta il testo originale per contesto e condizioni.','sources':[]})
                    source=next((r['url'] for r in audit if r.get('file')==filename),'')
                    author='Andrew Quinn' if filename=='limited-review.html' else 'Bryan Hohns (Veveil)'
                    entry={'id':path.stem,'label':'Draftsim, '+author+': '+path.stem,'url':source,'kind':'Limited','retrieved':DATE,'heading':text}
                    if entry not in observations[heading['id']]['sources']:observations[heading['id']]['sources'].append(entry)
                    matched.append({'catalogId':heading['id'],'name':heading['name'],'source':source,'heading':text})
            elif heading and tag=='p' and filename=='limited-review.html':
                rating=re.fullmatch(r'Rating:\s*([0-9]+(?:\.[0-9]+)?)/10',text)
                if rating:
                    original=float(rating.group(1));score=original/2
                    ratings[heading['id']]={'score':score,'why':f'Recensione Limited Draftsim: {original:g}/10. Scala originale conservata; conversione lineare nella scala 0-5 del sito.','condition':'Valutazione iniziale della fonte, distinta da risultati osservati e dalle revisioni successive della guida Draft.','evidence':[{'author':'Andrew Quinn','original':f'{original:g}/10','stars':score,'url':source,'kind':'Recensione Limited, voto iniziale','retrieved':DATE,'scale':{'min':0,'max':10,'conversion':'score = original / 2'}}]}
                    observations[heading['id']]['summary']=f'Draftsim assegna {original:g}/10 nella recensione Limited iniziale. Le osservazioni della guida successiva possono aggiornare questa valutazione.'
                    observations[heading['id']]['tone']='positivo' if original>=7 else 'negativo' if original<=3 else 'condizionato'
    write_json(dest/'sentiment.json',{'meta':{'isoDate':DATE,'covered':len(observations),'method':'Abbinamento esatto di titoli di recensioni a nomi Oracle, senza assegnare voti o ricopiare il testo delle recensioni.'},'cards':observations})
    write_json(dest/'ratings.json',{'date':DATE,'method':'Voti originali Draftsim 0-10 convertiti linearmente in 0-5; nessuna stima per carte senza voto numerico singolo. Data di acquisizione distinta dalla pubblicazione.','cards':ratings})
    # Preserve the official published product wording in the research snapshot.
    # HTML is source evidence; only concise factual summaries enter site datasets.
    collecting=blocks(folder/'collecting.html');product_lines=[];active=False
    for tag,text in collecting:
        if tag in ('h2','h3') and text=='Play Boosters':active=True
        elif active and tag in ('h2','h3') and text in ('Collector Boosters','Box Toppers','Bundles','Commander Decks','Jumpstart Boosters','Gift Bundles','Draft Night'):break
        elif active:product_lines.append(text)
    write_json(folder/'published-play-booster-contents.json',{'source':f'https://magic.wizards.com/en/news/feature/collecting-{slug}','retrieved':DATE,'statements':product_lines,'collationExecutable':False,'limitation':'Percentuali arrotondate e limiti <1% non definiscono una ricetta esatta; eleggibilità di singole stampe da abbinare.'})
    write_json(dest/'products.json',{'schemaVersion':1,'products':{'play':{'name':'Play Booster','packSize':14,'tokensIncluded':False,'collation':None,'published':{'date':DATE,'source':f'https://magic.wizards.com/en/news/feature/collecting-{slug}','catalogCodes':[code.upper()]+[x.upper() for x in extra_codes],'snapshot':str(folder.relative_to(ROOT)/'published-play-booster-contents.json').replace('\\','/')},'missing':['Abbinamento completo delle stampe ai singoli slot e verifica delle probabilità arrotondate o pubblicate come limite.']}}})
    events={}
    for event,kind,packs,seats,picks in [('draft','draft',3,8,1),('sealed','sealed',6,1,0)]:
        events[event]={'id':code+'-play-'+event,'name':NAMES[index]+' · '+event.title(),'kind':kind,'product':'play','packsPerPlayer':packs,'seats':seats,'picksPerTurn':picks,'directions':[1,-1,1] if picks else [],'minDeckSize':40,'maxCopies':None,'extraBasicLands':True,'mulligan':{'kind':'london','handSize':7,'freeMulligans':0},'sources':['https://magic.wizards.com/en/formats/'+('booster-draft' if picks else 'sealed-deck')]}
    write_json(dest/'limited.json',{'schemaVersion':1,'events':events})
    write_json(dest/'sources.json',{'date':DATE,'links':{s['id']:s['url'] for s in sources},'research':{'date':DATE,'sources':sources}})
    write_json(folder/'matched-review-observations.json',{'date':DATE,'observations':matched,'catalogCards':len(cards),'coveredCards':len(observations),'missingCards':[c['id'] for c in cards if c['id'] not in observations]})
    print(slug,len(cards),len(observations),'review matches',flush=True)
if __name__=='__main__':
    if '--fetch' in sys.argv:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            for slug in executor.map(supplement,SETS):print(slug,'supplement acquired',flush=True)
    else:
        for index,item in enumerate(SETS):integrate(index,item)
