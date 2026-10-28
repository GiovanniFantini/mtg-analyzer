'use strict';
// Measures from dated tournament lists. Scores are observed shares, never forecasts.
window.TournamentProspects=(()=>{
 const formats={standard:'Standard',pioneer:'Pioneer',modern:'Modern',pauper:'Pauper'};
 const labels={repeated:'Uso ripetuto',first_sightings:'Prime presenze',not_observed:'Non osservata nel campione',unavailable:'Dati insufficienti'};
 const trends={rising:'In crescita nel campione',falling:'In calo nel campione',stable:'Stabile nel campione',insufficient_data:'Confronto temporale insufficiente'};
 const outlooks={watch:'Da osservare',repeated_use:'Uso ripetuto documentato',no_signal:'Nessun segnale osservato',not_assessed:'Potenziale futuro non valutato'};
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const num=n=>n==null?'N/D':n.toLocaleString('it-IT',{maximumFractionDigits:2});
 const safeURL=url=>typeof url==='string'&&/^https:\/\//.test(url)?esc(url):'';
 function get(card,f){return card?.prospects?.formats?.[f]?.tournamentIndex}
 function assessment(card,f){const t=get(card,f);if(!t)return null;
  const legality=card.legalities?.[f]||t.legality||'unknown',notLegal=['not_legal','banned'].includes(legality);
  const rank=notLegal?null:Number.isFinite(t.score)?t.score:null;
  const state=notLegal?'not_legal':t.reason==='basic_land'?'not_applicable':rank===0?'not_observed':rank!=null?'documented':card.prospects?.formats?.[f]?.prospect==='anteprima_da_testare'?'unverified':'missing';
  const label=notLegal?(legality==='banned'?'Vietata':'Non legale'):t.reason==='basic_land'?'Terra base':t.reason==='no_post_release_sample'?'Campione dopo l’uscita non verificato':rank>0&&t.trend?.status==='rising'?'In crescita':labels[t.status]||'Dati insufficienti';
  return {legality,rank,state,label,date:t.date,tournament:t,assessment:card.prospects.formats[f]};
 }
 function compact(card,f){const a=assessment(card,f);if(!a)return '';const t=a.tournament,o=t.observed;
  return `${a.rank==null?'':`<span class="tournament-score">${num(a.rank)} / 100</span>`}${esc(a.label)}${a.rank!=null?`<small>${num(o.withCard)} / ${num(t.sample.decks)} liste · ${num(o.eventsWithCard)} eventi</small>`:''}<small>${esc(t.date)}</small>`;
 }
 function details(card){const indices=Object.entries(formats).filter(([f])=>get(card,f));if(!indices.length)return '';
  return `<section class="tournament-prospects"><h5>Indice dai tornei, formato per formato</h5><p>Indice 0–100 = percentuale delle liste pubblicate nel campione che contengono la carta, nel main deck o nel sideboard. Non misura la probabilità di vittoria o il potenziale futuro. Lo zero significa non osservata in questo campione.</p>${indices.map(([f,label])=>{const a=assessment(card,f),t=a.tournament,o=t.observed,h=t.history,tr=t.trend;
   const examples=(items,heading)=>items?.length?`<h6>${heading}</h6><ul>${items.map(e=>`<li>${safeURL(e.url)?`<a href="${safeURL(e.url)}" target="_blank" rel="noopener">${esc(e.event)} · ${esc(e.player)}</a>`:esc(e.event)} · ${esc(e.date)}${e.rank!=null?' · posto '+num(e.rank):''}${e.archetype?' · '+esc(e.archetype):''} · main ${num(e.main)}, sideboard ${num(e.sideboard)}</li>`).join('')}</ul>`:'';
   return `<details class="tournament-format" data-tournament-format="${f}"><summary>${label}: ${a.rank==null?'N/D':num(a.rank)+' / 100'} · ${esc(a.label)}</summary><p>Campione dal ${esc(t.sample.start)} al ${esc(t.sample.end)}: ${num(t.sample.decks)} liste ammissibili, ${num(t.sample.events)} eventi. Consultazione: ${esc(t.date)}.</p><p>Presenze: ${num(o.withCard)} liste; main deck ${num(o.mainDecks)}, sideboard ${num(o.sideboardDecks)}. Una lista con la carta in entrambe le sezioni conta una volta nell’indice. Copie totali: main ${num(o.mainCopies)}, sideboard ${num(o.sideboardCopies)}.</p><p>Risultati dei mazzi che la contengono: ${num(o.top8Lists)} Top 8 e ${num(o.winningLists)} vittorie di evento con piazzamento documentato. Non attribuiamo questi risultati alla singola carta.</p><p>${esc(trends[tr.status]||'Confronto non disponibile')}${tr.deltaPoints!=null?`: ${num(tr.deltaPoints)} punti percentuali fra 1–14 e 15–28 ottobre` :''}. Prime due settimane: ${num(tr.previous.withCard)} / ${num(tr.previous.decks)} liste. Ultime due: ${num(tr.recent.withCard)} / ${num(tr.recent.decks)}.</p><p>Segnale da seguire: ${esc(outlooks[t.outlook.status]||'Non valutato')}. È una lettura delle osservazioni disponibili, senza previsione numerica di successo.</p>${examples(t.examples,'Esempi verificabili nel campione recente')}${h.decks?`<p>Storico separato, antecedente alla finestra recente: ${num(h.withCard)} / ${num(h.decks)} liste in ${num(h.events)} eventi con presenza. I Pro Tour storici non entrano nell’indice recente.</p>${examples(t.historicalExamples,'Esempi storici e Pro Tour')}`:''}<p class="prospect-note">Le liste pubblicate possono coprire soltanto una parte dei partecipanti. Le ristampe condividono l’identità di gioco; i tornei anteriori alla prima uscita o traccia documentata non diventano assenze. Le terre base e le carte non legali hanno indice N/D.</p></details>`;
  }).join('')}</section>`;
 }
 return {formats,get,assessment,compact,details,num,labels,trends,outlooks};
})();
