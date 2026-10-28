const {chromium}=require('C:/Users/giova/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('node:fs'),assert=require('node:assert/strict');
const raw=JSON.parse(fs.readFileSync('draft-drilldown-20261016.json','utf8'));
const contexts=raw.contexts;
const metrics=(key,name)=>contexts[key].value.data.find(c=>c.name===name);
const percent=x=>(x*100).toLocaleString('it-IT',{minimumFractionDigits:1,maximumFractionDigits:1})+'%';
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8765/Reality-Fracture-Draft.html');
 assert.equal(await page.locator('#dd-pair').inputValue(),'WU');
 const search=async value=>{await page.locator('#dd-search').fill(value);await page.waitForFunction(value=>document.querySelector('#dd-rows').dataset.query===value.trim().toLowerCase(),value)};
 await search('Way of the Healer');
 assert.equal(await page.locator('#dd-rows tr').count(),1);
 const wr=await page.locator('#dd-rows td:nth-child(3)').innerText();
 assert.equal(wr,percent(metrics('ALL_TIME:WU','Way of the Healer').ever_drawn_win_rate));
 await page.locator('#dd-rows [data-name]').click();
 assert.equal(await page.locator('.dd-card-detail tbody').last().locator('tr').count(),10);
 await page.locator('#draft-close').click();
 await page.locator('#dd-pair').selectOption('BR');await search('Command the Stage');
 assert.equal(await page.locator('#dd-rows td:nth-child(3)').innerText(),percent(metrics('ALL_TIME:BR','Command the Stage').ever_drawn_win_rate));
 await page.locator('#dd-window').selectOption('LAST_WEEK');
  await page.locator('#dd-min').selectOption('500');
 assert.equal(await page.locator('#dd-rows td:nth-child(3)').innerText(),percent(metrics('LAST_WEEK:BR','Command the Stage').ever_drawn_win_rate));
 await page.locator('#dd-window').selectOption('TradDraft');
 assert.equal(await page.locator('#dd-pair').isDisabled(),true);assert.equal(await page.locator('#dd-pair').inputValue(),'all');
 await page.locator('#dd-window').selectOption('ALL_TIME');await page.locator('#dd-pair').selectOption('WU');await search('Twinned Vision');
 assert.equal(await page.locator('#dd-rows tr').count(),1);assert.ok((await page.locator('#dd-rows tr').innerText()).includes('Twinned Vision'));
 await search('Craftwork Crusher');
 assert.ok((await page.locator('#dd-rows').innerText()).includes('Nessuna carta'));
 await page.locator('#dd-compatible').uncheck();
 await page.locator('#dd-min').selectOption('0');
 assert.ok((await page.locator('#dd-rows').innerText()).includes('costo fuori colori'));
 await search('');await page.locator('#dd-pair').selectOption('all');await page.locator('#dd-min').selectOption('2000');
 await page.locator('#dd-more').click();assert.equal(await page.locator('#dd-rows tr').count(),40);
 await page.locator('[data-dd-stage="late"]').click();assert.ok((await page.locator('#dd-stage').innerText()).includes('Completa i ruoli'));assert.ok((await page.locator('#dd-stage').innerText()).includes('Surveillance Phantasm'));
 await page.locator('#dd-card-a').selectOption('Craftwork Crusher');assert.ok((await page.locator('#dd-comparison').innerText()).includes('Craftwork Crusher'));
 await page.locator('#dd-pair').selectOption('WU');
 await page.locator('#dd-guide').scrollIntoViewIfNeeded();await page.screenshot({path:'draft-report-assets-20261016/drilldown-desktop-qa.png'});
 await page.setViewportSize({width:390,height:844});
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 await page.locator('#draft-drilldown').scrollIntoViewIfNeeded();await page.screenshot({path:'draft-report-assets-20261016/drilldown-mobile-qa.png'});
 for(const pair of Object.keys((await page.evaluate(()=>DRAFT_DATA.drill.guides)))){
  await page.locator('#dd-pair').selectOption(pair);assert.ok((await page.locator('#dd-guide').innerText()).length>200);
 }
 assert.deepEqual(errors,[]);
 console.log('PASS: 10 archetipi; valori verificati contro snapshot; periodi; modalità; ibridi; filtri; confronti; dettagli; paginazione; desktop e mobile.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
