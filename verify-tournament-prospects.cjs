'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const base=process.env.MTG_SITE_URL;if(!base)throw Error('MTG_SITE_URL required');
const out=process.env.MTG_QA_DIR||fs.mkdtempSync(path.join(os.tmpdir(),'mtg-tournaments-'));fs.mkdirSync(out,{recursive:true});
const manifests=JSON.parse(fs.readFileSync('expansions.json','utf8')).map(r=>JSON.parse(fs.readFileSync(r.manifest,'utf8')));
(async()=>{const b=await chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL||'msedge'}),results=[],errors=[];
try{for(const m of manifests){const ctx=await b.newContext({viewport:{width:1440,height:1000},hasTouch:true}),p=await ctx.newPage();p.on('pageerror',e=>errors.push(m.id+': '+e.message));
 const representative=['reality-fracture','the-hobbit','star-trek'].includes(m.id);
 await ctx.route('**/*',route=>route.request().resourceType()==='image'?route.abort():route.continue());
 const prefix=new URL('sets/'+m.id+'/',base).href;await p.goto(prefix+m.presentation.pages.gallery.url+'#gallery',{waitUntil:'domcontentloaded'});await p.locator('#cards .card').first().waitFor();
 const storage=await p.evaluate(()=>JSON.stringify({...localStorage}));await p.locator('.site-catalog-filters').evaluate(e=>e.open=true);
 for(const f of ['standard','pioneer','modern','pauper']){
  await p.locator('#prospect-format').selectOption(f);
  const available=await p.locator('#order option[value="prospect-'+f+'"]').isEnabled();
  if(available)for(const asc of [false,true]){
   await p.locator('#order').selectOption('prospect-'+f+(asc?'-asc':''));
   const values=await p.evaluate(f=>filtered.map(c=>c.prospects.formats[f].tournamentIndex.score),f),valid=values.filter(v=>v!=null);assert.deepEqual(valid,[...valid].sort((a,b)=>asc?a-b:b-a));const missing=values.findIndex(v=>v==null);if(missing>=0)assert.ok(values.slice(missing).every(v=>v==null));
  }
  await p.locator('#prospect-min').fill('1');await p.locator('#prospect-sample').fill('50');
  assert.ok(await p.evaluate(f=>filtered.every(c=>c.prospects.formats[f].tournamentIndex.score>=1&&c.prospects.formats[f].tournamentIndex.sample.decks>=50),f));
  await p.locator('#prospect-max').fill('0');assert.equal(await p.evaluate(()=>filtered.length),0);await p.locator('#reset').click();await p.locator('#prospect-format').selectOption(f);await p.locator('#prospect-state').selectOption('not_observed');
  assert.ok(await p.evaluate(f=>filtered.every(c=>c.prospects.formats[f].tournamentIndex.score===0),f));await p.locator('#reset').click();
 }
 await p.locator('#prospect-format').selectOption('standard');await p.locator('#prospect-outlook').selectOption('watch');assert.ok(await p.evaluate(()=>filtered.every(c=>c.prospects.formats.standard.tournamentIndex.outlook.status==='watch')));await p.locator('#reset').click();
 assert.equal(await p.evaluate(()=>JSON.stringify({...localStorage})),storage,'Catalog filtering changes no saved records');
 if(representative)await ctx.unroute('**/*');
 await p.goto(prefix+m.presentation.pages.discovery.url,{waitUntil:'domcontentloaded'});await p.locator('#results .candidate').first().waitFor();assert.ok(await p.locator('#results .discovery-tournament-indices').count());assert.ok(await p.locator('#tournament-method').count());
 for(const f of ['Standard','Pioneer','Modern','Pauper']){const button=p.locator('#formats [data-format="'+f+'"]');if(await button.count()){await button.click();await p.locator('#sort').selectOption('tournament');const values=await p.locator('.discovery-tournament-indices dd').allInnerTexts();assert.ok(values.length);}}
 await p.locator('#formats [data-format="Tutti"]').click();
 if(['reality-fracture','the-hobbit','star-trek'].includes(m.id)){
  await p.evaluate(()=>window.scrollTo(0,0));await p.screenshot({path:path.join(out,m.id+'-discovery-desktop.png'),animations:'disabled'});
  const reference=p.locator('#results h3 [data-card-preview]').first();await reference.hover();await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');await reference.focus();await p.keyboard.press('Enter');await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
  const details=p.locator('details[data-prospect]').first();await details.locator('summary').click();await details.locator('.tournament-prospects').waitFor();await details.locator('.tournament-format summary').first().click();await p.screenshot({path:path.join(out,m.id+'-tournament-details.png'),animations:'disabled'});
  await p.setViewportSize({width:390,height:900});await p.evaluate(()=>window.scrollTo(0,0));assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await p.screenshot({path:path.join(out,m.id+'-discovery-mobile.png'),animations:'disabled'});
  await details.locator('summary').first().tap();await reference.scrollIntoViewIfNeeded();await reference.tap();await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
 }
 await p.locator('#research-view').selectOption('all');await p.locator('#research-status').filter({hasText:'analisi consultabili'}).waitFor();assert.ok(await p.locator('#results .candidate').count());
 results.push({expansion:m.id,numericSorts:8,fourFormatFilters:true,zeroVsMissing:true,savedRecordsPreserved:true,discoveryPopulated:true,allAnalyses:true});console.log('PASS',m.id);await ctx.close();
}assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({results,errors},null,2));console.log(JSON.stringify({expansions:results.length,out,errors}));}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
