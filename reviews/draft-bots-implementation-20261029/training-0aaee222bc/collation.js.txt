'use strict';
/* Versioned, declarative product recipes, shared by Draft and Sealed. */
((root) => {
 function createCollator(format, random) {
  const spec=format.collation, byId=Object.fromEntries(format.cards.map(c=>[c.id,c]));
  if(spec?.schemaVersion!==1)throw Error('Versione della collazione non supportata');
  const groups=Object.fromEntries(Object.entries(spec.groups).map(([key,ids])=>[key,ids.map(id=>{
   if(!byId[id])throw Error('Stampa sconosciuta: '+id);return byId[id];
  })]));
  const printedPartners={},partners={};
  for(const [a,b] of spec.partners||[]){
   if(!byId[a]||!byId[b]||byId[a].rarity!==byId[b].rarity)throw Error('Coppia non valida');
   printedPartners[a]=b;printedPartners[b]=a;partners[byId[a].full]=byId[b].full;partners[byId[b].full]=byId[a].full;
  }
  function weighted(items){
   if(!items.length||items.some(b=>!Number.isFinite(b.weight)||b.weight<0)||Math.abs(items.reduce((n,b)=>n+b.weight,0)-1)>1e-8)throw Error('Distribuzione non valida');
   let value=random();for(const b of items){value-=b.weight;if(value<0)return b;}return items.at(-1);
  }
  const branches={};let length=0;const previous=new Set();
  for(const rule of spec.recipe){
   if(!['draw','replace','pair'].includes(rule.op))throw Error('Operazione di collazione non supportata: '+rule.op);
   if(previous.has(rule.id))throw Error('Identificatore slot duplicato');
   if(!Number.isInteger(rule.count??1)||(rule.count??1)<1)throw Error('Quantità slot non valida');
   if(rule.op==='replace'){
    if(!previous.has(rule.target)||!Number.isFinite(rule.chance)||rule.chance<0||rule.chance>1)throw Error('Sostituzione non valida');
   }else length+=(rule.count??1)*(rule.op==='pair'?2:1);
   if((rule.exclude||[]).some(id=>!previous.has(id)))throw Error('Esclusione non valida');
   if(Math.abs(rule.branches.reduce((n,b)=>n+b.weight,0)-1)>1e-8||rule.branches.some(b=>!Number.isFinite(b.weight)||b.weight<0||!groups[b.group]?.length))throw Error('Gruppo o distribuzione non valida');
   if(rule.op==='pair'&&rule.branches.some(b=>groups[b.group].some(c=>!printedPartners[c.id])))throw Error('Partner mancante');
   branches[rule.id]=rule.branches.map(b=>[b.weight,{cards:groups[b.group],foil:!!(rule.foil||b.foil)}]);
   previous.add(rule.id);
  }
  if(length!==format.packSize)throw Error('Dimensione busta incompatibile con la ricetta');
  let sequence=0;
  function pack(){
   let result=[];const drawn={};
   for(const rule of spec.recipe){
    if(rule.op==='replace'&&random()>=rule.chance)continue;
    const selected=[];
    for(let i=0;i<(rule.count??1);i++){
     // A one-branch guaranteed common draw does not need an extra RNG call.
     // This preserves historical FRA sessions and their deterministic routing.
     const branch=(rule.unique||rule.op==='replace')&&rule.branches.length===1?rule.branches[0]:weighted(rule.branches);
     const excluded=new Set((rule.exclude||[]).flatMap(key=>drawn[key]||[]).map(e=>byId[e.id].full));
     if(rule.unique)selected.forEach(e=>excluded.add(byId[e.id].full));
     const available=groups[branch.group].filter(c=>!excluded.has(c.full));
     if(!available.length)throw Error('Nessuna carta disponibile nello slot '+rule.id);
     const card=available[Math.floor(random()*available.length)];
     const cards=rule.op==='pair'?[card,byId[printedPartners[card.id]]]:[card];
     selected.push(...cards.map(c=>({uid:sequence++,id:c.id,slot:rule.id,foil:!!(rule.foil||branch.foil)})));
    }
    if(rule.op==='replace'){
     const targets=drawn[rule.target]||[];
     if(targets.length<selected.length)throw Error('Sostituzione senza carte sufficienti');
     const removed=new Set(targets.slice(0,selected.length));
     result=result.filter(e=>!removed.has(e));drawn[rule.target]=targets.filter(e=>!removed.has(e));
    }
    drawn[rule.id]=selected;result.push(...selected);
   }
   if(result.length!==format.packSize)throw Error('Dimensione busta non valida');return result;
  }
  return {pack,branches,partners};
 }
 const api={createCollator};
 if(typeof module!=='undefined')module.exports=api;else root.Collation=api;
})(globalThis);
