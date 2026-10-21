'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const byId = new Map(DATA.cards.map(c => [c.id, c]));
  const basics = ['Plains','Island','Swamp','Mountain','Forest'];
  const basicIds = basics.map(name => DATA.cards.find(c => c.name === name && c.type.startsWith('Basic Land'))?.id);
  const isBasic = id => basicIds.includes(id);
  const pageKey = document.body.dataset.page;
  let mode = pageKey === 'draft' ? 'draft' : 'sealed';
  let page = 0, state = empty(), storageError = '';
  let hand = [], library = [], fullDeck = [], bottom = [], mulligans = 0, kept = false;
  function empty() { return {pool:{},deck:{},basics:{}}; }
  function key() { return 'mtg-trk-'+mode+'-v1'; }
  function validCounts(obj) {
    if (!obj || typeof obj !== 'object' || Array.isArray(obj)) throw Error('Conteggi mancanti.');
    for (const [id, n] of Object.entries(obj)) if (!byId.has(id) || !Number.isInteger(n) || n<0 || n>999) throw Error('Carta o quantità non valida nel salvataggio.');
    return Object.fromEntries(Object.entries(obj).filter(([,n])=>n>0));
  }
  function validate(value) {
    if (!value || typeof value !== 'object') throw Error('Salvataggio non valido.');
    const next = {pool:validCounts(value.pool),deck:validCounts(value.deck),basics:validCounts(value.basics)};
    for (const [id,n] of Object.entries(next.deck)) if (n>(next.pool[id]||0)) throw Error('Il mazzo supera le copie nel pool.');
    for (const id of Object.keys(next.basics)) if (!isBasic(id)) throw Error('Le terre aggiunte devono essere terre base normali.');
    return next;
  }
  function load() {
    storageError='';
    try { const raw=localStorage.getItem(key()); state=raw?validate(JSON.parse(raw)):empty(); }
    catch { state=empty();storageError='Salvataggio non leggibile o memoria non disponibile. Esporta il lavoro prima di chiudere la pagina.'; }
  }
  function save() {
    try { localStorage.setItem(key(),JSON.stringify(state));storageError=''; }
    catch { storageError='Memoria del browser non disponibile. Il lavoro resta in questa pagina: esportalo per conservarlo.'; }
    if ($('trk-storage-status')) $('trk-storage-status').textContent=storageError;
  }
  const ref = c => `<span class="card-reference" tabindex="0" role="button" data-card-preview="${esc(c.name)}" aria-label="Mostra ${esc(c.name)}">${esc(c.name)}</span>`;
  function actions(c) {
    return `<div class="trk-actions"><span>Pool: ${state.pool[c.id]||0}</span><button type="button" data-op="pool-minus" data-id="${c.id}" aria-label="Rimuovi una copia dal pool: ${esc(c.name)}" ${!state.pool[c.id]?'disabled':''}>Pool −</button><button type="button" data-op="pool-plus" data-id="${c.id}" aria-label="Aggiungi una copia al pool: ${esc(c.name)}">Pool +</button><span>Mazzo: ${state.deck[c.id]||0}</span><button type="button" data-op="deck-minus" data-id="${c.id}" aria-label="Rimuovi dal mazzo: ${esc(c.name)}" ${!state.deck[c.id]?'disabled':''}>Mazzo −</button><button type="button" data-op="deck-plus" data-id="${c.id}" aria-label="Aggiungi al mazzo: ${esc(c.name)}" ${(state.deck[c.id]||0)>=(state.pool[c.id]||0)?'disabled':''}>Mazzo +</button></div>`;
  }
  function card(c, controls=false, variants=false) {
    let watch=false;
    try { watch=JSON.parse(localStorage.getItem('mtg-trk-watch-v1')||'[]').includes(c.id); } catch {}
    const legal=$('trk-legality')?.value;
    return `<article class="trk-card"><h3>${ref(c)}</h3><div class="trk-meta">${esc(c.set)} #${esc(c.number)} · ${esc(c.mana||'Senza costo di mana')} · ${esc(c.rarity)} · MV ${c.cmc}</div><p>${esc(c.type)}</p><p class="trk-oracle">${esc(c.text)}</p><p><a href="${esc(c.url)}" target="_blank" rel="noopener" aria-label="Testo e dettagli: ${esc(c.name)}">Testo e dettagli ↗</a></p>${legal?`<p>Stato ${esc(legal)}: ${esc(c.legalities[legal]||'non disponibile')} (21 ottobre).</p>`:''}${controls?actions(c):''}${pageKey==='discovery'?`<button data-op="watch" data-id="${c.id}" type="button" aria-pressed="${watch}">${watch?'Osservata':'Segui carta'}</button>`:''}${variants?`<details><summary>${c.prints.length} stampe nello snapshot</summary><p>La presenza nel catalogo non certifica l’apertura nei Play Booster. Trattamenti e idoneità vanno verificati nella guida ufficiale.</p><div class="trk-variants">${c.prints.map(p=>`<div>${p.image?`<img src="${esc(p.image)}" loading="lazy" alt="${esc(c.name)} #${esc(p.number)}">`:''}<p>#${esc(p.number)} · ${esc(p.finishes.join(', '))}</p></div>`).join('')}</div></details>`:''}</article>`;
  }
  function filtered() {
    const q=($('trk-search')?.value||'').trim().toLocaleLowerCase();
    const color=$('trk-color')?.value, rarity=$('trk-rarity')?.value, set=$('trk-set')?.value, legal=$('trk-legality')?.value;
    let items=DATA.cards.filter(c=>(!q||(c.name+' '+c.type+' '+c.text).toLocaleLowerCase().includes(q))&&(!rarity||c.rarity===rarity)&&(!set||c.set===set)&&(!color||(color==='C'?c.colors.length===0:color==='M'?c.colors.length>1:c.colors.includes(color)))&&(!legal||['legal','restricted'].includes(c.legalities[legal])));
    const order=$('trk-order')?.value;
    items.sort((a,b)=>order==='name'?a.name.localeCompare(b.name):order==='cmc'?a.cmc-b.cmc||a.name.localeCompare(b.name):a.set.localeCompare(b.set)||Number(a.number)-Number(b.number));
    return items;
  }
  function renderCards() {
    if (!$('trk-cards')) return;
    const items=filtered(),pages=Math.max(1,Math.ceil(items.length/12)); page=Math.min(page,pages-1);
    $('trk-count').textContent=`${items.length} / ${DATA.cards.length} carte distinte disponibili. Catalogo parziale.`;
    $('trk-cards').innerHTML=items.length?items.slice(page*12,page*12+12).map(c=>card(c,pageKey!=='discovery',true)).join(''):'<p>Nessuna carta corrisponde ai filtri nello snapshot. Le carte non ancora rivelate non sono incluse.</p>';
    $('trk-page').textContent=`Pagina ${page+1} di ${pages}`;
    $('trk-prev').disabled=page===0;$('trk-next').disabled=page===pages-1;
  }
  function deckEntries() {
    const counts={...state.deck};
    for(const [id,n] of Object.entries(state.basics)) counts[id]=(counts[id]||0)+n;
    return Object.entries(counts).filter(([,n])=>n>0).map(([id,n])=>({c:byId.get(id),n}));
  }
  function renderDeck() {
    const entries=deckEntries(), total=entries.reduce((s,x)=>s+x.n,0), pool=Object.values(state.pool).reduce((s,n)=>s+n,0);
    const lands=entries.filter(x=>x.c.type.includes('Land')).reduce((s,x)=>s+x.n,0);
    if($('trk-deck-status')) $('trk-deck-status').textContent=`Pool: ${pool} copie. Mazzo: ${total} carte, ${lands} terre, ${total-lands} non terre. ${total<40?'Mancano '+(40-total)+' carte al minimo di 40.':'Minimo di 40 raggiunto.'} Controllo delle quantità, non certificazione del pool.`;
    if($('trk-new-hand')) $('trk-new-hand').disabled=total<40;
    if($('trk-storage-status')) $('trk-storage-status').textContent=storageError;
    if(!$('trk-deck')) return;
    $('trk-deck').innerHTML=Object.keys(state.pool).length?DATA.cards.filter(c=>state.pool[c.id]>0).map(c=>`<div class="trk-card"><h3>${ref(c)}</h3>${actions(c)}</div>`).join(''):'<p>Il pool è vuoto. Cerca le carte qui sotto e aggiungi le copie.</p>';
    $('trk-basics').innerHTML=basics.map((name,i)=>`<label>${esc(name)} aggiunte<input type="number" min="0" max="999" step="1" value="${state.basics[basicIds[i]]||0}" data-basic="${basicIds[i]}" aria-label="${esc(name)} aggiunte al mazzo"></label>`).join('');
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
    if(fullDeck.length<40)return;
    mulligans=mulligan?mulligans+1:0;kept=false;bottom=[];
    library=shuffle(fullDeck);hand=library.splice(0,7);renderHand();
  }
  function renderHand() {
    $('trk-hand').innerHTML=hand.map((id,i)=>`<div class="${bottom.includes(i)?'trk-hand-selected':''}">${card(byId.get(id))}${!kept?`<button type="button" data-bottom="${i}" aria-pressed="${bottom.includes(i)}">${bottom.includes(i)?'In fondo, posizione '+(bottom.indexOf(i)+1):'Metti in fondo'}</button>`:''}</div>`).join('');
    $('trk-hand-status').textContent=kept?`Mano tenuta: ${hand.length} carte. Biblioteca: ${library.length}.`:`Mulligan effettuati: ${mulligans}. Seleziona ${mulligans} carte da mettere in fondo. Selezionate: ${bottom.length}.`;
    $('trk-mulligan').disabled=kept||mulligans>=7;
    $('trk-keep').disabled=kept||bottom.length!==mulligans;
    $('trk-draw').disabled=!kept||!library.length;
  }
  load();
  if($('trk-mode')){$('trk-mode').value=mode;$('trk-mode').addEventListener('change',()=>{mode=$('trk-mode').value;load();page=0;clearHand();renderDeck();renderCards();});}
  for(const id of ['trk-search','trk-color','trk-rarity','trk-set','trk-order','trk-legality'])$(id)?.addEventListener(id==='trk-search'?'input':'change',()=>{page=0;renderCards();});
  $('trk-reset')?.addEventListener('click',()=>{for(const id of ['trk-search','trk-color','trk-rarity','trk-set','trk-legality'])if($(id))$(id).value='';$('trk-order').value='number';page=0;renderCards();});
  $('trk-prev')?.addEventListener('click',()=>{page--;renderCards();});$('trk-next')?.addEventListener('click',()=>{page++;renderCards();});
  document.addEventListener('click',event=>{
    const button=event.target.closest('button[data-op]');
    if(button){
      const id=button.dataset.id,op=button.dataset.op;if(!byId.has(id))return;
      if(op==='watch'){
        try{const ids=new Set(JSON.parse(localStorage.getItem('mtg-trk-watch-v1')||'[]'));if(ids.has(id))ids.delete(id);else ids.add(id);localStorage.setItem('mtg-trk-watch-v1',JSON.stringify([...ids]));button.setAttribute('aria-pressed',String(ids.has(id)));button.textContent=ids.has(id)?'Osservata':'Segui carta';}catch{button.textContent='Memoria non disponibile';}return;
      }
      const group=op.startsWith('pool')?'pool':'deck',delta=op.endsWith('plus')?1:-1;
      state[group][id]=Math.max(0,Math.min(999,(state[group][id]||0)+delta));
      if(group==='pool')state.deck[id]=Math.min(state.deck[id]||0,state.pool[id]);
      else state.deck[id]=Math.min(state.deck[id],state.pool[id]||0);
      for(const kind of ['pool','deck'])if(!state[kind][id])delete state[kind][id];
      save();renderDeck();
      // Keep the active control in place for repeated keyboard or touch actions.
      document.querySelectorAll(`.trk-actions button[data-id="${id}"]`).forEach(b=>{
        const row=b.parentElement;row.outerHTML=actions(byId.get(id));
      });
      const replacement=document.querySelector(`#trk-cards button[data-id="${id}"][data-op="${op}"]`);
      if(replacement&&!replacement.disabled)replacement.focus({preventScroll:true});
    }
    const pick=event.target.closest('[data-bottom]');
    if(pick&&!kept){const i=Number(pick.dataset.bottom);if(bottom.includes(i))bottom=bottom.filter(x=>x!==i);else if(bottom.length<mulligans)bottom.push(i);renderHand();}
  });
  $('trk-basics')?.addEventListener('change',event=>{
    const id=event.target.dataset.basic;if(!isBasic(id))return;
    state.basics[id]=Math.max(0,Math.min(999,Math.floor(Number(event.target.value)||0)));save();renderDeck();
  });
  $('trk-export')?.addEventListener('click',()=>{
    const data={version:1,set:'TRK',mode,snapshot:DATA.date,...state};
    const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download='star-trek-'+mode+'-pool.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  $('trk-import')?.addEventListener('change',async event=>{
    const file=event.target.files[0];if(!file)return;
    try{
      if(file.size>1000000)throw Error('File troppo grande.');
      const imported=JSON.parse(await file.text());
      if(imported.version!==1||imported.set!=='TRK'||imported.mode!==mode)throw Error('File di un altro set, formato o versione. Seleziona prima il pool corretto.');
      const next=validate(imported);state=next;save();renderDeck();renderCards();
      $('trk-storage-status').textContent=storageError||'Pool e mazzo importati.';
    }catch(error){$('trk-storage-status').textContent='Importazione non eseguita: '+error.message;}
    event.target.value='';
  });
  for(const id of ['trk-compare-a','trk-compare-b'])if($(id)){
    $(id).innerHTML=DATA.cards.map(c=>`<option value="${c.id}">${esc(c.name)}</option>`).join('');
    $(id).value=DATA.cards[id.endsWith('b')?1:0].id;$(id).addEventListener('change',renderCompare);
  }
  $('trk-new-hand')?.addEventListener('click',()=>deal());
  $('trk-mulligan')?.addEventListener('click',()=>deal(true));
  $('trk-keep')?.addEventListener('click',()=>{if(bottom.length!==mulligans)return;library.push(...bottom.map(i=>hand[i]));hand=hand.filter((_,i)=>!bottom.includes(i));bottom=[];kept=true;renderHand();});
  $('trk-draw')?.addEventListener('click',()=>{if(kept&&library.length){hand.push(library.shift());renderHand();}});
  if($('trk-statistics')){
    const counts={};DATA.cards.forEach(c=>counts[c.rarity]=(counts[c.rarity]||0)+1);
    $('trk-statistics').innerHTML='<div class="trk-stat-grid">'+Object.entries(counts).map(([r,n])=>`<p><span>${n}</span>${esc(r)}</p>`).join('')+'</div><p>'+DATA.print_count+' stampe, '+DATA.cards.length+' carte distinte nel catalogo parziale.</p>';
  }
  renderCards();renderDeck();renderCompare();
})();
