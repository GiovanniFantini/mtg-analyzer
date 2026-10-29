import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

from bot_profiles import describe, payload, validate_config
from expansion_data import load_expansions


class BotProfilesTests(unittest.TestCase):
    def test_mana_and_alternative_uses_are_structured(self):
        for oracle in ('Deal 3 damage to any target.', 'This spell deals 3 damage to any target.',
                       'This spell deals X damage to target creature.',
                       "Target creature you control fights target creature you don't control.",
                       'Destroy target creature.', 'Exile target creature.'):
            self.assertIn('interaction', describe({'cost': '{R}', 'oracle': oracle})['roles'], oracle)
        for oracle in ('Target creature an opponent controls gets -3/-3 until end of turn.',
                       "Enchanted creature can't attack or block.",
                       "Enchanted creature loses all abilities and doesn't untap during its controller's untap step.",
                       'Put X -1/-1 counters on up to one target creature.',
                       'All creatures get -3/-3 until end of turn.',
                       'Tap up to that many target creatures and put a stun counter on each of them.',
                       'Whenever a creature attacks you or a planeswalker you control, it gets -5/-0 until end of turn.'):
            self.assertIn('interaction', describe({'cost': '{B}', 'oracle': oracle})['roles'], oracle)
        for text in ('Exile up to one target card from a graveyard.', "Exile all cards from target player's graveyard."):
            self.assertIn('sideboard', describe({'cost': '{B}', 'oracle': text})['roles'])
        for text in ('Exile four other cards from your graveyard.', 'Exile this card from your graveyard: Draw a card.'):
            self.assertNotIn('sideboard', describe({'cost': '{B}', 'oracle': text})['roles'])
        for text in ('Untap target creature.', 'Tap target creatures you control.',
                     "Return target creature you control to its owner's hand.",
                     'Exile target creature you control, then return it to the battlefield.',
                     'Exile target card from a graveyard.', 'This spell deals 2 damage to target player.',
                     "This creature deals 1 damage to that creature's controller."):
            self.assertNotIn('interaction', describe({'cost': '{W}', 'oracle': text})['roles'], text)
        for text in ('This spell deals 5 damage to target black or green creature or planeswalker.',
                     'This card deals 4 damage to target attacking or blocking creature.',
                     'Target opponent reveals their hand. That player discards a card.'):
            self.assertIn('interaction', describe({'cost': '{R}', 'oracle': text})['roles'], text)
        artifact = describe({'cost': '{2}', 'type': 'Artifact Creature', 'oracle': ''})
        self.assertTrue(artifact['curve']['artifact'])
        p = describe({'oracle': 'Flying\nMountaincycling {2}', 'cost': '{5}{U}', 'mv': 6, 'creature': True})
        self.assertEqual(p['mana']['cycling'], [{'kind': 'subtype', 'type': 'Mountain', 'cost': '{2}'}])
        self.assertIn('evasion', p['roles'])
        self.assertEqual(p['reference']['status'], 'unsupported')
        restricted = describe({'oracle': '{T}: Add {R}. Spend this mana only to cast creature spells.', 'cost': '{G}'})
        self.assertTrue(restricted['mana']['abilities'][0]['restricted'])
        modal = describe({'oracle': '', 'cost': '{2}{W}', 'mv': 3, 'creature': True,
                          'faces': [{'type_line': 'Creature'}, {'type_line': 'Land', 'oracle_text': '{T}: Add {W}.'}]})
        self.assertEqual(modal['mana']['alternativeLand']['colors'], ['W'])
        fetch = describe({'land': True, 'cost': '', 'oracle': '{T}, Sacrifice this land: Search your library for a basic land card, put it onto the battlefield tapped, then shuffle.'})
        self.assertEqual(fetch['mana']['fetch']['kind'], 'basic')
        self.assertIn('fixing', fetch['roles'])
        self.assertEqual(describe({'cost': '{3}{G} // {1}{G}', 'mv': 4, 'oracle': ''})['status'], 'unsupported')

    def test_policy_coverage_is_uniform_and_does_not_change_legacy_revision(self):
        e = load_expansions()[0]
        fmt = e.draft_format()
        self.assertTrue(fmt['botPolicy']['available'])
        self.assertFalse(fmt['botPolicy']['coverage']['synergies'])
        # Broader negative-effect lexicon is an audit, not a role classifier:
        # self-restrictions need explicit reviewed exceptions with Oracle hashes.
        exceptions = json.loads((Path(__file__).parent / 'tests/fixtures/draft-interaction-audit.json').read_text(encoding='utf-8'))
        reviewed = set()
        for card in fmt['cards']:
            text = card.get('oracle', '')
            if card.get('land') or not re.search(r'gets? -|can.t attack|can.t block|doesn.t untap|-1/-1 counter', text, re.I):
                continue
            if 'interaction' not in fmt['botPolicy']['profiles'][card['id']]['roles']:
                self.assertIn(card['id'], exceptions, card['name'])
                self.assertEqual(exceptions[card['id']]['oracleHash'], hashlib.sha256(text.encode()).hexdigest())
                reviewed.add(card['id'])
        self.assertEqual(reviewed, set(exceptions))
        judgments = json.loads((Path(__file__).parent / 'tests/fixtures/draft-interaction-positive-negative-audit.json').read_text(encoding='utf-8'))
        audit_lexicon = r'\buntap target\b|exile target[^.\n]*(?:you control|graveyard)|return target[^.\n]*you control|deals? (?:\d+|X) damage to target (?:player|opponent)|damage[^.\n]*to that (?:creature|planeswalker|permanent).s (?:controller|owner)'
        candidates = {c['id']: c for c in fmt['cards'] if 'interaction' in fmt['botPolicy']['profiles'][c['id']]['roles'] or re.search(audit_lexicon, c['oracle'], re.I)}
        self.assertEqual(set(candidates), set(judgments))
        for printing, card in candidates.items():
            self.assertEqual(hashlib.sha256(card['oracle'].encode()).hexdigest(), judgments[printing]['oracleHash'])
            self.assertEqual('interaction' in fmt['botPolicy']['profiles'][printing]['roles'], judgments[printing]['interaction'], card['name'])
        sideboard = json.loads((Path(__file__).parent / 'tests/fixtures/draft-sideboard-audit.json').read_text(encoding='utf-8'))
        candidates = {c['id']: c for c in fmt['cards'] if re.search(r'exile[^.\n]*graveyard', c.get('oracle', ''), re.I)}
        self.assertEqual(set(sideboard), set(candidates))
        for printing, card in candidates.items():
            self.assertEqual(sideboard[printing]['oracleHash'], hashlib.sha256(card['oracle'].encode()).hexdigest())
            self.assertEqual('sideboard' in fmt['botPolicy']['profiles'][printing]['roles'], sideboard[printing]['sideboard'])
        old_revision = fmt['revision']
        # Images, source text and annotation provenance are nonfunctional.
        e.data['printings']['cards'][0]['image'] = 'https://example.com/new.png'
        self.assertEqual(e.draft_format()['botPolicy']['revision'], fmt['botPolicy']['revision'])
        e.data['limited']['events']['draft']['botPolicy'] = {'schemaVersion': 1, 'match': 'BO1'}
        updated = e.draft_format()
        self.assertEqual(updated['revision'], old_revision)
        self.assertNotEqual(updated['botPolicy']['revision'], fmt['botPolicy']['revision'])

    def test_invalid_descriptors_rejected(self):
        with self.assertRaisesRegex(ValueError, 'carta sconosciuta'):
            validate_config({'schemaVersion': 1, 'cards': {'unknown': {}}}, [])
        with self.assertRaisesRegex(ValueError, 'parametro'):
            validate_config({'schemaVersion': 1, 'relations': [{'id': 'life', 'referenceSupport': 3, 'saturation': 8, 'strength': float('nan')}]}, [])

    def test_incomplete_minimum_blocks_all_new_profiles(self):
        event = {'minDeckSize': 40, 'extraBasicLands': True}
        cards = [{'id': 'a', 'cost': '{W}', 'mv': 1, 'oracle': '', 'score': None}]
        # Artifact status is functional for reductions, unlike provenance.
        original = [{'id': 'a', 'cost': '{2}', 'mv': 2, 'oracle': '', 'score': 3, 'type': 'Creature'}]
        revised = copy.deepcopy(original)
        revised[0]['type'] = 'Artifact Creature'
        self.assertNotEqual(payload(original, {'a'}, event, {}, True)['revision'],
                            payload(revised, {'a'}, event, {}, True)['revision'])
        self.assertFalse(payload(cards, {'a'}, event, {}, True)['available'])
        self.assertFalse(payload([{**cards[0], 'score': 3}], {'a'}, event, {}, False)['available'])

    def test_manual_mana_and_curve_overrides_fail_before_runtime(self):
        invalid = [
            {'mana': {'alternativeLand': {'tapped': True}}},
            {'mana': {'alternativeLand': {'colors': ['WR'], 'tapped': False, 'restricted': False}}},
            {'mana': {'fetch': {'kind': 'basic', 'cost': '2', 'readyTurn': 2, 'tapped': False, 'restricted': False}}},
            {'mana': {'fetch': {'kind': 'basic', 'cost': ['Z'], 'readyTurn': 2, 'tapped': False, 'restricted': False}}},
            {'mana': {'fetch': {'kind': 'basic', 'cost': [], 'readyTurn': True, 'tapped': False, 'restricted': False}}},
            {'mana': {'subtypes': 'Mountain'}}, {'mana': {'subtypes': ['Unknown']}},
            {'mana': {'tapped': 1}}, {'mana': {'conditional': 'false'}},
            {'mana': {'abilities': {}}}, {'mana': {'abilities': [None]}},
            {'mana': {'cycling': [None]}}, {'mana': {'cycling': [{'kind': 'basic', 'type': 'Mountain', 'cost': '{2}'}]}},
            {'curve': {'reduction': 1}}, {'curve': {'reductionResource': 'bananas'}},
            {'curve': {'power': True}}, {'curve': {'toughness': '2'}},
            {'curve': {'attacker': None}}, {'curve': {'nominal': float('nan')}},
        ]
        for override in invalid:
            with self.subTest(override=override), self.assertRaises(ValueError):
                validate_config({'schemaVersion': 1, 'cards': {'a': {'status': 'supported', 'provenance': {}, **override}}}, ['a'])
        with self.assertRaisesRegex(ValueError, 'risorsa'):
            validate_config({'schemaVersion': 1, 'relations': [{'id': 'life', 'referenceSupport': 3, 'saturation': 8, 'strength': 1, 'resource': []}]}, [])
        validate_config({'schemaVersion': 1, 'cards': {'a': {'status': 'supported', 'provenance': {},
            'mana': {'alternativeLand': {'colors': ['R'], 'tapped': False, 'restricted': False},
                     'fetch': {'kind': 'basic', 'cost': ['2', 'T'], 'readyTurn': 3, 'tapped': True, 'restricted': False}},
            'curve': {'power': -1, 'toughness': None, 'reductionResource': 'unsupported'}}}}, ['a'])

    def test_partial_relations_disable_both_directions(self):
        event = {'minDeckSize': 40, 'extraBasicLands': True}
        cards = [{'id': x, 'cost': '{W}', 'mv': 1, 'oracle': '', 'score': 3} for x in ('a', 'b')]
        configured = {'schemaVersion': 1, 'relations': [{'id': 'life', 'referenceSupport': 3, 'strength': .6, 'saturation': 8}],
                      'cards': {'a': {'synergy': {'status': 'supported', 'enablers': {}, 'payoffs': {'life': 1}},
                                      'reference': {'status': 'supported', 'context': 'ordinary support'}}}}
        value = payload(cards, {'a', 'b'}, event, configured, True)
        self.assertTrue(value['available'])
        self.assertFalse(value['coverage']['synergies'])


if __name__ == '__main__':
    unittest.main()
