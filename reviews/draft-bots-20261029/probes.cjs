'use strict';
// Diagnostic counterexamples, not requirements that freeze the current policy.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const E=require('../../draft-engine.js'),formats=JSON.parse(fs.readFileSync(path.join(__dirname,'formats.json'),'utf8'));
const base=formats['reality-fracture'];
const make=(id,extra={})=>({id,name:id,full:id,score:3,rarity:'common',colors:['W'],identity:['W'],cost:'{1}{W}',mv:2,creature:true,land:false,basic:false,role:'',oracle:'',archetypes:['WU'],...extra});
const cards=[make('enabler',{oracle:'When this creature enters, you gain 2 life.'}),make('payoff',{oracle:'Whenever you gain life, draw a card.'}),make('filler'),
 make('conditional-source',{colors:['G'],identity:['G'],cost:'{5}{G}',mv:6,oracle:'{T}: Add one mana of any color.'}),
 make('red-bomb',{colors:['R'],identity:['R'],cost:'{3}{R}',mv:4,score:4.5}),
 make('solid',{archetypes:[],score:3.6}),make('supported-payoff',{score:3,archetypes:['WU']})];
const format={...base,cards},ev=E.createEvaluator(format);
const entries=ids=>ids.map((id,uid)=>({id,uid}));
const rank=(bot,ids,round=3,pick=1)=>ev.rank(bot,entries(ids),round,pick,E.rng('probe'),false).scores.map(s=>({id:s.entry.id,score:s.score,components:s.components,playable:s.playable}));
const bot=E.botState('synergy','WU');bot.phase=3;
bot.pool=entries(['enabler']);const one=rank(bot,['payoff']);
bot.pool=entries(Array(8).fill('enabler'));const eight=rank(bot,['payoff']);
assert.equal(one[0].components.sinergia,eight[0].components.sinergia);
const unrelated={...format,cards:cards.map(c=>c.id==='enabler'?{...c,oracle:'Vigilance'}:c)};
const unrelatedScore=E.createEvaluator(unrelated).rank(bot,entries(['payoff']),3,1,E.rng('probe'),false).scores[0].components.sinergia;
assert.equal(unrelatedScore,eight[0].components.sinergia);
const fix=E.botState('fixing','WU');fix.phase=3;
fix.pool=entries(['filler','filler']);const noSources=rank(fix,['red-bomb']);
fix.pool=entries(['conditional-source','conditional-source']);const inaccessibleSources=rank(fix,['red-bomb']);
assert.ok(inaccessibleSources[0].components.colori>noSources[0].components.colori);
const signalBot=E.botState('signals');signalBot.signals[1]={W:4,U:3,B:0,R:0,G:0};
const round1=ev.context(signalBot,1),round3=ev.context(signalBot,3);
assert.deepEqual(round3.sig,{});
const saturation=E.botState('synergy','WU');saturation.phase=3;saturation.pool=entries(Array(28).fill('enabler'));
const comparison=rank(saturation,['solid','supported-payoff']);
const threshold=E.botState('signals','WU');threshold.pool=entries(Array(28).fill('filler'));
const phases={};for(let i=0;i<500;i++){threshold.phase=0;ev.rank(threshold,entries(['solid']),3,1,E.rng('phase-'+i));phases[threshold.phase]=(phases[threshold.phase]||0)+1;}
const configs=Array.from({length:base.seats-1},()=>({strategy:'force',target:'WU'}));
const forced=[];
for(let i=0;i<10;i++){
 const seed='bot-force-audit-'+i,session=E.createSession(base,seed,configs),humanEv=E.createEvaluator(base,2),human=E.botState('signals'),r=E.rng(seed+'-human');
 while(!session.complete)session.step(humanEv.take(human,{packetId:Math.floor(session.current()[0].uid/base.packSize),cards:session.current()},session.round,session.pick,r).uid);
 assert.equal(new Set([...session.human,...session.bots.flatMap(b=>b.pool)].map(c=>c.uid)).size,base.seats*base.rounds*base.packSize);
 assert.deepEqual(E.replay(base,session.export()).bots,session.bots);
 forced.push({seed,record:session.export(),bots:session.bots.map(b=>({lane:b.lane,cards:b.pool.length}))});
}
// Capture a complete ordinary table, including all nine profile configurations across runs.
const strategies=['signals','bomb','synergy','aggro','control','fixing','denial'];
const seed='bot-audit-0',session=E.createSession(base,seed,strategies.map(strategy=>({strategy,target:null}))),he=E.createEvaluator(base,2),hb=E.botState('signals'),hr=E.rng(seed+'-human');
while(!session.complete)session.step(he.take(hb,{packetId:Math.floor(session.current()[0].uid/base.packSize),cards:session.current()},session.round,session.pick,hr).uid);
const table={seed,record:session.export(),human:session.human,bots:session.bots};
fs.writeFileSync(path.join(__dirname,'example-table.json'),JSON.stringify(table,null,2)+'\n');
const inventory=Object.fromEntries(Object.entries(formats).map(([slug,f])=>[slug,{cards:f.cards.length,revision:f.revision,collationPresent:!!f.collation,roles:f.cards.filter(c=>c.role).length,archetypeTags:f.cards.filter(c=>c.archetypes.length).length,hash:crypto.createHash('sha256').update(JSON.stringify(f)).digest('hex')}]));
const report={engineVersion:3,inventory,synthetic:{copies:{one,eight},unrelatedSameTag:unrelatedScore,mana:{noSources,inaccessibleSources},signals:{round1:round1.sig,round3:round3.sig},qualityCap:comparison,phaseAt28AfterExplore:{trials:500,phases}},forced};
fs.writeFileSync(path.join(__dirname,'probes.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.synthetic,null,2));
