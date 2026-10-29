'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto'),{Worker}=require('node:worker_threads');
const E=require('./draft-engine.js'),{fixture}=require('./tests/draft-policy-fixture.cjs');
(async()=>{
 const worker=new Worker(`
  const {parentPort}=require('node:worker_threads'),vm=require('node:vm'),fs=require('node:fs');
  const blobs=new Map();let blobId=0;
  class LocalURL extends URL {static createObjectURL(blob){const id='blob:'+ ++blobId;blobs.set(id,Buffer.concat(blob.parts.map(x=>Buffer.from(x))));return id;}static revokeObjectURL(id){blobs.delete(id);}}
  const context=vm.createContext({postMessage:data=>parentPort.postMessage(data),crypto:require('node:crypto').webcrypto,URL:LocalURL,Blob:class {constructor(parts){this.parts=parts;}},location:{href:'http://localhost/draft-worker.js'},fetch:async url=>({ok:true,arrayBuffer:async()=>fs.readFileSync(new URL(url).pathname.slice(1))})});
  context.self=context;context.importScripts=(...names)=>names.forEach(name=>vm.runInContext(blobs.get(name).toString('utf8'),context,{filename:name}));
  vm.runInContext(fs.readFileSync('draft-worker.js','utf8'),context);
  parentPort.on('message',data=>context.onmessage({data}));`,{eval:true});
 let id=0;
 const call=(command,args={})=>new Promise((resolve,reject)=>{const n=++id;const receive=data=>{if(data.id!==n||data.progress)return;worker.off('message',receive);data.error?reject(Error(data.error)):resolve(data.result);};worker.on('message',receive);worker.postMessage({id:n,command,...args});});
 try{
  const f=fixture();f.botPolicy.algorithmRevision=crypto.createHash('sha256').update(Buffer.concat(['draft-policy.js','draft-engine.js','collation.js'].flatMap((name,i)=>[...(i?[Buffer.from([0])]:[]),fs.readFileSync(name)]))).digest('hex');f.packSize=3;f.rounds=1;f.seats=3;f.directions=[1];f.collation.recipe[0].count=3;
  const configs=[{strategy:'signals'},{strategy:'aggro'}],options={match:'BO1',deterministic:true};
  const sync=E.createSession(f,'worker-parity',configs,4,options);
  let state=await call('create',{format:f,seed:sync.seed,configs,options});
  assert.deepEqual(state.record,sync.export());assert.deepEqual(state.bots,[]);
  await assert.rejects(call('deck',{seat:0}),/non disponibile/);
  while(!sync.complete){const uid=sync.current()[0].uid;sync.step(uid);state=await call('step',{uid});assert.deepEqual(state.record,sync.export());assert.deepEqual(state.current,sync.current());}
  assert.deepEqual(state.bots,sync.bots.map(b=>({strategy:b.strategy,lane:b.lane})));
  const full=JSON.parse(await call('export'));
  assert.deepEqual(full,{...sync.export(),review:sync.bots.map(({strategy,pool,log})=>({strategy,pool,log}))});
  const review=await call('review',{seat:0});
  assert.deepEqual(review.bot,{...sync.bots[0],log:sync.bots[0].log.map(({deck,...item})=>item)});
  const deck=await call('deck',{seat:0});assert.deepEqual(deck,E.createEvaluator(f,4).finalBuild(sync.bots[0].pool,'signals',{match:'BO1'}));
  const replayed=await call('replay',{format:f,record:state.record});assert.deepEqual(replayed.bots,state.bots);assert.deepEqual(JSON.parse(await call('export')),full);
  await assert.rejects(call('replay',{format:f,record:{...state.record,algorithmRevision:'old'}}),/incompatibile/);
  await assert.rejects(call('create',{format:{...f,botPolicy:{...f.botPolicy,algorithmRevision:'different-bytes'}},seed:sync.seed,configs,options}),/diversa dalla pagina/);
  console.log('PASS: worker and synchronous engine have identical records, full logs and final main; pending privacy and incompatible replay rejection.');
 }finally{await worker.terminate();}
})().catch(error=>{console.error(error);process.exitCode=1;});
