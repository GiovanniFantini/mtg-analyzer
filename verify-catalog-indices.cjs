'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const base=process.env.MTG_SITE_URL;if(!base)throw Error('MTG_SITE_URL required');
const out=process.env.MTG_QA_DIR||fs.mkdtempSync(path.join(os.tmpdir(),'mtg-indices-'));fs.mkdirSync(out,{recursive:true});
const fixture=process.env.MTG_INDICES_FIXTURE==='1';
const manifests=JSON.parse(fs.readFileSync('expansions.json','utf8')).map(r=>JSON.parse(fs.readFileSync(r.manifest,'utf8'))).filter(m=>!fixture||['reality-fracture','the-hobbit'].includes(m.id));
(async()=>{const b=await chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL||'msedge'}),results=[],errors=[];
try{for(const m of manifests){const p=await b.newPage({viewport:{width:1440,height:1000}});p.on('pageerror',e=>errors.push(m.id+': '+e.message));
 if(fixture)await p.route('**/*',route=>{const u=new URL(route.request().url()),name=path.basename(u.pathname);if(name===path.basename(m.presentation.pages.gallery.url))return route.fulfill({path:path.join(os.tmpdir(),'mtg-indices-'+m.id+'.html'),contentType:'text/html'});if(['catalog-controls.js','catalog-indices.js','catalog-controls.css','prospects-ui.js'].includes(name))return route.fulfill({path:path.resolve(name),contentType:name.endsWith('css')?'text/css':'application/javascript'});return route.continue()});
 await p.goto(new URL('sets/'+m.id+'/'+m.presentation.pages.gallery.url+'#gallery',base).href);await p.locator('#cards .card').first().waitFor();
 await p.locator('.site-catalog-filters').evaluate(e=>e.open=true);
 for(const id of ['wr-filters','sealed-wr-filters','prospect-filters'])assert.ok(await p.locator('#'+id).isVisible(),m.id+' '+id);
 const baseline=await p.evaluate(()=>JSON.stringify({...localStorage}));
 const sorts=[];
 for(const kind of ['draft','sealed']){
  const options=await p.locator('#'+kind+'-wr-source option').evaluateAll(os=>os.map(o=>o.value));
  for(const opt of options){if(options.length>1)await p.locator('#'+kind+'-wr-source').selectOption(opt);
   for(const asc of [false,true]){const order=(kind==='draft'?'wr':'sealed-wr')+(asc?'-asc':'');
    if(await p.locator('#order option[value="'+order+'"]').isDisabled())continue;
    await p.locator('#order').selectOption(order);
    const rows=await p.evaluate(kind=>filtered.map(c=>({id:c.id,value:catalog.indices.source(kind)?.cards[c.id]?.value??null})),kind);
    const nums=rows.filter(r=>r.value!=null).map(r=>r.value);assert.deepEqual(nums,[...nums].sort((a,b)=>asc?a-b:b-a));const missing=rows.findIndex(r=>r.value==null);if(missing>=0)assert.ok(rows.slice(missing).every(r=>r.value==null));sorts.push(order+':'+opt);
   }
  }
 }
 await p.locator('#reset').click();await p.locator('.site-catalog-filters').evaluate(e=>e.open=true);
 for(const format of ['standard','pioneer','modern','pauper']){
  await p.locator('#prospect-format').selectOption(format);await p.locator('#prospect-legality').selectOption('legal');
  assert.ok(await p.evaluate(f=>filtered.every(c=>['legal','restricted'].includes(c.legalities?.[f]||c.prospects?.formats?.[f]?.legality)),format));
  await p.locator('#prospect-state').selectOption('documented');assert.ok(await p.evaluate(f=>filtered.every(c=>c.prospects?.formats?.[f]?.evidence&&!['non_documentata','non_verificata','non_legale'].includes(c.prospects.formats[f].evidence)),format));
  await p.locator('#reset').click();
 }
 await p.locator('#sealed-wr-data').selectOption('missing');assert.ok(await p.evaluate(()=>filtered.every(c=>catalog.indices.rate(c,'sealed')==null)));await p.locator('#reset').click();
 if(!await p.locator('#sealed-wr-min').isDisabled()){
  await p.locator('#sealed-wr-min').fill('50');await p.locator('#sealed-wr-games').fill('100');assert.ok(await p.evaluate(()=>filtered.every(c=>catalog.indices.rate(c,'sealed')>=50&&catalog.indices.source('sealed').cards[c.id].games>=100)));
  await p.locator('#sealed-wr-max').fill('40');assert.equal(await p.evaluate(()=>filtered.length),0);await p.locator('#reset').click();
 }
 assert.equal(await p.evaluate(()=>JSON.stringify({...localStorage})),baseline,'Filters must not alter saves');
 await p.locator('.site-catalog-filters').evaluate(e=>e.open=false);
 assert.ok(await p.locator('#cards .catalog-performance').count());assert.equal(await p.locator('#cards .catalog-prospect-indices').first().locator('dt').count(),4);
 if(['reality-fracture','the-hobbit','star-trek'].includes(m.id)){
  await p.evaluate(()=>window.scrollTo(0,0));await p.screenshot({path:path.join(out,m.id+'-desktop.png'),animations:'disabled'});await p.setViewportSize({width:390,height:900});await p.locator('.site-catalog-filters').evaluate(e=>e.open=true);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await p.locator('#wr-filters').scrollIntoViewIfNeeded();await p.screenshot({path:path.join(out,m.id+'-mobile-filters.png'),animations:'disabled'});
  await p.locator('.site-catalog-filters').evaluate(e=>e.open=false);await p.locator('#cards .card-title').first().focus();await p.keyboard.press('Enter');await p.locator('#zoom').waitFor({state:'visible'});assert.ok(await p.locator('#zoom .catalog-performance').count());await p.keyboard.press('Escape');
 }
 results.push({id:m.id,sorts,filters:['draft WR','sealed WR','sample size','standard','pioneer','modern','pauper'],savesPreserved:true});await p.close();
}assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({results,errors},null,2));console.log(JSON.stringify({expansions:results.length,out,errors}));}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
