const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const base=(process.env.MTG_SITE_URL||'http://127.0.0.1:8765/')+'sets/star-trek/';
(async()=>{
 const out=process.env.MTG_QA_DIR||fs.mkdtempSync(path.join(os.tmpdir(),'mtg-trk-research-'));
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'}),errors=[];
 try{
  for(const width of [1440,390]){
   const ctx=await browser.newContext({viewport:{width,height:960},isMobile:width===390,hasTouch:width===390});
   const p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));
   await p.goto(base+'catalogo.html');await p.locator('#trk-search').fill('Federation Probe');
   const ref=p.locator('#trk-cards h3 [data-card-preview]');await p.locator('#trk-color').focus();
   if(width===390)await ref.tap();else await ref.hover();
   await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
   await ref.focus();await ref.press('Enter');await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
   const detail=p.locator('.trk-prospects');await detail.locator(':scope>summary').click();
   assert.match(await detail.innerText(),/Prevista dal/);
   const model=detail.locator('details').filter({has:p.getByText('Previsioni automatiche e letture delle fonti',{exact:true})});
   await model.locator(':scope>summary').click();assert.match(await model.innerText(),/3\.7\/5/);assert.match(await model.innerText(),/senza equivalenza con voti Limited/);
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await p.screenshot({path:path.join(out,'research-'+width+'.png')});
   await p.locator('#trk-search').fill('Type-2 Phaser');await p.locator('.trk-prospects>summary').click();
   assert.match(await p.locator('.card-prospects').innerText(),/0,99/);
   await p.goto(base+'discovery.html');await p.locator('#trk-set').selectOption('TRK');await p.locator('#trk-legality').selectOption('pauper');
   const current=await p.locator('#trk-count').innerText();
   await p.locator('#trk-legality-scope').selectOption('release');
   assert.ok(await p.locator('#trk-cards .trk-card').count());
   assert.notEqual(await p.locator('#trk-count').innerText(),current);
   await p.locator('#trk-cards .trk-prospects>summary').first().click();
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await ctx.close();
  }
  assert.deepEqual(errors,[]);console.log(JSON.stringify({out,widths:[1440,390],models:true,prices:true,legalities:true,previews:['mouse','keyboard','touch'],errors}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
