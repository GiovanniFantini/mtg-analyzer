"""Atlas presentation must preserve the original manual-pool keys and routes."""
import json
import unittest
from pathlib import Path
from expansion_data import load_expansions, ROOT
from build_expansion import data_for_page, manual_pool_source, render_page


class AtlasMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expansions=load_expansions()
        cls.before=json.loads((ROOT/'research/atlas-unification-20261028/before-manifests.json').read_text(encoding='utf-8'))

    def test_all_registered_expansions_use_atlas(self):
        for e in self.expansions:
            with self.subTest(expansion=e.manifest['id']):
                self.assertEqual(e.manifest['presentation']['style'],'atlas')
                self.assertFalse(any('/preview/' in p.get('template','') for p in e.manifest['presentation']['pages'].values()))

    def test_original_storage_keys_and_urls_remain(self):
        by_id={e.manifest['id']:e for e in self.expansions}
        for ident,old in self.before.items():
            e=by_id[ident]
            for key,value in old['storage'].items():
                self.assertEqual(e.manifest['storage'][key],value)
            current={p['url'] for p in e.manifest['presentation']['pages'].values()}
            self.assertTrue(set(old['routes'].values())<=current)

    def test_only_catalog_payload_contains_full_card_analyses(self):
        e=self.expansions[0]
        self.assertIn('prospects',data_for_page(e,'gallery')['cards'][0])
        for page in ('analysis','combos','simulator'):
            self.assertTrue(all('prospects' not in c for c in data_for_page(e,page)['cards']))
        self.assertIn('prospects',e.cards[0], 'Payload pruning must not mutate the catalog.')

    def test_manual_workbenches_and_adapters_share_original_records(self):
        for e in self.expansions:
            if not e.manifest['storage'].get('poolPrefix'):continue
            for kind in ('draft','sealed'):
                source=manual_pool_source(e,kind)
                self.assertEqual(source['key'],e.manifest['storage']['poolPrefix']+e.default_event_id(kind)+'-v1')
                self.assertTrue(source['nested'])
            self.assertEqual(e.manifest['presentation']['pages']['workbench']['controllerPage'],'draft')
            self.assertEqual(e.manifest['presentation']['pages']['practice']['controllerPage'],'simulator')

    def test_duplicate_names_retain_every_original_identity_for_draft(self):
        e=next(e for e in self.expansions if e.manifest['code']=='OM1')
        data=data_for_page(e,'draft')
        shock=[c for c in e.cards if c['name']=='Shock']
        self.assertGreater(len(shock),1)
        self.assertEqual({c['id'] for c in data['poolSource']['identities'] if c['name']=='Shock'},{c['id'] for c in shock})
        self.assertEqual(sum(c['name']=='Shock' for c in data['poolCards']),1)

    def test_manual_and_shared_pages_keep_atlas_shell_and_controller_identity(self):
        e=next(e for e in self.expansions if e.manifest['id']=='star-trek')
        for key,controller in [('workbench','draft'),('practice','simulator'),('strategy','strategy')]:
            rendered=render_page(e,key,e.manifest['presentation']['pages'][key])
            self.assertIn('data-page="'+controller+'"',rendered)
            self.assertNotIn('site-layout trk-page',rendered)
        self.assertIn('atlas-manual',render_page(e,'workbench',e.manifest['presentation']['pages']['workbench']))


if __name__=='__main__':unittest.main()
