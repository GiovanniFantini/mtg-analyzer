"""Offline editorial completion and explicit quarantine of early-access rankings."""
import copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'expansions/star-trek'
OUT=ROOT/'research/star-trek-20261109'
DATE='2026-11-09'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
NOTICE='Le WR e i tier Untapped del solo early access del 4 novembre sono esclusi dagli ordinamenti: campione selezionato e ridotto, margini molto ampi e denominatori GIH non pubblicati. I valori originali restano nei dati storici. I ranking Draft/Sealed qui proposti sono giudizi editoriali motivati, non risultati misurati. Arena apre il 10 novembre.'
def main():
 docs={n:read(BASE/(n+'.json')) for n in ['cards','ratings','sources','statistics','guides','expansion']}
 cards=docs['cards']['cards'];by_id={c['id']:c for c in cards};names={c['name'] for c in cards}
 legalities=read(OUT/'legalities.json')
 assert {r['catalogId'] for r in legalities['cards']}==set(by_id)
 contributions=[r for p in sorted((ROOT/'reviews/star-trek-20261109').glob('contribution-*.json')) for r in read(p)['cards']]
 recalibrated=[r for p in sorted((ROOT/'reviews/star-trek-20261109').glob('recalibration-*.json')) for r in read(p)['cards']]
 expected={c['id'] for c in cards if not c['basic'] and c['rarity'] not in ('common','uncommon')}
 assert len(contributions)==len({r['id'] for r in contributions})==len(expected)==135
 assert {r['id'] for r in contributions}==expected
 if recalibrated:
  expected_common={c['id'] for c in cards if not c['basic'] and c['set']=='TRK' and c['rarity'] in ('common','uncommon')}
  assert len(recalibrated)==201 and {r['id'] for r in recalibrated}==expected_common
  contributions+=recalibrated
 for r in contributions:
  assert set(r['partners'])<=names and r['partners']
  assert all(r[k]['tier'] in 'PSYFBN' and len(r[k]['note'])>40 for k in ['draft','sealed'])
  assert r['draft']['note']!=r['sealed']['note']
  assert all(r['usage'].get(k) for k in ['role','plan','conditions','confidence'])
 # All identities and references validate before writing any active file.
 for r in contributions:
  c=by_id[r['id']]
  c['prospects']['limitedAnalysis']={k:copy.deepcopy(r[k]) for k in ['draft','sealed','partners','usage']}
  c['prospects']['limitedAnalysis'].update(date=DATE,kind='qualitative_editorial',observedWinRates=False,method='Giudizio editoriale del testo Oracle, curva e supporti, con confronto fra recensioni attribuite. Nessuna WR o media di autori; nessun nuovo voto dei bot.',basis=['oracle','attributed_limited_reviews'],productCondition='Valutazione subordinata alla presenza della carta nello specifico evento. Il catalogo non certifica collazione.' if c['set']=='SDS' else None)
 for c in cards:
  p=c['prospects']
  if c['basic']:
   p['limitedApplicability']={'date':DATE,'status':'mana_base_not_power_ranked','note':'Terra base: non riceve un voto di potenza o una WR. Numero e colore dipendono dai simboli dei costi, dai turni in cui servono, dal fixing e dai colori del mazzo; non è una selezione automatica da pick alto.'}
   continue
  a=p['limitedAnalysis']
  if not a.get('usage'):
   a['usage']={'role':docs['ratings']['cards'][c['id']].get('role') or 'Contributo al piano',
    'plan':p['gameplayReview']['finding'],'conditions':a['sealed']['note'],'confidence':'bassa'}
   a['originalAssessmentDate']=a['date'];a['date']=DATE
   a['method']='Giudizio editoriale Oracle e di costruzione del mazzo. Note originali conservate, ruolo esplicitato; confronto fra fonti, non WR o media di autori.'
  p['sources']=list(dict.fromkeys(p.get('sources',[])+['limited-editorial-20261109']))
  for kind in ['draft','sealed']:
   entry=p['formats'][kind]
   entry['note']='Valutazione editoriale separata '+('Draft' if kind=='draft' else 'Sealed')+' del 9 novembre disponibile nella scheda Limited. '+('Carta ospite: presenza nel prodotto e nell’evento da verificare. ' if c['set']=='SDS' else '')+'WR early access escluse dai ranking per incertezza e popolazione selezionata; nessun campione post-lancio affidabile acquisito.'
   entry['researchRenderedNote']=entry['note']
 for r in legalities['cards']:
  c=by_id[r['catalogId']];p=c['prospects']
  if c['legalities']!=r['legalities']:
   p.setdefault('legalityHistory',[])
   if not any(h['date']==c.get('legalitiesRetrieved') for h in p['legalityHistory']):
    p['legalityHistory'].append(dict(date=c.get('legalitiesRetrieved'),legalities=copy.deepcopy(c['legalities'])))
  c.update(legalities=copy.deepcopy(r['legalities']),legalitiesRetrieved=DATE,legalitySource=r['url'])
  for fmt,a in p.get('formats',{}).items():
   current=r['legalities'].get('commander' if fmt=='cedh' else fmt)
   if current is None:continue
   a.update(legality=current,legalityDate=DATE,legalitySource=r['url'])
   if a.get('releaseEligibility'):
    a['historicalReleaseEligibility']=a.pop('releaseEligibility')
   a['note']=a.get('note','').replace('Stato Scryfall del 2 novembre 2026. Ammissibilità prevista all’uscita del 13 novembre: legale; non equivale alla legalità già attiva né a risultati di torneo.','Legalità corrente verificata su Scryfall il 9 novembre 2026. La legalità non dimostra risultati di torneo o disponibilità su Arena prima del 10 novembre.')
   t=a.get('tournamentIndex')
   if t:
    t.update(legality=current,legalityDate=DATE,legalitySource=r['url'])
    if current in ('legal','restricted') and t.get('reason')=='not_legal' and t.get('score') is None:
     t['reason']='no_post_release_sample';t['status']='unavailable'
    t['freshnessNote']='Corpus di torneo storico del '+t['date']+', non aggiornato al weekend del 6-8 novembre. La legalità corrente è verificata separatamente.'
 corrections=read(OUT/'editorial-corrections.json')
 for c in cards:
  finding=corrections['cards'].get(c['name'])
  if c['set']=='TRK' and c['land'] and 'pay 2 life' in c['text']:finding=corrections['shockLands']
  if finding and c['land'] and 'Plains' in c['type'] and 'pay 2 life' in c['text']:
   finding+=" There's Coffee in that Nebula trova questa carta perché cerca una Plains, non necessariamente una terra base."
  if finding:
   p=c['prospects'];review=p['gameplayReview']
   if review['finding']!=finding:review.setdefault('previousFinding',review['finding'])
   review.update(finding=finding,verified=DATE);p['summary']=finding;c['why']=finding
   if c['id'] in docs['ratings']['cards']:docs['ratings']['cards'][c['id']]['why']=finding
   if c['name'] not in {by_id[r['id']]['name'] for r in contributions}:p['limitedAnalysis']['usage']['plan']=finding
  a=c['prospects'].get('limitedAnalysis')
  if not a:continue
  if c['name']=='Bruvac the Grandiloquent':
   a['usage']['conditions']='Raddoppia solo il mill avversario. Ensign Pavel Chekov esilia le carte e non viene raddoppiato; First Contact e Temporal Conqueror fanno macinare il proprio controllore. Non è un motore di mill autonomo.'
  if c['name']=='Kobayashi Maru Scenario':
   a['usage']['conditions']='Serve un’uscita disponibile prima della quarta manutenzione successiva. Subcommander T’Pol può neutralizzare la quarta innescata: il modo resta scelto e, esauriti tutti i modi, le innescate successive sono rimosse dalla pila senza effetto, come indicano le release notes ufficiali.'
  if c['name']=='Borg Cube':
   a['usage']['conditions']='Tre creature artefatto portano il costo a quattro mana; ognuna riduce comunque il costo di uno. Dodici cariche richiedono forza disponibile e tap: si possono accumulare anche nello stesso turno, rinunciando ad attacchi o blocchi di quei corpi.'
  if c['name']=='The City on the Edge of Forever':
   a['usage']['conditions']='Richiede carte in mano e generatori di pedine. Rimuovere l’Umano permette il rientro dei permanenti nel successivo stap del rispettivo controllore, non immediatamente. Finiscono fuori fase anche i tuoi artefatti, Tesori e Indizi.'
  if c['name']=='Gwyndala, the Progeny':
   a['sealed']['note']='Un corpo effettivo 2/2 a due mana lascia un Equipaggiamento riassegnabile. Nel Sealed puoi verificare gli Equipaggiamenti aperti: copiare Combadge, Bat’leth o Type-2 Phaser migliora la pedina per un turno, senza ripetere eventuali effetti di ingresso. Senza supporto resta soprattutto una giocata da curva.'
   a['usage']['conditions']='Migliora con un Equipaggiamento utile da copiare; il bersaglio può anche essere una pedina. Diventare una copia non è un ingresso sul campo e la copia dura solo fino a fine turno.'
  if c['name'] in corrections.get('assessmentUpdates',{}):
   for key,patch in corrections['assessmentUpdates'][c['name']].items():a[key].update(patch)
  if c['name'] in corrections.get('sideboardCards',[]):
   a['sealed']['note']+=' Le modifiche dopo la prima partita sono possibili solo se l’evento prevede sideboard fra partite; nel BO1 questa scelta va fatta contro un avversario ignoto.'
  if c['name'] in ['Kobayashi Maru Scenario','The City on the Edge of Forever','Gwyndala, the Progeny']:
   a['ruleSources']=[dict(label='Release notes Wizards, aggiornate al 4 novembre',url='https://magic.wizards.com/en/news/feature/star-trek-release-notes')]
  if c['name']=='Isshin, Two Heavens as One':
   a['ruleSources']=[dict(label='Ruling Wizards del 18 febbraio 2022, distribuiti da Scryfall',url='https://scryfall.com/card/sds/19/isshin-two-heavens-as-one#rulings')]
  if c['name']=='Unexplored Territory' or c['name'].endswith(' Anomaly'):
   a['usage']['conditions']='Sacrificandola perdi il suo nome se era l’unica copia. Il numero di nomi può crescere solo se un’altra copia conserva il vecchio nome e la terra ottenuta ha un nome nuovo. Valuta inoltre il mana speso e l’ingresso tappato.'
 grades=read(OUT/'attributed-grades.json')
 for c in cards:
  p=c['prospects'];p['researchNotes']=[r for r in p.get('researchNotes',[]) if r.get('source') not in ('limitedlibrary-20261107','limitedlibrary-20261109')]
  p['sources']=[s for s in p['sources'] if s!='limitedlibrary-20261107']
 for r in grades['cards']:
  p=by_id[r['catalogId']]['prospects']
  p['researchNotes'].append(dict(source='limitedlibrary-20261109',origin='research-update-20261109',date=DATE,sourceUpdated=r['sourceUpdated'],formats=['draft'],context=r['context'],finding=r['author']+': '+r['grade']+'. Voto riportato da Limited Library. Non è un voto Sealed distinto né un risultato osservato.',url=r['url'],author=r['author'],originalGrade=r['grade'],attribution='secondary_aggregator'))
  p['sources']=list(dict.fromkeys(p['sources']+['limitedlibrary-20261109']))
 sealed_review=read(OUT/'sealed-review.json')
 for c in cards:
  p=c['prospects'];p['researchNotes']=[r for r in p.get('researchNotes',[]) if r.get('source')!='draftsim-sealed-20261109']
 for r in sealed_review['cards']:
  p=by_id[r['catalogId']]['prospects']
  p['researchNotes'].append(dict(source=sealed_review['source'],origin='research-update-20261109',date=DATE,sourceUpdated=sealed_review['published'],formats=['sealed'],context='Sealed, categoria qualitativa originale di Bryan Hohns (Veveil)',finding='Giudizio Sealed attribuito: '+r['grade']+'. Non è una WR o un voto Draft.',url=sealed_review['url'],author=sealed_review['author'],originalGrade=r['grade'],attribution='direct_review',groupAssessment=r.get('groupAssessment')))
  p['sources']=list(dict.fromkeys(p['sources']+[sealed_review['source']]))
 # Identical scores retain their original acquisition and provenance, with a fresh check.
 for source,file in [('draftsim','draftsim-review-refresh.json'),('arenazone','arenazone-comparison.json')]:
  snapshot=read(OUT/file)
  assert not snapshot.get('changedScores',snapshot.get('changed',[])), 'Changed numeric reviews require explicit integration'
  for r in snapshot['cards']:
   for review in by_id[r['catalogId']]['prospects'].get('limitedReviews',[]):
    if ('draftsim' in review['source'])==(source=='draftsim'):
     review['lastVerified']=DATE;review['verificationSnapshot']='research/star-trek-20261109/'+file
 eligibility={'status':'experimental_only','assessed':DATE,'reason':'Early access selezionato, margini ampi e denominatore GIH non documentato; conservazione diagnostica, escluso dai ranking ordinari.'}
 for kind in ['draft','sealed']:
  docs['statistics'][kind]['externalSources']['untapped']['assessmentEligibility']=copy.deepcopy(eligibility)
 for r in docs['ratings']['cards'].values():
  if r.get('untappedPickOrder'):r['untappedPickOrder']['assessmentEligibility']=copy.deepcopy(eligibility)
 docs['statistics']['researchAvailability'].update(date=DATE,usableObservedWinRates=False,catalogNotice=NOTICE,untappedPickOrder='experimental_only')
 for kind in ['draft','sealed']:docs['statistics']['researchAvailability'][kind+'WinRates']['status']='diagnostic_only'
 g=docs['guides'];study=g['limitedReview']
 study.update(title='Tutte le carte: Draft, Sealed e utilizzo previsto',date=DATE,origin='limited-study-2026-11-09',method='Fasce editoriali comuni a tutte le rarità: P prioritaria, bomba o rimozione premium; S solida sopra il livello di sostituzione; Y buona con supporto concreto; F riempitivo; B riserva per un avversario specifico, se l’evento consente cambi; N da evitare normalmente. Draft considera il costo del pick, Sealed il contributo al pool chiuso. Non sono WR, consenso statistico o voti dei bot.',coverageNote='336 carte non base TRK/SDS con giudizi separati, ruolo, condizioni e supporti. Le 5 terre base servono alla base di mana e non ricevono un voto di potenza. Le ospiti SDS sono valutate solo se ammesse nell’evento; collazione non certificata. Incertezza editoriale esplicita; nessuna WR attendibile post-lancio acquisita.')
 f=g['fragments']
 f['draft.limited-link']='<a href="#limited-review">Tutte le carte: Draft e Sealed</a><a href="#limited-impact">Carte decisive</a>'
 f['sealed.review-links']='<nav aria-label="Approfondimenti Sealed"><a href="#limited-review">Ranking e utilizzo di tutte le carte</a> · <a href="#limited-impact">Carte decisive e risposte</a></nav>'
 import re
 f['draft.copy-0']=re.sub(r'<span data-limited-summary>.*?</span>','',f['draft.copy-0'],flags=re.S)+'<span data-limited-summary> 336 valutazioni editoriali separate Draft/Sealed, con ruolo e condizioni d’uso. Le WR early access non sono utilizzate per i ranking.</span>'
 f['gallery.strategy']=re.sub(r'<p data-limited-study>.*?</p>','',f['gallery.strategy'],flags=re.S)+'<p data-limited-study>Studio aggiornato al 9 novembre: tutte le 336 carte non base hanno un giudizio Draft e Sealed separato con utilizzo previsto. Le cinque basi non ricevono un voto di potenza. '+NOTICE+'</p>'
 f['analysis.panel-1']='<section class="trk-panel"><h2>Conoscenza del set: 9 novembre</h2><p>341 identità TRK/SDS e '+str(docs['cards']['print_count'])+' stampe: 336 carte non base valutate separatamente in Draft e Sealed. Ruolo, condizioni, supporti e giudizi editoriali consultabili per ogni carta.</p><p>306 voti Draft J2SJosh e 336 voti Limited Andrew Quinn verificati il 9 novembre, invariati. Limited Library riporta 793 voti espliciti, compresi quelli di Limited Resources; attribuzione secondaria e scale originali conservate.</p><p>'+NOTICE+'</p><p>Le letture Constructed e Commander mantengono le proprie date e i limiti delle evidenze. Prezzi Cardmarket conservati al 27 ottobre.</p><p><a href="catalogo.html">Consulta le carte</a> · <a href="data/statistics.json">Dati storici e motivi dell’esclusione delle WR</a></p><div id="trk-statistics"></div></section>'
 f['method.panel-0']='<section class="trk-panel"><h2>Metodo e copertura: 9 novembre</h2><p>336 carte non base con giudizi editoriali distinti Draft/Sealed, ruolo, condizioni e supporti; 5 terre base senza voto di potenza. Le SDS sono condizionate alla loro presenza nell’evento. Nessuna media fra autori o conversione delle WR in voti.</p><p>306 voti Draft di J2SJosh e 336 voti Limited di Andrew Quinn nelle scale originali. Limited Library riporta 793 lettere esplicite di Nizzahon, Limited Level-Ups e Limited Resources; 8 giudizi inferred esclusi. L’attribuzione è secondaria e i video non sono stati trascritti indipendentemente.</p><p><a href="https://draftsim.com/mtg-star-trek-sealed-guide/">Bryan Hohns, guida Sealed del 5 novembre</a>: 135 categorie qualitative originali per rare, mitiche e ospiti, incluse valutazioni di cicli. Non sono voti Draft né risultati osservati.</p><p>'+NOTICE+'</p><p><a href="data/statistics.json">Snapshot e limiti statistici</a> · <a href="https://magic.wizards.com/en/news/mtg-arena/star-trek-event-schedule">Calendario ufficiale Arena</a></p></section>'
 f['method.panel-0'] += '<p>Identità e stampe: <a href="https://github.com/GiovanniFantini/mtg-analyzer/blob/main/'+docs['sources']['research']['catalogSnapshot']+'">catalog.json</a>. Testo Oracle, legalità e valutazioni hanno controlli e date separati.</p>'
 f['pick-guide-section.copy-0']='Valutazioni editoriali: controlla colori, curva e supporto. Tutte le carte sono confrontabili sotto in Draft e Sealed; le WR early access sono escluse dai ranking.'
 for group in g.get('pickGuide',{}).get('groups',[]):
  group['note']=group['note'].replace('tutte le 201 valutazioni','tutte le 336 valutazioni')
  for entry in group['cards']:
   card=next(c for c in cards if c['name']==entry['name'])
   if card['prospects'].get('limitedAnalysis'):entry['why']=card['prospects']['limitedAnalysis']['draft']['note']
 g['researchUpdate']=dict(date=DATE,summary='Copertura editoriale completa delle carte non base e quarantena dei ranking early access.',limitations=[NOTICE])
 registry=docs['sources']['research']['sources']
 new_sources=[dict(id='limited-editorial-20261109',publisher='MTG Analyzer',url='https://github.com/GiovanniFantini/mtg-analyzer/tree/main/research/star-trek-20261109',retrieved=DATE,context='Analisi editoriale originale, contributo e revisione Opus con controlli Oracle; non fonte esterna né risultati di gioco.'),dict(id='limitedlibrary-20261109',publisher='Limited Library',url='https://limitedlibrary.com/sets/star-trek/',retrieved=DATE,published=grades['sourceUpdated'],coverage=len(grades['cards']),context='Aggregatore secondario, solo voti espliciti; video non trascritti indipendentemente.'),dict(id=sealed_review['source'],publisher='Draftsim',author=sealed_review['author'],url=sealed_review['url'],retrieved=DATE,published=sealed_review['published'],coverage=len(sealed_review['cards']),context=sealed_review['context'])]
 source_updates={n['id']:n for n in new_sources}
 docs['sources']['research']['sources']=[source_updates.get(s['id'],s) for s in registry]+[n for n in new_sources if n['id'] not in {s['id'] for s in registry}]
 docs['sources']['research']['limitedCompletion']=dict(date=DATE,editorialCards=336,basicCardsNotPowerRanked=5,additionalEditorialCards=135,attributedGrades=793,snapshot='research/star-trek-20261109/coverage.json',earlyAccessExcludedFromOrdinaryRankings=True)
 docs['sources']['research']['limitations']=[s for s in docs['sources']['research'].get('limitations',[]) if s!=NOTICE and not s.startswith(('WR early access','Le valutazioni editoriali separate'))]+[NOTICE]
 docs['expansion'].update(date='9 novembre 2026',description='Tutte le carte TRK/SDS: ranking editoriali Draft e Sealed, ruolo e condizioni, recensioni attribuite. WR early access conservate come diagnostica, escluse dai ranking.')
 coverage=dict(date=DATE,catalogCards=len(cards),rankedNonbasic=sum(bool(c['prospects'].get('limitedAnalysis')) for c in cards),basicCardsNotPowerRanked=sum(bool(c['prospects'].get('limitedApplicability')) for c in cards),withUsage=sum(bool(c['prospects'].get('limitedAnalysis',{}).get('usage')) for c in cards),missing=[c['name'] for c in cards if not c['basic'] and not c['prospects'].get('limitedAnalysis')],attributedGrades=grades['coverage'],numericReviewsChanged=False,observedWinRatesAdded=False,earlyAccessExcluded=True,inferredGradesExcluded=len(grades['excludedInferred']))
 import collections
 coverage['tierDistribution']={k:{rarity:dict(collections.Counter(c['prospects']['limitedAnalysis'][k]['tier'] for c in cards if not c['basic'] and c['rarity']==rarity)) for rarity in ['common','uncommon','rare','mythic']} for k in ['draft','sealed']}
 coverage['recalibratedCommonUncommon']=len(recalibrated)
 assert coverage['rankedNonbasic']==coverage['withUsage']==336 and not coverage['missing']
 for n,d in docs.items():save(BASE/(n+'.json'),d)
 save(OUT/'coverage.json',coverage)
 print(coverage)
if __name__=='__main__':main()
