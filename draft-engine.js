'use strict';
/* Pure engine: no DOM, storage, network or knowledge of other seats' pools. */
((root) => {
 const COLORS = [...'WUBRG'];
 const STRATEGIES = {
  power: {name:'Potenza pura', description:'Sceglie per valutazione individuale, anche fuori colore. Profilo di confronto che può produrre un pool incoerente.', weights:[1,0,0,0,0,0], temperature:.10},
  bomb: {name:'Bomba e costruzione attorno', description:'Ricorda la prima bomba e privilegia i suoi colori; cambia piano solo se i segnali compensano il costo.', weights:[1.1,1.4,.8,.5,.6,.3], temperature:.16},
  signals: {name:'Lettura dei segnali', description:'Resta aperto, segue qualità e colori ricevuti, poi consolida il mazzo.', weights:[1,1,.7,.7,1.6,.6], temperature:.22},
  force: {name:'Archetipo forzato', description:'Privilegia la coppia di colori scelta prima del draft, anche se contesa.', weights:[.9,2.1,1.3,.7,0,.4], temperature:.12},
  synergy: {name:'Sinergie e build-around', description:'Cerca supporti degli archetipi già presenti, senza sommare bonus a carte isolate.', weights:[.9,1.1,1.8,.6,.8,.4], temperature:.18},
  aggro: {name:'Aggro e tempo', description:'Preferisce creature economiche e interazione; corregge gli eccessi della curva.', weights:[1,1.2,.5,1.5,.7,.2], temperature:.18},
  control: {name:'Controllo e vantaggio', description:'Preferisce risposte e vantaggio carte, conservando un numero utile di creature iniziali.', weights:[1.1,1.2,.6,.9,.8,.4], temperature:.18},
  fixing: {name:'Fixing e splash', description:'Prende fonti per colori aggiuntivi e accetta una bomba extra solo quando il mana la sostiene.', weights:[1.1,.8,.6,.6,.9,1.8], temperature:.2},
  denial: {name:'Counterpick ragionato', description:'Deduce colori richiesti dalle carte scomparse al giro. Rinuncia a una giocabile solo tardi e se il costo è basso.', weights:[1,1.3,.6,.8,.8,.5], temperature:.15}
 };
 const PHASES = ['esplora','orienta','consolida','completa'];
 // Rows are base transition masses, adjusted by progress and observed evidence.
 const TRANSITIONS = [[.68,.30,.02,0],[.08,.67,.25,0],[.02,.08,.84,.06],[0,0,.03,.97]];
 function rng(seed) {
  let h=2166136261; for(const ch of String(seed)) h=Math.imul(h^ch.charCodeAt(0),16777619);
  return () => {h+=0x6D2B79F5;let t=h;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return ((t^t>>>14)>>>0)/4294967296;};
 }
 function weighted(groups, random) {
  if(!groups.length || groups.some(([w])=>!Number.isFinite(w)||w<0)) throw Error('Invalid distribution');
  const total=groups.reduce((n,[w])=>n+w,0); if(total<=0) throw Error('Empty distribution');
  let value=random()*total; for(const [w,item] of groups){value-=w;if(value<0)return item;} return groups.at(-1)[1];
 }
 const choose=(a,r)=>{if(!a.length)throw Error('Empty card group');return a[Math.floor(r()*a.length)];};
 function createCollator(format, random) {
  if(format.collation?.schemaVersion)return (typeof module!=='undefined'?require('./collation.js'):root.Collation).createCollator(format,random);
  const byId=Object.fromEntries(format.cards.map(c=>[c.id,c])), spec=format.collation;
  if(!spec)throw Error('Profilo di collazione non disponibile');
  const resolve=ids=>ids.map(id=>{if(!byId[id])throw Error('Unknown card '+id);return byId[id];});
  const common=resolve(spec.common),guests=resolve(spec.guests);
  const branches=Object.fromEntries(Object.entries(spec.slots).map(([slot,groups])=>[slot,groups.map(g=>[g.weight,{cards:resolve(g.cards),foil:g.foil}])]));
  for(const [name,groups] of Object.entries(branches)) {
   if(Math.abs(groups.reduce((n,[w])=>n+w,0)-1)>1e-9 || groups.some(([w,g])=>w<0||!g.cards.length)) throw Error('Invalid slot '+name);
  }
  const partners={},printedPartners={};
  for(const [a,b] of spec.pairs){if(!byId[a]||!byId[b]||byId[a].rarity!==byId[b].rarity)throw Error('Invalid pair');printedPartners[a]=b;printedPartners[b]=a;partners[byId[a].full]=byId[b].full;partners[byId[b].full]=byId[a].full;}
  const draw=(slot,exclude=[])=>{const group=weighted(branches[slot],random);return {card:choose(group.cards.filter(c=>!exclude.includes(c.full)),random),foil:group.foil};};
  let sequence=0;
  function pack(){
   const result=[];const add=(c,slot,foil=false)=>result.push({uid:sequence++,id:c.id,slot,foil});
   const available=[...common];for(let i=0;i<spec.commonCount;i++)add(available.splice(Math.floor(random()*available.length),1)[0],'common');
   if(random()<spec.guestRate){result.shift();add(choose(guests,random),'guest');}
   let pair=[];
   for(const rule of spec.recipe){
    const {card,foil}=draw(rule.slot,rule.excludePair?pair.map(c=>c.full):[]);
    if(rule.paired){const partner=byId[printedPartners[card.id]];if(!partner)throw Error('Missing partner '+card.id);pair=[card,partner];pair.forEach(c=>add(c,'pair',rule.foil||foil));}
    else add(card,rule.slot,rule.foil||foil);
   }
   if(result.length!==format.packSize)throw Error('Invalid pack size');return result;
  }
  return {pack,branches,partners};
 }
 function botState(strategy='signals',target=null) {
  if(!STRATEGIES[strategy]&&strategy!=='adaptive')throw Error('Unknown strategy');
  if(strategy==='force'&&(!/^[WUBRG]{1,5}$/.test(target||'')||new Set(target).size!==target.length))throw Error('Choose an archetype');
  return {strategy,target,pool:[],phase:0,anchor:null,lane:target,signals:{},demand:Object.fromEntries(COLORS.map(c=>[c,0])),seen:{},log:[]};
 }
 function createEvaluator(format,engineVersion=3) {
  if(engineVersion===4)return (typeof module!=='undefined'?require('./draft-policy.js'):root.DraftPolicy).create(format);
  if(![2,3].includes(engineVersion))throw Error('Versione del motore non supportata');
  const modern=engineVersion===3;
  const byId=Object.fromEntries(format.cards.map(c=>[c.id,c])), archetypes=Object.keys(format.archetypes);
  if(!archetypes.length)throw Error('Archetipi non disponibili');
  const at=n=>format.rounds*format.packSize*n/42;
  const rating=c=>c.basic?0:(c.score??2.5);
  // Mana symbols, rather than color identity, determine whether a hybrid spell
  // needs a splash. This remains a draft heuristic, not a mana-payment engine.
  function missingColors(c,lane){
   const symbols=[...(c.cost||'').matchAll(/\{([^}]+)\}/g)].map(m=>m[1]);
   const colored=symbols.filter(s=>/[WUBRG]/.test(s));
   if(!colored.length)return c.colors.filter(x=>!lane.includes(x));
   return [...new Set(colored.flatMap(s=>{
    const choices=s.split('/').filter(x=>COLORS.includes(x));
    return choices.some(x=>lane.includes(x))||s.split('/').some(x=>/^\d+$/.test(x))?[]:choices;
   }))];
  }
  const fits=(c,lane)=>modern?missingColors(c,lane).length===0:c.colors.every(x=>lane.includes(x));
  function manaColors(c){
   const text=c.oracle||'';
   if(/mana of any color|basic landcycling|search your library for a basic land/i.test(text))return COLORS;
   if(c.land)return c.identity;
   const cycling=['Plains','Island','Swamp','Mountain','Forest'].flatMap((type,i)=>new RegExp('\\b'+type+'cycling\\b','i').test(text)?[COLORS[i]]:[]);
   const produced=[...text.matchAll(/\badd ([^.\n]+)/gi)].flatMap(m=>[...m[1].matchAll(/\{([WUBRG])\}/g)].map(x=>x[1]));
   return [...new Set([...cycling,...produced])];
  }
  function observe(bot,pack,round,pick) {
   const sig=bot.signals[round]??=Object.fromEntries(COLORS.map(c=>[c,0]));
   // The same packet has the same minimum UID. Track its route independently.
   const key=pack.packetId, previous=bot.seen[key];
   if(previous){const now=new Set(pack.cards.map(e=>e.uid));for(const old of previous){if(!now.has(old.uid)){const c=byId[old.id];for(const color of c.colors)bot.demand[color]+=(Math.max(0,rating(c)-2)/Math.max(1,c.colors.length));}}}
   for(const color of COLORS){const strengths=pack.cards.map(e=>byId[e.id]).filter(c=>c.colors.includes(color)&&!c.land).map(rating);const strength=Math.max(0,...strengths)-2.5;sig[color]=sig[color]*.78+Math.max(0,strength)*Math.min(1,(pick-1)/5);}
  }
  function context(bot,round) {
   const pool=bot.pool.map(e=>byId[e.id]);const sig=bot.signals[round]||{};
   const support=Object.fromEntries(archetypes.map(a=>[a,pool.reduce((n,c)=>n+(!c.land&&fits(c,a)?Math.max(0,rating(c)-1.5):0)+(c.archetypes.includes(a)&&(!modern||fits(c,a))?.7:0),0)]));
   const lanes=archetypes.map(a=>[support[a]+[...a].reduce((n,c)=>n+(sig[c]||0)*STRATEGIES[bot.strategy].weights[4],0),a]).sort((a,b)=>b[0]-a[0]);
   let lane=bot.target||lanes[0][1];
   if(bot.strategy==='bomb'&&bot.anchor){const anchored=lanes.find(([,a])=>fits(byId[bot.anchor],a));if(anchored){lane=lanes[0][0]>anchored[0]+6?lanes[0][1]:anchored[1];}}
   if(!bot.target&&bot.phase>=2&&bot.lane){const prior=lanes.find(([,a])=>a===bot.lane);if(prior&&lanes[0][0]<prior[0]+3)lane=bot.lane;}
   // Equally supported pairs stay open. Their order in the JSON must not give
   // one color a curve or synergy bonus before the bot has any evidence.
   if(!modern)return {pool,sig,lane,support,lanes};
   const supportedColors=new Set(pool.filter(c=>!c.land&&fits(c,lane)).flatMap(c=>[...(c.cost||'').matchAll(/\{([WUBRG])\}/g)].map(m=>m[1])));
   const keepLane=bot.target||(bot.phase>=2&&supportedColors.size>=2);
   const laneValue=lanes.find(([,a])=>a===lane)[0];
   const anchored=bot.strategy==='bomb'&&bot.anchor&&fits(byId[bot.anchor],lane);
   const options=keepLane?[lane]:lanes.filter(([value,a])=>value>=laneValue-.25&&(!anchored||fits(byId[bot.anchor],a))).map(([,a])=>a);
   return {pool,sig,lane,support,lanes,options};
  }
  function rankModern(bot,pack,round,pick,random,transition){
   const profile=STRATEGIES[bot.strategy],ctx=context(bot,round),n=bot.pool.length;
   if(transition){
    const masses=[...TRANSITIONS[bot.phase]];
    if(n<at(3)){masses[0]+=2;masses[2]=0;masses[3]=0;}
    if(n>=at(7))masses[1]+=.5;
    if(n>=at(14))masses[2]+=1.5;
    if(n>=at(5)&&ctx.lanes[0][0]-(ctx.lanes[1]?.[0]??0)>3)masses[2]+=.8;
    if(bot.phase>=2&&bot.lane&&ctx.lane!==bot.lane)masses[1]+=.8;
    if(n>=at(28))masses[3]+=4;
    if(n<at(26))masses[3]=0;
    bot.phase=weighted(masses.map((w,i)=>[w,i]),random);
   }
   const commitment=bot.strategy==='force'?1.5:n===0?0:[.08,.65,1.3,1.65][bot.phase];
   const removal=c=>/rimozione|risposta|contromagia/i.test(c.role);
   const sources=manaColors;
   const playable=(c,lane)=>!c.land&&fits(c,lane);
   function evaluate(entry,lane){
    const c=byId[entry.id],off=missingColors(c,lane),own=ctx.pool.filter(x=>playable(x,lane));
    const available=color=>ctx.pool.filter(x=>sources(x).includes(color)).length;
    const splash=bot.strategy==='fixing'&&off.length===1&&available(off[0])>=2&&
     [...(c.cost||'').matchAll(/\{([^}]+)\}/g)].filter(m=>m[1].split('/').includes(off[0])).length<=1;
    const on=c.land?sources(c).some(x=>lane.includes(x)):off.length===0;
    const fit=c.basic?-2:(on?1:splash?-.2:-1-off.length)*commitment;
    // Archetype membership is evidence of a shared plan, not proof that every
    // copy is another enabler. Duplicate copies cannot inflate this bonus.
    const distinctSupport=new Set(own.filter(x=>x.full!==c.full&&x.archetypes.includes(lane)).map(x=>x.full)).size;
    const synergy=playable(c,lane)&&c.archetypes.includes(lane)?Math.min(.35,distinctSupport*.07):0;
    let curve=0;
    const cheap=x=>x.creature&&x.mv<=2&&!/\{X\}/.test(x.cost||'');
    if(n&&playable(c,lane)){
     const cheapCount=own.filter(cheap).length;
     if(cheap(c))curve+=cheapCount<6?.25:-.15;
     if(c.creature&&own.filter(x=>x.creature&&Math.min(6,x.mv)===Math.min(6,c.mv)).length>=5)curve-=.2;
     // An expensive activated answer is not an efficient removal spell merely
     // because the editorial role contains the word "rimozione".
     if(!c.creature&&removal(c)&&own.filter(x=>!x.creature&&removal(x)).length<5)curve+=.15;
     if(bot.strategy==='aggro')curve+=c.creature&&c.mv<=3&&!/\{X\}/.test(c.cost||'')?.15:c.mv>=5?-.15:0;
     if(bot.strategy==='control')curve+=!c.creature&&removal(c)?.15:/pesca|vantaggio|difens/i.test(c.role)?.1:0;
    }
    const signal=c.colors.reduce((s,x)=>s+(ctx.sig[x]||0),0)/Math.max(1,c.colors.length)*.12;
    const offBombs=ctx.pool.filter(x=>rating(x)>=4&&!fits(x,lane));
    const useful=sources(c).some(color=>lane.includes(color)||offBombs.some(b=>missingColors(b,lane).includes(color)));
    const mana=useful&&!c.basic?.15:0;
    const components={potenza:rating(c)*profile.weights[0],colori:fit*profile.weights[1],sinergia:synergy*profile.weights[2],curva:curve*profile.weights[3],segnali:signal*profile.weights[4],mana:mana*profile.weights[5]};
    // Tactical preferences break close choices. Their combined bonus cannot
    // erase a full point of card quality on the same weighted rating scale.
    const keys=['sinergia','curva','segnali','mana'];
    const positive=keys.reduce((s,k)=>s+Math.max(0,components[k]),0),negative=keys.reduce((s,k)=>s+Math.min(0,components[k]),0);
    for(const key of keys)components[key]*=components[key]>=0?(positive>.45?.45/positive:1):(negative<-.2?-.2/negative:1);
    return {entry,components,score:Object.values(components).reduce((a,b)=>a+b,0),playable:playable(c,lane),card:c,lane};
   }
   const scores=pack.map(entry=>ctx.options.map(lane=>evaluate(entry,lane)).sort((a,b)=>b.score-a.score)[0]);
   const bestOwnPower=Math.max(0,...scores.filter(s=>s.playable).map(s=>rating(s.card)));
   if(bot.strategy==='denial'&&n>=at(21)&&pick>=Math.ceil(format.packSize/format.picksPerTurn)/2&&bestOwnPower<=2.7){
    for(const s of scores)if(!s.playable&&rating(s.card)>=3.5){const demand=Math.max(0,...s.card.colors.map(x=>bot.demand[x]));if(demand>=2){s.components.colori=0;s.components.negazione=Math.min(1.5,demand*.15);s.components.costoFuoriColore=-.6;s.score=Object.values(s.components).reduce((a,b)=>a+b,0);}}
   }
   scores.sort((a,b)=>b.score-a.score||a.entry.uid-b.entry.uid);
   return {scores,ctx};
  }
  function rank(bot,pack,round,pick,random,transition=true) {
   if(modern)return rankModern(bot,pack,round,pick,random,transition);
   const profile=STRATEGIES[bot.strategy];const ctx=context(bot,round);const n=bot.pool.length;
   if(transition){
    const masses=[...TRANSITIONS[bot.phase]];
    if(n<at(3)){masses[0]+=2;masses[2]=0;masses[3]=0;}
    if(n>=at(7))masses[1]+=.5;
    if(n>=at(14))masses[2]+=1.5;
    if(n>=at(5)&&ctx.lanes[0][0]-(ctx.lanes[1]?.[0]??0)>3)masses[2]+=.8;
    if(bot.phase>=2&&bot.lane&&ctx.lane!==bot.lane)masses[1]+=.8;
    if(n>=at(28))masses[3]+=4;
    if(n<at(26))masses[3]=0;
    bot.phase=weighted(masses.map((w,i)=>[w,i]),random);
   }
   const commitment=bot.strategy==='force'?1.5:n===0?0:[.08,.65,1.3,1.65][bot.phase];
   const colors=ctx.lane;const playable=c=>!c.land&&c.colors.every(x=>colors.includes(x));
   const own=ctx.pool.filter(playable), cheap=own.filter(c=>c.creature&&c.mv<=2).length;
   const removal=c=>/rimozione|risposta|contromagia/i.test(c.role);
   const fixing=c=>c.land&&!c.basic||/landcycling|mana of any color|search your library for a basic land/i.test(c.oracle);
   const supportCount=ctx.pool.filter(c=>c.archetypes.includes(colors)).length;
   const scores=pack.map(entry=>{
    const c=byId[entry.id], off=c.colors.filter(x=>!colors.includes(x));
    const sources=c.land?(/mana of any color/i.test(c.oracle)?COLORS:c.identity):[];
    const on=c.land?(sources.some(x=>colors.includes(x))?1:0):c.colors.length?1-off.length/c.colors.length:1;
    const manaSources=color=>ctx.pool.filter(c=>(c.land&&c.identity.includes(color))||/mana of any color/i.test(c.oracle)).length;
    const splashAllowed=bot.strategy==='fixing'&&off.length===1&&manaSources(off[0])>=2&&(c.cost.match(new RegExp('\\{'+off[0]+'\\}','g'))||[]).length<=1;
    const power=rating(c), fit=c.basic?-2:((on-.5)*2-off.length*(splashAllowed?.2:1))*commitment;
    const synergy=c.archetypes.includes(colors)?Math.min(1.8,supportCount*.18):0;
    let curve=0;
    if(playable(c)){
     if(c.creature&&c.mv<=2)curve+=(cheap<6?.8:-.3);
     if(c.creature&&ctx.pool.filter(x=>playable(x)&&x.creature&&Math.min(6,x.mv)===Math.min(6,c.mv)).length>=5)curve-=.8;
     if(removal(c)&&own.filter(removal).length<5)curve+=.5;
     if(bot.strategy==='aggro')curve+=c.creature&&c.mv<=3?1:c.mv>=5?-1:0;
     if(bot.strategy==='control')curve+=removal(c)?1:/pesca|vantaggio|difens/i.test(c.role)?.7:0;
    }
    const signal=c.colors.reduce((s,x)=>s+(ctx.sig[x]||0),0)/Math.max(1,c.colors.length)*.4;
    const offBombs=ctx.pool.filter(x=>rating(x)>=4&&x.colors.some(y=>!colors.includes(y)));
    const usefulFixing=fixing(c)&&(!c.land||sources.some(x=>colors.includes(x)||offBombs.some(b=>b.colors.includes(x))));
    const mana=usefulFixing?Math.min(1.2,.3+offBombs.filter(b=>!c.land||sources.some(x=>b.colors.includes(x))).length*.3):0;
    const components={potenza:power*profile.weights[0],colori:fit*profile.weights[1],sinergia:synergy*profile.weights[2],curva:curve*profile.weights[3],segnali:signal*profile.weights[4],mana:mana*profile.weights[5]};
    return {entry,components,score:Object.values(components).reduce((a,b)=>a+b,0),playable:playable(c),card:c};
   });
   const bestOwnPower=Math.max(0,...scores.filter(s=>s.playable).map(s=>rating(s.card)));
   if(bot.strategy==='denial'&&n>=at(21)&&pick>=Math.ceil(format.packSize/format.picksPerTurn)/2&&bestOwnPower<=2.7){for(const s of scores){if(!s.playable&&rating(s.card)>=3.5){const demand=Math.max(0,...s.card.colors.map(x=>bot.demand[x]));if(demand>=2){const denial=Math.min(1.5,demand*.15);s.score-=s.components.colori;s.components.colori=0;s.components.negazione=denial;s.components.costoFuoriColore=-.6;s.score+=denial-.6;}}}}
   scores.sort((a,b)=>b.score-a.score||a.entry.uid-b.entry.uid);
   return {scores,ctx};
  }
  function take(bot,pack,round,pick,random){
   observe(bot,pack,round,pick);
   const {scores,ctx}=rank(bot,pack.cards,round,pick,random);
   const max=scores[0].score;
   const candidates=modern?scores.filter(s=>s.score>=max-.2):scores;
   const selected=weighted(candidates.map(s=>[Math.exp((s.score-max)/STRATEGIES[bot.strategy].temperature),s]),random);
   bot.lane=modern?selected.lane:ctx.lane;bot.pool.push(selected.entry);
   if(!bot.anchor&&rating(selected.card)>=4&&!selected.card.land)bot.anchor=selected.entry.id;
   bot.seen[pack.packetId]=pack.cards.filter(e=>e.uid!==selected.entry.uid).map(e=>({...e}));
   bot.log.push({round,pick,packetId:pack.packetId,id:selected.entry.id,uid:selected.entry.uid,phase:PHASES[bot.phase],lane:bot.lane,components:selected.components,score:selected.score,alternatives:scores.slice(0,3).map(s=>({id:s.entry.id,score:s.score})),observed:pack.cards.map(e=>e.id)});
   return selected.entry;
  }
  return {byId,rating,observe,context,rank,take};
 }
 function createSession(format,seed,configs,engineVersion=3,options={}){
  if(![2,3,4].includes(engineVersion))throw Error('Versione del motore non supportata');
  if(typeof seed!=='string'||seed.length>200)throw Error('Seme non valido');
  const policyOptions=engineVersion===4?{match:options.match??format.botPolicy?.match??'BO3',deterministic:options.deterministic??false}:{};
  if(engineVersion===4&&(!['BO1','BO3','unknown'].includes(policyOptions.match)||typeof policyOptions.deterministic!=='boolean'))throw Error('Opzioni della politica non valide');
  if(!Number.isInteger(format.picksPerTurn)||format.picksPerTurn<1||!Number.isInteger(format.seats)||format.seats<2||format.directions.length!==format.rounds||format.directions.some(x=>x!==1&&x!==-1))throw Error('Regole del Draft non valide');
  if(!Array.isArray(configs)||configs.length!==format.seats-1)throw Error('Invalid bot count');
  for(const c of configs)if(!c||(!STRATEGIES[c.strategy]&&!(engineVersion===4&&c.strategy==='adaptive'))||(c.strategy==='force'&&!format.archetypes[c.target]))throw Error('Invalid bot configuration');
  const random=rng(seed),collator=createCollator(format,random),evaluator=createEvaluator(format,engineVersion);
  const bots=configs.map(c=>botState(c.strategy,c.target));
  const rounds=Array.from({length:format.rounds},(_,round)=>Array.from({length:format.seats},(_,seat)=>({packetId:round*format.seats+seat,cards:collator.pack()})));
  let packets=rounds[0],round=0,pick=0,pending=[],asyncBusy=false,applyingAsync=false;const human=[],log=[];
  const current=()=>round<format.rounds?packets[0].cards:[];
  function step(uid){
   if(asyncBusy&&!applyingAsync)throw Error('Calcolo dei bot già in corso');
   if(round>=format.rounds)throw Error('Draft completo');
   const entry=current().find(e=>e.uid===uid);if(!entry)throw Error('Carta non presente');
   human.push(entry);log.push({round:round+1,pick:pick+1,entry});
   pending.push(entry);packets[0].cards=packets[0].cards.filter(e=>e.uid!==uid);
   if(pending.length<format.picksPerTurn&&packets[0].cards.length)return entry;
   for(let i=0;i<bots.length;i++){
    const packet=packets[i+1];
    if(engineVersion===4){
     const choices=evaluator.takeGroup(bots[i],packet,round+1,pick+1,pending.length,
      rng(seed+'\0v4|'+(i+1)+'|'+round+'|'+pick+'|group'),policyOptions);
     const chosen=new Set(choices.map(e=>e.uid));packet.cards=packet.cards.filter(e=>!chosen.has(e.uid));continue;
    }
    for(let n=0;n<pending.length;n++){
     const selected=evaluator.take(bots[i],packet,round+1,pick+1,random);
     packet.cards=packet.cards.filter(e=>e.uid!==selected.uid);
    }
   }
   pending=[];
   pick++;
   if(packets.every(p=>!p.cards.length)){round++;pick=0;packets=rounds[round]||[];}
   else{const rotated=Array(format.seats);packets.forEach((p,i)=>rotated[(i+format.directions[round]+format.seats)%format.seats]=p);packets=rotated;}
   return entry;
  }
  async function stepAsync(uid,chooseBot){
   if(engineVersion!==4||typeof chooseBot!=='function')throw Error('Calcolo asincrono non disponibile');
   if(asyncBusy)throw Error('Calcolo dei bot già in corso');
   if(round>=format.rounds||!current().some(e=>e.uid===uid))throw Error('Carta non presente o draft completo');
   asyncBusy=true;const count=pending.length+1;
   try{
    if(count<format.picksPerTurn&&current().length>1){applyingAsync=true;return step(uid);}
    const results=await Promise.all(bots.map((bot,i)=>chooseBot({bot:structuredClone(bot),packet:structuredClone(packets[i+1]),round:round+1,pick:pick+1,count,
     randomSeed:seed+'\0v4|'+(i+1)+'|'+round+'|'+pick+'|group',options:policyOptions})));
    for(const [i,result] of results.entries()){
     const expected=Math.min(count,packets[i+1].cards.length),owned=bots[i].pool;
     if(!Array.isArray(result?.choices)||result.choices.length!==expected||new Set(result.choices).size!==expected||result.choices.some(uid=>!packets[i+1].cards.some(e=>e.uid===uid))||!Array.isArray(result.bot?.pool)||result.bot.pool.length!==owned.length+expected||owned.some((e,n)=>result.bot.pool[n]?.uid!==e.uid||result.bot.pool[n]?.id!==e.id)||result.choices.some((uid,n)=>result.bot.pool[owned.length+n]?.uid!==uid||result.bot.pool[owned.length+n]?.id!==packets[i+1].cards.find(e=>e.uid===uid).id)||result.bot.strategy!==bots[i].strategy||result.bot.target!==bots[i].target||result.bot.log?.length!==bots[i].log.length+expected)throw Error('Risultato del bot non coerente');
    }
    const original=evaluator.takeGroup;evaluator.takeGroup=(bot,packet)=>{const result=results[bots.indexOf(bot)];Object.assign(bot,result.bot);return result.choices.map(uid=>packet.cards.find(e=>e.uid===uid));};
    applyingAsync=true;try{return step(uid);}finally{evaluator.takeGroup=original;}
   }finally{applyingAsync=false;asyncBusy=false;}
  }
  return {format,seed,configs,bots,human,log,current,step,stepAsync,engineVersion,policyOptions,get packetId(){return packets[0]?.packetId;},get round(){return round+1;},get pick(){return pick+1;},get complete(){return round>=format.rounds;},export(){return {version:engineVersion===4?3:2,engineVersion,format:format.id,revision:format.revision,seed,configs,picks:log.map(x=>x.entry.uid),
   ...(engineVersion===4?{policyRevision:format.botPolicy.revision,algorithmRevision:format.botPolicy.algorithmRevision,randomSchema:'seat-pick-v1',options:policyOptions}:{})};}};
 }
 function createReplaySession(format,record){
  if(record?.version===3){
   if(record.engineVersion!==4||record.policyRevision!==format.botPolicy?.revision||typeof record.algorithmRevision!=='string'||record.algorithmRevision!==format.botPolicy?.algorithmRevision||record.randomSchema!=='seat-pick-v1'||record.revision!==format.revision||record.format!==format.id||typeof record.seed!=='string'||record.seed.length>200||!record.options||!['BO1','BO3','unknown'].includes(record.options.match)||typeof record.options.deterministic!=='boolean'||!Array.isArray(record.picks)||record.picks.length>format.rounds*format.packSize||record.picks.some(x=>!Number.isInteger(x)))throw Error('Salvataggio v4 incompatibile con i dati funzionali');
   return createSession(format,record.seed,record.configs,4,record.options);
  }
  if(!record||(record.version===1?!format.legacyReplay:record.version!==2||![2,3].includes(record.engineVersion)||(record.revision!==format.revision&&!(format.compatibleRevisions||[]).includes(record.revision)))||record.format!==format.id||typeof record.seed!=='string'||record.seed.length>200||!Array.isArray(record.picks)||record.picks.length>format.rounds*format.packSize||record.picks.some(x=>!Number.isInteger(x)))throw Error('Salvataggio non valido o riferito a un profilo differente');
  return createSession(format,record.seed,record.configs,record.version===1?2:record.engineVersion);
 }
 function replay(format,record){const session=createReplaySession(format,record);record.picks.forEach(uid=>session.step(uid));return session;}
 const api={STRATEGIES,PHASES,TRANSITIONS,rng,weighted,createCollator,botState,createEvaluator,createSession,createReplaySession,replay};
 if(typeof module!=='undefined')module.exports=api;else root.DraftEngine=api;
})(globalThis);
