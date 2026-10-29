'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const output=process.env.MTG_QA_DIR,base=process.env.MTG_SITE_URL,key='mtg-draft-table-fra-v1';
const frozen=JSON.parse(fs.readFileSync('tests/fixtures/draft-policy-production-cases.json','utf8'));
const quantile=(a,q)=>[...a].sort((a,b)=>a-b)[Math.max(0,Math.ceil(a.length*q)-1)];
(async()=>{
 fs.mkdirSync(output,{recursive:true});const destination=path.join(output,'performance.json');assert.ok(!fs.existsSync(destination),'Preserve earlier acquisition');
 const browser=await chromium.launch({headless:true,...(process.env.MTG_BROWSER_CHANNEL?{channel:process.env.MTG_BROWSER_CHANNEL}:{})}),rows=[];
 const scenarios=frozen.reservedSeeds.slice(0,3).map(seed=>({seed,scenario:'default'}));scenarios.push({seed:frozen.reservedSeeds[3],scenario:'power'});
 const monitor=()=>{window.longestTask=0;window.maxGap=0;window.longTasks=[];let last=performance.now();window.monitor=new PerformanceObserver(list=>list.getEntries().forEach(e=>{window.longestTask=Math.max(window.longestTask,e.duration);window.longTasks.push({stage:window.measureStage,duration:e.duration});}));window.monitor.observe({type:'longtask'});window.timer=setInterval(()=>{const now=performance.now();window.maxGap=Math.max(window.maxGap,now-last);last=now;},25);};
 try{for(const scenario of scenarios){
  const context=await browser.newContext({viewport:{width:1440,height:1050}});context.setDefaultTimeout(240000);await context.route('https://**/*',r=>r.abort());const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'sets/reality-fracture/Reality-Fracture-Draft-Engine.html');
  const hardware=await page.evaluate(()=>({concurrency:navigator.hardwareConcurrency,userAgent:navigator.userAgent}));
  const format=await page.evaluate(()=>{const d=JSON.parse(document.querySelector('#draft-data').textContent);return d.formats?.draft||d;});
  if(!fs.existsSync(path.join(output,'format.json')))fs.writeFileSync(path.join(output,'format.json'),JSON.stringify(format));
  await page.locator('#policy-version').selectOption('4');await page.locator('#seed').fill(scenario.seed);
  if(scenario.scenario==='power')await page.locator('[data-strategy]').evaluateAll(nodes=>nodes.forEach(node=>{node.value='power';node.dispatchEvent(new Event('change'));}));
  await page.locator('#start').click();await page.waitForFunction(()=>!document.querySelector('#start').disabled);await page.evaluate(monitor);
  const times=[];for(let n=0;n<format.rounds*format.packSize;n++){
   await page.evaluate(n=>window.measureStage='pick-'+n,n+1);const started=Date.now();await page.locator('#pack [data-pick]').first().click();await page.waitForFunction(()=>!document.querySelector('#start').disabled);
   if(n===format.rounds*format.packSize-1)await page.locator('#bot-review[aria-busy="false"]').waitFor({state:'visible'});
   times.push(Date.now()-started);
  }
  const record=await page.evaluate(k=>JSON.parse(localStorage.getItem(k)),key);assert.equal(record.picks.length,42);
  await page.evaluate(()=>window.measureStage='export');const download=page.waitForEvent('download');const exportStarted=Date.now();await page.locator('#export').click();const file=await download,raw=fs.readFileSync(await file.path(),'utf8');fs.writeFileSync(path.join(output,scenario.seed+'-export.json'),raw);
  const metrics=await page.evaluate(()=>{clearInterval(window.timer);return {longestTask:window.longestTask,maxGap:window.maxGap,longTasks:window.longTasks};});
  const row={...scenario,hardware,decisions:times.length,timesMs:times,p50Ms:quantile(times,.5),p95Ms:quantile(times,.95),maxMs:Math.max(...times),exportMs:Date.now()-exportStarted,...metrics,replays:[]};rows.push(row);
  for(const length of scenario.seed===scenarios[0].seed?[41,42]:[]){
   const prior={...record,picks:record.picks.slice(0,length)};await page.evaluate(({key,prior})=>localStorage.setItem(key,JSON.stringify(prior)),{key,prior});await page.reload();assert.equal(page.workers().length,0);
   const boot=await page.evaluate(()=>{const n=performance.getEntriesByType('navigation')[0];return n.domContentLoadedEventEnd-n.responseEnd;});assert.ok(boot<=1000,'Renderer boot '+boot);
   await page.evaluate(monitor);const started=Date.now();await page.locator('#resume').click();await page.waitForFunction(()=>!document.querySelector('#start').disabled);if(length===42)await page.locator('#bot-review[aria-busy="false"]').waitFor({state:'visible'});
   if(length===42){const replayDownload=page.waitForEvent('download');await page.locator('#export').click();const replayFile=await replayDownload,replayRaw=fs.readFileSync(await replayFile.path(),'utf8');fs.writeFileSync(path.join(output,scenario.seed+'-replay-export.json'),replayRaw);assert.deepEqual(JSON.parse(replayRaw),JSON.parse(raw),'Full resumed export must equal initial export');}
   const state=await page.evaluate(()=>{clearInterval(window.timer);return {longestTask:window.longestTask,maxGap:window.maxGap};});row.replays.push({picks:length,rendererBootMs:boot,durationMs:Date.now()-started,...state});
   assert.ok(state.longestTask<=200,JSON.stringify(row));assert.ok(state.maxGap<500,JSON.stringify(row));
  }
  fs.writeFileSync(destination,JSON.stringify({complete:false,rows},null,2));
  assert.deepEqual(errors,[]);assert.ok(metrics.longestTask<=200,JSON.stringify(row));assert.ok(metrics.maxGap<500,JSON.stringify(row));
  fs.writeFileSync(destination,JSON.stringify({complete:false,rows},null,2));console.log(JSON.stringify({...row,timesMs:undefined}));await context.close();
 }
 const defaults=rows.filter(r=>r.scenario==='default').flatMap(r=>r.timesMs),result={complete:true,rows,default:{decisions:defaults.length,p50Ms:quantile(defaults,.5),p95Ms:quantile(defaults,.95),maxMs:Math.max(...defaults)},acceptance:{hardware:'Desktop only. No physical mobile measurement or worker CPU emulation claim.',p95Ms:5000,longestTaskMs:200,maxGapMs:500},scope:'Reserved seeds used for functional/performance release checks. No competitive promotion or WR claim.'};
 fs.writeFileSync(destination,JSON.stringify(result,null,2));assert.ok(defaults.length>=126);assert.ok(result.default.p95Ms<=5000,JSON.stringify(result.default));console.log('PASS '+JSON.stringify(result.default));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
