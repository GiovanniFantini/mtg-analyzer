import csv,gzip,tempfile,unittest,importlib.util
from pathlib import Path
from import_public_game_statistics import aggregate,match_card_rows,acquire,updated_limitations,MISSING_PUBLIC_DATA_NOTE
class GameIdentityTests(unittest.TestCase):
 def test_historical_limitations_survive_new_public_data(self):
  historical='17Lands: lo snapshot precedente contiene solo Premier Draft Platino e oltre.'
  self.assertEqual(updated_limitations([historical,MISSING_PUBLIC_DATA_NOTE]),[historical])
 def test_front_face_column_matches_full_card(self):
  rows,matched=match_card_rows([{'id':'one','name':'Front // Back','faces':[{'name':'Front'}]}],{'cards':{'Front':{'games':10,'wins':6}}})
  self.assertEqual(rows[0]['metrics']['inHandWinRate'],60);self.assertEqual(matched,{'Front'})
 def test_distinct_oracle_identities_cannot_share_column(self):
  with self.assertRaisesRegex(ValueError,'different card identities'):
   match_card_rows([{'id':'one','name':'Front','oracleId':'a'},{'id':'two','name':'Front','oracleId':'b'}],{'cards':{'Front':{'games':10,'wins':6}}})
 def test_obsolete_cache_does_not_silently_reapply_old_matching(self):
  import json
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);manifest=root/'expansion.json';manifest.write_text(json.dumps({'id':'set','code':'SET'}))
   old=root/'set-PremierDraft.json';old.write_text(json.dumps({'cards':[]}))
   with self.assertRaisesRegex(ValueError,'new dated'):acquire(manifest,'PremierDraft',root)
   self.assertEqual(json.loads(old.read_text()),{'cards':[]})
@unittest.skipUnless(importlib.util.find_spec('pandas') and importlib.util.find_spec('numpy'),'Acquisition tests require optional pandas/numpy; the offline build does not.')
class PublicGameTests(unittest.TestCase):
 def test_game_presence_not_copies_and_no_double_counting(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'games.csv.gz'
   with gzip.open(path,'wt',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['won','opening_hand_One','drawn_One','opening_hand_Two','drawn_Two'])
    w.writerows([[True,2,1,0,0],[False,0,1,0,0],[True,0,0,0,0]])
   r=aggregate(path)
   self.assertEqual(r['games'],3);self.assertEqual(r['cards']['One'],{'games':2,'wins':1});self.assertEqual(r['cards']['Two'],{'games':0,'wins':0})
if __name__=='__main__':unittest.main()
