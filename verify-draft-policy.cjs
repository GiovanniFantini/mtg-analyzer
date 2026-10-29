'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const E=require('./draft-engine.js'),{fixture}=require('./tests/draft-policy-fixture.cjs');
const f=fixture(),ev=E.createEvaluator(f,4),entry=(id,uid)=>({id,uid});
const pool=(id,n,start=0)=>Array.from({length:n},(_,i)=>entry(id,start+i));
const cfg=Array.from({length:7},()=>({strategy:'signals',target:null}));
const rank=(b,ids)=>ev.rank(b,ids.map((id,i)=>entry(id,100+i)),3,1,E.rng('probe'),false);
// Historical digests are pinned to policy version, never the changing default.
const rootData=JSON.parse(fs.readFileSync('dist/sets/reality-fracture/Reality-Fracture-Draft-Engine.html','utf8').match(/<script id="draft-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const real=rootData.formats?.draft||rootData;
for(const test of JSON.parse(fs.readFileSync('tests/fixtures/draft-bots-v3.json','utf8')).cases){
 const s=E.replay(real,test.record);assert.equal(crypto.createHash('sha256').update(JSON.stringify(s.bots)).digest('hex'),test.digest);
 if(!s.complete){s.step(s.current()[0].uid);assert.equal(s.export().engineVersion,3);}
}
// The same grades and roles cannot acquire a color preference from data order.
const symmetric=structuredClone(f);symmetric.cards=[...'WUBRG'].map(color=>({...f.cards[0],id:color,name:color,full:color,colors:[color],cost:'{1}{'+color+'}'}));
symmetric.botPolicy.profiles=Object.fromEntries(symmetric.cards.map(c=>[c.id,{...structuredClone(f.botPolicy.profiles.early),symbols:['1',c.id]}]));
symmetric.collation.groups.all=symmetric.cards.map(c=>c.id);
for(const archetypes of [symmetric.archetypes,Object.fromEntries(Object.entries(symmetric.archetypes).reverse())]){
 const r=E.createEvaluator({...symmetric,archetypes},4).rank(E.botState('signals'),symmetric.cards.map((c,i)=>entry(c.id,i)),1,1,E.rng('sym'),false);
 assert.ok(Math.max(...r.scores.map(x=>x.score))-Math.min(...r.scores.map(x=>x.score))<1e-9);
}
// Inaccessible colored producers are not sources, while reachable cycling is.
const green=[ev.byId.inaccessible,ev.byId.inaccessible];
assert.equal(ev.sourceModel(green,[],{W:9,U:8}).sources.R,0);
assert.equal(ev.sourceModel([ev.byId.cycler],[],{W:9,U:8}).sources.R,0);
assert.ok(ev.sourceModel([ev.byId.cycler],[ev.byId['typed-dual']],{W:8,U:8}).sources.R>0);
assert.ok(ev.sourceModel([ev.byId.cycler],[],{W:8,U:7,R:2}).sources.R>2);
assert.equal(ev.sourceModel([ev.byId.cycler],[],{W:8,U:7,R:2},2).sources.R,2);
assert.ok(ev.sourceModel(Array(3).fill(ev.byId.cycler),[],{W:8,U:8,R:1}).sources.R<=1.5+1e-9);
assert.equal(ev.sourceModel([ev.byId['basic-cycler']],[ev.byId['typed-dual']],{W:8,U:8}).sources.R,1);
const uses=ev.sourceModel([ev.byId.cycler],[],{W:8,U:7,R:2}).uses.cycler[0];assert.ok(uses.cycling>0&&uses.cycling<1);
assert.ok(ev.turn(ev.byId.variable,[])>2);assert.ok(ev.turn(ev.byId.reducer,pool('early',12).map(e=>ev.byId[e.id]))>3);
const modal=structuredClone(f);modal.botPolicy.profiles.early.mana.alternativeLand={colors:['W'],tapped:false,restricted:false};
const modalModel=E.createEvaluator(modal,4).sourceModel([modal.cards[0]],[],{W:8,U:8});
assert.equal(modalModel.uses.early[0].alternativeLand,.5);assert.equal(modalModel.sources.W,8.5);
// Density, reference point, and shared resources, using distinct actual copies.
const payoff=ev.byId.payoff,enabler=ev.byId.enabler,consumer=ev.byId.consumer,resource=ev.byId.resource;
assert.ok(ev.synergy(payoff,[payoff],0).adjustment<0);
assert.equal(ev.synergy(payoff,[payoff,enabler,enabler,enabler],0).adjustment,0);
assert.ok(ev.synergy(payoff,[payoff,...Array(8).fill(enabler)],0).adjustment>0);
assert.ok(ev.synergy(payoff,[payoff],35).option>ev.synergy(payoff,[payoff],0).option);
assert.ok(ev.synergy(consumer,[consumer,...Array(8).fill(resource)],0).adjustment>
 ev.synergy(consumer,[consumer,consumer,...Array(8).fill(resource)],0).adjustment);
const partial=structuredClone(f);partial.botPolicy.coverage.synergies=false;
assert.deepEqual(E.createEvaluator(partial,4).synergy(payoff,[payoff,...Array(8).fill(enabler)],35),{adjustment:0,option:0});
// A surplus filler cannot count as an extra main slot or inflate curve support.
const full=ev.build(pool('early',24),'WU','aggro',{remaining:0});
const surplus=ev.build([...pool('early',24),entry('filler',99)],'WU','aggro',{remaining:0});
assert.equal(full.spells.length,surplus.spells.length);assert.ok(surplus.excluded.some(e=>e.id==='filler'));
assert.equal(full.slots,40);
assert.equal(ev.build(pool('early',12),'WU','adaptive',{remaining:0}).slots,40);
const limited=structuredClone(f);limited.botPolicy.maxCopies=4;
assert.equal(E.createEvaluator(limited,4).build(pool('early',24),'WU','aggro',{remaining:0}).spells.length,4);
const single=ev.build([...pool('early',24),entry('sideboard',99)],'WU','aggro',{remaining:0,match:'BO1'});
const match=ev.build([...pool('early',24),entry('sideboard',99)],'WU','aggro',{remaining:0,match:'BO3'});
assert.deepEqual(single.spells,match.spells);assert.equal(single.sideboard.length,0);assert.equal(match.sideboard.length,1);
// Functional roles, needs and pivot are independent of sunk picks.
for(const [style,expected] of [['aggro','early'],['control','defender']]){
 const r=ev.rank(E.botState(style),['early','defender'].map((id,uid)=>entry(id,uid)),1,1,E.rng('roles'),false);
 assert.equal(r.scores[0].entry.id,expected);
}
const pivot=E.botState('signals');pivot.phase=2;pivot.lane='WU';pivot.pool=[...pool('filler',8),...pool('blue',5,20)];
// Eight owned white playables and five blue ones do not justify abandoning W.
assert.ok(ev.context(pivot,2).lane.includes('W'));
pivot.pool=[entry('filler',0),...pool('blue',8,10),...pool('red',8,30)];
const pivotDeck=ev.context(pivot,2).plans[0].deck;
assert.ok(pivotDeck.spells.some(e=>e.id==='blue')&&pivotDeck.spells.some(e=>e.id==='red'));
assert.ok(!pivotDeck.spells.some(e=>e.id==='filler'));assert.equal(pivotDeck.basics.W,0);
pivot.pool=pool('late',24);pivot.target='WU';assert.equal(rank(pivot,['early','filler']).scores[0].entry.id,'early');
// Side memory and observations remain distinct even during Pick-Two subpicks.
const b=E.botState('signals'),packet={packetId:1,cards:pool('blue',5,100)};
ev.observe(b,packet,1,7);const memory=structuredClone(b.memory);ev.observe(b,{...packet,cards:packet.cards.slice(1)},1,7);
assert.deepEqual(b.memory,memory);assert.deepEqual(ev.context(b,3).sig,memory.sides['1'].values);
ev.observe(b,{packetId:20,cards:pool('early',5,200)},2,7);assert.notDeepEqual(ev.context(b,2).sig,ev.context(b,3).sig);
const earlySignal=E.botState('signals'),lateSignal=E.botState('signals');
ev.observe(earlySignal,{packetId:0,cards:pool('blue',3)},1,2);ev.observe(lateSignal,{packetId:0,cards:pool('blue',3)},1,8);
assert.ok(lateSignal.memory.sides[1].values.U>earlySignal.memory.sides[1].values.U);
// Versioned sessions, exact continuation, random isolation and active privacy.
const s=E.createSession(f,'new-policy',cfg,4,{match:'BO1'});
s.step(s.current()[0].uid);assert.equal(s.export().version,3);assert.equal(s.export().options.match,'BO1');
assert.ok(!s.export().review&&!s.export().bots);
assert.deepEqual(E.replay(f,s.export()).bots,s.bots);
assert.throws(()=>E.replay(f,{...s.export(),policyRevision:'different'}));
assert.throws(()=>E.replay(f,{...s.export(),options:undefined}));
assert.throws(()=>E.createSession(f,'bad',cfg,4,{match:'invalid'}));
const altered=cfg.map(c=>({...c}));altered[0].strategy='power';
const t=E.createSession(f,'new-policy',altered,4,{match:'BO1'});t.step(t.current()[0].uid);
// All opening packets are independent; changing bot 1 cannot shift bot 2 RNG.
assert.deepEqual(t.bots[1].log,s.bots[1].log);
while(!s.complete)s.step(s.current()[0].uid);
assert.equal(new Set([...s.human,...s.bots.flatMap(b=>b.pool)].map(c=>c.uid)).size,f.seats*f.rounds*f.packSize);
assert.deepEqual(E.replay(f,s.export()).bots,s.bots);
// Joint choices, odd final packet, no repeated evidence and exact replay.
const two=structuredClone(f);two.seats=4;two.picksPerTurn=2;two.packSize=5;two.collation.recipe[0].count=5;
const pairs=E.createSession(two,'pairs',cfg.slice(0,3),4);
while(!pairs.complete)pairs.step(pairs.current()[0].uid);
assert.equal(pairs.bots[0].pool.length,15);
assert.equal(Object.keys(pairs.bots[0].memory.observations).length,9);
assert.ok(pairs.bots[0].log.some(l=>l.joint));assert.deepEqual(E.replay(two,pairs.export()).bots,pairs.bots);
console.log('PASS: v3 frozen digests; v4 symmetric colors, mana, typed cycling, density, reference grades, resource contention, minimum main, BO1/BO3, side memory, replay, RNG isolation and joint Pick-Two.');
