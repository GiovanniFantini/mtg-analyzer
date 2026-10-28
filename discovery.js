'use strict';
(()=>{
 const $=id=>document.getElementById(id),knownFormats=['Standard','Commander','cEDH','Duel Commander','Pioneer','Modern','Pauper','Legacy','Vintage'];
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const key=EXPANSION_CONFIG.storage.watch;
 const levelOrder=[...new Set([...(EXPANSION_CONFIG.ui.discoveryLevels||['Confermata','Emergente','Preliminare']),'Analizzata'])];
 const levels=Object.fromEntries(levelOrder.map((label,i)=>[label,i]));
 let watched=new Set(),format='Tutti',storage=true,view='selected',limit=24,allCards=null,sources=[],loading=null,researchWarning='';
 const byName=new Map();
 let rawWatch=null;
 try{rawWatch=localStorage.getItem(key);const saved=rawWatch===null?[]:JSON.parse(rawWatch);if(!Array.isArray(saved)||saved.some(x=>typeof x!=='string'))throw Error('Osservate non leggibili');const aliases=DISCOVERY.watchNames||{};watched=new Set(saved.map(value=>Object.hasOwn(aliases,value)?aliases[value]:value));}catch{storage=false;if(rawWatch!==null){const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([rawWatch],{type:'application/json'}));link.download=EXPANSION_CONFIG.id+'-osservate-originali.json';link.textContent='Scarica il salvataggio originale delle osservate';$('storage-status').after(link);}}
 function storageNote(){$('storage-status').textContent=storage?'':'Salvataggio nel browser non disponibile: le osservate restano attive solo finché questa pagina è aperta.'}
 storageNote();
 const url=window.__portableURL||new URL(location.href),q=new URLSearchParams(url.search);
 if(window.parent!==window){try{const outer=new URL(window.parent.location.href);for(const id of ['format','level','product','sort','q','view'])if(outer.searchParams.has('discovery_'+id))q.set(id,outer.searchParams.get('discovery_'+id))}catch{}}
 format=q.get('format')||'Tutti';$('search').value=q.get('q')||'';
 for(const id of ['level','product','sort']){const value=q.get(id);if([...$(id).options].some(o=>o.value===value))$(id).value=value}
 function availableCards(){return view==='all'&&allCards?allCards:DISCOVERY.cards}
 function actualFormats(){const actual=[...new Set(availableCards().flatMap(c=>c.formats.map(f=>f.startsWith('Commander')?'Commander':f)))];return ['Tutti',...knownFormats.filter(f=>actual.includes(f)),...actual.filter(f=>!knownFormats.includes(f))]}
 function refreshOptions(){
  const selectedLevel=$('level').value,selectedProduct=$('product').value;
  $('level').innerHTML='<option value="">Tutti i segnali</option>'+levelOrder.filter(level=>availableCards().some(c=>c.level===level)).map(level=>`<option value="${esc(level)}">${esc(level)}</option>`).join('');
  $('product').innerHTML='<option value="">Tutti i prodotti</option>'+[...new Set(availableCards().map(c=>c.product))].sort().map(product=>`<option value="${esc(product)}">${esc(product)}</option>`).join('');
  if([...$('level').options].some(o=>o.value===selectedLevel))$('level').value=selectedLevel;
  if([...$('product').options].some(o=>o.value===selectedProduct))$('product').value=selectedProduct;
  if(!actualFormats().includes(format))format='Tutti';
 }
 async function localJSON(path){const target=new URL(path,location.href);if(target.origin!==location.origin)throw Error('Percorso dei dati non valido');const response=await fetch(target);if(!response.ok)throw Error('Dati non disponibili');return response.json()}
 function candidate(card){
  const p=card.prospects,selected=DISCOVERY.cards.find(c=>c.name===card.name),observations=p.tournamentObservations||[];
  const isRepeated=observations.some(row=>row.decklistsWithCard>=10)||p.cedhObservation?.lists>=10;
  const level=selected?.level||(isRepeated?'Confermata':observations.length?'Emergente':'Analizzata');
  return {name:card.name,product:card.set,image:card.image,formats:Object.entries(p.formats||{}).filter(([key,assessment])=>!['draft','sealed','pick_two'].includes(key)&&['legal','restricted'].includes(assessment.legality)).map(([key])=>CardProspects.formatLabels[key]||key),level,role:'Analisi della carta',verdict:p.gameplayReview?.finding||p.editorialThesis,evidence:p.summary,line:p.gameplayReview?.finding,limit:p.price?.outlook?.thesis,sources:[],record:card};
 }
 async function loadResearch(){
  if(allCards)return;
  if(loading)return loading;
  loading=(async()=>{
   const responses=await Promise.allSettled([localJSON('data/cards.json'),localJSON('data/sources.json')]);
   if(responses[0].status!=='fulfilled')throw Error('Impossibile caricare le analisi. Le carte selezionate restano consultabili.');
   const catalog=responses[0].value,records=(catalog.cards||[]).filter(c=>c.prospects);
   if(!records.length)throw Error('Le analisi complete non sono ancora disponibili per questa espansione.');
   sources=responses[1].status==='fulfilled'?responses[1].value.research?.sources||[]:[];
   if(responses[1].status!=='fulfilled')researchWarning='Il registro delle fonti non è disponibile; il testo Oracle resta collegato nelle schede.';
   if(DISCOVERY.research?.commanderAppendix){
    try{const appendix=await localJSON(DISCOVERY.research.commanderAppendix);records.push(...(appendix.cards||[]).filter(c=>c.prospects))}
    catch{researchWarning+=' L’appendice Commander non è disponibile; le analisi del catalogo restano consultabili.'}
   }
   for(const card of records)byName.set(card.name,card);
   allCards=records.map(candidate);
   const newPreviews=records.filter(card=>card.image&&!DATA.cards.some(p=>p.name===card.name));
   DATA.cards.push(...newPreviews);
   window.dispatchEvent(new CustomEvent('mtg-card-data',{detail:{cards:newPreviews}}));
  })();
  try{await loading}finally{loading=null}
 }
 function filterURL(){const u=new URL(url.href);u.search='';if(view==='all')u.searchParams.set('view','all');if(format!=='Tutti')u.searchParams.set('format',format);for(const id of ['level','product'])if($(id).value)u.searchParams.set(id,$(id).value);if($('sort').value!=='signal')u.searchParams.set('sort',$('sort').value);if($('search').value.trim())u.searchParams.set('q',$('search').value.trim());return u}
 function render(){
  $('formats').innerHTML=actualFormats().map(f=>`<button type="button" data-format="${esc(f)}" aria-pressed="${f===format}">${esc(f)}</button>`).join('');
  const search=$('search').value.trim().toLocaleLowerCase('it'),all=availableCards();
  const cards=all.filter(c=>(format==='Tutti'||c.formats.some(f=>f===format||format==='Commander'&&f.startsWith('Commander')))&&(!$('level').value||c.level===$('level').value)&&(!$('product').value||c.product===$('product').value)&&(!$('saved').checked||watched.has(c.name))&&(!search||[c.name,c.role,c.verdict,c.line,c.evidence,c.limit].join(' ').toLocaleLowerCase('it').includes(search)));
  cards.sort((a,b)=>$('sort').value==='name'?a.name.localeCompare(b.name):(levels[a.level]??99)-(levels[b.level]??99)||all.indexOf(a)-all.indexOf(b));
  const visible=view==='all'?cards.slice(0,limit):cards;
  $('count').textContent=`${cards.length} di ${all.length} carte${view==='all'?` · ${visible.length} mostrate`:''} · ${watched.size} osservate`;
  $('research-more').hidden=view!=='all'||visible.length>=cards.length;
  const commonNotes=(DISCOVERY.sharedEvidenceNotes||[]).filter(note=>visible.some(c=>c.evidence?.includes(note)));
  const notes=$('discovery-shared-notes');notes.hidden=!commonNotes.length;notes.textContent=commonNotes.join(' ');
  const evidence=c=>commonNotes.reduce((text,note)=>text.replace(note,''),c.evidence||'').trim();
  $('results').innerHTML=visible.length?visible.map(c=>`<article class="candidate"><div class="candidate-top">${c.image?`<img src="${esc(c.image)}" alt="${esc(c.name)}" loading="lazy" width="96" height="134">`:''}<div><span class="badge ${({Confermata:'confirmed',Emergente:'emerging',Preliminare:'early'})[c.level]||'early'}">${esc(c.level)}</span><h3>${esc(c.name)}</h3><div class="meta">${esc(view==='all'?'Prodotto '+c.product:c.formats.join(' · ')+' · '+c.product+' · '+c.role)}</div></div></div><p class="verdict">${esc(c.verdict)}</p><p class="evidence">${esc(evidence(c))}</p>${view==='selected'?`<details><summary>Perché funziona e cosa può limitarla</summary><p>Linea di gioco: ${esc(c.line)}</p><p>Il limite: ${esc(c.limit)}</p></details>`:''}<details data-prospect="${esc(c.name)}"><summary>Analisi per formato, prezzi e fonti</summary><div class="prospect-content"></div></details><div class="sources">${c.sources.map(([label,link])=>`<a href="${esc(link)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`).join('')}</div><button class="save" type="button" data-save="${esc(c.name)}" aria-pressed="${watched.has(c.name)}">${watched.has(c.name)?'Osservata':'Segui carta'}</button></article>`).join(''):'<div class="empty"><h3>Nessuna carta con questi filtri</h3><p>Prova un altro formato, allarga il segnale o azzera i filtri.</p><button type="button" data-reset>Azzera filtri</button></div>';
 }
 async function changeView(){
  const requested=$('research-view').value;
  if(requested==='all'){
   $('research-status').textContent='Caricamento delle analisi complete…';
   try{await loadResearch()}catch(error){$('research-status').textContent=error.message;$('research-view').value='selected';view='selected';refreshOptions();render();return}
  }
  view=$('research-view').value;limit=24;refreshOptions();render();
  $('research-status').textContent=view==='all'?`${allCards.length} analisi consultabili. Il filtro formato indica legalità, non adozione competitiva. Analizzata significa che il giudizio è disponibile, con prove ancora insufficienti.${researchWarning}`:'';
 }
 function reset(){format='Tutti';$('search').value='';$('level').value='';$('product').value='';$('sort').value='signal';$('saved').checked=false;limit=24;render()}
 $('formats').addEventListener('click',e=>{const b=e.target.closest('[data-format]');if(!b)return;format=b.dataset.format;limit=24;render();[...$('formats').querySelectorAll('[data-format]')].find(b=>b.dataset.format===format)?.focus()});
 for(const id of ['level','product','sort','saved'])$(id).addEventListener('change',()=>{limit=24;render()});
 $('search').addEventListener('input',()=>{limit=24;render()});$('reset').onclick=reset;
 $('research-view').addEventListener('change',changeView);
 $('research-more').onclick=()=>{limit+=24;render()};
 $('results').addEventListener('toggle',async e=>{
  const details=e.target;if(!details.matches('details[data-prospect]')||!details.open||details.dataset.loaded)return;
  const content=details.querySelector('.prospect-content');content.textContent='Caricamento dell’analisi…';
  try{await loadResearch();const card=byName.get(details.dataset.prospect);content.innerHTML=card?CardProspects.render(card,sources):'<p>L’analisi completa non è disponibile per questa carta.</p>';details.dataset.loaded='true'}
  catch(error){content.textContent=error.message}
 },true);
 $('results').addEventListener('click',e=>{if(e.target.closest('[data-reset]'))return reset();const b=e.target.closest('[data-save]');if(!b)return;const n=b.dataset.save;watched.has(n)?watched.delete(n):watched.add(n);try{if(storage)localStorage.setItem(key,JSON.stringify([...watched]))}catch{storage=false;storageNote()}render();const replacement=[...document.querySelectorAll('[data-save]')].find(x=>x.dataset.save===n);(replacement||$('saved')).focus()});
 $('copy').onclick=async()=>{let u=filterURL();if(window.parent!==window){try{const outer=new URL(window.parent.location.href);outer.hash='discovery';for(const id of ['format','level','product','sort','q','view'])outer.searchParams.delete('discovery_'+id);for(const [k,v]of u.searchParams)outer.searchParams.set('discovery_'+k,v);u=outer}catch{}}try{await navigator.clipboard.writeText(u.href);$('share-status').textContent='Link copiato. Le osservate restano personali.'}catch{$('share-status').textContent='Copia questo link:';const input=document.createElement('input');input.value=u.href;input.setAttribute('aria-label','Link ai filtri');$('share-status').append(input);input.focus();input.select()}};
 if(q.get('view')==='all'){
  $('research-view').value='all';
  changeView().then(()=>{for(const id of ['level','product']){const value=q.get(id);if([...$(id).options].some(o=>o.value===value))$(id).value=value}render()});
 }else{refreshOptions();render()}
})();
