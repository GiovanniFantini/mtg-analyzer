import json,unittest
from research_tournament_lists import parse_mtgo,parse_wizards
class TournamentParserTests(unittest.TestCase):
 def test_public_payload_after_an_empty_assignment(self):
  payload={'event_id':'1','description':'Pioneer Challenge','starttime':'2026-10-20 00:00:00','format':'PIONEER','decklists':[{'loginid':'a','player':'Pilot','main_deck':[{'qty':'4','card_attributes':{'card_name':'One'}}],'sideboard_deck':[]}],'final_rank':[{'loginid':'a','rank':'1'}],'winloss':[{'loginid':'a','wins':'7','losses':'1'}],'player_count':{'players':'32'}}
  text='window.MTGO.decklists.data = {}; window.MTGO.decklists.data = '+json.dumps(payload)+';'
  e=parse_mtgo(text,'https://www.mtgo.com/decklist/example');self.assertEqual(e['format'],'pioneer');self.assertEqual(e['decks'][0]['rank'],1);self.assertEqual(e['publishedCoverage'],'published-lists-only');self.assertEqual(e['decks'][0]['main'],{'One':4})
 def test_wizards_sections_and_html_entities(self):
  text='<deck-list deck-title="Pilot" subtitle="A &amp; B" event-date="May 01, 2026" event-name="Pro Tour" format="Standard"><main-deck>4 One\n56 Plains</main-deck><side-board>1 One\n14 Other</side-board></deck-list>'
  e=parse_wizards(text,'https://magic.gg/example','pt','standard','historical-pro-tour');self.assertEqual(e['date'],'2026-05-01');self.assertEqual(e['decks'][0]['archetype'],'A & B');self.assertEqual(e['decks'][0]['main']['One'],4);self.assertEqual(e['decks'][0]['sideboard']['One'],1)
 def test_wrong_format_is_not_imported(self):
  with self.assertRaises(ValueError):parse_wizards('<deck-list format="Modern"></deck-list>','https://magic.gg/example','pt','standard','historical-pro-tour')
if __name__=='__main__':unittest.main()
