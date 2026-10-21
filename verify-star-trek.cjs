const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'C:/Users/mimir/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8871/';
const set=base+'sets/star-trek/';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
 const errors=[],missing=[],checks=[];
 const context=await browser.newContext();context.setDefaultTimeout(15000);const page=await context.newPage();
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400&&!r.url().endsWith('favicon.ico'))missing.push(r.url())});
 try{
  const paths=['index','catalogo','draft','sealed','simulatore','sinergie','analisi','discovery','regole','fonti'];
  for(const width of [360,768,1440]){
   await page.setViewportSize({width,height:960});
   for(const path of paths){
    await page.goto(set+path+'.html');
    assert.equal(await page.locator('h1:visible').count(),1,path+' heading');
    assert.equal(await page.locator('.site-sidebar [aria-current=page]').count(),1,path+' current menu');
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
    assert.ok(overflow<=1,path+' overflow at '+width+': '+overflow);
    const wrongLinks=await page.locator('.site-sidebar [data-page]').evaluateAll(nodes=>nodes.filter(n=>n.href.includes('Reality-Fracture')).length);
    assert.equal(wrongLinks,0);checks.push({path,width});
   }
  }
  await page.goto(base);assert.equal(await page.locator('[data-set]').count(),2);await page.locator('#set-search').fill('TRK');assert.equal(await page.locator('[data-set]:visible').count(),1);
  await page.goto(set+'catalogo.html');assert.equal(await page.locator('#trk-cards>.trk-card').count(),12);
  await page.locator('#trk-search').fill('Open Communications');assert.equal(await page.locator('#trk-cards>.trk-card').count(),1);
  const preview=page.locator('#trk-cards h3 [data-card-preview]').first();await preview.hover();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');await preview.focus();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  await page.locator('#trk-search').fill('Open Communications');
  const id=await page.locator('#trk-cards [data-op=pool-plus]').getAttribute('data-id');
  for(let i=0;i<5;i++)await page.locator('#trk-cards [data-op=pool-plus]').click();
  assert.equal(await page.evaluate(id=>JSON.parse(localStorage.getItem('mtg-trk-sealed-v1')).pool[id],id),5,'Limited permits >4 copies');
  for(let i=0;i<5;i++)await page.locator('#trk-cards [data-op=deck-plus]').click();
  assert.ok(await page.locator('#trk-cards [data-op=deck-plus]').isDisabled());
  await page.locator('#trk-cards [data-op=pool-minus]').click();
  assert.equal(await page.evaluate(id=>JSON.parse(localStorage.getItem('mtg-trk-sealed-v1')).deck[id],id),4,'Reducing pool clamps deck');
  await page.locator('#trk-mode').selectOption('draft');assert.ok(await page.locator('#trk-cards [data-op=pool-minus]').isDisabled(),'Separate draft pool');
  await page.locator('#trk-cards [data-op=pool-plus]').click();
  assert.equal(await page.evaluate(id=>JSON.parse(localStorage.getItem('mtg-trk-sealed-v1')).pool[id],id),4);
  await page.goto(set+'sealed.html');assert.match(await page.locator('#trk-deck-status').innerText(),/Pool: 4 copie/);
  await page.locator('[data-basic]').first().fill('36');await page.locator('[data-basic]').first().dispatchEvent('change');assert.match(await page.locator('#trk-deck-status').innerText(),/Mazzo: 40 carte/);
  const exported=page.waitForEvent('download');await page.locator('#trk-export').click();const download=await exported;assert.match(download.suggestedFilename(),/star-trek-sealed/);
  const good={version:1,set:'TRK',mode:'sealed',pool:{[id]:5},deck:{[id]:5},basics:{}};
  await page.locator('#trk-import').setInputFiles({name:'invalid.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({...good,mode:'draft'}))});
  assert.match(await page.locator('#trk-storage-status').innerText(),/non eseguita/);assert.match(await page.locator('#trk-deck-status').innerText(),/Mazzo: 40/);
  await page.locator('#trk-import').setInputFiles({name:'invalid.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({...good,deck:{[id]:6}}))});assert.match(await page.locator('#trk-storage-status').innerText(),/supera/);
  const snapshot=await page.evaluate(()=>JSON.parse(localStorage.getItem('mtg-trk-sealed-v1')));
  await page.locator('#trk-import').setInputFiles({name:'good.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({version:1,set:'TRK',mode:'sealed',...snapshot}))});assert.match(await page.locator('#trk-storage-status').innerText(),/importati/);
  await page.goto(set+'simulatore.html');await page.locator('#trk-new-hand').click();assert.equal(await page.locator('#trk-hand .trk-card').count(),7);
  await page.locator('#trk-mulligan').click();assert.ok(await page.locator('#trk-keep').isDisabled());await page.locator('[data-bottom]').first().click();await page.locator('#trk-keep').click();assert.equal(await page.locator('#trk-hand .trk-card').count(),6);await page.locator('#trk-draw').click();assert.equal(await page.locator('#trk-hand .trk-card').count(),7);
  await page.locator('#trk-mode').selectOption('picktwo');assert.ok(await page.locator('#trk-new-hand').isDisabled());assert.equal(await page.locator('#trk-hand .trk-card').count(),0);
  await page.goto(set+'draft.html');assert.equal(await page.locator('#trk-compare>.trk-card').count(),2);assert.equal(await page.locator('#trk-mode').inputValue(),'draft');
  await page.goto(set+'discovery.html');await page.locator('#trk-set').selectOption('SDS');assert.equal(await page.locator('#trk-cards>.trk-card').count(),5);await page.locator('#trk-cards [data-op=watch]').first().click();assert.equal(await page.locator('#trk-cards [data-op=watch]').first().getAttribute('aria-pressed'),'true');
  await page.goto(set+'sinergie.html');assert.ok(await page.locator('[data-card-preview="Open Communications"]').count()>0);assert.ok(await page.locator('[data-card-preview="Seven of Nine"]').count()>0);
  await page.goto(set+'index.html');await page.screenshot({path:'star-trek-desktop-preview.png',fullPage:true});
  console.log('Controlli desktop e pool superati; verifica touch.');
  const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});mobile.setDefaultTimeout(15000);const m=await mobile.newPage();m.on('pageerror',e=>errors.push(e.message));
  await m.goto(set+'catalogo.html');assert.ok(await m.locator('.site-sidebar').evaluate(e=>e.inert));await m.locator('#trk-search').fill('Open Communications');await m.locator('#trk-cards h3 [data-card-preview]').scrollIntoViewIfNeeded();await m.locator('#trk-cards h3 [data-card-preview]').tap();await m.locator('#mtg-card-preview').waitFor({state:'visible'});await m.keyboard.press('Escape');
  await m.locator('.site-menu-toggle').tap();await m.waitForFunction(()=>document.querySelector('.site-sidebar').getBoundingClientRect().left>=0);await m.locator('.site-sidebar [data-page=rules]').tap();await m.waitForURL(/regole.html/);assert.equal(await m.locator('.site-menu-toggle').getAttribute('aria-expanded'),'false');
  await m.screenshot({path:'star-trek-mobile-preview.png',fullPage:true});
  // Legacy FRA smoke check: both set contexts and persisted data remain independent.
  await page.goto(base+'sets/reality-fracture/Reality-Fracture-Sealed.html#gallery');await page.locator('#cards .card').first().waitFor();assert.equal(await page.locator('#cards .card').count(),24);assert.equal(await page.evaluate(()=>localStorage.getItem('fra-sealed-pool-v1')),null);
  assert.deepEqual(errors,[]);assert.deepEqual(missing,[]);
  fs.writeFileSync('star-trek-verification.json',JSON.stringify({responsive:checks,previews:['hover','focus','touch'],poolIsolation:true,quantityConstraints:true,atomicImport:true,export:true,londonMulligan:true,mobileMenu:true,legacyFRA:true,errors,missing},null,2));
  console.log('Star Trek: 30 controlli responsive e flussi interattivi superati. Nessun errore JavaScript o asset locale mancante.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
