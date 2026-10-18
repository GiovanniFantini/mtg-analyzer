const Sentiment = (() => {
  const e = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const labels = {'molto-positivo':'Molto positivo',positivo:'Positivo',condizionato:'Condizionato',misto:'Misto',sideboard:'Soprattutto sideboard',cauto:'Cauto / negativo',insufficiente:'Insufficiente per Sealed',nd:'Non determinato'};
  const kind = s => s?.kind === 'misto' ? 'Utenti + recensioni' : s?.kind === 'utenti' ? 'Feedback utenti' : 'Recensione';
  const badge = s => `<span class="sent-badge" data-tone="${e(s?.tone || 'nd')}">${e(labels[s?.tone || 'nd'])}</span>`;
  const sources = s => s.sources.map(x => `<a class="sent-source" href="${e(x.url)}" target="_blank" rel="noopener noreferrer">${e(x.label)}${x.language?' · '+e(({ja:'日本語',en:'EN',fr:'FR',de:'DE',zh:'中文'})[x.language]||x.language):''}${x.date?' · '+e(x.date):''} ↗</a>`).join('');
  const score = s => `<p class="sent-index"><strong>Indice sentiment: ${s.index==null?'n.d.':Number(s.index).toLocaleString('it-IT',{minimumFractionDigits:1})+' / 5'}</strong><br><span>Editoriale · ${e(s.confidence)} · ${s.evidenceDocuments} ${s.evidenceDocuments===1?'documento':'documenti'}</span></p><details><summary>Come leggere questo indice</summary><p>${e(s.indexReason)}</p><p>${e(s.indexMethod)} Un documento non equivale a una persona: più articoli dello stesso autore non sono pareri indipendenti. Il numero di fonti non aumenta automaticamente il voto. Le condizioni del mazzo e i dissensi restano nella sintesi.</p></details>`;
  const eligible = c => c.set === 'FRA' && !c.basic && ['common','uncommon'].includes(c.rarity);
  function note(c) {
    if (!eligible(c)) return '';
    const s = c.sentiment;
    if (!s) return '<div class="sent-note"><b>Sentiment · non determinato</b><p>Indice n.d.: nessuna sintesi qualitativa disponibile nella raccolta del 25/09/2026. I voti esterni restano separati.</p></div>';
    return `<div class="sent-note"><b>Sentiment · ${kind(s)}${s.updated?' · Evidenze '+e(s.updated):''}</b><br>${badge(s)}${score(s)}<p>${e(s.summary)}</p><small>${e(s.breadth)} · ${e(DATA.sentimentMeta.date)} · non è un win rate.</small><details><summary>Fonti del sentiment</summary>${sources(s)}</details>${s.observations?.length?`<details><summary>Confronto delle fonti (${s.observations.length})</summary>${s.observations.map(o=>{const src=s.sources.find(x=>x.id===o.source);return `<p><a href="${e(src.url)}" target="_blank" rel="noopener noreferrer">${e(src.label)}</a> · ${e(labels[o.tone])}${o.checked?' · Raccolto '+e(o.checked):''}<br>${e(o.text)}</p>`}).join('')}<small>Prime impressioni e recensioni, comprese esperienze early access. I sottotitoli automatici possono contenere errori: i voti non chiaramente leggibili non vengono trascritti.</small></details>`:''}</div>`;
  }
  function mount() {
    const $ = id => document.getElementById('sent-' + id);
    if (!$('rows')) return;
    const cards = DATA.cards.filter(eligible), m = DATA.sentimentMeta;
    $('stats').innerHTML = [[m.covered,'carte con sintesi'],[m.userCards,'da feedback utenti'],[m.reviewCards,'solo recensioni'],[m.mixedCards,'utenti + recensioni'],[cards.length-m.covered,'senza sintesi aggiunta']].map(([n,t])=>`<div><strong>${n}</strong><span>${t}</span></div>`).join('');
    const fields = ['search','rarity','kind','tone','coverage'];
    function render() {
      const q = $('search').value.trim().toLocaleLowerCase('it');
      const result = cards.filter(c => {
        const s=c.sentiment, coverage=$('coverage').value;
        return (!q || c.full.toLocaleLowerCase('it').includes(q)) && (!$('rarity').value || c.rarity===$('rarity').value) && (!$('kind').value || s?.kinds?.includes($('kind').value)) && (!$('tone').value || (s?.tone || 'nd')===$('tone').value) && (coverage==='all' || coverage==='reviewed'&&s || coverage==='missing'&&!s || coverage==='attention'&&s?.attention);
      }).sort((a,b)=>Number(!!b.sentiment?.attention)-Number(!!a.sentiment?.attention)||a.name.localeCompare(b.name));
      $('count').textContent = `${result.length} carte mostrate su ${cards.length} comuni e non comuni FRA. Filtri indipendenti dall’atlante e dal pool.`;
      $('rows').innerHTML = result.length ? result.map(c => {
        const s = c.sentiment;
        return `<tr><td><a href="Reality-Fracture-Sealed.html?card=${encodeURIComponent(c.id)}#gallery">${e(c.name)}</a><br><small>${c.rarity==='common'?'Comune':'Non comune'}</small>${s?.attention?'<span class="sent-star">Da osservare · scelta editoriale</span>':''}</td><td>${badge(s)}${s?score(s):''}</td><td>${s?`<b>${kind(s)}</b> · ${e(s.breadth)}<p>${e(s.summary)}</p>`:'Nessuna sintesi qualitativa aggiunta. Non equivale a un giudizio neutrale; consulta i voti esterni nella scheda.'}</td><td>${s?sources(s):'—'}</td></tr>`;
      }).join('') : '<tr><td colspan="4">Nessuna carta con questi filtri. Prova ad azzerarli.</td></tr>';
    }
    fields.forEach(id => $(id).addEventListener(id==='search'?'input':'change', () => {
      if (id==='tone' && $('tone').value==='nd') { $('coverage').value='missing'; $('kind').value=''; }
      if (id==='coverage' && ['reviewed','attention'].includes($('coverage').value) && $('tone').value==='nd') $('tone').value='';
      render();
    }));
    $('reset').onclick=()=>{fields.forEach(id=>$(id).value=id==='coverage'?'reviewed':'');render();};
    render();
  }
  document.addEventListener('DOMContentLoaded', mount);
  return {note};
})();
