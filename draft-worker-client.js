'use strict';
// The proxy only exposes committed snapshots. No storage or DOM in this module.
((root)=>{
 async function create(format,request){
  const {signal,onProgress,...payload}=request;
  const workerURL=new URL('draft-worker.js',document.baseURI);workerURL.searchParams.set('v',format.botPolicy?.workerRevision||format.botPolicy?.algorithmRevision||'');
  const worker=new Worker(workerURL),pending=new Map();let next=0,failed=null;
  const fail=error=>{if(failed)return;failed=error;for(const {reject} of pending.values())reject(error);pending.clear();try{worker.postMessage({command:'dispose'});}catch{}setTimeout(()=>worker.terminate(),50);};
  worker.onerror=()=>fail(Error('Calcolo dei bot non disponibile. Il salvataggio precedente resta conservato.'));
  worker.onmessage=({data})=>{const task=pending.get(data.id);if(!task)return;if(data.progress){task.progress?.(data.progress);return;}pending.delete(data.id);if(data.error){const error=Error(data.error);task.reject(error);fail(error);}else task.resolve(data.result);};
  const call=(command,args={},progress)=>new Promise((resolve,reject)=>{
   if(failed){reject(failed);return;}const id=++next;pending.set(id,{resolve,reject,progress});
   try{worker.postMessage({id,command,...args});}catch(error){pending.delete(id);reject(error);}
  });
  const abort=()=>fail(Error('Ripresa annullata. Il salvataggio resta conservato.'));
  signal?.addEventListener('abort',abort,{once:true});if(signal?.aborted)abort();
  let state;
  try{state=await call(payload.record?'replay':'create',{format,...payload},onProgress);}catch(error){fail(error);throw error;}finally{signal?.removeEventListener('abort',abort);}
  const proxy={...state,current:()=>state.current,export:()=>structuredClone(state.record),
   async step(uid){state=await call('step',{uid});Object.assign(proxy,{...state,current:proxy.current});},
   finalDeck:seat=>call('deck',{seat}),review:seat=>call('review',{seat}),exportDownload:()=>failed?Promise.resolve(JSON.stringify(state.record,null,2)):call('export'),dispose:()=>fail(Error('Sessione chiusa'))};
  Object.defineProperty(proxy,'alive',{get:()=>!failed});
  return proxy;
 }
 root.DraftWorkerClient={create};
})(globalThis);
