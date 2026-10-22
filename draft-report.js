'use strict';
const q=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=(v,d=1)=>v==null?'N/D':Number(v).toLocaleString('it-IT',{minimumFractionDigits:d,maximumFractionDigits:d});
const rarities={common:'Comune',uncommon:'Non comune',rare:'Rara',mythic:'Mitica'};
function renderCards(){
 if(!q('draft-search'))return;
 const search=q('draft-search').value.trim().toLowerCase(),color=q('draft-color').value,rarity=q('draft-rarity').value;
 const rows=DRAFT_DATA.cards.filter(c=>(!search||c.name.toLowerCase().includes(search))&&(!color||(color==='C'?!c.color:c.color.includes(color)))&&(!rarity||c.rarity===rarity)&&(!q('draft-sample').checked||c.n>=2000));
 const sort=q('draft-sort').value;
 rows.sort((a,b)=>sort==='name'?a.name.localeCompare(b.name):sort==='gih-low'?(a.gih==null?(b.gih==null?0:1):b.gih==null?-1:a.gih-b.gih):sort==='alsa'?(b.alsa??-1)-(a.alsa??-1):sort==='n'?b.n-a.n:(b.gih??-1)-(a.gih??-1));
 q('draft-count').textContent=rows.length+' carte mostrate su '+DRAFT_DATA.cards.length+'.';
 q('draft-rows').innerHTML=rows.length?rows.map(c=>`<tr><td><button type="button" data-name="${esc(c.name)}">${esc(c.name)}</button><small>${esc(c.set)}</small></td><td>${esc(c.color||'C')}</td><td>${esc(rarities[c.rarity]||c.rarity)}</td><td>${c.gih==null?'N/D':fmt(c.gih*100)+'%'}</td><td>${fmt(c.n,0)}</td><td>${fmt(c.alsa)}</td></tr>`).join(''):'<tr><td colspan="6">Nessuna carta. Rimuovi un filtro o azzera la ricerca.</td></tr>';
}
function drawColors(){
 if(!q('archetype-chart')||!DRAFT_DATA.pairs?.length||DRAFT_DATA.baseline==null)return;
 const pairs=[...DRAFT_DATA.pairs].sort((a,b)=>b.wins/b.games-a.wins/a.games),avg=DRAFT_DATA.baseline*100;
 const extent=Math.ceil(Math.max(...pairs.map(c=>Math.abs(c.wins/c.games*100-avg)))*2)/2;
 q('archetype-chart').innerHTML='<h3>Scarto dalla media dei mazzi a due colori</h3><p>Zero = '+fmt(avg)+'% di vittorie. Barre in punti percentuali; splash inclusi.</p>'+pairs.map(c=>{const rate=c.wins/c.games*100,d=rate-avg;return `<div class="chart-row"><span class="chart-name">${esc(c.name)}</span><div class="chart-track" role="img" aria-label="${esc(c.name)}: ${fmt(rate)}%, scarto ${fmt(d)} punti"><span class="chart-fill" style="left:${d>=0?50:50+d/extent*50}%;width:${Math.abs(d)/extent*50}%;opacity:${d>=0?1:.5}"></span></div><span class="chart-value">${fmt(rate)}% (${d>=0?'+':''}${fmt(d)})</span></div>`}).join('')+`<div class="chart-axis"><span>−${fmt(extent)} pp</span><span>0</span><span>+${fmt(extent)} pp</span></div>`;
}
function showCard(name){
 const c=DRAFT_DATA.cards.find(c=>c.name===name)||(DRAFT_DATA.poolCards||[]).find(c=>c.name===name);if(!c)return;
 const oracle=c.faces?.length?c.faces.map(f=>f.name+' '+f.mana_cost+'\n'+f.oracle_text).join('\n\n'):c.oracle;
 q('draft-detail').innerHTML=`<h2 id="draft-card-title">${esc(c.name)}</h2><div class="detail-grid"><img src="${esc(c.image)}" alt="${esc(c.name)}"><div><p><strong>GIH WR ${c.gih==null?'N/D':fmt(c.gih*100)+'%'}</strong><br>${fmt(c.n,0)} osservazioni GIH · ALSA ${fmt(c.alsa)}</p><p class="oracle">${esc((oracle||'Consulta il testo aggiornato su Scryfall.').replace(/\u2014/g, ':'))}</p><p><a href="${esc(c.url)}" target="_blank" rel="noopener">Oracle e immagine su Scryfall ↗</a></p><p>Premier Draft · ${esc(DRAFT_DATA.date)}</p></div></div>`;
 if(window.DraftDrilldown)q('draft-detail').insertAdjacentHTML('beforeend',window.DraftDrilldown.detail(name));
 q('draft-dialog').showModal();
}
for(const id of ['draft-search','draft-color','draft-rarity','draft-sort','draft-sample'])q(id)?.addEventListener(id==='draft-search'?'input':'change',renderCards);
q('draft-reset')?.addEventListener('click',()=>{q('draft-search').value='';q('draft-color').value='';q('draft-rarity').value='';q('draft-sort').value='gih';q('draft-sample').checked=true;renderCards()});
q('draft-close').addEventListener('click',()=>q('draft-dialog').close());
document.addEventListener('click',e=>{const b=e.target.closest('[data-name]');if(b)showCard(b.dataset.name)});
drawColors();renderCards();
