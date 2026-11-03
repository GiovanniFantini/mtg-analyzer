'use strict';
// Filters editorial assessments; never changes ratings, pools or game state.
document.querySelectorAll('[data-limited-review]').forEach(root=>{
 const rows=[...root.querySelectorAll('[data-lr-card]')],find=key=>root.querySelector('[data-lr-filter="'+key+'"]');
 const controls=['query','color','rarity','tier','context'].map(find),host=root.querySelector('[data-lr-results]');
 function render(){
  const q=find('query').value.trim().toLocaleLowerCase('it'),color=find('color').value,rarity=find('rarity').value,tier=find('tier').value,event=find('context').value;
  const visible=rows.filter(row=>(!q||row.dataset.search.includes(q))&&(!color||(color==='M'?row.dataset.colors.length>1:color==='C'?!row.dataset.colors:row.dataset.colors.includes(color)))&&(!rarity||row.dataset.rarity===rarity)&&(!tier||row.dataset[event+'Tier']===tier));
  rows.forEach(row=>{row.hidden=!visible.includes(row);row.querySelectorAll('[data-lr-context]').forEach(p=>p.hidden=p.dataset.lrContext!==event)});
  visible.sort((a,b)=>Number(a.dataset[event+'Order'])-Number(b.dataset[event+'Order'])||a.dataset.lrName.localeCompare(b.dataset.lrName,'it'));
  // Moving existing rows preserves the delegated card previews and details state.
  visible.forEach(row=>host.append(row));
  root.querySelector('[data-lr-count]').textContent=visible.length+' / '+rows.length+' carte · ordine editoriale '+(event==='draft'?'Draft':'Sealed');
  root.querySelector('[data-lr-empty]').hidden=visible.length!==0;
 }
 controls.forEach(el=>el.addEventListener(el.type==='search'?'input':'change',render));
 root.querySelector('[data-lr-reset]').addEventListener('click',()=>{controls.forEach(el=>el.value=el.dataset.lrFilter==='context'?root.dataset.defaultContext:'');render()});
 render();
});
