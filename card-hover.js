'use strict';
// Shared card previews for the report, catalog, analysis and simulator.
(() => {
  const source = typeof DRAFT_DATA !== 'undefined' ? [...(DRAFT_DATA.poolCards || []), ...DRAFT_DATA.cards] : typeof DATA !== 'undefined' ? [...DATA.cards,...(DATA.previewCards||[])] : [];
  if (!Array.isArray(source) || !source.length) return;
  const cards = new Map();
  for (const card of source) {
    if (!card.image) continue;
    for (const name of [card.name, card.full, ...(card.faces || []).map(f => f.name)].filter(Boolean)) {
      cards.set(name, card);
    }
  }
  const aliasNames=new Set();
  if (typeof DRAFT_DATA !== 'undefined') {
    const aliases = typeof EXPANSION_CONFIG!=='undefined' ? EXPANSION_CONFIG.ui.cardAliases||{} : {};
    for (const [alias, name] of Object.entries(aliases)) if (cards.has(name)){cards.set(alias, cards.get(name));aliasNames.add(alias);}
  }
  const escape = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const normalize = s => s.replace(/’/g, "'");
  const normalized = new Map([...cards].map(([name, card]) => [normalize(name), card]));
  function buildPattern(){const names=[...cards.keys()].sort((a,b)=>b.length-a.length).map(n=>escape(n).replace(/['’]/g,"['’]"));return new RegExp('(?<![\\p{L}\\p{N}])(?:'+names.join('|')+')(?![\\p{L}\\p{N}])','gu')}
  let pattern = buildPattern();
  const preview = document.createElement('div');
  preview.id = 'mtg-card-preview'; preview.setAttribute('role','tooltip');
  preview.setAttribute('popover','manual'); preview.hidden=true;
  const image=document.createElement('img'), caption=document.createElement('div'), status=document.createElement('div');
  caption.className='mtg-preview-caption'; status.className='mtg-preview-status';
  preview.append(image,caption,status);document.body.append(preview);
  let active=null, pinned=false, framePending=false, scrollTimer=null, resumeHover=null;
  const skip='script,style,noscript,textarea,input,select,option,code,pre,.card-reference,#mtg-card-preview,[contenteditable="true"]';
  function annotate(root) {
    if(root.nodeType!==Node.ELEMENT_NODE || root.closest(skip))return;
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode(node){return node.parentElement?.closest(skip)?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT}});
    const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
    for(const node of nodes){
      pattern.lastIndex=0; const text=node.nodeValue,matches=[...text.matchAll(pattern)].filter(m=>!aliasNames.has(normalize(m[0]))||node.parentElement.closest('.report,#dd-guide,#dd-stage')); if(!matches.length)continue;
      const fragment=document.createDocumentFragment();let pos=0;
      for(const match of matches){
        fragment.append(document.createTextNode(text.slice(pos,match.index)));
        const span=document.createElement('span');span.className='card-reference';span.dataset.cardPreview=normalize(match[0]);span.textContent=match[0];
        if(!node.parentElement.closest('a,button')){span.tabIndex=0;span.setAttribute('role','button');span.setAttribute('aria-label','Mostra '+match[0]);}
        fragment.append(span);pos=match.index+match[0].length;
      }
      fragment.append(document.createTextNode(text.slice(pos)));node.replaceWith(fragment);
    }
  }
  function target(el){return el instanceof Element?(el.closest('[data-card-preview]') || el.closest('a,button')?.querySelector('[data-card-preview]')):null;}
  function position(trigger,event){
    const rect=trigger.getBoundingClientRect(),pad=12;
    const width=Math.max(80,Math.min(260,innerWidth-pad*2,(innerHeight-72)*488/680));
    preview.style.width=width+'px';
    const height=width*680/488+44;
    let x=event?.clientX??rect.right,y=event?.clientY??rect.top;
    x=x+18+width<=innerWidth-pad?x+18:x-width-18;
    y=Math.min(y+16,innerHeight-height-pad);
    preview.style.left=Math.max(pad,Math.min(x,innerWidth-width-pad))+'px';
    preview.style.top=Math.max(pad,y)+'px';
  }
  function hide(){
    clearTimeout(scrollTimer);resumeHover=null;
    if(active){const original=active.dataset.previewDescription;if(original)active.setAttribute('aria-describedby',original);else active.removeAttribute('aria-describedby');delete active.dataset.previewDescription;}
    active=null;pinned=false;preview.hidden=true;
    if(preview.matches(':popover-open'))preview.hidePopover();
  }
  function show(trigger,event,lock=false){
    const card=normalized.get(trigger.dataset.cardPreview);if(!card)return;
    if(active!==trigger){hide();active=trigger;active.dataset.previewDescription=active.getAttribute('aria-describedby')||'';active.setAttribute('aria-describedby','mtg-card-preview');
      caption.textContent=card.name;status.textContent='';image.alt=card.name;image.src=card.image;
    }
    pinned=lock;preview.hidden=false;if(!preview.matches(':popover-open'))preview.showPopover();position(trigger,event);
  }
  image.onerror=()=>{status.textContent='Immagine non disponibile. Apri i dettagli della carta.';};
  image.onload=()=>{status.textContent='';};
  document.addEventListener('pointerover',event=>{if(event.pointerType==='touch'||pinned)return;const t=target(event.target);if(t)show(t,event);});
  document.addEventListener('pointermove',event=>{if(active&&!pinned&&event.pointerType!=='touch')position(active,event);});
  document.addEventListener('pointerout',event=>{if(!pinned&&active&&!active.contains(event.relatedTarget))hide();});
  document.addEventListener('focusin',event=>{const t=target(event.target);if(t)show(t);});
  document.addEventListener('focusout',()=>{if(!pinned)hide();});
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape')hide();
    const t=target(event.target);
    if(t && !t.closest('a,button') && ['Enter',' '].includes(event.key)){event.preventDefault();show(t,null,true);}
  });
  document.addEventListener('click',event=>{
    const t=target(event.target);
    if(t&&!t.closest('a,button')){if(active===t&&pinned)hide();else show(t,null,true);}
    else hide();
  });
  function onScroll(){
    // A touch can focus a card and scroll it into view after the click.
    // Keep it only while its reference is still on screen.
    if(active&&pinned){
      const rect=active.getBoundingClientRect();
      if(!active.isConnected||rect.bottom<=0||rect.top>=innerHeight||rect.right<=0||rect.left>=innerWidth){hide();return;}
      position(active);return;
    }
    const trigger=active||resumeHover,restore=trigger&&!pinned;
    hide();
    if(restore){resumeHover=trigger;scrollTimer=setTimeout(()=>{resumeHover=null;if(trigger.isConnected&&(trigger.matches(':hover')||target(document.activeElement)===trigger))show(trigger);},160);}
  }
  document.addEventListener('scroll',onScroll,true);window.addEventListener('resize',hide);window.addEventListener('blur',hide);
  // An embedded report can be hovered while keyboard focus remains in the host.
  if(window.parent!==window){try{
    window.parent.document.addEventListener('keydown',event=>{if(event.key==='Escape')hide();});
    window.parent.document.addEventListener('scroll',onScroll,true);
    window.parent.document.addEventListener('pointerdown',hide);
  }catch{ /* Standalone and cross-origin embeds keep their own listeners. */ }}
  const pendingRoots=new Set();
  const observer=new MutationObserver(records=>{
    for(const record of records){
      if(record.target===preview||preview.contains(record.target))continue;
      for(const node of record.addedNodes){
        const root=node.nodeType===Node.ELEMENT_NODE?node:node.parentElement;
        if(root&&!root.closest(skip))pendingRoots.add(root);
      }
    }
    if(framePending||!pendingRoots.size)return;
    framePending=true;requestAnimationFrame(()=>{
      framePending=false;const roots=[...pendingRoots];pendingRoots.clear();
      for(const root of roots)if(root.isConnected&&!roots.some(other=>other!==root&&other.contains(root)))annotate(root);
      if(active&&!active.isConnected)hide();
    });
  });
  window.addEventListener('mtg-card-data',event=>{
    for(const card of event.detail?.cards||[]){
      if(!card.image)continue;
      for(const name of [card.name,card.full,...(card.faces||[]).map(face=>face.name)].filter(Boolean)){cards.set(name,card);normalized.set(normalize(name),card)}
    }
    pattern=buildPattern();annotate(document.body);
  });
  annotate(document.body);observer.observe(document.body,{childList:true,subtree:true});
})();
