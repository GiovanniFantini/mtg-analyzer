"""Second research pass: newly collected evidence, not all newly published.

Short attributed paraphrases. No vote changes or inferred win rates.
"""
SOURCES = {
 'jp-eb-green': ('Ｅ．Ｂ · verde', 'https://note.com/eindebelle/n/n0ef191693736', 'ja', '2026-09-23', 'recensione'),
 'az-green': ('J2SJosh · Arena Zone, verde', 'https://mtgazone.com/reality-fracture-fra-limited-set-review-green/', 'en', '2026-09-21', 'recensione'),
 'az-red': ('J2SJosh · Arena Zone, rosso', 'https://mtgazone.com/reality-fracture-fra-limited-set-review-red/', 'en', '2026-09-21', 'recensione'),
 'az-blue': ('J2SJosh · Arena Zone, blu', 'https://mtgazone.com/reality-fracture-fra-limited-set-review-blue/', 'en', '', 'recensione'),
 'az-artifacts': ('J2SJosh · Arena Zone, artefatti e terre', 'https://mtgazone.com/reality-fracture-fra-limited-set-review-artifacts-and-lands/', 'en', '2026-09-21', 'recensione'),
 'spikes-white': ('r/spikes · recensione bianco e repliche', 'https://www.reddit.com/r/spikes/comments/1wk4oip/draft_reality_fracture_set_review_white/', 'en', '', 'utenti'),
 'tcg-white': ('TCGplayer · bianco, testo indicizzato', 'https://www.tcgplayer.com/content/article/Reality-Fracture-Limited-Magic-The-Gathering-Set-Review-White/96d152d7-f0f7-498a-a6e2-fd1f738f0641/', 'en', '', 'recensione'),
 'rocks-early': ('Riley Hicks · MTG Rocks, esperienza early access', 'https://mtgrocks.com/mtg-reality-fracture-prerelease-guide/', 'en', '2026-09-24', 'recensione'),
 'draftsim-traps': ('Peter Smith · Draftsim, scelte in draft simulati', 'https://draftsim.com/mtg-fra-early-data-traps/', 'en', '2026-09-24', 'recensione'),
}
# Source ids black, gold, draftsim and en-lr reuse existing sources.
OBSERVATIONS = [
 ('Unflinching Hortimancer','tcg-white','condizionato','Valorizzata la combinazione con Seed Suture; giudizio Limited 2,25.'),
 ('Rescue Girl, First Responder','tcg-white','condizionato','Giudizio 1–2,5: servono permanenti da riutilizzare; costo e tempi limitano il rendimento.'),
 ('Rescue Girl, First Responder','spikes-white','positivo','Una replica invita a rivalutarla per riutilizzare incantesimi leggendari e creature preparate.'),
 ('Thalia, the Survivor','spikes-white','misto','Voto iniziale D+; una replica apprezza legame vitale nelle corse ai danni e alcuni matchup.'),
 ('Koth of the Homestead','spikes-white','positivo','Apprezzato il guadagno vita ripetuto per sostenere Hortimancer.'),
 ('Campus Crier','spikes-white','misto','Un commentatore ridimensiona il voto elevato dell’autore, pur considerandola buona.'),
 ('Shatterwing Pegasus','spikes-white','misto','Dissenso sul voto alto: una replica segnala il costo del potenziamento e il rischio di perdere tempo.'),
 ('Surveillance Phantasm','az-blue','condizionato','2/5: evasione e abilità attivata utili, ma valutazione generale moderata.'),
 ('Semester Foreseer','az-blue','cauto','2/5: prima copia accettabile; costo elevato e cautela sulle copie aggiuntive.'),
 ('Way of the Cryomancer','az-blue','condizionato','Richiede magie adatte da copiare e protezione del Jace; potenziale concreto con empower.'),
 ('Way of the Mind Sculptor','az-blue','condizionato','Base poco efficiente; altre fonti empower possono alimentare ulteriori pescate.'),
 ('Traxos, Academy Guardian','az-blue','positivo','Apprezzato come difensore economico, con requisito di lancio ritenuto gestibile.'),
 ('Extended Absence','black','molto-positivo','3,5/5: esilio versatile; utile anche per lifegain e danno non da combattimento.'),
 ('Screeching Soulbreaker','black','condizionato','2/5 di base; sale nei mazzi con ricompense per vita o danni non da combattimento.'),
 ('Arni, Renowned Champion','az-red','condizionato','Richiede creature grandi; il costo quattro limita la versatilità.'),
 ('Command the Stage','az-red','positivo','Sale se il mazzo riesce a riutilizzarla grazie ai danni non da combattimento.'),
 ('Koth, the Geomancer','az-red','condizionato','Accelerazione e danni finali utili, ma corpo fragile.'),
 ('Marwyn, the Clearcutter','az-red','positivo','Apprezzati costo basso e conversione di risorse superflue in carte.'),
 ('Tetsuko Umezawa, Pursuer','az-red','positivo','Minaccia incisiva nei mazzi con magie; vulnerabile alle rimozioni senza valore residuo.'),
 ('Tomik, Izzet Sparkmage','az-red','cauto','Corpo modesto; richiede frequenti danni non da combattimento.'),
 ('Violent Echoes','az-red','molto-positivo','3,5/5: rimozione con possibilità di vantaggio carte.'),
 ('Way of the Pyromancer','az-red','cauto','1/5: il recensore considera insufficiente il rendimento iniziale.'),
 ('Bestial Incursion','jp-eb-green','positivo','Comune affidabile; apprezzati travolgere e il secondo utilizzo.'),
 ('Greenhouse Propagator','jp-eb-green','positivo','Considerata utile anche fuori dal lifegain per accelerare e stabilizzare.'),
 ('Compel Brutality','jp-eb-green','positivo','Rimozione importante; può sfruttare anche la fedeltà di Jace.'),
 ('Restore with Empathy','jp-eb-green','condizionato','Recupero utile per le bombe; l’autore preferisce limitarne le copie.'),
 ('Marwyn, the Preserver','jp-eb-green','positivo','Buon corpo economico e recupero delle terre finite nel cimitero.'),
 ('Loot, the Nexus','jp-eb-green','positivo','Accelerazione potenzialmente ampia e accesso a tutti i colori.'),
 ('Titanbones, Towering Heart','jp-eb-green','condizionato','Cresce rapidamente con lifegain; suggerito Kitesail per superare i bloccanti.'),
 ('Way of the Wildspeaker','jp-eb-green','positivo','Valore iniziale convincente e possibilità di produrre altre Bestie con empower.'),
 ('Wrecking Gecko','jp-eb-green','cauto','Corpo ordinario e abilità costosa; soprattutto riempitivo o supporto artefatti.'),
 ('Greenhouse Propagator','az-green','condizionato','2/5 di base: importante con più ricompense lifegain, meno attraente come semplice acceleratore.'),
 ('Titanbones, Towering Heart','az-green','condizionato','Richiede vita affidabile; le dimensioni non risolvono la vulnerabilità a blocchi e rimozioni.'),
 ('Ghalta the Unstoppable','az-green','cauto','2/5: rischio di restare in mano quando manca una creatura abbastanza grande.'),
 ('Ghalta the Unstoppable','en-lr','misto','Commenti del 23–24 settembre divisi tra vulnerabilità alle rimozioni e pressione immediata del board.'),
 ('Yoshimaru, Scrappy Stray','en-lr','condizionato','Replica del 24 settembre: il piccolo corpo residuo vale di più con sacrifici o riutilizzo.'),
 ('Way of the Wildspeaker','az-green','molto-positivo','3,5/5: presenza sul campo e valore successivo, ulteriormente alimentati da empower.'),
 ('Way of the Paradox','az-green','cauto','1,5/5: il recensore teme il costo di una carta che richiede più sinergie.'),
 ('Medic\'s Kitesail','az-artifacts','condizionato','1,5/5 generale: costo di equipaggiare impegnativo; preferita con molte ricompense lifegain.'),
 ('Afterthought Sentry','az-artifacts','positivo','2,5/5: costo due incolore utile presto e dotato di utilità successiva.'),
 ('Archive Arbiter','az-artifacts','condizionato','Convince soprattutto quando rimuove un permanente importante; costo alto per il solo corpo.'),
 ('Murmuring Volume','az-artifacts','condizionato','Più importante nei mazzi lenti multicolore; poco desiderabile nei piani aggressivi.'),
 ('Living Library','az-artifacts','condizionato','Difensore con utilità tardiva; poco adatto ai mazzi aggressivi.'),
 ('Twisted Fates','gold','molto-positivo','3,5/5: rimozione e potenziamento collettivo molto apprezzati.'),
 ('Vigorbloom Charm','gold','positivo','3,5/5: promossa la flessibilità dei tre modi.'),
 ('Vigorbloom Vanguard','gold','positivo','2,5/5: corpo, segnalino, vigilanza e vita formano un insieme solido.'),
 ('Blessed Ghoul','gold','condizionato','Più utile con sacrifici e ricompense lifegain; recuperarlo richiede mana.'),
 ('Inspired Tethermage','draftsim','cauto','2/10 nella recensione preliminare: poco convincente all’inizio, dipendente da empower.'),
 ('Inspired Tethermage','rocks-early','positivo','Early access: crescita più facile del previsto, specialmente con Way of the Pyromancer.'),
 ('Way of the Pyromancer','rocks-early','positivo','Early access: segnalata la sinergia favorevole con Inspired Tethermage.'),
 ('Mindseeker Oculus','rocks-early','positivo','Early access: rendimento favorevole delle creature che alimentano Jace.'),
 ('Campus Crier','rocks-early','positivo','Early access: apprezzato il contributo al piano Jace.'),
 ('Hallway Heckler','rocks-early','positivo','Early access: rivalutata grazie alle sinergie della magia preparata.'),
 ('Void Extrapolator','rocks-early','positivo','Early access: rivalutata per le sinergie della preparazione.'),
 ('Fulminous Forte','rocks-early','molto-positivo','Early access: particolarmente convincente per versatilità e bersagli piccoli.'),
 ('Paradox Shaper','rocks-early','molto-positivo','Early access: motore molto incisivo nelle partite lunghe.'),
 ('Twisted Fates','rocks-early','molto-positivo','Early access: fra le multicolori maggiormente apprezzate.'),
 ('Warrior\'s Blades','rocks-early','positivo','Early access: segnalata fra le multicolori da considerare con fixing adeguato.'),
 ('Craftwork Crusher','rocks-early','molto-positivo','Early access: minaccia particolarmente potente nel formato descritto come lento.'),
 ('Hexhaven Battalion','rocks-early','molto-positivo','Early access: spicca fra i landcycler; Witness convince meno.'),
 ('Greenhouse Propagator','draftsim-traps','cauto','Scelte simulate: ritenuta presa troppo presto; non è una misura delle vittorie.'),
 ('Keeper of the Quiet Hour','draftsim-traps','cauto','Scelte simulate: l’autore critica la priorità elevata, senza definirla ingiocabile.'),
]

UPDATES = {
 'Surveillance Phantasm': ('misto','Molto apprezzata da もとなび; Arena Zone resta su una valutazione moderata. Manca consenso sulla priorità.'),
 'Semester Foreseer': ('misto','Presente nella selezione TCGplayer, ma Arena Zone invita a limitare le copie per il costo.'),
 'Greenhouse Propagator': ('misto','Utile nel lifegain; giudizi discordanti fuori da quel piano e cautela sulla priorità nei draft simulati.'),
 'Campus Crier': ('misto','Prime esperienze early access favorevoli; persistono divergenze sul voto generale.'),
 'Shatterwing Pegasus': ('misto','Recensioni entusiaste affiancate da dubbi degli utenti sul costo del potenziamento.'),
 'Inspired Tethermage': ('misto','Recensione preliminare cauta; Riley Hicks la rivaluta dopo l’early access per le sinergie con Jace.'),
 'Way of the Pyromancer': ('misto','Arena Zone è negativa; l’esperienza early access di Riley Hicks valorizza la sinergia con Inspired Tethermage.'),
 'Void Extrapolator': ('condizionato','Dubbi sul corpo, ma prime esperienze favorevoli quando la magia preparata sostiene il piano del mazzo.'),
 'Ghalta the Unstoppable': ('misto','Dibattito fra potenza del board e rischio di costo eccessivo; Arena Zone mantiene un voto prudente.'),
 'Rescue Girl, First Responder': ('condizionato','Più interessante con permanenti da riutilizzare; utenti e recensori discutono quanto compensi il costo di tempo.'),
 'Craftwork Crusher': ('condizionato','Prime esperienze molto favorevoli nel formato lento; restano da soddisfare costo e requisiti di mana.'),
 'Hexhaven Battalion': ('misto','Ulteriore riscontro favorevole dall’early access, ma resta la recensione giapponese più cauta.'),
}

def enrich(cards):
    from sentiment_data import SOURCES as base_sources
    from international_sentiment import SOURCES as international_sources
    sources = {k:(v[0],v[1],'en','',v[2]) for k,v in base_sources.items()}
    sources.update(international_sources)
    sources.update(SOURCES)
    by_name = {c['name']:c for c in cards if c['set']=='FRA'}
    for name, ref, tone, text in OBSERVATIONS:
        c = by_name[name]
        assert c['rarity'] in ('common','uncommon'), name
        label,url,language,date,kind = sources[ref]
        s = c.setdefault('sentiment',dict(tone=tone,summary=text,sources=[],attention=False))
        s.setdefault('observations',[]).append(dict(source=ref,tone=tone,text=text,checked='2026-09-24',batch='set-refresh'))
        if not any(x['id']==ref for x in s['sources']):
            s['sources'].append(dict(id=ref,label=label,url=url,language=language,date=date,kind=kind))
        s.update(updated='2026-09-24',batch='set-refresh',breadth='Ricontrollo esteso · opinioni attribuite, campione non rappresentativo')
        if tone=='molto-positivo': s['attention']=True
    for name,(tone,summary) in UPDATES.items():
        by_name[name]['sentiment'].update(tone=tone,summary=summary)
    for c in cards:
        if s:=c.get('sentiment'):
            s['kinds']=sorted({x['kind'] for x in s['sources']})
            s['kind']='misto' if len(s['kinds'])>1 else s['kinds'][0]
            s['languages']=sorted({x.get('language','en') for x in s['sources']})
    return dict(observations=len(OBSERVATIONS),cards=len({r[0] for r in OBSERVATIONS}),date='2026-09-24')
