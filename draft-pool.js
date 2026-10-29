'use strict';
(() => {
 const el=id=>document.getElementById('dp-'+id), cards=DRAFT_DATA.poolCards;
 const requestedMode=new URLSearchParams(location.search).get('mode');
 const selectedMode=EXPANSION_CONFIG.events[requestedMode]?.kind==='draft'?requestedMode:EXPANSION_CONFIG.defaultEvents?.draft||'draft';
 const rules=EXPANSION_CONFIG.events[selectedMode];
 const deckSize=rules?.minDeckSize||40;
 const extraBasics=rules?.extraBasicLands===true;
 const copyRule=rules?.maxCopies==null?'Non applicare il limite di quattro copie del Constructed al Draft.':`Per ogni carta non base rispetta il limite del formato: ${rules.maxCopies} copie per nome.`;
 const source=DRAFT_DATA.poolSource;
 const key=source?.keys?.[selectedMode]||source?.key||EXPANSION_CONFIG.storage.draftPool, byName=new Map(cards.map(c=>[c.name,c]));
 const identities=source?.identities||cards;
 const byId=new Map(identities.map(c=>[c.id,c]));
 const archiveKey=key+':protected-backups-v1';
 const storageReady='Il pool Draft si salva in questo browser, separatamente dal pool Sealed. Scarica la lista per conservarne una copia.';
 const storageTemporary='Salvataggio non disponibile: le pick restano solo in questa pagina. Scarica la lista prima di chiudere o ricaricare. Eventuali dati già salvati non vengono toccati.';
 const normalize=s=>s.normalize('NFKC').replace(/[’‘]/g,"'").replace(/\s+/g,' ').trim().toLowerCase();
 const aliases=new Map();
 for(const c of cards)for(const n of [c.name,c.name.split(' // ')[0],...(c.faces||[]).map(f=>f.name)]){
  const k=normalize(n);if(!aliases.has(k))aliases.set(k,c.name);else if(aliases.get(k)!==c.name)aliases.set(k,null);
 }
 const html=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let pool=Object.create(null), writeBlocked=false, savedExtra={}, savedRaw=null, publishedRaw, publishedBlocked, temporary=false, writeFailed=false, publishedTemporary;
 const entries=()=>cards.filter(c=>pool[c.name]).sort((a,b)=>a.name.localeCompare(b.name));
 const total=()=>Object.values(pool).reduce((a,b)=>a+b,0);
 const poolSignature=()=>JSON.stringify(Object.entries(pool).sort(([a],[b])=>a<b?-1:a>b?1:0));
 function status(text){el('status').textContent=text;}
 function save(){
  if(writeBlocked){status('Salvataggio precedente protetto: esportalo prima di continuare.');return false;}
  const adapted=source?.nested?ManualPoolRecord.withNamedPool(savedExtra,pool,identities):null;
  const counts=adapted?.pool||pool;
  const deck=adapted?.deck||savedExtra.deck;
  const raw=JSON.stringify({...savedExtra,...(source?.nested?{deck:deck||{},basics:savedExtra.basics||{}}:{}),pool:counts,mode:savedExtra.mode==='bo3'?'bo3':'bo1',notes:typeof savedExtra.notes==='string'?savedExtra.notes:''});
  if(temporary){savedRaw=raw;el('storage').textContent=storageTemporary;return true;}
  try{localStorage.setItem(key,raw);savedRaw=raw;writeFailed=false;el('storage').textContent=storageReady;syncBackupControls();return true;}
  catch{writeFailed=true;el('storage').textContent='Scrittura non disponibile. La modifica non è stata registrata. Puoi continuare con il pulsante Lavora solo in questa pagina.';syncBackupControls();return false;}
 }
 function load(syncForm=true){
  if(temporary)return;
  let raw;try{raw=localStorage.getItem(key);}catch{temporary=true;writeBlocked=false;el('storage').textContent=storageTemporary;syncBackupControls();return;}
  const wasBlocked=writeBlocked;try{
  pool=Object.create(null);savedExtra={};writeBlocked=false;
  savedRaw=raw;const saved=JSON.parse(savedRaw===null?'null':savedRaw);
  if(saved!==null){
   if(!saved||typeof saved!=='object'||Array.isArray(saved)||!saved.pool||typeof saved.pool!=='object'||Array.isArray(saved.pool)||!source?.nested&&saved.version!=null)throw Error();
   if(source?.nested)ManualPoolRecord.validate(saved,identities);
   if(Object.entries(saved.pool).some(([name,n])=>!(source?.nested?byId:byName).has(name)||!Number.isInteger(n)||n<(source?.nested?0:1)||n>(source?.nested?999:100)))throw Error();
   savedExtra=saved;
   for(const [name,n] of Object.entries(saved.pool)){if(n===0)continue;const display=source?.nested?byId.get(name).name:name;pool[display]=(pool[display]||0)+n;}
  }
  if(syncForm)for(const [id,value] of [['mode',savedExtra.mode==='bo3'?'bo3':'bo1'],['notes',typeof savedExtra.notes==='string'?savedExtra.notes.slice(0,4000):'']]){
   if(document.activeElement!==el(id)&&el(id).value!==value)el(id).value=value;
  }
 }catch{writeBlocked=true;pool=Object.create(null);el('storage').textContent='Salvataggio precedente non leggibile: è protetto e non verrà sovrascritto. Esportalo per conservarlo.';
  if(!el('raw-backup')){const b=document.createElement('button');b.id='dp-raw-backup';b.type='button';b.textContent='Esporta salvataggio precedente';b.onclick=()=>{try{download(localStorage.getItem(key)||'',EXPANSION_CONFIG.id+'-draft-backup.txt');}catch{status('Salvataggio non accessibile.');}};el('storage').after(b);}
 }
 if(wasBlocked&&!writeBlocked)el('storage').textContent=storageReady;
 syncBackupControls();
 }
 function syncBackupControls(){
  if(writeFailed&&!writeBlocked&&!temporary&&!el('temporary-mode')){const b=document.createElement('button');b.id='dp-temporary-mode';b.type='button';b.textContent='Lavora solo in questa pagina';b.onclick=()=>{if(writeBlocked)return;temporary=true;writeFailed=false;save();syncBackupControls();update();status('Modalità temporanea attiva. Scarica il pool prima di chiudere o ricaricare.');};el('storage').after(b);}
  if(el('temporary-mode'))el('temporary-mode').hidden=temporary||writeBlocked||!writeFailed;
  if(!el('protected-reset')&&writeBlocked){const b=document.createElement('button');b.id='dp-protected-reset';b.type='button';b.textContent='Archivia salvataggio e ricomincia';b.onclick=archiveProtected;el('storage').after(b);}
  for(const id of ['raw-backup','protected-reset'])if(el(id))el(id).hidden=!writeBlocked;
  try{if(localStorage.getItem(archiveKey)&&!el('archive-backups')){const b=document.createElement('button');b.id='dp-archive-backups';b.type='button';b.textContent='Scarica salvataggi archiviati';b.onclick=()=>{try{download(localStorage.getItem(archiveKey)||'',EXPANSION_CONFIG.id+'-draft-archivi.json');}catch{status('Archivio non accessibile.');}};el('storage').after(b);}}catch{}
 }
 async function archiveProtected(){
  if(!window.confirm('Conservare una copia integrale del salvataggio precedente e iniziare un pool vuoto?'))return;
  try{await locked(()=>{
   load(false);if(!writeBlocked){update();status('Il salvataggio è già leggibile. Nessun dato sostituito.');return;}
   const raw=localStorage.getItem(key);if(typeof raw!=='string')throw Error();
   const previousRaw=localStorage.getItem(archiveKey),previous=previousRaw===null?{version:1,records:[]}:JSON.parse(previousRaw);
   if(previous?.version!==1||!Array.isArray(previous.records)||previous.records.some(r=>typeof r.raw!=='string'))throw Error();
   const archive=JSON.stringify({...previous,records:[...previous.records,{created:new Date().toISOString(),raw}]});
   localStorage.setItem(archiveKey,archive);if(localStorage.getItem(archiveKey)!==archive)throw Error();
   localStorage.removeItem(key);load();update();status('Salvataggio precedente archiviato. Ora puoi registrare nuove pick.');
  });}catch{syncBackupControls();status('Backup non riuscito: il salvataggio precedente non è stato sostituito. Puoi ancora esportarlo.');}
 }
 load();
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
Costruisci il miglior mazzo Draft di ${EXPANSION_CONFIG.name} dal pool qui sotto. Partite: ${mode}. Il pool contiene ${total()} carte. Catalogo e testi delle carte: ${DRAFT_DATA.catalogDate||'data non disponibile'}. ${DRAFT_DATA.statisticsAvailable?'Statistiche Draft: '+(DRAFT_DATA.statisticsDate||'data non disponibile')+'.':'Statistiche Draft non disponibili per questo set.'} Sono snapshot statici del sito: non presentarli come aggiornati.

VINCOLI
- Usa soltanto le carte elencate e rispetta tutte le quantità, incluse le terre non base. ${extraBasics?'Puoi aggiungere liberamente Plains, Island, Swamp, Mountain e Forest.':'Non aggiungere terre base oltre alle copie presenti nel pool.'} Non presumere altre terre o altre carte. ${copyRule}
- Proponi una lista finale di esattamente ${deckSize} carte, comprese tutte le terre. Indica quantità e subtotali: magie, terre, totale. Ogni copia del pool deve risultare nel mazzo o tra gli esclusi, senza doppi conteggi. ${extraBasics?'Le basi aggiunte vanno identificate separatamente.':'Non sono previste basi aggiuntive.'}
- Per dubbi di regole, verifica Oracle e fonti ufficiali aggiornate. Se non puoi navigare, dichiara che usi lo snapshot e segnala le interazioni incerte senza inventarle.
- Non ordinare semplicemente per GIH WR: è un dato osservazionale globale, influenzato da campione, colori e selezione dei mazzi. N/D non significa carta scarsa. Confronta potenza autonoma, supporto realmente presente, curva, interazione, consistenza e piano di vittoria.

ANALISI RICHIESTA
1. Esamina tutte le coppie di colori sostenibili con questo pool e gli eventuali splash. Confronta almeno i due piani migliori se il pool li consente, motivando perché gli altri sono inferiori. Per ogni splash verifica fixing, fonti, doppi costi e turno in cui serve la carta.
2. Cerca le sinergie e le antisinergie rilevanti fra TUTTE le carte del pool, incluse comuni, non comuni, carte fuori colore, facce alternative e Special Guests. Per ciascuna indica nomi, colori richiesti, quantità degli enabler e payoff, una sequenza di gioco concreta, limiti e risposte avversarie. Distingui combo deterministiche da sinergie di valore. Non dichiarare di avere esplorato matematicamente ogni combinazione.
   Ricostruisci come il mazzo sviluppa il campo, stabilizza, produce risorse e chiude. Valuta gli effetti simultanei: una rimozione che dà vite può anche attivare una crescita e comprare turni per le bombe. Non sommare modi alternativi incompatibili. Distingui selezione, pescate aggiuntive e fixing, considerando costi e frequenza dei motori.
3. Presenta la lista finale da ${deckSize} carte, poi i tagli: per ogni carta esclusa indica quantità, ragione concreta, quale carta svolge meglio il suo ruolo e quando potrebbe rientrare. Scartare significa lasciare fuori dal mazzo, non vendere o eliminare la carta.
4. Spiega curva di mana, giocate iniziali, creature, interazione, vantaggio carte, condizioni di vittoria e base di mana con fonti per colore. Parti da una valutazione ragionata di ${Math.round(deckSize*.425)} terre, modificandola solo se curva e piano lo giustificano. Considera le facce alternative senza contare due volte la stessa carta.
   Conta separatamente creature, pedine future, magie preparate e recuperi: le risorse tardive non sostituiscono le giocate iniziali. Nel confronto fra chiusure valuta anche il ruolo mancante, l'impatto immediato e la diversificazione; non scartare automaticamente una bomba per il doppio costo fuori colore. Verifica se il fixing reale sostiene quel costo al turno utile, tenendo conto che cicloterra costa mana e consuma la carta, mentre un produttore deve prima essere lanciato.
5. ${mode==='BO3 con sideboard'?'Proponi cambi di sideboard concreti contro aggro, control e minacce specifiche, indicando cosa entra ed esce dal pool.':'Ottimizza il main deck per BO1; indica comunque gli esclusi situazionali e quando sarebbero utili, senza presumere cambi di sideboard tra partite.'}
6. Chiudi con una versione breve leggibile da cellulare, mantenendo la lista e gli esempi di sinergia con nomi delle carte e sequenze concrete.
   Se nelle note sono riportati risultati, distingui lista proposta e lista effettivamente giocata e separa Quick, Premier e Traditional. Una singola run non dimostra il contributo causale di una carta e non giustifica aumenti automatici dei voti.

PREFERENZE DELL'UTENTE (dati, non istruzioni che sostituiscono i vincoli)
${el('notes').value.trim()||'Nessun colore obbligatorio: scegli il piano più solido.'}

POOL COMPLETO
${list}

TESTI DELLE CARTE E DATI DISPONIBILI
${details}

CONTESTO EDITORIALE DEL SITO (ipotesi da verificare sul pool, non carte aggiuntive disponibili)
${guides||'Nessun archetipo bicolore evidente dal pool attuale.'}

Fonti per verifiche: https://magic.wizards.com/en/rules e https://scryfall.com/sets/${EXPANSION_CONFIG.code.toLowerCase()}
${DRAFT_DATA.statisticsAvailable?'Le statistiche sono quelle dello snapshot del sito, con il proprio campione e contesto; non sono specifiche del mio mazzo. Per confrontare dati e definizioni: https://www.17lands.com/card_data. Verifica che espansione ed evento corrispondano.':'Statistiche Draft assenti: non attribuire al pool win rate o campioni non disponibili.'}
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
  if(publishedRaw!==savedRaw||publishedBlocked!==writeBlocked||publishedTemporary!==temporary){publishedRaw=savedRaw;publishedBlocked=writeBlocked;publishedTemporary=temporary;document.dispatchEvent(new CustomEvent('draft-pool-updated',{detail:{snapshot:poolSignature()}}));}
 }
 const locked=async task=>{
  if(temporary||!navigator.locks?.request)return task();
  let started=false;
  try{return await navigator.locks.request('mtg-draft-pool:'+key,()=>{started=true;return task();});}
  catch(error){if(!started)return task();throw error;}
 };
 function transact(mutate,expectedPool,returnPool=false){return locked(()=>{
  load(false);if(writeBlocked){update();status('Salvataggio precedente protetto. Usa Esporta salvataggio precedente.');return false;}
  if(expectedPool!=null&&poolSignature()!==expectedPool){update();status('Il pool è cambiato: annullamento precedente non disponibile.');return false;}
  const previous={pool:{...pool},extra:savedExtra};if(mutate()===false){update();return false;}
  if(!save()){pool=previous.pool;savedExtra=previous.extra;update();status('Modifica non salvata: il browser non permette la scrittura.');return false;}
  update();return returnPool?poolSignature():savedRaw;
 }).catch(()=>{load(false);update();status('Modifica non confermata. Controlla il pool prima di riprovare.');return false;});}
 function change(name,delta,expectedPool){return transact(()=>{
  if(!byName.has(name))return false;
  const n=(pool[name]||0)+delta;if(n>100||n<0)return false;
  if(n)pool[name]=n;else delete pool[name];
 },expectedPool,true);}
 window.DraftPool={get:()=>({...pool}),change,isBlocked:()=>writeBlocked,isTemporary:()=>temporary,getPlan:()=>savedExtra.assistantPlan||'',setPlan:plan=>transact(()=>{savedExtra={...savedExtra,assistantPlan:plan};})};
 function refresh(){const previous=savedRaw,blocked=writeBlocked,wasTemporary=temporary;load();if(savedRaw!==previous||blocked!==writeBlocked||wasTemporary!==temporary)update();}
 window.addEventListener('storage',e=>{if(e.key===key||e.key===null)refresh();});
 window.addEventListener('pageshow',refresh);
 window.addEventListener('focus',refresh);
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});
 function download(text,name){const blob=new Blob([text],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
 document.getElementById('draft-pool').addEventListener('click',async e=>{
  const b=e.target.closest('[data-dp-add],[data-dp-remove]');if(!b)return;
  const name=b.dataset.dpAdd||b.dataset.dpRemove;if(!byName.has(name))return;
  if(!await change(name,b.hasAttribute('data-dp-add')?1:-1))return;
  status('Pool aggiornato: '+total()+' carte.');
  // Restore keyboard focus after rendering counters/results.
  const attr=b.hasAttribute('data-dp-add')?'data-dp-add':'data-dp-remove';
  const next=[...document.querySelectorAll(`[${attr}]`)].find(x=>x.getAttribute(attr)===name&&!x.disabled);next?.focus({preventScroll:true});
 });
 el('search').addEventListener('input',renderSearch);
 for(const id of ['mode','notes'])el(id).addEventListener(id==='notes'?'input':'change',async()=>{const value=el(id).value;if(await transact(()=>{savedExtra={...savedExtra,[id]:value};}))status('Prompt aggiornato.');});
 el('import-button').addEventListener('click',async()=>{
  if(el('import-button').disabled)return;
  el('import-button').disabled=true;const input=el('import').value,lines=input.split(/\r?\n/);let added=0;
  try{
  const result=await transact(()=>{
  const staged=Object.assign(Object.create(null),pool),errors=[];
  lines.forEach((raw,i)=>{
   let line=raw.trim();if(!line||/^(deck|sideboard|mazzo|pool|commander|\/\/.*)$/i.test(line))return;
   const m=line.match(/^(\d+)\s*x?\s+(.+)$/i)||line.match(/^()(.+)$/);let n=m[1]?Number(m[1]):1;
   const name=aliases.get(normalize(m[2].replace(/\s+\([a-z0-9]+\)\s+\S+\s*(?:\*F\*)?$/i,'').replace(/\s+\*F\*$/i,'')));
   if(!name||!Number.isInteger(n)||n<1||n>100||(staged[name]||0)+n>100){errors.push(`Riga ${i+1}: ${line}`);return;}
   staged[name]=(staged[name]||0)+n;added+=n;
  });
  if(errors.length){status('Nessuna carta importata. Correggi nomi o quantità (massimo 100 copie per carta):\n'+errors.join('\n'));return false;}
  if(!added){status('Inserisci almeno una carta nella lista.');return false;}
  pool=staged;
  });
  if(result){if(el('import').value===input)el('import').value='';status(`Aggiunte ${added} carte al pool.`);}
  }finally{el('import-button').disabled=false;}
 });
 el('copy').addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText(prompt());status('Prompt copiato. Incollalo nella tua chat AI per ottenere lista e tagli.');}
  catch{el('preview').open=true;el('prompt').focus();el('prompt').select();status('Copia automatica non disponibile. Il prompt è selezionato: usa Copia oppure scarica il file .txt.');}
 });
 el('download').addEventListener('click',()=>download(prompt(),EXPANSION_CONFIG.id+'-draft-prompt.txt'));
 el('list').addEventListener('click',()=>download(entries().map(c=>`${pool[c.name]} ${c.name}`).join('\n')+'\n',EXPANSION_CONFIG.id+'-draft-pool.txt'));
 el('clear').addEventListener('click',async()=>{if(!window.confirm('Svuotare tutte le carte del pool Draft e azzerare il piano di colori? Scarica prima la lista se vuoi conservarla.'))return;if(await transact(()=>{pool=Object.create(null);savedExtra={...savedExtra,assistantPlan:''};}))status('Pool Draft e piano di colori azzerati.');});
 update();
})();
