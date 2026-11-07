const fs = require('fs');
const path = require('path');
const {chromium} = require(process.env.MTG_PLAYWRIGHT_MODULE);
(async()=>{
 const browser=await chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL||'msedge',headless:true});
 const page=await browser.newPage();
 for(const [name,url] of [
  ['untapped-draft','https://mtga.untapped.gg/limited/draft/star-trek/card-data'],
  ['untapped-sealed','https://mtga.untapped.gg/limited/sealed/star-trek/card-data?eventType=SEALED'],
  ['limitedlibrary','https://limitedlibrary.com/sets/star-trek/']]) {
  await page.goto(url,{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForTimeout(7000);
  const decline=page.getByRole('button',{name:'Do not consent',exact:true});
  if(await decline.count()) {await decline.click();await page.waitForTimeout(7000);}
  const metadata=await page.evaluate(()=>({text:document.body.innerText,marginLabels:[...document.querySelectorAll('[title]')].map(e=>e.title).filter(t=>t.includes('confidence')),selectedEvent:document.querySelector('#filter-event-type')?.innerText.trim(),selectedRankText:document.querySelector('#filter-rank-range')?.innerText.trim(),selectedPeriod:document.querySelector('#limited-filter-event-time-range')?.innerText.trim()}));
  if(name.startsWith('untapped')){
   if(!metadata.text.includes('Early Access event on November 4, 2026'))throw Error('Unexpected event filter');
   if(metadata.selectedEvent!==(name==='untapped-sealed'?'Sealed':'Premier Draft')||metadata.selectedPeriod!=='Latest Event')throw Error('Unexpected selected queue/period');
   if(metadata.selectedRankText!==(name==='untapped-sealed'?'Unranked Game Mode':'Bronze\nPlatinum'))throw Error('Unexpected selected rank filter');
  }
  if(name.startsWith('untapped')) {
   const rows=new Map();
   let stable=0,lastSize=0,reachedEnd=false;
   for(let step=0,y=0;step<1000;step++){
    await page.evaluate(y=>window.scrollTo(0,y),y);await page.waitForTimeout(100);
    const batch=await page.evaluate(()=>[...document.querySelectorAll('.rc_row_content')].map(row=>({
     name:row.querySelector('.card-tile')?.getAttribute('aria-label'),url:row.closest('a')?.getAttribute('href'),
     cells:[...row.children].map(cell=>({text:cell.innerText,locked:!!cell.querySelector('.fa-lock'),margin:cell.querySelector('[title]')?.textContent||null}))
    })));
    batch.forEach(r=>{if(!r.name)throw Error('Public row has no card identity');rows.set(r.name,r)});
    const extent=await page.evaluate(()=>({bottom:scrollY+innerHeight,height:Math.max(document.body.scrollHeight,document.documentElement.scrollHeight)}));
    stable=extent.bottom>=extent.height-2&&rows.size===lastSize?stable+1:0;
    if(stable>=3){reachedEnd=true;break;}
    lastSize=rows.size;y=Math.min(y+550,extent.height);
   }
   if(!reachedEnd)throw Error('Virtual list end was not confirmed');
   fs.writeFileSync(path.join(require('os').tmpdir(),`mtg-star-trek-research-20261107/${name}-rows.json`),JSON.stringify([...rows.values()],null,2));
   console.log(name,'rows',rows.size);
  }
  const result={...await page.evaluate(()=>({url:location.href,text:document.body.innerText,tables:[...document.querySelectorAll('table')].map(t=>t.outerHTML),html:document.body.innerHTML})),metadata};
  fs.writeFileSync(path.join(require('os').tmpdir(),`mtg-star-trek-research-20261107/${name}-browser.json`),JSON.stringify(result,null,2));
  console.log(name,result.text.length,result.tables.length,result.text.slice(-500));
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
