const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
const fixed=process.argv.includes('--fixed');
const rgb=s=>s.match(/[\d.]+/g).slice(0,3).map(Number);
const luminance=values=>values.map(c=>{c/=255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4}).reduce((sum,c,i)=>sum+c*[.2126,.7152,.0722][i],0);
const contrast=(a,b)=>{const x=luminance(rgb(a)),y=luminance(rgb(b));return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
(async()=>{
 const browser=await chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
 const page=await browser.newPage({viewport:{width:1440,height:960}});
 const result={};
 try{
  await page.goto(base+'sets/reality-fracture/Reality-Fracture-Draft.html',{waitUntil:'domcontentloaded'});
  const summary=page.locator('.pick-decision>summary').first();await summary.focus();
  result.F1=await summary.evaluate(e=>({overflow:getComputedStyle(e.parentElement).overflow,outlineStyle:getComputedStyle(e).outlineStyle,outlineWidth:parseFloat(getComputedStyle(e).outlineWidth),outlineOffset:parseFloat(getComputedStyle(e).outlineOffset)}));
  await summary.screenshot({path:`ux-review-focus-${fixed?'after':'before'}-preview.png`});
  result.F3=await page.locator('.site-nav-group>p').first().evaluate(e=>({foreground:getComputedStyle(e).color,background:getComputedStyle(e.closest('.site-sidebar')).backgroundColor}));
  result.F3.contrast=contrast(result.F3.foreground,result.F3.background);
  await page.goto(base+'sets/reality-fracture/Reality-Fracture-Draft-Engine.html',{waitUntil:'domcontentloaded'});await page.locator('#start').click();
  await page.mouse.move(1,1);await page.waitForTimeout(600);
  const card=page.locator('.draft-card').first();await card.hover();await page.waitForTimeout(250);
  result.F2=await card.evaluate(e=>({transform:getComputedStyle(e).transform,translateY:new DOMMatrixReadOnly(getComputedStyle(e).transform).m42,fillMode:getComputedStyle(e).animationFillMode}));
  await page.mouse.move(1,1);const exportButton=page.locator('#export');
  result.F4={normal:await exportButton.evaluate(e=>getComputedStyle(e).borderColor)};
  await exportButton.hover();await page.waitForTimeout(250);result.F4.hover=await exportButton.evaluate(e=>getComputedStyle(e).borderColor);
  result.rootScheme=await page.evaluate(()=>getComputedStyle(document.documentElement).colorScheme);
  await page.goto(base+'sets/reality-fracture/Reality-Fracture-Combo.html',{waitUntil:'domcontentloaded'});
  result.comboIntro=await page.locator('section.intro').evaluate(e=>({width:e.clientWidth,available:e.parentElement.clientWidth-parseFloat(getComputedStyle(e.parentElement).paddingLeft)-parseFloat(getComputedStyle(e.parentElement).paddingRight)}));
  await page.setViewportSize({width:320,height:900});await page.goto(base+'sets/reality-fracture/Reality-Fracture-Combo.html',{waitUntil:'domcontentloaded'});
  result.narrowCombo={overflow:await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth)};
  if(fixed){
   assert.ok(result.F1.outlineStyle==='solid'&&result.F1.outlineOffset<=-result.F1.outlineWidth,'Visible inset focus');
   assert.ok(result.F3.contrast>=4.5,'Navigation group contrast');
   assert.ok(result.F2.translateY<=-3.5,'Draft card lift');
   assert.notEqual(result.F4.normal,result.F4.hover,'Secondary button hover feedback');
   assert.ok(result.narrowCombo.overflow<=1,'Combo at 320px');
   assert.equal(result.rootScheme,'light','Viewport uses the light theme');
   assert.ok(Math.abs(result.comboIntro.width-result.comboIntro.available)<=1,'Two-column combo introduction fills the content width');
  }
  fs.writeFileSync(`ux-review-${fixed?'after':'before'}-verification.json`,JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
