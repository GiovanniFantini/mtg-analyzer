const pw=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
const fixed=process.argv.includes('--fixed');
const result={};
(async()=>{
 const browser=await pw.chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:960}});
  await page.addInitScript(()=>{window.heroFrames=[];setInterval(()=>{const e=document.querySelector('.site-hero');if(e)window.heroFrames.push({opacity:+getComputedStyle(e).opacity,enter:e.classList.contains('site-enter')});},10);});
  await page.route('**/site.js',async route=>{await new Promise(resolve=>setTimeout(resolve,250));await route.continue();});
  await page.goto(base,{waitUntil:'domcontentloaded'});await page.waitForTimeout(650);
  result.initialHero=await page.evaluate(()=>({first:heroFrames[0],minimum:Math.min(...heroFrames.map(x=>x.opacity)),samples:heroFrames.length}));
  await page.unroute('**/site.js');
  await page.goto(base+'sets/reality-fracture/Reality-Fracture-Draft-Engine.html',{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>{window.animationEvents=[];document.addEventListener('animationend',e=>{const t=document.querySelector('#table');if(t.contains(e.target))animationEvents.push({name:e.animationName,target:e.target.id||e.target.className,panelEnter:t.classList.contains('site-enter')});});});
  await page.locator('#start').click();await page.waitForTimeout(800);
  result.panelEvents=await page.evaluate(()=>animationEvents);
  await page.goto(base+'sets/reality-fracture/Reality-Fracture-Draft.html',{waitUntil:'domcontentloaded'});
  result.nonScrollingTabStops=await page.locator('.tablewrap[tabindex="0"]').evaluateAll(nodes=>nodes.filter(e=>e.clientWidth>0&&e.scrollWidth<=e.clientWidth+1).length);
  await page.setViewportSize({width:360,height:960});
  // Exercise the actual dynamic drilldown output, then resize the same region.
  await page.evaluate(()=>{const area=document.createElement('div');area.id='review-dynamic';area.innerHTML=DraftDrilldown.detail('Mindseeker Oculus');document.querySelector('main').append(area);});
  await page.waitForTimeout(150);
  result.dynamicTables=await page.locator('#review-dynamic .tablewrap').evaluateAll(nodes=>nodes.map(e=>({overflow:e.scrollWidth>e.clientWidth+1,tabindex:e.getAttribute('tabindex'),label:e.getAttribute('aria-label')})));
  const trigger=page.locator('#draft-rows [data-name]').first();await trigger.click();await page.waitForTimeout(120);
  const dialogTables=()=>page.locator('#draft-dialog .tablewrap').evaluateAll(nodes=>nodes.map(e=>({overflow:e.scrollWidth>e.clientWidth+1,tabindex:e.getAttribute('tabindex'),label:e.getAttribute('aria-label')})));
  result.dialogTables=await dialogTables();
  const selected=page.locator('#draft-dialog .dd-selected-row');
  result.selectedRow={normal:await selected.evaluate(e=>getComputedStyle(e).backgroundColor)};
  await selected.hover();result.selectedRow.hover=await selected.evaluate(e=>getComputedStyle(e).backgroundColor);
  await page.locator('#draft-close').click();await trigger.click();await page.waitForTimeout(120);result.dialogTablesReopened=await dialogTables();
  if(fixed){
   assert.equal(result.initialHero.minimum,1,'Initially visible hero does not dim after first paint');
   assert.ok(result.panelEvents.some(e=>e.name==='site-enter'&&e.target==='table'),'Parent animation finishes on its own');
   assert.equal(result.nonScrollingTabStops,0,'Only scrolling regions add a tab stop');
   assert.ok(result.dynamicTables.some(e=>e.overflow),'Actual drilldown has a scrolling table');
   assert.ok(result.dynamicTables.every(e=>!e.overflow||e.tabindex==='0'),'Dynamic scrolling regions are focusable');
   const names=result.dynamicTables.filter(e=>e.overflow).map(e=>e.label);assert.equal(new Set(names).size,names.length,'Distinct dynamic region labels');
   assert.ok(result.dialogTables.some(e=>e.overflow),'Real dialog includes scrolling data');
   assert.ok(result.dialogTables.every(e=>!e.overflow||e.tabindex==='0'),'Real dialog tables are focusable');
   assert.deepEqual(result.dialogTables.map(e=>e.label),result.dialogTablesReopened.map(e=>e.label),'Stable labels when reopening the same card');
   assert.equal(result.selectedRow.normal,result.selectedRow.hover,'Selection remains visible on hover');
  }
 }finally{await browser.close()}
 console.log(JSON.stringify(result,null,2));
 result.progress={};
 for(const engine of ['firefox','webkit']){
  let browser;
  try{browser=await pw[engine].launch();}catch(e){result.progress[engine]={unavailable:e.message.split('\n')[0]};continue;}
  try{
   const page=await browser.newPage({viewport:{width:1440,height:960}});
   await page.goto(base+'sets/reality-fracture/Reality-Fracture-Draft-Engine.html',{waitUntil:'domcontentloaded'});await page.locator('#start').click();
   result.progress[engine]=await page.locator('#draft-meter').evaluate(e=>({background:getComputedStyle(e).backgroundColor,appearance:getComputedStyle(e).appearance,accent:getComputedStyle(e).accentColor,width:e.clientWidth,height:e.clientHeight}));
   await page.locator('#draft-meter').evaluate(e=>{e.value=21;e.style.transform='scaleY(8)';e.style.marginBlock='30px';});
   await page.locator('#draft-meter').screenshot({path:`ux-progress-${engine}-${fixed?'after':'before'}-preview.png`});
  }finally{await browser.close()}
 }
 fs.writeFileSync(`ux-review-motion-${fixed?'after':'before'}-verification.json`,JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
