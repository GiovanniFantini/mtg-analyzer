// Run against the static build. No application dependencies are installed.
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
const pages=['','sets/reality-fracture/index.html',...['Sealed','Draft','Draft-Engine','Analisi','Combo','Discovery','Simulatore'].map(x=>`sets/reality-fracture/Reality-Fracture-${x}.html`),...['index','catalogo','draft','sealed','simulatore','sinergie','analisi','discovery','regole','fonti'].map(x=>`sets/star-trek/${x}.html`)];
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
 const context=await browser.newContext();
 const page=await context.newPage();
 const errors=[],missing=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.url().startsWith(base)&&r.status()>=400&&!r.url().endsWith('favicon.ico'))missing.push(r.url());});
 const visit=path=>page.goto(base+path,{waitUntil:'domcontentloaded'});
 try{
  for(const width of [320,360,768,1024,1440]){
   await page.setViewportSize({width,height:960});
   for(const path of pages){
    await visit(path);
    await page.locator('#site-content').waitFor();
    const metrics=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth-innerWidth,headings:document.querySelectorAll('h1:not([hidden])').length}));
    assert.ok(metrics.overflow<=1,`${path} overflows at ${width}: ${metrics.overflow}`);
    assert.equal(await page.locator('h1:visible').count(),1,`${path} heading`);
    assert.equal(await page.locator('.site-sidebar [aria-current=page]').count(),1,`${path} active navigation`);
    checks.push({path,width});
   }
  }
  const draft='sets/reality-fracture/Reality-Fracture-Draft-Engine.html';
  const widths=[];
  for(const width of [360,768,1440]){
   await page.setViewportSize({width,height:960});await visit(draft);await page.locator('#start').click();
   let firstWidth;
   for(let pick=0;pick<14;pick++){
    const cards=await page.locator('#pack .draft-card').evaluateAll(cards=>cards.map(c=>({width:c.getBoundingClientRect().width,art:c.querySelector('.art').getBoundingClientRect().height,pick:c.querySelector('.pick').getBoundingClientRect().bottom-c.getBoundingClientRect().top})));
    assert.equal(cards.length,14-pick);
    if(pick===0)firstWidth=cards[0].width;
    assert.ok(cards.every(c=>Math.abs(c.width-firstWidth)<1),`Stable pack columns at ${width}, pick ${pick}`);
    assert.ok(Math.max(...cards.map(c=>c.art))-Math.min(...cards.map(c=>c.art))<1,'Equal art dimensions');
    assert.ok(Math.max(...cards.map(c=>c.pick))-Math.min(...cards.map(c=>c.pick))<1,'Aligned pick buttons');
    await page.locator('[data-pick]').first().click();
   }
   assert.equal(await page.locator('#draft-meter').evaluate(e=>e.value),14);
   await page.reload({waitUntil:'domcontentloaded'});await page.locator('#resume').click();assert.match(await page.locator('#progress').innerText(),/Busta 2\/3/);
   await page.locator('#pack .art').first().click();assert.ok(await page.locator('#card-dialog').isVisible());await page.keyboard.press('Escape');
   for(let pick=14;pick<42;pick++)await page.locator('[data-pick]').first().click();
   assert.equal(await page.locator('#draft-meter').evaluate(e=>e.value),42);assert.ok(await page.locator('#review').isVisible());assert.equal(await page.locator('#review-seat option').count(),7);
   widths.push({width,stableCardWidth:firstWidth,uniformPicksChecked:14,completedPicks:42,review:true});
  }
  await page.emulateMedia({reducedMotion:'reduce'});
  await visit(draft);await page.locator('#start').click();
  assert.equal(await page.locator('.draft-card').first().evaluate(e=>getComputedStyle(e).animationName),'none');
  await page.emulateMedia({reducedMotion:'no-preference'});
  for(const width of [390,1440]){
   await page.setViewportSize({width,height:960});
   for(const [name,path] of [['home',''],['draft',draft],['guida','sets/reality-fracture/Reality-Fracture-Draft.html'],['star-trek','sets/star-trek/index.html']]){
    await visit(path);if(name==='draft')await page.locator('#start').click();
    await page.waitForTimeout(550);
    await page.screenshot({path:`ux-${name}-${width}-preview.png`,fullPage:name==='home'});
   }
  }
  // CSS motion has a static, fully readable fallback when scripting is disabled.
  const noJS=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const staticPage=await noJS.newPage();await staticPage.goto(base,{waitUntil:'domcontentloaded'});
  assert.ok(await staticPage.locator('.site-hero h1').isVisible());
  assert.equal(await staticPage.locator('.site-task').first().evaluate(e=>getComputedStyle(e).opacity),'1');
  await noJS.close();
  assert.deepEqual(errors,[]);assert.deepEqual(missing,[]);
  const result={pages:pages.length,responsiveChecks:checks.length,widths:[320,360,768,1024,1440],draft:widths,reducedMotion:true,staticContentWithoutJS:true,errors,missing};
  fs.writeFileSync('ux-verification.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
