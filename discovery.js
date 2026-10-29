'use strict';
(()=>{
 const $=id=>document.getElementById(id),knownFormats=['Standard','Commander','cEDH','Duel Commander','Pioneer','Modern','Pauper','Legacy','Vintage'];
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const key=EXPANSION_CONFIG.storage.watch;
 const levelOrder=[...new Set([...(EXPANSION_CONFIG.ui.discoveryLevels||['Confermata','Emergente','Preliminare']),'Analizzata','Solo misure di torneo'])];
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
 if(DISCOVERY.defaultSort&&[...$('sort').options].some(o=>o.value===DISCOVERY.defaultSort))$('sort').value=DISCOVERY.defaultSort;
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
  const measured=Object.values(p.formats||{}).map(a=>a.tournamentIndex).filter(Boolean),positive=measured.filter(t=>t.score>0);
  const editorialLevel=isRepeated?'Confermata':observations.length?'Emergente':null;
  const level=selected?.level||p.tournamentLevel||editorialLevel||(p.analysisCoverage==='tournament_data_only'?'Solo misure di torneo':'Analizzata');
  return {name:card.name,editorialDate:selected?.editorialDate||(!p.tournamentLevel&&editorialLevel?p.date:null),product:card.set,image:card.image,formats:Object.entries(p.formats||{}).filter(([key,assessment])=>!['draft','sealed','pick_two'].includes(key)&&['legal','restricted'].includes(card.legalities?.[key]||assessment.legality)).map(([key])=>CardProspects.formatLabels[key]||key),level,role:'Analisi della carta',verdict:p.gameplayReview?.finding||p.editorialThesis,evidence:p.summary,line:p.gameplayReview?.finding,limit:p.price?.outlook?.thesis,sources:[],record:card};
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
 function filterURL(){const u=new URL(url.href);u.search='';if(view==='all')u.searchParams.set('view','all');if(format!=='Tutti')u.searchParams.set('format',format);for(const id of ['level','product'])if($(id).value)u.searchParams.set(id,$(id).value);if($('sort').value!==(DISCOVERY.defaultSort||'signal'))u.searchParams.set('sort',$('sort').value);if($('search').value.trim())u.searchParams.set('q',$('search').value.trim());return u}
 function measuredIndices(c){return c.tournamentIndices||Object.fromEntries(Object.entries(c.record?.prospects?.formats||{}).filter(([,a])=>a.tournamentIndex).map(([f,a])=>[f,a.tournamentIndex]))}
 function tournamentScore(c){const rows=measuredIndices(c),key=Object.keys(TournamentProspects.formats).find(k=>TournamentProspects.formats[k]===format);return key?rows[key]?.score:Math.max(...Object.values(rows).map(t=>t.score).filter(Number.isFinite),-1)}
 function tournamentHTML(c){const rows=measuredIndices(c),keys=Object.keys(rows).filter(f=>format==='Tutti'||TournamentProspects.formats[f]===format);return keys.length?'<dl class="catalog-prospect-indices discovery-tournament-indices">'+keys.map(f=>{const card=c.record||{prospects:{formats:{[f]:{tournamentIndex:rows[f]}}}};return `<div><dt>${esc(TournamentProspects.formats[f]||f)}</dt><dd>${TournamentProspects.compact(card,f)}</dd></div>`}).join('')+'</dl>':''}
 function render(){
  $('formats').innerHTML=actualFormats().map(f=>`<button type="button" data-format="${esc(f)}" aria-pressed="${f===format}">${esc(f)}</button>`).join('');
  const search=$('search').value.trim().toLocaleLowerCase('it'),all=availableCards();
  const cards=all.filter(c=>(format==='Tutti'||c.formats.some(f=>f===format||format==='Commander'&&f.startsWith('Commander')))&&(!$('level').value||c.level===$('level').value)&&(!$('product').value||c.product===$('product').value)&&(!$('saved').checked||watched.has(c.name))&&(!search||[c.name,c.role,c.verdict,c.line,c.evidence,c.limit].join(' ').toLocaleLowerCase('it').includes(search)));
  cards.sort((a,b)=>$('sort').value==='tournament'?(tournamentScore(b)??-1)-(tournamentScore(a)??-1)||a.name.localeCompare(b.name):$('sort').value==='name'?a.name.localeCompare(b.name):(levels[a.level]??99)-(levels[b.level]??99)||all.indexOf(a)-all.indexOf(b));
  const visible=view==='all'?cards.slice(0,limit):cards;
  $('count').textContent=`${cards.length} di ${all.length} carte${view==='all'?` · ${visible.length} mostrate`:''} · ${watched.size} osservate`;
  $('research-more').hidden=view!=='all'||visible.length>=cards.length;
  const commonNotes=(DISCOVERY.sharedEvidenceNotes||[]).filter(note=>visible.some(c=>c.evidence?.includes(note)));
  const notes=$('discovery-shared-notes');notes.hidden=!commonNotes.length;notes.textContent=commonNotes.join(' ');
  const evidence=c=>commonNotes.reduce((text,note)=>text.replace(note,''),c.evidence||'').trim();
  $('results').innerHTML=visible.length?visible.map(c=>`<article class="candidate"><div class="candidate-top">${c.image?`<img src="${esc(c.image)}" alt="${esc(c.name)}" loading="lazy" width="96" height="134">`:''}<div><span class="badge ${({Confermata:'confirmed',Emergente:'emerging',Preliminare:'early'})[c.level]||'early'}">${esc(c.level)}</span>${c.editorialDate?`<small>Valutazione editoriale del ${esc(c.editorialDate)}</small>`:''}<h3>${esc(c.name)}</h3><div class="meta">${esc(view==='all'?'Prodotto '+c.product:c.formats.join(' · ')+' · '+c.product+' · '+c.role)}</div></div></div><p class="verdict">${esc(c.verdict)}</p>${tournamentHTML(c)}<p class="evidence">${esc(evidence(c))}</p>${view==='selected'?`<details><summary>${c.generatedBy?'Dati e limiti dell’osservazione':'Perché funziona e cosa può limitarla'}</summary><p>${c.generatedBy?'Presenze nel campione':'Linea di gioco'}: ${esc(c.line)}</p><p>Il limite: ${esc(c.limit)}</p></details>`:''}<details data-prospect="${esc(c.name)}"><summary>Analisi per formato, prezzi e fonti</summary><div class="prospect-content"></div></details><div class="sources">${c.sources.map(([label,link])=>`<a href="${esc(link)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`).join('')}</div><button class="save" type="button" data-save="${esc(c.name)}" aria-pressed="${watched.has(c.name)}">${watched.has(c.name)?'Osservata':'Segui carta'}</button></article>`).join(''):'<div class="empty"><h3>Nessuna carta con questi filtri</h3><p>Prova un altro formato, allarga il segnale o azzera i filtri.</p><button type="button" data-reset>Azzera filtri</button></div>';
 }
 async function changeView(){
  const requested=$('research-view').value;
  if(requested==='all'){
   $('research-status').textContent='Caricamento delle analisi complete…';
   try{await loadResearch()}catch(error){$('research-status').textContent=error.message;$('research-view').value='selected';view='selected';refreshOptions();render();return}
  }
  view=$('research-view').value;limit=24;refreshOptions();render();
  $('research-status').textContent=view==='all'?`${allCards.length} analisi consultabili. Il filtro formato indica legalità, non adozione competitiva. Solo misure di torneo indica che manca una recensione strategica. Analizzata indica una scheda editoriale disponibile: adozione e assenze vanno lette nei riscontri datati e nei rispettivi campioni.${researchWarning}`:'';
 }
 function reset(){format='Tutti';$('search').value='';$('level').value='';$('product').value='';$('sort').value=DISCOVERY.defaultSort||'signal';$('saved').checked=false;limit=24;render()}
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
 if(DISCOVERY.tournamentResearch){
  const research=DISCOVERY.tournamentResearch,events=research.events||[],recent=events.filter(e=>e.date>=research.start&&e.date<=research.end);
  const eyebrow=document.querySelector('.hero .eyebrow');if(eyebrow)eyebrow.textContent='Osservatorio Constructed · indici torneo al '+research.end;
  const notice=document.querySelector('main > .notice');if(notice){const previous=notice.innerHTML,hasEditorial=DISCOVERY.cards.some(c=>c.editorialDate);notice.innerHTML=`<strong>Indici torneo aggiornati al ${esc(research.end)}.</strong><p>Le misure recenti, lo storico dei Pro Tour e le valutazioni editoriali conservano finestre distinte. Presenze e piazzamenti non sono una WR della carta o una previsione futura.</p>${hasEditorial?'<details><summary>Contesto editoriale precedente e relativi limiti</summary>'+previous+'</details>':''}`;}
  const box=document.createElement('details');box.className='tournament-method';box.id='tournament-method';
  box.innerHTML=`<summary>Indice torneo: metodo, copertura e fonti</summary><p>Finestra dell’indice: ${esc(research.start)} a ${esc(research.end)}. Indice 0–100 = 100 × liste con la carta / liste pubblicate ammissibili. Main e sideboard contano una sola presenza per lista. I Pro Tour storici sono separati dall’indice recente. Nessuna WR Constructed della carta è dedotta da questi risultati.</p><p>Campione recente: ${recent.length} eventi e ${recent.reduce((sum,e)=>sum+e.publishedDecks,0)} liste. Le pubblicazioni possono essere parziali. Pagine non acquisite: ${research.missingSourcePages||0}. Non osservata significa soltanto assente dalle liste acquisite, successive all’uscita o alla prima traccia documentata della carta.</p><p>Segnali da seguire: uso ripetuto con almeno cinque liste in tre eventi; prime presenze negli altri casi osservati. Crescita e calo confrontano il periodo precedente ${TournamentProspects.periodLabel(research.trendPeriods?.previous,'(date non registrate)')} e quello recente ${TournamentProspects.periodLabel(research.trendPeriods?.recent,'(date non registrate)')}, usando per carta una sola coorte presente in entrambi i periodi con lo stesso tipo di evento e la stessa classificazione di copertura: almeno 50 liste per periodo e uno scarto di un punto percentuale; crescita richiede almeno tre presenze recenti. Sono convenzioni di lettura del campione, non previsioni. Con Tutti, l’ordinamento usa il maggiore indice fra i formati della carta; seleziona un formato per un confronto omogeneo.</p><div class="prospect-table" role="region" tabindex="0" aria-label="Eventi del campione"><table><thead><tr><th>Evento e fonti</th><th>Formato</th><th>Data</th><th>Liste pubblicate / partecipanti dichiarati</th><th>Copertura</th></tr></thead><tbody>${events.map(e=>`<tr><td>${esc(e.name)} ${(e.pages||[]).map((url,i)=>`<a href="${esc(url)}" target="_blank" rel="noopener">Fonte ${i+1}</a>`).join(' · ')}</td><td>${esc(TournamentProspects.formats[e.format]||e.format)}</td><td>${esc(e.date)}</td><td>${e.publishedDecks} / ${e.players??'N/D'}</td><td>${esc(e.publishedCoverage)}</td></tr>`).join('')}</tbody></table></div>`;
  document.querySelector('.discovery-controls').before(box);
 }
 if(q.get('view')==='all'){
  $('research-view').value='all';
  changeView().then(()=>{for(const id of ['level','product']){const value=q.get(id);if([...$(id).options].some(o=>o.value===value))$(id).value=value}render()});
 }else{refreshOptions();render()}
})();
