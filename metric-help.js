'use strict';
(() => {
  const terms = {
    'GIH WR': ['Games in Hand Win Rate', 'Percentuale di vittorie nelle partite in cui la carta era nella mano iniziale o è stata pescata. Non misura il vantaggio causato dalla carta.'],
    GIH: ['Games in Hand', 'Carta vista in mano, nella mano iniziale o pescata durante la partita. Nelle colonne percentuali indica il win rate di queste partite; il campione conta queste osservazioni, non i draft.'],
    ATA: ['Average Taken At', 'Posizione media alla quale una carta viene scelta nella busta. ATA 10,7 significa circa undicesimo pick. Un valore basso indica scelte più precoci.'],
    ALSA: ['Average Last Seen At', 'Posizione media di ultima vista della carta nelle buste osservate. ALSA 7,1 significa circa settimo pick. Non indica quando viene scelta né garantisce che torni al giro.'],
    IWD: ['Improvement When Drawn', 'Win rate quando la carta è vista in mano meno win rate quando è nel mazzo ma non viene vista. Espresso in punti percentuali: −3,8 indica 3,8 punti in meno. È un confronto osservativo, non una perdita causata dalla carta.'],
    WR: ['Win Rate', 'Percentuale di vittorie nel campione indicato. WR 55% significa 55 vittorie ogni 100 partite osservate.'],
    pp: ['Punti percentuali', 'Differenza fra due percentuali. Dal 48% al 44,2% sono −3,8 punti percentuali.'],
    'N/D': ['Non disponibile', 'Il dato manca o non è pubblicato per quel campione. Non significa zero né che la carta sia debole.'],
    BO1: ['Best of One', 'Incontro deciso da una sola partita, come nel Premier Draft. Non c’è il normale cambio di sideboard fra partite dello stesso incontro.'],
    BO3: ['Best of Three', 'Incontro al meglio delle tre partite: vince chi ne vince due. Fra le partite puoi usare la sideboard, come nel Traditional Draft.'],
    CMC: ['Converted Mana Cost', 'Vecchio nome del valore di mana: somma del mana nel costo, indipendentemente dai colori.'],
    ETB: ['Enters the Battlefield', 'Ingresso sul campo di battaglia. Indica spesso un’abilità che si innesca quando il permanente entra.']
  };
  const aliases = {'GIH WR':'vittorie con la carta in mano',GIH:'carta vista in mano',ATA:'posizione media di scelta',ALSA:'ultima vista media',IWD:'scarto fra carta vista e non vista',WR:'percentuale di vittorie',pp:'punti percentuali','N/D':'non disponibile',BO1:'partita singola',BO3:'al meglio delle tre',CMC:'valore di mana',ETB:'ingresso sul campo'};
  const pattern=/(?<![\p{L}\p{N}])(?:GIH WR|ALSA|GIH|ATA|IWD|WR|BO1|BO3|CMC|ETB|N\/D|pp)(?![\p{L}\p{N}])/gu;
  const skip='script,style,noscript,input,textarea,select,option,code,pre,.metric-term,.card-reference,[data-card-preview],.oracle,#metric-help-tooltip,#mtg-card-preview,[contenteditable="true"]';
  const tip=document.createElement('div');tip.id='metric-help-tooltip';tip.setAttribute('popover','manual');tip.setAttribute('role','tooltip');tip.hidden=true;
  const heading=document.createElement('strong'),body=document.createElement('p');tip.append(heading,body);document.body.append(tip);
  let active=null,pinned=false,raf=false,scrollTimer=null,resume=null;const pending=new Set();
  function annotate(root){
    if(!root.isConnected||root.closest(skip))return;
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement.closest(skip)?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
    const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
    for(const node of nodes){
      const text=node.nodeValue;pattern.lastIndex=0;const matches=[...text.matchAll(pattern)];if(!matches.length)continue;
      const fragment=document.createDocumentFragment();let pos=0;
      for(const match of matches){
        fragment.append(document.createTextNode(text.slice(pos,match.index)));
        const term=document.createElement('abbr');term.className='metric-term';term.dataset.metricTerm=match[0];term.textContent=match[0];
        term.setAttribute('aria-label',match[0]+': '+aliases[match[0]]);
        if(!node.parentElement.closest('a,button,[role="button"]'))term.tabIndex=0;
        fragment.append(term);pos=match.index+match[0].length;
      }
      fragment.append(document.createTextNode(text.slice(pos)));node.replaceWith(fragment);
    }
    // Native option elements cannot contain formatted tooltips: expand their labels.
    for(const option of root.querySelectorAll('option:not([data-metric-expanded])')){
      pattern.lastIndex=0;option.textContent=option.textContent.replace(pattern,key=>key+' ('+aliases[key]+')');option.dataset.metricExpanded='true';
    }
  }
  function hide(){
    clearTimeout(scrollTimer);resume=null;
    if(active){const previous=active.dataset.metricDescription;if(previous)active.setAttribute('aria-describedby',previous);else active.removeAttribute('aria-describedby');delete active.dataset.metricDescription;}
    active=null;pinned=false;tip.hidden=true;if(tip.matches(':popover-open'))tip.hidePopover();
  }
  function show(term,lock=false){
    if(active!==term){hide();active=term;term.dataset.metricDescription=term.getAttribute('aria-describedby')||'';term.setAttribute('aria-describedby',((term.dataset.metricDescription||'')+' '+tip.id).trim());}
    pinned=lock;const key=term.dataset.metricTerm;heading.textContent=key+' · '+terms[key][0];body.textContent=terms[key][1];
    tip.hidden=false;if(!tip.matches(':popover-open'))tip.showPopover();
    const rect=term.getBoundingClientRect(),box=tip.getBoundingClientRect(),pad=12;
    const x=Math.max(pad,Math.min(rect.left,innerWidth-box.width-pad));
    let y=rect.bottom+8;if(y+box.height>innerHeight-pad)y=rect.top-box.height-8;
    tip.style.left=x+'px';tip.style.top=Math.max(pad,Math.min(y,innerHeight-box.height-pad))+'px';
  }
  const target=el=>el instanceof Element?el.closest('[data-metric-term]'):null;
  document.addEventListener('pointerover',e=>{if(e.pointerType==='touch'||pinned)return;const t=target(e.target);if(t)show(t);});
  document.addEventListener('pointerout',e=>{if(active&&!pinned&&!active.contains(e.relatedTarget)&&!tip.contains(e.relatedTarget))hide();});
  document.addEventListener('pointermove',e=>{if(e.pointerType==='touch'||pinned)return;const t=target(e.target);if(t&&t!==active)show(t);});
  tip.addEventListener('pointerleave',e=>{if(!pinned&&active&&!active.contains(e.relatedTarget))hide();});
  document.addEventListener('focusin',e=>{const t=target(e.target)||(e.target.matches('a,button')?e.target.querySelector('[data-metric-term]'):null);if(t)show(t);});
  document.addEventListener('focusout',()=>{if(!pinned)hide();});
  document.addEventListener('click',e=>{const t=target(e.target);if(t){if(active===t&&pinned)hide();else show(t,true);}else if(!tip.contains(e.target))hide();});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')hide();else if(['Enter',' '].includes(e.key)){const t=target(e.target);if(t&&!t.closest('a,button,label')){e.preventDefault();show(t,true);}}});
  function onScroll(){
    const trigger=active||resume,restore=trigger&&!pinned;hide();
    if(restore){resume=trigger;scrollTimer=setTimeout(()=>{resume=null;const focused=document.activeElement;if(trigger.isConnected&&(trigger.matches(':hover')||focused===trigger||focused.matches('a,button')&&focused.contains(trigger)))show(trigger);},160);}
  }
  document.addEventListener('scroll',onScroll,true);window.addEventListener('resize',hide);window.addEventListener('blur',hide);
  if(parent!==window){try{parent.document.addEventListener('keydown',e=>{if(e.key==='Escape')hide();});parent.document.addEventListener('scroll',onScroll,true);parent.document.addEventListener('pointerdown',hide);}catch{}}
  const observer=new MutationObserver(records=>{
    for(const r of records){if(tip.contains(r.target)||r.target===tip)continue;for(const n of r.addedNodes){const root=n.nodeType===Node.ELEMENT_NODE?n:n.parentElement;if(root&&!root.closest(skip))pending.add(root);}}
    if(raf||!pending.size)return;raf=true;requestAnimationFrame(()=>{raf=false;const roots=[...pending];pending.clear();for(const root of roots)if(!roots.some(other=>root!==other&&other.contains(root)))annotate(root);if(active&&!active.isConnected)hide();});
  });
  annotate(document.body);observer.observe(document.body,{childList:true,subtree:true});
})();
