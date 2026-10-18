'use strict';
(()=>{
 const $=id=>document.getElementById(id), formats=['Tutti','Commander','Pioneer','Modern','Pauper','Legacy'];
 const key='mtg-fra-discovery-watch-v1', levels={Confermata:0,Emergente:1,Preliminare:2};
 const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let watched=new Set(),format='Tutti',storage=true;
 try{const saved=JSON.parse(localStorage.getItem(key)||'[]');if(Array.isArray(saved))watched=new Set(saved.filter(x=>typeof x==='string'));}catch{storage=false}
 function storageNote(){ $('storage-status').textContent=storage?'':'Salvataggio nel browser non disponibile: le osservate restano attive solo finché questa pagina è aperta.'; }
 storageNote();
 const url=window.__portableURL||new URL(location.href), q=new URLSearchParams(url.search);
 if(window.parent!==window){try{const outer=new URL(window.parent.location.href);for(const id of ['format','level','product','sort','q'])if(outer.searchParams.has('discovery_'+id))q.set(id,outer.searchParams.get('discovery_'+id));}catch{}}
 if(formats.includes(q.get('format')))format=q.get('format');
 for(const id of ['level','product','sort']){const value=q.get(id);if([...$(id).options].some(o=>o.value===value))$(id).value=value;}
 $('search').value=q.get('q')||'';
 function filterURL(){const u=new URL(url.href);u.search='';if(format!=='Tutti')u.searchParams.set('format',format);for(const id of ['level','product'])if($(id).value)u.searchParams.set(id,$(id).value);if($('sort').value!=='signal')u.searchParams.set('sort',$('sort').value);if($('search').value.trim())u.searchParams.set('q',$('search').value.trim());return u;}
 function render(){
  $('formats').innerHTML=formats.map(f=>`<button type="button" data-format="${f}" aria-pressed="${f===format}">${f}</button>`).join('');
  const search=$('search').value.trim().toLocaleLowerCase('it');
  let cards=DISCOVERY.cards.filter(c=>(format==='Tutti'||c.formats.some(f=>f===format||format==='Commander'&&f.startsWith('Commander')))&&(!$('level').value||c.level===$('level').value)&&(!$('product').value||c.product===$('product').value)&&(!$('saved').checked||watched.has(c.name))&&(!search||[c.name,c.role,c.verdict,c.line,c.evidence,c.limit].join(' ').toLocaleLowerCase('it').includes(search)));
  cards.sort((a,b)=>$('sort').value==='name'?a.name.localeCompare(b.name):levels[a.level]-levels[b.level]||DISCOVERY.cards.indexOf(a)-DISCOVERY.cards.indexOf(b));
  $('count').textContent=`${cards.length} di ${DISCOVERY.cards.length} carte · ${watched.size} osservate`;
  $('results').innerHTML=cards.length?cards.map(c=>`<article class="candidate"><div class="candidate-top"><img src="${esc(c.image)}" alt="${esc(c.name)}" loading="lazy" width="96" height="134"><div><span class="badge ${['confirmed','emerging','early'][levels[c.level]]}">${c.level}</span><h3>${esc(c.name)}</h3><div class="meta">${esc(c.formats.join(' · '))} · ${c.product} · ${esc(c.role)}</div></div></div><p class="verdict">${esc(c.verdict)}</p><p class="evidence"><strong>Il segnale.</strong> ${esc(c.evidence)}</p><details><summary>Perché funziona e cosa può limitarla</summary><p><strong>Linea di gioco.</strong> ${esc(c.line)}</p><p><strong>Il limite.</strong> ${esc(c.limit)}</p></details><div class="sources">${c.sources.map(([label,link])=>`<a href="${esc(link)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`).join('')}</div><button class="save" type="button" data-save="${esc(c.name)}" aria-pressed="${watched.has(c.name)}">${watched.has(c.name)?'Osservata · rimuovi':'Aggiungi alle osservate'}</button></article>`).join(''):'<div class="empty"><h3>Nessuna carta con questi filtri</h3><p>Prova un altro formato, allarga il segnale o azzera i filtri.</p><button type="button" data-reset>Azzera filtri</button></div>';
 }
 function reset(){format='Tutti';$('search').value='';$('level').value='';$('product').value='';$('sort').value='signal';$('saved').checked=false;render()}
 $('formats').addEventListener('click',e=>{const b=e.target.closest('[data-format]');if(!b)return;format=b.dataset.format;render();$('formats').querySelector(`[data-format="${format}"]`).focus()});
 for(const id of ['level','product','sort','saved'])$(id).addEventListener('change',render);
 $('search').addEventListener('input',render);$('reset').onclick=reset;
 $('results').addEventListener('click',e=>{if(e.target.closest('[data-reset]'))return reset();const b=e.target.closest('[data-save]');if(!b)return;const n=b.dataset.save;watched.has(n)?watched.delete(n):watched.add(n);try{localStorage.setItem(key,JSON.stringify([...watched]))}catch{storage=false;storageNote()}render();const replacement=[...document.querySelectorAll('[data-save]')].find(x=>x.dataset.save===n);(replacement||$('saved')).focus()});
 $('copy').onclick=async()=>{let u=filterURL();if(window.parent!==window){try{const outer=new URL(window.parent.location.href);outer.hash='discovery';for(const id of ['format','level','product','sort','q'])outer.searchParams.delete('discovery_'+id);for(const [k,v]of u.searchParams)outer.searchParams.set('discovery_'+k,v);u=outer;}catch{}}try{await navigator.clipboard.writeText(u.href);$('share-status').textContent='Link copiato. Le osservate restano personali.'}catch{$('share-status').textContent='Copia questo link:';const input=document.createElement('input');input.value=u.href;input.setAttribute('aria-label','Link ai filtri');$('share-status').append(input);input.focus();input.select()}};
 render();
})();
