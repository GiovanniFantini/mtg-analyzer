const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'chrome'});
 const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
 const set=base+'sets/reality-fracture/';
 const errors=[],missing=[],checked=[];
 const context=await browser.newContext();
 const page=await context.newPage();
 page.on('pageerror',e=>errors.push({url:page.url(),message:e.message}));
 page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400&&!r.url().endsWith('favicon.ico'))missing.push(r.url())});
 const pages=['','sets/reality-fracture/index.html',...['Sealed','Draft','Analisi','Combo','Discovery','Simulatore'].map(s=>'sets/reality-fracture/Reality-Fracture-'+s+'.html')];
 try{
  for(const width of [360,768,1440]){
   await page.setViewportSize({width,height:960});
   for(const path of pages){
    await page.goto(base+path,{waitUntil:'domcontentloaded'});
    await page.locator('#site-content').waitFor();
    assert.equal(await page.locator('iframe').count(),0,'No nested browsing areas');
    assert.equal(await page.locator('h1:visible').count(),1,'One visible page heading: '+path);
    const overflow=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
    assert.ok(overflow.scroll<=overflow.width+1,JSON.stringify({path,...overflow}));
    assert.equal(await page.locator('.site-sidebar [aria-current=page]').count(),1,'One active menu entry: '+path);
    checked.push({path,width});
   }
  }
  await page.goto(base);await page.locator('#set-search').fill('inesistente');assert.equal(await page.locator('.set:visible').count(),0);assert.ok(await page.locator('#empty').isVisible());await page.locator('#set-search').fill('FRA');assert.equal(await page.locator('.set:visible').count(),1);
  await page.screenshot({path:'layout-home-desktop-preview.png',fullPage:true});
  await page.goto(set+'Reality-Fracture-Sealed.html#gallery');
  await page.locator('#cards .card').first().waitFor();assert.equal(await page.locator('#cards .card').count(),24);
  const plus=page.locator('#cards [data-delta="1"]').first();const cardId=await plus.getAttribute('data-id');await plus.click();assert.equal(await page.evaluate(id=>JSON.parse(localStorage.getItem('fra-sealed-pool-v1'))[id],cardId),1);
  await page.locator('.site-sidebar [data-page=pool]').click();assert.ok(await page.locator('#pool').isVisible());assert.ok(!(await page.locator('#gallery').isVisible()));assert.match(await page.locator('#poolcount').innerText(),/1 copia/);
  await page.locator('#poolfilter').click();assert.ok(await page.locator('#gallery').isVisible());assert.equal(await page.locator('#cards .card').count(),1);
  await page.goto(set+'Reality-Fracture-Draft.html');assert.equal(await page.locator('#draft-pool').count(),1);await page.locator('.site-local-nav a[href="#draft-drilldown"]').click();assert.ok(await page.locator('#draft-drilldown').isVisible());
  await page.goto(set+'Reality-Fracture-Discovery.html');await page.locator('.candidate').last().waitFor();assert.equal(await page.locator('.candidate').count(),17);await page.getByRole('button',{name:'Modern',exact:true}).click();await page.locator('#level').selectOption('Confermata');assert.equal(await page.locator('.candidate').count(),5);await page.locator('#search').fill('Nethergoyf');assert.equal(await page.locator('.candidate').count(),1);await page.locator('.save').click();await page.locator('#reset').click();await page.locator('#saved').check();assert.equal(await page.locator('.candidate').count(),1);await page.locator('#reset').click();
  const card=page.locator('h3 [data-card-preview="Dark Matter Manipulator"]').first();await card.hover();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');await card.focus();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  await page.goto(set+'Reality-Fracture-Simulatore.html');await page.locator('#all').click();assert.match(await page.locator('#progress').innerText(),/6/);
  await page.goto(set+'index.html#draft');await page.waitForURL(/Reality-Fracture-Draft\.html/);await page.goto(set+'Reality-Fracture-Sealed.html#discovery');await page.waitForURL(/Reality-Fracture-Discovery\.html/);
  const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const m=await mobile.newPage();m.on('pageerror',e=>errors.push({mobile:true,message:e.message}));await m.goto(base);await m.screenshot({path:'layout-home-mobile-preview.png',fullPage:true});assert.ok(await m.locator('.site-sidebar').evaluate(e=>e.inert));await m.getByRole('button',{name:'☰ Menu'}).tap();assert.equal(await m.locator('.site-menu-toggle').getAttribute('aria-expanded'),'true');await m.keyboard.press('Escape');assert.equal(await m.locator('.site-menu-toggle').getAttribute('aria-expanded'),'false');assert.equal(await m.evaluate(()=>document.activeElement.className),'site-menu-toggle');await m.locator('.site-menu-toggle').tap();await m.waitForFunction(()=>document.querySelector('.site-sidebar').getBoundingClientRect().left>=0);await m.screenshot({path:'layout-menu-mobile-preview.png'});await m.locator('.site-sidebar [data-page=discovery]').tap();await m.waitForURL(/Discovery/);assert.equal(await m.locator('.site-menu-toggle').getAttribute('aria-expanded'),'false');await m.locator('h3 [data-card-preview="Dark Matter Manipulator"]').first().tap();await m.locator('#mtg-card-preview').waitFor({state:'visible'});await m.keyboard.press('Escape');await m.screenshot({path:'layout-discovery-mobile-preview.png'});
  await m.goto(set+'Reality-Fracture-Sealed.html#pool');await m.locator('.site-menu-toggle').tap();await m.locator('.site-sidebar [data-page=gallery]').tap();assert.ok(await m.locator('#gallery').isVisible());assert.equal(await m.locator('.site-menu-toggle').getAttribute('aria-expanded'),'false');await m.waitForFunction(()=>document.querySelector('.site-sidebar').getBoundingClientRect().right<=0);await m.screenshot({path:'layout-catalog-mobile-preview.png'});assert.equal(await m.locator('.site-catalog-filters').getAttribute('open'),null);await m.locator('.site-catalog-filters summary').tap();await m.locator('[data-color=W]').tap();assert.equal(await m.locator('[data-color=W]').getAttribute('aria-pressed'),'true');assert.ok(Number((await m.locator('#count').innerText()).split(' / ')[0])<295);await m.locator('#reset').tap();assert.match(await m.locator('#count').innerText(),/^295 \/ 295/);
  assert.deepEqual(errors,[]);assert.deepEqual(missing,[]);
  const result={responsiveChecks:checked.length,widths:[360,768,1440],pages:8,nestedFrames:0,mobileMenu:true,mobileAdvancedFilters:true,keyboard:true,poolPersistence:true,draftLinks:true,discoveryFilters:true,watchlist:true,cardPreviews:['hover','keyboard','touch'],legacyBookmarks:true,errors,missing};fs.writeFileSync('site-verification.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
