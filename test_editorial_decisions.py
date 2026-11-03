import json
import tempfile
import unittest
from pathlib import Path

from integrate_editorial_decisions import integrate


class EditorialDecisionTests(unittest.TestCase):
    def test_repeat_preserves_existing_data_and_uses_manifest_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = {
                'cards.json': {'cards': [{'id': 'stable-id', 'name': 'Example', 'score': 3,
                                         'prospects': {'price': {'from': 2}, 'custom': 'keep'}}]},
                'guides.json': {'fragments': {'analysis.copy-0': '<p>Keep</p>'}},
                'sources.json': {'research': {'existing': 'keep'}},
                'expansion.json': {'presentation': {'pages': {'gallery': {'url': 'cards.html'}}}},
                'input.json': {'date': '2026-11-03', 'kind': 'editorial', 'scope': 'sample',
                               'cards': [{'name': 'Example', 'context': 'Draft', 'verdict': 'Useful',
                                          'sections': [{'title': 'Plan', 'text': 'Support'}]}]},
            }
            for name, value in docs.items():
                (root / name).write_text(json.dumps(value), encoding='utf-8')
            integrate(root, root / 'input.json')
            first = {name: (root / name).read_bytes() for name in docs}
            integrate(root, root / 'input.json')
            self.assertEqual(first, {name: (root / name).read_bytes() for name in docs})
            card = json.loads((root / 'cards.json').read_text(encoding='utf-8'))['cards'][0]
            self.assertEqual(card['score'], 3)
            self.assertEqual(card['prospects']['price'], {'from': 2})
            self.assertEqual(card['prospects']['custom'], 'keep')
            fragment = json.loads((root / 'guides.json').read_text(encoding='utf-8'))['fragments']['analysis.copy-0']
            self.assertIn('cards.html?card=stable-id', fragment)
            self.assertTrue(fragment.startswith('<p>Keep</p>'))
            # A bad second row must leave every active file untouched.
            for bad in ['Unknown', 'Example']:
                source = docs['input.json']
                source['cards'] = source['cards'][:1] + [{**source['cards'][0], 'name': bad}]
                (root / 'input.json').write_text(json.dumps(source), encoding='utf-8')
                with self.assertRaises(ValueError):
                    integrate(root, root / 'input.json')
                for name in ['cards.json', 'guides.json', 'sources.json']:
                    self.assertEqual((root / name).read_bytes(), first[name])


if __name__ == '__main__':
    unittest.main()
