'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.MTG_SITE_URL,output=process.env.MTG_QA_DIR;
if(!base||!output)throw Error('Set MTG_SITE_URL and a new MTG_QA_DIR');
fs.mkdirSync(output,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'}),results=[],errors=[];
 try{
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  await context.route('https://**/*',r=>r.abort());
  const page=await context.newPage();page.setDefaultTimeout(60000);page.on('pageerror',e=>errors.push(e.message));
  const prefix=new URL('sets/star-trek/',base).href;
  for(const event of ['draft','picktwo']){
   await page.goto(prefix+'draft-engine.html');
   assert.match(await page.locator('[data-collation-model]').innerText(),/Draftmancer.*stime/s);
   assert.match(await page.locator('.site-set-label').filter({hasText:'Star Trek'}).first().innerText(),/prerelease/i);
   if(event!=='draft'){await page.selectOption('#format',event);await page.waitForURL('**/*?event='+event);}
   await page.selectOption('#policy-version','3');
   await page.locator('#seed').fill('trk-browser-'+event);await page.locator('#start').click();
   const preview=page.locator('#pack .card-ref').first();await preview.hover();await page.locator('#card-hover').waitFor({state:'visible'});
   await page.keyboard.press('Escape');await preview.focus();await page.locator('#card-hover').waitFor({state:'visible'});
   await page.keyboard.press('Enter');await page.locator('#card-dialog').waitFor({state:'visible'});await page.locator('#close-card').click();
   await page.screenshot({path:path.join(output,event+'-desktop.png')});
   const read=()=>page.evaluate(key=>JSON.parse(localStorage.getItem(key)),'mtg-draft-table-trk-v1'+(event==='draft'?'':'-'+event));
   await page.locator('#pack [data-pick]').first().click();
   const first=await read();assert.equal(first.picks.length,1);
   await page.reload();await page.locator('#resume').click();
   assert.equal(await page.locator('#pool-count').innerText(),'('+first.picks.length+')');
   for(let turns=0;turns<42&&await page.locator('#pack [data-pick]').count();turns++)await page.locator('#pack [data-pick]').first().click();
   await page.locator('#review').waitFor({state:'visible'});assert.equal((await read()).picks.length,42);
   await page.selectOption('#review-seat','0');assert.equal(await page.locator('#bot-review .review-pick').count(),42);
   const before=await page.locator('#bot-review').innerText();
   const pending=page.waitForEvent('download');await page.locator('#export').click();const download=await pending;
   const exported=JSON.parse(fs.readFileSync(await download.path(),'utf8'));
   assert.equal(exported.picks.length,42);assert.equal(exported.review.length,event==='draft'?7:3);
   await download.saveAs(path.join(output,event+'-export.json'));
   await page.reload();await page.locator('#resume').click();await page.selectOption('#review-seat','0');
   assert.equal(await page.locator('#bot-review').innerText(),before);
   results.push({event,completed:42,replayIdentical:true,exported:true});
  }
  await page.goto(prefix+'sealed-simulator.html');
  assert.equal(await page.locator('#site-page-label').innerText(),'Simulatore Sealed');
  assert.match(await page.locator('.site-sidebar [data-page="practice"]').getAttribute('href'),/^simulatore\.html$/);
  assert.match(await page.locator('[data-collation-model]').innerText(),/Draftmancer/);
  await page.locator('#all').click();assert.match(await page.locator('#progress').innerText(),/6 di 6 buste.*84 carte/);
  assert.equal(await page.locator('#poolCount').innerText(),'84 carte');
  const sealed=await page.evaluate(()=>localStorage.getItem('trk-sealed-simulator-v1'));
  await page.reload();assert.equal(await page.evaluate(()=>localStorage.getItem('trk-sealed-simulator-v1')),sealed);
  await page.screenshot({path:path.join(output,'sealed-desktop.png')});
  results.push({event:'sealed',cards:84,reloadPreserved:true});
  const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  await mobile.route('https://**/*',r=>r.abort());const phone=await mobile.newPage();phone.on('pageerror',e=>errors.push(e.message));
  await phone.goto(prefix+'draft-engine.html');await phone.locator('#start').tap();
  await phone.locator('#pack .card-ref').first().tap();await phone.locator('#card-dialog').waitFor({state:'visible'});await phone.locator('#close-card').tap();
  assert.ok(await phone.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await phone.screenshot({path:path.join(output,'draft-mobile.png')});
  await phone.locator('#pack [data-pick]').first().tap();assert.equal(await phone.locator('#pool-count').innerText(),'(1)');
  await phone.goto(prefix+'sealed-simulator.html');await phone.locator('#all').tap();assert.match(await phone.locator('#poolCount').innerText(),/84/);
  assert.ok(await phone.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await phone.screenshot({path:path.join(output,'sealed-mobile.png')});
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({results,previews:['mouse','keyboard','touch'],errors},null,2));
  console.log('PASS: TRK Draft, Pick-Two, Sealed, export, reload and previews on desktop/touch.',JSON.stringify(results));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
