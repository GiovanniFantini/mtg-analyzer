/* Local single-pod Swiss tournament. No expansion or card catalogue dependency. */
(function(root){
'use strict';
const fail=message=>{throw new Error(message)};
const integer=(v,min,max)=>Number.isInteger(v)&&v>=min&&v<=max;
function result(value){
 if(!Array.isArray(value)||value.length!==3||!value.every(v=>integer(v,0,20))||value[0]>2||value[1]>2||value[0]===2&&value[1]===2)fail('Risultato non valido: indica vittorie dei due giocatori e game patte.');
 return value;
}
function validate(s){
 if(!s||s.schemaVersion!==1||s.kind!=='mtg-local-tournament'||typeof s.id!=='string'||s.id.length>100||typeof s.name!=='string'||!s.name.trim()||s.name.length>120||typeof s.set!=='string'||s.set.length>160||!['registration','active','complete'].includes(s.status)||!integer(s.roundLimit,1,7)||!integer(s.roundMinutes,1,180))fail('JSON torneo non compatibile (schema versione 1).');
 if(!Array.isArray(s.players)||s.players.length>8||!Array.isArray(s.rounds)||s.rounds.length>s.roundLimit)fail('Un tavolo richiede da 2 a 8 giocatori, con turni entro il limite annunciato.');
 const ids=new Set(),names=new Set();
 for(const p of s.players){if(!p||typeof p.id!=='string'||!p.id||p.id.length>100||ids.has(p.id)||typeof p.name!=='string'||!p.name.trim()||p.name.length>80||names.has(p.name.trim().toLocaleLowerCase())||typeof p.dropped!=='boolean')fail('Giocatori non validi o duplicati.');ids.add(p.id);names.add(p.name.trim().toLocaleLowerCase());}
 if(s.endedEarly!==undefined&&typeof s.endedEarly!=='boolean')fail('Conclusione anticipata non valida.');
 const early=s.endedEarly===true&&s.rounds.length>0&&s.players.filter(p=>!p.dropped).length<2;
 if(s.endedEarly===true&&(s.status!=='complete'||s.rounds.length>=s.roundLimit||!early))fail('Conclusione anticipata incoerente.');
 if(s.status!=='registration'&&s.players.length<2||s.status==='registration'&&s.rounds.length||s.status==='complete'&&s.rounds.length!==s.roundLimit&&!early)fail('Stato torneo incoerente.');
 s.rounds.forEach((round,i)=>{
  if(!round||round.number!==i+1||!Array.isArray(round.matches)||!round.matches.length||round.matches.length>4)fail('Turno non valido.');
  const seen=new Set();let byes=0;
  for(const m of round.matches){
   if(!m||!ids.has(m.a)||m.b!==null&&!ids.has(m.b)||m.a===m.b||seen.has(m.a)||m.b!==null&&seen.has(m.b))fail('Abbinamenti duplicati o giocatori sconosciuti.');
   seen.add(m.a);if(m.b!==null)seen.add(m.b);else byes++;
   if(m.result!==null)result(m.result);
   if(m.b===null&&(m.result===null||m.result.join(',')!=='2,0,0'))fail('Il bye deve assegnare 2-0.');
   if((i<s.rounds.length-1||s.status==='complete')&&m.result===null)fail('Un turno precedente ha risultati mancanti.');
  }
  if(byes>1)fail('Più di un bye nello stesso turno.');
 });
 const t=s.timer;
 if(!t||!integer(t.remainingMs,0,10800000)||t.deadline!==null&&(!Number.isFinite(t.deadline)||t.deadline<0)||typeof t.label!=='string'||t.label.length>80)fail('Timer non valido.');
 return s;
}
function create(id,name,set,roundLimit=3,roundMinutes=50){return validate({schemaVersion:1,kind:'mtg-local-tournament',id,name,set,status:'registration',roundLimit,roundMinutes,players:[],rounds:[],timer:{remainingMs:roundMinutes*60000,deadline:null,label:'Turno'}});}
function compareRank(a,b){
 if(a.points!==b.points)return b.points-a.points;
 for(const key of ['omw','gwp','ogw']){const delta=b[key]-a[key];if(Math.abs(delta)>1e-9)return delta;}
 return 0;
}
function standings(s){
 const rows=s.players.map((p,seed)=>({...p,seed,points:0,wins:0,losses:0,draws:0,gamePoints:0,games:0,played:0,opponents:[],byes:0})), map=new Map(rows.map(r=>[r.id,r]));
 for(const round of s.rounds)for(const m of round.matches){
  if(!m.result)continue;const [a,b,d]=m.result,x=map.get(m.a),y=map.get(m.b);
  function add(p,w,l){p.played++;p.games+=w+l+d;p.gamePoints+=w*3+d;if(w>l){p.points+=3;p.wins++;}else if(w<l)p.losses++;else{p.points++;p.draws++;}}
  add(x,a,b);if(y){add(y,b,a);x.opponents.push(y.id);y.opponents.push(x.id);}else x.byes++;
 }
 for(const r of rows){r.mwp=Math.max(.33,r.played?r.points/(3*r.played):0);r.gwp=Math.max(.33,r.games?r.gamePoints/(3*r.games):0);}
 for(const r of rows){const mean=key=>r.opponents.length?r.opponents.reduce((v,id)=>v+map.get(id)[key],0)/r.opponents.length:0;r.omw=mean('mwp');r.ogw=mean('gwp');}
 return rows.sort((a,b)=>compareRank(a,b)||a.seed-b.seed);
}
function pair(s){
 validate(s);
 if(s.status==='complete'||s.rounds.length>=s.roundLimit)fail('Tutti i turni annunciati sono già stati generati.');
 if(s.rounds.some(r=>r.matches.some(m=>m.result===null)))fail('Inserisci tutti i risultati del turno prima di proseguire.');
 let rows=standings(s).filter(p=>!p.dropped);if(rows.length<2)fail('Servono almeno due giocatori attivi.');
 let bye=null;
 if(rows.length%2){const min=Math.min(...rows.map(p=>p.byes));bye=rows.slice().reverse().find(p=>p.byes===min);rows=rows.filter(p=>p!==bye);}
 const memo=new Map();
 function solve(list){
  if(!list.length)return {cost:0,pairs:[]};const key=list.map(r=>r.id).join('|');if(memo.has(key))return memo.get(key);
  const a=list[0];let best={cost:Infinity,pairs:[]};
  for(let i=1;i<list.length;i++){const b=list[i],tail=solve(list.filter((_,j)=>j!==0&&j!==i));const cost=tail.cost+(a.opponents.includes(b.id)?100000:0)+Math.abs(a.points-b.points)*100+i;
   if(cost<best.cost)best={cost,pairs:[{a:a.id,b:b.id,result:null},...tail.pairs]};}
  memo.set(key,best);return best;
 }
 const matched=solve(rows);if(bye)matched.pairs.push({a:bye.id,b:null,result:[2,0,0]});
 return {number:s.rounds.length+1,matches:matched.pairs,rematch:matched.cost>=100000};
}
function remaining(timer,now=Date.now()){return timer.deadline===null?timer.remainingMs:Math.max(0,timer.deadline-now);}
const api={validate,create,result,compareRank,standings,pair,remaining};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.TournamentEngine=api;
})(globalThis);
