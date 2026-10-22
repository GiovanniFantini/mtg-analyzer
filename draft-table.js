'use strict';
(() => {
 const rootData=JSON.parse(document.getElementById('draft-data').textContent),requestedEvent=new URLSearchParams(location.search).get('event');
 const eventId=rootData.formats&&Object.hasOwn(rootData.formats,requestedEvent)?requestedEvent:(rootData.defaultEvent||'draft');
 const data=rootData.formats?.[eventId]||rootData,E=DraftEngine,$=id=>document.getElementById(id);
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 $('format').innerHTML=Object.entries(rootData.formats||{draft:rootData}).map(([id,f])=>`<option value="${esc(id)}">${esc(f.name)}</option>`).join('')+(rootData.unavailableFormats||[]).map(f=>`<option disabled>${esc(f.name)}: non disponibile</option>`).join('');
 const unavailable=document.createElement('div');unavailable.id='unavailable-formats';unavailable.innerHTML=(rootData.unavailableFormats||[]).map(f=>`<p>${esc(f.name)}: non disponibile. ${esc(f.missing.join(' '))}</p>`).join('');$('format').closest('.settings').after(unavailable);$('format').setAttribute('aria-describedby',unavailable.id);
 $('format').value=rootData.formats?.[eventId]?eventId:(rootData.defaultEvent||'draft');
 $('format').addEventListener('change',()=>{const url=new URL(location.href);url.searchParams.set('event',$('format').value);location.href=url.href;});

 if(data.summary)$('event-summary').textContent=data.summary;
 if(data.intro)document.querySelector('.draft-intro p:last-child').textContent=data.intro;
 const evaluator=E.createEvaluator(data),byId=evaluator.byId,key=EXPANSION_CONFIG.storage.draftTable+(eventId==='draft'?'':'-'+eventId);
 let session=null,saved=null,storageAvailable=true,incompatibleRaw=null,backupKey=null,recoveryURL=null;
 const strategies=['signals','bomb','synergy','aggro','control','fixing','denial'];
 const defaults=Array.from({length:data.seats-1},(_,i)=>strategies[i%strategies.length]);
 $('draft-meter').max=data.rounds*data.packSize;
 const options=Object.entries(E.STRATEGIES).map(([id,p])=>`<option value="${id}">${p.name}</option>`).join('');
 $('bot-configs').innerHTML=defaults.map((strategy,i)=>`<div class="bot-config"><h3>Posto ${i+2} · Bot ${i+1}</h3><label>Strategia<select data-strategy="${i}">${options}</select></label><label data-target-wrap="${i}" hidden>Archetipo da forzare<select data-target="${i}">${Object.entries(data.archetypes).map(([id,a])=>`<option value="${id}">${esc(a.name)} · ${esc(a.theme)}</option>`).join('')}</select></label><p data-description="${i}"></p></div>`).join('');
 function configDescription(i){const value=document.querySelector(`[data-strategy="${i}"]`).value;document.querySelector(`[data-target-wrap="${i}"]`).hidden=value!=='force';document.querySelector(`[data-description="${i}"]`).textContent=E.STRATEGIES[value].description;}
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
 try{const raw=localStorage.getItem(key);if(raw){incompatibleRaw=raw;const record=JSON.parse(raw);E.replay(data,record);saved=record;incompatibleRaw=null;backupKey=record.previousSaveKey||null;if(backupKey){const previous=localStorage.getItem(backupKey);if(previous!==null)recovery(previous);}$('resume').hidden=false;status('Hai un draft salvato in questo browser.');}}catch{if(incompatibleRaw!==null)recovery(incompatibleRaw);status('Salvataggio precedente non leggibile. Prima di salvare un nuovo draft ne conserveremo una copia separata.');}
 function persist(){try{
  if(incompatibleRaw!==null){
   backupKey=key+'-incompatible-'+Date.now()+'-'+Math.random().toString(36).slice(2);
   localStorage.setItem(backupKey,incompatibleRaw);
   if(localStorage.getItem(backupKey)!==incompatibleRaw)throw Error('Backup non riuscito');
   incompatibleRaw=null;
  }
  const record=session.export();if(backupKey)record.previousSaveKey=backupKey;localStorage.setItem(key,JSON.stringify(record));saved=record;storageAvailable=true;
  status('Draft salvato in questo browser.'+(backupKey?' Il salvataggio precedente è conservato separatamente.':''));
 }catch{storageAvailable=false;status('Salvataggio non disponibile: usa Esporta sessione. Il salvataggio precedente è conservato.');}}
 function render(){
  $('setup').hidden=true;$('table').hidden=false;$('review').hidden=!session.complete;
  $('progress').textContent=session.complete?'Draft completato':`Busta ${session.round}/${data.rounds} · Pick ${session.pick}/${Math.ceil(data.packSize/data.picksPerTurn)}`;
  $('draft-meter').value=session.human.length;
  $('draft-meter').setAttribute('aria-valuetext', `${session.human.length} carte su ${data.rounds*data.packSize}`);
  $('direction').textContent=session.complete?'Tutte le pick sono visibili nella revisione del tavolo.':`Passaggio a ${data.directions[session.round-1]===1?'sinistra':'destra'} · ${session.current().length} carte rimaste`;
  $('pack').innerHTML=session.current().map(e=>{const c=byId[e.id];return `<article class="draft-card"><button class="art" data-preview="${c.id}" aria-label="Anteprima ${esc(c.name)}"><img src="${esc(c.image)}" alt="${esc(c.name)}" loading="lazy"></button>${ref(c.id)}<small>${esc(c.rarity)}${e.foil?' · foil':''} · ${esc(e.slot)}</small><button class="pick" data-pick="${e.uid}" aria-label="Scegli ${esc(c.name)}">Scegli</button></article>`;}).join('');
  $('pool-count').textContent=`(${session.human.length})`;
  const grouped=new Map();session.human.forEach(e=>grouped.set(e.id,(grouped.get(e.id)||0)+1));
  $('human-pool').innerHTML=[...grouped].map(([id,n])=>`<span>${n} × ${ref(id)}</span>`).join('');
  if(session.complete)renderReview();
 }
 function renderReview(){const bot=session.bots[+$('review-seat').value];$('bot-review').innerHTML=`<p>${esc(E.STRATEGIES[bot.strategy].name)} · ${esc(bot.lane)} · ${bot.pool.length} carte</p>`+bot.log.map(item=>`<div class="review-pick">B${item.round} P${item.pick}: ${ref(item.id)}<p>${esc(item.phase)} · ${esc(item.lane)} · punteggio ${item.score.toFixed(2)}. ${Object.entries(item.components).map(([k,v])=>`${esc(k)} ${v.toFixed(2)}`).join(' · ')}</p><p>Alternative valutate: ${item.alternatives.filter(a=>a.id!==item.id).map(a=>`${ref(a.id)} (${a.score.toFixed(2)})`).join(', ')||'nessuna'}</p></div>`).join('');}
 $('review-seat').innerHTML=defaults.map((_,i)=>`<option value="${i}">Bot ${i+1} · posto ${i+2}</option>`).join('');$('review-seat').addEventListener('change',renderReview);
 $('start').addEventListener('click',()=>{const configs=defaults.map((_,i)=>{const strategy=document.querySelector(`[data-strategy="${i}"]`).value;return {strategy,target:strategy==='force'?document.querySelector(`[data-target="${i}"]`).value:null};});session=E.createSession(data,$('seed').value||EXPANSION_CONFIG.id+'-tavolo-1',configs);persist();render();$('progress').focus();});
 $('resume').addEventListener('click',()=>{try{session=E.replay(data,saved);status('Sessione ripresa dal salvataggio locale.');render();$('progress').focus();}catch{status('Impossibile riprendere la sessione.');}});
 $('reset').addEventListener('click',()=>{$('setup').hidden=false;$('table').hidden=true;$('resume').hidden=!saved;if(session){$('seed').value=session.seed;session.configs.forEach((c,i)=>{document.querySelector(`[data-strategy="${i}"]`).value=c.strategy;if(c.target)document.querySelector(`[data-target="${i}"]`).value=c.target;configDescription(i);});}$('start').textContent='Inizia un nuovo draft';$('start').focus();if(!storageAvailable)status('Salvataggio non disponibile: esporta prima di cambiare tavolo.');});
 $('export').addEventListener('click',()=>{const record=session.export();if(session.complete)record.review=session.bots.map(b=>({strategy:b.strategy,pool:b.pool,log:b.log}));const url=URL.createObjectURL(new Blob([JSON.stringify(record,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='draft-'+EXPANSION_CONFIG.id+'-sessione.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
 document.addEventListener('click',event=>{const pick=event.target.closest('[data-pick]');if(pick){session.step(+pick.dataset.pick);persist();render();$('progress').focus();}const preview=event.target.closest('[data-preview]');if(preview){const c=byId[preview.dataset.preview];$('card-image').src=c.image;$('card-image').alt=c.name;$('card-text').textContent=`${c.full} ${c.cost}\n${c.type}\n${c.oracle}`;$('card-hover').hidden=true;$('card-dialog').showModal();}});
 const hover=(event)=>{const target=event.target.closest('[data-preview]');if(!target)return;const c=byId[target.dataset.preview];$('card-hover').querySelector('img').src=c.image;$('card-hover').hidden=false;};
 document.addEventListener('pointerover',event=>{if(event.pointerType!=='touch')hover(event);});document.addEventListener('focusin',hover);
 document.addEventListener('pointerout',event=>{if(event.target.closest('[data-preview]'))$('card-hover').hidden=true;});document.addEventListener('focusout',()=>$('card-hover').hidden=true);
 document.addEventListener('keydown',event=>{if(event.key==='Escape')$('card-hover').hidden=true;});$('close-card').addEventListener('click',()=>$('card-dialog').close());
})();
