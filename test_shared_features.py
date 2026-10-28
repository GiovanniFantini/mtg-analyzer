"""Ready data must reach shared renderers regardless of the chosen presentation."""
import copy
import unittest
from expansion_data import load_expansions
from build_expansion import prepare_shared_pages, render_page, render_tokens, data_for_page


class SharedFeaturesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ready, cls.preview = load_expansions()

    def fixture(self):
        expansion=copy.deepcopy(self.ready)
        expansion.manifest['presentation']=copy.deepcopy(self.preview.manifest['presentation'])
        expansion.manifest['storage']=copy.deepcopy(self.preview.manifest['storage'])
        return expansion

    def test_ready_preview_features_use_shared_renderers(self):
        expansion=self.fixture()
        prepare_shared_pages(expansion)
        pages=expansion.manifest['presentation']['pages']
        for key in ('draft','combos','discovery','analysis','simulator'):
            self.assertEqual(pages[key]['template'],'templates/atlas/'+key+'.html')
            rendered=render_page(expansion,key,pages[key])
            self.assertNotIn('__DATA__',rendered)
            self.assertIn('site-content',rendered)
        self.assertIn('practice',pages)
        self.assertIn('workbench',pages)
        self.assertIn('data-page="draft"',render_page(expansion,'workbench',pages['workbench']))
        self.assertIn('strategy',pages)

    def test_missing_preview_data_keeps_existing_tools(self):
        expansion=copy.deepcopy(self.preview)
        prepare_shared_pages(expansion)
        pages=expansion.manifest['presentation']['pages']
        self.assertEqual(pages['draft']['template'],'templates/preview/draft.html')
        self.assertEqual(pages['simulator']['template'],'templates/preview/simulator.html')
        rendered=render_page(expansion,'strategy',pages['strategy'])
        self.assertIn('guides.fragments.gallery.strategy',rendered)

    def test_renamed_sealed_event_reaches_renderer(self):
        expansion=self.fixture()
        events=expansion.data['limited']['events']
        events['weekend-pool']=events.pop('sealed')
        self.assertIn('buste',render_tokens('{{sealedRules}}',expansion))
        self.assertEqual(data_for_page(expansion,'simulator')['format']['id'],events['weekend-pool']['id'])

    def test_preview_combo_uses_the_existing_manual_sealed_pool(self):
        expansion=self.fixture()
        expansion.manifest['storage']=copy.deepcopy(self.preview.manifest['storage'])
        prepare_shared_pages(expansion)
        source=data_for_page(expansion,'combos')['poolSource']
        self.assertEqual(source['key'],expansion.manifest['storage']['poolPrefix']+'sealed-v1')
        self.assertTrue(source['nested'])
        self.assertEqual(render_tokens('{{route:workbench}}',expansion),'draft-workbench.html')
        self.assertEqual(render_tokens('{{route:practice}}',self.preview),self.preview.manifest['presentation']['pages']['simulator']['url'])

    def test_missing_statistics_do_not_claim_catalog_date_or_provider(self):
        expansion=self.fixture()
        expansion.data['statistics']={}
        expansion.availability=expansion.capabilities()
        data=data_for_page(expansion,'draft')
        self.assertFalse(data['statisticsAvailable'])
        self.assertEqual(data['date'],'')
        self.assertEqual(data['statisticsDate'],'')
        self.assertEqual(data['catalogDate'],expansion.data['cards']['date'])
        self.assertIn('non disponibili',render_tokens('{{draftAttribution}}',expansion))

    def test_missing_sealed_guide_has_one_availability_notice(self):
        expansion=copy.deepcopy(self.preview)
        prepare_shared_pages(expansion)
        rendered=render_page(expansion,'strategy',expansion.manifest['presentation']['pages']['strategy'])
        self.assertEqual(rendered.count('class="notice feature-availability"'),1)

    def test_unavailable_sentiment_is_hidden_in_static_analysis(self):
        expansion=copy.deepcopy(self.preview)
        prepare_shared_pages(expansion)
        rendered=render_page(expansion,'analysis',expansion.manifest['presentation']['pages']['analysis'])
        self.assertRegex(rendered,r'<section[^>]*id="sentiment"[^>]*hidden')
        self.assertNotIn('Le recensioni giapponesi',rendered)
        self.assertNotIn('Le cinque rimozioni',rendered)

    def test_discovery_can_use_catalog_previews_and_legacy_watch_ids(self):
        expansion=copy.deepcopy(self.ready)
        expansion.data['discovery'].pop('previews',None)
        data=data_for_page(expansion,'discovery')
        names={c['name'] for c in data['previews']}
        selected={c['name'] for c in expansion.data['discovery']['cards']}
        self.assertTrue(selected.intersection(c['name'] for c in expansion.cards).issubset(names))
        self.assertNotIn('previews',expansion.data['discovery'])
        card=expansion.cards[0]
        self.assertEqual(data['watchNames'][card['id']],card['name'])


if __name__=='__main__':
    unittest.main()
