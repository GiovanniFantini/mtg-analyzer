'use strict';
// Pure, transparent heuristics over existing Limited reviews, never win-rate estimates.
((root)=>{
 const colors=c=>(c.colors||[...(c.color||'')]);
 const primary=c=>c.faces?.[0]||{};
 const creature=c=>/\bCreature\b/.test(primary(c).type_line||c.type||'');
 const mana=c=>{const f=primary(c);if(f.mana_cost!=null){return [...f.mana_cost.matchAll(/\{([^}]+)\}/g)].reduce((n,m)=>n+(/^\d+$/.test(m[1])?Number(m[1]):m[1]==='X'?0:m[1].split('/').includes('2')?2:1),0);}return c.mv??null;};
 const fits=(c,plan)=>{
  if(!plan)return true;
  const cost=primary(c).mana_cost??c.cost??'';
  return [...cost.matchAll(/\{([^}]+)\}/g)].every(m=>{
   const options=m[1].split('/').filter(x=>/^[WUBRG]$/.test(x));
   return !options.length||m[1].split('/').includes('2')||options.some(x=>plan.includes(x));
  });
 };
 const rating=c=>Number.isFinite(c.community)?c.community:Number.isFinite(c.score)?c.score:null;
 const land=c=>c.land===true||/\bLand\b/.test(primary(c).type_line||c.type||'');
 const candidatePlans=ctx=>ctx.flexibleSecond?[ctx.plan,...[...'WUBRG'].filter(x=>!ctx.plan.includes(x)).map(x=>ctx.plan+x)]:[ctx.plan];
 const compatible=(c,ctx)=>candidatePlans(ctx).some(p=>fits(c,p));
 function context(cards,pool,chosen=''){
  const picked=cards.filter(c=>pool[c.name]>0),total=picked.reduce((n,c)=>n+pool[c.name],0),progress=picked.filter(c=>!c.basic).reduce((n,c)=>n+pool[c.name],0);
  const weights=Object.fromEntries([...'WUBRG'].map(x=>[x,0]));
  for(const c of picked)for(const color of colors(c))weights[color]+=pool[c.name]*Math.max(.5,(rating(c)??2.5)-1)/Math.max(1,colors(c).length);
  const sorted=Object.keys(weights).sort((a,b)=>weights[b]-weights[a]);
  let plan=chosen==='open'?'':chosen;
  if(!chosen&&progress>=6&&weights[sorted[0]]>0)plan=sorted.filter((c,i)=>i<2&&weights[c]>=weights[sorted[0]]*.4).join('');
  const playable=picked.filter(c=>fits(c,plan)),bodies=playable.filter(creature);
  const count=fn=>playable.filter(fn).reduce((n,c)=>n+pool[c.name],0);
  return {plan,flexibleSecond:!chosen&&plan.length===1,total,progress,picked,playable,early:count(c=>creature(c)&&mana(c)!=null&&mana(c)<=2),bodies:bodies.reduce((n,c)=>n+pool[c.name],0),high:count(c=>!land(c)&&mana(c)>=5),spells:count(c=>!land(c))};
 }
 function evaluate(c,ctx,pool,data){
  const base=rating(c),reasons=[],warnings=[],parts={rating:base??0,colors:0,early:0,bodies:0,high:0,combo:0,archetype:0,conditional:0};let value=base??0;
  if(base==null)warnings.push('Manca un voto Limited: confronto incerto.');
  if(land(c))warnings.push('Mana prodotto dalla terra non valutato: controlla l’anteprima.');
  else if(ctx.plan){
   if(fits(c,ctx.plan)){value+=.3;parts.colors=.3;}
   else if(ctx.flexibleSecond&&compatible(c,ctx))reasons.push((c.role||'Valore di base dalla recensione Limited')+'. Secondo colore possibile.');
   else{parts.colors=ctx.progress>=12?-2:-1;value+=parts.colors;warnings.push('Fuori dai colori principali: non presumo uno splash sostenibile.');}
  }
  if(compatible(c,ctx)&&ctx.spells>=6&&creature(c)&&mana(c)!=null&&mana(c)<=2&&ctx.early/ctx.spells<.25){value+=.55;parts.early=.55;reasons.unshift('Ti serve una creatura per i primi turni.');}
  if(compatible(c,ctx)&&ctx.spells>=8&&ctx.bodies/ctx.spells<.5&&creature(c)){value+=.25;parts.bodies=.25;reasons.push('Aumenta le creature del piano.');}
  if(ctx.spells>=8&&ctx.high/ctx.spells>=.3&&mana(c)>=5){value-=.45;parts.high=-.45;warnings.push('Hai già molti costi alti.');}
  const byId=new Map(data.cards.map(x=>[x.id,x]));
  const combo=(data.combos||[]).find(x=>x.cards.includes(c.id)&&x.cards.length>1&&candidatePlans(ctx).some(plan=>fits(c,plan)&&x.cards.filter(id=>id!==c.id).every(id=>{const p=byId.get(id);return p&&pool[p.name]>0&&fits(p,plan);})));
  if(combo){value+=.5;parts.combo=.5;const partners=combo.cards.filter(id=>id!==c.id).map(id=>byId.get(id).name);reasons.unshift('Sinergia con '+partners.join(', ')+', già nel pool.');}
  const guide=data.guides?.[ctx.plan]||Object.entries(data.guides||{}).find(([key])=>key.length===ctx.plan.length&&[...key].every(x=>ctx.plan.includes(x)))?.[1];
  const inGuide=p=>guide&&[...(guide.core||[]),...(guide.support||[])].some(n=>n===p.name||n===p.shortName);
  if(inGuide(c)&&ctx.playable.filter(inGuide).length>=2){value+=.2;parts.archetype=.2;reasons.push('Sostiene il piano '+guide.theme+'.');}
  if(c.build&&!combo){value-=.35;parts.conditional=-.35;warnings.push('Carta condizionale: controlla il supporto richiesto.');}
  if(!reasons.length)reasons.push(c.role||'Valore di base dalla recensione Limited.');
  return {card:c,value,base,parts,reasons,warnings,condition:c.condition||'',why:c.why||''};
 }
 function explain(best,other){
  const key=Object.keys(best.parts).sort((a,b)=>(best.parts[b]-other.parts[b])-(best.parts[a]-other.parts[a]))[0];
  const text={rating:'Ha un voto Limited di partenza più alto.',colors:best.parts.colors>0?'Resta nei tuoi colori; l’altra richiede fonti aggiuntive.':'Può aprire il secondo colore; l’altra è fuori piano.',early:'Ti serve di più una creatura per i primi turni.',bodies:'Aggiunge una creatura al piano che ne ha poche.',high:'Appesantisce meno la curva già alta.',combo:best.reasons.find(r=>r.startsWith('Sinergia con ')),archetype:best.reasons.find(r=>r.startsWith('Sostiene il piano ')),conditional:'Richiede meno supporto ancora da trovare.'};
  return text[key]||best.reasons[0];
 }
 const comparisonGap=(best,other)=>Math.round((best.value-other.value)*1e6)/1e6;
 const api={colors,mana,creature,fits,compatible,land,rating,context,evaluate,explain,comparisonGap};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.DraftAdvisor=api;
})(globalThis);
