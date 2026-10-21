'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),E=require('./draft-engine.js');
const html=fs.readFileSync('dist/sets/reality-fracture/Reality-Fracture-Draft-Engine.html','utf8');
const data=JSON.parse(html.match(/<script id="draft-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const evaluator=E.createEvaluator(data),byId=evaluator.byId;
const configs=Object.keys(E.STRATEGIES).slice(1,8).map(strategy=>({strategy,target:strategy==='force'?'UB':null}));
const collator=E.createCollator(data,E.rng('distribution-audit'));
let guests=0,rareMain=0,foilLands=0;const count=30000;
for(let i=0;i<count;i++){
 const pack=collator.pack();assert.equal(pack.length,14);assert.equal(new Set(pack.map(e=>e.uid)).size,14);
 const pair=pack.filter(e=>e.slot==='pair').map(e=>byId[e.id]);assert.equal(pair.length,2);assert.equal(pair[0].rarity,pair[1].rarity);assert.equal(collator.partners[pair[0].full],pair[1].full);
 assert.equal(pack.filter(e=>e.slot==='foil').length,1);assert.ok(pack.find(e=>e.slot==='foil').foil);
 assert.ok(pack.filter(e=>e.slot==='common').every(e=>byId[e.id].number<175||byId[e.id].number===188));
 assert.equal(new Set(pack.filter(e=>e.slot==='common').map(e=>e.id)).size,pack.filter(e=>e.slot==='common').length);
 assert.ok(!['pair','echoed'].includes(pack.find(e=>e.slot==='rare').slot));
 assert.ok(byId[pack.find(e=>e.slot==='rare').id].number<195||byId[pack.find(e=>e.slot==='rare').id].number>320);
 const third=byId[pack.find(e=>e.slot==='echoed').id];assert.ok(!pair.some(c=>c.full===third.full));
 assert.ok(pack.every(e=>byId[e.id].set==='SPG'||byId[e.id].number<=401));
 guests+=pack.some(e=>e.slot==='guest');rareMain+=byId[pack.find(e=>e.slot==='rare').id].number<=194&&byId[pack.find(e=>e.slot==='rare').id].rarity==='rare';foilLands+=pack.find(e=>e.slot==='land').foil;
}
assert.ok(Math.abs(guests/count-1/55)<.004);assert.ok(Math.abs(rareMain/count-.744)<.012);assert.ok(Math.abs(foilLands/count-.2)<.012);
const session=E.createSession(data,'replay-check',configs),initial=session.current().map(e=>e.uid);
assert.equal(session.current().length,14);session.step(initial[0]);
assert.equal(session.current().length,13);assert.ok(session.current().every(e=>!initial.includes(e.uid)));
for(let i=1;i<42;i++)session.step(session.current()[i%session.current().length].uid);
assert.ok(session.complete);assert.equal(session.human.length,42);session.bots.forEach(b=>assert.equal(b.pool.length,42));
const all=[...session.human,...session.bots.flatMap(b=>b.pool)];assert.equal(all.length,336);assert.equal(new Set(all.map(e=>e.uid)).size,336);
const restored=E.replay(data,session.export());assert.deepEqual(restored.human,session.human);assert.deepEqual(restored.bots,session.bots);
assert.throws(()=>session.step(0));assert.throws(()=>E.replay(data,{...session.export(),picks:[-1]}));assert.throws(()=>E.createSession(data,'x',configs.map(c=>({...c,strategy:'fake'}))));
// Bots receive only packets they actually observed, before taking a card.
session.bots.forEach(b=>b.log.forEach(x=>{assert.ok(x.observed.includes(x.id));assert.ok(x.alternatives.every(a=>x.observed.includes(a.id)));}));
// Both directions: packet IDs seen at pick two must originate from the correct neighbor.
const route=E.createSession(data,'routing',configs);for(let n=0;n<42;n++)route.step(route.current()[0].uid);
route.bots.forEach((b,i)=>{const seat=i+1;for(const round of [1,2,3]){for(const pick of [1,2,9,14]){const item=b.log.find(x=>x.round===round&&x.pick===pick);assert.equal(item.observed.length,15-pick);const expected=(round-1)*8+(seat-(pick-1)*data.directions[round-1]%8+8)%8;assert.equal(item.packetId,expected);}}});
// Counterpick uses inferred demand and gives up only a weak own-color option.
const card=name=>data.cards.find(c=>c.name===name&&c.number<=280),entry=(name,uid)=>({id:card(name).id,uid});
const denial=E.botState('denial','WU');denial.phase=3;denial.pool=Array.from({length:28},(_,i)=>entry('Campus Crier',i));denial.demand.B=10;
const testPack=[entry('Extended Absence',100),entry('Academic Ascent',101)];
let ranking=evaluator.rank(denial,testPack,3,10,E.rng('denial'),false);assert.ok(ranking.scores.find(s=>s.entry.uid===100).components.negazione>0);
denial.demand.B=0;ranking=evaluator.rank(denial,testPack,3,10,E.rng('denial'),false);assert.equal(ranking.scores.find(s=>s.entry.uid===100).components.negazione,undefined);
// Prior pool changes the preference: a forced WU and a forced UB disagree.
const a=E.botState('force','WU'),b=E.botState('force','UB');a.phase=b.phase=3;
const alternatives=[entry('Campus Crier',200),entry('Extended Absence',201)];
assert.notEqual(evaluator.rank(a,alternatives,3,1,E.rng('x'),false).scores[0].entry.id,evaluator.rank(b,alternatives,3,1,E.rng('x'),false).scores[0].entry.id);
console.log(JSON.stringify({packs:count,guestRate:guests/count,rareMainRate:rareMain/count,foilLandRate:foilLands/count,drafted:all.length,replay:'identical',strategies:Object.keys(E.STRATEGIES).length}));
