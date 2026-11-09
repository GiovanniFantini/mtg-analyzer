"""Full editorial coverage and diagnostic-only empirical data are separate contracts."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from build_expansion import catalog_data
from expansion_data import Expansion
import integrate_star_trek_20261109 as importer
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
class CompletionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.expansion=Expansion(ROOT/'expansions/star-trek/expansion.json')
 def test_full_identity_coverage_distinct_contexts_and_real_partners(self):
  cards=self.expansion.cards;names={c['name'] for c in cards};nonbasic=[c for c in cards if not c['basic']]
  self.assertEqual(len(nonbasic),336)
  for c in nonbasic:
   a=c['prospects']['limitedAnalysis'];self.assertFalse(a['observedWinRates'])
   self.assertNotEqual(a['draft']['note'],a['sealed']['note'])
   for k in ['draft','sealed']:self.assertIn(a[k]['tier'],['P','S','Y','F','B','N'])
   self.assertTrue(set(a['partners'])<=names)
   for k in ['role','plan','conditions','confidence']:self.assertTrue(a['usage'][k])
   if c['set']=='SDS':self.assertIn('evento',a['productCondition'])
  for c in cards:
   if c['basic']:
    self.assertNotIn('limitedAnalysis',c['prospects']);self.assertEqual(c['prospects']['limitedApplicability']['status'],'mana_base_not_power_ranked')
 def test_diagnostic_values_survive_but_cannot_sort_catalog(self):
  d=catalog_data(self.expansion)
  self.assertEqual(d['catalogPerformance'],{'draft':[],'sealed':[]})
  self.assertEqual(d['catalogWinRates']['cards'],{})
  self.assertFalse(any(c.get('untappedPickOrder') for c in d['cards']))
  self.assertTrue(any(c.get('untappedPickOrder') for c in self.expansion.cards))
  self.assertIn('denominatori GIH',d['statisticsNotice'])
  self.assertEqual(len(self.expansion.data['statistics']['draft'].get('cards',[])),0)
  self.assertFalse(self.expansion.availability['draftStatistics']['available'])
  for event in ['draft','picktwo']:self.assertFalse(self.expansion.draft_format(event)['botPolicy']['empirical']['available'])
 def test_source_specific_sealed_and_secondary_grades(self):
  rows=[r for c in self.expansion.cards for r in c['prospects'].get('researchNotes',[]) if r.get('source')=='draftsim-sealed-20261109']
  self.assertEqual(len(rows),135)
  self.assertTrue(all(r['formats']==['sealed'] and r['attribution']=='direct_review' for r in rows))
  self.assertEqual({r['originalGrade'] for r in rows},{'Bomb','Great','Good','Mediocre','Bad'})
  library=read(ROOT/'research/star-trek-20261109/attributed-grades.json')
  self.assertEqual(len(library['cards']),793);self.assertEqual(len(library['excludedInferred']),8)
  self.assertEqual(library['coverage']['authors']['Limited Resources'],201)
 def test_recalibration_uses_consistent_anchors_and_specific_roles(self):
  coverage=read(ROOT/'research/star-trek-20261109/coverage.json')
  self.assertEqual(coverage['recalibratedCommonUncommon'],201)
  cards={c['name']:c for c in self.expansion.cards}
  for name in ['Pure Energy','Dathon and Picard at El-Adrel']:
   for k in ['draft','sealed']:self.assertNotIn(cards[name]['prospects']['limitedAnalysis'][k]['tier'],['P','S'])
  for c in self.expansion.cards:
   a=c['prospects'].get('limitedAnalysis')
   if a:self.assertNotIn(a['usage']['role'],['Interazione','Corpo e sinergie','Piano e condizioni','Permanente di supporto'])
  for k in ['draft','sealed']:
   self.assertEqual(sum(sum(values.values()) for values in coverage['tierDistribution'][k].values()),336)
  self.assertIn('fine turno avversario',cards['Collation Trimatrix']['prospects']['limitedAnalysis']['sealed']['note'])
 def test_current_legality_is_not_a_tournament_result(self):
  source={r['catalogId']:r for r in read(ROOT/'research/star-trek-20261109/legalities.json')['cards']}
  for c in self.expansion.cards:
   self.assertEqual(c['legalities'],source[c['id']]['legalities'])
   for fmt,a in c['prospects']['formats'].items():
    if fmt in c['legalities']:self.assertEqual(a['legality'],c['legalities'][fmt])
    if a.get('tournamentIndex'):self.assertEqual(a['tournamentIndex']['date'],'2026-10-28')
 def test_offline_reintegration_preserves_current_revision(self):
  import contextlib,io
  original=importer.BASE
  with tempfile.TemporaryDirectory() as t:
   import shutil
   target=Path(t);files=['cards','ratings','sources','statistics','guides','expansion']
   for name in files:shutil.copy2(original/(name+'.json'),target/(name+'.json'))
   before={name:(target/(name+'.json')).read_bytes() for name in files}
   try:
    importer.BASE=target
    with contextlib.redirect_stdout(io.StringIO()):importer.main()
    self.assertEqual(before,{name:(target/(name+'.json')).read_bytes() for name in files})
   finally:importer.BASE=original
if __name__=='__main__':unittest.main()
