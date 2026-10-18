"""Public, attributed preliminary opinions checked on 2026-09-24.

Language identifies the source, never the nationality of anonymous users.
Multiple articles by one author are not independent reviewers.
"""
SOURCES = {
 'jp-eb-white': ('Ｅ．Ｂ · bianco', 'https://note.com/eindebelle/n/n8f81382ea59f', 'ja', '2026-09-19', 'recensione'),
 'jp-pos-white': ('ぽｓ · prerelease bianco', 'https://note.com/poslog/n/n579372c527c2', 'ja', '2026-09-21', 'recensione'),
 'jp-blue': ('もとなび · blu', 'https://note.com/vivid_motonavi/n/n612b18bed9fc', 'ja', '2026-09-21', 'recensione'),
 'jp-black': ('もとなび · nero', 'https://note.com/vivid_motonavi/n/n5d59e709da6f', 'ja', '2026-09-21', 'recensione'),
 'jp-red': ('もとなび · rosso', 'https://note.com/vivid_motonavi/n/n2e3c741e3451', 'ja', '2026-09-22', 'recensione'),
 'en-overview': ('r/lrcast · commenti al Limited Overview', 'https://www.reddit.com/r/lrcast/comments/1wl020g/reality_fracture_limited_overview/', 'en', '2026-09-20', 'utenti'),
 'en-lr': ('r/lrcast · discussione LR 872', 'https://www.reddit.com/r/lrcast/comments/1wmta3x/limited_resources_872_reality_fracture_set_review/', 'en', '2026-09-22', 'utenti'),
 'en-top': ('Andrew Quinn · migliori comuni / non comuni', 'https://draftsim.com/best-commons-uncommons-mtg-reality-fracture/', 'en', '2026-09-22', 'recensione'),
 'en-tcg': ('TCGplayer · graduatoria comuni blu, testo indicizzato', 'https://www.tcgplayer.com/content/article/Reality-Fracture-Limited-Magic-The-Gathering-Set-Review-Blue/0d5d7daa-b791-4b94-8194-153c45fb726f/', 'en', '2026-09-22', 'recensione'),
}
# Exact English card name, source, tone, short Italian paraphrase.
OBSERVATIONS = [
 ('Academic Ascent','jp-eb-white','condizionato','Priorità maggiore in WU; il valore aggiuntivo richiede sinergie.'),
 ('Blossom-Blessed Angel','jp-eb-white','positivo','Considerata una comune solida per evasione, vigilanza e sinergie.'),
 ('Blossom-Blessed Angel','jp-pos-white','positivo','Giudizio forte nella sua rarità; apprezzata come minaccia volante.'),
 ('Campus Crier','jp-eb-white','positivo','Buona negli scambi e nei piani di logoramento con Jace.'),
 ('Campus Crier','jp-pos-white','condizionato','Giudizio ordinario, meno entusiasta delle altre fonti.'),
 ('Surgical Precision','jp-eb-white','condizionato','Rimozione di supporto; la velocità stregoneria ne limita la flessibilità.'),
 ('Surgical Precision','jp-pos-white','condizionato','Giudizio ordinario, penalizzato dalla velocità stregoneria.'),
 ('Hexhaven Battalion','jp-pos-white','cauto','Giudizio debole; valorizzata soprattutto per il landcycling.'),
 ('Fateshaper Aspirant','jp-pos-white','cauto','Costo cinque poco convincente senza sfruttare il valore aggiuntivo.'),
 ('Shatterwing Pegasus','jp-pos-white','molto-positivo','Fra i giudizi migliori nella propria rarità per evasione e potenziamento collettivo.'),
 ('Your Fate Ends Here','jp-pos-white','positivo','Apprezzata la rimozione istantanea delle minacce rilevanti.'),
 ('Prophesied End','jp-pos-white','molto-positivo','Molto favorevole alla rimozione economica delle bombe.'),
 ('Surveillance Phantasm','jp-blue','molto-positivo','La candidata dell’autore a migliore comune blu, grazie al supporto per sorvegliare.'),
 ('Cryotheory Adept','jp-blue','positivo','Inclusione affidabile; resta utile dopo scambi o sorvegliare.'),
 ('Icy Reception','jp-blue','positivo','Apprezzata la flessibilità anche nelle fasi avanzate.'),
 ("Sphinx's Approach",'jp-blue','cauto','Dubbi sullo slot dedicato alla pescata quando Jace già fornisce risorse.'),
 ('Mindseeker Oculus','jp-blue','positivo','Promossa per la pescata immediata e la fedeltà residua.'),
 ('Infinite Coursework','jp-blue','positivo','Trattata come rimozione affidabile a tre mana.'),
 ('Countersculpt','jp-blue','positivo','Promettente con Jace: neutralizzazione economica e fedeltà aggiuntiva.'),
 ('Undulating Witness','jp-blue','positivo','Apprezzati landcycling e corpo volante; cautela nel ridurne la costituzione.'),
 ('Silence the Echo','jp-black','cauto','Dubbi sulla comodità del costo rispetto alle rimozioni simili.'),
 ('Last Gasp','jp-black','positivo','Efficiente; può peggiorare contro creature cresciute o grandi leggende.'),
 ('Rank Rat','jp-black','positivo','Utilità concreta negli scambi e come materiale da sacrificare.'),
 ('Void Extrapolator','jp-black','cauto','Poco convincente senza evasione anche una volta raggiunta la soglia.'),
 ('Cast Away Doubt','jp-black','cauto','Pescata ordinaria; la velocità stregoneria soffre il confronto con empower.'),
 ('Extended Absence','jp-black','molto-positivo','Indicata come migliore comune nera e possibile motivo per uno splash.'),
 ('Screeching Soulbreaker','jp-black','positivo','Buon corpo difensivo volante con sinergie di danno e lifegain.'),
 ('Way of the Necromancer','jp-black','cauto','Ritenuta difficile da sfruttare in modo efficace.'),
 ('Skilled Battlecarver','jp-red','positivo','Buona pressione iniziale e utilità successiva, anche con Heartwood.'),
 ('No Admittance','jp-red','positivo','Interazione utile; conviene sfruttarla prima che i bersagli crescano.'),
 ("Chandra's Emberling",'jp-red','positivo','Minaccia che cresce con magie non creatura e preparazioni.'),
 ('Wrath of the Bloodmane','jp-red','positivo','Promossa come interazione istantanea, potenzialmente scontata.'),
 ('Heartstring Puller','jp-red','positivo','Apprezzata per produrre due creature con una carta.'),
 ('Awaken the Inferno','jp-red','molto-positivo','Candidata a migliore comune rossa; dubbio residuo sul costo elevato.'),
 ('Countersculpt','en-overview','positivo','Un commentatore la rivaluta: empower aggiunge valore oltre alla neutralizzazione.'),
 ('Paradox Shaper','en-lr','condizionato','Entusiasmo per il piano di riciclo; richiede un mazzo costruito attorno.'),
 ('Recursive Recruitment','en-lr','condizionato','Interesse per una chiusura da cimitero in un guscio sinergico.'),
 ('Eye of Jace','en-lr','condizionato','Un commentatore vede potenziale nelle sinergie, oltre al valore isolato.'),
 ('Hexhaven Battalion','en-top','molto-positivo','Prima comune bianca nella selezione di Andrew Quinn.'),
 ('Surgical Precision','en-top','positivo','Terza comune bianca: efficienza e modo alternativo per pescare e guadagnare vita.'),
 ('Memory Trap','en-top','positivo','Seconda comune bianca della selezione.'),
 ('Arcane Amphisbaena','en-top','positivo','Terza comune verde: abilita Jace e lo difende.'),
 ('Something Worth Saving','en-top','positivo','Seconda comune verde per sostenere il cimitero.'),
 ('Compel Brutality','en-top','positivo','Prima comune verde nella selezione preliminare.'),
 ('Mindseeker Oculus','en-tcg','molto-positivo','Prima nella graduatoria delle comuni blu.'),
 ('Infinite Coursework','en-tcg','positivo','Seconda nella graduatoria delle comuni blu.'),
 ('Icy Reception','en-tcg','positivo','Terza nella graduatoria delle comuni blu.'),
 ('Semester Foreseer','en-tcg','positivo','Quarta nella graduatoria delle comuni blu.'),
 ('Unsummon','en-tcg','positivo','Quinta nella graduatoria delle comuni blu.'),
]

def enrich(cards):
    by_name = {c['name']: c for c in cards if c['set'] == 'FRA'}
    for name, ref, tone, text in OBSERVATIONS:
        c = by_name[name]
        assert c['rarity'] in ('common', 'uncommon') and not c['basic'], name
        label, url, language, date, kind = SOURCES[ref]
        if not c.get('sentiment'):
            c['sentiment'] = dict(tone=tone, breadth='Valutazione preliminare attribuita',
                summary=text, sources=[], kind=kind, attention=tone=='molto-positivo')
        s = c['sentiment']
        s.setdefault('observations', []).append(dict(source=ref, tone=tone, text=text))
        if not any(x['id']==ref for x in s['sources']):
            s['sources'].append(dict(id=ref,label=label,url=url,language=language,date=date,kind=kind))
    updates = {
      'Hexhaven Battalion': ('misto','Entusiasmo nelle fonti inglesi; una recensione giapponese è nettamente più cauta. Il consenso non è uniforme.'),
      'Surgical Precision': ('misto','Efficienza apprezzata nelle fonti inglesi; due recensioni giapponesi ne ridimensionano la priorità.'),
      'Campus Crier': ('misto','Giudizi da favorevole a ordinario. Il valore dipende dal piano di gioco.'),
      'Void Extrapolator': ('condizionato','Il supporto al cimitero resta decisivo; una recensione giapponese solleva ulteriori dubbi.'),
    }
    for name,(tone,summary) in updates.items():
        by_name[name]['sentiment'].update(tone=tone,summary=summary,breadth='Confronto tra fonti; valutazioni preliminari')
    for c in cards:
        if s := c.get('sentiment'):
            s['kinds'] = sorted({x['kind'] for x in s['sources']})
            s['kind'] = 'misto' if len(s['kinds'])>1 else s['kinds'][0]
            s['languages'] = sorted({x.get('language','en') for x in s['sources']})
    return len(OBSERVATIONS)
