'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
(async()=>{
 let instance;
 class FakeWorker{
  constructor(){instance=this;this.messages=[];this.terminated=false;}
  postMessage(message){this.messages.push(message);if(message.command==='create')queueMicrotask(()=>this.onmessage({data:{id:message.id,result:{current:[{id:'a',uid:1}],record:{picks:[]},complete:false,human:[]}}}));}
  terminate(){this.terminated=true;}
 }
 const context=vm.createContext({Worker:FakeWorker,URL,document:{baseURI:'http://localhost/test.html'},Error,structuredClone,setTimeout});
 vm.runInContext(fs.readFileSync('draft-worker-client.js','utf8'),context);
 const proxy=await context.DraftWorkerClient.create({},{}),original=proxy.export();
 assert.equal(proxy.alive,true);
 const first=proxy.export();first.picks.push(123);assert.deepEqual(proxy.export(),original);
 const step=proxy.step(1);instance.onmessage({data:{id:instance.messages.at(-1).id,error:'failure mid-step'}});
 await assert.rejects(step,/failure/);await new Promise(resolve=>setTimeout(resolve,70));assert.equal(instance.terminated,true);assert.deepEqual(proxy.export(),original);
 assert.equal(proxy.alive,false);
  assert.deepEqual(JSON.parse(await proxy.exportDownload()),original);
 await assert.rejects(proxy.step(1),/failure/);assert.deepEqual(proxy.current(),[{id:'a',uid:1}]);
 const abort=new AbortController();const loading=context.DraftWorkerClient.create({},{record:{},signal:abort.signal});abort.abort();
 await assert.rejects(loading,/annullata/);await new Promise(resolve=>setTimeout(resolve,70));assert.equal(instance.terminated,true);
 console.log('PASS: failed worker step preserves committed export and current pack, rejects retry, and replay cancellation terminates the worker.');
})().catch(error=>{console.error(error);process.exitCode=1;});
