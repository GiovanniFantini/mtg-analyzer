const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE),fs=require('fs'),path=require('path'),os=require('os');
(async()=>{const b=await chromium.launch({channel:process.env.MTG_BROWSER_CHANNEL||'msedge'}),p=await b.newPage();
 await p.goto('https://mylimitedgrades.com/games/magic-the-gathering/sets/TRK',{waitUntil:'domcontentloaded'});await p.waitForTimeout(2500);
 await p.locator('select').last().selectOption('96');await p.waitForTimeout(700);
 const rows=[];let pages=0;
 while(true){
  const text=await p.locator('body').innerText(),match=text.match(/Page (\d+) of (\d+)/);if(!match)throw Error('Pagination unavailable');
  pages++;
  rows.push(...await p.evaluate(()=>[...document.querySelectorAll('a[aria-label^="Open "][href*="/cards/"]')].map(a=>({name:a.getAttribute('aria-label').replace(/^Open /,'').replace(/ details$/,''),url:a.href,community:a.closest('li').querySelector('[aria-label^="Community grade:"]')?.getAttribute('aria-label')||null}))));
  if(+match[1]===+match[2])break;
  await p.getByRole('button',{name:'Next',exact:true}).click();await p.waitForTimeout(400);
 }
 if(rows.length!==336||new Set(rows.map(r=>r.name)).size!==336)throw Error('Incomplete or duplicate grading pool');
 const target=path.join(__dirname,'captures/community-grades.json');fs.writeFileSync(target,JSON.stringify({retrieved:'2026-11-07',url:p.url(),pages,rows},null,2));
 console.log('Community',rows.length,'cards',rows.filter(r=>r.community).length,'with votes',pages,'pages');
 await b.close();})().catch(e=>{console.error(e);process.exitCode=1});
