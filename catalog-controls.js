'use strict';
// Shared catalog filters and ordering, independent of set and presentation.
window.CatalogControls={create(DATA,expansionCode=DATA.code){
const $=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function group(c){return c.land?'L':c.colors.length>1?'M':c.colors[0]||'C'}
const CATALOG_TYPES={Creature:'Creatura',Instant:'Istantaneo',Sorcery:'Stregoneria',Artifact:'Artefatto',Enchantment:'Incantesimo',Planeswalker:'Planeswalker',Land:'Terra',Battle:'Battaglia',Kindred:'Affine'};
const TIERS=['S','A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F'];
const wrSource=DATA.catalogWinRates||{cards:{}};
function winRate(c){const value=wrSource.cards[c.id]?.value;return Number.isFinite(value)?value:null}
function rangeMatches(value,minId,maxId){const min=$(minId).value,max=$(maxId).value;if(min===''&&max==='')return true;return Number.isFinite(value)&&(min===''||value>=Number(min))&&(max===''||value<=Number(max))}
function cardTypes(c){return Object.keys(CATALOG_TYPES).filter(type=>new RegExp('\\b'+type+'\\b').test(c.type.split(' // ')[0].split(' — ')[0]))}
function extraMatches(c){
const tier=$('catalog-tier').value,r=c.untappedPickOrder,wr=winRate(c),reviews=$('review-data').value,wrData=$('wr-data').value;
const rating=$('rating').value,evidence=c.evidence||[],diff=evidence.length>1&&Math.max(...evidence.map(e=>e.stars))-Math.min(...evidence.map(e=>e.stars))>=1;
const sentiment=$('catalog-sentiment').value,cs=c.sentiment;
const sm=!sentiment||sentiment==='covered'&&cs||sentiment==='updated'&&cs?.observations?.some(o=>o.batch==='set-refresh')||sentiment==='regional'&&cs?.batch==='regional-refresh'||sentiment==='european'&&cs?.languages?.some(l=>['fr','de'].includes(l))||sentiment==='japanese'&&cs?.languages?.includes('ja')||['utenti','recensione'].includes(sentiment)&&cs?.kinds?.includes(sentiment)||sentiment==='positive'&&['positivo','molto-positivo'].includes(cs?.tone)||cs?.tone===sentiment||sentiment==='missing'&&(!expansionCode||c.set===expansionCode)&&!c.basic&&['common','uncommon'].includes(c.rarity)&&!cs;
return sm&&(!rating||rating==='diff'&&diff||rating==='nd'&&c.community==null||rating==='combo'&&c.combos?.length>0||rating==='low'&&c.score!=null&&c.score<=2||['3','4'].includes(rating)&&c.score>=Number(rating))&&(!$('catalog-type').value||cardTypes(c).includes($('catalog-type').value))&&rangeMatches(c.mv,'mana-min','mana-max')&&rangeMatches(c.community,'review-min','review-max')&&rangeMatches(wr,'wr-min','wr-max')&&(!reviews||(reviews==='present'?c.community!=null:c.community==null))&&(!wrData||(wrData==='present'?wr!=null:wr==null))&&(!tier||tier==='ranked'&&r?.tier!=null||tier==='low'&&r?.status==='low_match_volume'||tier==='missing'&&!r||r?.tier===tier)}
function compareOptional(a,b,direction=1){if(a==null)return b==null?0:1;if(b==null)return -1;return (a-b)*direction}
function compareCards(a,b,order){const name=a.name.localeCompare(b.name,'it');let result=0;
if(order.startsWith('untapped'))result=compareOptional(a.untappedPickOrder?.tierOrder,b.untappedPickOrder?.tierOrder,order==='untapped' ? 1:-1);
else if(order==='wr'||order==='wr-asc')result=compareOptional(winRate(a),winRate(b),order==='wr'?-1:1);
else if(order==='community'||order==='community-asc')result=compareOptional(a.community,b.community,order==='community'?-1:1);
else if(order==='mana'||order==='mana-desc')result=compareOptional(a.mv,b.mv,order==='mana'?1:-1);
else if(order==='color')result=['W','U','B','R','G','M','C','L'].indexOf(group(a))-['W','U','B','R','G','M','C','L'].indexOf(group(b));
else if(order==='type')result=(cardTypes(a).map(t=>CATALOG_TYPES[t]).sort().join(', ')||a.type).localeCompare(cardTypes(b).map(t=>CATALOG_TYPES[t]).sort().join(', ')||b.type,'it');
else if(order==='score')result=compareOptional(a.score,b.score,-1);
else if(order==='sentiment')result=compareOptional(a.sentiment?.index,b.sentiment?.index,-1);
else if(order==='combo')result=compareOptional(a.comboScore,b.comboScore,-1)||compareOptional(a.comboFamilies,b.comboFamilies,-1);
else if(order!=='name')result=a.set.localeCompare(b.set)||a.number-b.number;
return result||name}

const ids=['rating','catalog-sentiment','catalog-type','catalog-tier','review-data','wr-data','mana-min','mana-max','review-min','review-max','wr-min','wr-max'];
const hasScore=DATA.cards.some(c=>c.score!=null),hasSentiment=DATA.cards.some(c=>c.sentiment),hasCombos=DATA.cards.some(c=>c.combos?.length);
const hasRank=DATA.cards.some(c=>c.untappedPickOrder?.tier!=null),hasWR=DATA.cards.some(c=>winRate(c)!=null),hasReviews=DATA.cards.some(c=>c.community!=null);
function mount(target,order){
 target.innerHTML="<div class=\"catalog-extra-filters\"><label>Valutazione Sealed<select id=\"rating\" aria-label=\"Filtro valutazione\"><option value=\"\">Tutte le valutazioni</option><option value=\"4\">Sealed ≥ 4 stelle</option><option value=\"3\">Sealed ≥ 3 stelle</option><option value=\"low\">Sealed ≤ 2 stelle</option><option value=\"diff\">Voti discordanti</option><option value=\"nd\">Senza voto esterno</option><option value=\"combo\">Con combo catalogate</option></select></label><label>Sentiment<select id=\"catalog-sentiment\" aria-label=\"Filtra sentiment\"><option value=\"\">Tutti i sentiment</option><option value=\"covered\">Con sentiment</option><option value=\"regional\">Fonti regionali</option><option value=\"updated\">Ricerca aggiornata</option><option value=\"utenti\">Feedback utenti</option><option value=\"recensione\">Recensioni</option><option value=\"japanese\">Con fonti giapponesi</option><option value=\"european\">Con fonti FR / DE</option><option value=\"positive\">Positivo / molto positivo</option><option value=\"misto\">Misto</option><option value=\"condizionato\">Condizionato</option><option value=\"sideboard\">Sideboard</option><option value=\"missing\">Comuni / non comuni senza sintesi</option></select></label>\n<label>Tipo di carta<select id=\"catalog-type\"><option value=\"\">Tutti i tipi</option></select></label>\n<fieldset><legend>Valore di mana</legend><label>Minimo<input id=\"mana-min\" type=\"number\" min=\"0\" step=\"0.5\" placeholder=\"Qualsiasi\"></label><label>Massimo<input id=\"mana-max\" type=\"number\" min=\"0\" step=\"0.5\" placeholder=\"Qualsiasi\"></label></fieldset>\n<fieldset><legend>Recensioni, stelle su 5</legend><label>Minimo<input id=\"review-min\" type=\"number\" min=\"0\" max=\"5\" step=\"0.25\" placeholder=\"Qualsiasi\"></label><label>Massimo<input id=\"review-max\" type=\"number\" min=\"0\" max=\"5\" step=\"0.25\" placeholder=\"Qualsiasi\"></label><label>Copertura<select id=\"review-data\"><option value=\"\">Tutte</option><option value=\"present\">Con recensioni</option><option value=\"missing\">Senza recensioni</option></select></label></fieldset>\n<label>Ranking Draft Untapped<select id=\"catalog-tier\"><option value=\"\">Tutti i tier</option><option value=\"ranked\">Con tier</option><option value=\"low\">Campione insufficiente</option><option value=\"missing\">Non presente nella fonte</option></select></label>\n<fieldset id=\"wr-filters\"><legend>WR in mano Untapped, %</legend><label>Minima<input id=\"wr-min\" type=\"number\" min=\"0\" max=\"100\" step=\"0.1\" placeholder=\"Qualsiasi\"></label><label>Massima<input id=\"wr-max\" type=\"number\" min=\"0\" max=\"100\" step=\"0.1\" placeholder=\"Qualsiasi\"></label><label>Copertura<select id=\"wr-data\"><option value=\"\">Tutte</option><option value=\"present\">Con WR</option><option value=\"missing\">Senza WR</option></select></label></fieldset>\n</div>";
 order.innerHTML="<option value=\"set\">Ordine del set</option><option value=\"color\">Colore</option><option value=\"type\">Tipo di carta</option><option value=\"untapped\">Ranking Draft: S → F</option><option value=\"untapped-reverse\">Ranking Draft: F → S</option><option value=\"wr\">WR in mano Untapped ↓</option><option value=\"wr-asc\">WR in mano Untapped ↑</option><option value=\"score\">Valutazione Sealed ↓</option><option value=\"community\">Recensioni ↓</option><option value=\"community-asc\">Recensioni ↑</option><option value=\"sentiment\">Indice sentiment ↓</option><option value=\"combo\">Valore di sinergia ↓</option><option value=\"mana\">Valore di mana ↑</option><option value=\"mana-desc\">Valore di mana ↓</option><option value=\"name\">Nome A–Z</option>";
 for(const [type,label] of Object.entries(CATALOG_TYPES))if(DATA.cards.some(c=>cardTypes(c).includes(type))){const option=document.createElement('option');option.value=type;option.textContent=label;$('catalog-type').append(option)}
 for(const tier of TIERS){const option=document.createElement('option');option.value=tier;option.textContent='Tier '+tier;option.disabled=!DATA.cards.some(c=>c.untappedPickOrder?.tier===tier);$('catalog-tier').append(option)}
 const availability={untapped:hasRank,'untapped-reverse':hasRank,wr:hasWR,'wr-asc':hasWR,community:hasReviews,'community-asc':hasReviews,score:hasScore,sentiment:DATA.cards.some(c=>c.sentiment?.index!=null),combo:hasCombos};
 for(const [key,available] of Object.entries(availability)){const option=order.querySelector(`[value="${key}"]`);option.disabled=!available;option.hidden=!available;if(!available)option.textContent+=' (dati assenti)'}
 for(const id of ['review-min','review-max'])$(id).disabled=!hasReviews;
 for(const id of ['wr-min','wr-max'])$(id).disabled=!hasWR;
 $('catalog-tier').querySelector('[value="ranked"]').disabled=!hasRank;
 $('catalog-tier').querySelector('[value="low"]').disabled=!DATA.cards.some(c=>c.untappedPickOrder?.status==='low_match_volume');
 for(const value of ['3','4','low'])$('rating').querySelector(`[value="${value}"]`).disabled=!hasScore;
 $('rating').querySelector('[value="combo"]').disabled=!hasCombos;
 $('rating').querySelector('[value="diff"]').disabled=!DATA.cards.some(c=>(c.evidence||[]).length>1);
 for(const option of $('catalog-sentiment').options)if(option.value&&option.value!=='missing')option.disabled=!hasSentiment;
 $('review-data').querySelector('[value="present"]').disabled=!hasReviews;
 $('wr-data').querySelector('[value="present"]').disabled=!hasWR;
 const missing=[!hasReviews&&'recensioni',!hasRank&&'ranking Draft',!hasWR&&'WR in mano',!hasScore&&'valutazioni Sealed',!hasSentiment&&'sentiment'].filter(Boolean);
 const status=document.createElement('p');status.id='catalog-data-status';status.className='catalog-data-status';status.textContent=missing.length?'Dati non disponibili: '+missing.join(', ')+'. Le valutazioni mancanti restano N/D.':'';target.append(status);
 // A catalog already inside a filter panel needs no second disclosure level.
 if(!target.closest('details')){
  const filters=target.querySelector('.catalog-extra-filters'),core=document.createElement('div');
  core.className='catalog-core-filters';
  core.append($('catalog-type').closest('label'),$('mana-min').closest('fieldset'));
  const advanced=document.createElement('details'),summary=document.createElement('summary');
  advanced.className='catalog-advanced-filters';summary.textContent='Valutazioni, ranking e WR';
  advanced.append(summary,filters);target.replaceChildren(core,advanced,status);
  if(!hasScore&&!hasCombos)$('rating').closest('label').hidden=true;
  if(!hasSentiment)$('catalog-sentiment').closest('label').hidden=true;
  if(!hasReviews)$('review-min').closest('fieldset').hidden=true;
  if(!DATA.cards.some(c=>c.untappedPickOrder))$('catalog-tier').closest('label').hidden=true;
  if(!hasWR)$('wr-filters').hidden=true;
  advanced.hidden=[...filters.children].every(node=>node.hidden);
 }
 const requested=new URLSearchParams(location.search).get('order');if(requested&&[...order.options].some(o=>o.value===requested&&!o.disabled))order.value=requested;
}
function summary(c){if(!hasReviews&&!hasRank&&!hasWR)return '';const rank=c.untappedPickOrder,row=wrSource.cards[c.id],wr=winRate(c);return `<p class="catalog-metrics">Recensioni: ${c.community==null?'N/D':esc(c.community)+' / 5'}<br>Ranking Draft: ${rank?.tier?'tier '+esc(rank.tier):rank?.status==='low_match_volume'?'campione insufficiente':'N/D'}<br>WR in mano: ${wr==null?'N/D':wr.toLocaleString('it-IT')+'%'}${rank?.retrieved?'<br>Ranking: '+esc(rank.retrieved):''}${row?'<br><a href="'+esc(row.url)+'" target="_blank" rel="noopener">Untapped, '+esc(wrSource.retrieved)+'</a>':''}</p>`}
return {mount,ids,extraMatches,compareCards,winRate,cardTypes,wrSource,hasRank,hasWR,summary,reset(){for(const id of ids)$(id).value=''}};
}};
