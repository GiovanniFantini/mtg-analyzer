'use strict';
// Presentation only: these summaries never enter bot decisions or saved records.
((root)=>{
 const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const colorNames={W:'Bianco',U:'Blu',B:'Nero',R:'Rosso',G:'Verde',C:'Incolore'};
 const value=c=>Math.max(0,Number(c.mv)||0);
 const land=c=>Boolean(c.land);
 const bucket=c=>land(c)?'Terre':value(c)>=6?'6+':String(Math.floor(value(c)));
 const rarity=c=>({common:'Comune',uncommon:'Non comune',rare:'Rara',mythic:'Mitica',special:'Speciale',bonus:'Bonus'}[c.rarity]||c.rarity||'Rarità non disponibile');
 function stacks(entries,byId,{emptyText='Le carte scelte appariranno qui, impilate per costo. Curva, colori e tipi si aggiornano a ogni pick.'}={}){
  const groups=new Map(['0','1','2','3','4','5','6+','Terre'].map(k=>[k,new Map()]));
  for(const entry of entries){const card=byId[entry.id];if(!card)continue;const group=groups.get(bucket(card)),previous=group.get(entry.id)||{count:0,foil:0};group.set(entry.id,{count:previous.count+1,foil:previous.foil+(entry.foil?1:0)});}
  if(!entries.length)return `<p class="empty-pool">${esc(emptyText)}</p>`;
  return [...groups].map(([key,items])=>`<section class="mana-stack"><h4>${key==='Terre'?'Terre':`${key} mana`}<span>${[...items.values()].reduce((n,x)=>n+x.count,0)}</span></h4><div>${[...items].sort(([a],[b])=>byId[a].name.localeCompare(byId[b].name)).map(([id,{count,foil}])=>{
   const c=byId[id],colors=c.colors||[],tone=colors.length>1?'multi':colors[0]||'C';
   return `<button class="stack-card tone-${esc(tone)}" data-preview="${esc(id)}" aria-label="Anteprima ${esc(c.name)}, ${esc(rarity(c))}${count>1?`, ${count} copie`:''}${foil?`, ${foil} foil`:''}"><img src="${esc(c.image)}" alt="" loading="lazy"><span class="stack-name">${count>1?`<span class="stack-count">${count}×</span> `:''}${esc(c.name)}<span class="stack-meta">${esc(rarity(c))}${foil?` · ${foil} foil`:''}</span></span></button>`;
  }).join('')}</div></section>`).join('');
 }
 function analysis(entries,byId,{title='Le tue pick',note='Analisi del pool, comprese le carte che potresti escludere.',basics={}}={}){
  const cards=entries.map(e=>byId[e.id]).filter(Boolean),curve=Array(7).fill(0),colors=Object.fromEntries(Object.keys(colorNames).map(c=>[c,0]));
  const types={'Creature':0,'Istantanei':0,'Stregonerie':0,'Incantesimi':0,'Artefatti':0,'Terre':0,'Altro':0};
  const basicCount=Object.values(basics).reduce((n,x)=>n+x,0);
  for(const c of cards){
   if(!land(c))curve[Math.min(6,Math.floor(value(c)))]++;
   for(const color of c.colors?.length?c.colors:['C'])if(color in colors)colors[color]++;
   const type=land(c)?'Terre':c.creature?'Creature':/Instant/.test(c.type)?'Istantanei':/Sorcery/.test(c.type)?'Stregonerie':/Enchantment/.test(c.type)?'Incantesimi':/Artifact/.test(c.type)?'Artefatti':'Altro';types[type]++;
  }
  types.Terre+=basicCount;
  const max=Math.max(1,...curve),total=cards.length+basicCount;
  const bars=(values,kind)=>Object.entries(values).map(([name,n])=>`<div class="composition-row"><span>${kind==='color'?`<i class="color-dot tone-${name}"></i>${colorNames[name]}`:name}</span><div class="composition-track"><span style="width:${total?Math.min(100,n/total*100):0}%"></span></div><span>${n}</span></div>`).join('');
  return `<h3>${esc(title)}</h3><p class="analysis-total">${total} <span>carte</span></p><p class="analysis-note">${esc(note)}</p><section><h4>Curva di mana</h4><div class="mana-chart" role="img" aria-label="Curva delle magie: ${curve.map((n,i)=>`${i===6?'6 o più':i} mana: ${n}`).join(', ')}">${curve.map((n,i)=>`<div class="mana-bar"><span>${n}</span><div><i style="height:${n/max*100}%"></i></div><span>${i===6?'6+':i}</span></div>`).join('')}</div><p class="analysis-note">Valore di mana stampato, terre escluse. X vale 0.</p></section><section><h4>Tipi principali</h4>${bars(types)}<p class="analysis-note">Una categoria per carta. Le creature artefatto contano tra le creature.</p></section><section><h4>Colori delle carte</h4>${bars(colors,'color')}<p class="analysis-note">Le multicolore compaiono in più colori. Non misura le fonti di mana${basicCount?'; basi aggiunte escluse dai colori':''}.</p></section>`;
 }
 function fitStacks(container){
  if(!container.clientHeight)return;
  const max=Math.max(1,...[...container.querySelectorAll('.mana-stack')].map(n=>n.querySelectorAll('.stack-card').length));
  const available=container.clientHeight-38,row=Math.max(34,Math.min(43,Math.floor((available-38)/max)));
  container.style.setProperty('--stack-row',`${row}px`);
  container.style.setProperty('--stack-tail',`${Math.max(row,Math.min(112,available-(max-1)*row))}px`);
 }
 root.DraftVisual={stacks,analysis,fitStacks,rarity,esc};
})(globalThis);
