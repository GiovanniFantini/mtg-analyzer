const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const out=__dirname;
const delta=JSON.parse(fs.readFileSync(path.join(out,'catalog-delta.json'),'utf8'));
const base=process.env.MTG_SITE_URL;
assert.ok(base,'Configure MTG_SITE_URL');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL});
 const errors=[];
 try{
  for(const width of [1440,390]){
   const ctx=await browser.newContext({viewport:{width,height:960},isMobile:width===390,hasTouch:width===390});
   const p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));
   await p.goto(base+'sets/star-trek/catalogo.html');
   for(const card of delta.newCards){
    await p.locator('#trk-search').fill(card.name);
    assert.equal(await p.locator('#trk-cards .trk-card').count(),1,card.name);
    assert.equal(await p.locator('#trk-cards [data-op=pool-plus]').getAttribute('data-id'),card.id);
   }
   await p.locator('#trk-search').fill('Federation Resupply');
   const ref=p.locator('#trk-cards h3 [data-card-preview]');
   await p.locator('#trk-color').focus();
   if(width===390)await ref.tap();else await ref.hover();
   await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
   await ref.focus();await ref.press('Enter');await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
   await p.locator('.trk-prospects>summary').click();
   const text=await p.locator('.card-prospects').innerText();
   assert.match(text,/28 ottobre 2026/);assert.match(text,/Nessuna osservazione Cardmarket/);
   assert.match(text,/Dato non disponibile/);
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await p.screenshot({path:path.join(out,'new-card-'+width+'.png')});
   await ctx.close();
  }
  assert.deepEqual(errors,[]);
  const report={newCards:delta.newCards.length,widths:[1440,390],previews:['mouse','keyboard','touch'],pricesNotInherited:true,errors};
  fs.writeFileSync(path.join(out,'browser-verification.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
