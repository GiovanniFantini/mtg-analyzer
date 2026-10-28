/* UI saves only validated transactions; replacement always retains a complete backup. */
(()=>{
'use strict';
const E=TournamentEngine,$=id=>document.getElementById(id),KEY='mtg-local-tournament-v1';
let state=null,loaded=null,blocked=false,objectURL=null;
const pendingResults=new Map();
const text=(id,value)=>$(id).textContent=value;
const message=value=>text('t-status',value);
function recovery(raw){if(objectURL)URL.revokeObjectURL(objectURL);objectURL=URL.createObjectURL(new Blob([raw],{type:'application/json'}));$('t-recovery').href=objectURL;$('t-recovery').hidden=false;}
function read(){
 try{loaded=localStorage.getItem(KEY);if(loaded){try{state=E.validate(JSON.parse(loaded));}catch(error){blocked=true;recovery(loaded);message('Salvataggio incompatibile conservato. Puoi scaricarlo, poi importare un torneo valido o preparare un nuovo torneo.');}}}
 catch(error){blocked=true;message('Salvataggio locale non accessibile. Abilita lo spazio del browser prima di modificare il torneo.');}
}
function save(next,replace=false){
 E.validate(next);const current=localStorage.getItem(KEY);
 if(current!==loaded)throw new Error('Il torneo è cambiato in un’altra scheda. Ricarica prima di modificarlo.');
 if(blocked&&!replace)throw new Error('Recupera prima il salvataggio precedente.');
 if(replace&&current){const backup=KEY+'-backup-'+Date.now()+'-'+crypto.randomUUID();localStorage.setItem(backup,current);recovery(current);}
 const raw=JSON.stringify(next);localStorage.setItem(KEY,raw);if(replace)pendingResults.clear();loaded=raw;state=next;blocked=false;
}
function change(fn,notice,onSaved){
 try{if(!state)throw new Error('Crea prima un torneo.');const next=structuredClone(state);fn(next);save(next);onSaved?.();render();message(notice||'Torneo salvato in questo browser.');}catch(error){message(error.message);}
}
function node(tag,content){const n=document.createElement(tag);if(content!==undefined)n.textContent=content;return n;}
function button(label,fn){const b=node('button',label);b.type='button';b.addEventListener('click',fn);return b;}
function player(id){return state.players.find(p=>p.id===id)?.name||'Giocatore';}
function renderMatch(m,index,current){
 const wrap=node('article');wrap.className='t-match';wrap.append(node('h3',m.b===null?player(m.a)+' · Bye':'Tavolo '+(index+1)+': '+player(m.a)+' / '+player(m.b)));
 if(m.b===null){wrap.append(node('p','Bye assegnato: 2-0, 3 punti.'));return wrap;}
 if(!current){wrap.append(node('p',m.result?m.result[0]+'-'+m.result[1]+' ('+m.result[2]+' game patte)':'Risultato da inserire'));return wrap;}
 const form=node('form');form.className='t-result';
 const resultKey=JSON.stringify([state.id,state.rounds.at(-1).number,m.a,m.b]);
 const inputs=[player(m.a),player(m.b),'Game patte'].map((name,i)=>{const label=node('label',i<2?'Vittorie '+name:name),input=node('input');input.type='number';input.min=0;input.max=i<2?2:20;input.required=true;input.value=pendingResults.get(resultKey)?.[i]??m.result?.[i]??0;label.append(input);form.append(label);return input;});
 const submit=node('button',m.result?'Correggi risultato':'Salva risultato');submit.type='submit';form.append(submit);
 form.append(node('p',m.result?'Salvato: '+m.result[0]+'-'+m.result[1]+', '+m.result[2]+' game patte.':'Da registrare. Per una patta 0-0 indica zero vittorie per entrambi.'));
 form.addEventListener('input',()=>{const values=inputs.map(i=>i.value);if(m.result&&values.every((v,i)=>v===String(m.result[i])))pendingResults.delete(resultKey);else pendingResults.set(resultKey,values);$('t-next').disabled=pendingResults.size>0||state.rounds.at(-1).matches.some(match=>!match.result);message('Risultato modificato: premi Salva risultato per confermarlo.');});
 form.addEventListener('submit',event=>{event.preventDefault();const values=inputs.map(i=>Number(i.value));change(s=>{if(s.status!=='active')throw new Error('Torneo concluso.');E.result(values);s.rounds.at(-1).matches[index].result=values;},'Risultato salvato e classifica aggiornata.',()=>pendingResults.delete(resultKey));});
 wrap.append(form);return wrap;
}
function clock(){
 if(!state)return;const ms=E.remaining(state.timer),seconds=Math.ceil(ms/1000);text('t-clock',Math.floor(seconds/60).toString().padStart(2,'0')+':'+(seconds%60).toString().padStart(2,'0'));
 $('t-expired').hidden=ms>0;text('t-toggle-clock',state.timer.deadline!==null&&ms>0?'Pausa timer':'Avvia timer');
}
function render(){
 $('t-create').hidden=!!state;$('t-event').hidden=!state;$('t-export').disabled=!state;$('t-new').hidden=!state&&!blocked;$('t-clock-panel').hidden=!state;
 $('t-players').replaceChildren();$('t-current').replaceChildren();$('t-ranking').replaceChildren();$('t-history').lastElementChild.replaceChildren();
 $('t-next').hidden=true;$('t-start').hidden=!state||state.status!=='registration';$('t-add').hidden=!state||state.status!=='registration';
 if(!state)return;
 text('t-summary',state.name+(state.set?' · '+state.set:'')+' · '+state.players.length+' iscritti · '+state.roundLimit+' turni · '+state.roundMinutes+' minuti');
 $('t-start').disabled=state.players.length<2;$('t-add').querySelector('button').disabled=state.players.length>=8;
 for(const p of state.players){const li=node('li',p.name+(p.dropped?' (ritirato)':''));
  if(state.status==='registration')li.append(button('Rimuovi '+p.name,()=>change(s=>{s.players=s.players.filter(x=>x.id!==p.id);})));else if(state.status==='active')li.append(button(p.dropped?'Riammetti '+p.name:'Ritira '+p.name,()=>change(s=>{s.players.find(x=>x.id===p.id).dropped=!p.dropped;},'Iscrizione aggiornata. Gli incontri già assegnati restano da completare.')));$('t-players').append(li);}
 const round=state.rounds.at(-1),pending=round?.matches.filter(m=>!m.result).length||0;
 const tooFew=state.players.filter(p=>!p.dropped).length<2;
 text('t-progress',state.status==='registration'?'Iscrizioni aperte.':state.status==='complete'?(state.endedEarly?'Torneo concluso anticipatamente: meno di due giocatori attivi. Classifica finale.':'Torneo concluso. Classifica finale.'):'Turno '+state.rounds.length+' di '+state.roundLimit+' · '+pending+' risultati mancanti.'+(round?.rematch?' È stata necessaria una rivincita con i giocatori attivi.':''));
 if(round){round.matches.forEach((m,i)=>$('t-current').append(renderMatch(m,i,state.status==='active')));$('t-next').hidden=state.status!=='active';$('t-next').disabled=pending>0||pendingResults.size>0;text('t-next',tooFew?'Concludi: meno di due giocatori attivi':state.rounds.length>=state.roundLimit?'Concludi torneo':'Genera il turno successivo');}
 for(const old of state.rounds.slice(0,-1)){const div=node('div');div.append(node('h3','Turno '+old.number));old.matches.forEach((m,i)=>div.append(renderMatch(m,i,false)));$('t-history').lastElementChild.append(div);}
 const rows=E.standings(state);let place=0;
 rows.forEach((r,i)=>{const prev=rows[i-1];if(!prev||E.compareRank(prev,r)!==0)place=i+1;const tr=node('tr');[place,r.name+(r.dropped?' (ritirato)':''),r.points,r.wins+'-'+r.draws+'-'+r.losses,...[r.omw,r.gwp,r.ogw].map(v=>(v*100).toFixed(2)+'%')].forEach(v=>tr.append(node('td',v)));$('t-ranking').append(tr);});
 $('t-phase').value=state.timer.label;$('t-clock').setAttribute('aria-label',state.timer.label+': tempo rimanente');clock();
}
$('t-create').addEventListener('submit',event=>{event.preventDefault();try{save(E.create(crypto.randomUUID(),$('t-name').value.trim(),$('t-set').value.trim(),Number($('t-limit').value),Number($('t-minutes').value)),true);render();message('Torneo creato. Iscrivi i giocatori.');}catch(error){message(error.message);}});
$('t-add').addEventListener('submit',event=>{event.preventDefault();const name=$('t-player').value.trim();change(s=>{if(s.status!=='registration')throw new Error('Iscrizioni chiuse.');s.players.push({id:crypto.randomUUID(),name,dropped:false});},'Giocatore iscritto.');$('t-player').value='';$('t-player').focus();});
$('t-start').addEventListener('click',()=>change(s=>{
 if(s.status!=='registration')throw new Error('Il torneo è già iniziato.');
 for(let i=s.players.length-1;i>0;i--){const random=new Uint32Array(1);crypto.getRandomValues(random);const j=random[0]%(i+1);[s.players[i],s.players[j]]=[s.players[j],s.players[i]];}
 const round=E.pair(s);s.rounds.push(round);s.status='active';s.timer={label:'Turno',deadline:null,remainingMs:s.roundMinutes*60000};
},'Primo turno sorteggiato. Avvia il timer quando i giocatori sono pronti.'));
$('t-next').addEventListener('click',()=>change(s=>{
 if(pendingResults.size)throw new Error('Salva le modifiche ai risultati prima di proseguire.');
 if(s.rounds.at(-1).matches.some(m=>!m.result))throw new Error('Mancano dei risultati.');
 if(s.rounds.length>=s.roundLimit||s.players.filter(p=>!p.dropped).length<2){s.status='complete';if(s.rounds.length<s.roundLimit)s.endedEarly=true;s.timer.remainingMs=E.remaining(s.timer);s.timer.deadline=null;return;}
 const round=E.pair(s);s.rounds.push(round);s.timer={label:'Turno',deadline:null,remainingMs:s.roundMinutes*60000};
},'Turno aggiornato. I risultati precedenti sono nello storico.'));
$('t-toggle-clock').addEventListener('click',()=>change(s=>{const ms=E.remaining(s.timer);if(s.timer.deadline!==null&&ms>0){s.timer.remainingMs=ms;s.timer.deadline=null;}else{if(ms<=0)throw new Error('Imposta una nuova durata per riavviare il timer.');s.timer.deadline=Date.now()+ms;}}));
$('t-reset-clock').addEventListener('click',()=>{if(state?.timer.deadline!==null&&!confirm('Sostituire il timer corrente con una nuova durata?'))return;change(s=>{const minutes=Number($('t-duration').value);if(!Number.isInteger(minutes)||minutes<1||minutes>180)throw new Error('Durata da 1 a 180 minuti.');s.timer={label:$('t-phase').value,remainingMs:minutes*60000,deadline:null};});});
$('t-export').addEventListener('click',()=>{if(!state)return;const url=URL.createObjectURL(new Blob([JSON.stringify(state,null,2)],{type:'application/json'})),a=node('a');a.href=url;a.download='torneo-draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('t-import').addEventListener('change',async event=>{const file=event.target.files[0];if(!file)return;try{if(file.size>1000000)throw new Error('Il JSON supera 1 MB.');const next=E.validate(JSON.parse(await file.text()));if(loaded&&!confirm('Importare questo torneo? Quello corrente verrà conservato in un backup locale.'))return;save(next,true);render();message('Torneo importato. Backup precedente disponibile per il download.');}catch(error){message(error.message);}finally{event.target.value='';}});
$('t-new').addEventListener('click',()=>{if(!confirm('Preparare un nuovo torneo? Il precedente sarà conservato integralmente alla creazione del nuovo.'))return;state=null;render();message('Compila il nuovo torneo. Il precedente resta salvato finché non premi Crea torneo.');});
window.addEventListener('storage',event=>{if(event.key!==KEY)return;blocked=true;message('Torneo modificato in un’altra scheda. Ricarica la pagina prima di proseguire.');});
read();render();if(!blocked)message(state?'Torneo ripristinato da questo browser.':'Crea un torneo per iniziare.');setInterval(clock,500);
})();
