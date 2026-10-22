"""Contract tests for incomplete documents, invalid recipes and new expansions."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from expansion_data import ROOT, Expansion, load_expansions
from build_expansion import build
from build_expansion import availability_notice, catalog_data, data_for_page
from build_site import Links
from urllib.parse import urlsplit, unquote


class ExpansionTests(unittest.TestCase):
    def setUp(self):
        self.source=load_expansions()[0]
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)

    def fixture(self, mutate=lambda m,d:None):
        manifest=copy.deepcopy(self.source.manifest)
        data=copy.deepcopy(self.source.data)
        mutate(manifest,data)
        for key,path in self.source.manifest['datasets'].items():
            (self.directory/path).write_text(json.dumps(data[key]),encoding='utf-8')
        path=self.directory/'expansion.json'
        path.write_text(json.dumps(manifest),encoding='utf-8')
        return Expansion(path)

    def test_incomplete_is_explicit(self):
        preview=load_expansions()[1]
        self.assertTrue(preview.availability['catalog']['available'])
        self.assertFalse(preview.availability['draftTable']['available'])
        self.assertIn('Catalogo completo',preview.availability['draftTable']['missing'][0])

    def test_bad_recipe_is_rejected(self):
        def mutate(m,d):d['products']['products']['play']['collation']['recipe'][0]['branches'][0]['weight']=.8
        with self.assertRaisesRegex(ValueError,'pesi slot'):
            self.fixture(mutate)

    def test_group_count_is_checked(self):
        def mutate(m,d):d['products']['products']['play']['collation']['groups']['common'].pop()
        with self.assertRaisesRegex(ValueError,'numerosità'):
            self.fixture(mutate)

    def test_unknown_operation_is_rejected(self):
        def mutate(m,d):d['products']['products']['play']['collation']['recipe'][0]['op']='run-code'
        with self.assertRaisesRegex(ValueError,'operazione collazione'):
            self.fixture(mutate)

    def test_path_escape_is_rejected(self):
        def mutate(m,d):m['datasets']['cards']='../outside.json'
        with self.assertRaisesRegex(ValueError,'Percorso esterno'):
            self.fixture(mutate)

    def test_newer_schema_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'schemaVersion'):
            self.fixture(lambda m,d:m.update(schemaVersion=999))

    def test_extensions_are_allowed(self):
        e=self.fixture(lambda m,d:m.update(extensions={'future':{'value':3}}))
        self.assertEqual(e.manifest['extensions']['future']['value'],3)

    def test_changed_rules_disable_legacy_reinterpretation(self):
        e=self.fixture(lambda m,d:d['limited']['events']['draft'].update(picksPerTurn=2))
        self.assertFalse(e.draft_format()['legacyReplay'])
        self.assertNotEqual(e.draft_format()['revision'],self.source.draft_format()['revision'])

    def test_metadata_refresh_preserves_replay(self):
        def mutate(m,d):
            d['printings']['cards'][0]['image']='https://example.com/refreshed-image.jpg'
            d['limited']['events']['draft']['sources'].append('https://example.com/source')
            d['products']['products']['play']['assumptions'].append('Precisazione editoriale.')
            d['archetypes']['WU']['plan']='Testo editoriale aggiornato.'
        e=self.fixture(mutate)
        self.assertEqual(e.draft_format()['revision'],self.source.draft_format()['revision'])
        self.assertTrue(e.draft_format()['legacyReplay'])
        self.assertIn(self.source.manifest['legacyDraftRevision'],e.draft_format()['compatibleRevisions'])

    def test_missing_draft_rules_are_unavailable(self):
        e=self.fixture(lambda m,d:d['limited']['events'].pop('draft'))
        self.assertFalse(e.availability['draftTable']['available'])
        self.assertTrue(e.availability['sealedSimulator']['available'])

    def test_required_storage_keys_are_validated(self):
        with self.assertRaisesRegex(ValueError,'storage mancanti: draftPool'):
            self.fixture(lambda m,d:m['storage'].pop('draftPool'))

    def test_empty_containers_are_not_data(self):
        def mutate(m,d):
            d['statistics']={'draft':{'cards':[],'poolCards':[],'drill':{}}}
            d['discovery']={'cards':[],'previews':[]}
        e=self.fixture(mutate)
        self.assertFalse(e.availability['draftStatistics']['available'])
        self.assertFalse(e.availability['discovery']['available'])
        self.assertTrue(e.availability['pickGuide']['available'])
        self.assertTrue(data_for_page(e,'draft')['poolCards'])

    def test_orphan_printing_disables_simulation(self):
        def mutate(m,d):
            id_=d['products']['products']['play']['collation']['groups']['common'][0]
            next(p for p in d['printings']['cards'] if p['id']==id_)['full']='Unmapped card'
        e=self.fixture(mutate)
        self.assertFalse(e.availability['sealedSimulator']['available'])
        self.assertTrue(any('Stampa senza' in reason for reason in e.availability['sealedSimulator']['missing']))

    def test_null_sentiment_metadata_has_safe_counts(self):
        e=self.fixture(lambda m,d:d.update(sentiment={'meta':None,'cards':{}}))
        self.assertEqual(catalog_data(e)['sentimentMeta']['covered'],0)

    def test_missing_sections_show_their_notice_on_host_page(self):
        e=self.fixture(lambda m,d:d['guides'].pop('sealed'))
        self.assertIn('Guida Sealed: non disponibile',availability_notice(e,'gallery'))

    def test_disabled_atlas_tools_can_render_their_notice(self):
        def mutate(m,d):
            for key in ('catalog','analysis','combos'):m['features'][key]['requested']=False
        e=self.fixture(mutate);build(e,self.directory/'disabled')
        for name in ('Sealed','Analisi','Combo'):
            content=(self.directory/'disabled'/f'Reality-Fracture-{name}.html').read_text(encoding='utf-8')
            self.assertIn('non disponibile',content)

    def test_manifest_fields_match_schema_requirements(self):
        with self.assertRaisesRegex(ValueError,'manca date'):
            self.fixture(lambda m,d:m.pop('date'))

    def test_ui_references_are_validated(self):
        mutations=[lambda m,d:d['ui']['botExamples'].update(power='[[Unknown card]]'),
                   lambda m,d:d['ui'].update(drilldownCompare=['Unknown card']),
                   lambda m,d:d['ui']['drilldownFindings'][0].update(pair='XX')]
        for mutate in mutations:
            with self.subTest(mutate=mutate),self.assertRaisesRegex(ValueError,'ui'):
                self.fixture(mutate)

    def test_source_urls_are_escaped_once(self):
        from build_expansion import render_tokens
        e=self.fixture()
        url=e.data['sources']['links']['afc44a857abe']
        self.assertIn('&format=',url)
        rendered=render_tokens('<a href="{{source:afc44a857abe}}">Fonte</a>',e)
        self.assertIn('&amp;format=',rendered)
        self.assertNotIn('&amp;amp;',rendered)

    def test_missing_editorial_keys_fail_with_actionable_errors(self):
        from build_expansion import render_tokens
        e=self.fixture()
        with self.assertRaisesRegex(ValueError,'sources.links: absent'):
            render_tokens('{{source:absent}}',e)
        with self.assertRaisesRegex(ValueError,'guides.fragments: absent'):
            render_tokens('<h1>{{fragment:absent}}</h1>',e)

    def test_baits_accept_a_valid_card_face(self):
        from render_guides import render
        def mutate(m,d):
            card=next(c for c in d['cards']['cards'] if len(c.get('faces',[]))>1)
            d['guides']['pickBaits']['groups'][0]['cards'][0]['name']=card['faces'][-1]['name']
        e=self.fixture(mutate)
        self.assertIn('pick-baits',render(e,'pickBaits'))

    def test_impossible_recipe_counts_are_rejected(self):
        def replace(m,d):
            recipe=d['products']['products']['play']['collation']['recipe']
            next(rule for rule in recipe if rule['op']=='replace')['count']=100
        def unique(m,d):
            recipe=d['products']['products']['play']['collation']
            rule=next(rule for rule in recipe['recipe'] if rule.get('unique') and rule.get('count',1)>1)
            group=rule['branches'][0]['group']
            recipe['groups'][group]=recipe['groups'][group][:rule['count']-1]
            recipe.pop('expectedGroupCounts',None)
        for mutate in (replace,unique):
            with self.subTest(mutate=mutate),self.assertRaisesRegex(ValueError,'sufficienti|insufficiente'):
                self.fixture(mutate)

    def test_card_contract_and_optional_fields(self):
        def optional(m,d):
            for key in ('faces','full','basic'):d['cards']['cards'][0].pop(key,None)
            d['printings']['cards'][0].pop('full',None)
        e=self.fixture(optional)
        self.assertEqual(e.cards[0]['faces'],[])
        self.assertEqual(e.cards[0]['full'],e.cards[0]['name'])
        self.assertEqual(e.draft_format()['cards'][0]['full'],e.draft_format()['cards'][0]['name'])
        with self.assertRaisesRegex(ValueError,r'cards.json/.*number'):
            self.fixture(lambda m,d:d['cards']['cards'][0].pop('number'))

    def test_home_uses_registry_routes_and_additional_sets(self):
        from build_site import homepage
        primary=copy.deepcopy(self.source.manifest)
        primary.update(id='renamed',slug='renamed',name='Renamed Set')
        primary['presentation']['pages']['draft']['url']='new-draft.html'
        another=copy.deepcopy(primary);another.update(id='third-set',slug='third-set',name='Third Set')
        content=homepage([primary,another])
        self.assertIn('sets/renamed/new-draft.html',content)
        self.assertIn('sets/third-set/index.html',content)
        self.assertNotIn('sets/reality-fracture/',content)

    def test_exclusion_of_an_entire_pair_group_is_rejected(self):
        def mutate(m,d):
            product=d['products']['products']['play']
            recipe=product['collation'];a,b=recipe['partners'][0]
            recipe.update(groups={'pair':[a,b]},expectedGroupCounts={},recipe=[{'id':'pair','op':'pair','count':1,'branches':[{'weight':1,'group':'pair'}]},{'id':'third','op':'draw','count':1,'exclude':['pair'],'branches':[{'weight':1,'group':'pair'}]}])
            product['packSize']=3
        with self.assertRaisesRegex(ValueError,'exclude'):
            self.fixture(mutate)

    def test_guaranteed_exclusions_do_not_block_a_valid_recipe(self):
        def mutate(m,d):
            product=d['products']['products']['play'];recipe=product['collation']
            a,b=[p['id'] for p in d['printings']['cards'][:2]]
            recipe.update(groups={'a':[a],'both':[a,b]},expectedGroupCounts={},recipe=[{'id':'first','op':'draw','branches':[{'weight':1,'group':'a'}]},{'id':'second','op':'draw','exclude':['first'],'branches':[{'weight':1,'group':'both'}]},{'id':'third','op':'draw','exclude':['second'],'branches':[{'weight':1,'group':'a'}]}])
            product['packSize']=3
        self.fixture(mutate)

    def test_correlated_exclusions_are_not_rejected_by_upper_bounds(self):
        def mutate(m,d):
            product=d['products']['products']['play'];recipe=product['collation']
            a,b,c=list({p['full']:p['id'] for p in d['printings']['cards']}.values())[:3]
            recipe.update(groups={'ab':[a,b],'abc':[a,b,c]},expectedGroupCounts={},recipe=[
                {'id':'first','op':'draw','branches':[{'weight':1,'group':'ab'}]},
                {'id':'complement','op':'draw','count':2,'unique':True,'exclude':['first'],'branches':[{'weight':1,'group':'abc'}]},
                {'id':'sameAsFirst','op':'draw','exclude':['complement'],'branches':[{'weight':1,'group':'ab'}]},
                {'id':'other','op':'draw','exclude':['first','sameAsFirst'],'branches':[{'weight':1,'group':'ab'}]}])
            product['packSize']=5
        self.fixture(mutate)

    def test_pair_unique_counts_use_actual_pair_members(self):
        def configure(d,count,three_pairs):
            product=d['products']['products']['play'];recipe=product['collation']
            by_id={p['id']:p for p in d['printings']['cards']};pairs=[];seen=set()
            for a,b in recipe['partners']:
                names={by_id[a]['full'],by_id[b]['full']}
                if not names&seen:pairs.append((a,b));seen.update(names)
                if len(pairs)==3:break
            group=[*pairs[0],pairs[1][0],pairs[2][0]] if three_pairs else list(pairs[0])
            recipe.update(groups={'pairs':group},expectedGroupCounts={},recipe=[{'id':'pairs','op':'pair','count':count,'unique':True,'branches':[{'weight':1,'group':'pairs'}]}])
            product['packSize']=2*count
        self.fixture(lambda m,d:configure(d,3,True))
        with self.assertRaisesRegex(ValueError,'unique'):
            self.fixture(lambda m,d:configure(d,2,False))

    def test_sealed_has_its_own_product_requirements(self):
        def mutate(m,d):
            d['products']['products']['other']={'name':'Other','packSize':14,'collation':None}
            d['limited']['events']['sealed']['product']='other'
        e=self.fixture(mutate)
        self.assertTrue(e.availability['draftTable']['available'])
        self.assertFalse(e.availability['sealedSimulator']['available'])

    def test_another_expansion_uses_shared_build(self):
        def mutate(m,d):
            m.update(id='contract-test',name='Contract Test',code='TST')
            d['guides']['fragments']['set.title']='Contract Test'
            for page in m['presentation']['pages'].values():
                filename,*anchor=page['url'].split('#')
                page['url']='test-'+filename+('#'+anchor[0] if anchor else '')
        e=self.fixture(mutate)
        build(e,self.directory/'site')
        catalog=(self.directory/'site'/'test-Reality-Fracture-Sealed.html').read_text(encoding='utf-8')
        self.assertIn('const EXPANSION_CONFIG=',catalog)
        self.assertIn('<title>Contract Test',catalog)
        self.assertIn('test-Reality-Fracture-Combo.html',catalog)
        self.assertNotIn('href="Reality-Fracture-Combo.html',catalog)
        self.assertTrue((self.directory/'site/data/cards.json').exists())
        for page in (self.directory/'site').glob('*.html'):
            parser=Links();parser.feed(page.read_text(encoding='utf-8'))
            for ref in parser.refs:
                url=urlsplit(ref)
                if not url.scheme and url.path and '/' not in url.path:
                    self.assertTrue((page.parent/unquote(url.path)).exists(),(page.name,ref))


if __name__=='__main__':unittest.main()
