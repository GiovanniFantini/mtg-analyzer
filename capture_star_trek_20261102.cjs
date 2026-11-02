// Normal public navigation only. No login, challenge solving or paid content.
const {chromium}=require(process.env.MTG_PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path');
const out=path.join(__dirname,'research/star-trek-20261102');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.MTG_BROWSER_CHANNEL||'msedge'});
 try{
  for(const [id,url] of [
   ['cardmarket-browser','https://www.cardmarket.com/en/Magic/Spoilers/Star-Trek'],
   ['17lands-draft-browser','https://www.17lands.com/card_data?expansion=TRK&format=PremierDraft'],
   ['17lands-sealed-browser','https://www.17lands.com/card_data?expansion=TRK&format=Sealed'],
  ]){
   const page=await browser.newPage();let data={date:'2026-11-02',url};
   try{
    const response=await page.goto(url,{waitUntil:'networkidle',timeout:45000});
    data={...data,httpStatus:response?.status(),finalUrl:page.url(),title:await page.title(),text:await page.locator('body').innerText(),tables:await page.locator('table').count()};
   }catch(e){data.error=e.message;}
   // Cardmarket failure pages and statistics controls are evidence of access,
   // never a claim that a complete price/statistics table was acquired.
   fs.writeFileSync(path.join(out,id+'.json'),JSON.stringify(data,null,2)+'\n');
   console.log(id,data.httpStatus,data.title,data.text?.length,data.error||'');await page.close();
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
