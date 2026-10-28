'use strict';
(()=>{
 const $=id=>document.getElementById('da-'+id),host=$('title')?.closest('section');if(!host||!window.DraftPool)return;
 const A=window.DraftAdvisor,data={...DRAFT_DATA.assistant,guides:DRAFT_DATA.drill.guides},allCards=data.cards,cards=allCards.filter(c=>!c.basic);
 const byName=new Map(allCards.map(c=>[c.name,c])),E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const norm=s=>s.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[’']/g,'').toLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim();
 const labels={W:'Bianco',U:'Blu',B:'Nero',R:'Rosso',G:'Verde',C:'Incolore',M:'Multi'};
 const rarityLabels={common:'Comune',uncommon:'Non comune',rare:'Rara',mythic:'Mitica',special:'Speciale',bonus:'Bonus'};
 let tab='pick',color='',selected=[],limit=12,lastPick=null,browsing=false,noticeState='';
 const name=c=>`<button type="button" class="da-name" data-name="${E(c.name)}" aria-label="Apri anteprima di ${E(c.name)}">${E(c.name)}</button>`;
 const currentPlan=()=>{const plan=window.DraftPool.getPlan();return [...$('plan').options].some(o=>o.value===plan)?plan:'';};
 const getContext=()=>A.context(allCards,window.DraftPool.get(),currentPlan());
 const analysisPanel=document.createElement('details');analysisPanel.id='da-analysis';
 $('plan-panel').after(analysisPanel);
 const analysisName=c=>`<span class="card-reference" role="button" tabindex="0" data-card-preview="${E(c.name.replace(/’/g,"'"))}" aria-label="Mostra ${E(c.name)}">${E(c.name)}</span>`;
 const evidence=entries=>entries.map(e=>`${e.quantity} × ${analysisName(e.card)}`).join(', ');
 function renderAnalysis(ctx,pool,blocked){
  analysisPanel.hidden=blocked||ctx.picked.filter(c=>!A.land(c)).reduce((n,c)=>n+(pool[c.name]||0),0)<6;if(analysisPanel.hidden)return;
  const a=A.poolAnalysis(ctx,pool),r=a.resources;
  const connections=a.observations.map(o=>`<li><h4>${E(o.title)}</h4><p>${evidence(o.sources)}${o.targets.length?' → '+evidence(o.targets):''}</p><p>${E(o.text)}</p></li>`).join('');
  const outside=a.outside.map(e=>`<li>${evidence([e])}: ${E(e.symbols||'costo da verificare')}, valore di mana ${A.mana(e.card)??'non disponibile'}.${e.repeated?' Richiede più simboli dello stesso colore fuori piano.':''}</li>`).join('');
  analysisPanel.innerHTML=`<summary>Come funziona il pool</summary><p>Analisi delle pick registrate, non di una lista finale da 40 carte. I collegamenti considerano i colori del piano; il fixing è elencato anche fuori piano, senza presumere di poterlo usare.</p>${connections?`<ul>${connections}</ul>`:'<p>Nessun collegamento riconosciuto con questi criteri: non significa assenza di sinergie. Controlla le anteprime e le combo del pool.</p>'}<h4>Risorse oltre alle carte creatura</h4><p>${r.prepared} carte che entrano preparate · ${r.tokens} carte con creazione di pedine creatura · ${r.flashback} carte con flashback. I gruppi possono sovrapporsi: non sono corpi già disponibili né giocate garantite nei primi turni.</p><h4>Colori e fixing</h4><p>${a.fixing.length?evidence(a.fixing):'Nessun cicloterra base o produttore di mana di qualsiasi colore riconosciuto.'}</p><p>Il cicloterra costa mana e scarta la carta; gli altri produttori devono essere lanciati e attivati. Le terre e le altre forme di fixing vanno controllate nelle anteprime. Questo elenco non certifica uno splash sostenibile.</p>${outside?`<p>Carte fuori dal piano attuale:</p><ul>${outside}</ul>`:''}${a.missing?`<p>Testo Oracle mancante per ${a.missing} carte: analisi parziale.</p>`:''}<p>Osservazioni euristiche dai testi disponibili, senza modificare voti o win rate. I risultati di Quick, Premier e Traditional vanno confrontati separatamente.</p>`;
 }
 function setFocus(active){document.body.classList.toggle('da-focused',active);$('focus').removeAttribute('aria-pressed');$('focus').dataset.selected=String(active);$('focus').textContent=active?'Mostra navigazione':'Solo assistente';}
 function poolError(message,keyboard=false){$('status').replaceChildren(document.createTextNode(message+' '));const link=document.createElement('a');link.href='#draft-pool';link.textContent='Apri lo stato del pool e il backup';$('status').append(link);$('status').scrollIntoView({block:'nearest'});if(keyboard)$('status').focus({preventScroll:true});}
 const analyze=(c,ctx)=>A.evaluate(c,ctx,window.DraftPool.get(),data);
 for(const [key,g]of Object.entries(data.guides||{}))$('plan').insertAdjacentHTML('beforeend',`<option value="${E(key)}">${E([...key].map(x=>labels[x]||x).join(' / ')+(g.theme?' · '+g.theme:''))}</option>`);
 for(const [key,label]of Object.entries(labels)){
  if(key!=='C'&&key!=='M')$('plan').insertAdjacentHTML('beforeend',`<option value="${key}">Solo ${label.toLowerCase()}</option>`);
  $('colors').insertAdjacentHTML('beforeend',`<button type="button" data-da-color="${key}" aria-pressed="false">${label}</button>`);
 }
 function cardRow(c,ctx,mode){
  const r=analyze(c,ctx),pool=window.DraftPool.get(),selectedCard=selected.includes(c.name);
  const advice=mode==='targets'?`<p>${E(r.reasons[0])}</p>${r.warnings.length?`<p class="small">${E(r.warnings[0])}</p>`:''}`:'';
  return `<article class="da-card"><div class="da-card-top"><img src="${E(c.image)}" alt="" width="52" height="73" loading="lazy"><div>${name(c)}<small>${E(c.cost||'Senza costo')} · ${E(rarityLabels[c.rarity]||c.rarity)} · nel pool: ${pool[c.name]||0}</small></div></div>${advice}<div class="da-actions">${tab==='compare'?`<button type="button" data-da-compare="${E(c.name)}" aria-label="${selectedCard?'Rimuovi dal confronto: ':'Confronta '}${E(c.name)}" data-selected="${selectedCard}">${selectedCard?'Rimuovi dal confronto':'Confronta'}</button>`:`<button type="button" data-da-pick="${E(c.name)}" aria-label="Presa +1: ${E(c.name)}" ${window.DraftPool.isBlocked()||pool[c.name]>=100?'disabled':''}>Presa +1</button>`}</div></article>`;
 }
 function renderResults(ctx){
  const query=norm($('search').value),cost=$('mana').value,type=$('type').value;
  let found=cards.filter(c=>(!query||norm(c.name).includes(query)||c.faces?.some(f=>norm(f.name).includes(query)))&&(!color||(color==='C'?A.colors(c).length===0:color==='M'?A.colors(c).length>1:A.colors(c).includes(color)))&&(cost===''||(cost==='6'?A.mana(c)>=6:A.mana(c)===Number(cost)))&&(!type||(c.faces?.[0]?.type_line||c.type).includes(type)));
  const relevance=c=>!query?0:norm(c.name).startsWith(query)?0:norm(c.name).split(/[\s/-]+/).some(w=>w.startsWith(query))?1:2;
  found.sort((a,b)=>relevance(a)-relevance(b)||a.name.localeCompare(b.name));
  const filters=[color?labels[color]:'',cost!==''?'Costo '+(cost==='6'?'6+':cost):'',type?$('type').selectedOptions[0].textContent:''].filter(Boolean);
  $('filter-summary').textContent=filters.length?'Filtri attivi: '+filters.join(' · '):'Filtri rapidi: colore, costo, tipo';
  if(!query&&!filters.length&&!browsing){
   $('count').textContent=`${cards.length} carte nel catalogo.`;
   $('results').innerHTML='<div class="da-empty"><h3>Quale carta stai valutando?</h3><p>Cerca un nome per registrare una pick o confrontare due alternative. Hai già un piano? Apri “Comuni da cercare”.</p><button type="button" data-da-browse>Sfoglia il catalogo</button></div>';
   $('more').hidden=true;return;
  }
  $('count').textContent=`${found.length} carte.`;
  $('results').innerHTML=found.slice(0,limit).map(c=>cardRow(c,ctx,'search')).join('')||`<p>${query?(filters.length?'Nessuna carta: controlla il nome inglese o i filtri.':'Nessuna carta: usa il nome inglese o prova meno lettere.'):'Nessuna carta con questi filtri.'}</p>`;
  $('more').hidden=found.length<=limit;
 }
 function renderComparison(ctx){
  const target=$('comparison');target.hidden=tab!=='compare';if(tab!=='compare')return;
  const rows=selected.map(n=>analyze(byName.get(n),ctx));
  let verdict='Seleziona due carte dai risultati. Puoi cambiare filtri tra la prima e la seconda.';
  if(rows.length===1)verdict='Prima alternativa selezionata. Cerca la seconda carta.';
  if(rows.length===2){
   rows.sort((a,b)=>b.value-a.value);const [best,other]=rows,gap=A.comparisonGap(best,other);
   verdict=rows.some(r=>A.land(r.card))?'Confronto parziale: controlla il mana prodotto dalle terre nell’anteprima.':rows.some(r=>r.base==null)?'Confronto incerto: manca un voto Limited. Controlla i dettagli.':gap<.2?'Scelta vicina: nessuna preferenza netta con i dati disponibili.':`Preferisco ${best.card.name}. ${A.explain(best,other)}`;
   if(gap>=.2&&rows.every(r=>r.base!=null&&!A.land(r.card))&&best.warnings.length)verdict+=' '+best.warnings[0];
   if(rows.every(r=>!A.compatible(r.card,ctx)))verdict+=' Entrambe fuori piano: cerca prima una giocabile nei tuoi colori.';
  }
  if(window.DraftPool.isBlocked())verdict='Confronto del pool non disponibile: apri backup e recupero del salvataggio precedente.';
  target.innerHTML=`<div class="da-verdict"><h3>Nel tuo pool</h3><p>${E(verdict)}</p></div><div class="da-results">${rows.map(r=>`<article class="da-card">${name(r.card)}<p>${r.reasons.map(E).join(' ')}</p>${r.warnings.length?`<p>${r.warnings.map(E).join(' ')}</p>`:''}<details><summary>Perché e a quali condizioni</summary><p>${E(r.why||'Analisi qualitativa non disponibile.')}</p><p>${E(r.condition)}</p><p>Voto Limited di partenza: ${r.base??'N/D'}. ${E(r.card.community!=null?'Recensione esterna.':'Valutazione editoriale.')}</p></details><div class="da-actions"><button type="button" data-da-pick="${E(r.card.name)}" aria-label="Prendi questa +1: ${E(r.card.name)}" ${window.DraftPool.isBlocked()||window.DraftPool.get()[r.card.name]>=100?'disabled':''}>Prendi questa +1</button><button type="button" data-da-unselect="${E(r.card.name)}" aria-label="Rimuovi ${E(r.card.name)} dal confronto">Rimuovi</button></div></article>`).join('')}</div>`;
 }
 function render(){
  const active=document.activeElement,focusId=host.contains(active)?active.id:'',focusAttr=host.contains(active)?['data-da-compare','data-da-remove','data-da-pick','data-da-unselect','data-name','data-card-preview'].find(a=>active.hasAttribute(a)):null;
  const focusValue=focusAttr?active.getAttribute(focusAttr):null,focusScope=active?.closest('#da-results,#da-targets,#da-comparison,#da-selected,#da-pool,#da-analysis')?.id;
  $('plan').value=currentPlan();
  const ctx=getContext(),pool=window.DraftPool.get();
  const blocked=window.DraftPool.isBlocked(),temporary=window.DraftPool.isTemporary();
  const nextNoticeState=blocked?'blocked':temporary?'temporary':'';
  if(nextNoticeState&&nextNoticeState!==noticeState)$('plan-panel').open=true;
  noticeState=nextNoticeState;
  $('context').textContent=blocked?'Salvataggio precedente protetto: le carte salvate non sono state cancellate.':`${ctx.total} carte registrate · ${ctx.plan?[...ctx.plan].map(x=>labels[x]).join(' / '):'Colori ancora aperti'}${!$('plan').value&&ctx.plan?' (ipotesi dal pool)':''}${ctx.flexibleSecond?' · secondo colore aperto':''}`;
  if(temporary)$('context').textContent+=' · solo in questa pagina';
  renderAnalysis(ctx,pool,blocked);
  $('needs').textContent=ctx.spells<6?'Prime scelte: privilegia qualità e flessibilità. I colori del pool non sono segnali del tavolo.':`${ctx.early} creature a costo 0–2 · ${ctx.bodies} creature · ${ctx.high} magie a costo 5+. ${ctx.early/ctx.spells<.25?'Cerca creature per i primi turni.':ctx.bodies/ctx.spells<.5?'Controlla di avere abbastanza creature.':'Confronta qualità, interazione e sinergie.'}`;
  if(blocked){$('needs').replaceChildren(document.createTextNode('Per riprendere, conserva il salvataggio precedente. '));const link=document.createElement('a');link.href='#draft-pool';link.textContent='Apri backup e recupero del pool';$('needs').append(link);}
  else if(temporary){const note=document.createElement('p');note.append(document.createTextNode('Pick temporanee: prima di chiudere o ricaricare, '));const link=document.createElement('a');link.href='#draft-pool';link.textContent='scarica la lista del pool';note.append(link);$('needs').append(note);}
  $('finder').hidden=tab==='targets';$('targets').hidden=tab!=='targets';
  if(tab!=='targets')renderResults(ctx);
  else{
   const commons=cards.filter(c=>c.rarity==='common'&&!A.land(c)&&A.rating(c)!=null&&A.compatible(c,ctx));
   const ranked=commons.map(c=>analyze(c,ctx)).sort((a,b)=>b.value-a.value||a.card.name.localeCompare(b.card.name));
   $('targets').innerHTML=`<h3>${ctx.plan?'Comuni da cercare per il tuo piano':'Comuni prioritarie, colori aperti'}</h3><p>Priorità relative fra le comuni del catalogo, non carte presenti nella tua busta. ${ctx.flexibleSecond?'Il secondo colore è ancora aperto: valuta anche le alternative.':ctx.plan?'':'Scegli un piano per restringere i colori.'}</p><div class="da-results">${ranked.slice(0,8).map(r=>cardRow(r.card,ctx,'targets')).join('')||'<p>Nessuna comune con voto disponibile per questi colori.</p>'}</div>`;
  }
  renderComparison(ctx);
  $('selected').hidden=tab!=='compare'||!selected.length;
  $('selected').innerHTML=selected.map((n,i)=>`<div class="da-selection"><small>Alternativa ${i+1}</small><div>${name(byName.get(n))}</div><button type="button" data-da-unselect="${E(n)}" aria-label="Rimuovi ${E(n)} dal confronto">Rimuovi</button></div>`).join('');
  $('pool-summary').textContent=blocked?'Salvataggio precedente protetto':`Le tue pick (${ctx.total}) · correggi quantità`;
  $('pool').innerHTML=ctx.picked.map(c=>`<div class="da-pool-row"><span>${pool[c.name]} × ${name(c)}</span><button type="button" data-da-remove="${E(c.name)}" aria-label="Togli una copia di ${E(c.name)}">−1</button></div>`).join('')||'<p>Nessuna pick registrata.</p>';
  if(focusId)document.getElementById(focusId)?.focus({preventScroll:true});
  else if(focusAttr){const scope=document.getElementById(focusScope)||host;const next=[...scope.querySelectorAll('['+focusAttr+']')].find(b=>b.getAttribute(focusAttr)===focusValue);(next||(focusAttr==='data-da-remove'?$('pool-summary'):$('status'))).focus({preventScroll:true});}
 }
 function reset(){color='';limit=12;$('mana').value='';$('type').value='';for(const b of $('colors').querySelectorAll('button'))b.setAttribute('aria-pressed','false');}
 host.addEventListener('click',async e=>{
  if(e.target.closest('a[href="#draft-pool"]'))setFocus(false);
  const b=e.target.closest('button');if(!b)return;
  if(b.hasAttribute('data-da-browse')){browsing=true;renderResults(getContext());$('results').focus({preventScroll:true});}
  if(b.dataset.daTab){tab=b.dataset.daTab;for(const x of host.querySelectorAll('[data-da-tab]'))x.setAttribute('aria-pressed',String(x===b));render();}
  if(b.dataset.daColor){color=color===b.dataset.daColor?'':b.dataset.daColor;limit=12;for(const x of $('colors').querySelectorAll('button'))x.setAttribute('aria-pressed',String(x.dataset.daColor===color));renderResults(getContext());}
  if(b.dataset.daCompare){const n=b.dataset.daCompare;if(selected.includes(n))selected=selected.filter(x=>x!==n);else if(selected.length<2)selected.push(n);else{$('status').textContent='Hai già due alternative: rimuovine una per sostituirla.';$('status').scrollIntoView({block:'nearest'});return;}render();if(selected.length===2)$('comparison').scrollIntoView({block:'start'});}
  if(b.dataset.daUnselect){selected=selected.filter(x=>x!==b.dataset.daUnselect);render();if(e.detail===0)$('search').focus({preventScroll:true});else $('search').scrollIntoView({block:'nearest'});}
  if(b.dataset.daPick){
   b.disabled=true;const n=b.dataset.daPick;
   try{const snapshot=await window.DraftPool.change(n,1);
    if(snapshot){lastPick={name:n,snapshot};selected=[];render();$('status').replaceChildren(document.createTextNode(`Registrata: ${n} (${window.DraftPool.get()[n]} nel pool). `));const undo=document.createElement('button');undo.type='button';undo.id='da-undo';undo.textContent='Annulla ultima aggiunta';$('status').append(undo);if(e.detail===0){if(tab==='targets'){[...$('targets').querySelectorAll('[data-da-pick]')].find(x=>x.dataset.daPick===n)?.focus({preventScroll:true});}else{$('search').focus({preventScroll:true});$('search').select();}}$('status').scrollIntoView({block:'nearest'});}
    else poolError('Pick non registrata.',e.detail===0);
   }catch{poolError('Pick non registrata.',e.detail===0);}finally{b.disabled=false;}
  }
  if(b.dataset.daRemove){const ok=await window.DraftPool.change(b.dataset.daRemove,-1);lastPick=null;if(ok)$('status').textContent='Quantità aggiornata.';else poolError('Rimozione non salvata.',e.detail===0);}
  if(b.id==='da-undo'&&lastPick){const previous=lastPick;lastPick=null;const ok=await window.DraftPool.change(previous.name,-1,previous.snapshot);$('status').textContent=ok?'Ultima aggiunta annullata.':'Annullamento non eseguito: il pool è cambiato o il salvataggio non è disponibile.';if(e.detail===0)(tab==='targets'?$('status'):$('search')).focus({preventScroll:true});}
 });
 for(const id of ['search','mana','type'])$(id).addEventListener(id==='search'?'input':'change',()=>{limit=12;renderResults(getContext());});
 $('search').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.isComposing){e.preventDefault();$('results').focus({preventScroll:true});$('results').scrollIntoView({block:'nearest'});}});
 $('plan').addEventListener('change',async()=>{if(!await window.DraftPool.setPlan($('plan').value)){render();poolError('Piano non salvato.');}});$('reset').addEventListener('click',()=>{reset();render();});$('more').addEventListener('click',e=>{const previous=limit,focused=document.activeElement===$('more');limit+=12;renderResults(getContext());if($('more').hidden&&focused){const next=e.detail===0?$('results').querySelectorAll('[data-name]')[previous]:null;(next||$('results')).focus({preventScroll:true});}});
 $('next-search').addEventListener('click',()=>{$('search').value='';limit=12;browsing=false;renderResults(getContext());$('search').focus();});
 $('focus').addEventListener('click',()=>{setFocus(!document.body.classList.contains('da-focused'));host.scrollIntoView({block:'start'});});
 document.addEventListener('draft-pool-updated',e=>{if(lastPick&&e.detail?.snapshot!==lastPick.snapshot){const focused=document.activeElement===$('undo');lastPick=null;$('status').textContent='Pool aggiornato: annullamento precedente non disponibile.';if(focused)$('status').focus({preventScroll:true});}render();});
 $('method').textContent=`Voti Limited: ${data.ratingsDate||'data non disponibile'}. Catalogo: ${EXPANSION_CONFIG.name}, ${DRAFT_DATA.catalogDate||'data non disponibile'}. Nessun dato viene aggiornato durante la consultazione.`;
 render();
})();
