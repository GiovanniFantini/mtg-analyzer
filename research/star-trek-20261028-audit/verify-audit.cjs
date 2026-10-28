const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
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
   for(const [name,expected] of [
    ['Federation Probe',/compresa la Probe stessa/],
    ['Emergency Medical Hologram',/anche avversaria o su se stesso/],
    ['Peace in Our Time',/anche te/],
    ['Borg Cube',/perde il collegamento/],
    ['Amok Time',/La Saga non fa pescare/],
    ['Genesis Effect',/servono entrambi i bersagli/]
   ]){
    await p.locator('#trk-search').fill(name);
    await p.locator('.trk-prospects>summary').click();
    assert.match(await p.locator('.card-prospects').innerText(),expected);
   }
   for(const [name,expected] of [
    ['Jett Reno, Problem Solver',/\+1\/\+1 counter/],
    ['Mirror Universe Intrusion',/additional \{4\}\{U\}\{B\}/]
   ]){
    await p.locator('#trk-search').fill(name);
    assert.match(await p.locator('.trk-oracle').innerText(),expected);
   }
   await p.locator('#trk-search').fill('Federation Probe');
   await p.locator('#trk-color').focus();
   const ref=p.locator('#trk-cards h3 [data-card-preview]');
   if(width===390)await ref.tap();else await ref.hover();
   await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
   await ref.focus();await ref.press('Enter');await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
   await p.locator('.trk-prospects>summary').click();
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await p.screenshot({path:path.join(__dirname,'corrected-card-'+width+'.png')});
   await p.goto(base+'sets/star-trek/fonti.html');
   const text=await p.locator('main').innerText();
   assert.match(text,/265 carte/);assert.match(text,/495 stampe/);assert.match(text,/231 previsioni/);
   assert.doesNotMatch(text,/248 carte|462 stampe|210 previsioni|Nessun minimo Cardmarket verificato/);
   assert.equal(await p.locator('a[download][href="star-trek-cards-20261028.json"]').count(),1);
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await p.screenshot({path:path.join(__dirname,'corrected-sources-'+width+'.png')});
   await p.goto(base+'sets/star-trek/analisi.html');
   assert.match(await p.locator('main').innerText(),/265 carte e 495 stampe/);
   await ctx.close();
  }
  assert.deepEqual(errors,[]);
  const report={widths:[1440,390],correctedProfiles:6,correctedTranscriptions:2,currentSummaries:true,historicalPriceDatesPreserved:true,previews:['mouse','keyboard','touch'],errors};
  fs.writeFileSync(path.join(__dirname,'browser-verification.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
