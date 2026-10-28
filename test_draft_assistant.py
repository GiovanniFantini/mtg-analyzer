"""Draft pool identities must follow the catalog even when statistics are dated."""
import copy
import unittest
from build_expansion import data_for_page
from expansion_data import load_expansions


class DraftAssistantDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expansion = load_expansions()[0]

    def test_dated_pool_snapshot_cannot_override_card_facts_or_remove_cards(self):
        expansion = copy.deepcopy(self.expansion)
        card = expansion.cards[0]
        name = card['full']
        expansion.data['statistics']['draft']['poolCards'] = [
            {'name': name, 'cost': 'obsolete', 'oracle': 'obsolete', 'gih': .61,
             'n': 13, 'alsa': 2, 'compatibleExtra': 'retained'},
            {'name': 'Obsolete card absent from catalog', 'gih': .9}]
        data = data_for_page(expansion, 'draft')
        self.assertEqual({c['name'] for c in data['poolCards']}, {c['name'] for c in data['assistant']['cards']})
        current = next(c for c in data['poolCards'] if c['name'] == name)
        self.assertEqual((current['cost'], current['oracle']), (card['cost'], card['oracle']))
        self.assertEqual((current['gih'], current['n'], current['alsa']), (.61, 13, 2))
        self.assertEqual(current['compatibleExtra'], 'retained')

    def test_missing_statistics_do_not_invent_win_rates(self):
        expansion = copy.deepcopy(self.expansion)
        expansion.data['statistics'] = {}
        data = data_for_page(expansion, 'draft')
        self.assertEqual(len(data['poolCards']), len(expansion.cards))
        self.assertTrue(all(c['gih'] is None and c['n'] == 0 for c in data['poolCards']))

    def test_assistant_keeps_canonical_oracle_for_pool_analysis(self):
        data = data_for_page(self.expansion, 'draft')
        canonical = {c['full']: c['oracle'] for c in self.expansion.cards}
        self.assertTrue(data['assistant']['cards'])
        for card in data['assistant']['cards']:
            self.assertEqual(card['oracle'], canonical[card['name']])


if __name__ == '__main__':
    unittest.main()
