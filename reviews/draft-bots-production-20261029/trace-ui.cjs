'use strict';
// Diagnostic only, excluded from acceptance. Collect main-thread CPU and timeline.
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const out=process.env.MTG_QA_DIR;fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL});
 try{const context=await browser.newContext({viewport:{width:1440,height:1050}}),page=await context.newPage();context.setDefaultTimeout(240000);await context.route('https://**/*',r=>r.abort());
 await page.goto(process.env.MTG_SITE_URL+'sets/reality-fracture/Reality-Fracture-Draft-Engine.html');
 await page.locator('#policy-version').selectOption('4');await page.locator('#seed').fill('production-reserved-227');await page.locator('#start').click();await page.waitForFunction(()=>!document.querySelector('#start').disabled);
 const cdp=await context.newCDPSession(page);await cdp.send('Profiler.enable');await cdp.send('Profiler.start');await cdp.send('Tracing.start',{categories:'devtools.timeline,v8,disabled-by-default-v8.gc',transferMode:'ReturnAsStream'});
 await page.evaluate(()=>{window.tasks=[];new PerformanceObserver(list=>list.getEntries().forEach(e=>window.tasks.push({stage:window.stage,duration:e.duration,start:e.startTime}))).observe({type:'longtask'});});
 for(let n=0;n<42;n++){await page.evaluate(n=>{window.stage=n;performance.mark('pick-'+n);},n+1);await page.locator('#pack [data-pick]').first().click();await page.waitForFunction(()=>!document.querySelector('#start').disabled);}
 await page.locator('#bot-review[aria-busy="false"]').waitFor();
 const profile=await cdp.send('Profiler.stop');fs.writeFileSync(path.join(out,'main.cpuprofile'),JSON.stringify(profile.profile));
 const complete=new Promise(resolve=>cdp.once('Tracing.tracingComplete',resolve));await cdp.send('Tracing.end');const {stream}=await complete;const file=fs.openSync(path.join(out,'timeline.json'),'w');
 for(;;){const chunk=await cdp.send('IO.read',{handle:stream});fs.writeSync(file,chunk.base64Encoded?Buffer.from(chunk.data,'base64'):chunk.data);if(chunk.eof)break;}fs.closeSync(file);await cdp.send('IO.close',{handle:stream});
 const tasks=await page.evaluate(()=>window.tasks);fs.writeFileSync(path.join(out,'long-tasks.json'),JSON.stringify(tasks,null,2));console.log(JSON.stringify(tasks));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
