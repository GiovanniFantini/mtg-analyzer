'use strict';
const assert=require('node:assert/strict'),E=require('./draft-engine.js'),{fixture}=require('./tests/draft-policy-fixture.cjs');
const f=fixture(),row=utility=>({utility,rate:55,games:2000,wins:1100,estimate:55,reliability:.9,contexts:{}});
const source=(event,first,late)=>({event,cohort:event==='TradDraft'?'game-one':'all-games',sourceId:event,
 fallbackModel:{intercept:-.5,slope:1},cards:{early:row(first),late:row(late),red:row(1)}});
f.botPolicy.empirical={available:true,method:'fixture',modes:{BO1:source('PremierDraft',1,4.8),BO3:source('TradDraft',4.8,1)}};
f.botPolicy.coverage.synergies=false;
const ev=E.createEvaluator(f,4),pack=[{id:'early',uid:100},{id:'late',uid:101},{id:'red',uid:102}];
for(const match of ['BO1','BO3','BO1','BO3']){
 const bot=E.botState('power'),ranking=ev.rank(bot,pack,1,1,E.rng('empirical'),false,{match});
 assert.equal(ranking.scores[0].entry.id,match==='BO1'?'late':'early');
 ev.take(bot,{packetId:1,cards:pack},1,1,E.rng('log'),{match});
 assert.equal(bot.log[0].quality.match,match);assert.equal(bot.log[0].quality.kind,'empirical');
 assert.equal(bot.log[0].quality.event,match==='BO1'?'PremierDraft':'TradDraft');
}
assert.equal(ev.quality(ev.byId.filler,undefined,{match:'BO1'}).kind,'editorial');
assert.equal(ev.quality(ev.byId.filler,undefined,{match:'BO1'}).utility,1.5);
assert.equal(ev.quality(ev.byId.filler,undefined,{match:'BO1'}).rate,undefined);
assert.equal(ev.quality(ev.byId.early,undefined,{match:'unknown'}).utility,3);
assert.equal(ev.quality(ev.byId['red-base'],undefined,{match:'BO1'}).utility,0);
assert.equal(ev.byId.late.score,3.2,'Empirical utility never rewrites the review');
const pool=Array.from({length:24},(_,uid)=>({id:'early',uid})).concat({id:'late',uid:50});
assert.ok(ev.finalBuild(pool,'signals',{target:'WU',match:'BO1'}).spells.some(e=>e.id==='late'));
assert.ok(!ev.finalBuild(pool,'signals',{target:'WU',match:'BO3'}).spells.some(e=>e.id==='late'));
f.botPolicy.empirical.modes.BO1.cards.early.contexts.WU={utility:2.2,games:500,rate:57,adjustment:1.2};
const contextual=E.createEvaluator(f,4);
assert.equal(contextual.quality(contextual.byId.early,'WU',{match:'BO1'}).utility,2.2);
assert.equal(contextual.quality(contextual.byId.early,'WR',{match:'BO1'}).utility,1);
const configs=Array.from({length:f.seats-1},()=>({strategy:'power'}));
const session=E.createSession(f,'empirical-match',configs,4,{match:'BO1',deterministic:true});
while(!session.complete)session.step(session.current()[0].uid);
assert.ok(session.bots.every(bot=>bot.log.every(pick=>pick.quality.kind==='basic'||pick.quality.match==='BO1')));
assert.deepEqual(E.replay(f,session.export()).bots,session.bots);
console.log('PASS: empirical quality drives picks and main; mode caches isolated; color contexts explicit; reviews, basics, missing data, source metadata and replay preserved.');
f.botPolicy.empirical.modes.BO1.cards.early.utility=3;
f.botPolicy.empirical.modes.BO1.cards.late.utility=3+1e-14;
const tie=E.createEvaluator(f,4);
for(const cards of [pack.slice(0,2),pack.slice(0,2).reverse()])assert.equal(tie.rank(E.botState('power'),cards,1,1,E.rng('roundoff'),false,{match:'BO1'}).scores[0].entry.id,'early');
