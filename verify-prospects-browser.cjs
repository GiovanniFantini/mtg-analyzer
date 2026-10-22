'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const base=(process.env.MTG_SITE_URL||'http://127.0.0.1:8896/').replace(/\/$/,'')+'/sets/reality-fracture/';
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.MTG_BROWSER_CHANNEL?{channel:process.env.MTG_BROWSER_CHANNEL}:{})});
 const errors=[];
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'Reality-Fracture-Discovery.html');
  await page.locator('.candidate').last().waitFor();assert.equal(await page.locator('.candidate').count(),17);
  await page.locator('#research-view').selectOption('all');
  await page.locator('#research-status').filter({hasText:'382 analisi'}).waitFor();
  assert.equal(await page.locator('.candidate').count(),24);
  await page.locator('#research-more').click();assert.equal(await page.locator('.candidate').count(),48);
  for(const [product,count]of [['FRA',285],['SPG',10],['FRC',87]]){
   await page.locator('#product').selectOption(product);assert.match(await page.locator('#count').innerText(),new RegExp('^'+count+' di 382'));
  }
  await page.locator('#product').selectOption('');await page.locator('#search').fill('Academic Ascent');
  assert.equal(await page.locator('.candidate').count(),1);
  await page.locator('[data-prospect] > summary').click();
  await page.locator('.card-prospects').waitFor();
  assert.match(await page.locator('.card-prospects').innerText(),/Dati insufficienti/);
  assert.equal(await page.locator('.prospect-price-grid > div').count(),3);
  await page.locator('.prospect-sources > summary').click();assert.ok(await page.locator('.prospect-sources a').count()>1);
  await page.screenshot({path:'research/reality-fracture-20261022/prospects-desktop.png'});
  await page.goto(base+'Reality-Fracture-Discovery.html?view=all&format=Vintage&product=FRC');
  await page.locator('#research-status').filter({hasText:'382 analisi'}).waitFor();
  await page.waitForFunction(()=>document.querySelector('#product').value==='FRC');
  assert.equal(await page.locator('[data-format="Vintage"]').getAttribute('aria-pressed'),'true');
  await page.locator('#reset').click();await page.locator('#search').fill('Arcane Signet');
  await page.locator('#research-status').click();
  const preview=page.locator('h3 [data-card-preview="Arcane Signet"]');
  await preview.hover();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  await preview.focus();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  await page.goto(base+'Reality-Fracture-Sealed.html');await page.locator('#search').fill('Academic Ascent');
  await page.getByRole('button',{name:'Analisi, prezzi e fonti',exact:true}).click();
  await page.locator('#zoom .card-prospects').waitFor();assert.equal(await page.evaluate(()=>DATA.cards.length),295);
  assert.ok(await page.locator('#zoom .prospect-sources a').count()>1);
  const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});mobile.on('pageerror',e=>errors.push(e.message));
  await mobile.goto(base+'Reality-Fracture-Discovery.html?view=all&q=Arcane+Signet');
  await mobile.locator('#research-status').filter({hasText:'382 analisi'}).waitFor();
  await mobile.locator('h3 [data-card-preview="Arcane Signet"]').tap();await mobile.locator('#mtg-card-preview').waitFor({state:'visible'});
  await mobile.keyboard.press('Escape');await mobile.locator('[data-prospect] > summary').click();await mobile.locator('.card-prospects').waitFor();
  assert.ok(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await mobile.screenshot({path:'research/reality-fracture-20261022/prospects-mobile.png'});
  await mobile.goto(base+'Reality-Fracture-Sealed.html');await mobile.locator('#search').fill('Academic Ascent');
  await mobile.getByRole('button',{name:'Analisi, prezzi e fonti',exact:true}).click();await mobile.locator('#zoom .card-prospects').waitFor();
  assert.ok(await mobile.locator('#zoom').evaluate(e=>e.scrollWidth<=e.clientWidth+1));
  const fallback=await browser.newPage();fallback.on('pageerror',e=>errors.push(e.message));
  await fallback.route('**/prospects-commander-*.json',route=>route.abort());
  await fallback.goto(base+'Reality-Fracture-Discovery.html?view=all');
  await fallback.locator('#research-status').filter({hasText:'295 analisi'}).waitFor();
  assert.match(await fallback.locator('#research-status').innerText(),/appendice Commander non è disponibile/);
  assert.deepEqual(errors,[]);
  console.log('OK: 382 analyses; filters, pagination, format deep links, catalog, hover/keyboard/touch, mobile layout, appendix failure.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
