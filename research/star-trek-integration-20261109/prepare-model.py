"""Transcribe the pinned Draftmancer model into the shared declarative contract."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
audit=json.loads((OUT/'source-audit.json').read_text(encoding='utf-8'))
groups={}
def group(name,lo,hi,count,rarity=None,set_code='TRK'):
    groups[name]=dict(set=set_code,min=lo,max=hi,count=count)
    if rarity:groups[name]['rarity']=rarity
for rarity,count in [('common',81),('uncommon',110),('rare',80),('mythic',25)]:group('main-'+rarity,1,306,count,rarity)
for name,lo,hi,counts in [('scene',338,362,{'uncommon':10,'rare':8,'mythic':7}),('lcars',363,391,{'uncommon':7,'rare':14,'mythic':8}),('classic',402,425,{'uncommon':5,'rare':13,'mythic':6}),('klingon',426,435,{'common':1,'uncommon':6,'rare':3}),('borderless',332,337,{'rare':5,'mythic':1})]:
    for rarity,count in counts.items():group(name+'-'+rarity,lo,hi,count,rarity)
group('shocks',392,401,10,'rare');group('duals',1,306,10,'common')
group('default-basic',317,326,10);group('holodeck-basic',312,316,5);group('away-basic',307,311,5)
group('stardates',1,30,30,'mythic','SDS')
recipe=[dict(op='draw',id='common',count=7,unique=True,branches=[dict(group='main-common',weight=1)]),
 dict(op='replace',id='klingon-common',target='common',chance=.029,branches=[dict(group='klingon-common',weight=1)]),
 dict(op='replace',id='stardates',target='common',chance=.04,branches=[dict(group='stardates',weight=1)])]
def draw(ident,weights,count=1,foil=False,unique=False):
    total=sum(w for g,w in weights)
    rule=dict(op='draw',id=ident,branches=[dict(group=g,weight=w/total) for g,w in weights])
    if count!=1:rule['count']=count
    if foil:rule['foil']=True
    if unique:rule['unique']=True
    recipe.append(rule)
draw('uncommon',[('main-uncommon',78.1),('scene-uncommon',7.7),('lcars-uncommon',4.6),('classic-uncommon',4.6),('klingon-uncommon',5)],3,unique=True)
unknown=['klingon-common','klingon-rare','scene-rare','scene-mythic','lcars-rare','lcars-mythic','classic-rare','classic-mythic','borderless-rare','borderless-mythic','shocks']
known=[('main-common',20.8),('main-uncommon',54.1),('main-rare',16.7),('main-mythic',2.6),('klingon-uncommon',1),('scene-uncommon',1.5),('lcars-uncommon',1)]
wild_residual=100-sum(w for g,w in known)
draw('wildcard',known+[(g,wild_residual/len(unknown)) for g in unknown])
known=[('main-rare',80.1),('main-mythic',12.4),('scene-rare',1),('lcars-rare',1.8),('classic-rare',1.5),('borderless-rare',1),('shocks',1.4)]
rare_unknown=['klingon-rare','scene-mythic','lcars-mythic','classic-mythic','borderless-mythic']
rare_residual=100-sum(w for g,w in known)
draw('rare',known+[(g,rare_residual/len(rare_unknown)) for g in rare_unknown])
known=[('main-common',51.2),('main-uncommon',34.7),('main-rare',6.3),('main-mythic',1),('klingon-uncommon',1),('scene-uncommon',1.6),('lcars-uncommon',1.1)]
foil_residual=100-sum(w for g,w in known)
draw('foil',known+[(g,foil_residual/len(unknown)) for g in unknown],foil=True)
# The source picks a normalized land family then foil independently at 20%.
land=[]
for g,w in [('duals',50),('default-basic',33.4),('holodeck-basic',8.4),('away-basic',8.4)]:
    land.extend([dict(group=g,weight=w*.8/100.2),dict(group=g,weight=w*.2/100.2,foil=True)])
recipe.append(dict(op='draw',id='land',branches=land))
limitations=[
 'Modello di simulazione Draftmancer, verificato sul codice sorgente indicato; non certifica le frequenze fisiche esatte o i fogli di stampa.',
 'Adattamento dei pesi e dei gruppi del modello sorgente, non replica integrale del generatore. Draftmancer protegge dai duplicati di stampa attraverso gli slot e consuma pool di copie; questo adattamento usa buste indipendenti e unicità per identità solo dentro gli slot comuni base e non comuni. Ordine di estrazione e gestione dei duplicati sono diversi.',
 'Le frequenze ufficiali meno dell’1% conservano quel limite nei dati published. Il modello ripartisce il residuo in parti uguali fra i rami non specificati: wildcard 2,3/11, rare 0,8/5, foil 3,1/11 punti percentuali.',
 'Dentro ogni gruppo il modello estrae uniformemente. Le varianti grafiche possono quindi modificare le frequenze delle identità; non sono equiprobabili tutte le carte del catalogo.',
 'Sette posizioni comuni, con sostituzioni indipendenti Klingon 2,9% e Stardates 4%; al massimo una Stardates non foil per busta. Nessuna Stardates negli slot foil o wildcard.',
 'Tre non comuni distinte per identità e comuni base distinte per identità; le sostituzioni Klingon e gli altri slot possono ripetere una identità. Le buste sono indipendenti. Nessuna garanzia di bilanciamento colori, opzione disattivata nel modello sorgente.',
 'Lo slot terra normalizza il totale arrotondato 100,2; foil al 20% come nel modello sorgente. Include Away Team foil come il modello e la lista degli slot ufficiale, pur restando una contraddizione con il paragrafo generale del trattamento.',
 'Non trasferire queste aperture a un valore economico atteso del box o a percentuali di vittoria.'
]
model=dict(date='2026-11-09',sourceCommit=audit['draftmancerCommit'],source='Draftmancer TRKBoosterFactory',groups=groups,recipe=recipe,limitations=limitations,estimatedResidualPercentages=dict(wildcard=wild_residual,rare=rare_residual,foil=foil_residual))
(OUT/'booster-model.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Prepared',len(groups),'groups and',len(recipe),'rules')
