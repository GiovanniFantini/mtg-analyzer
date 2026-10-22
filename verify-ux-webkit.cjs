const {webkit}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const base=process.env.MTG_SITE_URL||'http://127.0.0.1:8765/';
(async()=>{
 const browser=await webkit.launch();
 try{
  const page=await browser.newPage();const errors=[],failures=[];
  page.on('pageerror',e=>errors.push(e.message));
  const paths=['index.html',...fs.readdirSync('dist/sets/reality-fracture').filter(x=>x.endsWith('.html')).map(x=>'sets/reality-fracture/'+x),...fs.readdirSync('dist/sets/star-trek').filter(x=>x.endsWith('.html')).map(x=>'sets/star-trek/'+x)];
  for(const width of [320,1440]){
   await page.setViewportSize({width,height:960});
   for(const path of paths){
    await page.goto(base+path,{waitUntil:'domcontentloaded'});
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth);
    if(overflow>1)failures.push({path,width,overflow});
   }
  }
  await page.setViewportSize({width:320,height:960});
  await page.goto(base+'sets/reality-fracture/Reality-Fracture-Draft.html',{waitUntil:'domcontentloaded'});
  const sort=page.locator('#draft-sort');await sort.focus();await sort.press('Home');await sort.press('ArrowDown');await sort.press('Enter');
  assert.equal(await sort.inputValue(),'gih-low','Native select keyboard interaction preserved');
  assert.deepEqual(errors,[]);assert.deepEqual(failures,[]);
  const result={engine:'webkit',pages:paths.length,checks:paths.length*2,nativeSelectKeyboard:true,errors,failures};
  fs.writeFileSync('ux-webkit-verification.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
