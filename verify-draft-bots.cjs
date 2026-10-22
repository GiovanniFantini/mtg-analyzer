'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const E=require('./draft-engine.js');
const root=JSON.parse(fs.readFileSync('dist/sets/reality-fracture/Reality-Fracture-Draft-Engine.html','utf8').match(/<script id="draft-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const data=root.formats?.draft||root,ev=E.createEvaluator(data);
const defaults=['signals','bomb','synergy','aggro','control','fixing','denial'];
const configs=defaults.map(strategy=>({strategy,target:null}));
const card=name=>data.cards.find(c=>c.name===name),entry=(name,uid)=>({id:card(name).id,uid});
// Freeze the old algorithm's output, not just a round-trip using the same code.
const fixtures=JSON.parse(fs.readFileSync('tests/fixtures/draft-bots-v2.json','utf8'));
for(const {record,botDigest} of fixtures.cases){
 const restored=E.replay(data,record);
 assert.equal(crypto.createHash('sha256').update(JSON.stringify(restored.bots)).digest('hex'),botDigest);
 assert.deepEqual(restored.export(),record);
 const v1={version:1,format:record.format,seed:record.seed,configs:record.configs,picks:record.picks};
 assert.deepEqual(E.replay(data,v1).bots,restored.bots);
 if(!restored.complete){restored.step(restored.current()[0].uid);assert.equal(restored.export().engineVersion,2);assert.deepEqual(E.replay(data,restored.export()).bots,restored.bots);}
}
// Empty pools and JSON key order cannot favor any of five otherwise identical colors.
const colors=[...'WUBRG'];
const synthetic={...data,cards:colors.map(color=>({id:color,name:color,full:color,score:3,rarity:'common',colors:[color],identity:[color],cost:'{1}{'+color+'}',mv:2,creature:true,land:false,basic:false,role:'',oracle:'',archetypes:[]}))};
for(const strategy of Object.keys(E.STRATEGIES).filter(s=>s!=='force')){
 for(const archetypes of [data.archetypes,Object.fromEntries(Object.entries(data.archetypes).reverse())]){
  const evaluator=E.createEvaluator({...synthetic,archetypes}),bot=E.botState(strategy);
  const ranked=evaluator.rank(bot,colors.map((id,uid)=>({id,uid})),1,1,E.rng('symmetric'),false);
  assert.equal(new Set(ranked.scores.map(s=>s.score)).size,1,strategy+' must start color-neutral');
 }
}
// A single established color must not select an arbitrary second color, even
// after the phase machine reaches consolidation or the first bomb is anchored.
for(const strategy of ['signals','bomb']){
 const mono=E.botState(strategy);mono.phase=3;mono.lane='WU';
 mono.pool=Array.from({length:14},(_,uid)=>({id:'W',uid}));if(strategy==='bomb')mono.anchor='W';
 const ranked=E.createEvaluator(synthetic).rank(mono,colors.slice(1).map((id,uid)=>({id,uid:100+uid})),2,1,E.rng('second-color'),false);
 assert.equal(new Set(ranked.scores.map(s=>s.score)).size,1,strategy+' must leave the second color open');
}
// The reported P1P1 failure: a cheap common must not tie a five-point card.
const aggro=E.botState('aggro');
const opening=ev.rank(aggro,[entry('Mindseeker Oculus',0),entry('The Theorist, Jace Beleren',1)],1,1,E.rng('opening'),false);
assert.equal(opening.scores[0].card.name,'The Theorist, Jace Beleren');
assert.ok(opening.scores[0].score-opening.scores[1].score>.2);
// Same-color quality must survive all profiles, including saturated cheap slots.
for(const strategy of Object.keys(E.STRATEGIES)){
 const bot=E.botState(strategy,strategy==='force'?'WR':null);bot.lane='WR';bot.phase=3;
 bot.pool=Array.from({length:28},(_,i)=>entry(i<8?'Campus Crier':'Hallway Heckler',i));
 const ranked=ev.rank(bot,[entry('Graft Surgeon',100),entry('Ajani Unrelenting',101)],3,1,E.rng('quality'),false);
 assert.equal(ranked.scores[0].card.name,'Ajani Unrelenting',strategy);
 assert.ok(ranked.scores[0].score-ranked.scores[1].score>.2);
}
// Hybrid mana is playable in either color; repeated copies are not distinct synergy support.
const forced=E.botState('force','WU');forced.phase=2;
forced.pool=Array.from({length:10},(_,i)=>entry('Campus Crier',i));
const hybrid=ev.rank(forced,[entry('Blessed Ghoul',20)],2,1,E.rng('hybrid'),false).scores[0];
assert.equal(hybrid.playable,true);assert.ok(hybrid.components.colori>0);
const synergy=E.botState('force','WB');synergy.phase=2;
synergy.pool=Array.from({length:10},(_,i)=>entry('Blessed Ghoul',i));
assert.equal(ev.rank(synergy,[entry('Blessed Ghoul',20)],2,1,E.rng('copies'),false).scores[0].components.sinergia,0);
// Actual mana abilities and typed landcycling support the right splash color.
const manaFixture={...synthetic,cards:[...synthetic.cards,
 {id:'source',full:'source',score:2,colors:[],identity:[],cost:'{2}',mv:2,creature:false,land:false,basic:false,role:'',oracle:'{T}: Add {R}.',archetypes:[]},
 {id:'cycler',full:'cycler',score:2,colors:['R'],identity:['R'],cost:'{5}{R}',mv:6,creature:true,land:false,basic:false,role:'',oracle:'Mountaincycling {2}',archetypes:[]},
 {id:'splash',full:'splash',score:4.5,colors:['R'],identity:['R'],cost:'{3}{R}',mv:4,creature:false,land:false,basic:false,role:'',oracle:'',archetypes:[]},
 {id:'double-red',full:'double-red',score:4.5,colors:['R'],identity:['R'],cost:'{2}{R}{R}',mv:4,creature:false,land:false,basic:false,role:'',oracle:'',archetypes:[]}]};
const manaEv=E.createEvaluator(manaFixture),fixing=E.botState('fixing','WU');fixing.phase=3;
const splashPack=[{id:'splash',uid:100},{id:'double-red',uid:101}];
fixing.pool=[{id:'W',uid:0},{id:'W',uid:1}];
const noSources=manaEv.rank(fixing,splashPack,3,1,E.rng('mana'),false).scores.find(s=>s.entry.id==='splash').components.colori;
fixing.pool=[{id:'source',uid:0},{id:'cycler',uid:1}];
const withSources=manaEv.rank(fixing,splashPack,3,1,E.rng('mana'),false).scores;
assert.ok(withSources.find(s=>s.entry.id==='splash').components.colori>noSources);
assert.equal(withSources.find(s=>s.entry.id==='double-red').components.colori,noSources);
// Tactical components stay bounded, including colorless creatures with removal text.
for(const strategy of Object.keys(E.STRATEGIES)){
 const bot=E.botState(strategy,strategy==='force'?'WU':null);bot.phase=3;bot.lane='WU';
 bot.pool=Array.from({length:28},(_,i)=>entry('Campus Crier',i));bot.signals[3]=Object.fromEntries(colors.map(c=>[c,10]));
 for(const s of ev.rank(bot,data.cards.map((c,uid)=>({id:c.id,uid})),3,1,E.rng('bounds'),false).scores){
  const tactical=['sinergia','curva','segnali','mana'].map(k=>s.components[k]);
  assert.ok(tactical.reduce((n,v)=>n+Math.max(0,v),0)<=.4500001);
  assert.ok(tactical.reduce((n,v)=>n+Math.min(0,v),0)>=-.2000001);
  assert.ok(Number.isFinite(s.score));
 }
}
// First pack from an actual reported seed, with the old human policy held fixed.
const session=E.createSession(data,'bot-audit-134',configs);
const humanEv=E.createEvaluator(data,2),human=E.botState('signals');
session.step(humanEv.take(human,{packetId:0,cards:session.current()},1,1,E.rng('bot-audit-134-human')).uid);
assert.equal(ev.byId[session.bots[3].log[0].id].name,'The Theorist, Jace Beleren');
assert.equal(session.export().engineVersion,3);
assert.deepEqual(E.replay(data,session.export()).bots,session.bots);
assert.throws(()=>E.replay(data,{...session.export(),engineVersion:999}));
console.log('PASS: frozen v1/v2 replays and continuation; v3 replay; color neutrality; reported picks; bounded tactical bonuses; hybrid mana; duplicate support.');
