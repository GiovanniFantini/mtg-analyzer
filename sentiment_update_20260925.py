"""Regional review audit, 25 September. Paraphrases, not a player survey.

Video passages checked against exported auto captions; timestamps retained.
Original letter grades are reported as grades, not converted win rates.
"""
SOURCES = {
 'fr-drosan-green': ('Drosan · verde', 'https://www.youtube.com/watch?v=5UBzrNbWIgg', 'fr', '2026-09-24'),
 'de-solaris-green': ('Sol4r1s · verde', 'https://www.youtube.com/watch?v=BVpXZzfYP3o', 'de', '2026-09-24'),
 'jp-eb-black': ('Ｅ．Ｂ · nero', 'https://note.com/eindebelle/n/n2252b8ebbfbb', 'ja', '2026-09-21'),
 'jp-eb-red': ('Ｅ．Ｂ · rosso', 'https://note.com/eindebelle/n/nfd3dc4d5e975', 'ja', '2026-09-22'),
 'en-llu-marc': ('Marc · Limited Level-Ups, tier list', 'https://www.17lands.com/tier_list/e95fd9365a86464cae2451e34c39102a', 'en', '2026-09-21'),
}
OBSERVATIONS = [
 ('Arcane Amphisbaena','fr-drosan-green','positivo','0:46 · C+: difesa utile e contributo a Jace.'),
 ('Bestial Incursion','fr-drosan-green','positivo','1:06 · C+: apprezzato il secondo corpo ottenibile nel lungo periodo.'),
 ('Budding Insurgent','fr-drosan-green','positivo','1:28 · C+: buon corpo e bersagli rilevanti per il sacrificio.'),
 ('Compel Brutality','fr-drosan-green','positivo','2:39 · B−: buona rimozione anche nei mazzi con Jace e meno creature.'),
 ('Greenhouse Propagator','fr-drosan-green','condizionato','4:04 · C: accelerazione tardiva, compensata dalle sinergie lifegain.'),
 ('Heartwood Crafter','fr-drosan-green','positivo','4:23 · B−: apprezzata la partenza con Heartwood e magie preparate.'),
 ('Inspired Tethermage','fr-drosan-green','condizionato','6:33 · C: modesta in curva, utile come impiego del mana tardivo.'),
 ('Restore with Empathy','fr-drosan-green','cauto','7:53 · D: preferita solo con forte supporto lifegain.'),
 ('Something Worth Saving','fr-drosan-green','positivo','8:47 · C: selezione, cimitero e vita la rendono frequentemente utile.'),
 ('Sureshot Sower','fr-drosan-green','cauto','9:06 · C−: corpo fragile e risposta ai volanti costosa; prudenza sul main deck.'),
 ('Vinelasher Adept','fr-drosan-green','condizionato','10:37 · C: landcycling utile, ma efficienza del corpo poco entusiasmante.'),
 ('Wrecking Gecko','fr-drosan-green','cauto','11:05 · C−: sotto la media, pur migliorando nelle partite lunghe.'),
 ('Ghalta the Unstoppable','fr-drosan-green','positivo','13:24 · B: forte pressione con una buona curva; riconosciuto il rischio di restare in mano.'),
 ('Jiang Yanggu, Never Alone','fr-drosan-green','positivo','13:59 · B: due corpi e utilità dello stap dei token Heartwood.'),
 ('Loot, the Nexus','fr-drosan-green','cauto','14:26 · D+: fragile e dipendente dal campo; soprattutto per necessità di fixing.'),
 ('Marwyn, the Preserver','fr-drosan-green','condizionato','14:52 · C: soprattutto un buon corpo a due mana, recupero terre secondario.'),
 ('Pia, Aether Ascetic','fr-drosan-green','condizionato','15:26 · C: bersagli frequenti, ma il tutor richiede di scartare una risorsa.'),
 ('Titanbones, Towering Heart','fr-drosan-green','condizionato','16:18 · C+: crescita promettente, subordinata alla consistenza del lifegain.'),
 ('Way of the Paradox','fr-drosan-green','positivo','16:51 · C+: apprezzati pescata iniziale, terra aggiuntiva e lifegain.'),
 ('Way of the Wildspeaker','fr-drosan-green','positivo','17:18 · Giudizio sopra la media per corpo e valore successivo; voto finale poco chiaro nei sottotitoli.'),
 ('Yoshimaru, Scrappy Stray','fr-drosan-green','positivo','17:49 · C+: interazione su un corpo, con utilità tardiva.'),
 ('Arcane Amphisbaena','de-solaris-green','positivo','0:00 · Solida difesa economica, particolarmente adatta a UG Jace.'),
 ('Bestial Incursion','de-solaris-green','positivo','0:51 · Promossa per corpo iniziale e secondo utilizzo, soprattutto in RG.'),
 ('Budding Insurgent','de-solaris-green','condizionato','1:51 · Giocabile; distruggere una Way non annulla il valore già prodotto entrando.'),
 ('Compel Brutality','de-solaris-green','molto-positivo','4:45 · Indicata come migliore comune verde; apprezzata la modalità con Jace.'),
 ('Greenhouse Propagator','de-solaris-green','positivo','12:25 · Giocabile trasversalmente per accelerazione e guadagno vita.'),
 ('Heartwood Crafter','de-solaris-green','molto-positivo','12:59 · Indicata come migliore non comune verde, per accelerazione e impieghi del mana.'),
 ('Inspired Tethermage','de-solaris-green','positivo','19:35 · Solida in più archetipi, con sinergie Jace e uso del mana Heartwood.'),
 ('Jiang Yanggu, Never Alone','de-solaris-green','positivo','20:35 · Promossi i due corpi e lo stap dei token.'),
 ('Loot, the Nexus','de-solaris-green','positivo','21:47 · Potenziale elevato di accelerazione e fixing, pur con corpo vulnerabile.'),
 ('Marwyn, the Preserver','de-solaris-green','condizionato','23:09 · Soprattutto un corpo efficiente; il recupero terre richiede un piano utile.'),
 ('Pia, Aether Ascetic','de-solaris-green','positivo','24:50 · Promossa per cercare Way e altri incantesimi, scartando carte superflue.'),
 ('Restore with Empathy','de-solaris-green','positivo','27:27 · Giocabile nei piani lenti con self-mill e lifegain; recupero flessibile.'),
 ('Something Worth Saving','de-solaris-green','positivo','31:16 · Apprezzata per collegare selezione, cimitero e lifegain.'),
 ('Sureshot Sower','de-solaris-green','condizionato','32:17 · Ammette il main deck per scambiare presto o rispondere a un volante più tardi.'),
 ('Titanbones, Towering Heart','de-solaris-green','condizionato','35:49 · Richiede almeno una attivazione lifegain affidabile; mediocre senza supporto.'),
 ('Way of the Paradox','de-solaris-green','condizionato','39:01 · Build-around: servono ricompense lifegain, il solo valore iniziale non convince.'),
 ('Way of the Wildspeaker','de-solaris-green','positivo','39:47 · Promossa la conversione della fedeltà in Bestie, migliorata da ulteriore empower.'),
 ('Wrecking Gecko','de-solaris-green','positivo','41:33 · Più favorevole nei mazzi RG capaci di pagare l’abilità con Heartwood.'),
 ('Yoshimaru, Scrappy Stray','de-solaris-green','positivo','42:21 · Buona interazione con le grandi creature verdi, più un corpo residuo.'),
 ('Extended Absence','jp-eb-black','molto-positivo','Rimozione versatile e complessivamente eccellente, pur un poco costosa.'),
 ('Rank Rat','jp-eb-black','condizionato','Dopo lo scarto, utile per scambiare o alimentare sacrifici.'),
 ('Void Extrapolator','jp-eb-black','positivo','Buon supporto al cimitero e alla difesa; meno adatta all’aggressione RB.'),
 ('Screeching Soulbreaker','jp-eb-black','positivo','Volo e sinergie danno/lifegain ne aumentano l’utilità.'),
 ('Terminal Criticism','jp-eb-black','sideboard','Principalmente sideboard; i token Jace aumentano i possibili bersagli.'),
 ('Silence the Echo','jp-eb-black','cauto','Il costo della modalità sacrificio peggiora il tempo rispetto a precedenti analoghi.'),
 ('Awaken the Inferno','jp-eb-red','condizionato','Rimozione meno prioritaria per costo; landcycling utile per consistenza e splash.'),
 ('Blazing Crescendo','jp-eb-red','positivo','Trucco apprezzato per pressione, scambi e sinergie con magie.'),
 ('Fulminous Forte','jp-eb-red','molto-positivo','Promossa soprattutto per i cinque danni istantanei; modalità da un danno più situazionale.'),
 ('Hallway Heckler','jp-eb-red','positivo','Corpo e filtraggio accettabili; conservare la preparazione quando serve a innescare sinergie.'),
 ('Heartstring Puller','jp-eb-red','positivo','Apprezzati sviluppo del campo e sinergie con potenziamenti collettivi.'),
 ('Skilled Battlecarver','jp-eb-red','positivo','Buona pressione iniziale e impiego del mana in eccesso.'),
 ('Violent Echoes','jp-eb-red','positivo','Danni istantanei importanti; requisiti di colore poco adatti allo splash.'),
 ('Wrath of the Bloodmane','jp-eb-red','positivo','Giocabile anche senza sconto; sale con leggende economiche.'),
]
# Exact visible grades from Marc's grid (row labels checked). Selected C/UC
# spanning every color, gold and artifacts; not a reproduction of the full list.
GRADES = {
 'Way of the Healer':'B+', 'Campus Crier':'C+', 'Hexhaven Battalion':'C+',
 'Prophesied End':'C', 'Unflinching Hortimancer':'C−', 'Shatterwing Pegasus':'D+',
 'Countersculpt':'B', 'Mindseeker Oculus':'B−', 'Surveillance Phantasm':'C+',
 'Semester Foreseer':'C−', 'Multiply by Zero':'B', 'Extended Absence':'B−',
 'Screeching Soulbreaker':'D+', 'Violent Echoes':'B+', 'Fulminous Forte':'B−',
 'Way of the Pyromancer':'C', 'Compel Brutality':'C+', 'Heartwood Crafter':'B−',
 'Inspired Tethermage':'D+', 'Ghalta the Unstoppable':'D+', 'Restore with Empathy':'D',
 'Titanbones, Towering Heart':'D', 'Twisted Fates':'B', 'Paradox Shaper':'D+',
 'Afterthought Sentry':'D+', 'Keeper of the Quiet Hour':'C',
}
for name, grade in GRADES.items():
    tone = 'positivo' if grade.startswith('B') or grade == 'C+' else 'condizionato' if grade == 'C' else 'cauto'
    OBSERVATIONS.append((name,'en-llu-marc',tone,f'Voto originale {grade} nella tier list preliminare. È una recensione individuale, non un dato di partite 17Lands.'))

UPDATES = {
 'Compel Brutality': ('molto-positivo','Apprezzamenti convergenti in inglese, giapponese, francese e tedesco; Sol4r1s la indica come migliore comune verde.'),
 'Heartwood Crafter': ('molto-positivo','Drosan e Marc la promuovono; Sol4r1s la indica come migliore non comune verde per accelerazione e sinergie.'),
 'Budding Insurgent': ('positivo','Drosan apprezza corpo e bersagli; Sol4r1s è più moderato: distruggere una Way non recupera il valore già ottenuto dall’avversario.'),
 'Loot, the Nexus': ('misto','Giudizi favorevoli giapponesi e tedeschi sul ramp; Drosan è cauto per fragilità e dipendenza dal campo.'),
 'Restore with Empathy': ('misto','Drosan e Marc sono cauti; Sol4r1s la considera giocabile nei piani lenti. Cimitero e lifegain restano decisivi.'),
 'Wrecking Gecko': ('misto','Drosan ed E.B sono cauti; Sol4r1s la promuove nei mazzi RG con abbastanza mana Heartwood.'),
 'Way of the Paradox': ('misto','Drosan apprezza la flessibilità; Sol4r1s richiede ricompense lifegain e Arena Zone resta cauta.'),
 'Pia, Aether Ascetic': ('condizionato','Ora disponibili giudizi Limited specifici: discreta per Drosan e promossa da Sol4r1s con incantesimi utili da cercare. Escluso l’entusiasmo Commander.'),
 'Ghalta the Unstoppable': ('misto','Drosan assegna B, Marc D+: forte divergenza tra potenza in curva e rischio di restare in mano.'),
 'Inspired Tethermage': ('misto','Early access e Sol4r1s favorevoli con sinergie; Drosan la considera riempitivo e Marc assegna D+. Giudizio fortemente dipendente dal piano.'),
 'Screeching Soulbreaker': ('misto','E.B valorizza volo e sinergie; Marc assegna D+ e Arena Zone resta moderata. Nessun consenso sulla priorità.'),
 'Afterthought Sentry': ('misto','Arena Zone apprezza il costo due con utilità tardiva; Marc assegna D+. Valutazione non condivisa.'),
 'Prophesied End': ('misto','Alcune fonti la collocano fra le migliori rimozioni; Marc assegna C. Accoglienza complessivamente favorevole, priorità discussa.'),
 'Shatterwing Pegasus': ('misto','Alle riserve degli utenti sul costo si aggiunge il D+ di Marc, in contrasto con recensioni più entusiaste.'),
 'Awaken the Inferno': ('misto','Molto apprezzata da Motonavi; E.B ne ridimensiona la priorità come rimozione, valorizzando invece il landcycling.'),
 'Sureshot Sower': ('misto','Drosan preferisce prudenza sul main deck; Sol4r1s accetta il corpo iniziale con risposta tardiva ai volanti.'),
}

def enrich(cards):
    catalog = {c['name']: c for c in cards if c['set']=='FRA'}
    for name, ref, tone, text in OBSERVATIONS:
        c=catalog[name]
        assert c['rarity'] in ('common','uncommon') and not c['basic'], name
        label,url,language,date=SOURCES[ref]
        s=c.setdefault('sentiment',dict(tone=tone,summary=text,sources=[],attention=False))
        s.setdefault('observations',[]).append(dict(source=ref,tone=tone,text=text,checked='2026-09-25',batch='regional-refresh'))
        if not any(x['id']==ref for x in s['sources']):
            s['sources'].append(dict(id=ref,label=label,url=url,language=language,date=date,kind='recensione'))
        s.update(updated='2026-09-25',batch='regional-refresh',breadth='Confronto attribuito · evidenze preliminari')
    for name,(tone,summary) in UPDATES.items():
        catalog[name]['sentiment'].update(tone=tone,summary=summary)
    for c in cards:
        if s:=c.get('sentiment'):
            s['kinds']=sorted({x['kind'] for x in s['sources']})
            s['kind']='misto' if len(s['kinds'])>1 else s['kinds'][0]
            s['languages']=sorted({x.get('language','en') for x in s['sources']})
    return dict(date='2026-09-25',observations=len(OBSERVATIONS),cards=len({x[0] for x in OBSERVATIONS}),sources=len(SOURCES))
