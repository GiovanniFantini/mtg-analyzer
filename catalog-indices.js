'use strict';
// Observed results and attributed format assessments; no inferred WR or scores.
window.CatalogIndices={create(DATA){
 const $=id=>document.getElementById(id),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const formats={standard:'Standard',pioneer:'Pioneer',modern:'Modern',pauper:'Pauper'};
 const labels={adozione_ripetuta:'Adozione ripetuta',adozione_documentata:'Adozione documentata',prime_presenze:'Prime presenze',anteprima_da_testare:'Anteprima da testare',da_verificare:'Da verificare',non_applicabile:'Non applicabile'};
 const snapshots={draft:DATA.catalogPerformance?.draft||[],sealed:DATA.catalogPerformance?.sealed||[]};
 if(!snapshots.draft.length&&Object.keys(DATA.catalogWinRates?.cards||{}).length)snapshots.draft=[{id:'untapped',metric:'WR in mano',...DATA.catalogWinRates}];
 let refresh=()=>{};
 const ids=['draft-wr-source','sealed-wr-source','sealed-wr-min','sealed-wr-max','sealed-wr-data','draft-wr-games','sealed-wr-games','prospect-format','prospect-state','prospect-legality'];
 function source(kind){return snapshots[kind].find(s=>s.id===$(kind+'-wr-source')?.value)||snapshots[kind][0]}
 function rate(c,kind='draft'){const v=source(kind)?.cards[c.id]?.value;return Number.isFinite(v)?v:null}
 function assessment(c,format){
  const a=c.prospects?.formats?.[format],legality=c.legalities?.[format]||a?.legality||'unknown';
  if(['not_legal','banned'].includes(legality))return {legality,state:'not_legal',label:legality==='banned'?'Vietata':'Non legale',rank:null};
  const documented=a&&a.evidence&&!['non_documentata','non_verificata','non_legale'].includes(a.evidence);
  const rank=documented?({adozione_ripetuta:3,adozione_documentata:2,prime_presenze:1}[a.prospect]??null):null;
  return {legality,state:rank!=null?'documented':a?'unverified':'missing',label:a?(labels[a.prospect]||'Da verificare'):'Prospettiva N/D',rank,date:a?c.prospects?.date:null,evidence:a?.evidence,assessment:a};
 }
 function matches(c){
  for(const kind of ['draft','sealed']){
   const prefix=kind==='draft'?'wr':'sealed-wr',v=rate(c,kind),min=$(prefix+'-min')?.value||'',max=$(prefix+'-max')?.value||'',coverage=$(prefix+'-data')?.value||'',games=$(kind+'-wr-games')?.value||'';
   if((min!==''||max!=='')&&(v==null||min!==''&&v<Number(min)||max!==''&&v>Number(max)))return false;
   if(coverage&&(coverage==='present'?v==null:v!=null))return false;
   if(games!==''&&(source(kind)?.cards[c.id]?.games==null||source(kind).cards[c.id].games<Number(games)))return false;
  }
  const f=$('prospect-format')?.value;if(!f)return true;
  const a=assessment(c,f),state=$('prospect-state').value,legal=$('prospect-legality').value;
  return (!state||a.state===state)&&(!legal||(legal==='legal'?['legal','restricted'].includes(a.legality):legal==='unknown'?a.legality==='unknown':['not_legal','banned'].includes(a.legality)));
 }
 function rank(c,order){return assessment(c,order.replace('prospect-','').replace('-asc','')).rank}
 function rateHTML(c,compact=false){return '<div class="catalog-performance">'+['draft','sealed'].map(kind=>{
  const s=source(kind),v=rate(c,kind),r=s?.cards[c.id],title=kind==='draft'?'WR Draft':'WR Sealed';
  const value=v==null?'N/D':v.toLocaleString('it-IT',{maximumFractionDigits:1})+'%';
  const details=s?`${s.provider} · ${s.filters?.event||kind} · ${s.retrieved}`:'Nessun campione integrato';
  const n=r?.games!=null?` · ${s?.derivation?'n=':'partite riportate: '}${r.games.toLocaleString('it-IT')}${s?.derivation&&r.games<100?' (campione ridotto)':''}`:'';
  return `<p class="untapped-wr catalog-rate" data-wr-kind="${kind}"><span>${title}: ${value}</span><small>${esc(details)}${n}</small>${compact?'<small>In mano iniziale o pescata</small>':''}${!compact&&s?`<small>${esc(s.metric||'WR in mano')} · ${esc(s.filters?.period||'Periodo non indicato')} · ${esc(s.filters?.ranks||s.filters?.rankMin||'Ranghi non indicati')} · ${esc(s.filters?.archetype||'Archetipo non indicato')}</small>${!s.derivation?'<small>I conteggi riportati dalla fonte non sono un denominatore esatto documentato della WR.</small>':''}<a href="${esc(r?.url||s.url||'https://www.17lands.com/public_datasets')}" target="_blank" rel="noopener">Fonte e metodo</a>`:''}</p>`;
 }).join('')+'</div>'}
 function prospectHTML(c){return `<dl class="catalog-prospect-indices">${Object.entries(formats).map(([f,label])=>{const a=assessment(c,f);return `<div><dt>${label}</dt><dd>${esc(a.label)}${a.date&&a.state!=='not_legal'?`<small>${esc(a.date)}</small>`:''}</dd></div>`}).join('')}</dl>`}
 function mount(target,order){
  const filters=target.querySelector('.catalog-extra-filters');
  $('wr-filters').querySelector('legend').textContent='WR Draft, % (in mano)';
  const sourceSelect=kind=>`<label>Fonte ed evento<select id="${kind}-wr-source" data-filter-source="true">${snapshots[kind].map(s=>`<option value="${esc(s.id)}">${esc(s.provider)} · ${esc(s.filters?.event||kind)}</option>`).join('')||'<option value="">Dati assenti</option>'}</select></label>`;
  $('wr-filters').insertAdjacentHTML('afterbegin',sourceSelect('draft'));
  $('wr-filters').insertAdjacentHTML('beforeend','<label>Campione minimo<input id="draft-wr-games" type="number" min="0" step="1" placeholder="Qualsiasi"></label><p id="draft-wr-coverage" class="catalog-data-status"></p>');
  filters.insertAdjacentHTML('beforeend',`<fieldset id="sealed-wr-filters"><legend>WR Sealed, % (in mano)</legend>${sourceSelect('sealed')}<label>Minima<input id="sealed-wr-min" type="number" min="0" max="100" step="0.1" placeholder="Qualsiasi"></label><label>Massima<input id="sealed-wr-max" type="number" min="0" max="100" step="0.1" placeholder="Qualsiasi"></label><label>Copertura<select id="sealed-wr-data"><option value="">Tutte</option><option value="present">Con WR</option><option value="missing">Senza WR</option></select></label><label>Campione minimo<input id="sealed-wr-games" type="number" min="0" step="1" placeholder="Qualsiasi"></label><p id="sealed-wr-coverage" class="catalog-data-status"></p></fieldset><fieldset id="prospect-filters"><legend>Prospettive nei formati</legend><label>Formato<select id="prospect-format"><option value="">Tutti i formati</option>${Object.entries(formats).map(([f,label])=>`<option value="${f}">${label}</option>`).join('')}</select></label><label>Prospettiva<select id="prospect-state"><option value="">Tutte</option><option value="documented">Adozione documentata</option><option value="unverified">Da verificare / anteprima</option><option value="missing">Prospettiva N/D</option><option value="not_legal">Non applicabile</option></select></label><label>Legalità<select id="prospect-legality"><option value="">Tutte</option><option value="legal">Legale / limitata</option><option value="not_legal">Non legale / vietata</option><option value="unknown">Da verificare</option></select></label><p class="catalog-data-status">Ordine delle prospettive: adozione ripetuta, adozione documentata, prime presenze. Le carte senza riscontri seguono quelle documentate. La legalità da sola non è una prospettiva.</p><p id="prospect-coverage" class="catalog-data-status"></p></fieldset>`);
  for(const [value,label] of [['sealed-wr','WR Sealed ↓'],['sealed-wr-asc','WR Sealed ↑'],...Object.entries(formats).flatMap(([f,label])=>[['prospect-'+f,'Prospettiva '+label+' ↓'],['prospect-'+f+'-asc','Prospettiva '+label+' ↑']])])order.add(new Option(label,value));
  for(const value of ['wr','wr-asc'])order.querySelector(`[value="${value}"]`).textContent=value==='wr'?'WR Draft ↓':'WR Draft ↑';
  refresh=()=>{
   for(const kind of ['draft','sealed']){
    const s=source(kind),has=DATA.cards.some(c=>rate(c,kind)!=null),prefix=kind==='draft'?'wr':'sealed-wr';
    for(const suffix of ['min','max'])$(prefix+'-'+suffix).disabled=!has;
    $(kind+'-wr-games').disabled=!has;$(kind+'-wr-source').disabled=snapshots[kind].length<2;
    $(prefix+'-data').querySelector('[value="present"]').disabled=!has;
    $(kind+'-wr-coverage').textContent=s?`${DATA.cards.filter(c=>rate(c,kind)!=null).length} / ${DATA.cards.length} carte con WR. ${s.retrieved} · ${s.filters?.period||'Periodo non indicato'}.`:'WR non disponibile per questa espansione. Le recensioni non sono percentuali di vittoria.';
    for(const value of [prefix,prefix+'-asc']){const o=order.querySelector(`[value="${value}"]`);o.disabled=!has;o.hidden=false;}
   }
   const f=$('prospect-format').value;
   for(const id of ['prospect-state','prospect-legality'])$(id).disabled=!f;
   $('prospect-coverage').textContent=(f?[f]:Object.keys(formats)).map(f=>`${formats[f]}: ${DATA.cards.filter(c=>assessment(c,f).state==='documented').length} con adozione documentata, ${DATA.cards.filter(c=>assessment(c,f).state==='missing').length} senza prospettiva`).join(' · ');
  };
  for(const kind of ['draft','sealed'])$(kind+'-wr-source').addEventListener('change',refresh);
  $('prospect-format').addEventListener('change',()=>{if(!$('prospect-format').value){$('prospect-state').value='';$('prospect-legality').value='';}refresh()});
  for(const f of Object.keys(formats)){const has=DATA.cards.some(c=>assessment(c,f).rank!=null);for(const suffix of ['', '-asc']){const o=order.querySelector(`[value="prospect-${f}${suffix}"]`);o.disabled=!has;if(!has)o.textContent+=' (dati insufficienti)';}}
  refresh();
 }
 return {ids,rate,source,assessment,matches,rank,mount,rateHTML,prospectHTML,reset(){for(const id of ids){if($(id).hasAttribute('data-filter-source'))$(id).selectedIndex=0;else $(id).value='';}refresh()}};
}};
