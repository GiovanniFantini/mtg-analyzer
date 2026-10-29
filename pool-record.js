'use strict';
// Read/write adapters for the existing ID-based manual pool and deck records.
window.ManualPoolRecord={
 validate(record,cards){
  if(!record||typeof record!=='object'||Array.isArray(record)||record.version!=null&&record.version!==1)throw Error('Salvataggio non compatibile.');
  const ids=new Set(cards.map(card=>card.id));
  for(const field of ['pool','deck','basics']){
   const counts=record[field];
   if(!counts||typeof counts!=='object'||Array.isArray(counts))throw Error('Conteggi mancanti: '+field);
   for(const [id,n]of Object.entries(counts))if(!ids.has(id)||!Number.isInteger(n)||n<0||n>999)throw Error('Carta o quantità non valida.');
  }
  for(const [id,n]of Object.entries(record.deck))if(n>(record.pool[id]||0))throw Error('Il mazzo supera le copie del pool.');
  return record;
 },
 withPool(record,pool){
  const deck=Object.fromEntries(Object.entries(record.deck||{}).map(([id,n])=>[id,Math.min(n,pool[id]||0)]).filter(([,n])=>n>0));
  return {...record,pool,deck};
 },
 withNamedPool(record,counts,identities){
  const byId=new Map(identities.map(card=>[card.id,card.name])),left={...counts},pool={};
  // Preserve deck copies first, then sideboard copies, retaining printing IDs.
  for(const id of Object.keys(record.pool||{}))pool[id]=0;
  for(const [id,n]of Object.entries(record.pool||{})){
   const name=byId.get(id),take=Math.min(n,record.deck?.[id]||0,left[name]||0);
   pool[id]=take;left[name]=(left[name]||0)-take;
  }
  for(const [id,n]of Object.entries(record.pool||{})){
   const name=byId.get(id),take=Math.min(n-pool[id],left[name]||0);
   if(take){pool[id]+=take;left[name]-=take;}
  }
  for(const [name,n]of Object.entries(left))if(n>0){
   const previous=Object.keys(record.pool||{}).find(id=>byId.get(id)===name);
   const id=previous||identities.find(card=>card.name===name)?.id;
   if(!id)throw Error('Carta sconosciuta: '+name);
   pool[id]=(pool[id]||0)+n;
  }
  return this.withPool(record,Object.fromEntries(Object.entries(pool).filter(([,n])=>n>0)));
 }
};
