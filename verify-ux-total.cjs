const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'}),errors=[];
 try{
  for(const width of [1440,390]){
   const context=await browser.newContext({viewport:{width,height:960},isMobile:width===390,hasTouch:width===390});
   const p=await context.newPage();p.on('pageerror',e=>errors.push(e.message));
   const trk=base+'sets/star-trek/';
   await p.goto(trk+'draft.html');
   assert.ok(await p.locator('#trk-compare-a').evaluate(e=>e.getBoundingClientRect().top<800),'The comparison starts before the long documentation');
   await p.locator('#trk-mode').selectOption('picktwo');
   await p.goto(trk+'sealed.html');
   assert.equal(await p.locator('#trk-mode').inputValue(),'sealed','Sealed does not inherit the previous activity');
   assert.match(await p.locator('[data-event-rules]').textContent(),/Sealed/);
   await p.goto(trk+'catalogo.html?mode=picktwo');
   assert.equal(await p.locator('#trk-cards [data-op=deck-plus]').count(),0);
   assert.equal(await p.locator('.catalog-metrics').count(),0);
   assert.ok(await p.locator('#catalog-data-status').isVisible());
   await p.locator('#trk-cards [data-op=pool-plus]').first().click();
   await p.getByRole('link',{name:'Apri il banco di costruzione',exact:true}).click();
   assert.match(p.url(),/draft\.html\?mode=picktwo/);
   assert.equal(await p.locator('#trk-mode').inputValue(),'picktwo');
   await p.locator('#trk-deck [data-op=deck-plus]').first().click();await p.waitForFunction(()=>document.querySelector('#trk-deck').textContent.includes('Mazzo: 1'));
   assert.match(await p.locator('#trk-deck').innerText(),/Mazzo: 1/);
   await p.goto(trk+'sealed.html');
   assert.match(await p.locator('#trk-deck-status').innerText(),/Pool: 0 copie/);
   assert.equal(await p.evaluate(()=>Object.values(JSON.parse(localStorage.getItem('mtg-trk-picktwo-v1')).deck)[0]),1);
   await p.goto(trk+'catalogo.html');
   await p.locator('#trk-next').click();
   assert.equal(await p.evaluate(()=>document.activeElement.id),'trk-count');
   assert.ok(await p.locator('#trk-count').evaluate(e=>e.getBoundingClientRect().top>=0&&e.getBoundingClientRect().top<200));
   assert.match(await p.locator('#trk-page').innerText(),/^Pagina 2 di \d+$/);
   const fra=base+'sets/reality-fracture/Reality-Fracture-Sealed.html';
   await p.goto(fra+'#gallery');
   assert.equal(await p.locator('#cards .untapped-rank .small,#cards .untapped-wr .small,#cards .sent-note details').count(),0,'Method and dates do not repeat in each preview');
   const plus=p.locator('#cards [data-delta="1"]').first();await plus.focus();await plus.press('Enter');
   assert.equal(await p.evaluate(()=>document.activeElement.dataset.delta),'1','Adding a copy retains keyboard focus');
   await p.locator('#cards .imagebutton').first().click();
   assert.equal(await p.locator('#zoom').getAttribute('aria-labelledby'),'zoom-title');
   assert.ok(!(await p.locator('.constructed-prospects').getAttribute('open')));
   const ref=p.locator('#zoom-title [data-card-preview]').first();await ref.focus();await ref.press('Enter');
   await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
   assert.ok(await p.locator('#zoom').isVisible(),'Escape closes the preview before its parent dialog');
   await p.keyboard.press('Escape');assert.ok(!(await p.locator('#zoom').isVisible()));
   await p.goto(fra+'#pool');await p.waitForFunction(()=>document.querySelector('#pool').hidden===false);
   assert.match(await p.title(),/Segna quello che hai aperto/);
   await p.goto(fra+'#strategy');await p.evaluate(()=>scrollTo(0,1200));
   await p.locator('.site-to-top').click();assert.equal(new URL(p.url()).hash,'#strategy');
   await p.reload();assert.ok(await p.locator('#strategy').isVisible());
   if(width===390){
    await p.locator('.site-menu-toggle').click();
    assert.equal(await p.locator('.site-body').evaluate(e=>e.inert),true);
    await p.keyboard.press('Escape');assert.equal(await p.locator('.site-body').evaluate(e=>e.inert),false);
   }
   await p.goto(base+'sets/reality-fracture/Reality-Fracture-Discovery.html');
   await p.locator('.candidate').first().waitFor();
   assert.ok(await p.locator('#discovery-shared-notes').isVisible());
   assert.ok((await p.locator('.candidate .evidence').allTextContents()).every(text=>!text.includes('Campione Postboard')));
   await p.locator('[data-format=Modern]').click();await p.locator('.save').first().click();
   await p.reload();await p.locator('#saved').check();assert.equal(await p.locator('.candidate').count(),1);
   const watchedCard=p.locator('.candidate h3 [data-card-preview]').first();
   if(width===390)await watchedCard.tap();else await watchedCard.hover();
   await p.locator('#mtg-card-preview').waitFor({state:'visible'});await p.keyboard.press('Escape');
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await context.close();
  }
  assert.deepEqual(errors,[]);console.log(JSON.stringify({widths:[1440,390],modeIsolation:true,copyControls:true,keyboardPagination:true,dialogAndPreviewEscape:true,keyboardCopyFocus:true,hashNavigation:true,menuBackgroundInert:true,errors}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
