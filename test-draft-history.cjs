'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),E=require('./draft-engine.js');
require('./draft-history.js');
const html=fs.readFileSync('dist/sets/reality-fracture/Reality-Fracture-Draft-Engine.html','utf8');
const root=JSON.parse(html.match(/<script id="draft-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const base=root.formats?.[root.defaultEvent]||root;
for(const picksPerTurn of [1,2])for(const version of [2,3]){
 const format={...base,picksPerTurn};
 const configs=Array.from({length:format.seats-1},()=>({strategy:'signals'}));
 const s=E.createSession(format,'history-duplicates-foil',configs,version),observed=[];
 while(!s.complete){observed.push(s.current().map(e=>({...e})));s.step(s.current()[0].uid);}
 const record=JSON.stringify(s.export());
 for(let seat=-1;seat<s.bots.length;seat++){
  const history=DraftHistory.timeline(s,seat),pool=seat===-1?s.human:s.bots[seat].pool;
  assert.equal(history.length,format.rounds*Math.ceil(format.packSize/picksPerTurn));
  const picks=history.flatMap(t=>t.chosen);
  assert.deepEqual(picks.map(e=>e.uid).sort((a,b)=>a-b),pool.map(e=>e.uid).sort((a,b)=>a-b));
  let before=[];
  for(const t of history){
   assert.deepEqual(t.before.map(e=>e.uid),before.map(e=>e.uid));before.push(...t.chosen);
   const expected=seat===-1?observed[s.log.findIndex(i=>i.round===t.round&&i.pick===t.pick)]:s.bots[seat].log.find(i=>i.round===t.round&&i.pick===t.pick).observed;
   assert.deepEqual([...t.chosen,...t.left].map(e=>e.id).sort(),(seat===-1?expected.map(e=>e.id):expected).slice().sort());
   assert.equal(new Set([...t.chosen,...t.left].map(e=>e.uid)).size,t.chosen.length+t.left.length);
  }
  for(const entry of picks)assert.deepEqual(entry,pool.find(e=>e.uid===entry.uid));
  assert.deepEqual(DraftHistory.timeline(E.replay(format,s.export()),seat),history);
 }
 assert.equal(JSON.stringify(s.export()),record);
}
console.log('PASS: history for every seat, v2/v3 replay, both passing directions, Pick-Two, full observed packs, pools, unique copies and foil; saved record unchanged.');

