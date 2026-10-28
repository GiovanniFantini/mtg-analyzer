import copy,unittest
from tournament_index import calculate_index,prepare_events,validate_index,merge_events
class TournamentIndexTests(unittest.TestCase):
 def event(self,id,date,decks):return {'id':id,'name':id,'date':date,'format':'standard','kind':'recent-mtgo-challenge','url':'https://example.com/'+id,'decks':decks}
 def deck(self,id,main,side=None,rank=None):return {'id':id,'player':id,'main':main,'sideboard':side or {},'rank':rank,'sourceUrl':'https://example.com/deck','archetype':'Example'}
 def card(self,**extra):return {'id':'card','name':'One','type':'Creature','releasedAt':'2026-01-01','legalities':{'standard':'legal'},**extra}
 def calculate(self,c,events,release='2026-01-01'):return calculate_index(c,'standard',prepare_events(events),release)
 def test_union_of_main_and_side_not_copies(self):
  e=self.event('one','2026-10-20',[self.deck('a',{'One':4},{'One':1},1),self.deck('b',{'Other':4})]);r=self.calculate(self.card(),[e]);validate_index(r)
  self.assertEqual(r['score'],50);self.assertEqual(r['observed']['withCard'],1);self.assertEqual(r['observed']['mainDecks'],1);self.assertEqual(r['observed']['sideboardDecks'],1);self.assertEqual(r['observed']['mainCopies'],4);self.assertEqual(r['observed']['winningLists'],1)
 def test_pre_release_event_does_not_create_zero(self):
  e=self.event('one','2026-10-01',[self.deck('a',{'Other':4})]);r=self.calculate(self.card(),[e],'2026-11-01');self.assertIsNone(r['score']);self.assertEqual(r['reason'],'no_post_release_sample')
 def test_observed_zero_differs_from_missing_or_banned(self):
  e=self.event('one','2026-10-20',[self.deck('a',{'Other':4})]);r=self.calculate(self.card(),[e]);self.assertEqual(r['score'],0);self.assertEqual(r['status'],'not_observed');self.assertIsNone(self.calculate(self.card(legalities={'standard':'banned'}),[e])['score'])
 def test_historical_pro_tour_is_separate(self):
  past=self.event('pt','2026-05-01',[self.deck('a',{'One':4})]);recent=self.event('new','2026-10-20',[self.deck('b',{'Other':4})]);r=self.calculate(self.card(),[past,recent]);self.assertEqual(r['score'],0);self.assertEqual(r['history']['withCard'],1)
 def test_reprints_can_have_earlier_documented_identity(self):
  e=self.event('one','2026-10-01',[self.deck('a',{'One':4})]);r=self.calculate(self.card(),[e],'2026-11-01');self.assertEqual(r['score'],100);self.assertEqual(r['eligibleFrom'],'2026-10-01')
 def test_aliases_and_duplicate_event_pages(self):
  c=self.card(name='One // Two',full='One // Two',faces=[{'name':'One'}]);e=self.event('event','2026-10-20',[self.deck('a',{'One':1})]);events=merge_events([copy.deepcopy(e),copy.deepcopy(e)]);self.assertEqual(self.calculate(c,events)['score'],100);self.assertEqual(len(events[0]['decks']),1)
 def test_score_consistency_is_validated(self):
  e=self.event('one','2026-10-20',[self.deck('a',{'One':4})]);r=self.calculate(self.card(),[e]);r['score']=55
  with self.assertRaisesRegex(ValueError,'inconsistent'):validate_index(r)
 def test_trend_requires_two_adequate_samples(self):
  old=self.event('old','2026-10-03',[self.deck('o'+str(i),{'Other':1}) for i in range(50)]);new=self.event('new','2026-10-20',[self.deck('n'+str(i),{'One' if i<3 else 'Other':1}) for i in range(50)]);r=self.calculate(self.card(),[old,new]);self.assertEqual(r['trend']['status'],'rising');self.assertEqual(r['outlook']['status'],'watch')
if __name__=='__main__':unittest.main()
