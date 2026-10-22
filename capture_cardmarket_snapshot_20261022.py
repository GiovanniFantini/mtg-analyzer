"""Normalize browser-observed Cardmarket listings; no network requests.

The compact transcription has an explicitly observed EUR 0.02 group. Hashes of
the complete (name, product URL, From) rows are checked against the browser DOM
extraction before a snapshot can be saved.
"""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'research/reality-fracture-20261022'
DATE='2026-10-22'
PREFIX='https://www.cardmarket.com/en/Magic/Products/Singles/'

BASE_EXCEPTIONS="""Aerid Konstrari|1.99
Ajani Resolute|6.49
Ajani Unrelenting|9.99
Ajani's Anguish|0.08
Avatar of Burgeoning Echoes|1.8
Bloodline Recollector // Ancestral Craving|1.8
Chandra, Chill of Compliance|5.9
Chandra, Torch of Defiance|0.9
Craterclaw Colossus|6
Curse-Marred Demon|0.08
Dark Matter Manipulator|3
Darklight Phoenix|8.5
Denzilore Fatehold|1
Deserted Beach|0.25
Draconic Visitor|2.99
Emrakul, the Exigent Doom|10.99
Enlightened Confidant|4.45
Flickering Hound|3.75
Gardenize|0.1
Garruk, Curse Breaker|1.62
Garruk, Veiled Butcher|1.43
Geist of Saint Thalia|0.1
Germinate Recruits|0.03
Gideon's Memorial|0.03
Hall of Echoes|0.5
Haunted Ridge|0.34
Hexhaven Invigorator|15.5
Ingris Stingerquill|4
Jace's Machinations|0.04
Karn, Argent Defender|0.2
Kindred Judgment|0.48
Kwia Vigorbloom|4.25
Lich's Relic|0.49
Liliana the Faultless|1.5
Liliana the Repentant|0.1
Loyal Tutor|0.4
Lyra, Archangel of Dawn|0.94
Lyra, Tolarian Archangel|0.06
Omnipresence|1.25
Overgrown Farmland|0.4
Overwrite the Multiverse|1
Pompous Battlemage // Improvised Act|1.6
Return to the Light Realms|2.49
Rockfall Vale|0.15
Roiling Canopy|0.2
Samut, Hazoret's Champion|0.99
Samut, Tyrant of Naktamun|4.95
Sanctum Lurker|0.2
Seasoned Cryomancer|7
Shipwreck Marsh|0.7
Simulacrum Shaper|0.7
Sphinx of False Conclusions|0.05
Stingcaster Mage|3.1
Tam, the Possibility|0.03
Tarmogoyf|1
The Echoverse Fulcrum|1.85
The Theorist, Jace Beleren|41
Theorist's Sanctum|0.1
Uldaros Theorix|1.05
Verdant Kraken|1
Vraska, Soul of Stone|0.1"""

COMMANDER="""Avacyn, Angel of Horror|8
Arcane Signet|0.27
Sol Ring|0.8
Ob Nixilis, the Ascended|0.65
Niv-Mizzet, Ghost Counsel|2.34
Turbulent Wetlands|2.54
Command Tower|0.05
Swords to Plowshares|0.75
Path to Exile|0.49
Fabled Passage|0.5
Darksteel Angel|2.47
Fellwar Stone|0.4
Turbulent Crater|1.94
Flawless Maneuver|7
Turbulent Shore|2.31
Dack Fayden, Helping Hand|0.09
Archon of Cruelty|2
Brainstorm|0.73
Reflecting Pool|4.06
Memnarch, the Warden|0.69
Venser, Fervent Forger|0.02
Mystic Gate|0.78
Caves of Koilos|0.12
Teferi's Reproach|0.06
Exotic Orchard|0.04
Sulfurous Springs|0.3
Radiant Summit|0.1
Overlord of the Mistmoors|0.15
Omnath, Locus of the Void|0.95
The Ur-Sphinx|0.3
Sulfur Falls|0.05
Ginger, Queen of Sweets|0.02
Currency Converter|0.07
Isolated Chapel|0.1
Talisman of Creativity|0.4
Talisman of Dominance|0.32
Talisman of Indulgence|0.3
Talisman of Progress|0.1
Serra's Emissary|0.68
Underground River|0.5
Drowned Catacomb|0.48
Izzet Signet|0.08
Archfiend of Despair|2.19
Clifftop Retreat|0.04
Shivan Reef|0.08
Fetid Heath|0.08
Sunken Ruins|0.71
Chromatic Lantern|0.14
Grand Crescendo|0.45
Jhoira, Weatherlight Corsair|0.08
Tamiyo, Upriser Crowned|0.02
Glacial Fortress|0.08
Battlefield Forge|0.08
Rakdos Signet|0.18
Staff of the Storyteller|0.12
Dimir Signet|0.18
Shark Typhoon|0.12
Windcrag Siege|0.09
Elspeth, Sun's Champion|0.1
Stroke of Midnight|0.02
Azorius Signet|0.05
Cursed Mirror|0.08
Whirlwind of Thought|0.04
Skrelv's Hive|0.1
Brainsurge|0.02
Sunfall|0.04
Path of Ancestry|0.02
Secure the Wastes|0.03
Despark|0.02
Prairie Stream|0.04
Akroma, Angel of Fury|0.02
White Sun's Twilight|0.02
Proteus Staff|0.06
Dreadhorde Invasion|0.05
Mass Polymorph|0.02
Occult Epiphany|0.02
Restless Anchorage|0.03
Jace, Multiverse Architect|0.2
Nissa, Leyline Tamer|0.35
Martial Coup|0.02
Fact or Fiction|0.02
Synthetic Destiny|0.02
Contaminated Landscape|0.02
Perilous Landscape|0.02
Kher Keep|0.04
Restless Spire|0.02
Lingering Souls|0.02"""

SPG="""Eye of Ugin|24
Austere Command|1.99
Flesh Duplicate|8
Consign to Memory|8.5
Sublime Epiphany|1.9
Consider|3.7
Necrodominance|4.9
Mind Twist|2.35
Splinter Twin|4.49
Root Maze|2.8"""

def prices(text):
    return {name:float(value) for name,value in (line.rsplit('|',1) for line in text.splitlines())}

def slug(name):
    name=re.sub(r"[,'’.()]",'',name)
    return re.sub(r'[-\s/]+','-',name)

def fnv(value):
    text=json.dumps(value,ensure_ascii=False,separators=(',',':'))
    # Match JavaScript JSON number formatting for these finite two-decimal prices.
    text=re.sub(r'(\d)\.0(?=[,\]])',r'\1',text)
    h=2166136261
    for char in text:
        h=((h^ord(char))*16777619)&0xffffffff
    return f'{h:08x}'

def listing(name,value,expansion):
    return [name,PREFIX+expansion+'/'+slug(name),value]

def main():
    catalog=json.loads((ROOT/'expansions/reality-fracture/cards.json').read_text(encoding='utf-8'))['cards']
    exceptions=prices(BASE_EXCEPTIONS)
    base=[]
    for card in catalog:
        if card['set']!='FRA':continue
        names=[card['full']] if not card.get('basic') else [card['name']+' (V.1)',card['name']+' (V.2)']
        base.extend(listing(name,exceptions.get(name,0.02),'Reality-Fracture') for name in names)
    base.sort()
    commander=sorted(listing(name,value,'Commander-Reality-Fracture') for name,value in prices(COMMANDER).items())
    spg=sorted(listing(name,value,'Special-Guests') for name,value in prices(SPG).items())
    assert len(base)==290 and fnv(base)=='05287c7c',(len(base),fnv(base))
    assert len(commander)==87 and fnv(commander)=='e75c6c25',(len(commander),fnv(commander))
    assert len(spg)==10 and fnv(spg)=='1e3723bb',(len(spg),fnv(spg))
    queue=[r for r in base if not r[0].endswith('(V.2)')]+commander+spg
    assert len(queue)==382 and fnv([r[:2] for r in queue])=='2c6de37b'
    rows=[{'name':name,'url':url,'from':value,'source':'cardmarket','finishFilter':'any','currency':'EUR'} for name,url,value in base+commander+spg]
    result={'date':DATE,'source':'Cardmarket','collection':'Browser DOM, rendered public listing cards','metric':'From, EUR, no language/condition/seller-country filter; shipping excluded; finish not isolated','counts':{'basePrintings':290,'commanderIdentities':87,'specialGuests':10},'transcriptionChecks':{'algorithm':'FNV-1a32 over sorted JSON name/productURL/numericFrom tuples; integrity check, not cryptographic proof','base':'05287c7c','commander':'e75c6c25','specialGuests':'1e3723bb','focalQueue':'2c6de37b'},'rows':rows}
    path=OUT/'cardmarket-listings-20261022.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Verified browser transcription:',len(rows),'product listings')

if __name__=='__main__':main()
