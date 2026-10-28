'use strict';
const assert=require('node:assert/strict'),{chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.MTG_BROWSER_CHANNEL?{channel:process.env.MTG_BROWSER_CHANNEL}:{})});
 try{
  for(const width of [1440,390]){
   const context=await browser.newContext({viewport:{width,height:900},hasTouch:width===390}),page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base+'tournament.html');await page.locator('#t-name').fill('Torneo QA '+width);await page.locator('#t-limit').fill('2');await page.locator('#t-create button').click();
   for(const name of ['Ada','Bruno','Carla','Dario','Elena']){await page.locator('#t-player').fill(name);await page.locator('#t-add button').click();}
   await page.locator('#t-start').click();assert.equal(await page.locator('#t-current article').count(),3);
   assert.equal(await page.locator('#t-next').isDisabled(),true);
   await page.locator('#t-toggle-clock').click();await page.reload();assert.equal(await page.locator('#t-toggle-clock').innerText(),'Pausa timer');await page.locator('#t-toggle-clock').click();
   const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('mtg-local-tournament-v1')));assert.equal(saved.timer.deadline,null);
   const forms=page.locator('#t-current form');
   await forms.nth(1).locator('input').nth(0).fill('0');await forms.nth(1).locator('input').nth(1).fill('2');
   await forms.nth(0).locator('input').nth(0).fill('2');await forms.nth(0).locator('input').nth(1).fill('1');await forms.nth(0).locator('button').click();
   assert.equal(await forms.nth(1).locator('input').nth(1).inputValue(),'2');
   for(let i=0;i<await forms.count();i++){await forms.nth(i).locator('input').nth(0).fill('2');await forms.nth(i).locator('input').nth(1).fill('1');await forms.nth(i).locator('button').click();}
   assert.equal(await page.locator('#t-next').isDisabled(),false);await page.locator('#t-next').click();
   assert.match(await page.locator('#t-progress').innerText(),/Turno 2 di 2/);
   for(let i=0;i<await forms.count();i++){await forms.nth(i).locator('input').nth(0).fill('1');await forms.nth(i).locator('input').nth(1).fill('1');await forms.nth(i).locator('button').click();}
   await page.locator('#t-next').click();assert.match(await page.locator('#t-progress').innerText(),/concluso/);assert.equal(await page.locator('#t-ranking tr').count(),5);
   const download=page.waitForEvent('download');await page.locator('#t-export').click();assert.equal((await download).suggestedFilename(),'torneo-draft.json');
   await page.locator('#t-import').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from('{"schemaVersion":9}')});assert.match(await page.locator('#t-status').innerText(),/non compatibile/);
   assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('mtg-local-tournament-v1')).status),'complete');
   const current=await page.evaluate(()=>localStorage.getItem('mtg-local-tournament-v1'));
   page.on('dialog',d=>d.accept());await page.locator('#t-import').setInputFiles({name:'good.json',mimeType:'application/json',buffer:Buffer.from(current)});assert.equal(await page.evaluate(()=>Object.keys(localStorage).filter(k=>k.includes('-backup-')).length),1);
   // Storage failure during backup must leave the complete original unchanged.
   await page.evaluate(()=>{window.qaSet=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k.includes('-backup-'))throw new Error('Backup negato QA');return window.qaSet.call(this,k,v);};});
   await page.locator('#t-import').setInputFiles({name:'retry.json',mimeType:'application/json',buffer:Buffer.from(current)});assert.match(await page.locator('#t-status').innerText(),/Backup negato QA/);assert.equal(await page.evaluate(()=>localStorage.getItem('mtg-local-tournament-v1')),current);
   await page.evaluate(()=>{Storage.prototype.setItem=window.qaSet;});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
   await page.locator('#t-export').focus();assert.equal(await page.locator('#t-export').evaluate(el=>el===document.activeElement),true);
   const short=JSON.parse(current);short.status='active';short.roundLimit=3;short.players.forEach((p,i)=>p.dropped=i>0);
   await page.locator('#t-import').setInputFiles({name:'retirements.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(short))});
   assert.match(await page.locator('#t-next').innerText(),/meno di due/);await page.locator('#t-next').click();
   const ended=await page.evaluate(()=>JSON.parse(localStorage.getItem('mtg-local-tournament-v1')));
   assert.equal(ended.status,'complete');assert.equal(ended.endedEarly,true);assert.equal(ended.roundLimit,3);assert.equal(ended.rounds.length,2);
   assert.deepEqual(errors,[]);await context.close();
  }
  // Invalid old JSON is preserved and downloadable, including across reload.
  const context=await browser.newContext(),page=await context.newPage();await page.goto(base+'tournament.html');await page.evaluate(()=>localStorage.setItem('mtg-local-tournament-v1','{"old":true}'));await page.reload();assert.equal(await page.locator('#t-recovery').isVisible(),true);assert.equal(await page.evaluate(()=>localStorage.getItem('mtg-local-tournament-v1')),'{"old":true}');await context.close();
  console.log('Tournament browser PASS: desktop/touch, full event, reload timer, results, ranking, export/import, invalid recovery and backup failure.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
