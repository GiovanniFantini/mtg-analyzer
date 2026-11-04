'use strict';
const assert=require('node:assert/strict'),path=require('node:path'),os=require('node:os'),fs=require('node:fs');
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.MTG_BROWSER_CHANNEL?{channel:process.env.MTG_BROWSER_CHANNEL}:{})});
 const output=fs.mkdtempSync(path.join(os.tmpdir(),'mtg-tournament-audio-'));
 try{
  for(const width of [1440,390]){
   const context=await browser.newContext({viewport:{width,height:900},hasTouch:width===390}),page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.addInitScript(()=>{
    window.audioStarts=0;
    const create=AudioContext.prototype.createOscillator;
    AudioContext.prototype.createOscillator=function(){const oscillator=create.call(this),start=oscillator.start.bind(oscillator);oscillator.start=(...args)=>{window.audioStarts++;return start(...args);};return oscillator;};
   });
   await page.clock.install();
   await page.goto(base+'tournament.html');await page.locator('#t-minutes').fill('1');await page.locator('#t-create button').click();
   await page.locator('#t-toggle-clock').click();await page.waitForFunction(()=>document.getElementById('t-sound-status').textContent.includes('pronto'));
   await page.clock.runFor(1000);await page.locator('#t-toggle-clock').click();
   await page.clock.runFor(61000);assert.equal(await page.evaluate(()=>window.audioStarts),0,'Paused timer must not sound');
   await page.locator('#t-toggle-clock').click();await page.clock.runFor(60000);
   assert.equal(await page.evaluate(()=>window.audioStarts),3,'One three-tone alert on expiry');
   assert.equal(await page.locator('#t-expired').isVisible(),true);
   await page.clock.runFor(5000);assert.equal(await page.evaluate(()=>window.audioStarts),3,'No repeat on subsequent ticks');
   const screenshot=path.join(output,`audio-${width}.png`);await page.locator('#t-clock-panel').screenshot({path:screenshot});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
   await page.locator('#t-sound-toggle').focus();await page.keyboard.press('Enter');
   assert.equal(await page.locator('#t-sound-toggle').getAttribute('aria-pressed'),'false');
   page.on('dialog',d=>d.accept());await page.locator('#t-duration').fill('1');await page.locator('#t-reset-clock').click();await page.locator('#t-toggle-clock').click();
   await page.clock.runFor(61000);assert.equal(await page.evaluate(()=>window.audioStarts),3,'Muted timer must not sound');
   await page.locator('#t-sound-test')[width===390?'tap':'click']();
   assert.equal(await page.locator('#t-sound-toggle').getAttribute('aria-pressed'),'true');
   assert.equal(await page.evaluate(()=>window.audioStarts),6,'Sound preview works with mouse or touch');
   await page.locator('#t-reset-clock').click();await page.locator('#t-toggle-clock').click();
   await page.clock.runFor(61000);assert.equal(await page.evaluate(()=>window.audioStarts),9,'New timer gets a fresh alert');
   await page.reload();await page.clock.runFor(5000);
   assert.equal(await page.evaluate(()=>window.audioStarts),0,'Reloading an already expired timer must not replay the alert');
   assert.equal(await page.locator('#t-expired').isVisible(),true);
   await page.locator('#t-duration').fill('1');await page.locator('#t-reset-clock').click();await page.locator('#t-toggle-clock').click();
   await page.reload();await page.keyboard.press('Tab');
   await page.waitForFunction(()=>document.getElementById('t-sound-status').textContent.includes('pronto'));
   await page.clock.runFor(61000);assert.equal(await page.evaluate(()=>window.audioStarts),3,'A restored running timer can alert after a keyboard interaction');
   assert.deepEqual(errors,[]);await context.close();
  }
  for(const unavailable of [true,false]){
   const context=await browser.newContext(),page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.addInitScript(unavailable=>{window.AudioContext=unavailable?undefined:class{constructor(){throw new Error('Audio negato QA');}};window.webkitAudioContext=undefined;},unavailable);
   await page.goto(base+'tournament.html');await page.locator('#t-create button').click();
   if(unavailable)assert.equal(await page.locator('#t-sound-test').isDisabled(),true);
   else{await page.locator('#t-sound-test').click();assert.match(await page.locator('#t-sound-status').innerText(),/non attivato/);}
   await page.locator('#t-toggle-clock').click();assert.equal(await page.locator('#t-toggle-clock').innerText(),'Pausa timer');
   assert.deepEqual(errors,[]);await context.close();
  }
  console.log('Tournament audio PASS: real Web Audio, single expiry, pause/resume, mute, preview, new timer, expired reload, unavailable/denied audio, desktop/touch/keyboard. Screenshots: '+output);
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
