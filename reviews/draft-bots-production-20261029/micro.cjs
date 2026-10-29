'use strict';
const fs=require('node:fs'),path=require('node:path'),{performance}=require('node:perf_hooks');
const root=path.resolve(__dirname,'../..'),E=require(path.join(root,'draft-engine.js'));
const folder=path.join(__dirname,'training-1eb9c46a58'),f=JSON.parse(fs.readFileSync(path.join(folder,'format.json'))),r=JSON.parse(fs.readFileSync(path.join(folder,'results.json')));
const b=E.botState('signals');b.pool=r.results[1].decks[0].pool.slice(0,28);
const e=E.createEvaluator(f,4),pack={packetId:23,cards:f.cards.filter(c=>!c.basic).slice(0,14).map((c,i)=>({id:c.id,uid:9000+i}))};
const started=performance.now();e.take(b,pack,3,1,E.rng('micro'));console.log(JSON.stringify({microMs:performance.now()-started,chosen:b.pool.at(-1),scope:'Engineering sample on a prior training format, not release acceptance'}));
