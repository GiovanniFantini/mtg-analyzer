'use strict';
(() => {
 const rootData=JSON.parse(document.getElementById('draft-data').textContent),requestedEvent=new URLSearchParams(location.search).get('event');
 const eventId=rootData.formats&&Object.hasOwn(rootData.formats,requestedEvent)?requestedEvent:(rootData.defaultEvent||'draft');
 const data=rootData.formats?.[eventId]||rootData,E=DraftEngine,$=id=>document.getElementById(id);
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 $('format').innerHTML=Object.entries(rootData.formats||{draft:rootData}).map(([id,f])=>`<option value="${esc(id)}">${esc(f.name)}</option>`).join('')+(rootData.unavailableFormats||[]).map(f=>`<option disabled>${esc(f.name)}: non disponibile</option>`).join('');
 const unavailable=document.createElement('div');unavailable.id='unavailable-formats';unavailable.innerHTML=(rootData.unavailableFormats||[]).length?`<details><summary>Altri eventi e set: dati da completare</summary>${rootData.unavailableFormats.map(f=>`<p>${esc(f.name)}: non disponibile. Occorre completare:</p><ul>${(f.missing||[]).map(reason=>`<li>${esc(reason)}</li>`).join('')}</ul>`).join('')}</details>`:'';$('format').closest('.settings').after(unavailable);$('format').setAttribute('aria-describedby',unavailable.id);
 $('format').value=rootData.formats?.[eventId]?eventId:(rootData.defaultEvent||'draft');
 $('format').addEventListener('change',()=>{const url=new URL(location.href);url.searchParams.set('event',$('format').value);location.href=url.href;});

 const policyAvailable=data.botPolicy?.available&&data.picksPerTurn===1;
 if(data.summary)$('event-summary').textContent=data.summary;
 if(data.intro)document.querySelector('.draft-intro p:last-child').textContent=data.intro;
 const evaluator=E.createEvaluator(data),byId=evaluator.byId,key=EXPANSION_CONFIG.storage.draftTable+(eventId==='draft'?'':'-'+eventId);
 const policyControls=document.createElement('div');policyControls.className='settings';
 policyControls.innerHTML='<label>Avversari<select id="policy-version"><option value="3">Bot classici</option><option value="4"'+(policyAvailable?'':' disabled')+'>Bot contestuali (sperimentali)</option></select></label><label id="match-wrap" hidden>Partite previste<select id="policy-match"><option value="BO3">Al meglio di tre</option><option value="BO1">Partita singola</option><option value="unknown">Non definite: valuta solo il main</option></select></label>';
 $('bot-configs').before(policyControls);const policyInfo=document.createElement('p');policyInfo.id='policy-info';policyInfo.setAttribute('role','status');policyControls.after(policyInfo);
 function policyDescription(){const modern=$('policy-version').value==='4';$('match-wrap').hidden=!modern;
  policyInfo.textContent=modern?'Valutano il mazzo costruibile, il mana e i segnali ricevuti. Un aggiornamento del sito può impedire la ripresa dei draft sperimentali in corso. Puoi esportarne il record. '+(data.botPolicy.gaps||[]).join(' '):'Profili di allenamento classici. I draft già salvati conservano la politica con cui sono iniziati.';
  if(data.picksPerTurn!==1)policyInfo.textContent+=' Bot contestuali non disponibili in questo evento: tempi delle scelte multiple ancora da verificare.';
  if(!data.botPolicy?.available)policyInfo.textContent+=' Bot contestuali non disponibili: '+(data.botPolicy?.missing||['Profili strategici da completare.']).join(' ');
 }
 $('policy-match').value=data.botPolicy?.match||'BO3';$('policy-version').addEventListener('change',()=>{policyDescription();defaults.forEach((_,i)=>configDescription(i));});policyDescription();
 let busy=false,reviewGeneration=0,readyAt=0,replayController=null;
 const cancelReplay=document.createElement("button");cancelReplay.type="button";cancelReplay.id="cancel-replay";cancelReplay.hidden=true;cancelReplay.textContent="Annulla ripresa";$("resume").after(cancelReplay);cancelReplay.addEventListener("click",()=>replayController?.abort());
 const synergyNote="In questo evento usa la valutazione di riferimento: sinergie non coperte.";
 function setBusy(value,message){busy=value;for(const id of ["start","resume","reset","format"])$(id).disabled=value;document.querySelectorAll("[data-pick]").forEach(node=>node.disabled=value);$("table").setAttribute("aria-busy",String(value));if(message)status(message);}
 let session=null,saved=null,loadedSession=null,loadedRecord=null,storageAvailable=true,incompatibleRaw=null,backupKey=null,recoveryURL=null;
 const strategies=['signals','bomb','synergy','aggro','control','fixing','denial'];
 const defaults=Array.from({length:data.seats-1},(_,i)=>strategies[i%strategies.length]);
 $('draft-meter').max=data.rounds*data.packSize;
 const options=Object.entries(E.STRATEGIES).map(([id,p])=>`<option value="${id}">${p.name}</option>`).join('');
 $('bot-configs').innerHTML=defaults.map((strategy,i)=>`<div class="bot-config"><h3>Posto ${i+2} · Bot ${i+1}</h3><label>Strategia<select data-strategy="${i}">${options}</select></label><label data-target-wrap="${i}" hidden>Archetipo da forzare<select data-target="${i}">${Object.entries(data.archetypes).map(([id,a])=>`<option value="${id}">${esc(a.name)} · ${esc(a.theme)}</option>`).join('')}</select></label><p data-description="${i}"></p></div>`).join('');
 function configDescription(i){const value=document.querySelector(`[data-strategy="${i}"]`).value;document.querySelector(`[data-target-wrap="${i}"]`).hidden=value!=='force';document.querySelector(`[data-description="${i}"]`).textContent=E.STRATEGIES[value].description+($('policy-version').value==='4'&&value==='synergy'&&!data.botPolicy?.coverage.synergies?' '+synergyNote:'');}
 defaults.forEach((value,i)=>{const s=document.querySelector(`[data-strategy="${i}"]`);s.value=value;s.addEventListener('change',()=>configDescription(i));configDescription(i);});
 const ref=id=>`<button class="card-ref" data-preview="${esc(id)}">${esc(byId[id].name)}</button>`;
 const named=name=>{const card=data.cards.find(c=>c.name===name||c.full===name);if(!card)return esc(name);return ref(card.id);};
 const example=id=>esc(data.ui?.botExamples?.[id]||'Esempio strategico non ancora disponibile.').replace(/\[\[([^\]]+)\]\]/g,(_,name)=>named(name));
 $('strategies').innerHTML=Object.entries(E.STRATEGIES).map(([id,s])=>`<article><h3>${s.name}</h3><p>${s.description}</p><p class="example">${example(id)}</p></article>`).join('');
 $('assumptions').innerHTML='<ul>'+data.assumptions.map(s=>`<li>${esc(s)}</li>`).join('')+'</ul>';
 const collator=E.createCollator(data,E.rng('method'));
 $('collation').innerHTML=data.collation.recipe.map(rule=>{
  const groups=collator.branches[rule.id], count=rule.count||1;
  const operation=rule.op==='replace'?`Sostituisce ${esc(rule.target)} con probabilità ${(rule.chance*100).toLocaleString('it',{maximumFractionDigits:4})}%`:rule.op==='pair'?`${count} coppia/e garantita/e`:`${count} carta/e`;
  const restrictions=[rule.unique?'senza ripetizioni':'',...(rule.exclude||[]).map(id=>'diversa da '+id)].filter(Boolean).join(' · ');
  return `<details><summary>Slot ${esc(rule.id)} · ${operation}</summary><p>${esc(restrictions)}</p><p>Pesi condizionati all’estrazione di questo slot:</p><ul>${groups.map(([w,g])=>{const cards=Array.isArray(g)?g:g.cards;return `<li>${(w*100).toLocaleString('it',{maximumFractionDigits:4})}% · ${cards.length} stampe · ${esc([...new Set(cards.map(c=>c.rarity))].join('/'))}${g.foil?' · foil':''}</li>`;}).join('')}</ul></details>`;
 }).join('');
 function recovery(raw){if(recoveryURL)URL.revokeObjectURL(recoveryURL);recoveryURL=URL.createObjectURL(new Blob([raw],{type:'application/json'}));}
 function status(message){for(const id of ['save-status','draft-status']){const node=$(id);node.textContent=message;if(recoveryURL){const link=document.createElement('a');link.href=recoveryURL;link.download='draft-'+EXPANSION_CONFIG.id+'-precedente.json';link.textContent=' Scarica il salvataggio precedente';node.append(link);}}}
 let raw=null,storageReadable=true;
 try{raw=localStorage.getItem(key);}catch{storageAvailable=false;storageReadable=false;status('Memoria del browser non accessibile: sessione temporanea. Usa Esporta sessione prima di chiudere.');}
 async function loadSaved(){
  if(!storageReadable||raw===null)return;
  incompatibleRaw=raw;
  try{const record=JSON.parse(raw);
   if(record.engineVersion===4){E.createReplaySession(data,record);loadedSession=null;}else loadedSession=E.replay(data,record);
   loadedRecord=record;saved=record;if(record.engineVersion!==4)incompatibleRaw=null;backupKey=record.previousSaveKey||null;
   if(backupKey){try{const previous=localStorage.getItem(backupKey);if(previous!==null)recovery(previous);}catch{}}
   $('resume').hidden=false;status('Hai un draft salvato in questo browser.'+(record.engineVersion===4?' La ricostruzione può richiedere diverse decine di secondi.':''));
  }catch(error){if(incompatibleRaw!==null)recovery(incompatibleRaw);status(error instanceof SyntaxError?'Salvataggio precedente non leggibile. Prima di salvare un nuovo draft ne conserveremo una copia separata.':'Salvataggio incompatibile con questa versione dei bot o con i dati attuali. Puoi scaricarlo; prima di un nuovo draft ne conserveremo una copia separata.');}
  finally{setBusy(false);}
 }
 loadSaved();
 function persist(){if(!storageReadable){status('Memoria del browser non accessibile: sessione temporanea. Usa Esporta sessione prima di chiudere.');return;}try{
  if(incompatibleRaw!==null){
   backupKey=key+'-incompatible-'+Date.now()+'-'+Math.random().toString(36).slice(2);
   localStorage.setItem(backupKey,incompatibleRaw);
   if(localStorage.getItem(backupKey)!==incompatibleRaw)throw Error('Backup non riuscito');
   recovery(incompatibleRaw);incompatibleRaw=null;
  }
  const record=session.export();if(backupKey)record.previousSaveKey=backupKey;localStorage.setItem(key,JSON.stringify(record));saved=record;loadedRecord=record;loadedSession=session;storageAvailable=true;
  status('Draft salvato in questo browser.'+(backupKey?' Il salvataggio precedente è conservato separatamente.':''));
 }catch{storageAvailable=false;status('Salvataggio non disponibile: usa Esporta sessione.'+(saved||backupKey||incompatibleRaw!==null?' Il salvataggio precedente è conservato.':' La sessione resta temporanea.'));}}
 function render(){
  $('setup').hidden=true;$('table').hidden=false;$('review').hidden=true;
  $('progress').textContent=session.complete?'Draft completato':`Busta ${session.round}/${data.rounds} · Pick ${session.pick}/${Math.ceil(data.packSize/data.picksPerTurn)}`;
  $('draft-meter').value=session.human.length;
  $('draft-meter').setAttribute('aria-valuetext', `${session.human.length} carte su ${data.rounds*data.packSize}`);
  $('direction').textContent=session.complete?'Tutte le pick sono visibili nella revisione del tavolo.':`Passaggio a ${data.directions[session.round-1]===1?'sinistra':'destra'} · ${session.current().length} carte rimaste`;
  $('pack').innerHTML=session.current().map(e=>{const c=byId[e.id];return `<article class="draft-card"><button class="art" data-preview="${c.id}" aria-label="Anteprima ${esc(c.name)}"><img src="${esc(c.image)}" alt="${esc(c.name)}" loading="lazy"></button>${ref(c.id)}<small>${esc(c.rarity)}${e.foil?' · foil':''} · ${esc(e.slot)}</small><button class="pick" data-pick="${e.uid}" aria-label="Scegli ${esc(c.name)}">Scegli</button></article>`;}).join('');
  $('pool-count').textContent=`(${session.human.length})`;
  const grouped=new Map();session.human.forEach(e=>grouped.set(e.id,(grouped.get(e.id)||0)+1));
  $('human-pool').innerHTML=[...grouped].map(([id,n])=>`<span>${n} × ${ref(id)}</span>`).join('');
  readyAt=performance.now();if(session.complete)renderReview();
 }
 async function renderReview(){
  const generation=++reviewGeneration,seat=+$('review-seat').value;
  let bot=session.bots[seat];let deck='',reviewLane=bot.lane;
  $('bot-review').setAttribute('aria-busy','true');$('bot-review').textContent=`Bot ${seat+1}: ${E.STRATEGIES[bot.strategy]?.name||'Adattivo'}. Mazzo in calcolo.`;$('review').hidden=false;
  if(session.engineVersion===4){let built;try{const reviewed=await session.review(seat);built=reviewed.deck;bot=reviewed.bot;}catch(error){if(generation===reviewGeneration){$('bot-review').textContent=`Bot ${seat+1}: ${error.message}`;$('bot-review').setAttribute('aria-busy','false');status(error.message);}return;}if(generation!==reviewGeneration)return;
   reviewLane=built.lane;deck=`<details><summary>Mazzo costruibile: ${built.slots}/${built.targetSize} carte</summary><p>Piano finale: ${esc(built.lane)}. ${built.spells.length-built.manaOnly.length} magie e ${built.manaOnly.length} carte usate soltanto come fixing. Fonti per colore al turno ${built.sourceTurn}: ${Object.entries(built.sources).filter(([,n])=>n>0).map(([c,n])=>`${esc(c)} ${n.toFixed(1)}`).join(' · ')}. Le fonti indirette hanno un peso approssimato.</p><p>${built.spells.map(e=>ref(e.id)).join(', ')}</p><p>Terre possedute: ${built.lands.map(e=>ref(e.id)).join(', ')||'nessuna'}. Basi da aggiungere: ${Object.entries(built.basics).filter(([,n])=>n>0).map(([c,n])=>`${esc(c)} ${n}`).join(', ')||'nessuna'}.</p><p>Solo fixing: ${built.manaOnly.map(e=>ref(e.id)).join(', ')||'nessuna'}. Posti magia ancora scoperti: ${built.holes.spells}.</p><p>Riserve per sideboard: ${built.sideboard.map(e=>ref(e.id)).join(', ')||'nessuna classificata'}</p><p>${esc(built.assumptions.join(' '))}</p></details>`;
  }
  $('bot-review').innerHTML=`<p>${esc(E.STRATEGIES[bot.strategy]?.name||'Adattivo')} · ${esc(reviewLane)} · ${bot.pool.length} carte</p>${session.engineVersion===4&&bot.strategy==='synergy'&&!data.botPolicy?.coverage.synergies?'<p>'+esc(synergyNote)+'</p>':''}${deck}`+bot.log.map(item=>`<div class="review-pick">B${item.round} P${item.pick}: ${ref(item.id)}<p>${esc(item.phase)} · ${esc(item.lane)} · punteggio ${item.score.toFixed(2)}. ${Object.entries(item.components).map(([k,v])=>`${esc(k)} ${v.toFixed(2)}`).join(' · ')}</p>${item.reasons?`<p>${esc(item.reasons.join(' '))}</p><p>Migliore stimata: ${ref(item.bestId)}. ${item.joint?'Scelta valutata insieme alle altre carte dello stesso turno.':item.randomized?'Sorteggio fra alternative considerate equivalenti.':'Scelta della migliore valutazione stimata.'}</p>`:''}<p>Alternative valutate: ${item.alternatives.filter(a=>a.id!==item.id).map(a=>`${ref(a.id)} (${a.score.toFixed(2)})`).join(', ')||'nessuna'}</p>${item.poolBefore?`<details><summary>Busta, pool precedente e conseguenze</summary><p>Busta osservata: ${item.observed.map(ref).join(', ')}</p><p>Pool precedente: ${item.poolBefore.map(e=>ref(e.id)).join(', ')||'vuoto'}</p><p>Carte sostituite nel main: ${(item.replaces||[]).map(ref).join(', ')||'nessuna'}</p>${item.pivot?`<p>Cambio di piano: ${esc(item.pivot.from)} → ${esc(item.pivot.to)}. Carte escluse per il cambio: ${item.pivot.out.map(ref).join(', ')||'nessuna'}.</p>`:''}<p>${esc((item.gaps||[]).join(' '))}</p></details>`:''}</div>`).join('');
  $('bot-review').setAttribute('aria-busy','false');$('review').hidden=false;
 }
 $('review-seat').innerHTML=defaults.map((_,i)=>`<option value="${i}">Bot ${i+1} · posto ${i+2}</option>`).join('');$('review-seat').addEventListener('change',renderReview);
 $('start').addEventListener('click',async()=>{if(busy)return;const configs=defaults.map((_,i)=>{const strategy=document.querySelector(`[data-strategy="${i}"]`).value;return {strategy,target:strategy==='force'?document.querySelector(`[data-target="${i}"]`).value:null};});
  setBusy(true,'Preparazione del tavolo in corso.');try{const seed=$('seed').value||EXPANSION_CONFIG.id+'-tavolo-1',version=+$('policy-version').value,options={match:$('policy-match').value};
   const next=version===4?await DraftWorkerClient.create(data,{seed,configs,options}):E.createSession(data,seed,configs,version,options);
   if(session?.dispose)session.dispose();if(loadedSession!==session&&loadedSession?.dispose)loadedSession.dispose();
   loadedSession=null;session=next;persist();render();$('progress').focus();
  }catch(error){if($('policy-version').value==='4'){$('policy-version').querySelector('option[value="4"]').disabled=true;$('policy-version').value='3';policyDescription();}status('Impossibile avviare i bot selezionati. '+error.message+' Puoi usare i bot classici.');}finally{setBusy(false);}
 });
 $('resume').addEventListener('click',async()=>{if(busy)return;setBusy(true,'Ripresa del draft in corso.');replayController=new AbortController();cancelReplay.hidden=false;const replayStarted=performance.now();
  try{const next=loadedRecord===saved&&loadedSession&&loadedSession.alive!==false?loadedSession:saved.engineVersion===4?await DraftWorkerClient.create(data,{record:saved,signal:replayController.signal,onProgress:({done,total})=>{const seconds=Math.ceil((performance.now()-replayStarted)/1000/Math.max(1,done)*(total-done));status(`Ricostruzione del draft: ${done}/${total} pick. Circa ${seconds} s restanti (stima).`);}}):E.replay(data,saved);
   if(session!==next&&session?.dispose)session.dispose();session=next;loadedRecord=saved;loadedSession=session;incompatibleRaw=null;status('Sessione ripresa dal salvataggio locale.');render();$('progress').focus();
  }catch(error){if(incompatibleRaw!==null)recovery(incompatibleRaw);status(error.message);}finally{cancelReplay.hidden=true;replayController=null;setBusy(false);}
 });
 $('reset').addEventListener('click',()=>{if(busy)return;reviewGeneration++;$('setup').hidden=false;$('table').hidden=true;$('resume').hidden=!saved;if(session){$('policy-version').value=String(session.engineVersion===4?4:3);$('policy-match').value=session.policyOptions.match||'BO3';policyDescription();$('seed').value=session.seed;session.configs.forEach((c,i)=>{document.querySelector(`[data-strategy="${i}"]`).value=c.strategy;if(c.target)document.querySelector(`[data-target="${i}"]`).value=c.target;configDescription(i);});}$('start').textContent='Inizia un nuovo draft';$('start').focus();if(!storageAvailable)status('Salvataggio non disponibile: esporta prima di cambiare tavolo.');});
 $('export').addEventListener('click',async()=>{if($('export').disabled)return;$('export').disabled=true;try{let text;if(session.exportDownload)text=await session.exportDownload();else{const record=session.export();if(session.complete)record.review=session.bots.map(b=>({strategy:b.strategy,pool:b.pool,log:b.log}));text=JSON.stringify(record,null,2);}const url=URL.createObjectURL(new Blob([text],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='draft-'+EXPANSION_CONFIG.id+'-sessione.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){status(error.message);}finally{$('export').disabled=false;}});
 document.addEventListener('click',async event=>{const pick=event.target.closest('[data-pick]');if(pick){if(busy||event.timeStamp<readyAt||event.detail>1)return;setBusy(true,'I bot stanno valutando la busta.');try{await session.step(+pick.dataset.pick);persist();render();$('progress').focus();}catch(error){if(session.alive===false){loadedSession=null;$('setup').hidden=false;$('table').hidden=true;$('resume').hidden=!saved;}status(error.message+(saved?' Usa Riprendi per ricostruire il draft salvato.':' Esporta sessione per conservare lo stato completato.'));}finally{setBusy(false);}}const preview=event.target.closest('[data-preview]');if(preview){const c=byId[preview.dataset.preview];$('card-image').src=c.image;$('card-image').alt=c.name;$('card-text').textContent=`${c.full} ${c.cost}\n${c.type}\n${c.oracle}`;$('card-hover').hidden=true;$('card-dialog').showModal();}});
 const hover=(event)=>{const target=event.target.closest('[data-preview]');if(!target)return;const c=byId[target.dataset.preview];$('card-hover').querySelector('img').src=c.image;$('card-hover').hidden=false;};
 document.addEventListener('pointerover',event=>{if(event.pointerType!=='touch')hover(event);});document.addEventListener('focusin',hover);
 document.addEventListener('pointerout',event=>{if(event.target.closest('[data-preview]'))$('card-hover').hidden=true;});document.addEventListener('focusout',()=>$('card-hover').hidden=true);
 document.addEventListener('keydown',event=>{if(event.key==='Escape')$('card-hover').hidden=true;});$('close-card').addEventListener('click',()=>$('card-dialog').close());
})();
