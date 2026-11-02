const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const base=new URL('sets/star-trek/',process.env.MTG_SITE_URL||'http://127.0.0.1:8765/').href;
(async()=>{
 const out=process.env.MTG_QA_DIR||fs.mkdtempSync(path.join(os.tmpdir(),'mtg-trk-knowledge-'));
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'}),results=[];
 try{
  for(const width of [1440,390]){
   const context=await browser.newContext({viewport:{width,height:1000},isMobile:width===390,hasTouch:width===390});
   const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
   const data=await(await context.request.get(base+'data/cards.json')).json();
   assert.equal(data.cards.length,341);assert.equal(data.cards.filter(c=>c.community!=null).length,306);
   await page.goto(base+'catalogo.html');await page.locator('#cards .card').first().waitFor();
   await page.locator('#search').fill('Boarding Action');
   const card=page.locator('#cards .card').first();
   assert.match(await card.innerText(),/Valutazione Limited interna/i);
   assert.ok(!/Voto Limited adottato/i.test(await card.innerText()));
   const ref=card.locator('h3 [data-card-preview]');await ref.scrollIntoViewIfNeeded();
   if(width===390)await card.locator('.card-title').tap();else {await ref.hover();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');await card.locator('.card-title').focus();await page.keyboard.press('Enter');}
   const zoom=page.locator('#zoom');await zoom.waitFor({state:'visible'});
   await zoom.locator('details.evidence > summary').click();
   assert.match(await zoom.innerText(),/J2SJosh|j2sjosh/i);await page.keyboard.press('Escape');
   assert.match(await card.innerText(),/resta sul campo|non impone|permanente/i);
   await page.locator('#search').fill('Salt Vampire');
   await page.locator('#cards .card-title').first().click();await zoom.waitFor({state:'visible'});
   await zoom.locator('.constructed-prospects > summary').click();
   await zoom.getByText('Previsioni automatiche e letture delle fonti',{exact:true}).click();
   assert.match(await zoom.innerText(),/Cards Realm/);assert.ok(!(await zoom.innerText()).includes('undefined'));
   await page.keyboard.press('Escape');
   await page.screenshot({path:path.join(out,'catalog-'+width+'.png')});
   await page.goto(base+'draft.html#draft-combos');await page.locator('#draft-combos .draft-package').first().waitFor();
   assert.equal(await page.locator('#draft-combos .draft-package').count(),10);
   assert.equal(await page.locator('.pick-decision').count(),6);
   const dynamic=page.locator('#draft-combos [data-card-preview]').first();await dynamic.scrollIntoViewIfNeeded();
   if(width===390)await dynamic.tap();else await dynamic.hover();
   await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
   await dynamic.focus();await dynamic.press('Enter');await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await page.screenshot({path:path.join(out,'draft-'+width+'.png')});
   await page.goto(base+'strategy.html');assert.match(await page.locator('body').innerText(),/Costruire il Sealed Star Trek/);
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await page.screenshot({path:path.join(out,'sealed-'+width+'.png')});
   await page.goto(base+'fonti.html');assert.match(await page.locator('body').innerText(),/306|341/);
   for(const name of ['catalog.json','limited-reviews.json','commander-appendix.json'])assert.equal((await context.request.get(base+name)).status(),200);
   assert.deepEqual(errors,[]);results.push({width,cards:341,grades:306,packages:10,decisions:6,previews:['mouse-or-touch','keyboard'],errors});
   await context.close();
  }
  fs.writeFileSync(path.join(out,'knowledge-report.json'),JSON.stringify({results},null,2)+'\n');console.log(JSON.stringify({out,results}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
