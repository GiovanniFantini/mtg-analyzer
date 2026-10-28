'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const byId = new Map(DATA.cards.map(c => [c.id, c]));
  const basics = ['Plains','Island','Swamp','Mountain','Forest'];
  const basicIds = basics.map(name => DATA.cards.find(c => c.name === name && c.type.startsWith('Basic Land'))?.id);
  const isBasic = id => basicIds.includes(id);
  const basicCard = id => !!byId.get(id)?.basic||/\bBasic\b.*\bLand\b/.test(byId.get(id)?.type||'');
  const pageKey = document.body.dataset.page;
  const catalog=pageKey==='gallery'?CatalogControls.create(DATA,EXPANSION_CONFIG.code):null;
  if(catalog)catalog.mount($('catalog-extra-controls'),$('trk-order'));
  const modes = Object.keys(EXPANSION_CONFIG.events);
  const defaultSealed=EXPANSION_CONFIG.defaultEvents?.sealed||modes.find(id=>EXPANSION_CONFIG.events[id].kind==='sealed');
  const defaultDraft=EXPANSION_CONFIG.defaultEvents?.draft||modes.find(id=>EXPANSION_CONFIG.events[id].kind==='draft');
  const eventRules=(selectedMode=mode)=>EXPANSION_CONFIG.events[selectedMode];
  const handSize=()=>eventRules().mulligan.handSize;
  const bottomCount=()=>Math.max(0,mulligans-eventRules().mulligan.freeMulligans);
  const requestedMode = new URLSearchParams(location.search).get('mode');
  let rememberedMode;
  try { rememberedMode=sessionStorage.getItem(EXPANSION_CONFIG.storage.mode); } catch {}
  const pageKind=pageKey==='pool'?'sealed':pageKey==='draft'?'draft':null;
  const allowedModes=modes.filter(id=>!pageKind||EXPANSION_CONFIG.events[id].kind===pageKind);
  const preferredMode=pageKind==='sealed'?defaultSealed:defaultDraft;
  let mode=allowedModes.includes(requestedMode)?requestedMode:pageKind?(preferredMode||null):allowedModes.includes(rememberedMode)?rememberedMode:defaultSealed||allowedModes[0]||null;
  let page = 0, state = empty(), storageError = '';
  const memoryStates=new Map();
  let hand = [], library = [], fullDeck = [], bottom = [], mulligans = 0, kept = false;
  function empty() { return {pool:{},deck:{},basics:{}}; }
  function key(selectedMode=mode) { return EXPANSION_CONFIG.storage.poolPrefix+selectedMode+'-v1'; }
  function status(message=storageError) {
    let target=$('trk-storage-status');
    if(!target){target=document.createElement('p');target.id='trk-storage-status';target.setAttribute('role','status');target.setAttribute('aria-live','polite');document.querySelector('main').prepend(target);}
    target.textContent=message;
  }
  const contextualHrefs=new WeakMap();
  function modeLinks() {
    if(!mode)return;
    try { sessionStorage.setItem(EXPANSION_CONFIG.storage.mode,mode); } catch {}
    const modePaths=new Set(['gallery','pool','simulator','draft','workbench','practice'].map(key=>EXPANSION_CONFIG.routes[key]).filter(Boolean).map(route=>new URL(route,location.href).pathname));
    for(const link of document.querySelectorAll('a[href]')){
      if(link.hasAttribute('data-pool-workbench')&&!contextualHrefs.has(link))contextualHrefs.set(link,link.href);
      const url=new URL(contextualHrefs.get(link)||link.href);
      if(link.hasAttribute('data-pool-workbench')&&url.pathname===new URL(EXPANSION_CONFIG.routes.pool,location.href).pathname&&eventRules().kind==='draft')url.pathname=new URL(EXPANSION_CONFIG.routes.workbench||EXPANSION_CONFIG.routes.draft,location.href).pathname;
      if(link.closest('main')&&EXPANSION_CONFIG.routes.practice&&url.pathname===new URL(EXPANSION_CONFIG.routes.simulator,location.href).pathname)url.pathname=new URL(EXPANSION_CONFIG.routes.practice,location.href).pathname;
      if(url.origin===location.origin&&url.pathname.startsWith(location.pathname.slice(0,location.pathname.lastIndexOf('/')+1))&&modePaths.has(url.pathname)){
        url.searchParams.set('mode',mode);link.setAttribute('href',url.pathname+url.search+url.hash);
      }
    }
  }
  function validCounts(obj) {
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) throw Error('Conteggi mancanti.');
    for (const [id, n] of Object.entries(obj)) if (!byId.has(id) || !Number.isInteger(n) || n<0 || n>999) throw Error('Carta o quantità non valida nel salvataggio.');
    return Object.fromEntries(Object.entries(obj).filter(([,n])=>n>0));
  }
  function validate(value,selectedMode=mode) {
    const rules=eventRules(selectedMode);
    if(!rules)throw Error('Regole del formato non disponibili.');
    if (!value || typeof value !== 'object') throw Error('Salvataggio non valido.');
    const next = {pool:validCounts(value.pool),deck:validCounts(value.deck),basics:validCounts(value.basics)};
    if(!rules.extraBasicLands&&Object.keys(next.basics).length)throw Error('Terre base aggiuntive non previste dal profilo.');
    for(const [id,n] of Object.entries(next.deck))if(!basicCard(id)&&rules.maxCopies!=null&&n>rules.maxCopies)throw Error('Limite di copie del formato superato.');
    for (const [id,n] of Object.entries(next.deck)) if (n>(next.pool[id]||0)) throw Error('Il mazzo supera le copie nel pool.');
    for (const id of Object.keys(next.basics)) if (!isBasic(id)) throw Error('Le terre aggiunte devono essere terre base normali.');
    return next;
  }
  function stored(storageKey,fallback=empty(),selectedMode=mode) {
    if(memoryStates.has(storageKey))return {value:structuredClone(memoryStates.get(storageKey)),persistent:false};
    let raw;
    try { raw=localStorage.getItem(storageKey); }
    catch { return {value:fallback,persistent:false}; }
    return {value:raw?validate(JSON.parse(raw),selectedMode):empty(),persistent:true};
  }
  function load() {
    storageError='';
    if(!mode){state=empty();storageError='Regole del formato non disponibili: pool e mazzo non sono ancora utilizzabili.';status();return;}
    try { const result=stored(key());state=result.value;if(!result.persistent)storageError='Memoria non disponibile. Esporta il lavoro prima di chiudere la pagina.'; }
    catch { state=empty();storageError='Salvataggio non leggibile: il contenuto originale è conservato e non verrà sovrascritto.'; }
    status();
  }
  let writes=Promise.resolve();
  function changeState(mutate,selectedMode=mode) {
    const storageKey=key(selectedMode);
    const apply=()=>{
      const result=stored(storageKey,selectedMode===mode?state:empty(),selectedMode);
      mutate(result.value);
      validate(result.value,selectedMode);
      let message='';
      try { localStorage.setItem(storageKey,JSON.stringify(result.value));memoryStates.delete(storageKey); }
      catch { memoryStates.set(storageKey,result.value);message='Memoria del browser non disponibile. Il lavoro resta in questa pagina: esportalo per conservarlo.'; }
      if(mode===selectedMode){state=result.value;storageError=message;refresh();}
    };
    // Serialize same-pool changes across tabs, and read the latest state inside the lock.
    const task=writes.then(()=>navigator.locks?navigator.locks.request(storageKey,apply):apply());
    writes=task.catch(()=>{storageError='Salvataggio non leggibile: il contenuto originale è conservato e non verrà sovrascritto.';status();});
    return task;
  }
  function refresh() {
    const focus=captureFocus();renderDeck();
    if($('catalog-onlypool')?.checked)renderCards();
    if($('trk-cards')){
      for(const row of $('trk-cards').querySelectorAll('.trk-actions')){
        const id=row.querySelector('[data-id]')?.dataset.id;
        if(byId.has(id))row.outerHTML=actions(byId.get(id),row.dataset.deckControls==='true');
      }
    }
    restoreFocus(focus);status();
    if($('trk-hand'))clearHand();
  }
  function sync() { load();refresh(); }
  addEventListener('storage',event=>{if(event.key===key()||event.key===null)sync();});
  addEventListener('pageshow',event=>{if(event.persisted)sync();});
  function captureFocus() {
    const active=document.activeElement;
    return {active,area:active.closest?.('#trk-deck,#trk-cards,#trk-basics,#trk-hand')?.id,id:active.id,op:active.dataset?.op,card:active.dataset?.id,basic:active.dataset?.basic,bottom:active.dataset?.bottom};
  }
  function restoreFocus(focus) {
    if(!focus||focus.active.isConnected&&!focus.active.disabled)return;
    const area=$(focus.area);
    let target=focus.id?$(focus.id):null;
    if(area&&focus.card){
      target=area.querySelector(`[data-id="${focus.card}"][data-op="${focus.op}"]`);
      if(!target||target.disabled)target=area.querySelector(`.trk-actions button[data-id="${focus.card}"]:not(:disabled)`);
    }
    if(area&&focus.basic)target=area.querySelector(`[data-basic="${focus.basic}"]`);
    if(area&&focus.bottom!==undefined)target=area.querySelector(`[data-bottom="${focus.bottom}"]`);
    if(!target||target.disabled)target=area||$('trk-draw');
    if(target&&!target.disabled){if(!target.matches('button,input,select,[tabindex]'))target.tabIndex=-1;target.focus({preventScroll:true});}
  }
  const ref = c => `<span class="card-reference" tabindex="0" role="button" data-card-preview="${esc(c.name)}" aria-label="Mostra ${esc(c.name)}">${esc(c.name)}</span>`;
  function actions(c, deckControls=false) {
    if(!eventRules())return '';
    return `<div class="trk-actions" data-deck-controls="${deckControls}"><span>Pool: ${state.pool[c.id]||0}</span><button type="button" data-op="pool-minus" data-id="${c.id}" aria-label="Rimuovi una copia dal pool: ${esc(c.name)}" ${!state.pool[c.id]?'disabled':''}>Pool −</button><button type="button" data-op="pool-plus" data-id="${c.id}" aria-label="Aggiungi una copia al pool: ${esc(c.name)}">Pool +</button>${deckControls?`<span>Mazzo: ${state.deck[c.id]||0}</span><button type="button" data-op="deck-minus" data-id="${c.id}" aria-label="Rimuovi dal mazzo: ${esc(c.name)}" ${!state.deck[c.id]?'disabled':''}>Mazzo −</button><button type="button" data-op="deck-plus" data-id="${c.id}" aria-label="Aggiungi al mazzo: ${esc(c.name)}" ${(state.deck[c.id]||0)>=Math.min(state.pool[c.id]||0,basicCard(c.id)||eventRules().maxCopies==null?999:eventRules().maxCopies)?'disabled':''}>Mazzo +</button>`:''}</div>`;
  }
  function card(c, controls=false, variants=false) {
    let watch=false;
    try { watch=JSON.parse(localStorage.getItem(EXPANSION_CONFIG.storage.watch)||'[]').some(value=>value===c.id||value===c.name); } catch {}
    const legal=$('trk-legality')?.value;
    return `<article class="trk-card">${variants&&c.image?`<img class="trk-card-image" src="${esc(c.image)}" width="488" height="680" loading="lazy" decoding="async" alt="${esc(c.name)}" data-card-preview="${esc(c.name)}" tabindex="0" role="button" aria-label="Mostra immagine ingrandita: ${esc(c.name)}">`:''}<h3>${ref(c)}</h3><div class="trk-meta">${esc(c.set)} #${esc(c.number)} · ${esc(c.mana||'Senza costo di mana')} · ${esc(c.rarity)} · MV ${c.cmc}</div><p>${esc(c.type)}</p>${catalog?catalog.summary(c):''}<p class="trk-oracle">${esc(c.text)}</p><p><a href="${esc(c.url)}" target="_blank" rel="noopener" aria-label="Testo e dettagli: ${esc(c.name)}">Testo e dettagli ↗</a></p>${legal?`<p>Stato ${esc(legal)}: ${esc(legality(c,legal)||'non disponibile')} (${$('trk-legality-scope')?.value==='release'?'ammissibilità prevista all’uscita':esc(DATA.date||'data non disponibile')}).</p>`:''}${c.prospects&&window.CardProspects?`<details class="trk-prospects"><summary>Analisi, formati, prezzi e fonti</summary>${window.CardProspects.render(c,DATA.prospectSources||[])}</details>`:''}${controls?actions(c):''}${pageKey==='discovery'?`<button data-op="watch" data-id="${c.id}" type="button" aria-pressed="${watch}">${watch?'Osservata':'Segui carta'}</button>`:''}${variants&&c.prints.length>1?`<details><summary>${c.prints.length} stampe nello snapshot</summary><p>La presenza nel catalogo non certifica l’apertura nel prodotto selezionato per questo evento. Trattamenti e idoneità vanno verificati nella guida ufficiale.</p><div class="trk-variants">${c.prints.map(p=>`<div>${p.image?`<img src="${esc(p.image)}" loading="lazy" alt="${esc(c.name)} #${esc(p.number)}">`:''}<p>#${esc(p.number)} · ${esc(p.finishes.join(', '))}</p></div>`).join('')}</div></details>`:''}</article>`;
  }
  function legality(c,format) { return $('trk-legality-scope')?.value==='release' ? c.prospects?.formats?.[format]?.releaseEligibility?.status||c.legalities[format] : c.legalities[format]; }
  function filtered() {
    const q=($('trk-search')?.value||'').trim().toLocaleLowerCase();
    const color=$('trk-color')?.value, rarity=$('trk-rarity')?.value, set=$('trk-set')?.value, legal=$('trk-legality')?.value;
    let items=DATA.cards.filter(c=>(!catalog||catalog.extraMatches(c))&&(!$('catalog-onlypool')?.checked||state.pool[c.id])&&(!q||(c.name+' '+c.type+' '+c.text).toLocaleLowerCase().includes(q))&&(!rarity||c.rarity===rarity)&&(!set||c.set===set)&&(!color||(color==='C'?c.colors.length===0&&!c.land:color==='M'?c.colors.length>1:color==='L'?c.land:c.colors.includes(color)))&&(!legal||['legal','restricted'].includes(legality(c,legal))));
    const order=$('trk-order')?.value;
    items.sort((a,b)=>catalog?catalog.compareCards(a,b,order):order==='name'?a.name.localeCompare(b.name):order==='cmc'?a.cmc-b.cmc||a.name.localeCompare(b.name):a.set.localeCompare(b.set)||Number(a.number)-Number(b.number));
    return items;
  }
  function focusPage(){const count=$('trk-count');count.tabIndex=-1;count.scrollIntoView({block:'start'});count.focus({preventScroll:true});}
  function renderCards() {
    if (!$('trk-cards')) return;
    const items=filtered(),pages=Math.max(1,Math.ceil(items.length/12)); page=Math.min(page,pages-1);
    $('trk-count').textContent=`${items.length} / ${DATA.cards.length} carte distinte disponibili. ${DATA.complete?"Catalogo completo":"Catalogo parziale"}.`;
    $('trk-cards').innerHTML=items.length?items.slice(page*12,page*12+12).map(c=>card(c,pageKey!=='discovery',true)).join(''):'<p>Nessuna carta corrisponde ai filtri nello snapshot. Le carte non ancora rivelate non sono incluse.</p>';
    $('trk-page').textContent=`Pagina ${page+1} di ${pages}`;
    $('trk-prev').disabled=page===0;$('trk-next').disabled=page===pages-1;
  }
  function deckEntries() {
    const counts={...state.deck};
    for(const [id,n] of Object.entries(state.basics)) counts[id]=(counts[id]||0)+n;
    return Object.entries(counts).filter(([,n])=>n>0).map(([id,n])=>({c:byId.get(id),n}));
  }
  function renderRules() {
    const rules=eventRules();
    const notice=rules?`${rules.name}: almeno ${rules.minDeckSize} carte. ${rules.maxCopies==null?'Nessun limite alle copie non base provenienti dal pool.':`Limite di ${rules.maxCopies} copie per nome, eccetto le terre base.`} ${rules.extraBasicLands?'Puoi aggiungere terre base normali.':'Non puoi aggiungere terre base oltre a quelle del pool.'} Le carte restanti sono la sideboard.`:'Regole del formato non disponibili.';
    document.querySelectorAll('[data-event-rules]').forEach(node=>node.textContent=notice);
    if($('trk-new-hand'))$('trk-new-hand').textContent=rules?`Mescola e pesca ${rules.mulligan.handSize} carte`:'Mano iniziale non disponibile';
  }
  function renderDeck() {
    renderRules();
    if(!eventRules()){if($('trk-deck-status'))$('trk-deck-status').textContent='Regole del formato non disponibili.';for(const id of ['trk-new-hand','trk-mulligan','trk-keep','trk-draw'])if($(id))$(id).disabled=true;return;}
    const entries=deckEntries(), total=entries.reduce((s,x)=>s+x.n,0), pool=Object.values(state.pool).reduce((s,n)=>s+n,0);
    const lands=entries.filter(x=>x.c.type.includes('Land')).reduce((s,x)=>s+x.n,0);
    if($('trk-deck-status')) $('trk-deck-status').textContent=`Pool: ${pool} copie. Mazzo: ${total} carte, ${lands} terre, ${total-lands} non terre. ${total<eventRules().minDeckSize?'Mancano '+(eventRules().minDeckSize-total)+' carte al minimo di '+eventRules().minDeckSize+'.':'Minimo di '+eventRules().minDeckSize+' raggiunto.'} Controllo delle quantità, non certificazione del pool.`;
    if($('trk-new-hand')) $('trk-new-hand').disabled=total<eventRules().minDeckSize;
    if($('trk-storage-status')) $('trk-storage-status').textContent=storageError;
    if(!$('trk-deck')) return;
    $('trk-deck').innerHTML=Object.keys(state.pool).length?DATA.cards.filter(c=>state.pool[c.id]>0).map(c=>`<div class="trk-card"><h3>${ref(c)}</h3>${actions(c,true)}</div>`).join(''):'<p>Il pool è vuoto. Cerca le carte qui sotto e aggiungi le copie.</p>';
    $('trk-basics').innerHTML=basics.map((name,i)=>`<label>${esc(name)} aggiunte<input type="number" min="0" max="999" step="1" value="${state.basics[basicIds[i]]||0}" data-basic="${basicIds[i]}" aria-label="${esc(name)} aggiunte al mazzo" ${eventRules().extraBasicLands?'':'disabled'}></label>`).join('');
    const curve=Array(8).fill(0);
    entries.filter(x=>!x.c.type.includes('Land')).forEach(x=>curve[Math.min(7,Math.floor(x.c.cmc))]+=x.n);
    const max=Math.max(1,...curve);
    $('trk-curve').innerHTML=curve.map((n,i)=>`<div><div class="trk-bar"><i style="height:${Math.max(3,n/max*90)}px"></i></div><span>MV ${i===7?'7+':i}: ${n}</span></div>`).join('');
    const sources=['W','U','B','R','G'].map(color=>{
      const n=entries.filter(x=>x.c.type.includes('Land')&&((isBasic(x.c.id)&&basicIds['WUBRG'.indexOf(color)]===x.c.id)||new RegExp('\\{'+color+'\\}').test(x.c.text))).reduce((s,x)=>s+x.n,0);
      return color+': '+n;
    });
    $('trk-sources').textContent='Fonti di mana sulle terre (lettura del testo): '+sources.join(' · ')+'. Le condizioni di produzione, il mana filtrato e le fonti non terra richiedono verifica manuale.';
  }
  function renderCompare() {
    if(!$('trk-compare'))return;
    $('trk-compare').innerHTML=[$('trk-compare-a').value,$('trk-compare-b').value].map(id=>card(byId.get(id))).join('');
  }
  function shuffle(items) {
    const out=[...items];for(let i=out.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[out[i],out[j]]=[out[j],out[i]];}return out;
  }
  function clearHand() {
    hand=[];library=[];bottom=[];mulligans=0;kept=false;
    if($('trk-hand')){$('trk-hand').innerHTML='';$('trk-hand-status').textContent='Scegli il mazzo e mescola per iniziare.';for(const id of ['trk-mulligan','trk-keep','trk-draw'])$(id).disabled=true;}
  }
  function deal(mulligan=false) {
    fullDeck=deckEntries().flatMap(x=>Array(x.n).fill(x.c.id));
    if(!eventRules()||fullDeck.length<eventRules().minDeckSize)return;
    mulligans=mulligan?mulligans+1:0;kept=false;bottom=[];
    library=shuffle(fullDeck);hand=library.splice(0,handSize());renderHand();
  }
  function renderHand() {
    const focus=captureFocus();
    $('trk-hand').innerHTML=hand.map((id,i)=>`<div class="${bottom.includes(i)?'trk-hand-selected':''}">${card(byId.get(id))}${!kept&&mulligans>0?`<button type="button" data-bottom="${i}" aria-pressed="${bottom.includes(i)}">${bottom.includes(i)?'In fondo, posizione '+(bottom.indexOf(i)+1):'Metti in fondo'}</button>`:''}</div>`).join('');
    $('trk-hand-status').textContent=kept?`Mano tenuta: ${hand.length} carte. Biblioteca: ${library.length}.`:`Mulligan effettuati: ${mulligans}. Seleziona ${bottomCount()} carte da mettere in fondo. Selezionate: ${bottom.length}.`;
    $('trk-mulligan').disabled=kept||bottomCount()>=handSize();
    $('trk-keep').disabled=kept||bottom.length!==bottomCount();
    $('trk-draw').disabled=!kept||!library.length;
    restoreFocus(focus);
  }
  if($('trk-mode')){const select=$('trk-mode'),allowed=allowedModes;for(const option of [...select.options])if(!allowed.includes(option.value))option.remove();for(const id of allowed)if(![...select.options].some(option=>option.value===id))select.add(new Option(EXPANSION_CONFIG.events[id].name,id));select.disabled=!allowed.length;}
  load();
  modeLinks();
  if($('trk-mode')){$('trk-mode').value=mode;$('trk-mode').addEventListener('change',()=>{mode=$('trk-mode').value;const url=new URL(location.href);url.searchParams.set('mode',mode);history.replaceState(null,'',url);modeLinks();load();clearHand();refresh();});}
  for(const id of ['trk-search','trk-color','trk-rarity','trk-set','trk-order','trk-legality','trk-legality-scope'])$(id)?.addEventListener(id==='trk-search'?'input':'change',()=>{page=0;renderCards();});
  $('catalog-onlypool')?.addEventListener('change',()=>{page=0;renderCards()});
  if(catalog)for(const id of catalog.ids)$(id).addEventListener($(id).type==='number'?'input':'change',()=>{page=0;renderCards()});
  $('trk-reset')?.addEventListener('click',()=>{for(const id of ['trk-search','trk-color','trk-rarity','trk-set','trk-legality'])if($(id))$(id).value='';if($('trk-legality-scope'))$('trk-legality-scope').value='snapshot';if(catalog){catalog.reset();$('catalog-onlypool').checked=false}$('trk-order').value=catalog?'set':'number';page=0;renderCards();});
  $('trk-prev')?.addEventListener('click',()=>{page--;renderCards();focusPage();});$('trk-next')?.addEventListener('click',()=>{page++;renderCards();focusPage();});
  document.addEventListener('click',event=>{
    const button=event.target.closest('button[data-op]');
    if(button){
      const id=button.dataset.id,op=button.dataset.op;if(!byId.has(id))return;
      if(op==='watch'){
        try{const saved=JSON.parse(localStorage.getItem(EXPANSION_CONFIG.storage.watch)||'[]');if(!Array.isArray(saved)||saved.some(value=>typeof value!=='string'))throw Error('Osservate non leggibili');const ids=new Set(saved),name=byId.get(id)?.name||id;if(ids.has(id)||ids.has(name)){ids.delete(id);ids.delete(name);}else ids.add(id);localStorage.setItem(EXPANSION_CONFIG.storage.watch,JSON.stringify([...ids]));button.setAttribute('aria-pressed',String(ids.has(id)||ids.has(name)));button.textContent=ids.has(id)||ids.has(name)?'Osservata':'Segui carta';}catch{button.textContent='Memoria non disponibile';}return;
      }
      const group=op.startsWith('pool')?'pool':'deck',delta=op.endsWith('plus')?1:-1;
      changeState(next=>{
        next[group][id]=Math.max(0,Math.min(999,(next[group][id]||0)+delta));
        if(group==='pool')next.deck[id]=Math.min(next.deck[id]||0,next.pool[id]);
        else next.deck[id]=Math.min(next.deck[id],next.pool[id]||0,basicCard(id)||eventRules().maxCopies==null?999:eventRules().maxCopies);
        for(const kind of ['pool','deck'])if(!next[kind][id])delete next[kind][id];
      }).catch(()=>{});
    }
    const pick=event.target.closest('[data-bottom]');
    if(pick&&!kept){const focus=captureFocus(),i=Number(pick.dataset.bottom);if(bottom.includes(i))bottom=bottom.filter(x=>x!==i);else if(bottom.length<bottomCount())bottom.push(i);renderHand();restoreFocus(focus);}
  });
  $('trk-basics')?.addEventListener('change',event=>{
    const id=event.target.dataset.basic;if(!eventRules()?.extraBasicLands||!isBasic(id))return;
    const n=Math.max(0,Math.min(999,Math.floor(Number(event.target.value)||0)));
    changeState(next=>{next.basics[id]=n;}).catch(()=>{});
  });
  $('trk-export')?.addEventListener('click',async()=>{
    await writes;
    try { state=stored(key(),state).value; }
    catch { status('Salvataggio non leggibile: il contenuto originale è conservato e non verrà sovrascritto.');return; }
    const data={version:1,set:EXPANSION_CONFIG.code,mode,snapshot:DATA.date,...state};
    const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download=EXPANSION_CONFIG.id+'-'+mode+'-pool.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  $('trk-import')?.addEventListener('change',async event=>{
    const file=event.target.files[0];if(!file)return;
    const importMode=mode;
    try{
      if(file.size>1000000)throw Error('File troppo grande.');
      const imported=JSON.parse(await file.text());
      if(imported.version!==1||imported.set!==EXPANSION_CONFIG.code||imported.mode!==importMode)throw Error('File di un altro set, formato o versione. Seleziona prima il pool corretto.');
      const next=validate(imported);
      await changeState(value=>{Object.assign(value,next);},importMode);
      status(storageError||'Pool e mazzo importati.');
    }catch(error){$('trk-storage-status').textContent='Importazione non eseguita: '+error.message;}
    event.target.value='';
  });
  for(const id of ['trk-compare-a','trk-compare-b'])if($(id)){
    $(id).innerHTML=DATA.cards.map(c=>`<option value="${c.id}">${esc(c.name)}</option>`).join('');
    $(id).value=DATA.cards[id.endsWith('b')?1:0].id;$(id).addEventListener('change',renderCompare);
  }
  $('trk-new-hand')?.addEventListener('click',()=>deal());
  $('trk-mulligan')?.addEventListener('click',()=>deal(true));
  $('trk-keep')?.addEventListener('click',()=>{if(bottom.length!==bottomCount())return;library.push(...bottom.map(i=>hand[i]));hand=hand.filter((_,i)=>!bottom.includes(i));bottom=[];kept=true;renderHand();});
  $('trk-draw')?.addEventListener('click',()=>{if(kept&&library.length){hand.push(library.shift());renderHand();}});
  if($('trk-statistics')){
    const counts={};DATA.cards.forEach(c=>counts[c.rarity]=(counts[c.rarity]||0)+1);
    $('trk-statistics').innerHTML='<div class="trk-stat-grid">'+Object.entries(counts).map(([r,n])=>`<p><span>${n}</span>${esc(r)}</p>`).join('')+'</div><p>'+DATA.print_count+' stampe, '+DATA.cards.length+' carte distinte nel catalogo '+(DATA.complete?'completo':'parziale')+'.</p>';
  }
  const linkedCard=byId.get(new URLSearchParams(location.search).get('card'));
  if(linkedCard&&$('trk-search')){$('trk-search').value=linkedCard.name;page=0;}
  renderCards();renderDeck();renderCompare();
})();
