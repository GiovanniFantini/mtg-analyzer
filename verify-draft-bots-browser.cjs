'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8871/';
const fixture=JSON.parse(fs.readFileSync('tests/fixtures/draft-bots-v2.json','utf8')).cases[1].record;
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.MTG_BROWSER_CHANNEL?{channel:process.env.MTG_BROWSER_CHANNEL}:{})});
 try{
  const context=await browser.newContext(),page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  // Images are irrelevant to these UI checks; keep the test independent of the network.
  await context.route('https://**/*',route=>route.abort());
  const url=base+'sets/reality-fracture/Reality-Fracture-Draft-Engine.html';
  await page.goto(url);
  await page.evaluate(record=>localStorage.setItem('mtg-draft-table-fra-v1',JSON.stringify(record)),fixture);
  await page.reload();await page.locator('#resume').click();
  assert.equal(await page.locator('#draft-meter').getAttribute('value'),String(fixture.picks.length));
  await page.locator('#pack [data-pick]').first().click();
  const readSave=()=>page.evaluate(()=>JSON.parse(localStorage.getItem('mtg-draft-table-fra-v1')));
  const continued=await readSave();assert.equal(continued.engineVersion,2);assert.equal(continued.picks.length,20);
  await page.reload();await page.locator('#resume').click();assert.equal(await page.locator('#pool-count').innerText(),'(20)');
  await page.locator('#reset').click();await page.locator('#seed').fill('bots-v3-browser');await page.locator('#start').click();
  assert.equal((await readSave()).engineVersion,3);
  const preview=page.locator('#pack .card-ref').first();
  await preview.hover();await page.locator('#card-hover').waitFor({state:'visible'});
  await page.keyboard.press('Escape');await preview.focus();await page.locator('#card-hover').waitFor({state:'visible'});
  await page.keyboard.press('Enter');await page.locator('#card-dialog').waitFor({state:'visible'});await page.locator('#close-card').click();
  for(let i=0;i<42;i++)await page.locator('#pack [data-pick]').first().click();
  await page.locator('#review').waitFor({state:'visible'});assert.equal(await page.locator('#bot-review .review-pick').count(),42);
  const completed=await readSave();assert.equal(completed.engineVersion,3);assert.equal(completed.picks.length,42);
  const before=await page.locator('#bot-review').innerText();
  await page.reload();await page.locator('#resume').click();assert.equal(await page.locator('#bot-review').innerText(),before);
  const downloadPromise=page.waitForEvent('download');await page.locator('#export').click();const download=await downloadPromise;
  const exported=JSON.parse(fs.readFileSync(await download.path(),'utf8'));
  assert.equal(exported.engineVersion,3);assert.equal(exported.review.length,7);
  const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  await mobile.route('https://**/*',route=>route.abort());
  const phone=await mobile.newPage();phone.on('pageerror',e=>errors.push(e.message));await phone.goto(url);await phone.locator('#start').tap();
  await phone.locator('#pack .card-ref').first().tap();await phone.locator('#card-dialog').waitFor({state:'visible'});await phone.locator('#close-card').tap();
  assert.ok(await phone.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  assert.deepEqual(errors,[]);
  console.log('PASS: v2 saved draft resumes and stays v2; new v3 draft completes, reloads and exports identical review; mouse, keyboard and touch card previews; no browser errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
