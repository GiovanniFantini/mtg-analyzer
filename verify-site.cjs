const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.MTG_BROWSER_CHANNEL?{channel:process.env.MTG_BROWSER_CHANNEL}:{})});
 const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
 const errors=[];const missing=[];
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400&&!r.url().endsWith('favicon.ico'))missing.push(r.url())});
  await page.goto(base,{waitUntil:'domcontentloaded'});assert.equal(await page.title(),'MTG Analyzer · Espansioni, Limited e metagame');
  await page.locator('#set-search').fill('inesistente');assert.equal(await page.locator('.set:visible').count(),0);assert.ok(await page.locator('#empty').isVisible());await page.locator('#set-search').fill('FRA');await page.getByRole('link',{name:'Esplora il set'}).click();
  await page.locator('.workspace-nav').waitFor();assert.match(page.url(),/sets\/reality-fracture\/index.html/);
  for(const id of ['draft','analysis','combos','simulator','discovery']){
   await page.locator(`.workspace-nav a[href="#${id}"]`).click();await page.frameLocator(`#${id} iframe`).locator('main').waitFor();
  }
  const f=page.frameLocator('#discovery iframe');await f.locator('.candidate').last().waitFor();assert.equal(await f.locator('.candidate').count(),17);await f.getByRole('button',{name:'Modern',exact:true}).click();await f.locator('#level').selectOption('Confermata');assert.equal(await f.locator('.candidate').count(),5);await f.locator('#search').fill('Nethergoyf');assert.equal(await f.locator('.candidate').count(),1);await f.locator('.save').click();await f.locator('#reset').click();await f.locator('#saved').check();assert.equal(await f.locator('.candidate').count(),1);
  await f.locator('#reset').click();const card=f.locator('h3 [data-card-preview="Dark Matter Manipulator"]').first();await card.hover();await f.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');await card.focus();await f.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  assert.ok(!(await page.locator('body').innerText()).includes('WhatsApp'));assert.equal(await page.locator('#portable-share').count(),0);
  await page.screenshot({path:'site-desktop-preview.png'});
  const mobile=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true});mobile.on('pageerror',e=>errors.push(e.message));await mobile.goto(base,{waitUntil:'domcontentloaded'});assert.ok(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await mobile.screenshot({path:'site-home-mobile-preview.png'});await mobile.getByRole('link',{name:'Discovery meta',exact:true}).click();const mf=mobile.frameLocator('#discovery iframe');await mf.locator('.candidate').last().waitFor();assert.equal(await mf.locator('.candidate').count(),17);assert.ok(await mobile.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.ok(await mf.locator('html').evaluate(e=>e.scrollWidth<=innerWidth+1));await mf.locator('h3 [data-card-preview="Dark Matter Manipulator"]').first().tap();await mf.locator('#mtg-card-preview').waitFor({state:'visible'});
  assert.deepEqual(errors,[]);assert.deepEqual(missing,[]);const result={homepage:true,expansionRouting:true,sections:5,discoveryCards:17,filters:true,watchlist:true,previews:['hover','keyboard','touch'],mobileOverflow:false,obsoleteShareUI:false,errors,missing};fs.writeFileSync('site-verification.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
