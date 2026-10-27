import copy
import hashlib
import json
import unittest
from pathlib import Path

from import_untapped_pick_order import normalize


class PickOrderImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = Path('research/reality-fracture-20261027/untapped-pick-order-dom.json').read_bytes()
        cls.capture = json.loads(raw)
        cls.input_hash = hashlib.sha256(raw).hexdigest()
        cls.catalog = json.loads(Path('expansions/reality-fracture/cards.json').read_text(encoding='utf-8'))['cards']

    def test_complete_capture_and_insufficient_samples(self):
        result = normalize(self.capture, self.catalog, self.input_hash)
        self.assertEqual(result['coverage']['observedCards'], 290)
        self.assertEqual(result['coverage']['rankedCards'], 283)
        self.assertEqual(result['coverage']['lowMatchVolumeCards'], 7)
        self.assertEqual(len(result['coverage']['missingCards']), 5)
        self.assertEqual(sum(r['catalogId'].startswith('spg-') for r in result['cards']), 10)
        self.assertTrue(all(r['tierOrder'] is None for r in result['cards'] if r['status'] == 'low_match_volume'))

    def test_rejects_duplicate_unknown_cards_and_changed_tiers(self):
        for mutation in ('duplicate', 'unknown', 'tier'):
            with self.subTest(mutation=mutation):
                capture = copy.deepcopy(self.capture)
                if mutation == 'duplicate':
                    capture['groups'][0]['cards'].append(capture['groups'][0]['cards'][0])
                elif mutation == 'unknown':
                    capture['groups'][0]['cards'][0]['name'] = 'Carta sconosciuta'
                else:
                    capture['groups'][0]['tier'] = 'SS'
                with self.assertRaises((ValueError, KeyError)):
                    normalize(capture, self.catalog, self.input_hash)

    def test_import_does_not_replace_editorial_ratings(self):
        ratings = json.loads(Path('expansions/reality-fracture/ratings.json').read_text(encoding='utf-8'))
        result = normalize(self.capture, self.catalog, self.input_hash)
        for row in result['cards']:
            saved = ratings['cards'][row['catalogId']]
            self.assertIn('score', saved)
            self.assertEqual(saved['untappedPickOrder']['tier'], row['tier'])


if __name__ == '__main__':
    unittest.main()
