"""Integrity checks for the dated Star Trek research import."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


class StarTrekResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = read('expansions/star-trek/cards.json')
        cls.cards = cls.doc['cards']
        cls.sources = read('expansions/star-trek/sources.json')['research']

    def test_complete_matching_without_claiming_complete_catalog(self):
        ids = {c['id'] for c in self.cards}
        old = read('star-trek-cards-20261022.json')['cards']
        self.assertTrue({c['id'] for c in old} <= ids)
        self.assertEqual(len(ids), len(self.cards))
        self.assertFalse(self.doc['complete'])
        self.assertEqual(sum(len(c['prints']) for c in self.cards), self.doc['print_count'])
        registry = {s['id'] for s in self.sources['sources']}
        for card in self.cards:
            p = card['prospects']
            self.assertTrue(p['gameplayReview']['finding'])
            self.assertFalse(p['gameplayReview']['evidenceOfTournamentSuccess'])
            self.assertEqual(p['tournamentObservations'], [])
            self.assertTrue(set(p['sources']) <= registry)

    def test_models_do_not_become_limited_votes(self):
        scores = read('research/star-trek-20261027/standard-constructed-preview.json')
        self.assertEqual(scores['unmatchedNames'], [])
        self.assertEqual(scores['matchedCards'], len(scores['cards']))
        ratings = read('expansions/star-trek/ratings.json')['cards']
        for rating in ratings.values():
            self.assertIsNone(rating.get('score'))
            self.assertIsNone(rating.get('community'))
        self.assertEqual(sum(bool(c['prospects'].get('automatedEvaluations')) for c in self.cards), scores['matchedCards'])

    def test_forecasts_preserve_snapshot_legalities(self):
        for c in self.cards:
            formats = c['prospects']['formats']
            for f in ('standard', 'pauper', 'commander'):
                self.assertEqual(formats[f]['legality'], c['legalities'].get(f, 'unknown'))
            if c['set'] == 'SDS':
                self.assertNotIn('releaseEligibility', formats['standard'])
            if 'releaseEligibility' in formats['pauper']:
                self.assertEqual((c['set'], c['rarity']), ('TRK', 'common'))

    def test_price_identity_and_missing_finishes(self):
        found = 0
        for c in self.cards:
            p = c['prospects']['price']
            self.assertEqual(p['sourceLabel'], 'Cardmarket')
            self.assertIsNone(p['nonfoil'])
            self.assertIsNone(p['foil'])
            self.assertIsNone(p['comparison']['changePct'])
            if p['from'] is not None:
                found += 1
                self.assertGreater(p['from'], 0)
                self.assertTrue(p['url'].startswith('https://www.cardmarket.com/'))
            if p['printingId']:
                self.assertEqual(p['sourceReading']['collectorNumber'], c['number'])
        self.assertEqual(found, self.sources['coverage']['primaryCardmarketMinima'])

    def test_commander_appendix_does_not_enter_limited_catalog(self):
        appendix = read('star-trek-commander-observations-20261027.json')
        ids = {c['id'] for c in self.cards}
        for r in appendix['rows']:
            self.assertEqual(r['scope'], 'commander_appendix')
            self.assertNotIn(r.get('catalogId'), ids)
        for c in self.cards:
            for r in c['prospects']['commanderObservations']:
                self.assertEqual(r['catalogId'], c['id'])
                self.assertTrue(r['decksDisplay'])


if __name__ == '__main__':
    unittest.main()
