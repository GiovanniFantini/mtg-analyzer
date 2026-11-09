'use strict';
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const E=require('../../draft-engine.js');
const qa=process.env.MTG_SIM_QA_DIR||path.join(process.cwd(),'docs/local/qa/star-trek-sim-integration');
const formats=Object.fromEntries(['draft','picktwo'].map(k=>[k,JSON.parse(fs.readFileSync(path.join(qa,k+'.json'),'utf8'))]));
const f=formats.draft,byId=new Map(f.cards.map(c=>[c.id,c]));
const collator=E.createCollator(f,E.rng('trk-model-distribution-20261109'));
const n=10000;let sds=0,foils=0,dual=0;
for(let i=0;i<n;i++){
 const pack=collator.pack();assert.equal(pack.length,14);assert.equal(new Set(pack.map(e=>e.uid)).size,14);
 assert.equal(pack.filter(e=>e.slot==='foil').length,1);assert.equal(pack.filter(e=>e.slot==='land').length,1);
 for(const slot of ['common','uncommon']){const names=pack.filter(e=>e.slot===slot).map(e=>byId.get(e.id).full);assert.equal(new Set(names).size,names.length);}
 const bonus=pack.filter(e=>byId.get(e.id).set==='SDS');assert.ok(bonus.length<=1);assert.ok(bonus.every(e=>e.slot==='stardates'&&!e.foil));sds+=bonus.length;
 foils+=pack.filter(e=>e.foil).length;dual+=byId.get(pack.find(e=>e.slot==='land').id).identity.length===2;
 assert.ok(pack.every(e=>f.collation.recipe.some(r=>r.id===e.slot)));
}
assert.ok(Math.abs(sds/n-.04)<.01);assert.ok(Math.abs(foils/n-1.2)<.02);assert.ok(Math.abs(dual/n-50/100.2)<.02);
const results=[];const strategies=Object.keys(E.STRATEGIES);
for(const [event,format] of Object.entries(formats))for(const version of [2,3,4]){
 const configs=Array.from({length:format.seats-1},(_,i)=>({strategy:version===4&&i===0?'adaptive':strategies[(i+(event==='picktwo'?6:0))%strategies.length],target:strategies[(i+(event==='picktwo'?6:0))%strategies.length]==='force'?'WU':null}));
 const seed='trk-complete-'+event+'-'+version;
 const session=E.createSession(format,seed,configs,version,{match:'BO1',deterministic:true});
 while(!session.complete){const pack=session.current();session.step(pack[(session.pick-1)%pack.length].uid);}
 const expected=format.rounds*format.packSize;assert.equal(session.human.length,expected);
 assert.ok(session.bots.every(b=>b.pool.length===expected));
 const all=[...session.human,...session.bots.flatMap(b=>b.pool)];assert.equal(all.length,format.seats*expected);assert.equal(new Set(all.map(e=>e.uid)).size,all.length);
 const restored=E.replay(format,session.export());assert.deepEqual(restored.export(),session.export());assert.deepEqual(restored.bots,session.bots);
 assert.throws(()=>E.replay({...format,revision:'former-empty-profile'},session.export()));
 results.push({event,engineVersion:version,players:format.seats,picksPerPlayer:expected,conservedCards:all.length,replay:true,profiles:configs.map(c=>c.strategy)});
 console.log('Completed',event,'v'+version);
}
const report={samplePacks:n,sdsRate:sds/n,meanFoilCards:foils/n,dualLandRate:dual/n,interpretation:'Agreement with simulator input model, not observed physical booster rates or gameplay WR.',results};
fs.writeFileSync(path.join(qa,'simulation-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
