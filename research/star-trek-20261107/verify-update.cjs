const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE);
let activeBrowser;
(async()=>{
 const browser=await chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
 activeBrowser=browser;
 const out=process.env.MTG_QA_DIR;fs.mkdirSync(out,{recursive:true});const results=[];
 for(const width of [1440,390]){
  const context=await browser.newContext({viewport:{width,height:1000},isMobile:width===390,hasTouch:width===390});
  const p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
  const base=new URL('sets/star-trek/',process.env.MTG_SITE_URL).href;
  const cards=(await(await context.request.get(base+'data/cards.json')).json()).cards;
  const genesis=cards.find(c=>c.name==='Genesis Device');
  await p.goto(base+'catalogo.html?card='+genesis.id+'#gallery');await p.locator('#cards .card-title[data-zoom="'+genesis.id+'"]').click();await p.locator('#zoom').waitFor({state:'visible'});
  await p.locator('#zoom details').evaluateAll(ds=>ds.forEach(d=>d.open=true));
  const limited=p.locator('#zoom .card-limited');assert.ok(await limited.count());
  assert.doesNotMatch(await p.locator('#zoom .untapped-rank').innerText(),/undefined/);
  assert.match(await p.locator('#zoom .untapped-rank').innerText(),/Early Access 2026-11-04/);
  assert.match(await p.locator('#cards .untapped-rank').first().innerText(),/Early Access 2026-11-04/);
  assert.match(await limited.innerText(),/aggregatore/);assert.doesNotMatch(await limited.innerText(),/senza WR osservate/);
  const rate=p.locator('#zoom [data-wr-kind="draft"]');assert.match(await rate.innerText(),/volume riportato/);
  const sourceData=await p.evaluate(()=>catalog.indices.source('draft'));
  assert.equal(sourceData.gamesAreDenominator,false);
  assert.ok(Object.values(sourceData.cards).some(r=>r.confidenceMargin));
  const previews=p.locator('#zoom [data-card-preview]');
  const external=previews.filter({hasText:'Scapeshift'}).first();
  await external.waitFor({state:'visible',timeout:10000});
  await external.scrollIntoViewIfNeeded();
  if(width===390)await external.tap();else await external.hover();
  await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
  if(width===1440){await external.focus();await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');}
  await p.locator('#zoom').evaluate(e=>e.scrollTo(0,0));
  assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await p.screenshot({path:path.join(out,'genesis-'+width+'.png')});
  await p.keyboard.press('Escape');
  const sds=cards.find(c=>c.set==='SDS'&&c.prospects.limitedReviews?.length);
  await p.goto(base+'catalogo.html?card='+sds.id+'#gallery');await p.locator('#cards .card-title[data-zoom="'+sds.id+'"]').click();await p.locator('#zoom').waitFor({state:'visible'});
  assert.ok(await p.locator('#zoom .card-limited').count(),'SDS gets Limited block without own editorial analysis');
  const deEvolve=cards.find(c=>c.name==='De-evolve');
  await p.goto(base+'catalogo.html?card='+deEvolve.id+'#gallery');await p.locator('#cards .card-title[data-zoom="'+deEvolve.id+'"]').click();
  await p.locator('#zoom details').evaluateAll(ds=>ds.forEach(d=>d.open=true));
  const muldrak=p.locator('#zoom [data-card-preview="Gor Muldrak, Amphinologist"]').first();await muldrak.waitFor({state:'visible'});await muldrak.scrollIntoViewIfNeeded();
  if(width===390)await muldrak.tap();else await muldrak.focus();
  await p.locator('#mtg-card-preview').waitFor({state:'visible'});
  assert.deepEqual(errors,[]);results.push({width,externalPreview:true,rareAndSdsLimited:true,errors});await context.close();
 }
 await browser.close();fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({results},null,2));console.log(JSON.stringify(results));
})().catch(async e=>{console.error(e);await activeBrowser?.close();process.exitCode=1});
