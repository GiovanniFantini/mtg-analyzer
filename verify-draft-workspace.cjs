'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.MTG_PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.MTG_SITE_URL;
if (!base) throw Error('Set MTG_SITE_URL');
const url = new URL('sets/reality-fracture/Reality-Fracture-Draft.html', base).href;
const screenshotDir = process.env.MTG_QA_DIR || require('node:os').tmpdir();
const views = {assistant:'#draft-assistant', guide:'[data-draft-panel="guide"]', pool:'#draft-pool', data:'[data-draft-panel="data"]'};
async function readable(page, selector, pseudo = null) {
 const ratios = await page.locator(selector).evaluateAll((nodes, pseudo) => {
  const rgb = value => (value.match(/[\d.]+/g) || []).slice(0,3).map(Number);
  const luminance = color => rgb(color).map(v => v/255).map(v => v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
  return nodes.map(node => {
   let bg = node;
   while(bg.parentElement && getComputedStyle(bg).backgroundColor === 'rgba(0, 0, 0, 0)') bg=bg.parentElement;
   const a=luminance(getComputedStyle(node,pseudo).color),b=luminance(getComputedStyle(bg).backgroundColor);
   return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
  });
 },pseudo);
 assert(ratios.length>0 && ratios.every(r=>r>=4.5),`${selector}: text contrast ${ratios}`);
}
async function unobscured(page, selector) {
 await page.waitForFunction(selector => {
  const node=document.querySelector(selector);if(!node)return false;
  const r=node.getBoundingClientRect(),nav=document.querySelector('.draft-workspace-nav'),n=nav.getBoundingClientRect();
  const edge=Math.max(document.querySelector('.site-bar').getBoundingClientRect().bottom,getComputedStyle(nav).position==='sticky'?n.bottom:0);
  return r.top>=edge-1 && r.bottom<=innerHeight+1;
 },selector);
 const rect = await page.locator(selector).evaluate(node => {
  const r=node.getBoundingClientRect(),nav=document.querySelector('.draft-workspace-nav'),n=nav.getBoundingClientRect();
  const edge=Math.max(document.querySelector('.site-bar').getBoundingClientRect().bottom,getComputedStyle(nav).position==='sticky'?n.bottom:0);
  return {top:r.top,bottom:r.bottom,edge,height:innerHeight};
 });
 assert(rect.top>=rect.edge-1 && rect.bottom<=rect.height+1,`${selector}: obscured ${JSON.stringify(rect)}`);
}
(async () => {
 const browser = await chromium.launch({headless:true, channel:process.env.MTG_BROWSER_CHANNEL || 'msedge'});
 const errors = [], missing = [], checks = [];
 try {
  const context = await browser.newContext({reducedMotion:'reduce'});
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  page.on('response', r => {if(r.url().startsWith(base) && r.status() >= 400) missing.push(r.url());});
  await page.goto(url);
  assert.equal(await page.locator('#da-results .da-card').count(), 0);
  assert(await page.locator('[data-da-browse]').isVisible());
  await readable(page,'#da-search','::placeholder');
  await page.emulateMedia({forcedColors:'active'});
  assert.match(await page.locator('.draft-workspace-nav [aria-current]').evaluate(e=>getComputedStyle(e).textDecorationLine),/underline/);
  assert.equal(await page.locator('.draft-workspace-nav [aria-current]').evaluate(e=>getComputedStyle(e).outlineStyle),'solid');
  const unfocusedOutline=await page.locator('.draft-workspace-nav [aria-current]').evaluate(e=>getComputedStyle(e).outlineOffset);
  await page.locator('.draft-workspace-nav [aria-current]').focus();
  assert(await page.locator('.draft-workspace-nav [aria-current]').evaluate(e=>e.matches(':focus-visible')));
  assert.notEqual(await page.locator('.draft-workspace-nav [aria-current]').evaluate(e=>getComputedStyle(e).outlineOffset),unfocusedOutline,'High contrast distinguishes keyboard focus from current view');
  await page.emulateMedia({forcedColors:'none'});
  for (const width of [320,360,390,768,1024,1440]) {
   await page.setViewportSize({width,height:960});
   for (const [view, selector] of Object.entries(views)) {
    await page.locator(`[data-draft-view="${view}"]`).click();
    assert(await page.locator(selector).isVisible());
    assert.equal(await page.locator('.draft-workspace-nav [aria-current="location"]').getAttribute('data-draft-view'),view);
    for (const [other, region] of Object.entries(views)) if(other !== view) assert(!await page.locator(region).isVisible());
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth+1),`${view}: overflow at ${width}`);
    assert.equal(await page.locator('h1:visible').count(),1);
    assert.equal(await page.locator('.site-sidebar [aria-current="page"]').count(),1);
    if(width<=700 && view!=='assistant'){
     const section=view==='pool'?page.locator(selector):page.locator(selector+' .report-section').first();
     assert(parseFloat(await section.evaluate(e=>getComputedStyle(e).paddingLeft))<=18,'Mobile report padding stays compact');
    }
    const nav = await page.locator('.draft-workspace-nav').boundingBox();
    assert(nav.y >= 60 && nav.y+nav.height < 300,'Activity navigation remains reachable');
    if(width === 390 || width === 1440) await page.screenshot({path:path.join(screenshotDir,`draft-workspace-${view}-${width}.png`)});
    checks.push({view,width});
   }
  }
  await page.locator('[data-draft-view="assistant"]').click();
  await page.locator('#da-search').fill('Surveillance');
  const card = page.locator('#da-results [data-name]').first();
  await card.hover();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  await page.locator('#da-search').fill('Surveillance');
  await card.focus();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  await page.locator('#da-results [data-da-pick]').click();
  await page.waitForFunction(() => DraftPool.get()['Surveillance Phantasm'] === 1);
  await page.locator('[data-draft-view="pool"]').click();
  assert.match(await page.locator('#dp-pool').innerText(),/Surveillance Phantasm/);
  await page.locator('#dp-notes').fill('Verifica nuova navigazione');
  await page.locator('[data-draft-view="assistant"]').click();
  assert.equal(await page.locator('#da-search').inputValue(),'Surveillance','Search survives view changes');
  await page.locator('[data-da-tab="compare"]').click();
  for(const term of ['Surveillance','Mindseeker']){
   await page.locator('#da-search').fill(term);await page.locator('#da-results [data-da-compare]').click();
  }
  await readable(page,'#da-selected .da-name');
  await unobscured(page,'#da-comparison .da-verdict');
  await page.locator('#da-comparison [data-da-pick]').first().click();
  await page.waitForFunction(()=>document.getElementById('da-undo'));
  await unobscured(page,'#da-status');
  await page.locator('#da-pool-details').evaluate(e=>e.open=true);await readable(page,'#da-pool .da-name');
  await page.locator('#da-focus').click();assert(!await page.locator('.draft-workspace-nav').isVisible());
  await page.locator('#da-pool-details').evaluate(e=>e.open=true);
  await page.locator('#da-pool-details a').click();assert(await page.locator('#draft-pool').isVisible());
  assert(await page.locator('.draft-workspace-nav').isVisible());
  await page.reload();assert.equal(await page.locator('#dp-notes').inputValue(),'Verifica nuova navigazione');
  assert(await page.locator('#draft-pool').isVisible());
  for (const hash of ['#draft-combos','#pick-decisions','#report-3','#card-statistics','#dp-import']) {
   await page.goto(url+hash);
   const target = page.locator(hash);
   assert(await target.isVisible(),`${hash}: direct URL opens the view and ancestor details`);
  }
  await page.goto(url+'#draft-assistant');
  await page.locator('[data-draft-view="guide"]').click();
  await page.locator('[data-draft-view="data"]').click();
  await page.goBack();assert(await page.locator(views.guide).isVisible());
  await page.goForward();assert(await page.locator(views.data).isVisible());
  await page.goto(url);
  await page.locator('[data-draft-view="guide"]').click();
  await page.goBack();assert.equal(new URL(page.url()).hash,'');assert(await page.locator(views.assistant).isVisible());
  await page.goForward();assert(await page.locator(views.guide).isVisible());
  await page.locator('[data-draft-view="assistant"]').click();await page.locator('#da-search').focus();
  await page.goBack();assert(await page.locator(views.guide).isVisible());
  assert.equal(await page.evaluate(()=>document.activeElement.id),'pick-guide','History restores focus to the revealed view');
  await page.locator('[data-draft-view="pool"]').focus();await page.keyboard.press('Enter');
  assert(await page.locator('#draft-pool').isVisible());
  assert.equal(await page.evaluate(()=>document.activeElement.id),'draft-pool');
  await page.locator('[data-draft-view="assistant"]').click();await page.locator('#da-focus').click();
  const reportOpen = await page.locator('#draft-report').evaluate(e=>e.open);
  await page.evaluate(()=>dispatchEvent(new Event('beforeprint')));
  await page.emulateMedia({media:'print'});
  assert(await page.locator(views.guide).isVisible(),'Focused mode preserves printed guide');
  assert(await page.locator(views.data).isVisible(),'Focused mode preserves printed statistics');
  assert(!await page.locator(views.pool).isVisible(),'Pool editing controls stay out of print');
  assert(await page.locator('#report-0').isVisible(),'Extended report is included in print');
  assert(await page.locator('.draft-workspace-intro h1').isVisible(),'Focused print includes page title');
  assert(await page.locator('.attribution').isVisible(),'Focused print includes source attribution');
  await page.emulateMedia({media:'screen'});await page.evaluate(()=>dispatchEvent(new Event('afterprint')));
  assert.equal(await page.locator('#draft-report').evaluate(e=>e.open),reportOpen);
  await page.locator('#da-focus').click();
  await page.goto(url+'#pick-decisions');
  assert.equal(await page.locator('#draft-report .site-page-index').count(),0,'One disclosure level for report navigation');
  const alias = page.locator('#pick-decisions [data-card-preview]').filter({hasText:/^Kiora$/}).first();
  await alias.locator('xpath=ancestor::details[1]').locator('summary').click();
  await alias.hover();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  await alias.focus();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  const touch = await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'reduce'});
  const mobile = await touch.newPage();await mobile.goto(url);
  const tablet=await touch.newPage();await tablet.setViewportSize({width:1024,height:600});await tablet.goto(url);
  await tablet.locator('#da-search').focus();await tablet.setViewportSize({width:1024,height:340});
  await tablet.waitForFunction(()=>document.body.classList.contains('draft-editing'));
  await tablet.setViewportSize({width:1024,height:600});
  assert.equal(await tablet.locator('.draft-workspace-nav').evaluate(e=>getComputedStyle(e).position),'static','Tablet nav stays static through keyboard closing');
  await tablet.locator('[data-draft-view="pool"]').tap();
  assert.equal(await tablet.locator('.draft-workspace-nav').evaluate(e=>getComputedStyle(e).position),'sticky','Explicit navigation restores tablet navigation');await tablet.close();
  await mobile.goto(url+'#draft-drilldown');
  for(const control of ['#dd-lands','#dd-pair']){
   await mobile.locator(control).focus();assert.equal(await mobile.locator('.draft-workspace-nav').evaluate(e=>getComputedStyle(e).position),'sticky');
  }
  await mobile.goto(url);await mobile.locator('[data-da-browse]').click();await mobile.locator('#da-search').focus();
  await unobscured(mobile,'#da-search');
  await mobile.evaluate(()=>{
   const original=window.scrollBy;window.workspaceScrollCalls=[];
   window.scrollBy=function(options){window.workspaceScrollCalls.push(options);return original.call(this,options);};
   window.scrollTo({top:document.body.scrollHeight,behavior:'instant'});dispatchEvent(new Event('resize'));
  });
  await mobile.evaluate(()=>new Promise(requestAnimationFrame));
  assert.equal(await mobile.evaluate(()=>window.workspaceScrollCalls.length),0,'Same-height resize preserves voluntary scrolling');
  const cdp = await touch.newCDPSession(mobile);
  await cdp.send('Emulation.setPageScaleFactor',{pageScaleFactor:2});
  await mobile.evaluate(()=>new Promise(requestAnimationFrame));
  assert.equal(await mobile.evaluate(()=>window.workspaceScrollCalls.length),0,'Pinch zoom does not force scrolling back to the focused field');
  await cdp.send('Emulation.setPageScaleFactor',{pageScaleFactor:1});await cdp.detach();await mobile.goto(url);
  await mobile.setViewportSize({width:390,height:340});
  await mobile.locator('#da-search').fill('Surveillance');await mobile.locator('#da-search').focus();
  assert.equal(await mobile.locator('.draft-workspace-nav').evaluate(e=>getComputedStyle(e).position),'static');
  await unobscured(mobile,'#da-search');
  await mobile.setViewportSize({width:390,height:844});
  await mobile.locator('#da-search').fill('Surveillance');await mobile.locator('#da-results [data-name]').tap();
  assert(await mobile.locator('#draft-dialog').isVisible());await mobile.locator('#draft-close').tap();
  await mobile.locator('[data-draft-view="guide"]').tap();await mobile.locator('a[href="#draft-combos"]').first().tap();
  await mobile.locator('#combo-search').fill('proft');
  const combo = mobile.locator('.draft-package:visible [data-card-preview="Proft, Consulting Detective"]').first();
  await combo.tap();await mobile.locator('#mtg-card-preview').waitFor({state:'visible'});
  await combo.tap();await mobile.locator('#mtg-card-preview').waitFor({state:'hidden'});
  await mobile.goto(url+'#pick-decisions');
  const touchAlias = mobile.locator('#pick-decisions [data-card-preview]').filter({hasText:/^Kiora$/}).first();
  await touchAlias.locator('xpath=ancestor::details[1]').locator('summary').tap();await touchAlias.tap();
  await mobile.locator('#mtg-card-preview').waitFor({state:'visible'});await mobile.keyboard.press('Escape');
  await mobile.locator('[data-draft-view="data"]').tap();await mobile.locator('a[href="#card-statistics"]').click();
  await mobile.locator('#draft-search').fill('Surveillance');await mobile.locator('#draft-rows [data-name]').tap();
  assert(await mobile.locator('#draft-dialog').isVisible());await mobile.locator('#draft-close').tap();
  await mobile.locator('[data-draft-view="pool"]').tap();await mobile.locator('#dp-search').fill('Surveillance');
  await mobile.locator('#dp-results [data-dp-add]').tap();await mobile.locator('#dp-pool [data-name]').tap();
  assert(await mobile.locator('#draft-dialog').isVisible());await touch.close();
  const staticContext = await browser.newContext({javaScriptEnabled:false,reducedMotion:'reduce',viewport:{width:390,height:844}});
  const staticPage = await staticContext.newPage();await staticPage.goto(url+'#pick-guide');
  assert(await staticPage.locator('#pick-guide').isVisible());
  assert(await staticPage.locator('#draft-combos .draft-package').first().isVisible());
  await staticPage.locator('#draft-report>summary').click();assert(await staticPage.locator('#report-3').isVisible());
  assert(await staticPage.evaluate(()=>document.documentElement.scrollWidth <= innerWidth+1));
  await staticContext.close();
  assert.deepEqual(errors,[]);assert.deepEqual(missing,[]);
  const result={responsiveChecks:checks.length,widths:[320,360,390,768,1024,1440],views:Object.keys(views),deepLinks:true,history:true,emptyHashHistory:true,historyFocus:true,forcedColors:true,forcedColorsFocus:true,mobileReportPadding:true,placeholderContrast:true,zoomPreservesScroll:true,checkboxAndSelectKeepNavigation:true,focusedPrint:true,printTitleAndAttribution:true,reportPrintRestored:true,readableSelectedAndPoolNames:true,feedbackUnobscured:true,shortViewport:true,tabletKeyboardTransition:true,decisionAliases:true,keyboard:true,touch:true,previews:true,staticContent:true,errors,missing};
  fs.writeFileSync(path.join(screenshotDir,'draft-workspace-verification.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result,null,2));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
