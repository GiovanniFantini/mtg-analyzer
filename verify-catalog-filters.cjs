const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');const fs=require('node:fs');const os=require('node:os');const path=require('node:path');
(async()=>{
 const out=process.env.MTG_QA_DIR||fs.mkdtempSync(path.join(os.tmpdir(),'mtg-catalog-filters-'));fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL||'msedge',headless:true});const errors=[];
 const url=(process.env.MTG_SITE_URL||'http://127.0.0.1:8770/')+'sets/reality-fracture/Reality-Fracture-Sealed.html#gallery';
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url,{waitUntil:'domcontentloaded'});await page.locator('#cards .card').first().waitFor();
  assert.equal(await page.getByRole('button',{name:'Mostra ranking Draft Untapped'}).count(),0);
  const visible=()=>page.evaluate(()=>filtered.map(c=>({id:c.id,mv:c.mv,colors:c.colors,type:c.type,review:c.community,tier:c.untappedPickOrder?.tier,wr:winRate(c)})));
  for(const order of ['color','type','mana','mana-desc','community','community-asc','untapped','untapped-reverse','wr','wr-asc']){
   await page.locator('#order').selectOption(order);const rows=await visible();assert.equal(rows.length,295);
   const key=order.startsWith('mana')?'mv':order.startsWith('community')?'review':order.startsWith('wr')?'wr':null;
   if(key){const nums=rows.map(r=>r[key]).filter(v=>v!=null);const asc=['mana','community-asc','wr-asc'].includes(order);assert.deepEqual(nums,[...nums].sort((a,b)=>asc?a-b:b-a));const firstMissing=rows.findIndex(r=>r[key]==null);if(firstMissing>=0)assert.ok(rows.slice(firstMissing).every(r=>r[key]==null))}
   if(order==='untapped')assert.equal(rows[0].tier,'S');if(order==='untapped-reverse')assert.equal(rows[0].tier,'F');
  }
  await page.locator('#reset').click();await page.locator('[data-color=U]').click();await page.locator('#catalog-type').selectOption('Creature');await page.locator('#mana-min').fill('2');await page.locator('#mana-max').fill('4');await page.locator('#review-min').fill('2.5');await page.locator('#review-max').fill('5');await page.locator('#wr-min').fill('50');await page.locator('#wr-max').fill('80');
  let rows=await visible();assert.ok(rows.length);assert.ok(rows.every(r=>r.colors.includes('U')&&r.type.split(' // ')[0].includes('Creature')&&r.mv>=2&&r.mv<=4&&r.review>=2.5&&r.review<=5&&r.wr>=50&&r.wr<=80));
  await page.locator('#mana-min').fill('8');assert.equal((await visible()).length,0);assert.ok(await page.getByText('Nessuna carta con questi filtri.').isVisible());
  await page.locator('#reset').click();assert.equal((await visible()).length,295);
  await page.locator('#catalog-tier').selectOption('low');assert.equal((await visible()).length,7);
  await page.locator('#catalog-tier').selectOption('missing');assert.equal((await visible()).length,5);
  await page.locator('#catalog-tier').selectOption('S');assert.equal((await visible()).length,7);
  await page.locator('#reset').click();await page.locator('#wr-data').selectOption('missing');rows=await visible();assert.ok(rows.length);assert.ok(rows.every(r=>r.wr==null));
  await page.locator('#reset').click();await page.locator('#review-data').selectOption('missing');assert.ok((await visible()).every(r=>r.review==null));
  await page.locator('#reset').click();await page.locator('#order').selectOption('wr');
  await page.locator('.site-catalog-filters summary').click();
  const ref=page.locator('#cards h3 [data-card-preview]').first();await ref.hover();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  await page.locator('#cards .card-title').first().focus();await page.keyboard.press('Enter');await page.locator('#zoom').waitFor({state:'visible'});assert.ok(await page.locator('#zoom .untapped-wr').count());await page.keyboard.press('Escape');
  await page.screenshot({path:path.join(out,'catalog-desktop.png')});
  for(const width of [768,390]){
   const ctx=await browser.newContext({viewport:{width,height:900},isMobile:width===390,hasTouch:true});const m=await ctx.newPage();m.on('pageerror',e=>errors.push(e.message));await m.goto(url,{waitUntil:'domcontentloaded'});await m.locator('#cards .card').first().waitFor();
   if(!await m.locator('#catalog-type').isVisible())await m.locator('.site-catalog-filters summary').tap();
   await m.locator('#catalog-type').selectOption('Instant');await m.locator('#mana-max').fill('3');assert.ok(await m.evaluate(()=>filtered.length>0&&filtered.every(c=>c.type.split(' // ')[0].includes('Instant')&&c.mv<=3)));
   assert.ok(await m.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await m.screenshot({path:path.join(out,'catalog-filters-'+width+'.png')});
   await m.locator('.site-catalog-filters summary').tap();await m.locator('#order').selectOption('wr');await m.locator('#cards .card-title').first().tap();await m.locator('#zoom').waitFor({state:'visible'});await m.keyboard.press('Escape');
   await m.screenshot({path:path.join(out,'catalog-results-'+width+'.png')});await ctx.close();
  }
  assert.deepEqual(errors,[]);const report={sorts:10,combinedFilters:true,emptyResults:true,reset:true,missingData:true,tierCounts:true,widths:[1440,768,390],previews:['mouse','keyboard','touch'],errors};fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({out,...report}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
