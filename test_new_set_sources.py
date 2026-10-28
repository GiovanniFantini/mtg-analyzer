"""Source inventories must keep each registered expansion's research separate."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).parent/'.agents/skills/mtg-new-set/scripts/inventory_sources.py'
SPEC=importlib.util.spec_from_file_location('mtg_sources_inventory',SCRIPT)
INVENTORY=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INVENTORY)


class SourceInventoryTest(unittest.TestCase):
    def test_prefix_sets_do_not_share_research_sources(self):
        with tempfile.TemporaryDirectory(prefix='mtg-source-ownership-') as temporary:
            root=Path(temporary)
            entries=[]
            for slug in ('foundations','foundations-jumpstart'):
                folder=root/'expansions'/slug;folder.mkdir(parents=True)
                manifest=folder/'expansion.json'
                manifest.write_text(json.dumps({'id':slug,'datasets':{'sources':'sources.json'}}),encoding='utf-8')
                (folder/'sources.json').write_text('{}',encoding='utf-8')
                entries.append({'manifest':manifest.relative_to(root).as_posix()})
                research=root/'research'/(slug+'-20270101-audit');research.mkdir(parents=True)
                (research/'source-audit.json').write_text(json.dumps({'url':'https://example.test/'+slug}),encoding='utf-8')
            (root/'expansions.json').write_text(json.dumps(entries),encoding='utf-8')
            result=INVENTORY.inventory(root)['sets']
            for item in result:
                self.assertEqual([row['url'] for row in item['sources']],['https://example.test/'+item['id']])
                self.assertEqual(len(item['researchFiles']),1)

    def test_date_suffixes_and_numeric_registered_slug_are_unambiguous(self):
        slugs=['foundations','foundations-20270101']
        self.assertEqual(INVENTORY.research_owner('foundations-20270101-audit',slugs),'foundations')
        self.assertEqual(INVENTORY.research_owner('foundations-20270101-20270202',slugs),'foundations-20270101')
        self.assertIsNone(INVENTORY.research_owner('foundations-jumpstart-20270101',slugs))


if __name__=='__main__':
    unittest.main()
