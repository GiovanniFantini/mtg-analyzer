'use strict';
// Offline diagnostic: node audit-draft-bots.cjs [tables=200] [expansion] [event=draft] [strategy=mixed] [engineVersion=3]
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const E=require('./draft-engine.js');
const tables=Number(process.argv[2]||200),expansion=process.argv[3]||'reality-fracture',event=process.argv[4]||'draft';
const scenario=process.argv[5]||'mixed';
const engineVersion=Number(process.argv[6]||3);
assert.ok(Number.isInteger(tables)&&tables>0&&tables<=10000);
assert.ok(scenario==='mixed'||Object.hasOwn(E.STRATEGIES,scenario)&&scenario!=='force');
assert.ok([2,3].includes(engineVersion));
const loaded=spawnSync('python',['-c',
 'import json,sys; from expansion_data import load_expansions; e=next(e for e in load_expansions() if e.manifest["id"]==sys.argv[1]); print(json.dumps({"format":e.draft_format(sys.argv[2]),"ratingsDate":e.data["ratings"].get("date"),"statistics":e.data["statistics"].get("draft",{})}))',expansion,event],
 {cwd:__dirname,encoding:'utf8',maxBuffer:32*1024*1024});
if(loaded.status!==0)throw Error(loaded.stderr);
const input=JSON.parse(loaded.stdout),data=input.format,ev=E.createEvaluator(data,engineVersion),humanEvaluator=E.createEvaluator(data,2);
const defaults=['signals','bomb','synergy','aggro','control','fixing','denial'];
const configs=Array.from({length:data.seats-1},(_,i)=>({strategy:scenario==='mixed'?defaults[i%defaults.length]:scenario,target:null}));
const groups={},strategies={},examples=[],rarePasses=[];
const stats=new Map((input.statistics.cards||[]).map(c=>[c.name,c]));
const describe=id=>{const c=ev.byId[id],s=stats.get(c.name);return {id,name:c.name,rarity:c.rarity,colors:c.colors,cost:c.cost,base:c.score,gih:s?.gih,sample:s?.n};};
let total=0;
for(let table=0;table<tables;table++){
 const seed='bot-audit-'+table,session=E.createSession(data,seed,configs,engineVersion);
 // A separate seeded evaluator supplies the human seat without consuming the table RNG.
 const human=E.botState('signals'),humanRng=E.rng(seed+'-human');
 while(!session.complete){
  const pack=session.current(),packetId=Math.floor(pack[0].uid/data.packSize);
  const chosen=humanEvaluator.take(human,{packetId,cards:pack},session.round,session.pick,humanRng);
  session.step(chosen.uid);
 }
 assert.equal(new Set([...session.human,...session.bots.flatMap(b=>b.pool)].map(c=>c.uid)).size,data.seats*data.rounds*data.packSize);
 assert.deepEqual(E.replay(data,session.export()).bots,session.bots);
 for(const bot of session.bots)for(const [index,log] of bot.log.entries()){
  total++;const c=ev.byId[log.id],rare=['rare','mythic'].includes(c.rarity);
  const strat=strategies[bot.strategy]??={picks:0,highRatedRareAvailableInSameLane:0,highRatedRarePassedForWeakerSameLane:0};strat.picks++;
  const available=log.observed.map(id=>ev.byId[id]).filter(x=>['rare','mythic'].includes(x.rarity)&&!x.land&&x.score>=4.5&&x.colors.every(color=>log.lane.includes(color)));
  if(available.length)strat.highRatedRareAvailableInSameLane++;
  if(rare){
   const key=c.rarity+(c.score>=4.5?'_scoreAtLeast4.5':c.score>=4?'_score4':'_scoreBelow4');
   const g=groups[key]??={count:0,pickSum:0,afterPick4:0,afterPick7:0,histogram:{}};
   g.count++;g.pickSum+=log.pick;g.afterPick4+=log.pick>4;g.afterPick7+=log.pick>7;
   g.histogram[log.pick]=(g.histogram[log.pick]||0)+1;
   if(c.score>=4.5&&log.pick>=7)rarePasses.push({seed,strategy:bot.strategy,round:log.round,pick:log.pick,lane:log.lane,card:describe(c.id)});
  }
  const passed=available.filter(x=>x.id!==c.id&&x.score-c.score>=1).sort((a,b)=>b.score-a.score);
  if(!c.land&&passed.length){
   strat.highRatedRarePassedForWeakerSameLane++;
   const ownPool=bot.pool.slice(0,index).map(e=>ev.byId[e.id]).filter(x=>!x.land&&x.colors.every(color=>log.lane.includes(color)));
   for(const x of passed)examples.push({seed,strategy:bot.strategy,round:log.round,pick:log.pick,phase:log.phase,lane:log.lane,pool:{cards:index,inLaneCreatures:ownPool.filter(x=>x.creature).length,inLaneCreaturesAtMost2Mana:ownPool.filter(x=>x.creature&&x.mv<=2).length},chosen:describe(c.id),passed:describe(x.id),chosenTotal:log.score,passedTotal:log.alternatives.find(a=>a.id===x.id)?.score??null,components:log.components,gap:x.score-c.score});
  }
 }
}
for(const g of Object.values(groups))g.averagePick=g.pickSum/g.count;
// Symmetric inputs expose color preferences before any evidence exists.
const symmetric={...data,cards:[...'WUBRG'].map((color,i)=>({id:'probe-'+color,name:color,full:color,colors:[color],identity:[color],score:3,mv:2,cost:'{1}{'+color+'}',creature:true,land:false,basic:false,oracle:'',role:'',archetypes:[]}))};
const firstPickProbe=E.createEvaluator(symmetric,engineVersion).rank(E.botState('signals'),symmetric.cards.map((c,uid)=>({id:c.id,uid})),1,1,E.rng('probe'),false);
const disagreements=(input.statistics.cards||[]).filter(s=>s.n>=5000).map(s=>{const c=data.cards.find(c=>c.name===s.name);return {name:s.name,base:c?.score,gih:s.gih,sample:s.n};});
const report={expansion,event,scenario,engineVersion,tables,botPicks:total,formatRevision:data.revision,configs,humanPolicy:'signals v2, separate seeded RNG',ratingsDate:input.ratingsDate,statisticsDate:input.statistics.date,
 caveats:['Pick counts describe this simulation, not player results.','Passing a rare is not automatically a mistake. Same-lane rating gaps flag cases for review; curve, mana costs and synergy still matter.','GIH rates are historical observational data, not causal card grades.','First-pick color probe is synthetic; all draft examples use unmodified source data.'],
 rareSelection:groups,byStrategy:strategies,firstPickColorProbe:{lane:firstPickProbe.ctx.lane,scores:firstPickProbe.scores.map(s=>({color:s.card.name,score:s.score,components:s.components}))},
 suspiciousExamples:examples.sort((a,b)=>b.gap-a.gap||a.pick-b.pick),lateHighRatedRares:rarePasses,
 ratingReview:{highGradeLowGIH:disagreements.filter(c=>c.base>=4).sort((a,b)=>a.gih-b.gih).slice(0,8),lowGradeHighGIH:disagreements.filter(c=>c.base<=2.5).sort((a,b)=>b.gih-a.gih).slice(0,8)}};
const output=path.join(__dirname,'reviews','draft-bots-20261022');fs.mkdirSync(output,{recursive:true});
fs.writeFileSync(path.join(output,expansion+'-'+event+'-'+scenario+'-v'+engineVersion+'.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({tables,botPicks:total,rareSelection:groups,byStrategy:strategies,firstPickColorProbe:report.firstPickColorProbe,examples:report.suspiciousExamples.slice(0,5),lateHighRatedRares:report.lateHighRatedRares.slice(0,4)},null,2));
