'use strict';
const assert=require('node:assert/strict'),E=require('./draft-engine.js'),{fixture}=require('./tests/draft-policy-fixture.cjs');
for(const strategy of ['signals','bomb','synergy','aggro','control','fixing','denial','power'])for(const basicId of ['a-free-basic','z-free-basic']){
 const f=fixture();f.botPolicy.coverage.synergies=false;
 const base=f.cards.find(c=>c.id==='red-base');
 f.cards.push({...base,id:basicId,name:basicId,full:basicId});f.botPolicy.profiles[basicId]=structuredClone(f.botPolicy.profiles['red-base']);
 const ev=E.createEvaluator(f,4),bot=E.botState(strategy);bot.pool=Array.from({length:40},(_,uid)=>({id:'early',uid}));
 const reserve=f.cards.find(c=>c.id==='filler');
 // A full pool cannot gain a main slot from this lower-grade on-color reserve.
 const pack=[{id:basicId,uid:100},{id:reserve.id,uid:101}];
 const r=ev.rank(bot,pack,3,14,E.rng('tie'),false,{match:'BO3'});
 assert.equal(r.scores[0].entry.id,reserve.id,strategy+' '+basicId);
 const reversed=ev.rank(bot,pack.slice().reverse(),3,14,E.rng('tie'),false,{match:'BO3'});
 assert.equal(reversed.scores[0].entry.id,reserve.id);
 const only=ev.rank(bot,[pack[0]],3,14,E.rng('tie'),false,{match:'BO3'});assert.equal(only.scores[0].entry.id,basicId);
}
// Without free basics a physical source must keep its actual draft value.
const f=fixture();f.botPolicy.allowedBasics=[];
const ev=E.createEvaluator(f,4),bot=E.botState('signals');bot.pool=Array.from({length:23},(_,uid)=>({id:'red',uid}));
const r=ev.rank(bot,[{id:'red-base',uid:100},{id:'filler',uid:101}],3,1,E.rng('physical'),false);
assert.equal(r.scores[0].entry.id,'red-base');assert.ok(r.scores[0].components.mazzo>0);
console.log('PASS: free basics lose tied picks across all profiles, both ID/pack orders; forced final basics and useful physical sources remain legal.');
// Empty-pool construction cannot demote a stronger late card below filler.
for(const strategy of ['signals','bomb','synergy','aggro','control','fixing','denial'])for(const color of ['W','U','B','R','G']){
 const f=fixture(),late={...f.cards.find(c=>c.id==='late'),id:'premium',name:'Premium',full:'Premium',score:4.5,colors:[color],cost:'{4}{'+color+'}{'+color+'}{'+color+'}',mv:7};
 f.cards.push(late);f.botPolicy.profiles.premium={...structuredClone(f.botPolicy.profiles.late),symbols:['4',color,color,color]};
 const ev=E.createEvaluator(f,4),bot=E.botState(strategy),pack=[{id:'early',uid:100},{id:'premium',uid:101}];
 for(const cards of [pack,pack.slice().reverse()]){
  const result=ev.rank(bot,cards,1,1,E.rng('opening'),false);
  assert.equal(result.scores[0].entry.id,'premium',strategy+' '+color);
  assert.ok(Number.isFinite(result.scores[0].components.qualitaIniziale));
 }
 bot.pool=Array.from({length:f.packSize},(_,uid)=>({id:'early',uid}));
 assert.ok(ev.rank(bot,pack,2,1,E.rng('oriented'),false).scores.every(s=>!Object.hasOwn(s.components,'qualitaIniziale')));
}
console.log('PASS: opening grade prior across five colors/seven styles and both pack orders; prior absent after the first pack.');

const forced=fixture(),forcedBot=E.botState('force','WU'),forcedEv=E.createEvaluator(forced,4);
const forcedScores=forcedEv.rank(forcedBot,[{id:'early',uid:90},{id:'red',uid:91}],1,1,E.rng('forced'),false).scores;
assert.ok(!Object.hasOwn(forcedScores.find(s=>s.entry.id==='red').components,'qualitaIniziale'));
assert.ok(Object.hasOwn(forcedScores.find(s=>s.entry.id==='early').components,'qualitaIniziale'));
