'use strict';
const assert=require('node:assert/strict'),E=require('./draft-engine.js'),{fixture}=require('./tests/draft-policy-fixture.cjs');
const f=fixture(),many=(id,n,start=0)=>Array.from({length:n},(_,i)=>({id,uid:start+i}));
const basic=(id,color,type)=>{
 f.cards.push({...f.cards[0],id,name:id,full:id,colors:[],cost:'',mv:0,land:true,basic:true,creature:false,score:null,type:'Basic Land - '+type});
 f.botPolicy.profiles[id]={...structuredClone(f.botPolicy.profiles['red-base']),mana:{abilities:[{colors:[color],restricted:false,activation:'{T}'}],cycling:[],subtypes:[type],tapped:false}};
};
basic('plains','W','Plains');basic('island','U','Island');
f.botPolicy.coverage.synergies=false;
const ev=E.createEvaluator(f,4),deck=ev.build([...many('early',12),...many('blue',11,30),...many('plains',6,100)],'WU','adaptive',{remaining:0});
assert.equal(deck.slots,40);assert.ok(deck.basics.U>deck.basics.W);assert.ok(Math.abs(deck.sources.W-deck.sources.U)<=2);
// Same spells and physical sources, only the name of the primary lane changes.
const fixed=structuredClone(f);fixed.botPolicy.allowedBasics=[];
const pool=[...many('red',23),...many('plains',8,100),...many('red-base',9,200)];
const e=E.createEvaluator(fixed,4),main=e.build(pool,'WR','adaptive',{remaining:0,splash:'U'}),splash=e.build(pool,'WU','adaptive',{remaining:0,splash:'R'});
assert.deepEqual(main.spells,splash.spells);assert.deepEqual(main.lands,splash.lands);assert.deepEqual(main.basics,splash.basics);
assert.ok(splash.score<=main.score,'Delaying a splash cannot grant a free objective improvement');
assert.equal(splash.manaEstimates[0].turn,main.manaEstimates[0].turn);
assert.equal(splash.manaEstimates[0].requiredSources,4);
function add(id,card,profile){f.cards.push({...f.cards[0],id,name:id,full:id,...card});f.botPolicy.profiles[id]={...structuredClone(f.botPolicy.profiles.early),...profile};}
add('modal-r',{colors:['B'],cost:'{5}{B}',mv:6,score:1},{symbols:['5','B'],mana:{abilities:[],cycling:[],subtypes:[],tapped:false,alternativeLand:{colors:['R'],tapped:false,restricted:false}}});
add('hybrid-wu',{colors:['W','U'],cost:'{1}{W/U}',mv:2},{symbols:['1','W/U']});
for(const color of ['W','U'])add('double-'+color,{colors:[color],cost:'{'+color+'}{'+color+'}',mv:2},{symbols:[color,color]});
add('neutral',{colors:[],cost:'{2}',mv:2,score:2},{symbols:['2']});
add('one-w',{colors:['W'],cost:'{W}',mv:1},{symbols:['W']});
add('slow-wu',{colors:[],cost:'',mv:0,land:true,creature:false,score:3},{symbols:[],roles:['land'],mana:{abilities:[{colors:['W','U'],activation:'{T}',restricted:false}],cycling:[],subtypes:[],tapped:true}});
add('red-two',{colors:['R'],cost:'{1}{R}',mv:2,score:4},{symbols:['1','R']});
const revised=E.createEvaluator(f,4),basePool=[...many('early',24),{id:'red',uid:300}],without=revised.build(basePool,'WU','adaptive',{remaining:0,splash:'R'});
const modal=revised.build([...basePool,{id:'modal-r',uid:400}],'WU','adaptive',{remaining:0,splash:'R',sourceModes:1});
assert.equal(modal.basics.R,without.basics.R-1);assert.equal(modal.sources.R,without.sources.R);assert.equal(modal.manaOnly.length,1);
const hybridPool=color=>[...many('hybrid-wu',8),...many('double-'+color,6,50),...many('neutral',9,100)];
const u=revised.build(hybridPool('U'),'WU','adaptive',{remaining:0}),w=revised.build(hybridPool('W'),'WU','adaptive',{remaining:0});
assert.equal(u.basics.U,w.basics.W);assert.equal(u.basics.W,w.basics.U);assert.ok(u.basics.U>u.basics.W);
const slow=revised.build([...many('one-w',23),...many('slow-wu',4,100)],'WU','adaptive',{remaining:0});assert.equal(slow.lands.length,0);
const fixedEarly=structuredClone(f);fixedEarly.botPolicy.allowedBasics=[];const earlyEv=E.createEvaluator(fixedEarly,4),earlyPool=[...many('red-two',23),...many('plains',8,100),...many('red-base',9,200)];
const on=earlyEv.build(earlyPool,'WR','adaptive',{remaining:0}),off=earlyEv.build(earlyPool,'WU','adaptive',{remaining:0,splash:'R'});
assert.deepEqual(on.deficits,off.deficits);assert.ok(off.score<=on.score);
// Check local base exchanges against actual sourceModel/castability, including modal fixing.
for(const deck of [modal,u,w]){
 const sourceOnly=new Set(deck.manaOnly.map(e=>e.uid)),cards=deck.spells.map(e=>({...revised.byId[e.id],_entry:e,_modeOnly:sourceOnly.has(e.uid)})),lands=deck.lands.map(e=>revised.byId[e.id]);
 const objective=basics=>cards.filter(c=>!c._modeOnly).reduce((value,c)=>{const t=revised.turn(c,cards.filter(x=>!x._modeOnly));return value+c.score*revised.castability(c,[...deck.colors],revised.sourceModel(cards,lands,basics,t),t);},0);
 for(const from of [...deck.colors].filter(c=>deck.basics[c]>0))for(const to of [...deck.colors].filter(c=>c!==from))assert.ok(objective({...deck.basics,[from]:deck.basics[from]-1,[to]:deck.basics[to]+1})<=objective(deck.basics)+1e-9);
}
const dualPool=[...many('early',24),...many('typed-dual',2,100),{id:'red',uid:200}];
const dual=ev.build(dualPool,'WU','adaptive',{remaining:0,splash:'R',splashBasics:2});
const noDual=ev.build(dualPool.filter(e=>e.id!=='typed-dual'),'WU','adaptive',{remaining:0,splash:'R',splashBasics:2});
assert.ok(dual.lands.length===2);assert.ok(dual.basics.R<noDual.basics.R);
// Actual construction with freely addable basics, rather than a fixed base.
const singleBomb=[...many('early',22),{id:'red',uid:200}];
const primary=ev.build(singleBomb,'WR','adaptive',{remaining:0}),optional=ev.build(singleBomb,'WB','adaptive',{remaining:0,splash:'R'});
assert.ok(primary.spells.some(e=>e.id==='red'));assert.ok(primary.basics.R>=2);assert.ok(primary.score>=optional.score);assert.deepEqual(primary.basics,optional.basics);
const heavy=ev.build([...many('blue',13),...many('red',10,100)],'UR','adaptive',{remaining:0});
assert.ok(heavy.sources.R>=7);
const objective=basics=>heavy.spells.reduce((value,e)=>{const c=ev.byId[e.id];return value+Object.entries(ev.needs(c,['U','R'])).reduce((n,[color,pips])=>n+c.score*ev.chance(basics[color]||0,ev.turn(c,[]),pips),0);},0);
for(const from of ['U','R'])if(heavy.basics[from])for(const to of ['U','R'].filter(c=>c!==from))assert.ok(objective({...heavy.basics,[from]:heavy.basics[from]-1,[to]:heavy.basics[to]+1})<=objective(heavy.basics)+1e-9);
const owned=structuredClone(f);owned.botPolicy.allowedBasics=[];
const restricted=E.createEvaluator(owned,4).build([...many('early',20),...many('blue',4,50),...many('plains',12,100),...many('island',12,200)],'WU','adaptive',{remaining:0});
assert.ok(restricted.sources.W>=restricted.sources.U);
const rename=id=>id==='plains'?'island':id==='island'?'plains':id,renamed=structuredClone(owned);
renamed.cards=renamed.cards.map(c=>({...c,id:rename(c.id)}));renamed.botPolicy.profiles=Object.fromEntries(Object.entries(renamed.botPolicy.profiles).map(([id,p])=>[rename(id),p]));
const renamedPool=[...many('early',20),...many('blue',4,50),...many('plains',12,100),...many('island',12,200)].map(e=>({...e,id:rename(e.id)}));
const same=E.createEvaluator(renamed,4).build(renamedPool,'WU','adaptive',{remaining:0});assert.deepEqual(same.sources,restricted.sources);
const power=E.botState('power'),pack=[{id:'early',uid:100},{id:'blue',uid:101}];
for(let seed=0;seed<30;seed++){
 const b=structuredClone(power);ev.take(b,{packetId:0,cards:pack},1,1,E.rng('power-'+seed));assert.equal(b.pool[0].id,'blue');assert.equal(b.log[0].randomized,false);
}
console.log('PASS: owned sources balance added basics; identical mana does not gain value by relabeling a primary color as splash.');
