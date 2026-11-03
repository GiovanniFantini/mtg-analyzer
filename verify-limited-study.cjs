'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const base=new URL('sets/star-trek/',process.env.MTG_SITE_URL).href;
(async()=>{
 const out=process.env.MTG_QA_DIR||fs.mkdtempSync(path.join(os.tmpdir(),'mtg-limited-study-'));
 fs.mkdirSync(out,{recursive:true});const results=[];
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
 try{
  for(const width of [1440,390]){
   const context=await browser.newContext({viewport:{width,height:1000},isMobile:width===390,hasTouch:width===390}),page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   const doc=await(await context.request.get(base+'data/cards.json')).json(),cards=doc.cards;
   for(const [route,event] of [['draft.html','draft'],['strategy.html','sealed']]){
    await page.goto(base+route+'#limited-review');
    const root=page.locator('#limited-review');await root.waitFor({state:'visible'});
    assert.equal(await root.locator('[data-lr-card]').count(),201);
    assert.equal(await page.locator('#limited-impact .lr-card').count(),42);
    assert.equal(await root.locator('[data-lr-filter="context"]').inputValue(),event);
    await root.locator('[data-lr-filter="context"]').selectOption('sealed');
    await root.locator('[data-lr-filter="color"]').selectOption('G');
    await root.locator('[data-lr-filter="rarity"]').selectOption('common');
    await root.locator('[data-lr-filter="tier"]').selectOption('P');
    const expected=cards.filter(c=>c.prospects?.limitedAnalysis&&c.identity.includes('G')&&c.rarity==='common'&&c.prospects.limitedAnalysis.sealed.tier==='P');
    const visible=root.locator('[data-lr-card]:not([hidden])');
    assert.equal(await visible.count(),expected.length);assert.ok(expected.length>0);
    const ref=visible.first().locator('h3 [data-card-preview]');await ref.waitFor();await ref.scrollIntoViewIfNeeded();
    if(width===390)await ref.tap();else await ref.hover();
    await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
    await ref.focus();await ref.press('Enter');await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
    assert.equal(await visible.first().locator('[data-lr-context="draft"]').isVisible(),false);
    await root.locator('[data-lr-filter="query"]').fill('this-is-not-a-card-934701');
    assert.equal(await root.locator('[data-lr-card]:not([hidden])').count(),0);
    assert.ok(await root.locator('[data-lr-empty]').isVisible());
    await root.locator('[data-lr-reset]').click();
    assert.equal(await root.locator('[data-lr-card]:not([hidden])').count(),201);
    assert.equal(await root.locator('[data-lr-filter="context"]').inputValue(),event);
    await root.locator('[data-lr-filter="query"]').fill('Support Mission');
    const support=root.locator('[data-lr-card][data-lr-name="Support Mission"]');
    await support.locator('summary').click();assert.equal(await page.locator('#draft-dialog[open]').count(),0);assert.match(await support.innerText(),/Andrew Quinn: 0\.0\/10/);
    await root.locator('.lr-disagreements > summary').click();assert.match(await root.locator('.lr-disagreements').innerText(),/quattro nomi a cinque/);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    await page.screenshot({path:path.join(out,event+'-'+width+'.png')});
   }
   await page.goto(base+'sinergie.html');
   assert.equal(await page.locator('.draft-package').count(),26);
   await page.locator('#combo-role').selectOption('Interazione');
   assert.ok(await page.locator('.draft-package:not([hidden])').count()>=3);
   await page.locator('#combo-reset').click();assert.equal(await page.locator('.draft-package:not([hidden])').count(),26);
   assert.equal(await page.locator('#catalogo').isVisible(),false);
   const packageRef=page.locator('.draft-package [data-card-preview]').first();await packageRef.scrollIntoViewIfNeeded();
   if(width===390)await packageRef.tap();else await packageRef.hover();
   await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
   await page.goto(base+'catalogo.html');await page.locator('#search').fill('Common Goal');
   const id=cards.find(c=>c.name==='Common Goal').id;
   await page.locator('#cards .card-title[data-zoom="'+id+'"]').click();
   const review=page.locator('#zoom .card-limited');await review.waitFor({state:'visible'});
   assert.match(await page.locator('#zoom .ratings').innerText(),/scale originali/i);
   assert.match(await page.locator('#zoom .ratings').innerText(),/Andrew Quinn/);
   assert.match(await review.innerText(),/Draft: Prioritaria/);assert.match(await review.innerText(),/Sealed: Prioritaria/);
   await review.locator('summary').click();assert.match(await review.innerText(),/Andrew Quinn/);assert.match(await review.innerText(),/J2SJosh/);
   assert.equal(await page.locator('#zoom .card-limited').count(),1);
   assert.deepEqual(errors,[]);results.push({width,editorialCards:201,impactCards:42,packages:26,filters:true,zeroPreserved:true,previews:['mouse-or-touch','keyboard'],errors});
   await context.close();
  }
  const plain=await browser.newContext({javaScriptEnabled:false}),p=await plain.newPage();
  await p.goto(base+'strategy.html');assert.equal(await p.locator('[data-lr-card]').count(),201);assert.equal(await p.locator('[data-lr-context="sealed"]').count(),201);await plain.close();
  const fraRoute=require('./expansions/reality-fracture/expansion.json').presentation.pages.gallery.url;
  const fallback=await browser.newPage();await fallback.goto(new URL('../reality-fracture/'+fraRoute,base).href);
  await fallback.locator('#cards .card').first().waitFor();assert.ok(await fallback.locator('#cards .stars').count());
  assert.ok(!(await fallback.locator('#cards').innerText()).includes('undefined'));await fallback.close();
  fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify({results,noJavaScript:'201 assessments remain readable'},null,2)+'\n');console.log(JSON.stringify({out,results,noJavaScript:true}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
