'use strict';
(() => {
 const $=id=>document.getElementById(id), E=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const F=(v,d=1)=>v==null?'N/D':Number(v).toLocaleString('it-IT',{minimumFractionDigits:d,maximumFractionDigits:d});
 const pct=v=>v==null?'N/D':F(v*100)+'%',pp=v=>v==null?'N/D':(v>0?'+':'')+F(v*100);
 const data=DRAFT_DATA.drill, cards=DRAFT_DATA.cards, guides=data.guides;
 const rarityNames={common:'Comune',uncommon:'Non comune',rare:'Rara',mythic:'Mitica'};
 const byName=new Map(cards.map(c=>[c.name,c]));let stage='early',limit=20,lastPremierPair='WU',searchTimer;
 const modes={ALL_TIME:'Premier Draft · intero formato',LAST_WEEK:'Premier Draft · ultima settimana',TradDraft:'Traditional Draft · generale',QuickDraft:'Quick Draft · generale'};
 const premier=w=>['ALL_TIME','LAST_WEEK'].includes(w);
 const state=()=>({window:$('dd-window').value,pair:$('dd-pair').value,min:+$('dd-min').value});
 const metrics=(name,w,pair='all')=>data.contexts[w+':'+pair]?.[name]||null;
 const rate=(row,i=0)=>row?.[i]??null;
 const difference=(a,b)=>a==null||b==null?null:a-b;
 const cardLink=name=>`<button class="dd-card-link" type="button" data-name="${E(name)}">${E(name)}</button>`;
 const baseline=(w,pair='all')=>{
  const rows=data.colors[w];if(!rows)return null;
  if(pair==='all'){const all=rows.find(r=>r.short_name==='All');return all?{wins:all.wins,games:all.games}:null;}
  const clean=rows.find(r=>r.short_name===pair),splash=rows.find(r=>r.short_name===pair+'+');
  return clean?{wins:clean.wins+(splash?.wins??0),games:clean.games+(splash?.games??0),clean,splash}:null;
 };
 function renderGuide(){
  const s=state(),g=guides[s.pair];
  const guideCard=name=>{const row=metrics(name,s.window,s.pair);return `<li>${cardLink(name)}<small>GIH ${pct(rate(row))} · ${F(rate(row,1),0)} osservazioni${(rate(row,1)??0)<s.min?' · sotto soglia':''}</small></li>`;};
  if(!g){$('dd-guide').innerHTML='<h3>Leggere il campione generale</h3><p>Parti da qualità autonoma e flessibilità: Mindseeker Oculus sviluppa campo e risorse in più coppie blu; Recursive Recruitment richiede invece blu e nero. Seleziona una coppia nel Premier per analizzare il piano specifico e i suoi supporti.</p>';}
  else $('dd-guide').innerHTML=`<div class="dd-guide-head"><h3>${E(g.name)} · ${E(g.theme)}</h3><p>${E(g.plan)}</p><p class="small">Selezione editoriale per ruolo e sinergia, non classifica statistica. Dati della coppia e del periodo selezionati; le carte restano visibili anche se sotto soglia.</p></div><div class="dd-guide-columns"><div><h4>Nucleo da cercare</h4><ul>${g.core.map(guideCard).join('')}</ul></div><div><h4>Supporti e ruoli complementari</h4><ul>${g.support.map(guideCard).join('')}</ul></div></div><p class="notice"><strong>Errore da evitare:</strong> ${E(g.risk)}</p>`;
  document.querySelectorAll('[data-dd-stage]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.ddStage===stage)));
  const generic={early:'Nei primi pick privilegia qualità autonoma e flessibilità: Mindseeker Oculus può andare in blu/bianco o blu/nero, Craftwork Crusher impegna rosso e verde. Non confondere una preferenza per un colore con un segnale che quel colore sia aperto.',middle:'Leggi una sequenza coerente: Mindseeker Oculus, Countersculpt e Surveillance Phantasm ricevuti dopo diversi pick sono più informativi di una sola Codie, Ravenous Codex tardiva. Se hai già pescate ma pochi bloccanti, valuta Prudent Fateseer rispetto a Twinned Vision.',late:'Completa i ruoli: Surveillance Phantasm per il turno due, Your Fate Ends Here per rimuovere minacce con valore di mana almeno tre, Fatehold Annex per il mana bianco/blu. Nel BO3 Budding Insurgent contro Way of the Healer viene normalmente prima di una bomba fuori colore presa solo per negarla.'};
  $('dd-stage').innerHTML=`<p><strong>Priorità strategica:</strong> ${E(g?g[stage]:generic[stage])}</p>${g?`<p><strong>Esempio di scelta:</strong> ${E(g.example)}</p>`:''}<p class="small">Queste indicazioni dipendono dal pool. I dati aggregati non contengono la busta attuale e non identificano il pick ottimale in ogni situazione.</p>`;
 }
 function renderSummary(){
  const s=state(),b=baseline(s.window,s.pair),all=baseline(s.window);
  $('dd-summary').innerHTML=b?`<p><strong>${E(guides[s.pair]?.name||'Tutti i mazzi')}: WR dei mazzi ${pct(b.wins/b.games)}</strong> su ${F(b.games,0)} partite. WR di tutti i mazzi della modalità e finestra, inclusi monocolore e tre o più colori: ${all?pct(all.wins/all.games):'N/D'}.</p>${b.clean?`<p class="small">Base a due colori senza splash: ${pct(b.clean.wins/b.clean.games)} (${F(b.clean.games,0)} partite). Con splash: ${b.splash?pct(b.splash.wins/b.splash.games)+' ('+F(b.splash.games,0)+')':'N/D'}. Le statistiche delle carte qui sotto includono entrambi i gruppi.</p>`:''}<p class="small">Il WR dei mazzi e il GIH delle carte hanno denominatori diversi. Una coppia forte può alzare il GIH di molte sue carte: lo scarto dal GIH generale non misura il vantaggio prodotto dalla sinergia.</p>`:'<p>Dati del campione non disponibili.</p>';
 }
 function renderRows(){
  const s=state(),query=$('dd-search').value.trim().toLowerCase(),rarity=$('dd-rarity').value;
  $('dd-rows').dataset.query=query;
  const eligible=cards.filter(c=>(!query||c.name.toLowerCase().includes(query))&&(!rarity||(rarity==='cu'?['common','uncommon'].includes(c.rarity):c.rarity===rarity))&&($('dd-lands').checked||!c.type.includes('Land'))&&(!$('dd-compatible').checked||s.pair==='all'||c.playable.includes(s.pair)));
  const pickRange=$('dd-picks').value;
  const rows=eligible.map(c=>({c,m:metrics(c.name,s.window,s.pair),general:metrics(c.name,s.window)})).filter(r=>(r.m?.[1]??0)>=s.min&&(pickRange==='all'||rate(r.general,7)!=null&&(pickRange==='early'?rate(r.general,7)<=5:rate(r.general,7)>5)));
  const lowest=rows.filter(r=>rate(r.m)!=null).sort((a,b)=>rate(a.m)-rate(b.m)||a.c.name.localeCompare(b.c.name)).slice(0,6);
  $('dd-lowest').innerHTML=lowest.length?lowest.map(({c,m,general})=>`<article><h4>${cardLink(c.name)}</h4><p><strong>GIH ${pct(rate(m))}</strong> · ${F(rate(m,1),0)} osservazioni<br>Generale ${pct(rate(general))}${s.pair==='all'?'':` · scarto grezzo ${pp(difference(rate(m),rate(general)))} pp`}<br><strong>ATA globale ${F(rate(general,7))}</strong> · ALSA globale ${F(rate(general,6))}<br>${rate(general,7)==null?'Posizione media N/D':rate(general,7)<=5?'Scelta mediamente entro il pick 5':'Scelta mediamente dopo il pick 5'} · ${E(rarityNames[c.rarity]||c.rarity)}</p></article>`).join(''):'<p>Nessun win rate pubblicato soddisfa i filtri selezionati.</p>';
  const get=(r,key)=>key.startsWith('delta')?difference(rate(r.m),rate(r.general)):key==='alsa'?rate(r.general,6):key==='iwd'?rate(r.m,8):rate(r.m);
  const sort=$('dd-sort').value,ascending=sort.endsWith('-low');
  rows.sort((a,b)=>{
   if(sort==='name')return a.c.name.localeCompare(b.c.name);
   const av=get(a,sort),bv=get(b,sort);
   if(av==null||bv==null)return av==null&&bv==null?a.c.name.localeCompare(b.c.name):av==null?1:-1;
   return (ascending?av-bv:bv-av)||a.c.name.localeCompare(b.c.name);
  });
  $('dd-rows').innerHTML=rows.length?rows.slice(0,limit).map(({c,m,general})=>`<tr><td>${cardLink(c.name)}<small>${E(c.set)} · ${E(rarityNames[c.rarity]||c.rarity)}${s.pair!=='all'&&!c.playable.includes(s.pair)?' · costo fuori colori':''}</small></td><td>${E(c.cost)||'N/D'}</td><td>${pct(rate(m))}</td><td>${F(rate(m,1),0)}</td><td>${pct(rate(general))}</td><td>${s.pair==='all'?'Non applicabile':pp(difference(rate(m),rate(general)))}</td><td>${pp(rate(m,8))}</td><td>${F(rate(general,6))}</td><td>${F(rate(general,7))}</td></tr>`).join(''):'<tr><td colspan="9">Nessuna carta soddisfa i filtri. Abbassa il campione minimo o modifica la selezione.</td></tr>';
  $('dd-count').textContent=Math.min(rows.length,limit)+' di '+rows.length+' carte mostrate. '+(s.pair==='all'?'Campione generale.':'Contesto con colori principali '+s.pair+', inclusi gli splash.')+(pickRange==='all'?'':' Filtro ATA globale '+(pickRange==='early'?'≤ 5.':'> 5.'))+(ascending?' Ordine crescente: i valori N/D restano in fondo.':'');
  $('dd-more').hidden=rows.length<=limit;
  const date=new Date(data.retrieved).toLocaleString('it-IT',{timeZone:'Europe/Rome'});
  const source=new URL('https://www.17lands.com/card_data');source.searchParams.set('expansion','FRA');source.searchParams.set('format',premier(s.window)?'PremierDraft':s.window);source.searchParams.set('time_period',premier(s.window)?s.window:'ALL_TIME');if(s.pair!=='all')source.searchParams.set('color',s.pair);
  $('dd-source').innerHTML=`Fonte: <a href="${E(source.href)}" target="_blank" rel="noopener">17Lands con modalità, periodo e colori selezionati</a>. Rilevazione ${E(date)} (Europe/Rome). ${E(modes[s.window])}. La pagina esterna mostra dati aggiornati, non necessariamente identici allo snapshot. Campioni scarsi non equivalgono a carte deboli.`;
 }
 function renderComparison(){
  const s=state(),names=[$('dd-card-a').value,$('dd-card-b').value];
  const list=names.map(name=>({c:byName.get(name),m:metrics(name,s.window,s.pair),g:metrics(name,s.window)}));
  const cells=fn=>list.map(x=>'<td>'+fn(x)+'</td>').join('');
  $('dd-comparison').innerHTML=`<table><thead><tr><th scope="col">Metrica</th>${cells(x=>cardLink(x.c.name))}</tr></thead><tbody><tr><th scope="row">Costo principale</th>${cells(x=>E(x.c.cost))}</tr><tr><th scope="row">Costo nei due colori</th>${cells(x=>s.pair==='all'?'Scegli un archetipo':x.c.playable.includes(s.pair)?'Compatibile con i simboli':'Servono altre fonti')}</tr><tr><th scope="row">GIH nel contesto</th>${cells(x=>pct(rate(x.m)))}</tr><tr><th scope="row">Osservazioni GIH</th>${cells(x=>F(rate(x.m,1),0))}</tr><tr><th scope="row">GIH generale</th>${cells(x=>pct(rate(x.g)))}</tr><tr><th scope="row">IWD descrittivo in pp</th>${cells(x=>pp(rate(x.m,8)))}</tr><tr><th scope="row">ALSA globale</th>${cells(x=>F(rate(x.g,6)))}</tr><tr><th scope="row">Campione minimo selezionato</th>${cells(x=>(rate(x.m,1)??0)>=s.min?'Soglia raggiunta':'Sotto soglia: prudenza')}</tr></tbody></table>`;
 }
 function renderFindings(){
  const examples=[{name:'Way of the Healer',pair:'WU',text:'Il risultato di bianco blu è un motivo per approfondire il pacchetto surveil e pedine. Non prova che aggiungere la carta a qualunque mazzo produca lo stesso miglioramento.'},{name:'Command the Stage',pair:'BR',text:'Migliorare rispetto al dato generale non basta: considera anche il rendimento assoluto, il piano del mazzo e il costo dei supporti.'},{name:'Twinned Vision',pair:'UR',text:'La carta è ibrida e non obbliga a Izzet. Il confronto per archetipo va letto insieme ai simboli del costo, non soltanto al colore stampato.'}];
  $('dd-findings').innerHTML=examples.map(e=>{const m=metrics(e.name,'ALL_TIME',e.pair),g=metrics(e.name,'ALL_TIME');return `<article><h4>${cardLink(e.name)}</h4><p>Generale ${pct(rate(g))}; ${E(guides[e.pair].name)} ${pct(rate(m))}, ${F(rate(m,1),0)} osservazioni GIH. Scarto grezzo ${pp(difference(rate(m),rate(g)))} pp.</p><p>${E(e.text)}</p></article>`}).join('');
 }
 function detail(name){
  const s=state(),m=metrics(name,s.window,s.pair),g=metrics(name,s.window);
  let content=`<section class="dd-card-detail"><h3>Drilldown della carta</h3><p>${E(modes[s.window])}, ${E(guides[s.pair]?.name||'tutti i mazzi')}. GIH ${pct(rate(m))} (${F(rate(m,1),0)} osservazioni); generale ${pct(rate(g))}.</p><div class="tablewrap"><table><thead><tr><th>Quando viene vista</th><th>Vittorie</th><th>Osservazioni</th></tr></thead><tbody><tr><td>Mano iniziale</td><td>${pct(rate(m,2))}</td><td>${F(rate(m,3),0)}</td></tr><tr><td>Pescata durante la partita</td><td>${pct(rate(m,4))}</td><td>${F(rate(m,5),0)}</td></tr><tr><td>Mai vista in mano</td><td>${pct(rate(m,9))}</td><td>${F(rate(m,10),0)}</td></tr></tbody></table></div><p class="small">Sono gruppi osservativi differenti: le percentuali non misurano quanto sia conveniente tenere la carta in mano iniziale o pescarla tardi.</p>`;
  if(premier(s.window)){
   content+='<h4>La stessa carta nelle dieci coppie</h4><div class="tablewrap"><table><thead><tr><th>Contesto con splash</th><th>GIH WR</th><th>Campione GIH</th><th>Scarto grezzo dal generale</th><th>Costo principale</th></tr></thead><tbody>'+Object.entries(guides).map(([pair,guide])=>{const row=metrics(name,s.window,pair),c=byName.get(name);return `<tr${pair===s.pair?' class="dd-selected-row"':''}><td>${E(guide.name)}</td><td>${pct(rate(row))}</td><td>${F(rate(row,1),0)}${(rate(row,1)??0)<s.min?' · sotto soglia':''}</td><td>${pp(difference(rate(row),rate(g)))} pp</td><td>${c.playable.includes(pair)?'Nei due colori':'Altre fonti'}</td></tr>`}).join('')+'</tbody></table></div><p class="small">La presenza di una carta fuori colori nel campione non suggerisce di splasherla: i mazzi possono includere fonti aggiuntive.</p>';
  }
  return content+'</section>';
 }
 function render(){
  const general=$('dd-pair').value==='all';
  for(const option of $('dd-sort').options)if(option.value.startsWith('delta'))option.disabled=general;
  if(general&&$('dd-sort').value.startsWith('delta'))$('dd-sort').value='gih';
  renderSummary();renderGuide();renderRows();renderComparison();
 }
 for(const id of ['dd-window','dd-pair','dd-min','dd-rarity','dd-search','dd-sort','dd-compatible','dd-lands','dd-picks'])$(id).addEventListener(id==='dd-search'?'input':'change',()=>{
  if(id==='dd-window'){const disabled=!premier($('dd-window').value);if(disabled&&!$('dd-pair').disabled)lastPremierPair=$('dd-pair').value;if(!disabled&&$('dd-pair').disabled)$('dd-pair').value=lastPremierPair;$('dd-pair').disabled=disabled;if(disabled)$('dd-pair').value='all';}
  clearTimeout(searchTimer);limit=20;
  if(id==='dd-search')searchTimer=setTimeout(renderRows,180);else render();
 });
 document.querySelectorAll('[data-dd-stage]').forEach(b=>b.addEventListener('click',()=>{stage=b.dataset.ddStage;renderGuide();}));
 const options=[...cards].sort((a,b)=>a.name.localeCompare(b.name)).map(c=>`<option value="${E(c.name)}">${E(c.name)}</option>`).join('');
 $('dd-card-a').innerHTML=options;$('dd-card-b').innerHTML=options;$('dd-card-a').value='Mindseeker Oculus';$('dd-card-b').value='Countersculpt';
 for(const id of ['dd-card-a','dd-card-b'])$(id).addEventListener('change',renderComparison);
 $('dd-more').addEventListener('click',()=>{limit+=20;renderRows();});
 $('dd-low').addEventListener('click',()=>{$('dd-sort').value='gih-low';limit=20;renderRows();$('dd-rows').closest('.tablewrap').scrollIntoView({behavior:'smooth',block:'start'});});
 $('dd-low-early').addEventListener('click',()=>{$('dd-picks').value='early';$('dd-sort').value='gih-low';limit=20;renderRows();});
 window.DraftDrilldown={detail,state};render();renderFindings();
})();
