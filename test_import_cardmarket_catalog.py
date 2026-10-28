"""Monetary references preserve zero, absence, variants and source boundaries."""
import json
import tempfile
import unittest
from pathlib import Path
from import_cardmarket_catalog import integrate


class CardmarketImportTests(unittest.TestCase):
    def fixture(self, rows, cards=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        expansion = directory/'set'
        expansion.mkdir()
        documents = {'cards': {'cards': cards or [{'id': 'one', 'name': 'Example', 'set': 'TST'}]},
                     'prices': {'available': False}, 'sources': {}}
        for key, value in documents.items():
            (expansion/(key+'.json')).write_text(json.dumps(value), encoding='utf-8')
        capture = directory/'capture.json'
        capture.write_text(json.dumps({'retrieved': '2026-10-28', 'finishFilter': 'any',
                                       'pages': [{'url': 'https://www.cardmarket.com/en/Magic/Products/Singles/Test',
                                                  'rows': rows}]}), encoding='utf-8')
        return capture, expansion

    def row(self, name, price, suffix='example'):
        return {'text': name+'\n\n'+('From '+price+' €' if price else 'No offers'),
                'href': 'https://www.cardmarket.com/en/Magic/Products/Singles/Test/'+suffix}

    def test_zero_and_missing_and_variant_prices_are_distinct(self):
        capture, expansion = self.fixture([self.row('Example', '0,00'),
                                            self.row('Example (V.2)', '1.234,56', 'example-v2')])
        result = integrate(capture, expansion)
        self.assertEqual(result['products'], 2)
        reference = json.loads((expansion/'prices.json').read_text(encoding='utf-8'))['references']['cards']['one']
        self.assertEqual(reference['from'], 0)
        self.assertEqual(reference['observations'][1]['from'], 1234.56)
        self.assertIsNone(reference['printingId'])
        self.assertIsNone(reference['nonfoil'])
        self.assertIsNone(reference['foil'])
        # A missing offer is not replaced by a zero.
        capture, expansion = self.fixture([self.row('Example', None)])
        integrate(capture, expansion)
        reference = json.loads((expansion/'prices.json').read_text(encoding='utf-8'))['references']['cards']['one']
        self.assertIsNone(reference['from'])

    def test_variants_do_not_invent_a_canonical_print_price(self):
        capture, expansion = self.fixture([self.row('Example (V.1)', '1,50', 'v1'),
                                            self.row('Example (V.2)', '0,10', 'v2')])
        integrate(capture, expansion)
        prices = json.loads((expansion/'prices.json').read_text(encoding='utf-8'))
        self.assertIsNone(prices['references']['cards']['one']['from'])
        self.assertFalse(prices['available'])

    def test_ambiguous_names_are_kept_unmatched(self):
        cards = [{'id': 'one', 'name': 'Example', 'set': 'AAA'},
                 {'id': 'two', 'name': 'Example', 'set': 'BBB'}]
        capture, expansion = self.fixture([self.row('Example', '1,00')], cards)
        result = integrate(capture, expansion)
        self.assertEqual(result['cards'], 0)
        self.assertEqual(result['unmatched'], 1)

    def test_non_cardmarket_prices_are_rejected(self):
        row = self.row('Example', '1,00')
        row['href'] = 'https://www.cardmarket.com.attacker.test/Example'
        capture, expansion = self.fixture([row])
        with self.assertRaisesRegex(ValueError, 'Cardmarket'):
            integrate(capture, expansion)


if __name__ == '__main__':
    unittest.main()
