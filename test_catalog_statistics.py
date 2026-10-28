import copy
import unittest
from types import SimpleNamespace

from build_expansion import catalog_data


class CatalogStatisticsTests(unittest.TestCase):
    def fixture(self, status='public'):
        source = {'provider': 'Untapped.gg', 'retrieved': '2026-10-22',
                  'url':'https://example.com/statistics','filters': {'event': 'Premier Draft'},
                  'metrics': {'inHandWinRate': {'label':'In-hand WR','unit':'percent','status': status}, 'games': {'status': 'public'}},
                  'cards': [{'catalogId': 'one', 'sourceUrl': 'https://example.com/one',
                             'metrics': {'inHandWinRate': 0.0, 'games': 100}},
                            {'catalogId': 'two', 'sourceUrl': 'https://example.com/two',
                             'metrics': {'inHandWinRate': None, 'games': 10}}]}
        return SimpleNamespace(default_event_id=lambda kind:None, manifest={'storage':{}},cards=[{'id': 'one'}, {'id': 'two'}, {'id': 'three'}],
                               data={'cards': {}, 'sentiment': {}, 'statistics': {'draft': {'externalSources': {'untapped': source}}},
                                     'ratings': {}, 'combos': [], 'sources': {}, 'discovery': {}})

    def test_preserves_zero_null_missing_and_provenance(self):
        expansion = self.fixture()
        original = copy.deepcopy(expansion.data)
        result = catalog_data(expansion)['catalogWinRates']
        self.assertEqual(result['cards']['one']['value'], 0)
        self.assertIsNone(result['cards']['two']['value'])
        self.assertNotIn('three', result['cards'])
        self.assertEqual(result['retrieved'], '2026-10-22')
        self.assertEqual(result['filters'], {'event': 'Premier Draft'})
        self.assertEqual(expansion.data, original)

    def test_locked_or_suspect_win_rates_are_excluded(self):
        for status in ('locked', 'suspect'):
            with self.subTest(status=status):
                self.assertEqual(catalog_data(self.fixture(status))['catalogWinRates']['cards'], {})

    def test_absent_provider_does_not_invent_values(self):
        expansion = self.fixture()
        expansion.data['statistics'] = {}
        self.assertEqual(catalog_data(expansion)['catalogWinRates']['cards'], {})


if __name__ == '__main__':
    unittest.main()
