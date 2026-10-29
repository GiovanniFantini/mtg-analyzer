'use strict';
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const folder=process.argv[2],record=JSON.parse(fs.readFileSync(path.join(folder,'results.json'),'utf8')).results.find(r=>r.version===4).record;
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8767/',key='mtg-draft-table-fra-v1',output=path.join(__dirname,'browser');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.MTG_BROWSER_CHANNEL?{channel:process.env.MTG_BROWSER_CHANNEL}:{})});
 try{
  for(const [name,width,height,touch] of [['desktop',1440,1050,false],['mobile',390,844,true]]){
   const context=await browser.newContext({viewport:{width,height},isMobile:touch,hasTouch:touch});context.setDefaultTimeout(120000);
   await context.route('https://**/*',r=>r.abort());const page=await context.newPage();
   await page.goto(base+'sets/reality-fracture/Reality-Fracture-Draft-Engine.html');
   await page.evaluate(({key,record})=>localStorage.setItem(key,JSON.stringify(record)),{key,record});await page.reload();
   await page.locator('#resume').click();const detail=page.locator('#bot-review > details');await detail.locator('summary').click();
   const text=await detail.innerText();assert.match(text,/Basi da aggiungere/);assert.match(text,/Solo fixing/);
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await detail.screenshot({path:path.join(output,'policy-v4-main-'+name+'.png')});await context.close();
  }
  console.log('PASS: expanded final main, land list, basics, fixing-only slots and 390px overflow.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
