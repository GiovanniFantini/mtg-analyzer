'use strict';
// Same deterministic engine, isolated from the browser UI and from storage.
let session=null,evaluator=null;
let loadedRevision=null;
let verifiedSources=null,pool=null;
async function loadAlgorithm(format){
 const revision=format.botPolicy?.algorithmRevision;
 if(loadedRevision===revision)return;
 if(!self.crypto?.subtle||typeof revision!=='string')throw Error('Bot contestuali non disponibili: verifica della versione non supportata in questo browser. Usa i bot classici.');
 const names=['draft-policy.js','draft-engine.js','collation.js'],buffers=await Promise.all(names.map(async name=>{
  const url=new URL(name,self.location.href);url.searchParams.set('v',revision);
  const response=await fetch(url,{cache:'no-store'});if(!response.ok)throw Error('Codice dei bot non disponibile. Ricarica la pagina o usa i bot classici.');return new Uint8Array(await response.arrayBuffer());
 }));
 const bytes=new Uint8Array(buffers.reduce((n,b)=>n+b.length,0)+2);let offset=0;
 for(const [index,buffer] of buffers.entries()){if(index)bytes[offset++]=0;bytes.set(buffer,offset);offset+=buffer.length;}
 const digest=[...new Uint8Array(await self.crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
 if(digest!==revision)throw Error('Versione del codice dei bot diversa dalla pagina. Ricarica il sito o usa i bot classici. Il salvataggio precedente resta conservato.');
 const urls=buffers.map(buffer=>URL.createObjectURL(new Blob([buffer],{type:'text/javascript'})));
 try{importScripts(urls[2],urls[0],urls[1]);loadedRevision=revision;verifiedSources=buffers;}finally{urls.forEach(url=>URL.revokeObjectURL(url));}
}
function seatPool(format){
 const footer=`let evaluator;self.onmessage=event=>{const {id,format,job}=event.data;try{if(format)evaluator=DraftEngine.createEvaluator(format,4);const choices=evaluator.takeGroup(job.bot,job.packet,job.round,job.pick,job.count,DraftEngine.rng(job.randomSeed),job.options);self.postMessage({id,result:{bot:job.bot,choices:choices.map(e=>e.uid)}});}catch(error){self.postMessage({id,error:error.message});}};`;
 const url=URL.createObjectURL(new Blob([verifiedSources[2],'\n',verifiedSources[0],'\n',verifiedSources[1],'\n',footer],{type:'text/javascript'}));
 const workers=[],queue=[];let next=0,closed=false;
 const fail=error=>{closed=true;for(const item of workers){item.worker.terminate();item.task?.reject(error);}for(const task of queue)task.reject(error);queue.length=0;};
 const drain=()=>{for(const item of workers){if(item.task||!queue.length)continue;const task=queue.shift();item.task=task;try{item.worker.postMessage({id:task.id,...(!item.initialized?{format}:{}),job:task.job});item.initialized=true;}catch(error){fail(error);return;}}};
 // Leave capacity for the page, coordinator and browser work under CPU load.
 try{for(let i=0;i<Math.min(format.seats-1,4,Math.max(1,(self.navigator?.hardwareConcurrency||2)-2));i++){
  const item={worker:new Worker(url),task:null,initialized:false};workers.push(item);
  item.worker.onmessage=({data})=>{const task=item.task;if(!task||task.id!==data.id)return;item.task=null;if(data.error){task.reject(Error(data.error));fail(Error(data.error));return;}task.resolve(data.result);drain();};
  item.worker.onerror=()=>fail(Error('Calcolo parallelo non disponibile. Usa i bot classici.'));
 }}catch(error){fail(error);throw error;}finally{URL.revokeObjectURL(url);}
 return {run:job=>new Promise((resolve,reject)=>{if(closed){reject(Error('Calcolo dei bot interrotto'));return;}queue.push({id:++next,job,resolve,reject});drain();}),dispose:()=>fail(Error('Sessione chiusa'))};
}
const decks=new Map();
const snapshot=()=>({engineVersion:session.engineVersion,seed:session.seed,configs:session.configs,
 policyOptions:session.policyOptions,human:session.human,bots:session.complete?session.bots.map(b=>({strategy:b.strategy,lane:b.lane})):[],
 round:session.round,pick:session.pick,complete:session.complete,current:session.current(),record:session.export()});
self.onmessage=async event=>{
 const {id,command,format,record,seed,configs,options,uid,seat}=event.data;
 try{
  if(command==='dispose'){pool?.dispose();self.close();return;}
  let result;
  if(command==='create'||command==='replay'){
   await loadAlgorithm(format);
   pool?.dispose();pool=typeof Worker==='function'?seatPool(format):null;
   session=command==='replay'?DraftEngine.createReplaySession(format,record):DraftEngine.createSession(format,seed,configs,4,options);
   if(command==='replay')for(const [index,pick] of record.picks.entries()){if(pool)await session.stepAsync(pick,pool.run);else session.step(pick);self.postMessage({id,progress:{done:index+1,total:record.picks.length}});}
   evaluator=DraftEngine.createEvaluator(format,4);decks.clear();result=snapshot();
  }else if(command==='step'){if(pool)await session.stepAsync(uid,pool.run);else session.step(uid);result=snapshot();}
  else if(command==='deck'||command==='review'){
   if(!session?.complete||!Number.isInteger(seat)||!session.bots[seat])throw Error('Revisione non disponibile');
   if(!decks.has(seat)){const bot=session.bots[seat];decks.set(seat,evaluator.finalBuild(bot.pool,bot.strategy,
    {target:bot.strategy==='force'?bot.target:null,match:session.policyOptions.match}));}
   result=command==='deck'?decks.get(seat):{deck:decks.get(seat),bot:{...session.bots[seat],log:session.bots[seat].log.map(({deck,...item})=>item)}};
  }else if(command==='export'){
   const record=session.export();if(session.complete)record.review=session.bots.map(({strategy,pool,log})=>({strategy,pool,log}));result=JSON.stringify(record,null,2);
  }else throw Error('Comando non riconosciuto');
  self.postMessage({id,result});
 }catch(error){self.postMessage({id,error:error.message||String(error)});}
};
