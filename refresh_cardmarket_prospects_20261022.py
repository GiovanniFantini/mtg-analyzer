"""Use exclusively directly observed Cardmarket values for active card research.

Offline, idempotent overlay. Original Scryfall snapshots remain historical inputs
for Oracle/legality research and the superseded analysis, never price fallbacks.
"""
import copy
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
EXP=ROOT/'expansions/reality-fracture'
RESEARCH=ROOT/'research/reality-fracture-20261022'
DATE='2026-10-22'
CURRENT_SOURCE='cardmarket-browser-20261022'
HISTORY_SOURCE='cardmarket-browser-20261018'

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eur(value):return f'{value:.2f}'.replace('.',',')+' euro'

def main():
    snapshot=read(RESEARCH/'cardmarket-listings-20261022.json')
    details=read(RESEARCH/'cardmarket-product-checks-20261022.json')
    historical=read(RESEARCH/'cardmarket-history-20261018.json')
    lookup={(row['url'].split('/')[-2],row['name']):row for row in snapshot['rows']}
    cols=details['columns']
    checks={kind:{r[0]:dict(zip(cols,r)) for r in details[kind+'Rows']} for kind in ['default','nonfoil','foil']}
    cards=read(EXP/'cards.json');appendix=read(EXP/'prospects-commander-20261022.json')
    records=cards['cards']+appendix['cards']
    for card in records:
        p=card['prospects'];old=p['price'];name=card['name'];set_=card['set'].upper()
        group={'FRA':'Reality-Fracture','FRC':'Commander-Reality-Fracture','SPG':'Special-Guests'}[set_]
        product_name=(name+' (V.1)') if card.get('basic') else card.get('full',name)
        row=lookup[(group,product_name)]
        # Default product pages are later than the listing, so their reading takes
        # priority for the same product/filter. Both observations remain archived.
        default=checks['default'].get(name) if set_=='SPG' else None
        nf=checks['nonfoil'].get(name);foil=checks['foil'].get(name)
        number=str(old['number'])
        for checked in [default,nf,foil]:
            if checked:assert str(checked['collectorNumber'])==number,(name,number,checked)
        current=default['from'] if default else row['from']
        previous=historical['base_above_threshold'].get(number) if set_=='FRA' else None
        delta=round((current/previous-1)*100,2) if previous is not None else None
        comparison={'date':'2026-10-18','source':'Cardmarket','sourceId':HISTORY_SOURCE,'samePrinting':True if previous is not None and (default or nf) else None,'sameProduct':True if previous is not None else None,'metric':'from','finishFilter':'any','from':previous,'nonfoil':None,'changePct':delta,'status':'comparable' if previous is not None else 'missing_reference','note':'Confronto dei minimi From del prodotto base, senza isolamento della finitura. Lo snapshot del 18 ottobre conserva solo i valori strettamente superiori a 0,10 euro; gli altri non sono zeri.'}
        outlook=copy.deepcopy(old['outlook'])
        outlook['downsideRisks']=[r for r in outlook['downsideRisks'] if not r.startswith('Il riferimento è già salito:') and not r.startswith('Il minimo Cardmarket è già salito:')]
        if delta is not None and delta>20:outlook['downsideRisks'].append('Il minimo Cardmarket è già salito: servono vendite e domanda persistenti per sostenere questo livello.')
        outlook['priceAuthority']='Cardmarket'
        outlook['action']='verificare_offerte_cardmarket_della_stessa_stampa_e_finitura'
        position=f'Il minimo Cardmarket osservato è {eur(current)}. '
        if current<=0.10:
            position+='Non supera la soglia personale di vendita di 0,10 euro; un premio foil o di una variante richiede una quotazione distinta.'
        else:position+='Supera la soglia personale di vendita di 0,10 euro, ma resta un prezzo di offerta, prima di commissioni, materiali e tempo.'
        if delta is not None:
            direction='aumentato' if delta>0 else 'diminuito' if delta<0 else 'rimasto invariato'
            position+=f' Dal 18 ottobre il minimo dello stesso prodotto è {direction} ({delta:+.2f}%). Questo movimento non dimostra né esclude crescita della domanda.'
        else:position+=' Manca un minimo storico esatto confrontabile: nessuna variazione percentuale viene calcolata.'
        market=default or nf
        market_assessment=None
        if market and market['average30'] and market['average7']:
            ratio=round((market['average7']/market['average30']-1)*100,2)
            market_assessment={'source':'Cardmarket','finishFilter':'any' if default else 'nonfoil','average7Vs30Pct':ratio,'note':f"La media a 7 giorni è {eur(market['average7'])}, quella a 30 giorni {eur(market['average30'])}. Le finestre si sovrappongono e possono avere campioni diversi: non è una previsione né la variazione del minimo."}
        outlook['marketAssessment']=position
        outlook['windowAssessment']=market_assessment
        price={'date':DATE,'source':'Cardmarket','sourceId':CURRENT_SOURCE,'sourceLabel':'Cardmarket','url':row['url'],'currency':'EUR','metric':'Cardmarket From, minimo richiesto per il prodotto; non ricavo realizzato','metricLabel':'Minimo Cardmarket (From)','finishFilter':'any','printingId':old['printingId'],'set':old['set'],'number':number,'productName':product_name,'collectorNumberVerified':bool(default or nf or foil),'from':current,'listingFrom':row['from'],'nonfoil':nf['from'] if nf else None,'foil':foil['from'] if foil else None,'finishReadings':{'nonfoil':dict(nf,url=row['url']+'?isFoil=N',source='Cardmarket',filter='N') if nf else None,'foil':dict(foil,url=row['url']+'?isFoil=Y',source='Cardmarket',filter='Y') if foil else None},'marketMetrics':dict(market,source='Cardmarket',finishFilter='any' if default else 'nonfoil') if market else None,'comparison':comparison,'variants':[],'outlook':outlook,'methodNote':'Minimo From del prodotto Cardmarket, senza filtri lingua, condizione o paese del venditore; spedizione esclusa. Il minimo generale non isola la finitura. Foil e non foil sono valorizzati soltanto dove il filtro è stato verificato. Listino e schede sono rilevazioni successive e possono differire. Mancano volumi di vendita verificati.','coverageNote':'387 prodotti rilevati nei listini, riferiti alle 382 identità analizzate. Lettura sistematica delle finiture fermata dalla verifica di sicurezza Cardmarket; nessuna sostituzione con altre fonti.'}
        p['price']=price
        p['sources']=sorted((set(p['sources'])-{'echomtg'})|{CURRENT_SOURCE}|({HISTORY_SOURCE} if previous is not None else set()))
    write(EXP/'cards.json',cards);write(EXP/'prospects-commander-20261022.json',appendix)
    by_name={c['name']:c for c in records}
    discovery=read(EXP/'discovery.json')
    for card in discovery['cards']:
        price=by_name[card['name']]['prospects']['price']
        card['priceProspect']=price['outlook']
        card['priceReference']={k:price[k] for k in ['date','source','url','currency','metric','from','nonfoil','foil','comparison','printingId']}
    discovery['research']['priceAuthority']='Cardmarket'
    write(EXP/'discovery.json',discovery)
    prices=read(EXP/'prices.json')
    prices['missing']=['Il valore atteso del box richiede prezzi distinti per tutte le finiture e varianti della collazione.']
    prices['references']={'available':True,'date':DATE,'source':'Cardmarket','metric':'From per prodotto; finiture isolate solo dove verificate','location':'cards.json: cards[].prospects.price e appendice Commander','cardmarketFromAvailable':True,'soldPricesAvailable':False,'boxEVUpdated':False,'catalogCoverage':295,'commanderCoverage':87,'nonfoilCoverage':sum(c['prospects']['price']['nonfoil'] is not None for c in records),'foilCoverage':sum(c['prospects']['price']['foil'] is not None for c in records),'missing':'Serie storica esatta per le carte a 0,10 euro o meno nello snapshot del 18 ottobre; finiture e varianti non verificate; volumi delle vendite.'}
    write(EXP/'prices.json',prices)
    sources=read(EXP/'sources.json');research=sources['research']
    for id_,filename,label in [(CURRENT_SOURCE,'cardmarket-listings-20261022.json','Listini e schede Cardmarket, 22 ottobre'),(HISTORY_SOURCE,'cardmarket-history-20261018.json','Snapshot storico Cardmarket, 18 ottobre')]:
        entry={'id':id_,'publisher':'Cardmarket','kind':'marketplace-direct-browser','url':'https://www.cardmarket.com/en/Magic/Spoilers/Reality-Fracture','retrieved':DATE if id_==CURRENT_SOURCE else '2026-10-18','status':'retrieved','label':label,'snapshot':'research/reality-fracture-20261022/'+filename,'snapshotSha256':hashlib.sha256((RESEARCH/filename).read_bytes()).hexdigest(),'scope':'Prezzi richiesti, non ricavi di vendita; nessun filtro lingua/condizione/paese; spedizione esclusa.'}
        research['sources']=[s for s in research['sources'] if s['id']!=id_]+[entry]
    research['publishers']=sorted({s['publisher'] for s in research['sources'] if s['status']=='retrieved'})
    research['publisherCount']=len(research['publishers'])
    research['methodology']['prices']='Unica autorità dei valori attivi: Cardmarket, lettura diretta del browser del 22 ottobre. Minimo From per prodotto, senza isolamento della finitura salvo filtro N/Y verificato. Confronto del minimo dello stesso prodotto con il 18 ottobre solo dove conservato esattamente. Scryfall resta fonte Oracle/legalità: nessuna quotazione Scryfall attiva.'
    research['priceAuthority']='Cardmarket'
    research['scope']['treatmentRule']='Valutazione di gioco per identità; prezzi per prodotto, finiture separate solo dove il filtro è verificato.'
    research['priceCoverage']=prices['references']
    research['unavailable']=[s for s in research.get('unavailable',[]) if s.get('publisher')!='Cardmarket']
    research['collectionLimitations']=['Le pagine prodotto hanno successivamente presentato la verifica di sicurezza Cloudflare. Usati soltanto i valori già letti, senza aggirare il controllo.']
    research['sourceDisagreements']=[s for s in research.get('sourceDisagreements',[]) if not {'echomtg','scryfall-api'}.issubset(set(s.get('sources',[])))]
    write(EXP/'sources.json',sources)
    guides=read(EXP/'guides.json')
    addition=f'<p id="prospects-research">Ricerca del 22 ottobre: 295 carte del catalogo e 87 Commander, con {research["publisherCount"]} editori o servizi. <a href="data/cards.json">Analisi del catalogo</a> · <a href="prospects-commander-20261022.json">Appendice Commander</a> · <a href="data/sources.json">Fonti, date e metodo</a>. Valori esclusivamente Cardmarket: minimo From del prodotto, finiture isolate solo se verificate. Il confronto al 18 ottobre usa soltanto minimi Cardmarket esatti conservati. Prezzi richiesti, non ricavi realizzati; spedizione esclusa. Nessun prezzo obiettivo o probabilità di rialzo.</p>'
    guides['fragments']['discovery.method']=re.sub(r'<p id="prospects-research">.*?</p>',lambda _:addition,guides['fragments']['discovery.method'])
    write(EXP/'guides.json',guides)
    summary={'date':DATE,'priceAuthority':'Cardmarket','identities':len(records),'listings':len(snapshot['rows']),'historicalComparable':sum(c['prospects']['price']['comparison']['status']=='comparable' for c in records),'nonfoilVerified':prices['references']['nonfoilCoverage'],'foilVerified':prices['references']['foilCoverage'],'abovePersonalSellThreshold':sum(c['prospects']['price']['from']>0.10 for c in records),'historicalEVUpdated':False,'highestFrom':sorted([{'name':c['name'],'set':c['set'],'from':c['prospects']['price']['from'],'comparison':c['prospects']['price']['comparison']} for c in records],key=lambda c:c['from'],reverse=True)[:20]}
    write(RESEARCH/'cardmarket-assessment-20261022.json',summary)
    assessment=read(RESEARCH/'assessment-summary.json')
    assessment.update({'publishers':research['publishers'],'priceAuthority':'Cardmarket','priceMetric':'From per prodotto, finitura any salvo verifica distinta','eurReferenceAvailable':295,'eurComparable':summary['historicalComparable'],'verifiedNonfoil':summary['nonfoilVerified'],'verifiedFoil':summary['foilVerified']})
    write(RESEARCH/'assessment-summary.json',assessment)
    print(json.dumps({k:v for k,v in summary.items() if k!='highestFrom'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
