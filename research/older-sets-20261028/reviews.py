"""Acquire attributed Limited ratings. Numeric ratings are never inferred from prose."""
import concurrent.futures, html, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from import_expansion_catalogs import write_json
from acquire import fetch
PREFIXES={'bloomburrow':'bloomburrow-blb','outlaws-of-thunder-junction':'outlaws-of-thunder-junction-otj','murders-at-karlov-manor':'murders-at-karlov-manor-mkm','lost-caverns-of-ixalan':'the-lost-caverns-of-ixalan-lci','wilds-of-eldraine':'wilds-of-eldraine'}
def clean(s):return html.unescape(re.sub('<[^>]+>','',s)).replace('’',"'").strip()
def run(slug,prefix):
 d=ROOT/'research'/f'{slug}-20261028'; audit=json.loads((d/'fetch-audit.json').read_text());out=ROOT/'expansions'/slug; catalog=json.loads((out/'cards.json').read_text())['cards'];names={clean(c['name']):c for c in catalog}; ratings={};rawrows=[];unmatched=[]
 topics=['white','blue','black','red','green','multicolored','artifacts-and-lands']
 if slug=='outlaws-of-thunder-junction':topics+=['breaking-news','the-big-score-and-special-guests']
 if slug=='wilds-of-eldraine':topics+=['enchanting-tales']
 for topic in topics:
  url=f'https://mtgazone.com/{prefix}-limited-set-review-{topic}/';raw=fetch(url,d/f'mtgazone-{topic}.html',audit['acquisitions'])
  if not raw:continue
  text=raw.decode('utf-8','replace');(d/f'mtgazone-{topic}.txt').write_text(clean(text),encoding='utf-8')
  # Each card heading owns only the section up to the next h2.
  for name,section in re.findall(r'<h2\b[^>]*>(.*?)</h2>(.*?)(?=<h2\b|\Z)',text,re.S|re.I):
   match=re.search(r'Rating:\s*(?:</?[^>]+>\s*)*([0-5](?:\.\d+)?)\s*/\s*5',section,re.I)
   if not match:continue
   name=clean(name);score=float(match[1]);rawrows.append({'name':name,'score':score,'scale':[0,5],'url':url,'author':'J2SJosh','context':'Limited','retrieved':'2026-10-28'})
   card=names.get(name)
   if not card:
    # Review heading may use only the face name of adventure/transform cards.
    card=next((c for c in catalog if clean(c['name'].split(' // ')[0])==name),None)
   if not card:unmatched.append(name);continue
   ratings[card['id']]={'score':score,'role':'Valutazione Limited attribuita','why':'Voto dell’autore sulla scala originale da 0 a 5. Leggi la recensione per condizioni e sinergie.','condition':'Giudizio editoriale della recensione, distinto da risultati di partite e da una priorità assoluta per il pool.','evidence':[{'author':'J2SJosh','original':str(score)+'/5','stars':score,'url':url,'kind':'Recensione Limited MTG Arena Zone','retrieved':'2026-10-28'}]}
  (d/f'mtgazone-{topic}.html').unlink()
 write_json(out/'ratings.json',{'date':'2026-10-28','cards':ratings,'coverage':{'rated':len(ratings),'catalogCards':len(catalog),'unmatchedNames':unmatched,'missingIds':[c['id'] for c in catalog if c['id'] not in ratings]},'method':'Trascrizione della scala originale Limited 0-5 MTG Arena Zone; nessuna interpolazione delle carte assenti.'})
 write_json(d/'mtgazone-ratings.json',{'cards':rawrows,'unmatchedNames':unmatched,'retrieved':'2026-10-28'});write_json(d/'fetch-audit.json',audit)
 sources=json.loads((out/'sources.json').read_text()); sources['research']['sources'] += [{'id':'mtgazone-'+t,'url':f'https://mtgazone.com/{prefix}-limited-set-review-{t}/','label':'Recensione Limited MTG Arena Zone '+t,'retrieved':'2026-10-28'} for t in topics];write_json(out/'sources.json',sources)
 print(slug,len(ratings),len(rawrows),len(unmatched),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda x:run(*x),PREFIXES.items()))
