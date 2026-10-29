'use strict';
const assert=require('node:assert/strict'),E=require('./draft-engine.js'),{fixture,make}=require('./tests/draft-policy-fixture.cjs');
const f=fixture(),entry=(id,uid)=>({id,uid}),many=(id,n,start=0)=>Array.from({length:n},(_,i)=>entry(id,start+i));
function add(id,card,profile){f.cards.push(make(id,card));f.botPolicy.profiles[id]={...structuredClone(f.botPolicy.profiles.early),...profile};f.collation.groups.all.push(id);}
add('double-red-cycler',{colors:['R'],cost:'{R}{R}',mv:2,score:4},
 {symbols:['R','R'],mana:{...structuredClone(f.botPolicy.profiles.cycler.mana)}});
add('red-seven',{colors:['R'],cost:'{6}{R}',mv:7,score:4.8},{symbols:['6','R']});
add('gold',{colors:['W','R'],cost:'{2}{W}{W}{R}',mv:5,score:4.8},{symbols:['2','W','W','R']});
add('colorless-land',{colors:[],cost:'',mv:0,land:true,creature:false,type:'Land',score:3},
 {symbols:[],roles:['land'],mana:{abilities:[{colors:['C'],activation:'{T}',restricted:false}],cycling:[],subtypes:[],tapped:false}});
add('fetch',{colors:[],cost:'',mv:0,land:true,creature:false,type:'Land',score:3},
 {symbols:[],roles:['land','fixing'],mana:{abilities:[],cycling:[],subtypes:[],tapped:false,fetch:{kind:'basic',tapped:true,restricted:false}}});
add('red-self',{colors:['R'],cost:'{3}{R}',mv:4,score:4.8},
 {symbols:['3','R'],mana:{...structuredClone(f.botPolicy.profiles.cycler.mana)}});
add('a-plains-cycler',{colors:['B'],cost:'{5}{B}',mv:6,score:2},{symbols:['5','B'],mana:{...structuredClone(f.botPolicy.profiles.cycler.mana),cycling:[{kind:'subtype',type:'Plains',cost:'{2}'}]}});
add('z-mountain-cycler',{colors:['U'],cost:'{5}{U}',mv:6,score:2},{symbols:['5','U'],mana:structuredClone(f.botPolicy.profiles.cycler.mana)});
for(const color of ['B','G'])add('double-'+color,{colors:[color],cost:'{3}{'+color+'}{'+color+'}',mv:5,score:4.8},{symbols:['3',color,color]});
add('a-restricted-modal',{colors:['B'],cost:'{5}{B}',mv:6,score:2},{symbols:['5','B'],mana:{abilities:[],cycling:[],subtypes:[],alternativeLand:{colors:['R'],tapped:false,restricted:true}}});
for(const [id,color,type] of [['owned-plains','W','Plains'],['owned-island','U','Island']])add(id,{colors:[],cost:'',mv:0,land:true,basic:true,creature:false,type:'Basic Land - '+type,score:null},{symbols:[],roles:['land'],mana:{abilities:[{colors:[color],activation:'{T}',restricted:false}],cycling:[],subtypes:[type],tapped:false}});
add('tapped-wb',{colors:[],cost:'',mv:0,land:true,creature:false,type:'Land',score:3},{symbols:[],roles:['land'],mana:{abilities:[{colors:['W','B'],activation:'{T}',restricted:false}],cycling:[],subtypes:[],tapped:true}});
const ev=E.createEvaluator(f,4);
// CODE-01: rejected spell slots are refilled, and discarded cyclers cannot
// continue to supply red to the remaining finisher.
const p=[...many('early',25),...many('double-red-cycler',2,100),entry('red-seven',200)];
const noRedBasics=structuredClone(f);noRedBasics.botPolicy.allowedBasics=['W','U'];
const filled=E.createEvaluator(noRedBasics,4).build(p,'WU','adaptive',{remaining:0,splash:'R',splashBasics:2});
assert.equal(filled.spells.length,23);assert.ok(!filled.spells.some(e=>['double-red-cycler','red-seven'].includes(e.id)));
assert.equal(filled.sources.R,0);assert.equal(filled.slots,40);
// CODE-02: a double pip in the primary color does not ban a single-pip splash.
const gold=ev.build([...many('early',25),entry('gold',100)],'WU','adaptive',{remaining:0,splash:'R',splashBasics:5});
assert.ok(gold.spells.some(e=>e.id==='gold'));
// CODE-03: a reduction never delays the nominal turn of a cheap spell.
const cheap={...ev.byId.early,id:'cheap',mv:2,type:'Artifact Creature'};
f.botPolicy.profiles.cheap={...structuredClone(f.botPolicy.profiles.early),curve:{...f.botPolicy.profiles.early.curve,reduction:true,reductionResource:'artifacts'}};
assert.equal(ev.turn(cheap,[cheap]),2);
// CODE-04: irrelevant C-only lands do not replace freely addable colored bases.
const colored=ev.build([...many('early',24),...many('colorless-land',2,100)],'WU','adaptive',{remaining:0});
assert.equal(colored.lands.length,0);assert.equal(colored.sources.C,0);
// CODE-05: a basic fetch resolves only colors present in the candidate main.
const fetched=ev.build([...many('early',12),...many('blue',12,20),entry('fetch',99)],'WU','adaptive',{remaining:0});
assert.ok(fetched.lands.some(e=>e.id==='fetch'));assert.ok(fetched.sources.W>fetched.basics.W&&fetched.sources.U>fetched.basics.U);assert.equal(fetched.sources.R,0);
// CODE-06: an individual card cannot be its own alternative mana source.
const c={...ev.byId['red-self'],_entry:entry('red-self',77)};
const model=ev.sourceModel([c],[],{W:15,R:2});
assert.ok(model.sources.R>2);assert.equal(ev.castability(c,['W','U','R'],model,4),ev.chance(2,4,1));
// Off-color cycling can explicitly be a fixing-only slot, never a creature.
const mode=ev.build([...many('early',24),entry('red-seven',88),entry('cycler',99)],'W','adaptive',{remaining:0,splash:'R',splashBasics:2,sourceModes:1});
assert.ok(mode.manaOnly.some(e=>e.id==='cycler'));assert.equal(mode.slots,40);
// A hybrid payment can draw from the union without counting a dual twice.
const hybrid={...ev.byId.early,id:'hybrid',cost:'{W/U}{W/U}'};
f.botPolicy.profiles.hybrid={...structuredClone(f.botPolicy.profiles.early),symbols:['W/U','W/U']};
assert.ok(ev.castability(hybrid,['W','U'],ev.sourceModel([],[],{W:8,U:8}),2)>ev.chance(8,2,2));
const oneDual={units:[{W:1,U:1}],sources:{W:1,U:1}};assert.equal(ev.castability(hybrid,['W','U'],oneDual,2),0);
f.cards.push(cheap,hybrid);f.collation.groups.all.push('cheap','hybrid');
// CODE-09: joint choices use the same phase function before each pick.
const two=structuredClone(f);two.seats=4;two.packSize=5;two.picksPerTurn=2;two.collation.recipe[0].count=5;
const s=E.createSession(two,'phase-regression',Array.from({length:3},()=>({strategy:'signals'})),4);
s.step(s.current()[0].uid);s.step(s.current()[0].uid);assert.equal(s.bots[0].log[0].phase,'esplora');
// CODE-10/13: owned main quality is absolute, independent of catalog averages.
const absolute=structuredClone(f);absolute.archetypes={WU:{},BR:{}};absolute.botPolicy.coverage.synergies=false;
absolute.cards=[make('owned-w',{score:3}),make('owned-r',{score:2.99,colors:['R'],cost:'{1}{R}'}),
 make('catalog-w',{score:4.8}),make('catalog-r',{score:1,colors:['R'],cost:'{1}{R}'}),
 make('fill-w',{score:2}),make('improve-r',{score:3.5,colors:['R'],cost:'{1}{R}'}),
 make('unused-g',{colors:['G'],cost:'{G}',score:1})];
absolute.botPolicy.profiles=Object.fromEntries(absolute.cards.map(c=>[c.id,{...structuredClone(f.botPolicy.profiles.early),symbols:[...c.cost.matchAll(/\{([^}]+)\}/g)].map(m=>m[1])}]));
absolute.collation.groups.all=absolute.cards.map(c=>c.id);
const ae=E.createEvaluator(absolute,4),owned=[...many('owned-w',23),...many('owned-r',23,100)];
assert.ok(ae.build(owned,'WU','signals',{remaining:0}).score>ae.build(owned,'BR','signals',{remaining:0}).score);
const almost=E.botState('signals');almost.target='WU';almost.pool=[...many('owned-w',22),...many('unused-g',19,100)];
assert.equal(ae.rank(almost,[entry('unused-g',999),entry('fill-w',998)],3,13,E.rng('fill'),false).scores[0].entry.id,'fill-w');
// CODE-11: a different ordering from signals cannot credit an unused card.
const signalBot=E.botState('signals');signalBot.pool=owned;
signalBot.memory={sides:{'1':{values:{R:5,B:5,W:0,U:0,G:0},count:4}}};
const plans=ae.context(signalBot,3).plans;assert.equal(plans[0].lane,'BR');assert.ok(plans[0].deck.score<plans[1].deck.score);
const sr=ae.rank(signalBot,[entry('unused-g',999),entry('improve-r',998)],3,13,E.rng('signals'),false);
assert.equal(sr.scores[0].entry.id,'improve-r');assert.ok(sr.scores.find(x=>x.entry.id==='unused-g').components.mazzo<=1e-9);
// CODE-14/15: freely addable basics permit splash without owned fixing.
const splash=ev.bestBuild([...many('early',24),entry('red',999)],'WU','adaptive',{remaining:0});
assert.ok(splash.spells.some(e=>e.id==='red'));assert.ok(splash.basics.R>=3);
const prioritized=ev.build([...many('early',24),entry('red-seven',88),entry('cycler',99),entry('basic-cycler',98)],'W','adaptive',{remaining:0,splash:'R',splashBasics:2,sourceModes:1});
assert.ok(prioritized.manaOnly.length===1);
const named=ev.build([...many('early',24),entry('red-seven',88),entry('a-plains-cycler',98),entry('z-mountain-cycler',99)],'W','adaptive',{remaining:0,splash:'R',splashBasics:2,sourceModes:1});
assert.equal(named.manaOnly[0].id,'z-mountain-cycler');
const allColors=ev.bestBuild([...many('early',24),entry('red',999),entry('double-B',998),entry('double-G',997)],'WU','adaptive',{remaining:0});
assert.ok(allColors.spells.some(e=>e.id==='red'));
// CODE-17: waiting two turns for splash does not require two extra lands.
const delayed=ev.build([...many('early',24),entry('gold',999)],'WU','adaptive',{remaining:0,splash:'R',splashBasics:5});
const estimate=delayed.manaEstimates.find(x=>x.id==='gold');assert.equal(estimate.turn,5);assert.equal(estimate.latestTurn,7);assert.equal(estimate.requiredSources,5);
// CODE-18/19: an excluded in-color cycler may replace a base, while a
// restricted modal face cannot obscure a usable cycler with a later id.
const inside=ev.build([...many('early',24),entry('cycler',99)],'WU','adaptive',{remaining:0,splash:'R',splashBasics:2,sourceModes:1});
assert.ok(inside.manaOnly.some(e=>e.id==='cycler'));assert.equal(inside.spells.filter(e=>e.id==='cycler').length,1);assert.equal(inside.slots,40);
const restricted=ev.build([...many('early',24),entry('a-restricted-modal',98),entry('z-mountain-cycler',99)],'W','adaptive',{remaining:0,splash:'R',splashBasics:2,sourceModes:1});
assert.equal(restricted.manaOnly[0].id,'z-mountain-cycler');
const copyLimited=structuredClone(f);copyLimited.botPolicy.maxCopies=4;
const copies=E.createEvaluator(copyLimited,4).build([...many('early',24),...many('cycler',6,100)],'WU','adaptive',{remaining:0,splash:'R',splashBasics:2,sourceModes:1});
assert.ok(copies.spells.filter(e=>e.id==='cycler').length<=4);
// CODE-20: final main ignores draft signal preferences, respecting force.
assert.equal(ae.finalBuild(owned,'signals').lane,'WU');assert.equal(ae.finalBuild(owned,'force',{target:'BR'}).lane,'BR');
const equivalents=E.botState('signals');equivalents.target='WU';
const eq=ev.rank(equivalents,[entry('early',1),entry('blue',2)],1,1,E.rng('equivalence'),false);
assert.notEqual(eq.scores[0].signature,eq.scores[1].signature);
// CODE-21: improvement to a nearby second plan beats a useless card even
// before that plan overtakes the first. Option value disappears at the end.
const optionFormat=structuredClone(absolute);optionFormat.packSize=28;
optionFormat.cards.find(c=>c.id==='improve-r').score=3.01;
const oe=E.createEvaluator(optionFormat,4),optionBot=E.botState('adaptive');optionBot.pool=owned;
const options=oe.rank(optionBot,[entry('unused-g',999),entry('improve-r',998)],2,1,E.rng('option'),false);
assert.equal(options.scores[0].entry.id,'improve-r');assert.ok(options.scores[0].components.opzioni>0);
const finalOptions=ae.rank({...optionBot,pool:[...owned,...many('unused-g',40,1000)]},[entry('unused-g',999),entry('fill-w',998)],3,14,E.rng('end'),false);
assert.ok(finalOptions.scores.every(x=>x.components.opzioni===0));
// CODE-22: fetch targets include owned basics when free basics are forbidden.
const ownedOnly=structuredClone(f);ownedOnly.botPolicy.allowedBasics=[];ownedOnly.botPolicy.extraBasicLands=false;
const noFree=E.createEvaluator(ownedOnly,4).build([...many('early',12),...many('blue',11,100),...many('owned-plains',8,200),...many('owned-island',8,220),entry('fetch',240)],'WU','adaptive',{remaining:0});
assert.ok(noFree.sources.W>8&&noFree.sources.U>8);assert.equal(noFree.sources.R,0);assert.equal(noFree.slots,40);
// CODE-23: a tapped land with only one relevant color does not displace a
// strictly better free basic in the modeled mana configuration.
const tapped=ev.build([...many('early',12),...many('blue',12,100),...many('tapped-wb',3,200)],'WU','adaptive',{remaining:0});
assert.equal(tapped.lands.length,0);
// CODE-24: a pivot reports exits separately from replacements in its new lane.
const pivotBot=E.botState('adaptive');pivotBot.pool=owned;
const pivotPick=ae.rank(pivotBot,[entry('improve-r',998)],2,1,E.rng('pivot-explanation'),false).scores[0];
assert.ok(pivotPick.pivot);assert.equal(pivotPick.pivot.from,'WU');assert.equal(pivotPick.pivot.to,'BR');
assert.ok(pivotPick.replaces.every(id=>id==='owned-r'));assert.ok(pivotPick.pivot.out.includes('owned-w'));
// The off-plan pruning preserves the full build, including excluded cards.
const pruneBot=E.botState('signals');pruneBot.target='WU';pruneBot.pool=many('early',8);
const pruneEntry=entry('inaccessible',999),pruned=ev.rank(pruneBot,[pruneEntry],1,9,E.rng('prune'),false).scores[0];
assert.deepEqual(pruned.deck,ev.bestBuild([...pruneBot.pool,pruneEntry],'WU','signals',{remaining:34}));
// CODE-25: the realized winning plan cannot also receive option credit.
assert.equal(pivotPick.components.opzioni,0);
const mirror=structuredClone(optionFormat);mirror.cards.find(c=>c.id==='owned-r').score=2.9996;
mirror.cards.find(c=>c.id==='improve-r').score=3.4996;
mirror.cards.push({...mirror.cards.find(c=>c.id==='owned-w'),id:'improve-w',name:'improve-w',full:'improve-w',score:3.5});
mirror.botPolicy.profiles['improve-w']=structuredClone(mirror.botPolicy.profiles['owned-w']);mirror.collation.groups.all.push('improve-w');
const me=E.createEvaluator(mirror,4),mr=me.rank(optionBot,[entry('improve-w',998),entry('improve-r',999)],2,1,E.rng('mirror'),false);
assert.ok(mr.scores.every(x=>x.components.opzioni===0));assert.equal(mr.scores[0].entry.id,'improve-w');assert.ok(mr.scores[0].score-mr.scores[1].score<.02);
// CODE-26: a sideboard reserve for a close second plan is not a real pivot.
mirror.cards.push({...mirror.cards.find(c=>c.id==='owned-r'),id:'side-r',name:'side-r',full:'side-r',score:1.5});
mirror.botPolicy.profiles['side-r']={...structuredClone(mirror.botPolicy.profiles['owned-r']),roles:['spell','sideboard']};mirror.collation.groups.all.push('side-r');
const se=E.createEvaluator(mirror,4),sideRank=se.rank(optionBot,[entry('side-r',998)],2,1,E.rng('side-pivot'),false).scores[0];
assert.ok(sideRank.components.sideboard>0);assert.equal(sideRank.lane,'WU');assert.equal(sideRank.pivot,null);assert.equal(sideRank.deck.lane,'WU');assert.deepEqual(sideRank.replaces,[]);
// CODE-27: the structured pivot also survives the joint-choice log.
const jointFormat=structuredClone(absolute);jointFormat.packSize=28;jointFormat.picksPerTurn=2;
const je=E.createEvaluator(jointFormat,4),jointBot=E.botState('adaptive');jointBot.pool=owned;
je.takeGroup(jointBot,{packetId:8,cards:[entry('improve-r',998),entry('unused-g',999)]},2,19,2,E.rng('joint-pivot'),{deterministic:true});
assert.ok(jointBot.log.some(l=>l.joint&&l.pivot?.from==='WU'&&l.pivot?.to==='BR'));
// CODE-28: equivalent fixing spends the less valuable body, independently of
// printing identifiers. The bomb remains a spell rather than a source slot.
for(const [bombId,junkId] of [['a-bomb','z-junk'],['z-bomb','a-junk']]){
 const modeFormat=structuredClone(f);
 for(const [id,color,score] of [[bombId,'W',4.2],[junkId,'B',1.5]]){
  modeFormat.cards.push(make(id,{colors:[color],cost:'{5}{'+color+'}',mv:6,score}));
  modeFormat.botPolicy.profiles[id]={...structuredClone(f.botPolicy.profiles.cycler),symbols:['5',color]};modeFormat.collation.groups.all.push(id);
 }
 const md=E.createEvaluator(modeFormat,4).build([...many('early',24),entry(bombId,998),entry(junkId,999)],'W','adaptive',{remaining:0,splash:'R',splashBasics:2,sourceModes:1});
 assert.equal(md.manaOnly[0].id,junkId);assert.ok(md.spells.some(e=>e.id===bombId));
}
console.log('PASS: main refill, ghost support, primary double pips, reductions, C lands, fetch, own sources, alternative modes, hybrid union, joint phases, absolute plans, signal deltas, late filler and splash basics.');
