'use strict';
// Old official Pro Tour pages render lists in the browser rather than deck-list HTML.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
(async()=>{const b=await chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});try{const p=await b.newPage();
for(const suffix of ['a-d','e-j','k-n','o-s','t-z']){
 const url='https://magic.gg/decklists/pro-tour-murders-at-karlov-manor-pioneer-decklists-'+suffix;
 await p.goto(url,{waitUntil:'networkidle',timeout:60000});
 const raw=await p.locator('div[id*="_Pro%2520Tour%2520Murders%2520at%2520Karlov%2520Manor_"]').allInnerTexts();assert.ok(raw.length);
 const decks=raw.map(text=>{const lines=text.split('\n').map(s=>s.trim()).filter(Boolean);let section='main';const sections={main:{},sideboard:{}};
  assert.ok(lines.includes('PIONEER')&&lines.includes('FEBRUARY 23, 2024'),'Unexpected tournament format/date');const start=lines.indexOf('Overview');assert.ok(start>=0,'Missing Overview');
  for(let i=start+1;i<lines.length;i++){if(lines[i]==='SIDEBOARD'){section='sideboard';continue;}if(/^\d+$/.test(lines[i])&&lines[i+1]&&!/^\d+$/.test(lines[i+1])){const n=Number(lines[i]),name=lines[++i];sections[section][name]=(sections[section][name]||0)+n;}}
  const main=Object.values(sections.main).reduce((a,b)=>a+b,0),side=Object.values(sections.sideboard).reduce((a,b)=>a+b,0);assert.ok(main>=60&&main<=250,lines[0]+' main '+main);assert.ok(side<=15,lines[0]+' side '+side);
  return {id:'pt-mkm-2024:'+lines[0],player:lines[0],archetype:lines[1],...sections,rank:null,wins:null,losses:null,sourceUrl:url};});
 const event={id:'pt-mkm-2024',name:'Pro Tour Murders at Karlov Manor',date:'2024-02-23',format:'pioneer',kind:'historical-pro-tour',publishedCoverage:'complete-field-published-in-parts',players:258,decks,url,publisher:'Wizards of the Coast / Magic.gg',retrieved:new Date().toISOString().slice(0,10),captureMethod:'Rendered public deck list text; quantity/name pairs verified by section totals',sha256:crypto.createHash('sha256').update(JSON.stringify(raw)).digest('hex')};
 const file=crypto.createHash('sha256').update(url).digest('hex').slice(0,16)+'.json';fs.writeFileSync(path.join('research/tournament-prospects-20261028/events',file),JSON.stringify(event,null,2)+'\n');console.log(suffix,decks.length);
}
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
