const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE);
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL,headless:true});
 const errors=[];const base=process.env.MTG_SITE_URL+'sets/reality-fracture/Reality-Fracture-Sealed.html';
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'?order=untapped',{waitUntil:'domcontentloaded'});console.log('loaded');
  assert.equal(await page.locator('#order').inputValue(),'untapped');
  assert.equal(await page.locator('#cards h3').first().innerText(),'Ajani Unrelenting');
  assert.match(await page.locator('#untapped-ranking-note').innerText(),/283 carte con tier, 7 con campione insufficiente/);
  assert.equal(await page.locator('#cards .card').count(),24);
  assert.equal(await page.locator('.untapped-rank').count(),24);
  await page.locator('#search').fill('Eye of Ugin');
  assert.equal(await page.locator('#cards .card').count(),1);
  assert.match(await page.locator('.untapped-rank').innerText(),/N\/D, campione insufficiente/);
  await page.locator('#reset').click();await page.getByRole('button',{name:'Mostra ranking Draft Untapped'}).click();
  const ref=page.locator('#cards h3 [data-card-preview]').first();
  await ref.hover();await page.locator('#mtg-card-preview').waitFor({state:'visible'});await page.keyboard.press('Escape');
  await page.locator('#cards .card-title').first().focus();await page.keyboard.press('Enter');await page.locator('#zoom').waitFor({state:'visible'});await page.keyboard.press('Escape');
  await page.screenshot({path:path.join(__dirname,'ranking-desktop.png')});
  const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
  const m=await mobile.newPage();m.on('pageerror',e=>errors.push(e.message));await m.goto(base,{waitUntil:'domcontentloaded'});
  await m.getByRole('button',{name:'Mostra ranking Draft Untapped'}).tap();
  assert.equal(await m.locator('#order').inputValue(),'untapped');
  await m.locator('#cards .card-title').first().tap();await m.locator('#zoom').waitFor({state:'visible'});await m.keyboard.press('Escape');
  assert.ok(await m.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await m.screenshot({path:path.join(__dirname,'ranking-mobile.png')});
  assert.deepEqual(errors,[]);
  const result={cards:295,observed:290,ranked:283,lowMatchVolume:7,sort:true,search:true,previews:['hover','keyboard','touch'],widths:[1440,390],errors};
  fs.writeFileSync(path.join(__dirname,'browser-verification.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
