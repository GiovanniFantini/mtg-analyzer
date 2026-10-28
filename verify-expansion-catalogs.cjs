'use strict';
// Verify actual registered routes, catalogs and previews for newly added expansions.
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const assert=require('node:assert/strict');
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const root=__dirname;
const base=process.env.MTG_SITE_URL;
if(!base)throw Error('Impostare MTG_SITE_URL al sito servito da dist/.');
const wanted=process.argv.slice(2);
const manifests=JSON.parse(fs.readFileSync(path.join(root,'expansions.json'),'utf8'))
 .map(row=>JSON.parse(fs.readFileSync(path.join(root,row.manifest),'utf8')))
 .filter(manifest=>wanted.length?wanted.includes(manifest.id):!['reality-fracture','star-trek'].includes(manifest.id));
const output=process.env.MTG_QA_DIR||fs.mkdtempSync(path.join(os.tmpdir(),'mtg-expansion-catalogs-'));
fs.mkdirSync(output,{recursive:true});
fs.rmSync(path.join(output,'report.json'),{force:true});
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
 const results=[];
 try{
  for(const manifest of manifests){
   const context=await browser.newContext({viewport:{width:1440,height:1000}});
   const page=await context.newPage();
   const errors=[];
   page.on('pageerror',error=>errors.push(error.message));
   page.setDefaultTimeout(60000);
   try{
   const prefix=new URL('sets/'+manifest.id+'/',base).href;
   const response=await context.request.get(prefix+'data/runtime.json');
   assert.equal(response.status(),200);
   const runtime=await response.json();
   const routes=[...new Set(Object.values(runtime.routes))];
   for(const route of routes){
    const response=await page.goto(prefix+route,{waitUntil:'domcontentloaded'});
    assert.equal(response.status(),200,manifest.id+'/'+route);
    await page.locator('main').waitFor();
   }
   await page.goto(prefix+manifest.presentation.pages.gallery.url,{waitUntil:'domcontentloaded'});
   const list=page.locator('#trk-cards .trk-card');
   const data=JSON.parse(fs.readFileSync(path.join(root,'expansions',manifest.id,'cards.json'),'utf8'));
   const count=data.cards.length;
   const ratings=JSON.parse(fs.readFileSync(path.join(root,'expansions',manifest.id,'ratings.json'),'utf8'));
   const hasReviews=Object.values(ratings.cards||{}).some(rating=>rating.community!=null);
   if(count){
    await list.first().waitFor();
    const cardName=data.cards[0].name;
    await page.locator('#trk-search').fill(cardName);
    await page.waitForFunction(name=>document.querySelector('#trk-cards')?.textContent.includes(name),cardName);
    assert.ok(await list.count());
    const preview=page.locator('#trk-cards h3 [data-card-preview]').first();
    if(await preview.count()){
     await preview.hover();
     await page.locator('#mtg-card-preview').waitFor({state:'visible'});
     await page.keyboard.press('Escape');
     await preview.focus();
     await preview.press('Enter');
     await page.locator('#mtg-card-preview').waitFor({state:'visible'});
     await page.keyboard.press('Escape');
    }
    await page.locator('#trk-reset').click();
    await page.locator('#trk-order').selectOption('name');
    assert.ok(await list.count());
    if(hasReviews){
     assert.ok(await page.locator('#review-min').isEnabled(),manifest.id+' external reviews available');
     await page.locator('#trk-order').selectOption('community');
     assert.ok(await page.locator('#trk-cards .catalog-metrics').count());
     assert.match(await page.locator('#trk-cards .catalog-metrics').first().innerText(),/Recensioni: [\d.,]+ \/ 5/);
     assert.ok(await page.locator('#trk-cards .catalog-metrics a').first().getAttribute('href'));
    }
   }
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),manifest.id+' desktop overflow');
   await page.screenshot({path:path.join(output,manifest.id+'-desktop.png')});
   const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
   const touch=await mobile.newPage();
   touch.setDefaultTimeout(60000);
   touch.on('pageerror',error=>errors.push(error.message));
   await touch.goto(prefix+manifest.presentation.pages.gallery.url,{waitUntil:'domcontentloaded'});
   if(count){
    await touch.locator('#trk-cards .trk-card').first().waitFor();
    const preview=touch.locator('#trk-cards h3 [data-card-preview]').first();
    if(await preview.count()){
     await preview.tap();
     await touch.locator('#mtg-card-preview').waitFor({state:'visible'});
     await touch.keyboard.press('Escape');
    }
   }
   assert.ok(await touch.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),manifest.id+' mobile overflow');
   await touch.screenshot({path:path.join(output,manifest.id+'-mobile.png')});
   assert.deepEqual(errors,[],manifest.id+' browser errors');
   results.push({id:manifest.id,catalogCards:count,routes:routes.length,widths:[1440,390],previews:count?['mouse','keyboard','touch']:[],errors});
   console.log(JSON.stringify(results.at(-1)));
   await mobile.close();
   await context.close();
   }catch(error){
    fs.writeFileSync(path.join(output,manifest.id+'-failure.json'),JSON.stringify({id:manifest.id,url:page.url(),errors,error:String(error)},null,2));
    error.message=manifest.id+': '+error.message;
    throw error;
   }
  }
  fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({base,results},null,2));
  console.log('QA: '+output);
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
