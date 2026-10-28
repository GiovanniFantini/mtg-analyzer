'use strict';
const assert=require('node:assert/strict');
const path=require('node:path');
const fs=require('node:fs');
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const base=process.env.MTG_SITE_URL;if(!base)throw Error('Set MTG_SITE_URL');
const directory=process.env.MTG_QA_DIR||require('node:os').tmpdir();
fs.mkdirSync(directory,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
 const errors=[];
 try{
  for(const mobile of [false,true]){
   const context=await browser.newContext({viewport:{width:mobile?390:1440,height:1000},hasTouch:mobile,isMobile:mobile,reducedMotion:'reduce'});
   const page=await context.newPage();page.on('pageerror',e=>{errors.push(e.message);console.error('Page error:',e.message);});
   await page.goto(new URL('sets/reality-fracture/Reality-Fracture-Draft.html#assistant',base).href);
   await page.waitForFunction(()=>window.DraftPool&&window.DraftAdvisor);
   await page.evaluate(async()=>{
    await DraftPool.setPlan('WB');
    for(const [name,quantity]of Object.entries({'Unflinching Hortimancer':2,'Eye of Jace':1,'Break Under Pressure':2,'Surgical Precision':1}))await DraftPool.change(name,quantity);
   });
   const panel=page.locator('#da-analysis');
   await panel.locator('summary').click();
   assert.match(await panel.innerText(),/Vite che sviluppano il campo/);
   assert.match(await panel.innerText(),/2 × Unflinching Hortimancer/);
   assert.match(await panel.innerText(),/non di una lista finale/);
   assert.match(await panel.innerText(),/Quick, Premier e Traditional/);
   assert.match(await page.locator('#dp-prompt').inputValue(),/pedine future, magie preparate e recuperi/);
   assert.match(await page.locator('#dp-prompt').inputValue(),/singola run non dimostra/);
   // Use the same preview overlay contract as the existing workspace checks.
   const card=panel.locator('[data-card-preview="Unflinching Hortimancer"]').first();
   if(mobile){await card.tap();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');}
   else{
    await card.hover();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
    await page.mouse.move(0,0);await card.focus();await page.locator('#mtg-card-preview').waitFor({state:'visible'});
    await page.keyboard.press('Escape');
   }
   const changed=await page.evaluate(async()=>{const results=[await DraftPool.setPlan('UR')];for(const [name,n]of Object.entries({'Craftwork Crusher':1,'Undulating Witness':2,'Kiora of Salt and Sand':2,"Tam's Resistance":1}))results.push(await DraftPool.change(name,n));return {results,plan:DraftPool.getPlan(),pool:DraftPool.get()};});
   assert(changed.results.every(Boolean),JSON.stringify(changed));
   assert(await panel.isVisible(),'Analysis remains available when the plan excludes several picks');
   assert(await panel.evaluate(e=>e.open),'Pool updates preserve the open panel');
   assert.match(await panel.innerText(),/Craftwork Crusher.*\{G\}\{G\}/);
   assert.match(await panel.innerText(),/2 × Undulating Witness/);
   const snapshot=await page.evaluate(()=>localStorage.getItem(EXPANSION_CONFIG.storage.draftPool));
   await panel.locator('summary').click();await panel.locator('summary').click();
   assert.equal(await page.evaluate(()=>localStorage.getItem(EXPANSION_CONFIG.storage.draftPool)),snapshot,'Opening analysis never changes saved picks');
   for(const width of mobile?[320,390]:[768,1440]){
    await page.setViewportSize({width,height:1000});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`No overflow at ${width}`);
   }
   await panel.scrollIntoViewIfNeeded();await page.screenshot({path:path.join(directory,`pool-analysis-${mobile?'mobile':'desktop'}.png`),fullPage:true});
   await context.close();
  }
  assert.deepEqual(errors,[]);console.log('Pool analysis browser: dynamic evidence, desktop/mobile, previews, layout and persistence verified.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
