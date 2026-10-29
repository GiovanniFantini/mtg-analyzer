'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {fixture}=require('./tests/draft-policy-fixture.cjs'),policy=fs.readFileSync('draft-policy.js','utf8'),engine=fs.readFileSync('draft-engine.js','utf8');
const fast="    if(!p.mana.cycling.length&&!p.mana.alternativeLand&&!direct(c).length){uses[c.id]=(uses[c.id]||[]).concat(entryUse);continue;}";
assert.ok(policy.includes(fast));
let reference=policy.replace(fast,'').replace('const cached=allocationCache.get(allocationKey);','const cached=null;').replace(/  const directColors=new Map\(\);\r?\n  function direct\(c\)\{[^\n]+\}/,"  function direct(c){const m=profile(c).mana;return [...new Set(m.abilities.filter(a=>!a.restricted).flatMap(a=>a.colors))];}");
assert.ok(!reference.includes('directColors'));
const symbolStart=reference.indexOf('  function symbolChance('),symbolEnd=reference.indexOf('  function synergy(',symbolStart);
reference=reference.slice(0,symbolStart)+fs.readFileSync('tests/fixtures/draft-symbol-chance-reference.js.txt','utf8')+reference.slice(symbolEnd);
const groupStart=reference.indexOf('  function takeGroup('),groupEnd=reference.indexOf('  return {byId',groupStart);
reference=reference.slice(0,groupStart)+fs.readFileSync('tests/fixtures/draft-policy-group-reference.js.txt','utf8')+reference.slice(groupEnd);
const load=source=>{const context=vm.createContext({module:{exports:{}}});vm.runInContext(source,context);return context.module.exports;};
const implementation=source=>{const api=load(source),context=vm.createContext({module:{exports:{}},require:name=>name==='./draft-policy.js'?api:require(name)});vm.runInContext(engine,context);return context.module.exports;};
const optimized=implementation(policy),unoptimized=implementation(reference),hash=x=>crypto.createHash('sha256').update(x).digest('hex'),digests=[];
for(const picksPerTurn of [1,2]){
 const f=fixture();f.seats=3;f.rounds=2;f.packSize=4;f.directions=[1,-1];f.picksPerTurn=picksPerTurn;f.collation.recipe[0].count=4;
 const configs=[{strategy:'signals'},{strategy:'fixing'}],a=optimized.createSession(f,'perf-parity-'+picksPerTurn,configs,4),b=unoptimized.createSession(f,'perf-parity-'+picksPerTurn,configs,4);
 while(!a.complete){const uid=a.current()[0].uid;a.step(uid);b.step(uid);assert.equal(JSON.stringify(a.bots),JSON.stringify(b.bots));assert.equal(JSON.stringify(a.export()),JSON.stringify(b.export()));}
 digests.push({picksPerTurn,digest:hash(JSON.stringify(a.bots))});
}
const result={optimizedHash:hash(policy),referenceHash:hash(reference),digests};
fs.writeFileSync('reviews/draft-bots-production-20261029/optimization-parity.json',JSON.stringify(result,null,2));
console.log('PASS: cached direct colors and zero-source fast path preserve all bot pool/log digests for ordinary and Pick-Two fixtures.');
