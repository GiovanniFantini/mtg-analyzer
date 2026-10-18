"""Coarse editorial index of the collected reception, NOT a survey mean.

No arithmetic aggregation of incomparable review scales or forum threads.
Mixed/conditional cards require an explicit decision, never a neutral fallback.
"""
DECISIONS = {
 'Academic Ascent':(3,'Apprezzamento subordinato al piano WU.'),
 'Campus Crier':(3.5,'Più riscontri favorevoli, ma priorità discussa.'),
 'Hexhaven Battalion':(3.5,'Apprezzamenti inglesi e C+ di Marc contro prudenza giapponese.'),
 'Prophesied End':(3.5,'Promossa da più fonti, ma il C di Marc impedisce una sintesi entusiasta.'),
 'Refute Destiny':(None,'Giudizio di sideboard: non confrontabile con il main deck alla cieca.'),
 'Shatterwing Pegasus':(2.5,'Entusiasmo iniziale contro D+ di Marc e riserve sul costo.'),
 'Surgical Precision':(3,'Pareri favorevoli inglesi e riserve giapponesi si contrappongono.'),
 'Unflinching Hortimancer':(3,'Interesse per lifegain, ma base poco convincente senza supporto.'),
 'Divining Duelist':(2.5,'Entusiasmo per Twin separato dal rendimento autonomo.'),
 'Semester Foreseer':(2.5,'Selezione favorevole contro costo elevato e C− di Marc.'),
 'Surveillance Phantasm':(3.5,'Un recensore molto favorevole; gli altri moderano la priorità.'),
 'Unsummon':(3,'Buone applicazioni, ma dubbi sul piano tempo.'),
 'Apex Witchstalker':(2.5,'Flessibilità riconosciuta, accoglienza complessivamente tiepida.'),
 'Rank Rat':(3,'Utilità soprattutto dopo lo scarto e nei sacrifici.'),
 'Screeching Soulbreaker':(2.5,'Sinergie apprezzate, ma D+ di Marc e voto moderato di Arena Zone.'),
 'Terminal Criticism':(None,'Dipendenza dai colori avversari: indice main deck non assegnato.'),
 'Void Extrapolator':(3,'Il supporto al cimitero giustifica l’interesse, non una priorità universale.'),
 'Awaken the Inferno':(3.5,'Landcycling apprezzato; costo della rimozione divide le recensioni.'),
 'Greenhouse Propagator':(3,'Giocabile e sinergica, ma non unanimemente prioritaria.'),
 'Inspired Tethermage':(3,'Riscontri early access favorevoli contro giudizi preliminari bassi.'),
 'Restore with Empathy':(2.5,'Due riscontri cauti contro apprezzamento nei piani lenti.'),
 'Sureshot Sower':(2.5,'Dissenso sull’inclusione in main deck, senza particolare entusiasmo.'),
 'Vinelasher Adept':(3,'Flessibilità utile, efficienza moderata.'),
 'Wrecking Gecko':(2.5,'Apprezzamento tedesco in RG contro riserve francesi e giapponesi.'),
 'Blessed Ghoul':(2.5,'Dipendente da sacrifici/lifegain e mana per il recupero.'),
 'Craftwork Crusher':(4,'Forte apprezzamento early access, subordinato alla base di mana.'),
 'Paradox Shaper':(2.5,'Potenziale del motore contro D+ di Marc e necessità di costruirci attorno.'),
 'Recursive Recruitment':(3,'Interesse per la chiusura da cimitero con setup.'),
 'Theorix Metamage':(3,'Supporto specifico al piano Dimir.'),
 'Afterthought Sentry':(2.5,'Giudizio utile/solido di Arena Zone contro D+ di Marc.'),
 'Archive Arbiter':(3,'Promossa quando risponde a un permanente rilevante.'),
 'Eye of Jace':(3,'Potenziale sinergico, evidenza ristretta.'),
 'Living Library':(2.5,'Applicazione difensiva circoscritta.'),
 "Medic's Kitesail":(2.5,'Sinergie lifegain contro costo di equipaggiamento.'),
 'Murmuring Volume':(3,'Apprezzamento circoscritto ai mazzi lenti multicolore.'),
 'Rescue Girl, First Responder':(3,'Riutilizzo interessante, costo in tempo discusso.'),
 'Thalia, the Survivor':(2.5,'Riserve iniziali, con utilità nelle corse ai danni.'),
 'Way of the Cryomancer':(3,'Potenziale legato alle magie da copiare.'),
 'Way of the Mind Sculptor':(2.5,'Serve ulteriore empower per compensare la base modesta.'),
 'Arni, Renowned Champion':(2.5,'Richiede seguito di creature grandi.'),
 'Koth, the Geomancer':(3,'Accelerazione utile, corpo fragile.'),
 'Way of the Pyromancer':(3,'Giudizio basso di Arena Zone contro riscontro early access favorevole.'),
 'Ghalta the Unstoppable':(3,'B di Drosan contro D+ di Marc e timori sul costo.'),
 'Loot, the Nexus':(3,'Ramp apprezzato da E.B e Sol4r1s, D+ di Drosan.'),
 'Marwyn, the Preserver':(3.5,'Corpo apprezzato; abilità accessorie valutate con moderazione.'),
 'Pia, Aether Ascetic':(3,'Ora sostenuta da recensioni Limited specifiche, con condizione sui bersagli.'),
 'Titanbones, Towering Heart':(2.5,'Potenziale con vita ripetuta contro rischio senza supporto e D di Marc.'),
 'Way of the Paradox':(3,'Drosan favorevole, Sol4r1s condizionato, Arena Zone cauta.'),
 'Yoshimaru, Scrappy Stray':(3.5,'Apprezzamenti FR/DE per interazione e corpo, ma serve un bersaglio proprio valido.'),
 'Keeper of the Quiet Hour':(None,'La critica riguarda soprattutto la priorità in draft simulati; insufficiente per sintetizzare il rendimento Sealed.'),
}

def enrich(cards):
    for c in cards:
        s=c.get('sentiment')
        if not s:
            continue
        if c['name'] in DECISIONS:
            score,reason=DECISIONS[c['name']]
        elif s['tone'] in ('positivo','molto-positivo','cauto'):
            score={'positivo':4,'molto-positivo':4.5,'cauto':2}[s['tone']]
            reason=s['summary']
        elif s['tone'] in ('sideboard','insufficiente'):
            score,reason=None,'Giudizio situazionale o evidenze insufficienti: nessun voto neutro automatico.'
        else:
            raise AssertionError('Serve decisione editoriale: '+c['name'])
        s.update(index=score,indexReason=reason,indexMethod='Sintesi editoriale 1–5, passi di 0,5; non media dei voti o misura statistica.',
                 indexDate='2026-09-25',evidenceDocuments=len({x['url'] for x in s['sources']}),confidence='Preliminare')
