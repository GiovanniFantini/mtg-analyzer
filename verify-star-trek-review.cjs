const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'C:/Users/mimir/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8871/';
const set=base+'sets/star-trek/';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
 const context=await browser.newContext({viewport:{width:1440,height:800}});
 context.setDefaultTimeout(10000);
 await context.route('https://cards.scryfall.io/**',route=>route.abort());
 const a=await context.newPage(),b=await context.newPage(),errors=[],results=[];
 for(const p of [a,b])p.on('pageerror',e=>errors.push(e.message));
 const cards=JSON.parse(fs.readFileSync('star-trek-cards-20261021.json','utf8')).cards;
 const first=cards.find(c=>c.name==='Open Communications').id,second=cards.find(c=>c.name==='Seven of Nine').id;
 const key='mtg-trk-sealed-v1';
 const go=(p,path)=>p.goto(set+path,{waitUntil:'domcontentloaded'});
 const state=p=>p.evaluate(key=>JSON.parse(localStorage.getItem(key)),key);
 async function seed(pool,deck={},basics={}){await a.evaluate(({key,pool,deck,basics})=>localStorage.setItem(key,JSON.stringify({pool,deck,basics})),{key,pool,deck,basics});await a.reload({waitUntil:'domcontentloaded'});}
 async function check(name,fn){try{await fn();results.push({name,passed:true});}catch(e){results.push({name,passed:false,error:e.message});console.log(name+': '+e.message.split('\n')[0]);}}
 try{
  await go(a,'sealed.html');
  await check('two_tabs_keep_both_updates',async()=>{
   await seed({[first]:1});await go(b,'sealed.html');
   await a.locator(`#trk-deck [data-id="${first}"][data-op=pool-plus]`).click();
   await b.locator('#trk-search').fill('Seven of Nine');await b.locator(`#trk-cards [data-id="${second}"][data-op=pool-plus]`).click();
   await b.waitForFunction(({key,id})=>JSON.parse(localStorage.getItem(key)).pool[id]===1,{key,id:second});
   assert.equal((await state(b)).pool[first],2);
  });
  await check('simultaneous_tabs_serialize_updates',async()=>{
   await seed({[first]:1});await go(b,'sealed.html');await b.locator('#trk-search').fill('Open Communications');
   await Promise.all([a.locator(`#trk-deck [data-id="${first}"][data-op=pool-plus]`).click(),b.locator(`#trk-cards [data-id="${first}"][data-op=pool-plus]`).click()]);
   await a.waitForFunction(({key,id})=>JSON.parse(localStorage.getItem(key)).pool[id]===3,{key,id:first},{timeout:2000});
  });
  await check('deck_controls_keep_focus_in_deck',async()=>{
   await seed({[first]:3},{[first]:1});await a.locator('#trk-search').fill('Open Communications');
   const control=a.locator('#trk-deck [data-op=deck-plus]');await control.focus();await a.keyboard.press('Enter');
   await a.waitForFunction(({key,id})=>JSON.parse(localStorage.getItem(key)).deck[id]===2,{key,id:first});
   assert.equal(await a.evaluate(()=>document.activeElement.closest('#trk-deck')?.id),'trk-deck');
   await a.keyboard.press('Enter');await a.waitForFunction(({key,id})=>JSON.parse(localStorage.getItem(key)).deck[id]===3,{key,id:first});
   assert.equal(await a.evaluate(()=>document.activeElement.closest('#trk-deck')?.id),'trk-deck');
   assert.equal(await a.evaluate(()=>document.activeElement.disabled),false);
  });
  await check('basic_inputs_keep_focus',async()=>{
   await go(a,'sealed.html');const input=a.locator('[data-basic]').first();await input.focus();await a.keyboard.press('ArrowUp');
   await a.waitForFunction(key=>Object.values(JSON.parse(localStorage.getItem(key)).basics).some(n=>n>0),key);
   assert.equal(await a.evaluate(()=>Boolean(document.activeElement.dataset.basic)),true);
  });
  await check('mulligan_controls_keep_keyboard_focus',async()=>{
   const plains=cards.find(c=>c.name==='Plains').id;
   await seed({[first]:3},{[first]:3},{[plains]:37});await go(a,'simulatore.html?mode=sealed');
   await a.locator('#trk-new-hand').click();assert.equal(await a.locator('[data-bottom]').count(),0);
   await a.locator('#trk-mulligan').click();const choice=a.locator('[data-bottom]').first();await choice.focus();await a.keyboard.press('Enter');
   assert.equal(await a.evaluate(()=>document.activeElement.dataset.bottom),'0');
   await a.locator('#trk-keep').focus();await a.keyboard.press('Enter');assert.equal(await a.evaluate(()=>document.activeElement.id),'trk-draw');
  });
  await check('selected_mode_follows_links',async()=>{
   await go(a,'catalogo.html');await a.locator('#trk-mode').selectOption('picktwo');await a.locator('a[href*="sealed.html"]').first().click();await a.waitForURL(/sealed.html/);
   assert.equal(await a.locator('#trk-mode').inputValue(),'picktwo');
   await a.locator('.site-sidebar [data-page=simulator]').click();await a.waitForURL(/simulatore.html/);assert.equal(await a.locator('#trk-mode').inputValue(),'picktwo');
   await a.locator('.site-sidebar [data-page=draft]').click();await a.waitForURL(/draft.html/);assert.equal(await a.locator('#trk-mode').inputValue(),'picktwo');
  });
  await check('bad_saved_data_is_not_overwritten',async()=>{
   await go(a,'catalogo.html?mode=sealed');const bad=JSON.stringify({pool:{[first]:2,'unknown-id':1},deck:{},basics:{}});
   await a.evaluate(({key,bad})=>localStorage.setItem(key,bad),{key,bad});await a.reload({waitUntil:'domcontentloaded'});await a.locator('#trk-search').fill('Open Communications');await a.locator('#trk-cards [data-op=pool-plus]').click();
   await a.waitForTimeout(100);assert.equal(await a.evaluate(key=>localStorage.getItem(key),key),bad);assert.match(await a.locator('#trk-storage-status').innerText(),/non.*sovrascritto|conservato/i);
  });
  await check('pinned_preview_closes_after_trigger_leaves_screen',async()=>{
   await a.setViewportSize({width:1440,height:400});await go(a,'sinergie.html');await a.mouse.move(0,0);const ref=a.locator('[data-card-preview="Open Communications"]').first();await ref.focus();await a.keyboard.press('Enter');await a.locator('#mtg-card-preview').waitFor({state:'visible'});
   await a.evaluate(()=>scrollTo(0,document.documentElement.scrollHeight));await a.locator('#mtg-card-preview').waitFor({state:'hidden',timeout:2000});
   assert.ok(await ref.evaluate(e=>e.getBoundingClientRect().bottom<=0));await a.setViewportSize({width:1440,height:800});
  });
  await check('FRA_saved_data_and_preview_regression',async()=>{
   const sentinel='{"existing-card":7}';await a.evaluate(v=>localStorage.setItem('fra-sealed-pool-v1',v),sentinel);
   await go(a,'catalogo.html?mode=draft');await a.locator('#trk-search').fill('Open Communications');await a.locator('#trk-cards [data-op=pool-plus]').click();assert.equal(await a.evaluate(()=>localStorage.getItem('fra-sealed-pool-v1')),sentinel);
   await a.goto(base+'sets/reality-fracture/Reality-Fracture-Discovery.html',{waitUntil:'domcontentloaded'});const ref=a.locator('h3 [data-card-preview]').first();await ref.focus();await a.keyboard.press('Enter');await a.locator('#mtg-card-preview').waitFor({state:'visible'});await a.evaluate(()=>scrollTo(0,document.documentElement.scrollHeight));await a.locator('#mtg-card-preview').waitFor({state:'hidden',timeout:2000});
  });
  await check('failed_storage_writes_keep_exportable_memory_state',async()=>{
   const isolated=await browser.newContext();await isolated.route('https://cards.scryfall.io/**',route=>route.abort());
   await isolated.addInitScript(()=>{const original=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(key==='mtg-trk-sealed-v1')throw new DOMException('Quota','QuotaExceededError');return original.call(this,key,value);};});
   const p=await isolated.newPage();try{
    await go(p,'sealed.html?mode=sealed');await p.locator('#trk-search').fill('Open Communications');
    for(let i=0;i<2;i++){await p.locator('#trk-cards [data-op=pool-plus]').click();await p.waitForFunction(n=>document.querySelector('#trk-cards .trk-actions').textContent.includes('Pool: '+n),i+1);}
    assert.match(await p.locator('#trk-storage-status').innerText(),/esportalo/);
    const downloadEvent=p.waitForEvent('download');await p.locator('#trk-export').click();const download=await downloadEvent;
    const exported=JSON.parse(fs.readFileSync(await download.path(),'utf8'));assert.equal(exported.pool[first],2);
   }finally{await isolated.close();}
  });
  assert.deepEqual(errors,[]);fs.writeFileSync('star-trek-review-verification.json',JSON.stringify({results,errors},null,2));console.log(JSON.stringify(results,null,2));
  assert.ok(results.every(r=>r.passed),'Some review regressions failed');
 }finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exitCode=1});
