'use strict';
const assert=require('node:assert/strict'),E=require('./draft-engine.js'),{fixture}=require('./tests/draft-policy-fixture.cjs');
(async()=>{
 for(const picksPerTurn of [1,2]){
  const f=fixture();f.seats=4;f.packSize=4;f.rounds=2;f.directions=[1,-1];f.picksPerTurn=picksPerTurn;f.collation.recipe[0].count=4;
  const configs=['signals','fixing','power'].map(strategy=>({strategy})),sync=E.createSession(f,'async-'+picksPerTurn,configs,4),parallel=E.createSession(f,sync.seed,configs,4),evaluator=E.createEvaluator(f,4);
  const choose=async job=>{await Promise.resolve();const choices=evaluator.takeGroup(job.bot,job.packet,job.round,job.pick,job.count,E.rng(job.randomSeed),job.options);return {bot:job.bot,choices:choices.map(e=>e.uid)};};
  while(!sync.complete){const uid=sync.current()[0].uid;sync.step(uid);await parallel.stepAsync(uid,choose);assert.deepEqual(parallel.bots,sync.bots);assert.deepEqual(parallel.export(),sync.export());assert.deepEqual(parallel.current(),sync.current());}
 }
 const f=fixture(),s=E.createSession(f,'async-failure',Array.from({length:7},()=>({strategy:'signals'})),4),before=s.export();
 await assert.rejects(s.stepAsync(s.current()[0].uid,async()=>{throw Error('failed');}),/failed/);assert.deepEqual(s.export(),before);assert.equal(s.human.length,0);
 await assert.rejects(s.stepAsync(s.current()[0].uid,async()=>({choices:[],bot:{}})),/non coerente/);assert.deepEqual(s.export(),before);
 console.log('PASS: asynchronous and sequential records, pools and logs identical for ordinary/Pick-Two; failed or malformed results leave committed state intact.');
})().catch(error=>{console.error(error);process.exitCode=1;});
