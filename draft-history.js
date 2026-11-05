'use strict';
// Read-only reconstruction: never advances the session or changes bot decisions.
((root)=>{
 function timeline(session,seat=-1){
  const E=root.DraftEngine||(typeof require==='function'?require('./draft-engine.js'):null);
  const format=session.format,collator=E.createCollator(format,E.rng(session.seed));
  const rounds=Array.from({length:format.rounds},()=>Array.from({length:format.seats},()=>collator.pack()));
  const logs=[session.log,...session.bots.map(b=>b.log)];
  const turns=new Map();
  logs.forEach((log,player)=>log.forEach(item=>{
   const key=`${item.round}:${item.pick}`;
   if(!turns.has(key))turns.set(key,Array.from({length:format.seats},()=>[]));
   turns.get(key)[player].push(item.entry||{id:item.id,uid:item.uid});
  }));
  const pools=Array.from({length:format.seats},()=>[]),history=[];
  for(let round=1;round<=format.rounds;round++){
   let packets=rounds[round-1];
   for(let pick=1;turns.has(`${round}:${pick}`);pick++){
    const choices=turns.get(`${round}:${pick}`),player=seat+1;
    const selected=new Set(choices[player].map(e=>e.uid));
    history.push({round,pick,before:[...pools[player]],chosen:packets[player].filter(e=>selected.has(e.uid)),left:packets[player].filter(e=>!selected.has(e.uid))});
    packets=packets.map((pack,i)=>{const taken=new Set(choices[i].map(e=>e.uid));const entries=pack.filter(e=>taken.has(e.uid));pools[i].push(...entries);return pack.filter(e=>!taken.has(e.uid));});
    const rotated=Array(format.seats);packets.forEach((pack,i)=>rotated[(i+format.directions[round-1]+format.seats)%format.seats]=pack);packets=rotated;
   }
  }
  return history;
 }
 root.DraftHistory={timeline};
})(globalThis);
