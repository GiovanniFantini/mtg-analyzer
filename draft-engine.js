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
  if(!STRATEGIES[strategy])throw Error('Unknown strategy');
  if(strategy==='force'&&!/^[WUBRG]{2}$/.test(target||''))throw Error('Choose an archetype');
  return {strategy,target,pool:[],phase:0,anchor:null,lane:target,signals:{},demand:Object.fromEntries(COLORS.map(c=>[c,0])),seen:{},log:[]};
 }
 function createEvaluator(format) {
  const byId=Object.fromEntries(format.cards.map(c=>[c.id,c])), archetypes=Object.keys(format.archetypes);
  const rating=c=>c.basic?0:(c.score??2.5);
  function observe(bot,pack,round,pick) {
   const sig=bot.signals[round]??=Object.fromEntries(COLORS.map(c=>[c,0]));
   // The same packet has the same minimum UID. Track its route independently.
   const key=pack.packetId, previous=bot.seen[key];
   if(previous){const now=new Set(pack.cards.map(e=>e.uid));for(const old of previous){if(!now.has(old.uid)){const c=byId[old.id];for(const color of c.colors)bot.demand[color]+=(Math.max(0,rating(c)-2)/Math.max(1,c.colors.length));}}}
   for(const color of COLORS){const strengths=pack.cards.map(e=>byId[e.id]).filter(c=>c.colors.includes(color)&&!c.land).map(rating);const strength=Math.max(0,...strengths)-2.5;sig[color]=sig[color]*.78+Math.max(0,strength)*Math.min(1,(pick-1)/5);}
  }
  function context(bot,round) {
   const pool=bot.pool.map(e=>byId[e.id]);const sig=bot.signals[round]||{};
   const support=Object.fromEntries(archetypes.map(a=>[a,pool.reduce((n,c)=>n+(!c.land&&c.colors.every(x=>a.includes(x))?Math.max(0,rating(c)-1.5):0)+(c.archetypes.includes(a)?.7:0),0)]));
   const lanes=archetypes.map(a=>[support[a]+[...a].reduce((n,c)=>n+(sig[c]||0)*STRATEGIES[bot.strategy].weights[4],0),a]).sort((a,b)=>b[0]-a[0]);
   let lane=bot.target||lanes[0][1];
   if(bot.strategy==='bomb'&&bot.anchor){const anchored=lanes.find(([,a])=>byId[bot.anchor].colors.every(c=>a.includes(c)));if(anchored){lane=lanes[0][0]>anchored[0]+6?lanes[0][1]:anchored[1];}}
   if(!bot.target&&bot.phase>=2&&bot.lane){const prior=lanes.find(([,a])=>a===bot.lane);if(prior&&lanes[0][0]<prior[0]+3)lane=bot.lane;}
   return {pool,sig,lane,support,lanes};
  }
  function rank(bot,pack,round,pick,random,transition=true) {
   const profile=STRATEGIES[bot.strategy];const ctx=context(bot,round);const n=bot.pool.length;
   if(transition){
    const masses=[...TRANSITIONS[bot.phase]];
    if(n<3){masses[0]+=2;masses[2]=0;masses[3]=0;}
    if(n>=7)masses[1]+=.5;
    if(n>=14)masses[2]+=1.5;
    if(n>=5&&ctx.lanes[0][0]-ctx.lanes[1][0]>3)masses[2]+=.8;
    if(bot.phase>=2&&bot.lane&&ctx.lane!==bot.lane)masses[1]+=.8;
    if(n>=28)masses[3]+=4;
    if(n<26)masses[3]=0;
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
   if(bot.strategy==='denial'&&n>=21&&pick>=7&&bestOwnPower<=2.7){for(const s of scores){if(!s.playable&&rating(s.card)>=3.5){const demand=Math.max(0,...s.card.colors.map(x=>bot.demand[x]));if(demand>=2){const denial=Math.min(1.5,demand*.15);s.score-=s.components.colori;s.components.colori=0;s.components.negazione=denial;s.components.costoFuoriColore=-.6;s.score+=denial-.6;}}}}
   scores.sort((a,b)=>b.score-a.score||a.entry.uid-b.entry.uid);
   return {scores,ctx};
  }
  function take(bot,pack,round,pick,random){
   observe(bot,pack,round,pick);
   const {scores,ctx}=rank(bot,pack.cards,round,pick,random);
   const max=scores[0].score;
   const selected=weighted(scores.map(s=>[Math.exp((s.score-max)/STRATEGIES[bot.strategy].temperature),s]),random);
   bot.lane=ctx.lane;bot.pool.push(selected.entry);
   if(!bot.anchor&&rating(selected.card)>=4&&!selected.card.land)bot.anchor=selected.entry.id;
   bot.seen[pack.packetId]=pack.cards.filter(e=>e.uid!==selected.entry.uid).map(e=>({...e}));
   bot.log.push({round,pick,packetId:pack.packetId,id:selected.entry.id,uid:selected.entry.uid,phase:PHASES[bot.phase],lane:bot.lane,components:selected.components,score:selected.score,alternatives:scores.slice(0,3).map(s=>({id:s.entry.id,score:s.score})),observed:pack.cards.map(e=>e.id)});
   return selected.entry;
  }
  return {byId,rating,observe,context,rank,take};
 }
 function createSession(format,seed,configs){
  if(!Array.isArray(configs)||configs.length!==format.seats-1)throw Error('Invalid bot count');
  for(const c of configs)if(!c||!STRATEGIES[c.strategy]||(c.strategy==='force'&&!format.archetypes[c.target]))throw Error('Invalid bot configuration');
  const random=rng(seed),collator=createCollator(format,random),evaluator=createEvaluator(format);
  const bots=configs.map(c=>botState(c.strategy,c.target));
  const rounds=Array.from({length:format.rounds},(_,round)=>Array.from({length:format.seats},(_,seat)=>({packetId:round*format.seats+seat,cards:collator.pack()})));
  let packets=rounds[0],round=0,pick=0;const human=[],log=[];
  const current=()=>round<format.rounds?packets[0].cards:[];
  function step(uid){
   if(round>=format.rounds)throw Error('Draft completo');
   const entry=current().find(e=>e.uid===uid);if(!entry)throw Error('Carta non presente');
   const selections=[entry,...bots.map((bot,i)=>evaluator.take(bot,packets[i+1],round+1,pick+1,random))];
   human.push(entry);log.push({round:round+1,pick:pick+1,entry});
   packets.forEach((packet,i)=>packet.cards=packet.cards.filter(e=>e.uid!==selections[i].uid));
   pick++;
   if(packets.every(p=>!p.cards.length)){round++;pick=0;packets=rounds[round]||[];}
   else{const rotated=Array(format.seats);packets.forEach((p,i)=>rotated[(i+format.directions[round]+format.seats)%format.seats]=p);packets=rotated;}
   return entry;
  }
  return {format,seed,configs,bots,human,log,current,step,get round(){return round+1;},get pick(){return pick+1;},get complete(){return round>=format.rounds;},export(){return {version:1,format:format.id,seed,configs,picks:log.map(x=>x.entry.uid)};}};
 }
 function replay(format,record){
  if(record?.version!==1||record.format!==format.id||typeof record.seed!=='string'||record.seed.length>200||!Array.isArray(record.picks)||record.picks.length>format.rounds*format.packSize||record.picks.some(x=>!Number.isInteger(x)))throw Error('Salvataggio non valido');
  const session=createSession(format,record.seed,record.configs);record.picks.forEach(uid=>session.step(uid));return session;
 }
 const api={STRATEGIES,PHASES,TRANSITIONS,rng,weighted,createCollator,botState,createEvaluator,createSession,replay};
 if(typeof module!=='undefined')module.exports=api;else root.DraftEngine=api;
})(globalThis);
