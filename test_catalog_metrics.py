import copy
import unittest
from catalog_metrics import catalog_performance
from statistics_data import validate_external_statistics

class PerformanceTests(unittest.TestCase):
 def snapshot(self,event='PremierDraft',status='public',value=0):
  return {'schemaVersion':1,'provider':'Example','url':'https://example.com/data','retrieved':'2026-10-28','rateUnit':'percent','filters':{'event':event},'metrics':{'inHandWinRate':{'label':'GIH WR','unit':'percent','status':status},'games':{'label':'GIH games','unit':'games','status':'public'}},'cards':[{'catalogId':'one','name':'One','metrics':{'inHandWinRate':value,'games':10}}]}
 def test_draft_sealed_and_population_separation(self):
  stats={'draft':{'externalSources':{'premier':self.snapshot(),'traditional':self.snapshot('TradDraft',value=75)}},'sealed':{'externalSources':{'sealed':self.snapshot('Sealed',value=25)}}}
  original=copy.deepcopy(stats);result=catalog_performance(stats)
  self.assertEqual([s['cards']['one']['value'] for s in result['draft']],[0,75]);self.assertEqual(result['sealed'][0]['cards']['one']['value'],25);self.assertEqual(stats,original)
 def test_public_values_only_no_fallback_between_events(self):
  stats={'draft':{'externalSources':{'locked':self.snapshot(status='locked',value=None),'suspect':self.snapshot(status='suspect',value=50)}}}
  self.assertEqual(catalog_performance(stats),{'draft':[],'sealed':[]})
 def test_sealed_validation_rejects_incorrect_percentage(self):
  stats={'sealed':{'externalSources':{'sealed':self.snapshot('Sealed',value=101)}}}
  with self.assertRaisesRegex(ValueError,'statistics.sealed'):validate_external_statistics(stats,[{'id':'one','name':'One'}])
 def test_null_is_not_zero(self):
  s=self.snapshot(value=None);r=catalog_performance({'sealed':{'externalSources':{'one':s}}})
  self.assertIsNone(r['sealed'][0]['cards']['one']['value']);self.assertNotIn('two',r['sealed'][0]['cards'])
if __name__=='__main__':unittest.main()
