'use strict';
/* Policy 4: bounded deck search over public data and the seat's own history.
 * No table/session object, future packs, storage or DOM is accepted here.
 * Objective values and source weights are heuristics, never win probabilities.
 */
((root)=>{
 const COLORS=[...'WUBRG'],MANA=[...COLORS,'C'],TYPES=['Plains','Island','Swamp','Mountain','Forest'];
 const STYLES={power:{},adaptive:{signals:.45},signals:{signals:1.35,open:.2},bomb:{anchor:.45},
  force:{},synergy:{synergy:1.25},aggro:{attack:.3,early:.3},control:{defense:.3,answers:.25},
  fixing:{splash:.25},denial:{denial:true}};
 const clamp=(x,a,b)=>Math.max(a,Math.min(b,x)),sum=a=>a.reduce((n,x)=>n+x,0);
 const compare=(a,b)=>String(a)<String(b)?-1:String(a)>String(b)?1:0;
 const stable=(a,b)=>compare(a.id,b.id)||compare(a.uid,b.uid);
 function create(format){
  const config=format.botPolicy;if(!config?.available)throw Error('Politica v4 non disponibile: dati minimi incompleti');
  const byId=Object.fromEntries(format.cards.map(c=>[c.id,c])),profiles=config.profiles;
  const active=Object.keys(profiles).map(id=>byId[id]);
  if(active.some(c=>!c||(!c.basic&&!Number.isFinite(c.score))))throw Error('V4 richiede voti espliciti sulle stampe attive');
  const rating=c=>c.basic?0:c.score,profile=c=>profiles[c.id];
  const has=(c,r)=>profile(c)?.roles.includes(r),total=format.rounds*format.packSize;
  const target=config.minDeckSize,freeBasics=config.allowedBasics||[];
  // Stable expectation from declared recipe. Dependencies/exclusions are an
  // approximation here, not a second collator or a claim about unopened packs.
  const weights={};
  if(format.collation?.schemaVersion===1){
   const slots={};
   for(const rule of format.collation.recipe){
    const dist={};const count=(rule.count||1)*(rule.op==='replace'?rule.chance:1);
    for(const branch of rule.branches){const ids=format.collation.groups[branch.group];
     for(const id of ids){dist[id]=(dist[id]||0)+count*branch.weight/ids.length;
      if(rule.op==='pair'){const pair=(format.collation.partners||[]).find(p=>p.includes(id));if(pair){const other=pair.find(x=>x!==id);dist[other]=(dist[other]||0)+count*branch.weight/ids.length;}}}}
    if(rule.op==='replace'&&slots[rule.target])for(const [id,w] of Object.entries(slots[rule.target]))weights[id]-=w*count/Math.max(1,sum(Object.values(slots[rule.target])));
    for(const [id,w] of Object.entries(dist))weights[id]=(weights[id]||0)+w;slots[rule.id]=dist;
   }
  }
  const weightTotal=sum(Object.values(weights).map(w=>Math.max(0,w)));
  const frequency=c=>weightTotal?Math.max(0,weights[c.id]||0)/weightTotal:1/Math.max(1,active.length);
  const axisAvailability=Object.fromEntries(config.relations.map(r=>[r.id,sum(active.map(c=>frequency(c)*(profile(c).synergy.enablers[r.id]||0)))]));
  function needs(c,colors,sources={}){
   const need={};
   for(const symbol of profile(c).symbols){
    const choices=symbol.split('/').filter(x=>MANA.includes(x));
    if(!choices.length||symbol.includes('P')||symbol.split('/').some(x=>/^\d+$/.test(x)))continue;
    const allowed=choices.filter(x=>x==='C'||colors.includes(x));if(!allowed.length)return null;
    const color=allowed.sort((a,b)=>(sources[b]||0)-(sources[a]||0)||(need[a]||0)-(need[b]||0)||MANA.indexOf(a)-MANA.indexOf(b))[0];need[color]=(need[color]||0)+1;
   }
   return need;
  }
  const fits=(c,lane)=>needs(c,lane)!==null;
  function turn(c,own){
   const p=profile(c);if(p.variable)return Math.max(3,c.mv+2);if(!p.curve.reduction)return Math.max(1,c.mv);
   const available=own.filter(x=>x.creature&&x.mv<=4),resource=p.curve.reductionResource;
   const reduction=['power','toughness'].includes(resource)?Math.max(0,...available.map(x=>profile(x).curve[resource]||0)):
    resource==='creatures'?available.length*.5:resource==='artifacts'?own.filter(x=>profile(x).curve.artifact&&x.mv<=4).length:0;
   // Deployment and survival are uncertain. A printed reduction is never
   // silently converted into a guaranteed early play.
   return reduction?Math.min(Math.max(1,c.mv),Math.max(4,c.mv-reduction)):Math.max(1,c.mv);
  }
  function probability(size,sources,draws,required){
   // Hypergeometric tail, linearly interpolated for declared fractional sources.
   if(required<=0)return 1;
   if(sources<=0)return 0;
   const exact=k=>{k=clamp(k,0,size);let dist=Array(required).fill(0);dist[0]=1;let success=0;
    for(let d=0;d<Math.min(size,draws);d++){const next=Array(required).fill(0);for(let n=0;n<required;n++){const p=clamp((k-n)/(size-d),0,1);next[n]+=dist[n]*(1-p);if(n+1===required)success+=dist[n]*p;else next[n+1]+=dist[n]*p;}dist=next;}return clamp(success,0,1);};
   const low=Math.floor(sources);return exact(low)*(1-(sources-low))+exact(low+1)*(sources-low);
  }
  const probabilityCache=new Map();
  const sourceCache=new Map();
  const allocationCache=new Map();
  function chance(sources,t,pips=1){const s=Math.round(sources*20)/20,key=[s,t,pips].join(':');
   if(!probabilityCache.has(key))probabilityCache.set(key,probability(target,s,Math.min(target,7+Math.max(0,Math.ceil(t)-1)),pips));return probabilityCache.get(key);}
  const directColors=new Map();
  function direct(c){if(!directColors.has(c.id)){const m=profile(c).mana;directColors.set(c.id,[...new Set(m.abilities.filter(a=>!a.restricted).flatMap(a=>a.colors))]);}return directColors.get(c.id);}
  function landColors(c,basics,t=6,lands=[]){const fetch=profile(c).mana.fetch;
   if(!fetch||fetch.restricted||t<(fetch.readyTurn||1))return direct(c);
   const owned=lands.filter(x=>x.basic).flatMap(direct),available=[...COLORS.filter(color=>basics[color]>0),...lands.flatMap(direct)];
   const payable=fetch?.cost?.every(symbol=>{const choices=symbol.split('/').filter(x=>COLORS.includes(x));return !choices.length||choices.some(x=>available.includes(x));})??true;
   return fetch&&!fetch.restricted&&payable&&t>=(fetch.readyTurn||1)?[...new Set([...direct(c),...owned,...COLORS.filter(color=>basics[color]>0)])]:direct(c);
  }
  function landSources(lands,basics,t){
   const counts=Object.fromEntries(MANA.map(x=>[x,basics[x]||0]));
   for(const c of lands)for(const color of landColors(c,basics,t,lands)){const tapped=profile(c).mana.tapped||profile(c).mana.fetch?.tapped;counts[color]+=(tapped&&t===1?0:tapped&&t<=3?.8:1);}
   return counts;
  }
  function landUnits(lands,basics,t){return [
   ...lands.map(c=>{const tapped=profile(c).mana.tapped||profile(c).mana.fetch?.tapped;return Object.fromEntries(landColors(c,basics,t,lands).map(color=>[color,tapped&&t===1?0:tapped&&t<=3?.8:1]));}),
   ...Object.entries(basics).filter(([,n])=>n>0).map(([color,n])=>({[color]:n}))];}
  function sourceModel(spells,lands,basics,targetTurn=6){
   const cacheKey=[spells.map((c,i)=>c.id+':'+(c._entry?.uid??i)+':'+!!c._modeOnly).join(','),lands.map(c=>c.id).sort().join(','),...COLORS.map(c=>basics[c]||0),targetTurn].join('|');
   if(sourceCache.has(cacheKey))return sourceCache.get(cacheKey);
   const base=landSources(lands,basics,targetTurn),sources={...base},uses={},units=landUnits(lands,basics,targetTurn);
   const targets=[...lands.map(c=>({colors:direct(c),basic:c.basic,subtypes:profile(c).mana.subtypes})),
    ...Object.entries(basics).flatMap(([color,count])=>Array.from({length:count},()=>({colors:[color],basic:true,subtypes:[TYPES[COLORS.indexOf(color)]]})))];
   const cyclers=spells.filter(c=>profile(c).mana.cycling.length),baseUnits=[...units];
   for(const [index,c] of spells.entries()){const p=profile(c),entryUse={uid:c._entry?.uid??'spell-'+index,cycling:0,producer:0,alternativeLand:0,colors:[],weights:{}};
    if(!p.mana.cycling.length&&!p.mana.alternativeLand&&!direct(c).length){uses[c.id]=(uses[c.id]||[]).concat(entryUse);continue;}
    const alternate=p.mana.alternativeLand;
    if(alternate&&!alternate.restricted&&!(alternate.tapped&&targetTurn<=1)){
     const weight=(alternate.tapped&&targetTurn<=3?.4:.5)*(c._modeOnly?2:1);entryUse.alternativeLand=weight;
     for(const color of alternate.colors){entryUse.weights[color]=Math.max(entryUse.weights[color]||0,weight);entryUse.colors.push(color);}
    }
    for(const cycle of p.mana.cycling){
     const eligible=targets.filter(x=>cycle.kind==='basic'?x.basic:x.subtypes.includes(cycle.type));
     const cost=sum([...cycle.cost.matchAll(/\{([^}]+)\}/g)].map(m=>Math.max(...m[1].split('/').map(x=>/^\d+$/.test(x)?+x:1))));
     const symbols=[...cycle.cost.matchAll(/\{([^}]+)\}/g)].map(m=>m[1]);
     if(!eligible.length||targetTurn<=cost)continue;
     const access=Math.min(chance(lands.length+sum(Object.values(basics)),Math.max(1,cost),cost),symbolChance(symbols,MANA,baseUnits,Math.max(2,cost)));
     if(access<.65)continue;
     for(const color of new Set(eligible.flatMap(x=>x.colors))){
      const competitors=cyclers.filter(other=>profile(other).mana.cycling.some(cy=>targets.some(x=>x.colors.includes(color)&&(cy.kind==='basic'?x.basic:x.subtypes.includes(cy.type))))).length;
      const weight=(c._modeOnly?1:.5)*access*Math.min(1,eligible.filter(x=>x.colors.includes(color)).length/Math.max(1,competitors));
      entryUse.cycling=Math.max(entryUse.cycling,weight);entryUse.weights[color]=Math.max(entryUse.weights[color]||0,weight);entryUse.colors.push(color);
     }
    }
    // Only direct, accessible nonlands can help. Restricted abilities do not
    // silently become unrestricted sources. Expensive producers are very slow.
    const n=needs(c,MANA,base),cast=!c._modeOnly&&!p.variable&&n&&chance(lands.length+sum(Object.values(basics)),Math.max(1,c.mv),Math.ceil(c.mv))>=.65&&Object.entries(n).every(([color,pips])=>chance(base[color],turn(c,spells),pips)>=.65);
    if(cast&&targetTurn>=Math.max(1,c.mv+1))for(const color of direct(c)){
     const activation=profile(c).mana.abilities.find(a=>!a.restricted&&a.colors.includes(color))?.activation||'';
     const activationColors=[...activation.matchAll(/\{([WUBRGC])\}/g)].map(m=>m[1]);
     if(activationColors.some(x=>!base[x]))continue;
     const activationMana=sum([...activation.matchAll(/\{(\d+)\}/g)].map(m=>+m[1]));
     const weight=(c.mv<=3?.35:c.mv<=5?.15:0)/(1+activationMana);entryUse.weights[color]=Math.max(entryUse.weights[color]||0,weight);entryUse.producer=Math.max(entryUse.producer,weight);entryUse.colors.push(color);
    }
    uses[c.id]=(uses[c.id]||[]).concat(entryUse);units.push({...entryUse.weights,_uid:entryUse.uid,_cardId:c.id,_spell:true});
   }
   for(const color of MANA)sources[color]=sum(units.map(u=>u[color]||0));
   const result={base,sources,uses,targets,units};if(sourceCache.size>4000)sourceCache.delete(sourceCache.keys().next().value);sourceCache.set(cacheKey,result);return result;
  }
  function castability(c,colors,model,t){
   const ownUid=c._entry?.uid??model.units.find(u=>u._spell&&u._cardId===c.id)?._uid;
   const units=model.units.filter(u=>!(u._spell&&u._uid===ownUid));
   return symbolChance(profile(c).symbols,colors,units,t);
  }
  const symbolConstraints=new Map();
  const maskColors=Array.from({length:64},(_,mask)=>MANA.filter((_,i)=>mask&1<<i));
  function paymentConstraints(symbols,colors){
   const key=symbols.join(':')+'|'+colors.join('');if(symbolConstraints.has(key))return symbolConstraints.get(key);
   const groups=[];for(const symbol of symbols){
    if(symbol.includes('P')||symbol.split('/').some(x=>/^\d+$/.test(x)))continue;
    const options=symbol.split('/').filter(x=>MANA.includes(x)&&(x==='C'||colors.includes(x)));
    if(!options.length){if(/[WUBRGC]/.test(symbol)){symbolConstraints.set(key,null);return null;}continue;}
    groups.push(options.reduce((n,color)=>n|1<<MANA.indexOf(color),0));
   }
   const masks=new Set();for(const group of groups){const previous=[...masks];masks.add(group);for(const mask of previous)masks.add(mask|group);}
   const result=[...masks].map(mask=>({mask,pips:groups.filter(group=>(group&mask)===group).length}));
   if(symbolConstraints.size>4000)symbolConstraints.clear();symbolConstraints.set(key,result);return result;
  }
  function sourceAmount(units,mask){let value=0;for(const unit of units){let weight=0;for(const color of maskColors[mask])weight=Math.max(weight,unit[color]||0);value+=weight;}return value;}
  function symbolChance(symbols,colors,units,t){const requirements=paymentConstraints(symbols,colors);if(requirements===null)return 0;
   let value=1;for(const {mask,pips} of requirements)value=Math.min(value,chance(sourceAmount(units,mask),t,pips));return value;
  }
  function synergy(c,own,remaining=0){
   if(!config.coverage.synergies)return {adjustment:0,option:0};
   const traits=profile(c).synergy;let adjustment=0,option=0;
   for(const relation of config.relations){
    const axis=relation.id,others=own.filter(x=>x!==c),payoff=traits.payoffs[axis]||0;
    const density=sum(others.map(x=>profile(x).synergy.enablers[axis]||0));
    if(payoff){
     let support=density;
     if(relation.resource){const consumers=sum(own.map(x=>sum(config.relations.filter(r=>r.resource===relation.resource).map(r=>profile(x).synergy.payoffs[r.id]||0))));support=Math.min(support,(relation.resourceBudget??support)/Math.max(1,consumers));}
     const utility=n=>{const threshold=relation.threshold||0,saturation=Math.max(threshold+1,relation.saturation||8);return clamp((n-threshold)/(saturation-threshold),0,1);};
     const reference=profile(c).reference.support?.[axis]??relation.referenceSupport??0,strength=(relation.strength??.6)*payoff;
     adjustment+=(utility(support)-utility(reference))*strength;
     const expected=(axisAvailability[axis]||0)*Math.max(0,remaining)*.25;
     option+=Math.max(0,utility(support+expected)-utility(support))*strength;
    }
    if(traits.enablers[axis]){const beneficiaries=sum(others.map(x=>profile(x).synergy.payoffs[axis]||0));
     // Enabler reference is explicit; it does not count each payoff at full value.
     adjustment+=clamp((beneficiaries-(profile(c).reference.payoffs?.[axis]??relation.referencePayoffs??0))*.06,-.2,.3)*Math.min(1,traits.enablers[axis]);}
   }
   return {adjustment,option};
  }
  const fillExpectations=new Map();
  function replacement(role,lane,remaining,holes){
   if(!holes||remaining<=0)return 0;
   const key=lane+':'+role;
   if(!fillExpectations.has(key)){
    const cards=active.filter(c=>!c.land&&fits(c,lane)&&(role==='spell'||role==='creature'&&c.creature||role==='interaction'&&has(c,'interaction')&&!c.creature));
    const mass=sum(cards.map(frequency));fillExpectations.set(key,{mass,value:mass?sum(cards.map(c=>rating(c)*frequency(c)))/mass:0});
   }
   const row=fillExpectations.get(key);
   // Public marginal mass, remaining own picks and a conservative retention
   // factor estimate uncovered slots. Owned cards keep their absolute value.
   return holes*row.value*(1-Math.exp(-remaining*row.mass*.35/holes));
  }
  function tactical(c,style,own,earlyWeight=1){
   const p=profile(c),early=turn(c,own)<=3;
   return (p.curve.attacker?(style.attack||0):0)+(p.curve.defensive?(style.defense||0):0)
    +(has(c,'interaction')&&(early||!c.creature)?(style.answers||0):0)+(c.creature&&early?(style.early||0)*earlyWeight:0)
    +(has(c,'evasion')?.06:0);
  }
  function build(pool,lane,strategy='adaptive',options={}){
   const style=STYLES[strategy]||STYLES.adaptive,remaining=options.remaining??Math.max(0,total-pool.length),match=options.match??config.match;
   const physical=pool.map(e=>({...byId[e.id],_entry:e})).filter(c=>profile(c));
   const splash=options.splash||null,colors=[...new Set([...lane,...(splash?[splash]:[])])];
   const landTarget=clamp(Math.round(target*(strategy==='aggro'?.4:strategy==='control'?.45:.425)),0,target),spellTarget=target-landTarget;
   const candidates=physical.filter(c=>!c.land&&fits(c,colors)&&(!splash||fits(c,lane)||rating(c)>=3.5));
   const alternativeColors=c=>{
    const m=profile(c).mana,produced=new Set(m.alternativeLand&&!m.alternativeLand.restricted?m.alternativeLand.colors:[]);
    for(const cy of m.cycling){
    const costs=[...cy.cost.matchAll(/\{([^}]+)\}/g)].map(m=>m[1]);
    if(!costs.every(symbol=>{const choices=symbol.split('/').filter(x=>COLORS.includes(x));return symbol.includes('P')||symbol.split('/').some(x=>/^\d+$/.test(x))||!choices.length||choices.some(x=>colors.includes(x));}))continue;
    if(cy.kind==='basic'){
     for(const color of freeBasics.filter(x=>colors.includes(x)))produced.add(color);
     for(const land of physical.filter(x=>x.land&&x.basic))for(const color of direct(land).filter(x=>colors.includes(x)))produced.add(color);
    }
    else{
     const color=COLORS[TYPES.indexOf(cy.type)];if(colors.includes(color)&&freeBasics.includes(color))produced.add(color);
     for(const land of physical.filter(x=>x.land&&profile(x).mana.subtypes.includes(cy.type)))for(const color of direct(land).filter(x=>colors.includes(x)))produced.add(color);
    }
    }return [...produced].filter(x=>colors.includes(x));
   };
   const canAlternate=c=>!c.land&&alternativeColors(c).length>0;
   const sourceUtility=c=>{
    const provides=new Set(alternativeColors(c));
    return (splash&&provides.has(splash)?10:0)+colors.filter(x=>provides.has(x)).length;
   };
   const expendable=c=>!fits(c,colors)||!fits(c,lane)&&rating(c)<3.5;
   const manaOnly=physical.filter(canAlternate).sort((a,b)=>sourceUtility(b)-sourceUtility(a)||Number(!expendable(a))-Number(!expendable(b))||rating(a)-rating(b)||stable(a._entry,b._entry)).slice(0,options.sourceModes||0).map(c=>({...c,_modeOnly:true}));
   let spells=[],choices=candidates.filter(c=>!manaOnly.some(x=>x._entry.uid===c._entry.uid)),rejected=new Set();
   const choose=()=>{
    while(spells.length<spellTarget&&choices.length){
     const early=spells.filter(c=>c.creature&&!profile(c).variable&&turn(c,spells)<=3).length,answers=spells.filter(c=>has(c,'interaction')&&!c.creature).length;
     let best=-1,value=-Infinity;
     for(let i=0;i<choices.length;i++){
      const c=choices[i];if(rejected.has(c._entry.uid)||config.maxCopies&&[...spells,...manaOnly].filter(x=>x.full===c.full).length>=config.maxCopies)continue;
      const syn=config.coverage.synergies?synergy(c,[...spells,c],remaining):{adjustment:0,option:0},earlyCard=c.creature&&!profile(c).variable&&turn(c,spells)<=3;
      const q=rating(c)+tactical(c,style,spells)+(syn.adjustment+syn.option)*(style.synergy||1)
       +(earlyCard&&early<spellTarget*(strategy==='aggro'?.38:strategy==='control'?.23:.3)?.3:0)
       +(has(c,'interaction')&&!c.creature&&answers<Math.max(2,spellTarget*.17)?.2:0)-(fits(c,lane)?0:.65-(style.splash||0));
      if(q>value||q===value&&best>=0&&stable(c._entry,choices[best]._entry)<0){best=i;value=q;}
     }
     if(best<0)break;spells.push(choices.splice(best,1)[0]);
    }
   };
   function allocate(){
    const lands=[],basics=Object.fromEntries(COLORS.map(x=>[x,0])),demand=Object.fromEntries(MANA.map(x=>[x,0])),rows=[];
    const grouped=new Map(),all=[...spells,...manaOnly],hasSource=c=>profile(c).mana.cycling.length||profile(c).mana.alternativeLand||direct(c).length;
    for(const c of spells){const n=needs(c,colors)||{},t=turn(c,spells),symbols=profile(c).symbols,uid=hasSource(c)?c._entry.uid:null;
     for(const [color,pips] of Object.entries(n))demand[color]+=pips*(t<=3?2:1);
     const key=JSON.stringify([symbols,t,uid]);if(!grouped.has(key))grouped.set(key,{symbols,t,uid,weight:0});grouped.get(key).weight+=rating(c);}
    rows.push(...grouped.values());for(const row of rows)row.requirements=paymentConstraints(row.symbols,colors);
    const values=new Map(),turns=[...new Set(rows.map(row=>Math.ceil(row.t)))],masks=[...new Set(rows.flatMap(row=>(row.requirements||[]).map(r=>r.mask)))];let indirect={};
    const timedLands=physical.some(c=>c.land&&(profile(c).mana.tapped||profile(c).mana.fetch));
    const allocationCounts=(ls,bs)=>{const base=!timedLands?landUnits(ls,bs,6):null,common=base?Object.fromEntries(masks.map(mask=>[mask,sourceAmount(base,mask)])):null;
     const supplies=Object.fromEntries(turns.map(t=>{if(common)return [t,common];const units=landUnits(ls,bs,t);return [t,Object.fromEntries(masks.map(mask=>[mask,sourceAmount(units,mask)]))];}));
     return {...landSources(ls,bs,6),_supplies:supplies};};
    const utility=counts=>{const key=JSON.stringify(counts._supplies);if(!values.has(key))values.set(key,sum(rows.map(row=>{
     if(row.requirements===null)return 0;let value=1;const extra=indirect[Math.ceil(row.t)]||[],own=row.uid===null?[]:extra.filter(u=>u._uid===row.uid);
     for(const {mask,pips} of row.requirements){const n=counts._supplies[Math.ceil(row.t)][mask]+sourceAmount(extra,mask)-sourceAmount(own,mask);value=Math.min(value,chance(n,row.t,pips));}
     return row.weight*value;
    })));return values.get(key);};
    const permitted=colors.filter(c=>freeBasics.includes(c));
    if(!permitted.length&&freeBasics.length)permitted.push(freeBasics[0]);
    const needsC=demand.C>0;
    let available=physical.filter(c=>{
     if(!c.land)return false;const m=profile(c).mana,relevant=direct(c).filter(x=>colors.includes(x)||x==='C'&&needsC);
     if(m.tapped&&!m.fetch&&relevant.length<2&&relevant.length>0&&relevant.every(x=>freeBasics.includes(x)))return false;
     return relevant.length>0||!freeBasics.length&&direct(c).includes('C')||m.fetch&&!m.fetch.restricted;
    }).sort((a,b)=>Number(profile(a).mana.tapped||profile(a).mana.fetch?.tapped)-Number(profile(b).mana.tapped||profile(b).mana.fetch?.tapped)||stable(a._entry,b._entry));
    const capacity=Math.max(0,landTarget-manaOnly.length);
    const allocationKey=JSON.stringify([colors,rows,all.filter(hasSource).map(c=>[c.id,c._entry.uid,!!c._modeOnly]),available.map(c=>[c.id,c._entry.uid]),permitted,capacity,options.splashBasics??2]);
    const cached=allocationCache.get(allocationKey);
    if(cached){lands.push(...cached.lands.map(uid=>physical.find(c=>c._entry.uid===uid)));Object.assign(basics,cached.basics);indirect=cached.indirect;}
    const choices=()=>[...available.filter(c=>c.basic||!config.maxCopies||lands.filter(x=>x.full===c.full).length<config.maxCopies).map(c=>({card:c})),...permitted.map(color=>({color}))];
    const increment=(before,produced,weight)=>{
     const result={...before,_supplies:{}};for(const color of produced)result[color]=(result[color]||0)+weight(6);
     const mask=produced.reduce((n,color)=>n|1<<MANA.indexOf(color),0);
     for(const t of turns)result._supplies[t]=Object.fromEntries(masks.map(m=>[m,before._supplies[t][m]+(m&mask?weight(t):0)]));return result;
    };
    const after=(choice,before)=>{
     const fetch=lands.some(c=>profile(c).mana.fetch);
     if(choice.card){const m=profile(choice.card).mana;if(!fetch&&!m.fetch)return increment(before,direct(choice.card),t=>m.tapped&&t===1?0:m.tapped&&t<=3?.8:1);
      return allocationCounts([...lands,choice.card],basics);}
     if(!fetch||basics[choice.color]>0)return increment(before,[choice.color],()=>1);
     return allocationCounts(lands,{...basics,[choice.color]:basics[choice.color]+1});
    };
    const commit=choice=>{if(choice.card){lands.push(choice.card);available=available.filter(c=>c!==choice.card);}else basics[choice.color]++;};
    if(!cached){
    const originalAvailable=[...available];
    const passes=all.some(hasSource)?2:1;
    for(let allocationPass=0;allocationPass<passes;allocationPass++){
    lands.length=0;for(const color of COLORS)basics[color]=0;available=[...originalAvailable];values.clear();
    // Bootstrap every demanded color equally, including primary colors. Multi-
    // pip tails can have zero marginal gain before their first required sources.
    for(const color of MANA.filter(c=>demand[c]>0)){
     const minimum=Math.max(options.splashBasics??2,...spells.map(c=>needs(c,colors)?.[color]||0));
     while(lands.length+sum(Object.values(basics))<capacity){const supplied=allocationCounts(lands,basics),extra=sum((indirect[6]||indirect[turns.at(-1)]||[]).map(unit=>unit[color]||0));if(supplied[color]+extra>=minimum)break;
      const best=choices().map(choice=>({choice,counts:after(choice,supplied)})).filter(x=>x.counts[color]>supplied[color]).sort((a,b)=>utility(b.counts)-utility(a.counts))[0];
      if(!best)break;commit(best.choice);
     }
    }
    while(lands.length+sum(Object.values(basics))<capacity){const supplied=allocationCounts(lands,basics),best=choices().map(choice=>({choice,value:utility(after(choice,supplied))})).sort((a,b)=>b.value-a.value)[0];if(!best)break;commit(best.choice);}
    // Bounded coordinate ascent removes greedy artifacts in the added basics.
    for(let pass=0;pass<capacity*Math.max(1,permitted.length);pass++){
     const before=utility(allocationCounts(lands,basics));let best=null;
     for(const from of permitted.filter(c=>basics[c]>0))for(const to of permitted.filter(c=>c!==from)){
      const candidate={...basics,[from]:basics[from]-1,[to]:basics[to]+1},value=utility(allocationCounts(lands,candidate));
      if(value>before+1e-9&&(!best||value>best.value+1e-9))best={candidate,value};
     }
     if(!best)break;Object.assign(basics,best.candidate);
    }
    if(allocationPass+1<passes){indirect=Object.fromEntries([...new Set([...turns,6])].map(t=>[t,sourceModel(all,lands,basics,t).units.filter(unit=>unit._spell)]));}
    }
    if(allocationCache.size>2000)allocationCache.clear();allocationCache.set(allocationKey,{lands:lands.map(c=>c._entry.uid),basics:{...basics},indirect});
    }
    const chooseBasic=()=>permitted.map(color=>({color,value:utility(allocationCounts(lands,{...basics,[color]:basics[color]+1}))})).sort((a,b)=>b.value-a.value)[0]?.color;
    return {lands,basics,demand,permitted,chooseBasic};
   }
   // Reject and refill to a fixed point. A removed card cannot remain a source,
   // reduction resource, curve play or synergy support in the final objective.
   choose();let allocation;
   for(let pass=0;pass<=candidates.length;pass++){
    allocation=allocate();const all=[...spells,...manaOnly],models=new Map(),bad=[];
    for(const c of spells){const t=turn(c,spells)+(!fits(c,lane)?2:0),key=Math.ceil(t);if(!models.has(key))models.set(key,sourceModel(all,allocation.lands,allocation.basics,key));
     const m=models.get(key),p=castability(c,colors,m,t),n=needs(c,colors,m.sources),off=!fits(c,lane);
     if(!n||p===0||off&&(p<.65||Object.entries(n).some(([color,pips])=>!lane.includes(color)&&pips>1)))bad.push(c);
    }
    if(!bad.length)break;
    for(const c of bad)rejected.add(c._entry.uid);
    spells=spells.filter(c=>!rejected.has(c._entry.uid));choose();
   }
   allocation=allocate();const {lands,basics,demand,permitted}=allocation;
   const missingSpells=Math.max(0,spellTarget-spells.length),manaErrors=[];
   if(remaining===0&&freeBasics.length){let fill=target-spells.length-manaOnly.length-lands.length-sum(Object.values(basics));
    while(fill>0&&permitted.length){const color=allocation.chooseBasic();basics[color]++;fill--;}
   }
   if(remaining===0&&!freeBasics.length){
    const used=new Set([...spells,...manaOnly,...lands].map(c=>c._entry.uid));
    for(const c of physical.filter(c=>!used.has(c._entry.uid)).sort((a,b)=>Number(fits(b,colors))-Number(fits(a,colors))||rating(b)-rating(a)||stable(a._entry,b._entry))){
     if(spells.length+manaOnly.length+lands.length>=target)break;
     if(!c.basic&&config.maxCopies&&[...spells,...lands,...manaOnly].filter(x=>x.full===c.full).length>=config.maxCopies)continue;
     (c.land?lands:spells).push(c);manaErrors.push({id:c.id,reason:'Ripiego per completare il main senza basi aggiungibili: mana o piano insufficienti.'});
    }
   }
   const all=[...spells,...manaOnly],model=sourceModel(all,lands,basics),timed=new Map(),manaEstimates=[];let score=0,manaPenalty=0,creatures=0,early=0,answers=0;
   for(const c of spells){const costTurn=turn(c,spells),t=costTurn,key=Math.ceil(t);if(!timed.has(key))timed.set(key,sourceModel(all,lands,basics,key));
    const m=timed.get(key),colored=castability(c,colors,m,t),ownUid=c._entry.uid;
    const indirect=sum(Object.values(m.uses).flat().filter(u=>u.uid!==ownUid).map(u=>Math.max(u.alternativeLand||0,u.cycling||0,u.producer||0)));
    const count=lands.length+sum(Object.values(basics))+indirect,mana=colored*chance(count,t,Math.ceil(Math.min(costTurn,count+1)));
    manaEstimates.push({id:c.id,uid:c._entry.uid,turn:t,latestTurn:t+(!fits(c,lane)?2:0),requiredSources:Math.ceil(costTurn),probability:mana});
    const ownUse=(m.uses[c.id]||[]).find(u=>u.uid===ownUid),use=Math.max(ownUse?.cycling||0,ownUse?.alternativeLand||0);
    if(colored>0){if(c.creature){creatures+=1-use;if(t<=3&&!profile(c).variable)early+=(1-use)*mana;}if(has(c,'interaction'))answers+=c.creature?.4:1;}
    const penalty=(1-mana)*(fits(c,lane)?1:1.8),syn=config.coverage.synergies?synergy(c,spells,remaining):{adjustment:0,option:0};manaPenalty+=penalty;
    score+=(colored?rating(c):0)+(colored?tactical(c,style,spells,mana)+(syn.adjustment+syn.option)*(style.synergy||1):0)-penalty;
   }
   const progress=clamp(1-remaining/Math.max(1,total),0,1),deficits={early:Math.max(0,spellTarget*(strategy==='aggro'?.38:strategy==='control'?.23:.3)-early),
    creatures:Math.max(0,spellTarget*(strategy==='control'?.52:.65)-creatures),interaction:Math.max(0,spellTarget*.16-answers)};
   const creatureHoles=Math.min(missingSpells,Math.ceil(deficits.creatures)),answerHoles=Math.min(missingSpells-creatureHoles,Math.ceil(deficits.interaction));
   score+=replacement('creature',lane,remaining,creatureHoles)+replacement('interaction',lane,remaining,answerHoles)+replacement('spell',lane,remaining,missingSpells-creatureHoles-answerHoles);
   score+=spells.length*progress*.65;score-=progress*(deficits.early*.14+deficits.creatures*.08+deficits.interaction*.12+missingSpells*.25);
   const used=new Set([...all,...lands].map(c=>c._entry.uid)),excluded=physical.filter(c=>!used.has(c._entry.uid));
   const sideboard=match==='BO3'?excluded.filter(c=>has(c,'sideboard')&&fits(c,lane)).map(c=>c._entry):[];
   return {lane,colors:colors.join(''),splash,spells:all.map(c=>c._entry),manaOnly:manaOnly.map(c=>c._entry),lands:lands.map(c=>c._entry),basics,
    excluded:excluded.map(c=>c._entry),sideboard,holes:{spells:missingSpells,lands:Math.max(0,landTarget-lands.length-manaOnly.length-sum(Object.values(basics)))},
    targetSize:target,slots:all.length+lands.length+sum(Object.values(basics)),score,deficits,manaPenalty,manaErrors,
    sources:model.sources,sourceTurn:6,alternativeUses:model.uses,manaEstimates,match,
    assumptions:['Ricerca limitata per piani, fonti indirette frazionarie, lancio ipergeometrico senza mulligan; vincoli di pagamento approssimati.',
     'Costi ridotti stimati con prudenza; accesso allo splash ammesso fino a due turni dopo, ma il punteggio paga il rischio al turno nominale. Attese di riempimento con fattore prudenziale 0,35. Carte solo fixing non sono minacce.',
     ...(match==='unknown'?['Contesto match sconosciuto: nessun valore di sideboarding.']:[])]};
  }
  function bestBuild(pool,lane,strategy,options={}){
   const alternate=pool.some(e=>{const m=profile(byId[e.id]).mana;return m.cycling.length||m.alternativeLand&&!m.alternativeLand.restricted;});
   let best=build(pool,lane,strategy,options);
   if(alternate){const mode=build(pool,lane,strategy,{...options,sourceModes:1});if(mode.score>best.score+.05)best=mode;}
   const off=pool.map(e=>byId[e.id]).filter(c=>!c.land&&!fits(c,lane)&&rating(c)>=3.5);
   // The allocator now optimizes the basic split; the old fixed 2/3-basic grid
   // is redundant. Do not search colors for spells this policy cannot splash.
   const colors=[...new Set(off.flatMap(c=>c.colors.filter(x=>!lane.includes(x))))].filter(color=>off.some(c=>{
    const n=needs(c,[...lane,color]);return n&&Object.entries(n).every(([key,pips])=>lane.includes(key)||key==='C'||pips<=1);
   })).filter(color=>pool.some(e=>{
    const c=byId[e.id];return freeBasics.includes(color)||direct(c).includes(color)||profile(c).mana.alternativeLand?.colors.includes(color)||profile(c).mana.fetch&&freeBasics.includes(color)||profile(c).mana.cycling.some(cy=>cy.kind==='basic'||cy.type===TYPES[COLORS.indexOf(color)]);
   })).sort();
   for(const color of colors)for(const sourceModes of alternate?[0,1]:[0]){const candidate=build(pool,lane,strategy,{...options,splash:color,sourceModes});if(candidate.score>best.score+.05)best=candidate;}
   return best;
  }
  function finalBuild(pool,strategy='adaptive',options={}){
   const lanes=options.target?[options.target]:Object.keys(format.archetypes).sort();
   return lanes.map(lane=>bestBuild(pool,lane,strategy,{...options,remaining:0})).sort((a,b)=>b.score-a.score||compare(a.lane,b.lane))[0];
  }
  function observe(bot,pack,round,pick){
   bot.memory??={sides:{},observations:{},packets:{},demand:Object.fromEntries(COLORS.map(c=>[c,0]))};
   const memory=bot.memory,key=[round,pick,pack.packetId].join(':');if(memory.observations[key])return;
   memory.observations[key]=true;const direction=String(format.directions[round-1]),side=memory.sides[direction]??={values:Object.fromEntries(COLORS.map(c=>[c,0])),count:0};
   const previous=memory.packets[pack.packetId],now=new Set(pack.cards.map(e=>e.uid));
   if(previous)for(const entry of previous)if(!now.has(entry.uid)){const c=byId[entry.id];for(const color of c.colors)memory.demand[color]+=Math.max(0,rating(c)-2.5)/Math.max(1,c.colors.length);}
   if(pick>1){side.count++;
    for(const color of COLORS){
     const actual=sum(pack.cards.map(e=>byId[e.id]).filter(c=>!c.land&&c.colors.includes(color)).map(c=>Math.max(0,rating(c)-2.3)));
     const expected=sum(active.filter(c=>!c.land&&c.colors.includes(color)).map(c=>frequency(c)*Math.max(0,rating(c)-2.3)))*pack.cards.length/Math.max(1,Math.sqrt(pick));
     const confidence=Math.min(1,(pick-1)/Math.max(2,format.seats-1)),wheel=previous?1.25:1;
     side.values[color]=clamp(side.values[color]*.88+(actual-expected)*confidence*wheel,-5,5);
    }
   }
  }
  function context(bot,round,options={}){
   const direction=String(format.directions[round-1]),side=bot.memory?.sides[direction],sig=side?.values||{},style=STYLES[bot.strategy]||STYLES.adaptive;
   const lanes=bot.target?[bot.target]:[...new Set([...Object.keys(format.archetypes),...(bot.pool.length<total*(.28+(style.open||0))?COLORS:[])])].sort();
   const remaining=Math.max(0,total-bot.pool.length),plans=lanes.map(lane=>{
    const deck=bestBuild(bot.pool,lane,bot.strategy,{...options,remaining}),signal=sum([...lane].map(c=>sig[c]||0))/Math.max(1,lane.length);
    const confidence=side?Math.min(1,side.count/4):0;
    const signalValue=signal*(style.signals??.45)*confidence*.2;
    return {lane,deck,signalValue,value:deck.score+signalValue};
   }).sort((a,b)=>b.value-a.value||compare(a.lane,b.lane));
   return {pool:bot.pool.map(e=>byId[e.id]),sig,plans,lane:plans[0].lane,remaining,confidence:side?Math.min(1,side.count/4):0};
  }
  function phase(bot,ctx){const progress=bot.pool.length/total,style=STYLES[bot.strategy]||STYLES.adaptive;return progress>.7?3:progress>.35+(style.open||0)&&ctx.confidence>.3?2:progress>.12?1:0;}
  function rank(bot,pack,round,pick,random,transition=true,options={}){
   const direction=String(format.directions[round-1]),side=bot.memory?.sides[direction];
   const ctx=bot.strategy==='power'?{lane:bot.lane||'libero',remaining:Math.max(0,total-bot.pool.length),confidence:side?Math.min(1,side.count/4):0,plans:[]}:context(bot,round,options),style=STYLES[bot.strategy]||STYLES.adaptive,before=ctx.plans[0];
   const opening=bot.pool.length===0;
   const scores=pack.map(entry=>{
    const c=byId[entry.id];if(!profile(c)||!Number.isFinite(rating(c)))throw Error('Carta senza profilo/voto v4: '+entry.id);
    if(bot.strategy==='power')return {entry,card:c,score:rating(c),lane:ctx.lane,playable:!c.land,components:{potenza:rating(c)},reasons:['Profilo di confronto sulla sola qualità individuale.'],signature:'power|'+c.id};
    const candidatePlans=opening?ctx.plans.filter(p=>fits(c,p.lane)):ctx.plans.slice(0,style.open?3:2);
    // A genuinely new color must be allowed to challenge the current shortlist.
    if(!bot.target&&!opening){const challenger=ctx.plans.find(p=>fits(c,p.lane)&&!candidatePlans.includes(p));if(challenger)candidatePlans.push(challenger);}
    const evaluated=(candidatePlans.length?candidatePlans:ctx.plans.slice(0,1)).map(plan=>{
     const alternateMana=profile(c).mana.cycling.length||profile(c).mana.alternativeLand;
     // An excluded off-plan spell below the splash threshold, with no land
     // mode, cannot alter any configuration. Reuse that exact prior main.
     const irrelevant=!c.land&&!fits(c,plan.lane)&&rating(c)<3.5&&!alternateMana;
     let after=irrelevant?{...plan.deck,excluded:[...plan.deck.excluded,entry]}:bestBuild([...bot.pool,entry],plan.lane,bot.strategy,{...options,remaining:ctx.remaining});
     // Adding a card permits retaining every previous configuration.
     if(after.score<plan.deck.score)after=plan.deck;
     const used=[...after.spells,...after.lands].some(e=>e.uid===entry.uid),delta=after.score+plan.signalValue-before.value;
     const signal=used?sum(c.colors.map(color=>ctx.sig[color]||0))/Math.max(1,c.colors.length)*(style.signals??.45)*ctx.confidence*.08:0;
     const replaces=plan.deck.spells.filter(e=>!after.spells.some(x=>x.uid===e.uid));
     const pivot=plan.lane!==before.lane&&after.score+plan.signalValue>before.value+1e-9?{from:before.lane,to:plan.lane,out:before.deck.spells.filter(e=>!after.spells.some(x=>x.uid===e.uid)).map(e=>e.id)}:null;
     const active=plan.lane===before.lane||!!pivot;
     const own=[...bot.pool,entry].map(e=>({...byId[e.id],_entry:e}));
     const support=synergy(own.find(x=>x._entry.uid===entry.uid),own,ctx.remaining);
     const components={mazzo:delta,segnali:signal,ancora:bot.anchor&&style.anchor&&after.spells.some(e=>e.id===bot.anchor)?style.anchor:0};
     let side=0;if(!used&&after.match==='BO3'&&after.sideboard.some(e=>e.uid===entry.uid)&&before.deck.holes.spells===0)side=.12;
     components.sideboard=side;
     let denial=0;if(style.denial&&!used&&ctx.remaining<total*.35&&rating(c)>=3.5&&Object.values(before.deck.deficits).every(x=>x<2)){
      const demand=Math.max(0,...c.colors.map(color=>bot.memory?.demand[color]||0));denial=Math.min(.15,demand*.01);}
     components.negazione=denial;
     const reasons=[!active?'Conserva una carta per il piano alternativo '+plan.lane+'; il main corrente resta '+before.lane+'.':used?(replaces.length?'Migliora uno slot del main provvisorio.':'Copre un posto ancora disponibile nel mazzo.'):'Non migliora il main in questa configurazione.',
      pivot?'Cambio di piano da '+pivot.from+' a '+pivot.to+'.':'',
      after.deficits.early<plan.deck.deficits.early?'Aumenta le giocate iniziali affidabili.':'',
      after.splash?'Lo splash è confrontato con basi e consistenza dei colori principali.':'',
      after.manaOnly.some(e=>e.uid===entry.uid)?'Usata soltanto come fixing: il corpo non conta fra le minacce.':'',
      config.coverage.synergies?'Sinergie come scarto dal contesto del voto.':'Sinergie contestuali disattivate uniformemente: copertura incompleta.',
      denial?'Negazione incerta dedotta dal wheel, con beneficio limitato.':'',side?'Riserva di sideboard, senza rinunciare al completamento del main.':''].filter(Boolean);
     return {entry,card:c,score:sum(Object.values(components)),components,lane:active?plan.lane:before.lane,evaluatedLane:plan.lane,playable:active&&used,
      deck:active?after:{...before.deck,excluded:[...before.deck.excluded,entry]},replaces:active?replaces.map(e=>e.id):[],pivot,
      optionGain:Math.max(0,after.score-plan.deck.score),afterPlanValue:after.score+plan.signalValue,
      synergy:support,reasons,signature:[c.id,plan.lane,used,after.manaOnly.some(e=>e.uid===entry.uid),profile(c).roles.slice().sort().join(','),after.holes.spells>0,after.manaErrors.length>0].join('|')};
    }).sort((a,b)=>b.score-a.score||compare(a.evaluatedLane,b.evaluatedLane));
    const best=evaluated[0],remaining=Math.max(0,ctx.remaining-1),temperature=.5+2*remaining/Math.max(1,total);
    const realizedValue=Math.max(before.value,best.afterPlanValue);
    const alternatives=evaluated.filter(p=>p.evaluatedLane!==best.lane&&p.optionGain>0).map(p=>({...p,weight:Math.exp(-Math.max(0,realizedValue-p.afterPlanValue)/temperature)}));
    const option=Math.min(.35,sum(alternatives.map(p=>p.optionGain*p.weight))*.25*(1+(style.open||0))*remaining/Math.max(1,total));
    best.components.opzioni=option;best.score+=option;
    if(option>0)best.reasons.push('Mantiene aperto il piano alternativo '+alternatives.sort((a,b)=>b.optionGain*b.weight-a.optionGain*a.weight)[0].evaluatedLane+', con valore limitato alle pick restanti.');
    return best;
   }).sort((a,b)=>b.score-a.score||stable(a.entry,b.entry));
   if(style.denial&&scores.some(s=>s.playable&&s.components.mazzo>1e-6||s.components.sideboard>0||s.components.opzioni>0)){
    for(const s of scores){s.score-=s.components.negazione||0;s.components.negazione=0;}
    scores.sort((a,b)=>b.score-a.score||stable(a.entry,b.entry));
   }
   if(transition)bot.phase=phase(bot,ctx);
   return {scores,ctx};
  }
  function take(bot,pack,round,pick,random,options={}){
   observe(bot,pack,round,pick);const prior=bot.pool.map(e=>({...e})),{scores,ctx}=rank(bot,pack.cards,round,pick,random,true,options),best=scores[0];
   const close=options.deterministic?[best]:scores.filter(s=>s.signature===best.signature&&s.score>=best.score-.04);
   const selected=close[Math.floor(random()*close.length)];
   bot.lane=selected.lane;bot.pool.push(selected.entry);if(!bot.anchor&&!selected.card.land&&rating(selected.card)>=4)bot.anchor=selected.entry.id;
   bot.memory.packets[pack.packetId]=pack.cards.filter(e=>e.uid!==selected.entry.uid).map(e=>({...e}));
   bot.log.push({round,pick,packetId:pack.packetId,id:selected.entry.id,uid:selected.entry.uid,phase:['esplora','orienta','consolida','completa'][bot.phase],lane:bot.lane,
    score:selected.score,components:selected.components,observed:pack.cards.map(e=>e.id),poolBefore:prior,bestId:best.entry.id,randomized:selected!==best,
    reasons:selected.reasons,replaces:selected.replaces||[],pivot:selected.pivot||null,gaps:config.gaps,deck:selected.deck||null,
    alternatives:scores.slice(0,3).map(s=>({id:s.entry.id,score:s.score,lane:s.lane,reasons:s.reasons,replaces:s.replaces||[]}))});
   return selected.entry;
  }
  function takeGroup(bot,pack,round,pick,count,random,options={}){
   if(count<=1)return [take(bot,pack,round,pick,random,options)];
   observe(bot,pack,round,pick);
   // Bounded beam, evaluating combinations on cloned own state. No observation
   // is counted twice; only the final committed choices reach the real bot.
   const initial=rank(bot,pack.cards,round,pick,random,false,options),first=initial.scores.slice(0,4);let best=null;
   for(const candidate of first){const clone=JSON.parse(JSON.stringify({...bot,log:[]}));
    const left={packetId:pack.packetId,cards:[...pack.cards]};let value=0;const selected=[];
    for(let n=0;n<Math.min(count,pack.cards.length);n++){
     const scored=n===0?initial.scores:rank(clone,left.cards,round,pick,random,false,options).scores;
     const choice=n===0?scored.find(s=>s.entry.uid===candidate.entry.uid):scored[0];value+=choice.score;
     clone.pool.push(choice.entry);clone.lane=choice.lane;if(!clone.anchor&&!choice.card.land&&rating(choice.card)>=4)clone.anchor=choice.entry.id;selected.push(choice.entry);left.cards=left.cards.filter(e=>e.uid!==choice.entry.uid);
    }
    if(!best||value>best.value)best={selected,value};
   }
   const result=[];for(const selected of best.selected){
    // Reuse normal logging, but restrict selection to the jointly selected card.
    observe(bot,pack,round,pick);const ranked=result.length===0?initial:rank(bot,pack.cards,round,pick,random,false,options),ranking=ranked.scores,scored=ranking.find(s=>s.entry.uid===selected.uid);
    const prior=bot.pool.map(e=>({...e}));bot.phase=phase(bot,ranked.ctx);bot.pool.push(selected);bot.lane=scored.lane;if(!bot.anchor&&!scored.card.land&&rating(scored.card)>=4)bot.anchor=selected.id;
    bot.log.push({round,pick,packetId:pack.packetId,id:selected.id,uid:selected.uid,phase:['esplora','orienta','consolida','completa'][bot.phase],lane:bot.lane,components:scored.components,score:scored.score,
     poolBefore:prior,bestId:ranking[0].entry.id,randomized:false,joint:true,reasons:[...scored.reasons,'Combinazione valutata con ricerca limitata nella stessa busta.'],replaces:scored.replaces||[],pivot:scored.pivot||null,deck:scored.deck||null,gaps:config.gaps,
     observed:pack.cards.map(e=>e.id),alternatives:ranking.slice(0,3).map(s=>({id:s.entry.id,score:s.score}))});
    pack.cards=pack.cards.filter(e=>e.uid!==selected.uid);result.push(selected);
   }
   bot.memory.packets[pack.packetId]=pack.cards.map(e=>({...e}));return result;
  }
  return {byId,rating,profile,needs,fits,turn,probability,chance,sourceModel,castability,synergy,build,bestBuild,finalBuild,observe,context,rank,take,takeGroup,
   assumptions:{frequency:'Marginali della ricetta; dipendenze ed esclusioni approssimate soltanto per le attese, non per generare buste.'}};
 }
 const api={create,STYLES};if(typeof module!=='undefined')module.exports=api;else root.DraftPolicy=api;
})(globalThis);
