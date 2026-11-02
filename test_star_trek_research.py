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

    def test_complete_matching_and_explicit_printing_scope(self):
        ids = {c['id'] for c in self.cards}
        old = read(self.sources.get('previousCatalogSnapshot', 'star-trek-cards-20261022.json'))['cards']
        self.assertTrue({c['id'] for c in old} <= ids)
        self.assertEqual(len(ids), len(self.cards))
        self.assertTrue(self.doc['complete'])
        self.assertFalse(self.doc['printingCoverage']['complete'])
        for code, count in [('TRK', 311), ('SDS', 30)]:
            self.assertEqual({int(c['number']) for c in self.cards if c['set'] == code}, set(range(1, count + 1)))
        self.assertEqual(sum(len(c['prints']) for c in self.cards), self.doc['print_count'])
        registry = {s['id'] for s in self.sources['sources']}
        for card in self.cards:
            p = card['prospects']
            self.assertTrue(p['gameplayReview']['finding'])
            self.assertFalse(p['gameplayReview']['evidenceOfTournamentSuccess'])
            self.assertEqual(p['tournamentObservations'], [])
            self.assertTrue(set(p['sources']) <= registry)

    def test_models_do_not_become_limited_votes(self):
        scores = read(self.sources.get('automatedEvaluationsSnapshot', 'research/star-trek-20261027/standard-constructed-preview.json'))
        self.assertEqual(scores['unmatchedNames'], [])
        self.assertEqual(scores['matchedCards'], len(scores['cards']))
        ratings = read('expansions/star-trek/ratings.json')['cards']
        for rating in ratings.values():
            self.assertIsNone(rating.get('score'))
        reviews = read('research/star-trek-20261102/limited-reviews.json')
        expert = {r['catalogId']: r for r in reviews['cards']}
        for ident, rating in ratings.items():
            self.assertEqual(rating.get('community'), expert.get(ident, {}).get('value'))
            if ident in expert:
                self.assertEqual(rating['evidence'][0]['original'], expert[ident]['original'])
                self.assertEqual(rating['evidence'][0]['stars'], expert[ident]['value'])
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

    def test_active_catalog_preserves_only_documented_source_corrections(self):
        raw = read(self.sources['rawSnapshot'])['data']
        by_print = {(r['oracle_id'], r['set'].upper(), r['collector_number']): r for r in raw}
        for c in self.cards:
            r = by_print[c['id'], c['set'], c['number']]
            fixes = {v['field']: v for v in c.get('catalogCorrections', [])}
            for field, original in [('text', r.get('oracle_text', '')), ('type', r['type_line'].replace('\u2014', ':'))]:
                if c[field] != original:
                    self.assertIn(field, fixes, c['name'])
                    fix = fixes[field]
                    self.assertTrue((ROOT / fix['evidence']).is_file())
                    self.assertEqual(c[field], original.replace(fix['rawValue'], fix['correctedValue']))
            self.assertEqual(c['oracle'], c['text'])
            self.assertEqual(c['prospects']['oracle']['text'], c['text'])

    def test_historical_observations_still_match_their_original_captures(self):
        market = read('research/star-trek-20261027/cardmarket-normalized.json')
        edh = read('research/star-trek-20261027/edhrec-set-observations.json')
        for c in self.cards:
            p = c['prospects']
            original = market['primary'].get(c['id'])
            self.assertEqual(p['price']['from'], original['from'] if original else None)
            self.assertEqual(p['price']['variants'], market['variants'].get(c['id'], []))
            if original:
                self.assertEqual(p['price']['sourceReading'], original)
                self.assertEqual(p['price']['date'], '2026-10-27')
            self.assertEqual(p['commanderObservations'], [r for r in edh['rows'] if r.get('catalogId') == c['id']])

    def test_current_summary_uses_current_catalog_and_preserves_price_date(self):
        guides = read('expansions/star-trek/guides.json')['fragments']
        self.assertIn(str(len(self.cards)) + ' identità', guides['analysis.panel-1'])
        self.assertIn(str(self.doc['print_count']) + ' stampe', guides['analysis.panel-1'])
        self.assertIn(Path(self.sources['catalogSnapshot']).name, guides['method.panel-0'])
        self.assertNotIn('Nessun minimo Cardmarket verificato', guides['method.panel-1'])
        self.assertIn('rilevati il 27 ottobre', guides['method.panel-1'])

    def test_every_identity_has_specific_assessment_and_sds_has_no_borrowed_grade(self):
        self.assertEqual(self.sources['coverage']['specificEditorialNotes'], len(self.cards))
        self.assertEqual(sum(c.get('community') is not None for c in self.cards), 306)
        for card in self.cards:
            self.assertEqual(card['why'], card['prospects']['gameplayReview']['finding'])
            if card['set'] == 'SDS':
                self.assertIsNone(card.get('community'))
                self.assertNotIn('limitedReview', card['prospects'])
            for note in card['prospects'].get('researchNotes', []):
                self.assertTrue(note.get('context'))
                self.assertTrue(note.get('date'))

    def test_commander_catalog_is_separate_and_does_not_claim_competitive_coverage(self):
        appendix = read('research/star-trek-20261102/commander-appendix.json')
        self.assertEqual(appendix['catalogCards'], 336)
        self.assertEqual(len({r['oracleId'] for r in appendix['cards']}), 336)
        for card in appendix['cards']:
            self.assertEqual(card['scope'], 'commander_appendix')
            self.assertIsNone(card['cedhResults'])
            self.assertIsNone(card['price'])
        self.assertFalse(any(c['set'] == 'TRC' for c in self.cards))

    def test_written_guides_are_really_available(self):
        from expansion_data import Expansion
        expansion = Expansion(ROOT / 'expansions/star-trek/expansion.json')
        for feature in ('sealedGuide', 'draftGuide', 'pickGuide', 'pickDecisions', 'draftCombos'):
            self.assertTrue(expansion.availability[feature]['available'], feature)
        self.assertFalse(expansion.availability['draftTable']['available'])


if __name__ == '__main__':
    unittest.main()
