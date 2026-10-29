'use strict';
// Conservation and paired construction after exact same-browser sequential replay.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const E=require('../../draft-engine.js'),out=process.env.MTG_QA_DIR;
const f=JSON.parse(fs.readFileSync(path.join(out,'format.json'),'utf8'));
const performance=JSON.parse(fs.readFileSync(path.join(out,'performance.json'),'utf8'));
assert.equal(performance.complete,true);
const browserParity=JSON.parse(fs.readFileSync(path.join(out,'browser-sequential-parity.json'),'utf8'));assert.equal(browserParity.complete,true);
const destination=path.join(out,'sequential-parity.json');assert.ok(!fs.existsSync(destination));
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex'),results=[];
const ev=E.createEvaluator(f,4);
function diagnostic(session){return session.bots.map((bot,seat)=>{
 const d=ev.finalBuild(bot.pool,'adaptive',{match:'BO3'}),owned=new Map(bot.pool.map(e=>[e.uid,e.id]));
 const used=[...d.spells,...d.lands];assert.equal(d.slots,40);assert.equal(new Set(used.map(e=>e.uid)).size,used.length);
 for(const e of used)assert.equal(owned.get(e.uid),e.id);
 for(const [color,count] of Object.entries(d.basics)){assert.ok(Number.isInteger(count)&&count>=0);if(count)assert.ok(f.botPolicy.allowedBasics.includes(color));}
 return {seat:seat+1,strategy:bot.strategy,slots:d.slots,spells:d.spells.length,ownedLands:d.lands.length,basics:d.basics,manaOnly:d.manaOnly.length,holes:d.holes,manaErrors:d.manaErrors,sources:d.sources};
});}
for(const row of performance.rows){
 const record=JSON.parse(fs.readFileSync(path.join(out,row.seed+'-export.json'),'utf8')),start=Date.now();
 const canonical=JSON.parse(fs.readFileSync(path.join(out,row.seed+'-browser-sequential.json'),'utf8'));
 assert.equal(hash(canonical),hash(record),'Same-browser sequential full export');
 const parity=browserParity.results.find(r=>r.seed===row.seed&&r.exactFullExportParity);assert.ok(parity);
 const collator=E.createCollator(f,E.rng(row.seed)),initial=Array.from({length:f.rounds*f.seats},()=>collator.pack()).flat().sort((a,b)=>a.uid-b.uid);
 const byUid=new Map(initial.map(e=>[e.uid,e])),s={bots:record.review,human:record.picks.map(uid=>byUid.get(uid))},review=record.review;
 const all=[...s.human,...s.bots.flatMap(b=>b.pool)].sort((a,b)=>a.uid-b.uid);
 assert.equal(new Set(all.map(e=>e.uid)).size,f.seats*f.rounds*f.packSize);assert.deepEqual(all,initial);
 const classic=E.createSession(f,row.seed,record.configs,3,record.options);
 while(!classic.complete)classic.step(classic.current()[0].uid);
 const classicAll=[...classic.human,...classic.bots.flatMap(b=>b.pool)].sort((a,b)=>a.uid-b.uid);assert.deepEqual(classicAll,initial);
 const replayFile=path.join(out,row.seed+'-replay-export.json');if(fs.existsSync(replayFile))assert.deepEqual(JSON.parse(fs.readFileSync(replayFile,'utf8')),record);
 const result={seed:row.seed,scenario:row.scenario,exactPoolLogParity:true,parityRuntime:'Chromium',conservedCards:all.length,collationHash:hash(initial),reviewHash:hash(review),sequentialReplayMs:parity.sequentialReplayMs,v4:diagnostic(s),v3:diagnostic(classic)};
 results.push(result);fs.writeFileSync(destination,JSON.stringify({complete:false,results},null,2));console.log(JSON.stringify({seed:row.seed,exactPoolLogParity:true,conservedCards:all.length,sequentialReplayMs:result.sequentialReplayMs}));
}
fs.writeFileSync(destination,JSON.stringify({complete:true,scope:'Paired fixed first-visible human choices and public collation. Shared evaluator diagnostics measure construction only, not competitive strength or WR.',results},null,2));
console.log('PASS: all acquired browser tables match sequential replay exactly, with paired v3 collation and owned-only forty-slot construction.');
