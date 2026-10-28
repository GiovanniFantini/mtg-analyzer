"""Import regressions for variant identity, two-faced cards and source boundaries."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import import_expansion_catalogs as importer


class CatalogImportTests(unittest.TestCase):
    def raw(self, identity='one', **updates):
        return {'id': identity, 'oracle_id': 'oracle', 'name': 'Front // Back',
                'set': 'tst', 'collector_number': '1', 'rarity': 'rare',
                'cmc': 3, 'color_identity': ['U'], 'legalities': {'modern': 'legal'},
                'finishes': ['nonfoil', 'foil'], 'prices': {'eur': '999'},
                'card_faces': [
                    {'name': 'Front', 'mana_cost': '{2}{U}', 'type_line': 'Creature',
                     'oracle_text': 'Flying', 'colors': ['U'],
                     'image_uris': {'normal': 'https://example.com/front.jpg'}},
                    {'name': 'Back', 'type_line': 'Land', 'oracle_text': '{T}: Add {U}.'}],
                **updates}

    def test_faces_and_legality_survive_without_external_prices(self):
        card = importer.normalize_printing(self.raw())
        self.assertEqual(card['image'], 'https://example.com/front.jpg')
        self.assertEqual(card['mana'], '{2}{U}')
        self.assertEqual(len(card['faces']), 2)
        self.assertEqual(card['legalities'], {'modern': 'legal'})
        self.assertNotIn('prices', card)
        self.assertNotIn('catalogId', card)

    def test_variants_map_to_one_card_per_set_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'expansions/star-trek'
            source.mkdir(parents=True)
            template = importer.ROOT / 'expansions/star-trek/expansion.json'
            (source / 'expansion.json').write_bytes(template.read_bytes())
            raw = [self.raw(), self.raw('two', collector_number='301'),
                   self.raw('bonus', set='bon'), self.raw()]
            with patch.object(importer, 'ROOT', root):
                directory = importer.create_expansion('test-set', 'Test', 'TST', raw)
                cards = json.loads((directory/'cards.json').read_text(encoding='utf-8'))
                prints = json.loads((directory/'printings.json').read_text(encoding='utf-8'))
                self.assertEqual(len(cards['cards']), 2)
                self.assertEqual(len(prints['cards']), 3)
                self.assertEqual({p['catalogId'] for p in prints['cards']}, {'one', 'bonus'})
                self.assertFalse(cards['complete'])
                products = json.loads((directory/'products.json').read_text())
                self.assertEqual(products['products'], {})
                with self.assertRaises(FileExistsError):
                    importer.create_expansion('test-set', 'Test', 'TST', raw)

    def test_printed_digital_identity_can_be_stored_only_on_faces(self):
        raw = self.raw(name='Peter Parker // Amazing Spider-Man')
        raw['card_faces'][0].update(name='Peter Parker', printed_name='Surris, Spidersilk Innovator',
                                    oracle_text='Transform Peter Parker.', printed_text='Transform Surris.')
        raw['card_faces'][1].update(name='Amazing Spider-Man', printed_name='Surris, Silk-Tech Vanguard',
                                    oracle_text='Amazing Spider-Man attacks.', printed_text='Surris attacks.')
        original = copy.deepcopy(raw)
        canonical = importer.normalize_printing(raw)
        self.assertEqual(canonical['name'], raw['name'])
        self.assertEqual(canonical['faces'][0]['printed_name'], 'Surris, Spidersilk Innovator')
        digital = importer.apply_printed_identity(canonical, raw)
        self.assertEqual(digital['name'], 'Surris, Spidersilk Innovator // Surris, Silk-Tech Vanguard')
        self.assertEqual(digital['full'], digital['name'])
        self.assertEqual(digital['oracleName'], raw['name'])
        self.assertEqual(digital['canonicalOracleText'], 'Transform Peter Parker.\n//\nAmazing Spider-Man attacks.')
        self.assertEqual(digital['text'], 'Transform Surris.\n//\nSurris attacks.')
        self.assertEqual(digital['faces'][1]['name'], 'Surris, Silk-Tech Vanguard')
        self.assertEqual(digital['faces'][1]['oracleName'], 'Amazing Spider-Man')
        self.assertEqual(digital['id'], raw['id'])
        self.assertEqual(digital['oracleId'], raw['oracle_id'])
        self.assertEqual(raw, original)


if __name__ == '__main__':
    unittest.main()
