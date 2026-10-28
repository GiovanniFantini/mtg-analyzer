'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const base=process.env.MTG_SITE_URL;
if(!base)throw Error('Impostare MTG_SITE_URL.');
const wanted=process.argv.slice(2),root=__dirname;
const manifests=JSON.parse(fs.readFileSync(path.join(root,'expansions.json'),'utf8')).map(row=>JSON.parse(fs.readFileSync(path.join(root,row.manifest),'utf8'))).filter(m=>!wanted.length||wanted.includes(m.id));
const out=process.env.MTG_QA_DIR||fs.mkdtempSync(path.join(os.tmpdir(),'mtg-atlas-'));
fs.mkdirSync(out,{recursive:true});fs.rmSync(path.join(out,'report.json'),{force:true});
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'}),results=[];
 try{for(const m of manifests){
  assert.equal(m.presentation.style,'atlas');
  assert.ok(Object.values(m.presentation.pages).every(page=>!page.template?.includes('/preview/')));
  const context=await browser.newContext({viewport:{width:1440,height:1000}}),p=await context.newPage(),errors=[];
  p.setDefaultTimeout(60000);p.on('pageerror',e=>errors.push(e.message));
  const prefix=new URL('sets/'+m.id+'/',base).href;
  const runtime=await(await context.request.get(prefix+'data/runtime.json')).json();
  const catalog=JSON.parse(fs.readFileSync(path.join(root,'expansions',m.id,'cards.json'),'utf8')).cards;
  const card=catalog.find(c=>!c.basic&&c.set===m.code)||catalog[0],basic=catalog.find(c=>c.basic);
  const manual=!!m.storage.poolPrefix,seed={pool:{[card.id]:2},deck:{[card.id]:1},basics:basic?{[basic.id]:8}:{},notes:'Note da conservare',custom:{preserved:true}};
  try{
   await p.goto(prefix+m.presentation.pages.set.url);
   if(manual)await p.evaluate(({storage,events,seed})=>{for(const kind of ['draft','sealed'])if(events[kind])localStorage.setItem(storage.poolPrefix+events[kind]+'-v1',JSON.stringify(seed));},{storage:m.storage,events:runtime.defaultEvents,seed});
   for(const route of new Set(Object.values(runtime.routes))){
    const response=await p.goto(prefix+route,{waitUntil:'domcontentloaded'});if(response)assert.equal(response.status(),200,m.id+'/'+route);
    assert.ok(await p.locator('body.site-layout:not(.trk-page)').count());
   }
   await p.goto(prefix+m.presentation.pages.gallery.url+'#gallery',{waitUntil:'domcontentloaded'});
   await p.locator('#cards .card').first().waitFor();
   await p.locator('#search').fill(card.full||card.name);
   if(manual){
    // Exact ID lookup avoids choosing a reprint with the same display name.
    await p.locator('#cards [data-delta="1"][data-id="'+card.id+'"]').click();
    const saved=await p.evaluate(key=>JSON.parse(localStorage.getItem(key)),m.storage.poolPrefix+runtime.defaultEvents.sealed+'-v1');
    assert.equal(saved.pool[card.id],3);assert.equal(saved.deck[card.id],1);assert.deepEqual(saved.basics,seed.basics);assert.equal(saved.notes,seed.notes);assert.deepEqual(saved.custom,seed.custom);
    await p.goto(prefix+m.presentation.pages.draft.url+'#draft-pool',{waitUntil:'domcontentloaded'});
    await p.waitForFunction(()=>!!window.DraftPool);
    assert.equal(await p.evaluate(name=>DraftPool.get()[name],card.full||card.name),2);
    await p.locator('#dp-pool [data-dp-add]').first().click();
    await p.waitForFunction(({key,id})=>JSON.parse(localStorage.getItem(key)).pool[id]===3,{key:m.storage.poolPrefix+runtime.defaultEvents.draft+'-v1',id:card.id});
    const draft=await p.evaluate(key=>JSON.parse(localStorage.getItem(key)),m.storage.poolPrefix+runtime.defaultEvents.draft+'-v1');
    assert.equal(draft.pool[card.id],3);assert.equal(draft.deck[card.id],1);assert.deepEqual(draft.basics,seed.basics);assert.equal(draft.notes,seed.notes);assert.deepEqual(draft.custom,seed.custom);
    const alternate=Object.keys(runtime.events).find(id=>runtime.events[id].kind==='draft'&&id!==runtime.defaultEvents.draft);
    if(alternate){
     const key=m.storage.poolPrefix+alternate+'-v1',other={...seed,pool:{[card.id]:4}};
     await p.evaluate(({key,other})=>localStorage.setItem(key,JSON.stringify(other)),{key,other});
     await p.goto(prefix+m.presentation.pages.draft.url+'?mode='+alternate+'#draft-pool');
     await p.waitForFunction(()=>!!window.DraftPool);
     assert.equal(await p.evaluate(name=>DraftPool.get()[name],card.full||card.name),4);
     await p.locator('#dp-pool [data-dp-add]').first().click();
     await p.waitForFunction(({key,id})=>JSON.parse(localStorage.getItem(key)).pool[id]===5,{key,id:card.id});
     assert.equal(await p.evaluate(key=>JSON.parse(localStorage.getItem(key)).pool[Object.keys(JSON.parse(localStorage.getItem(key)).pool)[0]],m.storage.poolPrefix+runtime.defaultEvents.draft+'-v1'),3);
    }
    await p.goto(prefix+m.presentation.pages.workbench.url,{waitUntil:'domcontentloaded'});
    assert.equal(await p.locator('body').getAttribute('data-page'),'draft');
    await p.locator('#trk-cards .trk-card').first().waitFor();
    await p.goto(prefix+m.presentation.pages.practice.url,{waitUntil:'domcontentloaded'});
    assert.equal(await p.locator('body').getAttribute('data-page'),'simulator');
    // A corrupt prior record must remain byte-for-byte intact.
    const key=m.storage.poolPrefix+runtime.defaultEvents.sealed+'-v1',bad='{"pool":{"unknown":1},"deck":{},"basics":{}}';
    await p.evaluate(({key,bad})=>localStorage.setItem(key,bad),{key,bad});
    await p.goto(prefix+m.presentation.pages.gallery.url+'#gallery',{waitUntil:'domcontentloaded'});
    assert.ok(await p.locator('#storageWarning').isVisible());
    await p.locator('#cards [data-delta="1"]').first().click();
    assert.equal(await p.evaluate(key=>localStorage.getItem(key),key),bad);
    await p.evaluate(({key,seed})=>localStorage.setItem(key,JSON.stringify(seed)),{key,seed});
   }
   await p.goto(prefix+m.presentation.pages.gallery.url+'#gallery',{waitUntil:'domcontentloaded'});
   const ref=p.locator('#cards h3 [data-card-preview]').first();await ref.waitFor();
   await ref.scrollIntoViewIfNeeded();await p.mouse.move(0,0);await ref.hover();await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
   await p.locator('#cards .card-title').first().focus();await p.keyboard.press('Enter');await p.locator('#zoom').waitFor({state:'visible'});await p.keyboard.press('Escape');
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await p.screenshot({path:path.join(out,m.id+'-desktop.png')});
   const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true}),touch=await mobile.newPage();
   touch.setDefaultTimeout(60000);touch.on('pageerror',e=>errors.push(e.message));
   await touch.goto(prefix+m.presentation.pages.gallery.url+'#gallery',{waitUntil:'domcontentloaded'});
   await touch.locator('#cards .card-title').first().tap();await touch.locator('#zoom').waitFor({state:'visible'});await touch.keyboard.press('Escape');
   assert.ok(await touch.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await touch.screenshot({path:path.join(out,m.id+'-mobile.png')});await mobile.close();
   assert.deepEqual(errors,[],m.id+' JavaScript errors');
   results.push({id:m.id,routes:new Set(Object.values(runtime.routes)).size,manualRecordsPreserved:manual,previews:['mouse','keyboard','touch'],errors});console.log(JSON.stringify(results.at(-1)));
  }catch(e){fs.writeFileSync(path.join(out,m.id+'-failure.json'),JSON.stringify({error:String(e),errors,url:p.url()},null,2));throw e;}
  finally{await context.close();}
 }
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({results},null,2));console.log('QA: '+out);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
