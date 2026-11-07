"""Integrate dated TRK factual snapshots offline, preserving unrelated evidence."""
import copy
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'research/star-trek-20261107'
BASE=ROOT/'expansions/star-trek'
DATE='2026-11-07'
ORIGIN='research-update-20261107'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def key(s):return ''.join(c for c in s.casefold() if c.isalnum())
def main():
 catalog=load(BASE/'cards.json');cards=catalog['cards'];names={key(c['name']):c for c in cards}
 baseline=load(OUT/'baseline-evidence.json')
 baseline_notes=load(OUT/'baseline-format-notes.json')
 formats=load(OUT/'format-notes.json')
 affected={(key(name),fmt) for s in formats['sources'] for name in s['notes'] for fmt in s['formats']}
 sources=load(BASE/'sources.json');statistics=load(BASE/'statistics.json');ratings=load(BASE/'ratings.json');guides=load(BASE/'guides.json')
 migrated=sources['research'].get('evidenceMigrationVersion',0)>=1
 notes_migrated=sources['research'].get('noteMigrationVersion',0)>=1
 raw_catalog=load(OUT/'scryfall.json')['data']
 added_print_ids={r['printingId'] for r in load(OUT/'printing-updates.json')['added']}
 for c in cards:
  known={str(p['number']) for p in c['prints']}
  for r in raw_catalog:
   if r['oracle_id']==c['id'] and r['set'].upper()==c['set'] and r['collector_number'] not in known:
    printing=dict(number=r['collector_number'],printingId=r['id'],url=r['scryfall_uri'].split('?')[0],image=r.get('image_uris',{}).get('normal'),finishes=r['finishes'],frame_effects=r.get('frame_effects',[]),promo_types=r.get('promo_types',[]))
    c['prints'].append(printing);known.add(r['collector_number'])
   elif r['oracle_id']==c['id'] and r['id'] in added_print_ids:
    next(p for p in c['prints'] if str(p['number'])==r['collector_number']).update(printingId=r['id'],url=r['scryfall_uri'].split('?')[0])
 catalog['print_count']=sum(len(c['prints']) for c in cards)
 catalog['date']=DATE;catalog['printingCoverage']['observed']=catalog['print_count']
 assert catalog['print_count']==len(raw_catalog),'Unresolved printing difference'
 sources['research']['coverage']['printings']=catalog['print_count']
 latest_catalog='research/star-trek-20261107/catalog.json'
 if sources['research']['catalogSnapshot']!=latest_catalog:sources['research']['previousCatalogSnapshot']=sources['research']['catalogSnapshot']
 sources['research']['catalogSnapshot']=latest_catalog
 sources['research']['rawSnapshot']='research/star-trek-20261107/scryfall.json'
 owned_sources={s['id'] for s in sources['research']['sources'] if s.get('origin')==ORIGIN}
 for c in cards:
  p=c['prospects'];p['researchNotes']=[n for n in p.get('researchNotes',[]) if n.get('origin')!=ORIGIN]
  p['sources']=[s for s in p['sources'] if s not in owned_sources]
  for fmt,entry in p['formats'].items():
   if entry.get('researchEvidenceOrigin')==ORIGIN:
    previous=entry.pop('researchEvidencePrevious');entry.pop('researchEvidenceOrigin')
    if entry['evidence']=='recensione':entry['evidence']=previous
   # Migrate the initial import to the reversible evidence contract.
   elif not migrated and (key(c['name']),fmt) in affected:
    entry['evidence']=baseline[c['id']][fmt]
 def note(c,source,formats,finding,context,url=None,**extra):
  p=c['prospects'];p['researchNotes'].append(dict(origin=ORIGIN,source=source,formats=formats,finding=finding,context=context,date=DATE,**({'url':url} if url else {}),**extra))
  p['sources']=sorted(set(p['sources']+[source]))
 registry=[s for s in sources['research']['sources'] if s.get('origin')!=ORIGIN]
 audit=load(OUT/'source-audit.json')
 by_source={s['id']:s for s in audit['sources']}
 for kind in ('draft','sealed'):
  snapshot=load(OUT/f'untapped-{kind}.json')
  statistics.setdefault(kind,{}).setdefault('externalSources',{})['untapped']=snapshot
  registry.append(dict(id=f'untapped-{kind}-20261107',origin=ORIGIN,publisher='Untapped.gg',url=snapshot['url'],retrieved=DATE,context=snapshot['filters']['event'],coverage=snapshot['coverage']))
  by_metric={r['catalogId']:r for r in snapshot['cards']}
  for c in cards:
   entry=c['prospects']['formats'][kind]
   row=by_metric.get(c['id'])
   if not notes_migrated:entry['researchNotePrevious']=baseline_notes[c['id']][kind]
   elif 'researchNotePrevious' not in entry:entry['researchNotePrevious']=entry.get('note','')
   if entry.get('researchRenderedNote') and entry.get('note')!=entry['researchRenderedNote']:entry['researchNotePrevious']=entry.get('note','')
   original_note=entry['researchNotePrevious'].replace('; nessuna WR TRK importata.','.')
   entry['note']=original_note+' Aggiornamento del 7 novembre: '+('WR in mano early access Untapped del 4 novembre disponibile nel catalogo.' if row and row['metrics']['inHandWinRate'] is not None else 'nessuna WR in mano per questa carta nell’early access Untapped del 4 novembre.')
   entry['researchRenderedNote']=entry['note']
 pick=load(OUT/'untapped-pick-order.json')
 for r in ratings['cards'].values():r.pop('untappedPickOrder',None)
 for row in pick['cards']:
  ratings['cards'].setdefault(row['catalogId'],{})['untappedPickOrder']={**{k:row[k] for k in ('tier','tierOrder','status','url')},'retrieved':DATE,'filters':pick['filters']}
 sources.setdefault('externalRankings',{})['untappedPickOrder']={k:pick[k] for k in ('provider','url','retrieved','filters','coverage','limitations','inputSha256')}
 registry.append(dict(id='limitedlibrary-20261107',origin=ORIGIN,publisher='Limited Library',url='https://limitedlibrary.com/sets/star-trek/',retrieved=DATE,context='Aggregatore di voti attribuiti. Video originali collegati, non verificati tramite trascrizione indipendente.',inputSha256=load(OUT/'attributed-grades.json')['captureSha256']))
 grades=load(OUT/'attributed-grades.json')
 by_id={c['id']:c for c in cards}
 refreshed=load(OUT/'draftsim-review-refresh.json')
 changed_review_ids={r['catalogId'] for r in refreshed['changedScores']}
 registry.append(dict(id='draftsim-trk-limited-20261107',origin=ORIGIN,publisher='Draftsim',author=refreshed['author'],published=refreshed['published'],retrieved=DATE,url=refreshed['url'],coverage=len(refreshed['cards']),context=refreshed['context'],captureSha256=refreshed['captureSha256']))
 for row in refreshed['cards']:
  c=by_id[row['catalogId']]
  for review in c['prospects'].get('limitedReviews',[]):
   if review['author']==refreshed['author'] and review['url']==refreshed['url']:
    review.update(value=row['value'],scaleMax=row['scaleMax'],source='draftsim-trk-limited-20261107',date=DATE,published=refreshed['published'])
    if c['id'] in changed_review_ids:
     old=next(r for r in load(OUT/'draftsim-review-baseline.json')['cards'] if r['catalogId']==c['id'])
     review['previousReading']=dict(value=old['value'],date='2026-11-03',source='research/star-trek-limited-20261103/draftsim-reviews.json')
  c['prospects']['sources']=sorted(set(c['prospects']['sources']+['draftsim-trk-limited-20261107']))
  for evidence in ratings['cards'].get(c['id'],{}).get('evidence',[]):
   if evidence.get('author')==refreshed['author'] and evidence.get('url')==refreshed['url']:
    if c['id'] in changed_review_ids:
     old=next(r for r in load(OUT/'draftsim-review-baseline.json')['cards'] if r['catalogId']==c['id'])
     evidence['previousReading']=dict(value=old['value'],scaleMax=10,date='2026-11-03',source='research/star-trek-limited-20261103/draftsim-reviews.json')
    evidence.update(original=f"{row['value']}/10",stars=row['value']/2,retrieved=DATE)
 for row in grades['cards']:
  note(by_id[row['catalogId']],'limitedlibrary-20261107',['draft'],f"{row['author']}: {row['grade']}. Voto esplicito riportato da Limited Library, aggiornato al {row['sourceUpdated']}; scala originale conservata, senza conversione numerica. Il video originale non è stato trascritto indipendentemente. Non è un voto Sealed distinto.",'Recensione Limited',row['url'],author=row['author'],originalGrade=row['grade'],sourceUpdated=row['sourceUpdated'],attribution='secondary_aggregator')
 community=load(OUT/'community-grades.json')
 registry.append(dict(id='community-grades-20261107',origin=ORIGIN,publisher='myLimitedGrades',url=community['url'],retrieved=DATE,context='Aggregati Community, non voti di esperti o statistiche di partite',coverage=community['coverage']))
 for row in community['cards']:
  if row['grade'] is not None:
   note(by_id[row['catalogId']],'community-grades-20261107',['draft'],f"Community: {row['grade']} da {row['raters']} valutatori. Campione di opinioni ridotto, non recensione esperta né WR.",'Opinioni della Community',row['url'],author='Community myLimitedGrades',originalGrade=row['grade'],raters=row['raters'],attribution='community_aggregate')
 for source in formats['sources']:
  source_audit=by_source[source['id'].removesuffix('-20261107')]
  registry.append({**{k:v for k,v in source.items() if k!='notes'},'origin':ORIGIN,'retrieved':DATE,'captureSha256':source_audit['sha256']})
  for name,finding in source['notes'].items():
   c=names[key(name)]
   note(c,source['id'],source['formats'],finding,' / '.join(source['formats'])+' · '+source['author']+' · opinione prima dell’uscita',source['url'])
   for fmt in source['formats']:
    entry=c['prospects']['formats'][fmt]
    if entry['evidence']=='non_documentata':
     entry['researchEvidencePrevious']=entry['evidence'];entry['researchEvidenceOrigin']=ORIGIN;entry['evidence']='recensione'
 # Modern scenarios are editorial analysis grounded in the catalog, never tournament results.
 modern={
  'Salt Vampire':'Per Birthing Ritual o blink, il valore è ripetere l’interferenza con la mano. Non ha flash e l’avversario pesca subito: non è uno scarto netto né una risposta affidabile a una combo già in pila.',
  'Genesis Device':'Il tutor iniziale sviluppa mana, ma il piano simile a Scapeshift richiede altri cinque mana, tap e tempistica da stregoneria. In Modern va giustificato rispetto alle opzioni più rapide; nessun risultato TRK acquisito.',
  'Federation Resupply':'Trova Aura, Equipment o Spacecraft. Beam me up offre un secondo uso restituendo una creatura, ma costa quattro: il vantaggio nel tutor rispetto alle alternative di Hammer deve compensare questo investimento.',
  'Tea, Earl Grey, Hot':'Candidata soltanto a un piano che riusi gli ingressi degli artefatti e sfrutti il danno. Pescare all’ingresso non dimostra che sia abbastanza efficiente per il Modern.',
  'Collation Trimatrix':'Il motore richiede specificamente creature artefatto disponibili. Artefatti non creatura non soddisfano il costo: controllare quante risorse di attacco o difesa si immobilizzano.',
  'Ravenous Cosmozoan':'La riduzione del costo può consentire pressione evasiva, ma va costruita con magie adatte e confrontata con minacce che richiedono meno preparazione. Nessuna lista Modern TRK post-uscita acquisita.',
  'The Holodeck':'Nei tornei Constructed può giocare un permanente dalla sideboard oppure dal cimitero, una volta nel proprio turno: un possibile toolbox che consuma slot di sideboard. Non evita costi o tempi normali e deve competere con motori che stabilizzano prima.',
  'Starfleet Academy':'Richiede cinque mana e tap. Sei tipi non-Borg pareggiano le risorse considerando il mana incolore a cui si rinuncia; sette danno un guadagno netto. Non sostiene da sola un piano Modern veloce o una base multicolore.'
 }
 registry.append(dict(id='oracle-modern-scenarios-20261107',origin=ORIGIN,publisher='MTG Analyzer · analisi editoriale',url='https://magic.wizards.com/en/news/feature/star-trek-release-notes',retrieved=DATE,context='Scenari Modern sul testo Oracle, senza risultati o voti esterni'))
 for name,finding in modern.items():note(names[key(name)],'oracle-modern-scenarios-20261107',['modern'],finding,'Modern · scenario editoriale da testare')
 registry.append(dict(id='research-audit-20261107',origin=ORIGIN,publisher='MTG Analyzer · audit delle fonti',url='https://magic.wizards.com/en/news/feature/star-trek-release-notes',retrieved=DATE,context='Controlli Oracle e limiti delle sintesi secondarie'))
 for name in ['Starfleet Academy','Genesis Device','The Holodeck']:
  note(names[key(name)],'research-audit-20261107',['commander','modern'],formats['corrections'][name],'Controllo editoriale sul testo e sulle condizioni')
 # Preserve current legality separately from eligibility of the new TRK printing.
 note(names[key('Engineered Explosives')],'research-audit-20261107',['pioneer'],formats['corrections']['Engineered Explosives'],'Controllo della legalità corrente e prevista')
 statistics['researchAvailability']={**statistics.get('researchAvailability',{}),'date':DATE,'observedWinRates':True,'untappedPickOrder':'early_access_low_volume','reason':'Disponibili snapshot early access del 4 novembre, separati per Draft e Sealed; non sono dati del lancio pubblico.',
  **{kind+'WinRates':dict(status='available_early_access',observed=statistics[kind]['externalSources']['untapped']['coverage']['observedCards'],withWinRate=statistics[kind]['externalSources']['untapped']['coverage']['cardsWithInHandWinRate']) for kind in ['draft','sealed']}}
 draft=statistics['draft']['externalSources']['untapped'];sealed=statistics['sealed']['externalSources']['untapped']
 coverage=dict(catalogCards=len(cards),newCatalogIdentities=0,draftObserved=draft['coverage']['observedCards'],draftWithWinRate=draft['coverage']['cardsWithInHandWinRate'],sealedObserved=sealed['coverage']['observedCards'],sealedWithWinRate=sealed['coverage']['cardsWithInHandWinRate'],untappedRanked=pick['coverage']['rankedCards'],untappedLowVolume=pick['coverage']['lowMatchVolumeCards'],additionalAttributedGrades=len(grades['cards']),inferredGradesExcluded=len(grades['excludedInferred']),gradeAuthors=sorted({r['author'] for r in grades['cards']}),newFormatObservations=sum(len(s['notes']) for s in formats['sources']),modernEditorialScenarios=len(modern),separateEditorialDraftSealed=sum(bool(c['prospects'].get('limitedAnalysis')) for c in cards))
 coverage['communityCardsWithGrade']=community['coverage']['withGrade']
 sources['research']['sources']=registry
 sources['research']['latestUpdate']=dict(date=DATE,origin=ORIGIN,coverage=coverage,report='research/star-trek-20261107/README.md')
 sources['research']['earlyAccessUpdate']=copy.deepcopy(sources['research']['latestUpdate'])
 sources['research']['evidenceMigrationVersion']=1
 sources['research']['noteMigrationVersion']=1
 sources['research']['limitedReviewRefresh']=dict(date=DATE,snapshot='research/star-trek-20261107/draftsim-review-refresh.json',previousSnapshot='research/star-trek-limited-20261103/draftsim-reviews.json',changedScores=len(refreshed['changedScores']))
 sources['research']['limitations']=[x for x in sources['research'].get('limitations',[]) if x not in ['WR Draft e WR Sealed TRK assenti prima dell’apertura degli eventi Arena del 10 novembre.','306 voti Draft attribuiti a un solo autore: non sono consenso multi-autore, WR o voti Sealed.'] and not x.startswith(('WR disponibili soltanto per early access','Voti J2SJosh e Andrew Quinn conservati;','Le valutazioni editoriali separate Draft/Sealed coprono'))]
 wr_summary=f"WR early access del 4 novembre: {coverage['draftWithWinRate']} carte Draft ({draft['filters']['ranks']}) e {coverage['sealedWithWinRate']} Sealed ({sealed['filters']['ranks']}). Volume ridotto, non metagame stabilizzato."
 grades_summary=f"{coverage['additionalAttributedGrades']} voti espliciti aggiuntivi tramite Limited Library; video originali collegati, non trascritti indipendentemente."
 limited_summary=f"Le valutazioni editoriali separate Draft/Sealed coprono {coverage['separateEditorialDraftSealed']} comuni e non comuni; le rare e SDS non ricevono automaticamente un voto Sealed distinto."
 for limitation in [wr_summary,grades_summary,limited_summary]:
  if limitation not in sources['research']['limitations']:sources['research']['limitations'].append(limitation)
 guides['researchUpdate']=copy.deepcopy(sources['research']['latestUpdate'])
 fragments=guides['fragments']
 fragments['draft.copy-0']=fragments['draft.copy-0'].replace('I voti dei recensori sono confronti attribuiti, senza WR osservate.','Voti attribuiti e WR early access restano distinti: consulta nel catalogo le coperture Draft e Sealed del 7 novembre.')
 draft_total=draft['totalMatchesDisplay'].replace(',','.');sealed_total=sealed['totalMatchesDisplay'].replace(',','.')
 fragments['analysis.panel-1']=f'<section class="trk-panel"><h2>Conoscenza del set: 7 novembre</h2><p>{len(cards)} identità TRK/SDS e {catalog["print_count"]} stampe nel catalogo attivo. {grades_summary} Le scale e i dissensi restano separati.</p><p>{wr_summary} Totali dichiarati: {draft_total} partite Draft e {sealed_total} Sealed (precisione della fonte). Il filtro di campione minimo è disponibile solo per fonti con denominatore documentato.</p><p>Nuove letture Commander, Pioneer e Legacy; scenari Modern distinti dai tornei. Pauper: riletta la review di Romeu del 31 ottobre, nessuna nuova recensione per carta acquisita. Prezzi Cardmarket conservati al 27 ottobre.</p><p><a href="catalogo.html">Consulta ranking, WR e prospettive per carta</a></p><div id="trk-statistics"></div></section>'
 update=f'<section class="trk-panel" data-research-update-20261107><h2>Ricerca del 7 novembre</h2><p>{wr_summary} Nessuna trasposizione fra eventi. Tier Untapped: {coverage["untappedRanked"]} carte classificate e {coverage["untappedLowVolume"]} con campione insufficiente.</p><p>{grades_summary} {limited_summary}</p><p>Pauper: review di Romeu del 31 ottobre riletta, senza nuovi risultati post-uscita. Commander e Modern mantengono contesti e limiti propri.</p><p><a href="https://mtga.untapped.gg/limited/draft/star-trek/card-data">Dati Draft Untapped</a> · <a href="https://mtga.untapped.gg/limited/sealed/star-trek/card-data?eventType=SEALED">Dati Sealed Untapped</a> · <a href="https://limitedlibrary.com/sets/star-trek/">Voti attribuiti Limited Library</a></p></section>'
 fragments['method.panel-0']=re.sub(r'<section class="trk-panel" data-research-update-20261107>.*?</section>','',fragments['method.panel-0'],flags=re.S)
 fragments['method.panel-0']=update+fragments['method.panel-0']
 manifest=load(BASE/'expansion.json');manifest['date']='7 novembre 2026';manifest['description']='Catalogo TRK/SDS, ranking Limited attribuiti, WR Draft e Sealed early access e analisi per formato con fonti e copertura esplicite.'
 manifest['assets']=[latest_catalog if a=='research/star-trek-20261102/catalog.json' else a for a in manifest['assets']]
 save(BASE/'expansion.json',manifest)
 discovery=load(BASE/'discovery.json');previews={r['id']:r for r in discovery.get('previews',[])}
 previews.update({r['id']:r for r in load(OUT/'preview-references.json')['cards']})
 discovery['previews']=list(previews.values());save(BASE/'discovery.json',discovery)
 for file,d in [('cards.json',catalog),('sources.json',sources),('statistics.json',statistics),('ratings.json',ratings),('guides.json',guides)]:save(BASE/file,d)
 save(OUT/'catalog.json',catalog)
 save(OUT/'coverage.json',coverage)
 print(json.dumps(coverage,ensure_ascii=False))
if __name__=='__main__':main()
