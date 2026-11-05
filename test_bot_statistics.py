import copy
import unittest

from bot_statistics import payload, semantic


def fixture():
    cards = [{'id': str(i), 'catalogId': str(i), 'score': 1 + i / 4, 'basic': False} for i in range(12)]
    cards.append({'id': 'basic', 'catalogId': 'basic', 'score': None, 'basic': True})
    rows = [{'catalogId': str(i), 'metrics': {'games': 1000, 'wins': 450 + 20 * i,
                                             'inHandWinRate': 45 + 2 * i}} for i in range(12)]
    source = {'schemaVersion': 1, 'provider': '17Lands public datasets', 'url': 'https://www.17lands.com/public_datasets',
              'retrieved': '2026-11-05', 'rateUnit': 'percent', 'filters': {'event': 'PremierDraft'},
              'derivation': {'license': 'CC BY 4.0', 'datasetUrl': 'https://17lands-public.s3.amazonaws.com/test.csv.gz'},
              'metrics': {key: {'status': 'public'} for key in ('inHandWinRate', 'games', 'wins')}, 'cards': rows}
    return cards, {'draft': {'externalSources': {'public': source}}}, {'kind': 'draft', 'picksPerTurn': 1, 'product': 'play',
        'botPolicy': {'statisticsReference': {'population': 'MTG Arena', 'purpose': 'card-quality-prior', 'product': 'play', 'events': {'BO1': 'PremierDraft', 'BO3': 'TradDraft'}, 'provenance': {}}}}


class BotStatisticsTests(unittest.TestCase):
    def model(self, cards, stats, event):
        return payload(stats, cards, {c['id'] for c in cards}, event)

    def test_variants_share_evidence_and_free_basics_are_excluded(self):
        cards, stats, event = fixture()
        cards.append({**cards[0], 'id': 'variant'})
        result = self.model(cards, stats, event)['modes']['BO1']
        self.assertEqual(len(result['cards']), 12)
        self.assertEqual(result['coverage']['withEvidence'], 13)
        self.assertNotIn('basic', result['cards'])
        self.assertEqual(result['cards']['0']['games'], 1000)

    def test_event_and_match_populations_do_not_leak(self):
        cards, stats, event = fixture()
        self.assertNotIn('BO3', self.model(cards, stats, event)['modes'])
        traditional = copy.deepcopy(stats['draft']['externalSources']['public'])
        traditional['filters']['event'] = 'TradDraft'
        traditional['gameOne'] = {'cards': copy.deepcopy(traditional['cards'])}
        stats['draft']['externalSources']['traditional'] = traditional
        self.assertEqual(set(self.model(cards, stats, event)['modes']), {'BO1', 'BO3'})
        for changed in ({'kind': 'sealed', 'picksPerTurn': 0}, {'kind': 'draft', 'picksPerTurn': 2}):
            self.assertFalse(self.model(cards, stats, changed)['available'])
        traditional['filters']['event'] = 'QuickDraft'
        self.assertNotIn('BO3', self.model(cards, stats, event)['modes'])
        for changed in ({**event, 'product': 'different'}, {**event, 'botPolicy': {}}):
            self.assertFalse(self.model(cards, stats, changed)['available'])

    def test_traditional_main_quality_never_uses_post_sideboard_games(self):
        cards, stats, event = fixture()
        source = stats['draft']['externalSources']['public']
        source['filters']['event'] = 'TradDraft'
        self.assertFalse(self.model(cards, stats, event)['available'])
        source['gameOne'] = {'cards': copy.deepcopy(source['cards'])}
        source['colorContexts'] = {'WU': {'cards': copy.deepcopy(source['cards'])}}
        source['cards'][0]['metrics'] = {'games': 5000, 'wins': 4900, 'inHandWinRate': 98}
        result = self.model(cards, stats, event)['modes']['BO3']
        self.assertEqual(result['cohort'], 'game-one')
        self.assertEqual(result['cards']['0']['rate'], 45)
        self.assertEqual(result['cards']['0']['games'], 1000)
        self.assertEqual(result['cards']['0']['contexts'], {})

    def test_missing_small_invalid_and_locked_samples_are_not_win_rates(self):
        cards, stats, event = fixture()
        rows = stats['draft']['externalSources']['public']['cards']
        rows[0]['metrics'] = {'games': 0, 'wins': 0, 'inHandWinRate': None}
        rows[1]['metrics'] = {'games': 50, 'wins': 50, 'inHandWinRate': 100}
        rows[2]['metrics'] = {'games': 1000, 'wins': 1, 'inHandWinRate': 50}
        result = self.model(cards, stats, event)['modes']['BO1']
        for key in ('0', '1', '2'):
            self.assertNotIn(key, result['cards'])
        self.assertEqual(result['coverage']['editorialFallback'], 3)
        stats['draft']['externalSources']['public']['metrics']['inHandWinRate']['status'] = 'locked'
        self.assertFalse(self.model(cards, stats, event)['available'])

    def test_regularization_and_unit_conversion_preserve_ranking(self):
        cards, stats, event = fixture()
        result = self.model(cards, stats, event)['modes']['BO1']
        values = list(result['cards'].values())
        self.assertEqual([r['utility'] for r in values], sorted(r['utility'] for r in values))
        center = 100 * result['model']['center']
        for row in values:
            self.assertLessEqual(abs(row['estimate'] - center), abs(row['rate'] - center) + 1e-8)
        self.assertEqual(values[0]['rate'], 45)
        self.assertTrue(all(0 <= row['utility'] <= 5 for row in values))

    def test_sparse_evidence_respects_known_quality_and_large_samples_override_it(self):
        cards, stats, event = fixture()
        cards.append({'id': 'rare', 'catalogId': 'rare', 'score': 4.8, 'basic': False})
        rows = stats['draft']['externalSources']['public']['cards']
        rows.append({'catalogId': 'rare', 'metrics': {'games': 100, 'wins': 55, 'inHandWinRate': 55}})
        sparse = self.model(cards, stats, event)['modes']['BO1']['cards']['rare']
        self.assertGreater(sparse['priorRate'], sparse['rate'])
        self.assertGreater(sparse['estimate'], sparse['rate'])
        self.assertLess(sparse['estimate'], sparse['priorRate'])
        rows[-1]['metrics'] = {'games': 100000, 'wins': 55000, 'inHandWinRate': 55}
        large = self.model(cards, stats, event)['modes']['BO1']['cards']['rare']
        self.assertLess(abs(large['estimate'] - 55), abs(sparse['estimate'] - 55))
        self.assertGreater(large['reliability'], .99)

    def test_uniform_color_cohort_uplift_is_not_a_synergy_bonus(self):
        cards, stats, event = fixture()
        source = stats['draft']['externalSources']['public']
        context_rows = copy.deepcopy(source['cards'])
        for row in context_rows:
            row['metrics']['wins'] += 50
            row['metrics']['inHandWinRate'] += 5
        source['colorContexts'] = {'WU': {'cards': context_rows}}
        result = self.model(cards, stats, event)['modes']['BO1']
        for row in result['cards'].values():
            self.assertAlmostEqual(row['contexts']['WU']['adjustment'], 0)
            self.assertAlmostEqual(row['contexts']['WU']['utility'], row['utility'])
        context_rows[0]['metrics']['wins'] += 30
        context_rows[0]['metrics']['inHandWinRate'] += 3
        changed = self.model(cards, stats, event)['modes']['BO1']
        self.assertGreater(changed['cards']['0']['contexts']['WU']['adjustment'], 0)

    def test_replay_signature_ignores_provenance_but_tracks_functional_data(self):
        cards, stats, event = fixture()
        before = semantic(self.model(cards, stats, event))
        source = stats['draft']['externalSources']['public']
        source['url'] = 'https://www.17lands.com/updated-reference'
        source['retrieved'] = '2026-11-06'
        self.assertEqual(before, semantic(self.model(cards, stats, event)))
        source['cards'][0]['metrics']['wins'] += 1
        source['cards'][0]['metrics']['inHandWinRate'] += .1
        self.assertNotEqual(before, semantic(self.model(cards, stats, event)))


if __name__ == '__main__':
    unittest.main()
