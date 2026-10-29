'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
const destination=path.join(__dirname,process.argv[2]||'probes.json');
if(fs.existsSync(destination))throw Error('Probe acquisition already exists');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.MTG_BROWSER_CHANNEL?{channel:process.env.MTG_BROWSER_CHANNEL}:{})});
 const result={};
 try{
  const page=await browser.newPage({viewport:{width:1366,height:768}});
  await page.route('https://**/*',r=>r.abort());
  await page.goto(base+'sets/reality-fracture/Reality-Fracture-Draft-Engine.html');await page.locator('#start').click();
  result.sidebarInitial=await page.locator('.site-sidebar').evaluate(n=>n.inert);
  await page.setViewportSize({width:900,height:768});await page.setViewportSize({width:1366,height:768});
  result.sidebarAfterResize=await page.locator('.site-sidebar').evaluate(n=>n.inert);
  result.metadata=await page.locator('#pack .draft-card').first().evaluate(n=>({text:n.querySelector('small').textContent,display:getComputedStyle(n.querySelector('small')).display}));
  const previous=await page.evaluate(()=>document.querySelector('#pack [data-pick]').dataset.pick);
  result.layout=[];
  for(const viewport of [{width:900,height:600},{width:1280,height:600},{width:1920,height:500},{width:800,height:400},{width:320,height:640},{width:390,height:844}]){
   await page.setViewportSize(viewport);
   result.layout.push(await page.evaluate(viewport=>{const pack=document.querySelector('#pack'),first=pack.querySelector('.draft-card'),button=first.querySelector('[data-pick]'),name=first.querySelector('.card-ref');return {viewport,pack:[pack.clientHeight,pack.scrollHeight],card:first.getBoundingClientRect().toJSON(),button:button.getBoundingClientRect().toJSON(),name:name.getBoundingClientRect().toJSON(),table:document.querySelector('#table').getBoundingClientRect().toJSON(),pageWidth:document.documentElement.scrollWidth};},viewport));
  }
  await page.locator('#reset').click();
  result.sidebarOnMobileExit=await page.locator('.site-sidebar').evaluate(n=>({inert:n.inert,transform:getComputedStyle(n).transform}));
  console.log(JSON.stringify(result,null,2));
  fs.writeFileSync(destination,JSON.stringify(result,null,2)+'\n');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
