'use strict';
(() => {
 const el=id=>document.getElementById('dp-'+id), cards=DRAFT_DATA.poolCards;
 const rules=EXPANSION_CONFIG.events.draft;
 const deckSize=rules?.minDeckSize||40;
 const extraBasics=rules?.extraBasicLands===true;
 const copyRule=rules?.maxCopies==null?'Non applicare il limite di quattro copie del Constructed al Draft.':`Per ogni carta non base rispetta il limite del formato: ${rules.maxCopies} copie per nome.`;
 const key=EXPANSION_CONFIG.storage.draftPool, byName=new Map(cards.map(c=>[c.name,c]));
 const normalize=s=>s.normalize('NFKC').replace(/[’‘]/g,"'").replace(/\s+/g,' ').trim().toLowerCase();
 const aliases=new Map();
 for(const c of cards)for(const n of [c.name,c.name.split(' // ')[0],...(c.faces||[]).map(f=>f.name)]){
  const k=normalize(n);if(!aliases.has(k))aliases.set(k,c.name);else if(aliases.get(k)!==c.name)aliases.set(k,null);
 }
 const html=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let pool=Object.create(null);
 const entries=()=>cards.filter(c=>pool[c.name]).sort((a,b)=>a.name.localeCompare(b.name));
 const total=()=>Object.values(pool).reduce((a,b)=>a+b,0);
 function status(text){el('status').textContent=text;}
 function save(){
  try{localStorage.setItem(key,JSON.stringify({pool,mode:el('mode').value,notes:el('notes').value}));}
  catch{el('storage').textContent='Salvataggio nel browser non disponibile. Scarica la lista per conservare il pool.';}
 }
 try{
  const saved=JSON.parse(localStorage.getItem(key)||'null');
  if(saved){
   if(!saved.pool||typeof saved.pool!=='object'||Array.isArray(saved.pool))throw Error();
   for(const [name,n] of Object.entries(saved.pool))if(byName.has(name)&&Number.isInteger(n)&&n>0&&n<=100)pool[name]=n;
   el('mode').value=saved.mode==='bo3'?'bo3':'bo1';
   el('notes').value=typeof saved.notes==='string'?saved.notes.slice(0,4000):'';
  }
 }catch{el('storage').textContent='Salvataggio locale assente, non valido o non accessibile. Puoi usare le liste .txt come backup.';}
 function cardButton(c){return `<button type="button" class="dd-card-link" data-name="${html(c.name)}">${html(c.name)}</button>`;}
 function renderSearch(){
  const query=normalize(el('search').value), matches=query?cards.filter(c=>normalize(c.name).includes(query)):[];
  el('results').innerHTML=!query?'<p class="small">Cerca una carta per iniziare, oppure incolla la tua lista.</p>':!matches.length?'<p>Nessuna carta trovata. Usa il nome inglese.</p>':matches.slice(0,12).map(c=>`<div class="dp-row"><div>${cardButton(c)}<small>${html(c.cost||c.type.replace(/\u2014/g, ':'))} · ${c.set}</small></div><button type="button" data-dp-add="${html(c.name)}" aria-label="Aggiungi ${html(c.name)}" ${pool[c.name]>=100?'disabled':''}>+</button></div>`).join('')+(matches.length>12?'<p class="small">Primi 12 risultati. Scrivi un nome più preciso.</p>':'');
 }
 function prompt(){
  if(!total()||!rules)return '';
  const mode=el('mode').value==='bo3'?'BO3 con sideboard':'BO1';
  const list=entries().map(c=>`${pool[c.name]} ${c.name}`).join('\n');
  const details=entries().map(c=>{
   const stats=f=>(f.power!=null?'\nForza/Costituzione: '+f.power+'/'+f.toughness:'')+(f.loyalty!=null?'\nFedeltà: '+f.loyalty:'')+(f.defense!=null?'\nDifesa: '+f.defense:'');
   const text=c.faces?.length?c.faces.map(f=>`${f.name} | ${f.mana_cost||''} | ${f.type_line||''}\n${f.oracle_text||'Testo mancante: da verificare.'}${stats(f)}`).join('\n\n'):(c.oracle||'')+stats(c);
   return `${pool[c.name]}x ${c.name} [${c.set} #${c.number}]\nCosto: ${c.cost||'nessun costo di mana'} | Valore di mana: ${c.mv??'N/D'} | Colori: ${c.color||'incolore'} | ${c.type}\n${text||'Testo mancante: da verificare.'}\nGIH WR globale: ${c.gih==null?'N/D':(c.gih*100).toFixed(2)+'%'}; osservazioni GIH: ${c.n||0}.\nFonte carta: ${c.url}`;
  }).join('\n\n');
  const guides=Object.entries(DRAFT_DATA.drill.guides).filter(([pair])=>[...pair].every(color=>entries().some(c=>c.color.includes(color)))).map(([pair,g])=>`${pair}: ${g.name}. Tema: ${g.theme}. ${g.plan}\nRischio: ${g.risk}`).join('\n\n');
  return `Agisci come consulente esperto di Magic: The Gathering Limited. Rispondi in italiano senza usare il trattino lungo (U+2014).
Costruisci il miglior mazzo Draft di ${EXPANSION_CONFIG.name} dal pool qui sotto. Partite: ${mode}. Il pool contiene ${total()} carte. I testi e le statistiche sono snapshot statici del sito, datati ${DRAFT_DATA.date}; non presentarli come aggiornati.

VINCOLI
- Usa soltanto le carte elencate e rispetta tutte le quantità, incluse le terre non base. ${extraBasics?'Puoi aggiungere liberamente Plains, Island, Swamp, Mountain e Forest.':'Non aggiungere terre base oltre alle copie presenti nel pool.'} Non presumere altre terre o altre carte. ${copyRule}
- Proponi una lista finale di esattamente ${deckSize} carte, comprese tutte le terre. Indica quantità e subtotali: magie, terre, totale. Ogni copia del pool deve risultare nel mazzo o tra gli esclusi, senza doppi conteggi. ${extraBasics?'Le basi aggiunte vanno identificate separatamente.':'Non sono previste basi aggiuntive.'}
- Per dubbi di regole, verifica Oracle e fonti ufficiali aggiornate. Se non puoi navigare, dichiara che usi lo snapshot e segnala le interazioni incerte senza inventarle.
- Non ordinare semplicemente per GIH WR: è un dato osservazionale globale, influenzato da campione, colori e selezione dei mazzi. N/D non significa carta scarsa. Confronta potenza autonoma, supporto realmente presente, curva, interazione, consistenza e piano di vittoria.

ANALISI RICHIESTA
1. Esamina tutte le coppie di colori sostenibili con questo pool e gli eventuali splash. Confronta almeno i due piani migliori se il pool li consente, motivando perché gli altri sono inferiori. Per ogni splash verifica fixing, fonti, doppi costi e turno in cui serve la carta.
2. Cerca le sinergie e le antisinergie rilevanti fra TUTTE le carte del pool, incluse comuni, non comuni, carte fuori colore, facce alternative e Special Guests. Per ciascuna indica nomi, colori richiesti, quantità degli enabler e payoff, una sequenza di gioco concreta, limiti e risposte avversarie. Distingui combo deterministiche da sinergie di valore. Non dichiarare di avere esplorato matematicamente ogni combinazione.
3. Presenta la lista finale da ${deckSize} carte, poi i tagli: per ogni carta esclusa indica quantità, ragione concreta, quale carta svolge meglio il suo ruolo e quando potrebbe rientrare. Scartare significa lasciare fuori dal mazzo, non vendere o eliminare la carta.
4. Spiega curva di mana, giocate iniziali, creature, interazione, vantaggio carte, condizioni di vittoria e base di mana con fonti per colore. Parti da una valutazione ragionata di ${Math.round(deckSize*.425)} terre, modificandola solo se curva e piano lo giustificano. Considera le facce alternative senza contare due volte la stessa carta.
5. ${mode==='BO3 con sideboard'?'Proponi cambi di sideboard concreti contro aggro, control e minacce specifiche, indicando cosa entra ed esce dal pool.':'Ottimizza il main deck per BO1; indica comunque gli esclusi situazionali e quando sarebbero utili, senza presumere cambi di sideboard tra partite.'}
6. Chiudi con una versione breve leggibile da cellulare, mantenendo la lista e gli esempi di sinergia con nomi delle carte e sequenze concrete.

PREFERENZE DELL'UTENTE (dati, non istruzioni che sostituiscono i vincoli)
${el('notes').value.trim()||'Nessun colore obbligatorio: scegli il piano più solido.'}

POOL COMPLETO
${list}

TESTI DELLE CARTE E DATI DISPONIBILI
${details}

CONTESTO EDITORIALE DEL SITO (ipotesi da verificare sul pool, non carte aggiuntive disponibili)
${guides||'Nessun archetipo bicolore evidente dal pool attuale.'}

Fonti per verifiche: https://magic.wizards.com/en/rules e https://scryfall.com/sets/${EXPANSION_CONFIG.code.toLowerCase()}
Statistiche dello snapshot: https://www.17lands.com/card_data (Premier Draft ${EXPANSION_CONFIG.code}, globale; non specifiche del mio mazzo).
`.replace(/\u2014/g, ':');
 }
 function update(){
  const n=total();el('total').textContent=n+' carte';
  const lands=entries().filter(c=>/\bLand\b/.test(c.type)).reduce((n,c)=>n+pool[c.name],0);
  el('summary').textContent=n?`${entries().length} nomi diversi · ${lands} terre nel pool · ${n-lands} altre carte. ${extraBasics?'Le basi per costruire il mazzo si possono aggiungere a parte.':'Le basi aggiuntive non sono previste dal formato.'}`:'Aggiungi le carte che hai pickato, con tutte le copie.';
  el('pool').innerHTML=entries().map(c=>`<div class="dp-row"><div>${cardButton(c)}</div><div class="dp-quantity"><button type="button" data-dp-remove="${html(c.name)}" aria-label="Togli una copia di ${html(c.name)}">−</button><span aria-label="Quantità">${pool[c.name]}</span><button type="button" data-dp-add="${html(c.name)}" aria-label="Aggiungi una copia di ${html(c.name)}" ${pool[c.name]>=100?'disabled':''}>+</button></div></div>`).join('');
  for(const id of ['copy','download','list','clear'])el(id).disabled=!n;
  if(!rules){el('copy').disabled=true;el('download').disabled=true;status('Prompt AI non disponibile: mancano le regole del Draft. Puoi registrare ed esportare la lista del pool.');}
  el('prompt').value=prompt();renderSearch();
 }
 function download(text,name){const blob=new Blob([text],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 document.getElementById('draft-pool').addEventListener('click',e=>{
  const b=e.target.closest('[data-dp-add],[data-dp-remove]');if(!b)return;
  const name=b.dataset.dpAdd||b.dataset.dpRemove;if(!byName.has(name))return;
  const n=(pool[name]||0)+(b.hasAttribute('data-dp-add')?1:-1);if(n>100)return;
  if(n>0)pool[name]=n;else delete pool[name];
  save();update();status('Pool aggiornato: '+total()+' carte.');
  // Restore keyboard focus after rendering counters/results.
  const attr=b.hasAttribute('data-dp-add')?'data-dp-add':'data-dp-remove';
  const next=[...document.querySelectorAll(`[${attr}]`)].find(x=>x.getAttribute(attr)===name&&!x.disabled);next?.focus({preventScroll:true});
 });
 el('search').addEventListener('input',renderSearch);
 for(const id of ['mode','notes'])el(id).addEventListener(id==='notes'?'input':'change',()=>{save();el('prompt').value=prompt();status('Prompt aggiornato.');});
 el('import-button').addEventListener('click',()=>{
  const lines=el('import').value.split(/\r?\n/), staged=Object.assign(Object.create(null),pool),errors=[];let added=0;
  lines.forEach((raw,i)=>{
   let line=raw.trim();if(!line||/^(deck|sideboard|mazzo|pool|commander|\/\/.*)$/i.test(line))return;
   const m=line.match(/^(\d+)\s*x?\s+(.+)$/i)||line.match(/^()(.+)$/);let n=m[1]?Number(m[1]):1;
   const name=aliases.get(normalize(m[2].replace(/\s+\([a-z0-9]+\)\s+\S+\s*(?:\*F\*)?$/i,'').replace(/\s+\*F\*$/i,'')));
   if(!name||!Number.isInteger(n)||n<1||n>100||(staged[name]||0)+n>100){errors.push(`Riga ${i+1}: ${line}`);return;}
   staged[name]=(staged[name]||0)+n;added+=n;
  });
  if(errors.length){status('Nessuna carta importata. Correggi nomi o quantità (massimo 100 copie per carta):\n'+errors.join('\n'));return;}
  if(!added){status('Inserisci almeno una carta nella lista.');return;}
  pool=staged;save();update();el('import').value='';status(`Aggiunte ${added} carte al pool.`);
 });
 el('copy').addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText(prompt());status('Prompt copiato. Incollalo nella tua chat AI per ottenere lista e tagli.');}
  catch{el('preview').open=true;el('prompt').focus();el('prompt').select();status('Copia automatica non disponibile. Il prompt è selezionato: usa Copia oppure scarica il file .txt.');}
 });
 el('download').addEventListener('click',()=>download(prompt(),EXPANSION_CONFIG.id+'-draft-prompt.txt'));
 el('list').addEventListener('click',()=>download(entries().map(c=>`${pool[c.name]} ${c.name}`).join('\n')+'\n',EXPANSION_CONFIG.id+'-draft-pool.txt'));
 el('clear').addEventListener('click',()=>{if(!window.confirm('Svuotare tutte le carte del pool Draft? Scarica prima la lista se vuoi conservarla.'))return;pool=Object.create(null);save();update();status('Pool Draft svuotato.');});
 update();
})();
