"""Aggiorna guide e metadati di pubblicazione senza sovrascrivere prezzi."""
import html,json,pathlib,re,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent))
from import_expansion_catalogs import write_json
from enrich_recent_sets_20261028 import ROOT,DATE,SETS,blocks
MONTHS={name:i+1 for i,name in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'])}
def iso(text):
 match=re.search(r'('+'|'.join(MONTHS)+r') (\d{1,2}), (\d{4})',text)
 return f'{match[3]}-{MONTHS[match[1]]:02}-{int(match[2]):02}' if match else None
for slug,code,_ in SETS:
 dest=ROOT/'expansions'/slug;folder=ROOT/'research'/f'{slug}-20261028'
 source_doc=json.loads((dest/'sources.json').read_text(encoding='utf8'))
 for filename in ['draft-guide.html','sealed-guide.html','limited-review.html']:
  path=folder/filename
  if not path.exists():continue
  content=blocks(path);authorline=next((t for tag,t in content if tag=='h1' and re.search(r'\d{4} Deckbuilding',t)),'')
  published=iso(authorline);updated=next((iso(t) for _,t in content if t.startswith('Last updated on ')),None)
  for source in source_doc['research']['sources']:
   if source['id']==path.stem:
    source.update(author='Andrew Quinn' if filename=='limited-review.html' else 'Bryan Hohns (Veveil)',published=published,updated=updated,coverage='Abbinamento esatto dei titoli di carta; voti numerici singoli estratti dalla recensione Limited.' if filename=='limited-review.html' else 'Guida letta per le sintesi degli archetipi; riferimenti per carta abbinati separatamente.')
  if filename=='limited-review.html':
   ratings=json.loads((dest/'ratings.json').read_text(encoding='utf8'))
   for row in ratings['cards'].values():
    for evidence in row.get('evidence',[]):evidence.update(published=published,updated=updated)
   write_json(dest/'ratings.json',ratings)
 write_json(dest/'sources.json',source_doc)
 archetypes=json.loads((dest/'archetypes.json').read_text(encoding='utf8'));guides=json.loads((dest/'guides.json').read_text(encoding='utf8'))
 fragments=guides['fragments'];fragments['draft.examples']='<section class="trk-panel"><h2>Piani Limited dalla ricerca</h2><p>Sintesi editoriali delle guide Draftsim di Bryan Hohns, distinte dai voti iniziali di Andrew Quinn e da risultati osservati.</p>'+''.join('<h3>'+html.escape(pair+' · '+archetype['theme'])+'</h3><p>'+html.escape(archetype['plan'])+'</p>'+('<p>Carte da esaminare: '+html.escape(', '.join(archetype['core']))+'.</p>' if archetype['core'] else '') for pair,archetype in archetypes.items())+'<p><a href="'+html.escape(source_doc['links'].get('draft-guide','fonti.html'))+'">Consulta la guida originale e le sue revisioni.</a></p></section>'
 fragments['rules.panel-1']='<section class="trk-panel"><h2>Meccaniche e perimetro delle carte</h2><p>Le carte aggiuntive mantengono le proprie legalità. Le carte Commander e degli altri prodotti collegati non entrano automaticamente nel pool di un evento.</p><p><a href="'+html.escape(source_doc['links'].get('mechanics','fonti.html'))+'">Guida ufficiale alle meccaniche</a>. <a href="'+html.escape(source_doc['links'].get('collecting','fonti.html'))+'">Composizione ufficiale dei prodotti</a>.</p></section>'
 write_json(dest/'guides.json',guides)
 printing_doc=json.loads((dest/'printings.json').read_text(encoding='utf8'));excluded=[p['id'] for p in printing_doc['cards'] if 'paper' not in p.get('games',[])]
 products=json.loads((dest/'products.json').read_text(encoding='utf8'));products['products']['play']['published'].update(paperExcludedDigitalPrintingIds=excluded,scopeNote='Catalogo esteso alle piattaforme documentate, distinto dal pool cartaceo. Le stampe solo digitali sono escluse dal prodotto cartaceo. Il catalogo TLE può comprendere anche prodotti diversi dai Play Booster.')
 write_json(dest/'products.json',products)
 cards=json.loads((dest/'cards.json').read_text(encoding='utf8'))['cards'];source_ids={s['id'] for s in source_doc['research']['sources']};count=0
 for card in cards:
  prospect=card.get('prospects')
  if not prospect:continue
  required=['date','kind','summary','gameplayReview','sources','oracle','formats','tournamentObservations','commanderObservations','price','limitations']
  assert all(k in prospect for k in required),card['name']
  assert set(prospect['sources'])<=source_ids,card['name']
  assert all(k in prospect['price'] for k in ['date','currency','metric','printingId','nonfoil','foil','comparison','variants','outlook']),card['name']
  count+=1
 print(slug,'prospects required fields/source IDs valid',count,flush=True)
