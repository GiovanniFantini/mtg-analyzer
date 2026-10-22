'use strict';
(() => {
 const data=JSON.parse(document.getElementById('draft-data').textContent),E=DraftEngine,$=id=>document.getElementById(id);
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const evaluator=E.createEvaluator(data),byId=evaluator.byId,key='mtg-draft-table-fra-v1';
 let session=null,saved=null,storageAvailable=true;
 const defaults=['signals','bomb','synergy','aggro','control','fixing','denial'];
 const options=Object.entries(E.STRATEGIES).map(([id,p])=>`<option value="${id}">${p.name}</option>`).join('');
 $('bot-configs').innerHTML=defaults.map((strategy,i)=>`<div class="bot-config"><h3>Posto ${i+2} · Bot ${i+1}</h3><label>Strategia<select data-strategy="${i}">${options}</select></label><label data-target-wrap="${i}" hidden>Archetipo da forzare<select data-target="${i}">${Object.entries(data.archetypes).map(([id,a])=>`<option value="${id}">${esc(a.name)} · ${esc(a.theme)}</option>`).join('')}</select></label><p data-description="${i}"></p></div>`).join('');
 function configDescription(i){const value=document.querySelector(`[data-strategy="${i}"]`).value;document.querySelector(`[data-target-wrap="${i}"]`).hidden=value!=='force';document.querySelector(`[data-description="${i}"]`).textContent=E.STRATEGIES[value].description;}
 defaults.forEach((value,i)=>{const s=document.querySelector(`[data-strategy="${i}"]`);s.value=value;s.addEventListener('change',()=>configDescription(i));configDescription(i);});
 const ref=id=>`<button class="card-ref" data-preview="${esc(id)}">${esc(byId[id].name)}</button>`;
 const named=name=>{const card=data.cards.find(c=>c.name===name);if(!card)throw Error('Missing example '+name);return ref(card.id);};
 const examples={
  power:()=>`${named('The Theorist, Jace Beleren')} è una scelta di potenza in blu: il profilo lo valuta senza correggere il costo di abbandonare altri colori.`,
  bomb:()=>`Dopo ${named('The Theorist, Jace Beleren')}, cerca una base blu. In bianco/blu, ${named('Surveillance Phantasm')} è una giocata difensiva iniziale che aiuta a proteggere il planeswalker.`,
  signals:()=>`${named('Extended Absence')} ricevuta tardi aumenta l’interesse per il nero; una sola carta non basta e il bot accumula più osservazioni prima di consolidare.`,
  force:()=>`Forzando blu/nero preferisce ${named('Recursive Recruitment')}, che sviluppa il campo e offre un secondo lancio con flashback, a una giocabile di colori esterni.`,
  synergy:()=>`In blu/nero, ${named('Apex Witchstalker')} usa landcycling e finisce nel cimitero: ${named('Rewrite Regrets')} può poi rianimarlo. Il profilo premia i supporti quando l’archetipo è già rappresentato nel pool.`,
  aggro:()=>`In una base bianca cerca creature iniziali come ${named('Campus Crier')}; ${named('Your Fate Ends Here')} può liberare il passaggio da una creatura con valore di mana almeno tre.`,
  control:()=>`In blu/nero valorizza ${named('Countersculpt')} come risposta e ${named('Recursive Recruitment')} per corpi e risorse nel lungo periodo; conserva comunque giocate iniziali.`,
  fixing:()=>`${named('Konstrari Annex')} offre rosso e verde: il profilo conta le fonti già prese prima di concedere uno splash. Una singola terra non basta per una magia con doppio simbolo fuori colore.`,
  denial:()=>`Se ${named('Bloodline Recollector')} scompare da una busta al giro, è un indizio di richiesta del nero. Solo tardi, con alternative proprie deboli, valuta di sottrarre una rimozione forte come ${named('Extended Absence')}.`
 };
 $('strategies').innerHTML=Object.entries(E.STRATEGIES).map(([id,s])=>`<article><h3>${s.name}</h3><p>${s.description}</p><p class="example">${examples[id]()}</p></article>`).join('');
 $('assumptions').innerHTML='<ul>'+data.assumptions.map(s=>`<li>${esc(s)}</li>`).join('')+'</ul>';
 const collator=E.createCollator(data,E.rng('method'));
 $('collation').innerHTML=Object.entries(collator.branches).map(([slot,groups])=>`<details><summary>Slot ${esc(slot)}</summary><ul>${groups.map(([w,g])=>{const cards=Array.isArray(g)?g:g.cards;return `<li>${(w*100).toLocaleString('it',{maximumFractionDigits:4})}% · ${cards.length} stampe · ${esc([...new Set(cards.map(c=>c.rarity))].join('/'))} · ${esc(cards[0].set)} ${Math.min(...cards.map(c=>c.number))}–${Math.max(...cards.map(c=>c.number))}${g.foil?' · foil':''}</li>`;}).join('')}</ul></details>`).join('');
 function status(message){$('save-status').textContent=message;$('draft-status').textContent=message;}
 try{const raw=localStorage.getItem(key);if(raw){saved=JSON.parse(raw);E.replay(data,saved);$('resume').hidden=false;status('Hai un draft salvato in questo browser.');}}catch{status('Salvataggio precedente non leggibile. Puoi iniziare un nuovo draft.');}
 function persist(){try{saved=session.export();localStorage.setItem(key,JSON.stringify(saved));status('Draft salvato in questo browser.');}catch{storageAvailable=false;status('Salvataggio non disponibile: usa Esporta sessione.');}}
 function render(){
  $('setup').hidden=true;$('table').hidden=false;$('review').hidden=!session.complete;
  $('progress').textContent=session.complete?'Draft completato':`Busta ${session.round}/3 · Pick ${session.pick}/14`;
  $('draft-meter').value=session.human.length;
  $('draft-meter').setAttribute('aria-valuetext', `${session.human.length} pick su 42`);
  $('direction').textContent=session.complete?'Tutte le pick sono visibili nella revisione del tavolo.':`Passaggio a ${data.directions[session.round-1]===1?'sinistra':'destra'} · ${session.current().length} carte rimaste`;
  $('pack').innerHTML=session.current().map(e=>{const c=byId[e.id];return `<article class="draft-card"><button class="art" data-preview="${c.id}" aria-label="Anteprima ${esc(c.name)}"><img src="${esc(c.image)}" alt="${esc(c.name)}" loading="lazy"></button>${ref(c.id)}<small>${esc(c.rarity)}${e.foil?' · foil':''} · ${esc(e.slot)}</small><button class="pick" data-pick="${e.uid}" aria-label="Scegli ${esc(c.name)}">Scegli</button></article>`;}).join('');
  $('pool-count').textContent=`(${session.human.length})`;
  const grouped=new Map();session.human.forEach(e=>grouped.set(e.id,(grouped.get(e.id)||0)+1));
  $('human-pool').innerHTML=[...grouped].map(([id,n])=>`<span>${n} × ${ref(id)}</span>`).join('');
  if(session.complete)renderReview();
 }
 function renderReview(){const bot=session.bots[+$('review-seat').value];$('bot-review').innerHTML=`<p>${esc(E.STRATEGIES[bot.strategy].name)} · ${esc(bot.lane)} · ${bot.pool.length} carte</p>`+bot.log.map(item=>`<div class="review-pick">B${item.round} P${item.pick}: ${ref(item.id)}<p>${esc(item.phase)} · ${esc(item.lane)} · punteggio ${item.score.toFixed(2)}. ${Object.entries(item.components).map(([k,v])=>`${esc(k)} ${v.toFixed(2)}`).join(' · ')}</p><p>Alternative valutate: ${item.alternatives.filter(a=>a.id!==item.id).map(a=>`${ref(a.id)} (${a.score.toFixed(2)})`).join(', ')||'nessuna'}</p></div>`).join('');}
 $('review-seat').innerHTML=defaults.map((_,i)=>`<option value="${i}">Bot ${i+1} · posto ${i+2}</option>`).join('');$('review-seat').addEventListener('change',renderReview);
 $('start').addEventListener('click',()=>{const configs=defaults.map((_,i)=>{const strategy=document.querySelector(`[data-strategy="${i}"]`).value;return {strategy,target:strategy==='force'?document.querySelector(`[data-target="${i}"]`).value:null};});session=E.createSession(data,$('seed').value||'fra-tavolo-1',configs);persist();render();$('progress').focus();});
 $('resume').addEventListener('click',()=>{try{session=E.replay(data,saved);status('Sessione ripresa dal salvataggio locale.');render();$('progress').focus();}catch{status('Impossibile riprendere la sessione.');}});
 $('reset').addEventListener('click',()=>{$('setup').hidden=false;$('table').hidden=true;$('resume').hidden=!saved;if(session){$('seed').value=session.seed;session.configs.forEach((c,i)=>{document.querySelector(`[data-strategy="${i}"]`).value=c.strategy;if(c.target)document.querySelector(`[data-target="${i}"]`).value=c.target;configDescription(i);});}$('start').textContent='Inizia un nuovo draft';$('start').focus();if(!storageAvailable)status('Salvataggio non disponibile: esporta prima di cambiare tavolo.');});
 $('export').addEventListener('click',()=>{const record=session.export();if(session.complete)record.review=session.bots.map(b=>({strategy:b.strategy,pool:b.pool,log:b.log}));const url=URL.createObjectURL(new Blob([JSON.stringify(record,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='draft-fra-sessione.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
 document.addEventListener('click',event=>{const pick=event.target.closest('[data-pick]');if(pick){session.step(+pick.dataset.pick);persist();render();$('progress').focus();}const preview=event.target.closest('[data-preview]');if(preview){const c=byId[preview.dataset.preview];$('card-image').src=c.image;$('card-image').alt=c.name;$('card-text').textContent=`${c.full} ${c.cost}\n${c.type}\n${c.oracle}`;$('card-hover').hidden=true;$('card-dialog').showModal();}});
 const hover=(event)=>{const target=event.target.closest('[data-preview]');if(!target)return;const c=byId[target.dataset.preview];$('card-hover').querySelector('img').src=c.image;$('card-hover').hidden=false;};
 document.addEventListener('pointerover',event=>{if(event.pointerType!=='touch')hover(event);});document.addEventListener('focusin',hover);
 document.addEventListener('pointerout',event=>{if(event.target.closest('[data-preview]'))$('card-hover').hidden=true;});document.addEventListener('focusout',()=>$('card-hover').hidden=true);
 document.addEventListener('keydown',event=>{if(event.key==='Escape')$('card-hover').hidden=true;});$('close-card').addEventListener('click',()=>$('card-dialog').close());
})();
