'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const base=new URL('sets/star-trek/',process.env.MTG_SITE_URL).href;
const study=require('./research/star-trek-decisions-20261103/assessments.json');
(async()=>{
 const out=process.env.MTG_QA_DIR||fs.mkdtempSync(path.join(os.tmpdir(),'mtg-decisions-'));
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL}),results=[];
 try{
  for(const width of [1440,390]){
   const ctx=await browser.newContext({viewport:{width,height:1000},isMobile:width===390,hasTouch:width===390}),page=await ctx.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   const catalog=await(await ctx.request.get(base+'data/cards.json')).json();
   await page.goto(base+'analisi.html');
   const index=page.locator('[data-editorial-decisions]');await index.waitFor({state:'visible'});
   assert.equal(await index.locator('a').count(),12);
   const href=await index.locator('a').first().getAttribute('href');
   await index.locator('a').first().click();
   assert.ok(page.url().includes(new URL(href,base).search));
   await page.locator('#cards .card').first().waitFor();
   assert.match(await page.locator('#search').inputValue(),/Salt Vampire/);
   for(const row of study.cards){
    await page.locator('#search').fill(row.name);
    const id=catalog.cards.find(c=>c.name===row.name).id;
    await page.locator('#cards .card-title[data-zoom="'+id+'"]').click();
    const zoom=page.locator('#zoom'),review=zoom.locator('.prospect-decision');
    await review.waitFor({state:'visible'});
    assert.equal(await review.count(),1);
    await page.waitForFunction(verdict=>document.querySelector('#zoom .prospect-decision')?.textContent.includes(verdict),row.verdict);
    assert.equal(await review.locator('h5').count(),row.sections.length);
    assert.equal(await zoom.locator('.constructed-prospects').getAttribute('open'),null);
    const ref=review.locator('[data-card-preview]').first();await ref.waitFor();await ref.scrollIntoViewIfNeeded();
    if(width===390)await ref.tap();else await ref.hover();
    await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
    await ref.focus();await ref.press('Enter');await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
    assert.ok(await zoom.evaluate(el=>el.scrollWidth<=el.clientWidth+1),row.name+' dialog overflow');
    if(row.name==='Salt Vampire')await page.screenshot({path:path.join(out,'decision-'+width+'.png')});
    await zoom.locator('.close').click();
   }
   await page.locator('#search').fill('Salt Vampire');
   await page.locator('#cards .card-title[data-zoom="'+catalog.cards.find(c=>c.name==='Salt Vampire').id+'"]').click();
   await page.locator('#zoom .constructed-prospects > summary').click();
   await page.locator('#zoom').getByText('Previsioni automatiche e letture delle fonti',{exact:true}).click();
   await page.locator('#zoom .card-prospects details:not(.prospect-sources) a[href*="usmantherad.com"]').first().waitFor({state:'visible'});
   await page.goto(base+'discovery.html?view=all&q=Salt%20Vampire');
   const details=page.locator('details[data-prospect="Salt Vampire"]');await details.waitFor();await details.locator('summary').click();
   await details.locator('.prospect-decision').waitFor({state:'visible'});
   assert.equal(await details.locator('.prospect-decision').count(),1);
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   assert.deepEqual(errors,[]);results.push({width,cards:12,indexLinks:12,previews:['mouse-or-touch','keyboard'],sourceLinks:true,discovery:true,errors});
   await ctx.close();
  }
  fs.writeFileSync(path.join(out,'browser-results.json'),JSON.stringify({results},null,2)+'\n');console.log(JSON.stringify({out,results}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
