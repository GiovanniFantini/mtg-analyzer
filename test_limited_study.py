import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from integrate_limited_study import integrate, TIERS
from expansion_data import Expansion
from render_guides import render
from build_expansion import render_page

ROOT=Path(__file__).resolve().parent
FOLDER=ROOT/'expansions/star-trek'
STUDY=ROOT/'research/star-trek-limited-20261103'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


class LimitedStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards=read(FOLDER/'cards.json')['cards']
        cls.by_id={c['id']:c for c in cls.cards}

    def test_complete_common_uncommon_and_separate_contexts(self):
        expected=[c for c in self.cards if c['set']=='TRK' and c['rarity'] in ('common','uncommon') and not c['basic']]
        self.assertEqual(len(expected),201)
        self.assertEqual(sum(c['rarity']=='common' for c in expected),91)
        for c in expected:
            a=c['prospects']['limitedAnalysis']
            self.assertFalse(a['observedWinRates'])
            self.assertIn(a['draft']['tier'],TIERS)
            self.assertIn(a['sealed']['tier'],TIERS)
            self.assertNotEqual(a['draft']['note'],a['sealed']['note'])
            self.assertTrue(a['partners'])
            self.assertTrue(set(a['partners'])<={x['name'] for x in self.cards})

    def test_attribution_scales_zero_and_adopted_grades(self):
        research=read(FOLDER/'sources.json')['research']
        snapshot=read(ROOT/research['limitedReviewRefresh']['snapshot']) if research.get('limitedReviewRefresh') else read(STUDY/'draftsim-reviews.json')
        ratings=read(FOLDER/'ratings.json')['cards']
        old={r['catalogId']:r for r in read(ROOT/'research/star-trek-20261102/limited-reviews.json')['cards']}
        self.assertEqual(snapshot['matchedCards'],336)
        self.assertEqual(snapshot['unmatched'],[])
        self.assertEqual(snapshot['missing'],[])
        self.assertTrue(any(r['value']==0 for r in snapshot['cards']))
        for r in snapshot['cards']:
            c=self.by_id[r['catalogId']]
            current=next(x for x in c['prospects']['limitedReviews'] if x['source']==snapshot['source'])
            self.assertEqual(current['value'],r['value'])
            self.assertEqual(current['scaleMax'],10)
            self.assertEqual(ratings[c['id']].get('community'),old.get(c['id'],{}).get('value'))
            self.assertEqual(ratings[c['id']].get('engineSource'),'draftsim-bot-20261109')
            if c['set']=='SDS':
                self.assertNotIn('limitedReview',c['prospects'])
                self.assertEqual(c['prospects']['limitedAnalysis']['date'],'2026-11-09')

    def test_game_changers_and_real_sequence_references(self):
        impact=[c for c in self.cards if c['prospects'].get('limitedImpact')]
        self.assertEqual(len(impact),42)
        names={c['name'] for c in self.cards}
        for c in impact:
            a=c['prospects']['limitedImpact']
            self.assertTrue(a['draft'] and a['sealed'] and a['limit'])
            self.assertTrue(set(a['before']+a['after'])<=names)
        packages=read(FOLDER/'guides.json')['draftCombos']['packages']
        self.assertEqual(len(packages),26)
        self.assertEqual(sum(p.get('id','').startswith('limited-20261103-') for p in packages),16)
        for p in packages:self.assertTrue(set(p['cards'])<=names)
        self.assertEqual(read(FOLDER/'combos.json'),[])

    def test_offline_repeat_is_identical_and_preserves_unrelated_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)
            names=['cards','ratings','sources','guides']
            for n in names:shutil.copy2(FOLDER/(n+'.json'),target/(n+'.json'))
            before=read(target/'cards.json')
            integrate(target,STUDY)
            self.assertNotIn('senza WR osservate',read(target/'guides.json')['fragments']['draft.copy-0'])
            first={n:hashlib.sha256((target/(n+'.json')).read_bytes()).hexdigest() for n in names}
            integrate(target,STUDY)
            self.assertEqual(first,{n:hashlib.sha256((target/(n+'.json')).read_bytes()).hexdigest() for n in names})
            self.assertEqual(before,read(target/'cards.json'))

    def test_invalid_coverage_does_not_write(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'set';target.mkdir()
            source=Path(temp)/'study';shutil.copytree(STUDY,source)
            for n in ['cards','ratings','sources','guides']:shutil.copy2(FOLDER/(n+'.json'),target/(n+'.json'))
            bad=read(source/'editorial.json');bad['cards'].pop();(source/'editorial.json').write_text(json.dumps(bad),encoding='utf-8')
            before={p.name:p.read_bytes() for p in target.iterdir()}
            with self.assertRaises(ValueError):integrate(target,source)
            self.assertEqual(before,{p.name:p.read_bytes() for p in target.iterdir()})

    def test_shared_static_renderer_and_new_data_availability(self):
        expansion=Expansion(FOLDER/'expansion.json')
        for mode in ['limitedReview','sealedReview']:
            output=render(expansion,mode)
            self.assertEqual(output.count('data-lr-card '),336)
            self.assertIn('data-lr-context="draft"',output)
            self.assertIn('data-lr-context="sealed"',output)
        self.assertEqual(render(expansion,'limitedImpact').count('class="lr-card"'),42)
        sealed=render_page(expansion,'strategy',expansion.manifest['presentation']['pages']['strategy'])
        self.assertEqual(sealed.count('data-lr-card '),336)
        self.assertIn('data-default-context="sealed"',sealed)
        self.assertTrue(expansion.availability['pickBaits']['available'])
        self.assertTrue(expansion.availability['draftTable']['available'])


if __name__=='__main__':unittest.main()
