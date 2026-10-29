'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.MTG_BROWSER_CHANNEL?{channel:process.env.MTG_BROWSER_CHANNEL}:{})});
 try{
  const context=await browser.newContext(),page=await context.newPage(),errors=[];
  await context.route('https://**/*',r=>r.abort());page.on('pageerror',e=>errors.push(e.message));
  await context.addInitScript(()=>{Storage.prototype.getItem=function(){throw new DOMException('Blocked','SecurityError');};const OriginalWorker=Worker;window.Worker=class extends OriginalWorker{constructor(...args){super(...args);window.mainDraftWorker=this;}};});
  const settled=n=>page.waitForFunction(n=>document.querySelector('#pool-count').textContent===`(${n})`&&!document.querySelector('#start').disabled,n);
  await page.goto(base+'sets/reality-fracture/Reality-Fracture-Draft-Engine.html');
  await page.locator('#start').click();await page.locator('#pack [data-pick]').first().click();await page.locator('#reset').click();
  assert.equal(await page.locator('#resume').isVisible(),true);assert.equal(await page.locator('#export-memory').isVisible(),true);
  let pending=page.waitForEvent('download');await page.locator('#export-memory').click();
  assert.equal(JSON.parse(fs.readFileSync(await (await pending).path(),'utf8')).picks.length,1);
  await page.locator('#resume').click();assert.equal(await page.locator('#pool-count').innerText(),'(1)');await page.locator('#reset').click();
  await page.locator('#policy-version').selectOption('4');
  for(const select of await page.locator('[data-strategy]').all())await select.selectOption('power');
  await page.locator('#start').click();await settled(0);await page.locator('#pack [data-pick]').first().click();await settled(1);
  await page.evaluate(()=>window.mainDraftWorker.onerror(new Event('error')));
  await page.locator('#pack [data-pick]').first().click();
  await page.locator('#setup').waitFor({state:'visible'});await page.waitForFunction(()=>!document.querySelector('#resume').disabled);
  assert.equal(await page.locator('#export-memory').isVisible(),true);
  pending=page.waitForEvent('download');await page.locator('#export-memory').click();
  const record=JSON.parse(fs.readFileSync(await (await pending).path(),'utf8'));assert.equal(record.engineVersion,4);assert.equal(record.picks.length,1);
  await page.locator('#resume').click();await settled(1);
  await page.locator('#pack [data-pick]').first().click();await settled(2);
  assert.deepEqual(errors,[]);
  console.log('PASS: blocked storage retains classic memory session after reset; setup export downloads exact progress; failed v4 worker retains downloadable snapshot and resumes that snapshot without storage.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
