/* Attributed notes must be visible with their source links on both layouts. */
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const base=new URL('sets/star-trek/',process.env.MTG_SITE_URL||'http://127.0.0.1:8765/').href;
(async()=>{
 const out=process.env.MTG_QA_DIR||fs.mkdtempSync(path.join(os.tmpdir(),'mtg-trk-authors-'));
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'}),results=[];
 try{
  for(const width of [1440,390]){
   const context=await browser.newContext({viewport:{width,height:1000},isMobile:width===390,hasTouch:width===390});
   const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
   const evidence=await(await context.request.get(base+'author-feedback-evidence.json')).json();
   const coverage=await(await context.request.get(base+'author-feedback-coverage.json')).json();
   assert.equal(evidence.observations.length,68);assert.equal(coverage.cards.length,341);
   assert.equal(coverage.summary.cardsWithOpinion,38);assert.equal(coverage.summary.cardsWithoutOpinion,303);
   await page.goto(base+'catalogo.html');await page.locator('#cards .card').first().waitFor();
   for(const [search,expected] of [['Dr. Leonard',/favorito/],['Salt Vampire',/Moist_Username/],['Holo-Engineer',/Pest Infestation/]]){
    await page.locator('#search').fill(search);await page.locator('#cards .card-title').first().click();
    const zoom=page.locator('#zoom');await zoom.waitFor({state:'visible'});
    await zoom.locator('.constructed-prospects > summary').click();
    await zoom.getByText('Previsioni automatiche e letture delle fonti',{exact:true}).click();
    const content=await zoom.innerText();assert.match(content,expected);assert.ok(!content.includes('undefined'));
    await zoom.locator('.prospect-sources > summary').click();
    const sourceHost=search==='Salt Vampire'?'reddit.com':search==='Dr. Leonard'?'stevemanadventures.substack.com':'mtgsalvation.com';
    assert.ok(await zoom.locator('.prospect-sources a[href*="'+sourceHost+'"]').count());
    if(search==='Holo-Engineer'){
     const external=zoom.locator('[data-card-preview="Pest Infestation"]').first();
     await external.scrollIntoViewIfNeeded();
     if(width===390)await external.tap();else await external.hover();
     await page.locator('#mtg-card-preview').waitFor({state:'visible'});
    }
    await page.keyboard.press('Escape');
   }
   await page.goto(base+'analisi.html');await page.getByRole('heading',{name:'Giudizi degli autori e dissensi'}).waitFor();
   const panel=page.locator('.trk-panel').filter({has:page.getByRole('heading',{name:'Giudizi degli autori e dissensi'})});
   assert.match(await panel.innerText(),/303/);
   const ref=panel.locator('[data-card-preview]').first();assert.ok(await ref.count());await ref.scrollIntoViewIfNeeded();
   if(width===390)await ref.tap();else await ref.hover();
   await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
   await ref.focus();await ref.press('Enter');await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await page.screenshot({path:path.join(out,'authors-'+width+'.png')});
   assert.deepEqual(errors,[]);results.push({width,visibleNotes:true,sourceLinks:true,coverage:true,previews:['mouse-or-touch','keyboard'],errors});
   await context.close();
  }
  fs.writeFileSync(path.join(out,'author-browser-results.json'),JSON.stringify({results},null,2)+'\n');console.log(JSON.stringify({out,results}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
