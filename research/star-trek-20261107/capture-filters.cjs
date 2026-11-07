const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE),fs=require('fs'),path=require('path');
(async()=>{const b=await chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
try{const p=await b.newPage(),rows=[];
 for(const [kind,url] of [['draft','https://mtga.untapped.gg/limited/draft/star-trek/card-data'],['sealed','https://mtga.untapped.gg/limited/sealed/star-trek/card-data?eventType=SEALED'],['pick-order','https://mtga.untapped.gg/limited/draft/star-trek/pick-order']]){
  await p.goto(url,{waitUntil:'domcontentloaded'});await p.waitForTimeout(2200);
  const data=await p.evaluate(()=>({eventTypeLabel:document.querySelector('#filter-event-type')?.innerText.trim(),selectedRanks:[...document.querySelectorAll('#filter-rank-range img[alt]')].map(e=>e.alt),rankControlText:document.querySelector('#filter-rank-range')?.innerText.trim(),periodLabel:document.querySelector('#limited-filter-event-time-range')?.innerText.trim()}));
  if(data.eventTypeLabel!==(kind==='sealed'?'Sealed':'Premier Draft')||data.periodLabel!=='Latest Event')throw Error('Unexpected selected filters '+JSON.stringify(data));
  if(kind!=='sealed'&&[...new Set(data.selectedRanks.map(s=>s.toLowerCase()))].join(',')!=='bronze,platinum')throw Error('Unexpected selected ranks '+JSON.stringify(data));
  rows.push({kind,url,...data});
 }
 fs.writeFileSync(path.join(__dirname,'captures/selected-filters.json'),JSON.stringify({retrieved:'2026-11-07',method:'Exact text of closed #filter-event-type and #limited-filter-event-time-range controls; image alt values inside closed #filter-rank-range only. Dropdown options excluded.',rows},null,2));console.log(JSON.stringify(rows));
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
