"""Data integrity for the dated early-access import, distinct from live services."""
import json
import unittest
import contextlib
import hashlib
import io
import shutil
import tempfile
from pathlib import Path
from catalog_metrics import catalog_performance
from statistics_data import validate_external_statistics
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
class StarTrekUpdateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.cards=read('expansions/star-trek/cards.json')['cards']
  cls.stats=read('expansions/star-trek/statistics.json')
 def test_distinct_populations_and_missing_rates(self):
  validate_external_statistics(self.stats,self.cards)
  for kind,count,rates in [('draft',322,280),('sealed',318,253)]:
   snapshot=self.stats[kind]['externalSources']['untapped']
   self.assertEqual(len(snapshot['cards']),count)
   self.assertEqual(sum(r['metrics']['inHandWinRate'] is not None for r in snapshot['cards']),rates)
   self.assertIn('Early Access',snapshot['filters']['event'])
   self.assertEqual(snapshot['metrics']['includedWinRate']['status'],'suspect')
   self.assertTrue(all(r['metrics']['playedWinRate'] is None for r in snapshot['cards']))
  view=catalog_performance(self.stats)
  self.assertNotEqual(view['draft'][0]['cards'],view['sealed'][0]['cards'])
  self.assertTrue(all(r['games'] is None for r in view['draft'][0]['cards'].values()))
  self.assertTrue(any(r['confidenceMargin'] for r in view['draft'][0]['cards'].values()))
 def test_secondary_grades_are_explicit_and_not_engine_weights(self):
  grades=read('research/star-trek-20261107/attributed-grades.json')
  self.assertEqual(len(grades['cards']),498)
  self.assertTrue(all(r['gradeType']=='explicit' for r in grades['cards']))
  self.assertTrue(all(r['gradeType']=='inferred' for r in grades['excludedInferred']))
  ratings=read('expansions/star-trek/ratings.json')['cards']
  self.assertTrue(all(r.get('score') is None for r in ratings.values()))
  for c in self.cards:
   for row in c['prospects'].get('researchNotes',[]):
    if row.get('source')=='limitedlibrary-20261107':
     self.assertEqual(row['attribution'],'secondary_aggregator')
     self.assertIn('Non è un voto Sealed distinto',row['finding'])
 def test_no_inferred_pioneer_legality(self):
  c=next(c for c in self.cards if c['name']=='Engineered Explosives')
  self.assertEqual(c['set'],'TRK')
  self.assertEqual(c['prospects']['formats']['pioneer']['legality'],c['legalities']['pioneer'])
  self.assertEqual(c['prospects']['formats']['pioneer']['releaseEligibility']['date'],'2026-11-13')
  self.assertTrue(any(r.get('source')=='research-audit-20261107' for r in c['prospects']['researchNotes']))
 def test_all_new_sources_resolve_and_tiers_preserve_absence(self):
  registry={s['id'] for s in read('expansions/star-trek/sources.json')['research']['sources']}
  for c in self.cards:self.assertTrue(set(c['prospects']['sources'])<=registry)
  snapshot=read('research/star-trek-20261107/untapped-pick-order.json')
  self.assertEqual(sum(r['tier'] is not None for r in snapshot['cards']),268)
  self.assertEqual(sum(r['tier'] is None for r in snapshot['cards']),54)
  self.assertTrue(all(r['tierOrder'] is None for r in snapshot['cards'] if r['tier'] is None))
 def test_repeat_import_is_identical_and_keeps_unrelated_data(self):
  import integrate_star_trek_20261107 as importer
  original_base,original_out=importer.BASE,importer.OUT
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);target=root/'expansion';snapshots=root/'research'
   shutil.copytree(original_base,target);shutil.copytree(original_out,snapshots)
   cards=read('expansions/star-trek/cards.json');cards['unrelatedSentinel']={'preserve':True}
   importer.save(target/'cards.json',cards)
   try:
    importer.BASE,importer.OUT=target,snapshots
    from integrate_limited_study import integrate
    integrate(target,ROOT/'research/star-trek-limited-20261103')
    self.assertNotIn('senza WR osservate',importer.load(target/'guides.json')['fragments']['draft.copy-0'])
    with contextlib.redirect_stdout(io.StringIO()):importer.main()
    first={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.glob('*.json')}
    with contextlib.redirect_stdout(io.StringIO()):importer.main()
    self.assertNotIn('senza WR osservate',importer.load(target/'guides.json')['fragments']['draft.copy-0'])
    self.assertEqual(first,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.glob('*.json')})
    self.assertEqual(importer.load(target/'cards.json')['unrelatedSentinel'],{'preserve':True})
   finally:importer.BASE,importer.OUT=original_base,original_out
 def test_printings_and_engine_inputs(self):
  catalog=read('expansions/star-trek/cards.json')
  self.assertEqual(catalog['print_count'],read('research/star-trek-20261107/oracle-check.json')['printings'])
  self.assertEqual(catalog['print_count'],sum(len(c['prints']) for c in self.cards))
  audit=read('research/star-trek-20261107/functional-input-audit.json')
  self.assertEqual(audit['changedEngineCards'],[]);self.assertEqual(audit['changedAdoptedRatings'],[])
 def test_v2_v4_replay_fingerprints_match_pre_update_baseline(self):
  from expansion_data import Expansion
  expansion=Expansion(ROOT/'expansions/star-trek/expansion.json')
  audit=read('research/star-trek-20261107/functional-input-audit.json')
  for event_id,expected in audit['replayEvents'].items():
   current=expansion.draft_format(event_id)
   self.assertEqual(current['revision'],expected['baselineRevision'])
   self.assertEqual(current['botPolicy']['revision'],expected['baselineBotPolicyRevision'])
   self.assertFalse(current['botPolicy']['empirical']['available'])
 def test_changed_reviews_keep_previous_reading_by_identity(self):
  baseline={r['catalogId']:r for r in read('research/star-trek-20261107/draftsim-review-baseline.json')['cards']}
  changed={r['catalogId'] for r in read('research/star-trek-20261107/draftsim-review-refresh.json')['changedScores']}
  ratings=read('expansions/star-trek/ratings.json')['cards']
  for c in self.cards:
   review=next((r for r in c['prospects'].get('limitedReviews',[]) if r['source']=='draftsim-trk-limited-20261107'),None)
   if not review:continue
   evidence=next(r for r in ratings[c['id']]['evidence'] if r['author']==review['author'] and r['url']==review['url'])
   for row in [review,evidence]:
    if c['id'] in changed:self.assertEqual(row['previousReading']['value'],baseline[c['id']]['value'])
    else:self.assertNotIn('previousReading',row)
if __name__=='__main__':unittest.main()
