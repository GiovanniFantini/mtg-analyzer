'use strict';
const assert=require('node:assert/strict'),E=require('./tournament-engine.js');
function event(n){const s=E.create('test','Test','Un set qualsiasi');s.players=Array.from({length:n},(_,i)=>({id:'p'+i,name:'Player '+i,dropped:false}));return s;}
for(let count=2;count<=8;count++){
 const s=event(count),seen=new Set(),byes=new Set();
 for(let r=0;r<Math.min(3,count-1);r++){
  const round=E.pair(s),ids=round.matches.flatMap(m=>m.b?[m.a,m.b]:[m.a]);assert.equal(new Set(ids).size,count);
  for(const m of round.matches){if(m.b){const key=[m.a,m.b].sort().join(':');assert.ok(!seen.has(key));seen.add(key);m.result=[2,1,0];}else{assert.ok(!byes.has(m.a));byes.add(m.a);}}
  s.status='active';s.rounds.push(round);E.validate(s);
 }
 const raw=JSON.stringify(s);assert.deepEqual(E.validate(JSON.parse(raw)),s);assert.equal(E.standings(s).reduce((n,p)=>n+p.points,0),s.rounds.length*Math.ceil(count/2)*3);
}
const s=event(4);s.rounds.push(E.pair(s));s.status='active';assert.throws(()=>E.pair(s),/risultati/);
s.rounds[0].matches[0].result=[2,0,0];s.rounds[0].matches[1].result=[1,1,1];
const rank=E.standings(s);assert.equal(rank[0].points,3);assert.equal(rank[0].omw,.33);assert.equal(rank.find(p=>p.id==='p2').gamePoints,4);assert.equal(rank.find(p=>p.id==='p2').gwp,4/9);
const b=event(3);b.rounds.push(E.pair(b));b.status='active';b.rounds[0].matches[0].result=[2,0,0];const bye=E.standings(b).find(p=>p.byes);assert.equal(bye.points,3);assert.equal(bye.games,2);assert.equal(bye.omw,0);
const invalid=structuredClone(s);invalid.rounds[0].matches[1].a=invalid.rounds[0].matches[0].a;assert.throws(()=>E.validate(invalid),/duplicati/);
assert.throws(()=>E.result([2,2,0]));assert.throws(()=>E.result([-1,0,0]));assert.throws(()=>E.result([1.2,0,0]));assert.throws(()=>E.validate({...s,schemaVersion:2}));
const corrupt=structuredClone(s);corrupt.rounds[0].matches[0].result=null;corrupt.status='complete';assert.throws(()=>E.validate(corrupt));
assert.equal(E.remaining({deadline:12000,remainingMs:3000},10000),2000);assert.equal(E.remaining({deadline:12000,remainingMs:3000},13000),0);assert.equal(E.remaining({deadline:null,remainingMs:3000}),3000);
s.players[3].dropped=true;const next=E.pair(s);assert.ok(!next.matches.some(m=>m.a==='p3'||m.b==='p3'));
const early=event(2);early.status='complete';early.rounds=[{number:1,matches:[{a:'p0',b:'p1',result:[2,0,0]}]}];early.players[1].dropped=true;early.endedEarly=true;E.validate(early);
assert.throws(()=>E.validate({...early,endedEarly:false}));
const fakeEarly=structuredClone(early);fakeEarly.players[1].dropped=false;assert.throws(()=>E.validate(fakeEarly));
const tied=E.create('floating','Floating point fixture','');tied.status='active';tied.players=['A','B','X','Y','Z','Q'].map(id=>({id,name:id,dropped:false}));
tied.rounds=[{number:1,matches:[{a:'A',b:'X',result:[2,0,0]},{a:'B',b:'Y',result:[2,0,0]},{a:'Z',b:'Q',result:[2,0,0]}]},{number:2,matches:[{a:'A',b:'Y',result:[2,0,0]},{a:'B',b:'Z',result:[1,1,0]},{a:'X',b:'Q',result:[0,2,0]}]},{number:3,matches:[{a:'A',b:'Z',result:[1,1,0]},{a:'B',b:'X',result:[2,0,0]},{a:'Y',b:'Q',result:[0,2,0]}]}];
const equalRows=E.standings(E.validate(tied)).filter(p=>p.id==='A'||p.id==='B');assert.equal(E.compareRank(...equalRows),0);
assert.ok(E.compareRank({...equalRows[0],omw:equalRows[0].omw+.0001},equalRows[1])<0);
console.log('Tournament: pairings 2–8 players, no avoidable rematches, fair byes, scoring, tiebreakers, drops, validation and durable clock passed.');
