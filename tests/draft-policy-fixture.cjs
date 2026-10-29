'use strict';
const make=(id,extra={})=>({id,name:id,full:id,type:'Creature',score:3,colors:['W'],identity:['W'],cost:'{1}{W}',mv:2,creature:true,land:false,basic:false,rarity:'common',oracle:'',archetypes:[],...extra});
function fixture(){
 const cards=[make('early'),make('late',{mv:6,cost:'{5}{W}',score:3.2}),make('filler',{mv:4,cost:'{3}{W}',score:2}),
  make('defender',{oracle:'Defender',score:3}),make('answer',{creature:false,type:'Instant',oracle:'Destroy target creature.',score:3.1}),
  make('blue',{colors:['U'],cost:'{1}{U}'}),make('red',{colors:['R'],cost:'{3}{R}',mv:4,score:4.8}),
  make('inaccessible',{colors:['G'],cost:'{5}{G}',mv:6,oracle:'{T}: Add one mana of any color.'}),
  make('cycler',{colors:['U'],cost:'{5}{U}',mv:6,oracle:'Mountaincycling {2}'}),
  make('basic-cycler',{colors:['U'],cost:'{5}{U}',mv:6,oracle:'Basic landcycling {2}'}),
  make('typed-dual',{colors:[],cost:'',mv:0,type:'Land - Plains Mountain',land:true,creature:false,score:3}),
  make('red-base',{colors:[],cost:'',mv:0,type:'Basic Land - Mountain',land:true,basic:true,creature:false,score:null}),
  make('enabler',{oracle:'When this creature enters, you gain 2 life.'}),
  make('payoff',{oracle:'Whenever you gain life, draw a card.',score:3.5}),
  make('consumer',{oracle:'Exile a card from your graveyard: Draw a card.',score:3.5}),
  make('resource',{oracle:'Mill three cards.'}),
  make('sideboard',{creature:false,type:'Instant',oracle:'Destroy target artifact.',score:2}),
  make('variable',{cost:'{X}{W}',mv:1}),make('reducer',{cost:'{8}{W}',mv:9,oracle:'This spell costs {X} less to cast.'})];
 const profiles=Object.fromEntries(cards.map(c=>[c.id,{
  status:'supported',roles:[c.land?'land':c.creature?'creature':'spell',...(['answer','sideboard'].includes(c.id)?['interaction']:[]),...(c.id==='sideboard'?['sideboard']:[])],
  symbols:[...c.cost.matchAll(/\{([^}]+)\}/g)].map(x=>x[1]),variable:c.id==='variable',
  mana:{abilities:c.id==='inaccessible'?[{colors:[...'WUBRG'],activation:'{T}',restricted:false}]:c.land?[{colors:c.id==='typed-dual'?['W','R']:['R'],activation:'{T}',restricted:false}]:[],
   cycling:['cycler','basic-cycler'].includes(c.id)?[{kind:c.id==='cycler'?'subtype':'basic',type:c.id==='cycler'?'Mountain':'Basic Land',cost:'{2}'}]:[],
   subtypes:c.id==='typed-dual'?['Plains','Mountain']:c.id==='red-base'?['Mountain']:[],tapped:false,conditional:false},
  curve:{nominal:c.mv,reduction:c.id==='reducer',defensive:c.id==='defender',attacker:c.creature&&c.id!=='defender'},
  reference:{status:'supported',context:'ordinary support'},
  synergy:{status:'supported',enablers:c.id==='enabler'?{life:1}:c.id==='resource'?{grave:1}:{},payoffs:c.id==='payoff'?{life:1}:c.id==='consumer'?{grave:1}:{}},
  provenance:{kind:'handwritten-strategic-fixture',version:1}
 }]));
 const format={id:'fixture',revision:'fixture-1',seats:8,rounds:3,packSize:14,picksPerTurn:1,directions:[1,-1,1],
  archetypes:{WU:{},WB:{},WR:{},WG:{},UB:{},UR:{},UG:{},BR:{},BG:{},RG:{}},cards,
  collation:{schemaVersion:1,groups:{all:cards.filter(c=>!c.land).map(c=>c.id)},partners:[],recipe:[{id:'common',op:'draw',count:14,branches:[{group:'all',weight:1}]}]},
  botPolicy:{schemaVersion:1,revision:'fixture-policy-1',algorithmRevision:'fixture-algorithm-1',available:true,status:'experimental',minDeckSize:40,allowedBasics:[...'WUBRG'],extraBasicLands:true,match:'BO3',maxCopies:null,
   profiles,coverage:{synergies:true},gaps:[],relations:[{id:'life',referenceSupport:3,saturation:8,strength:.8},
    {id:'grave',referenceSupport:3,saturation:8,strength:.8,resource:'graveyard',resourceBudget:4}]}};
 return format;
}
module.exports={fixture,make};
