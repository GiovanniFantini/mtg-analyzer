"""Sourced simulator data, backwards compatible pools and honest model scope."""
import copy,json,shutil,tempfile,unittest
from pathlib import Path
from expansion_data import Expansion
from integrate_star_trek_simulators import integrate
ROOT=Path(__file__).resolve().parent
FOLDER=ROOT/'expansions/star-trek';RESEARCH=ROOT/'research/star-trek-integration-20261109'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
class SimulatorIntegrationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.e=Expansion(FOLDER/'expansion.json')
 def test_real_dependencies_are_ready(self):
  for feature in ['sealedSimulator','draftTable']:
   self.assertTrue(self.e.availability[feature]['available']);self.assertEqual(self.e.availability[feature]['missing'],[])
  for event in ['draft','sealed','picktwo']:self.assertTrue(self.e.event_availability(event)['available'])
  self.assertEqual(self.e.manifest['status'],'prerelease')
 def test_source_grades_not_wr_or_editorial_conversion(self):
  source={r['catalogId']:r for r in read(RESEARCH/'bot-ratings.json')['cards']}
  for c in self.e.cards:
   if c['basic']:self.assertIsNone(c['score']);self.assertEqual(source[c['id']]['value'],-1)
   else:self.assertEqual(c['score'],source[c['id']]['value']);self.assertEqual(c['engineSource'],'draftsim-bot-20261109')
  self.assertFalse(self.e.data['statistics']['researchAvailability']['usableObservedWinRates'])
 def test_membership_and_slot_source_facts(self):
  f=self.e.draft_format('draft');spec=f['collation'];printed={c['id']:c for c in f['cards']}
  self.assertEqual(spec['expectedGroupCounts']['main-common'],81)
  self.assertEqual(spec['expectedGroupCounts']['main-uncommon'],110)
  self.assertEqual(spec['expectedGroupCounts']['main-rare'],80)
  self.assertEqual(spec['expectedGroupCounts']['main-mythic'],25)
  self.assertEqual(len(self.e.product_printings('draft')),460)
  self.assertTrue(all(c['set'] in ['TRK','SDS'] for c in printed.values()))
  self.assertTrue(all(printed[i]['set']=='SDS' for i in spec['groups']['stardates']))
  self.assertEqual(next(r for r in spec['recipe'] if r['id']=='stardates')['chance'],.04)
  self.assertFalse(any(b['group']=='stardates' for r in spec['recipe'] if r['id'] in ['foil','wildcard','rare'] for b in r['branches']))
  self.assertIn('Unexplored Territory',[printed[i]['name'] for i in spec['groups']['main-common']])
  self.assertNotIn('Unexplored Territory',[printed[i]['name'] for i in spec['groups']['duals']])
  self.assertIn('not measured physical print sheets',spec['verificationScope'])
 def test_storage_and_identity_preservation(self):
  before=read(RESEARCH/'before-integration.json')
  self.assertEqual(self.e.manifest['storage'],before['storage'])
  self.assertEqual({c['id'] for c in self.e.cards},{r['catalogId'] for r in read(RESEARCH/'bot-ratings.json')['cards']})
 def test_offline_repeat_is_identical(self):
  with tempfile.TemporaryDirectory() as t:
   target=Path(t)/'set';shutil.copytree(FOLDER,target)
   before={p.name:p.read_bytes() for p in target.glob('*.json')}
   integrate(target,RESEARCH)
   self.assertEqual(before,{p.name:p.read_bytes() for p in target.glob('*.json')})
if __name__=='__main__':unittest.main()
