import csv,gzip,tempfile,unittest,importlib.util
from pathlib import Path
from import_public_game_statistics import aggregate
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
