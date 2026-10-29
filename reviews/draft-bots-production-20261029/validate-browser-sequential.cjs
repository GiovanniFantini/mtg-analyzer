'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const out=process.env.MTG_QA_DIR,f=JSON.parse(fs.readFileSync(path.join(out,'format.json'))),perf=JSON.parse(fs.readFileSync(path.join(out,'performance.json')));
const destination=path.join(out,'browser-sequential-parity.json');assert.ok(!fs.existsSync(destination));
const hash=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL});const results=[];
 async function run(row){
  const original=JSON.parse(fs.readFileSync(path.join(out,row.seed+'-export.json'))),{review,...record}=original;
  const context=await browser.newContext(),page=await context.newPage();context.setDefaultTimeout(300000);
  await context.route('**/__sequential_validation__',r=>r.fulfill({contentType:'text/html',body:'<html></html>'}));await page.goto(process.env.MTG_SITE_URL+'__sequential_validation__');
  const start=Date.now();
  const raw=await page.evaluate(async({f,record,base})=>{
   const names=['draft-policy.js','draft-engine.js','collation.js'];const buffers=await Promise.all(names.map(async n=>new Uint8Array(await(await fetch(base+n,{cache:'no-store'})).arrayBuffer())));
   const joined=new Uint8Array(buffers.reduce((n,b)=>n+b.length,0)+2);let offset=0;for(const [i,b] of buffers.entries()){if(i)joined[offset++]=0;joined.set(b,offset);offset+=b.length;}
   const revision=[...new Uint8Array(await crypto.subtle.digest('SHA-256',joined))].map(n=>n.toString(16).padStart(2,'0')).join('');if(revision!==f.botPolicy.algorithmRevision)throw Error('Wrong source bytes');
   const footer=`self.onmessage=({data})=>{try{const s=DraftEngine.replay(data.f,data.record),record=s.export();record.review=s.bots.map(({strategy,pool,log})=>({strategy,pool,log}));self.postMessage({raw:JSON.stringify(record)});}catch(e){self.postMessage({error:e.message});}};`;
   const url=URL.createObjectURL(new Blob([buffers[2],'\n',buffers[0],'\n',buffers[1],'\n',footer],{type:'text/javascript'})),worker=new Worker(url);URL.revokeObjectURL(url);
   try{return await new Promise((resolve,reject)=>{worker.onmessage=({data})=>data.error?reject(Error(data.error)):resolve(data.raw);worker.onerror=e=>reject(Error(e.message));worker.postMessage({f,record});});}finally{worker.terminate();}
  },{f,record,base:process.env.MTG_SITE_URL+'sets/reality-fracture/'});
  const reconstructed=JSON.parse(raw);
  // Compare hashes first to avoid printing megabytes on a concrete mismatch.
  const actualHash=hash(reconstructed),expectedHash=hash(original);
  const result={seed:row.seed,scenario:row.scenario,exactFullExportParity:actualHash===expectedHash,actualHash,expectedHash,sequentialReplayMs:Date.now()-start};
  fs.writeFileSync(path.join(out,row.seed+'-browser-sequential.json'),raw);results.push(result);console.log(JSON.stringify(result));await context.close();assert.equal(actualHash,expectedHash,'Same Chromium sequential full export parity: '+row.seed);
 }
 try{for(let n=0;n<perf.rows.length;n+=2)await Promise.all(perf.rows.slice(n,n+2).map(run));
 fs.writeFileSync(destination,JSON.stringify({complete:true,runtime:'Same Chromium build as acquired exports, source bytes verified, original synchronous E.replay inside isolated worker without auxiliary pool. Two independent cases in parallel after performance acquisition.',results},null,2));}
 finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
