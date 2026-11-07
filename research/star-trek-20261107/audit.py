"""Audit actual research inputs, preserving acquisition versus integration status."""
import hashlib,json,runpy,tempfile
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
CACHE=Path(tempfile.gettempdir())/'mtg-star-trek-research-20261107'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 cards=read(ROOT/'expansions/star-trek/cards.json')['cards']
 raw=read(OUT/'scryfall.json')['data'];by_id={c['oracle_id']:c for c in raw}
 diffs=[dict(name=c['name'],catalogId=c['id'],field='text',local=c['text'],source=by_id[c['id']].get('oracle_text')) for c in cards if c['text']!=by_id[c['id']].get('oracle_text',c['text'])]
 assert len(diffs)==1 and diffs[0]['name']=='Mirror Universe Intrusion'
 assert all(c['legalities']==by_id[c['id']]['legalities'] for c in cards)
 save(OUT/'oracle-check.json',dict(date='2026-11-07',identities=len(cards),printings=len(raw),legalitiesUnchanged=True,allIdentitiesMatched=True,textDifferences=diffs,decision='Conservata la correzione documentata sul reminder di Mirror Universe Intrusion; nessuna sostituzione funzionale.'))
 old_prints={r['id'] for r in read(ROOT/'research/star-trek-20261102/scryfall.json')['data']}
 save(OUT/'printing-updates.json',dict(date='2026-11-07',before=len(old_prints),after=len(raw),added=[dict(printingId=r['id'],oracleId=r['oracle_id'],name=r['name'],set=r['set'],number=r['collector_number'],frameEffects=r.get('frame_effects',[]),finishes=r['finishes'],boosterFlag=r['booster'],decision='Variante grafica aggiunta alla stessa identità. Non abilita collazione o nuovi eventi.') for r in raw if r['id'] not in old_prints]))
 if (CACHE/'draftsim-review.html').exists():
  extractor=runpy.run_path(str(ROOT/'research/star-trek-limited-20261103/extract_reviews.py'))['extract']
  refresh=extractor(CACHE/'draftsim-review.html',cards)
  old={r['catalogId']:r['value'] for r in read(ROOT/'research/star-trek-limited-20261103/draftsim-reviews.json')['cards']}
  refresh.update(date='2026-11-07',retrieved='2026-11-07',source='draftsim-trk-limited-20261107',changedScores=[r for r in refresh['cards'] if r['value']!=old[r['catalogId']]])
  save(OUT/'draftsim-review-refresh.json',refresh)
 integrated={
  'limitedlibrary-data':'498 voti espliciti estratti, 8 inferred esclusi; fonte secondaria dichiarata.',
  'untapped-draft':'DOM completo: WR Draft early access, celle pubbliche e margini; Premium escluso.',
  'untapped-sealed':'DOM completo: WR Sealed early access, popolazione separata.',
  'untapped-pick-order':'268 tier e 54 low volume, nessuna conversione in voto numerico.',
  'draftsim-review':'336 voti riletti e abbinati; due punteggi cambiati rispetto al 3 novembre.',
  'edhrec-typal':'16 osservazioni Commander integrate e controllate su Oracle.',
  'edhrec-artifacts':'28 osservazioni Commander integrate, correzioni meccaniche separate.',
  'cardsrealm-pioneer':'10 osservazioni attribuite integrate, legalità attuale e prevista distinte.',
  'cardsrealm-legacy':'21 osservazioni attribuite integrate; nessun risultato post-uscita.',
  'mylimitedgrades-trk':'336 carte acquisite su quattro pagine, 125 aggregati Community con numero di valutatori pubblicato. Nessun benchmark né attribuzione a un esperto.',
 }
 excluded={
  'cardsrealm-modern':'Pagina generica senza articolo Modern utile, non una review acquisita.',
  'edhlab-review':'Accesso fallito: nessun giudizio per carta acquisito.',
  'arenazone-historic':'Contesto Historic: escluso dalle nuove conclusioni Modern/Pauper, senza trasferire giudizi fra formati.',
  'metagame-guide':'Guida generale letta; non contiene voti individuali da importare. Piano Limited già coperto dalle analisi precedenti.',
  'limitedmtg':'Analisi automatica del testo, non recensioni numeriche né partite osservate; non importata come ranking.',
  'mtgsold':'Indice del sito, non acquisita una review per carta.',
  'limitedlibrary':'Shell e controllo browser; i voti vengono dal payload pubblico separato.',
  '17lands-trk-draft':'Shell di caricamento, nessuna nuova tabella statistica da importare.',
  'cardsrealm-pauper-trk':'Review del 31 ottobre riletta: sette candidature e limiti già presenti, nessun nuovo voto o risultato.',
  'meta-limited-preview':'Modello predittivo, nessun WR osservato utilizzabile come sostituto di Untapped.',
  'standard-preview-ratings':'Previsioni automatiche Constructed già conservate, escluse dai nuovi voti Limited.',
  'mylimitedgrades-trk':'Nessun benchmark 17Lands disponibile; presenti aggregati Community con pochissimi valutatori. Acquisizione completa paginata separata, nessuna attribuzione a un esperto.',
 }
 assessments=[]
 for row in read(OUT/'source-audit.json')['sources']:
  ident=row['id'];status='integrated' if ident in integrated else 'excluded_or_context_only' if ident in excluded else 'acquisition_only'
  reason=integrated.get(ident,excluded.get(ident,'Fonte storica riacquisita per inventario; nessun nuovo dato estratto in questo giro. Le prove precedenti conservano data e provenienza.'))
  if ident.startswith('arenazone-trk-'):
   status='confirmed';reason='306 voti estratti dalle sette review e confrontati con il 2 novembre: nessuna variazione. Vedere arenazone-comparison.json.'
  if row['status']=='unavailable':
   status='not_acquired_local_tls' if 'CERTIFICATE_VERIFY_FAILED' in row.get('error','') else 'unavailable'
   reason=row.get('error','Accesso non disponibile.')
  assessments.append(dict(id=ident,url=row['url'],status=status,reason=reason,sha256=row.get('sha256')))
 save(OUT/'source-assessments.json',dict(date='2026-11-07',sources=assessments,additionalSearches=[
  dict(url='https://www.youtube.com/watch?v=MdCSKac_xEs',publisher='StrataGames',context='Pauper',status='indexed_not_transcribed',reason='Video del 6 novembre individuato, lettura web limitata; nessun giudizio per carta attribuito.'),
  dict(url='https://www.buzzsprout.com/2284313/episodes',publisher='Common Ground',context='Pauper',status='indexed_not_transcribed',reason='Episodio 151 del 5 novembre trovato negli indici; nessuna trascrizione primaria acquisita.'),
  dict(url='https://mtga.untapped.gg/limited/draft/star-trek/card-data',publisher='Untapped.gg',context='Ranghi',status='current_public_filter_only',reason='Acquisiti solo Bronze-Platinum nel Draft e Unranked nel Sealed, non tutti i ranghi. Nessun aggiramento delle opzioni Premium.')]))
 print('Audited sources',len(assessments))
if __name__=='__main__':main()
