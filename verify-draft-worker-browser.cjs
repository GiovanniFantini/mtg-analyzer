'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
const base=process.env.MTG_SITE_URL,key='mtg-draft-table-fra-v1';
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.MTG_BROWSER_CHANNEL?{channel:process.env.MTG_BROWSER_CHANNEL}:{})});
 try{
  const context=await browser.newContext();context.setDefaultTimeout(180000);await context.route('https://**/*',r=>r.abort());
  await context.addInitScript(()=>{const NativeWorker=Worker;window.Worker=class extends NativeWorker{postMessage(message){if(window.failNextWorkerStep&&message.command==='step'){window.failNextWorkerStep=false;queueMicrotask(()=>this.onerror(new Event('error')));return;}super.postMessage(message);}};});
  const page=await context.newPage(),url=base+'sets/reality-fracture/Reality-Fracture-Draft-Engine.html';await page.goto(url);
  const idle=()=>page.waitForFunction(()=>!document.querySelector('#start').disabled),read=()=>page.evaluate(k=>JSON.parse(localStorage.getItem(k)),key);
  await page.locator('#policy-version').selectOption('4');await page.locator('#start').click();await idle();
  await page.locator('#pack [data-pick]').first().click();await idle();const saved=await read();assert.equal(saved.picks.length,1);const activeWorkers=await page.evaluate(()=>{const d=JSON.parse(document.querySelector('#draft-data').textContent),f=d.formats?.draft||d;return 1+Math.min(f.seats-1,4,Math.max(1,navigator.hardwareConcurrency-2));});
  const workersSettled=async()=>{const until=Date.now()+5000;while(page.workers().length!==activeWorkers&&Date.now()<until)await new Promise(resolve=>setTimeout(resolve,25));assert.equal(page.workers().length,activeWorkers);};await workersSettled();
  await page.evaluate(()=>window.failNextWorkerStep=true);await page.locator('#pack [data-pick]').first().click();await idle();
  assert.deepEqual(await read(),saved);assert.match(await page.locator('#draft-status').innerText(),/Riprendi/);
  assert.equal(await page.locator('#resume').isVisible(),true);await page.locator('#resume').click();await idle();
  await page.locator('#pack [data-pick]').first().click();await idle();assert.equal((await read()).picks.length,2);await workersSettled();
  // Failed persistence must not leave a closed cached session or an orphan worker.
  await page.locator('#reset').click();await page.evaluate(()=>{Storage.prototype.setItem=function(){throw Error('full');};});
  await page.locator('#start').click();await idle();await page.locator('#reset').click();await page.locator('#resume').click();await idle();
  assert.equal(await page.locator('#pool-count').innerText(),'(2)');await workersSettled();
  await context.close();
  const integrity=await browser.newContext();integrity.setDefaultTimeout(180000);await integrity.route('https://**/*',r=>r.abort());
  await integrity.route('**/draft-policy.js?v=*',async route=>{const response=await route.fetch();await route.fulfill({response,body:(await response.text())+'\n// mixed cached bytes\n'});});
  const other=await integrity.newPage();await other.goto(url);await other.evaluate(({key,saved})=>localStorage.setItem(key,JSON.stringify(saved)),{key,saved});await other.reload();
  await other.locator('#policy-version').selectOption('4');await other.locator('#start').click();await other.waitForFunction(()=>!document.querySelector('#start').disabled);
  assert.match(await other.locator('#save-status').innerText(),/diversa dalla pagina/);assert.equal(await other.locator('#policy-version').inputValue(),'3');assert.deepEqual(await other.evaluate(k=>JSON.parse(localStorage.getItem(k)),key),saved);
  await other.locator('#start').click();assert.equal((await other.evaluate(k=>JSON.parse(localStorage.getItem(k)),key)).engineVersion,3);
  await integrity.close();console.log('PASS: dead-worker resume, failed-save worker lifecycle, mixed-code hash rejection preserves original record, classical fallback.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
