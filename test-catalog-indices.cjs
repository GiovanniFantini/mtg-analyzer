'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const elements={};const ctx={window:{},document:{getElementById:id=>elements[id]}};
vm.createContext(ctx);vm.runInContext(fs.readFileSync('competitive-prospects-ui.js','utf8'),ctx);ctx.TournamentProspects=ctx.window.TournamentProspects;vm.runInContext(fs.readFileSync('catalog-indices.js','utf8'),ctx);
const cards=[{id:'one',legalities:{standard:'legal',modern:'banned',pauper:'not_legal'},prospects:{date:'2026-10-28',formats:{standard:{legality:'legal',evidence:'liste_documentate',prospect:'prime_presenze'},modern:{legality:'legal',evidence:'liste_documentate',prospect:'adozione_ripetuta'}}}},{id:'two',legalities:{standard:'legal'},prospects:{date:'2026-10-28',formats:{commander:{evidence:'inclusioni_documentate',prospect:'adozione_documentata'}}}}];
const indices=ctx.window.CatalogIndices.create({cards,catalogPerformance:{draft:[{id:'premier',cards:{one:{value:0,games:200},two:{value:null,games:3}}},{id:'traditional',cards:{one:{value:72,games:100}}}],sealed:[{id:'sealed',cards:{one:{value:60,games:400}}}]}});
assert.equal(indices.rate(cards[0]),0);assert.equal(indices.rate(cards[1]),null);assert.equal(indices.rate(cards[0],'sealed'),60);
elements['draft-wr-source']={value:'traditional'};assert.equal(indices.rate(cards[0]),72);assert.equal(indices.rate(cards[0],'sealed'),60);
assert.equal(indices.assessment(cards[0],'standard').rank,1);assert.equal(indices.assessment(cards[0],'modern').rank,null);assert.equal(indices.assessment(cards[0],'modern').state,'not_legal');assert.equal(indices.assessment(cards[0],'pauper').state,'not_legal');
assert.equal(indices.assessment(cards[1],'standard').state,'missing');assert.equal(indices.assessment(cards[1],'standard').date,null);assert.equal(indices.assessment(cards[1],'standard').rank,null,'Commander adoption must not become Standard evidence');
console.log('PASS: event separation, zero/null, current bans, missing format assessments and Commander isolation');
vm.runInContext(fs.readFileSync('prospects-ui.js','utf8'),ctx);
const details=ctx.window.CardProspects.render({prospects:{date:'2026-10-28',formats:{standard:{legality:'legal',evidence:'liste_documentate',prospect:'prime_presenze'}},sources:[],limitations:[]}});
assert.ok(details.includes('<th>Prospettiva</th>'));assert.ok(details.includes('<td>Prime presenze</td>'));
console.log('PASS: attributed prospects remain visible in the format details table');

const observed={id:'measured',legalities:{standard:'legal'},prospects:{date:'2026-10-22',formats:{standard:{evidence:'non_documentata',prospect:'da_verificare',tournamentIndex:{score:0,date:'2026-10-28',status:'not_observed',legality:'legal',reason:null,sample:{decks:100},observed:{withCard:0,eventsWithCard:0}}}}}};
const newer=ctx.window.CatalogIndices.create({cards:[observed]});assert.equal(newer.assessment(observed,'standard').rank,0);assert.equal(newer.assessment(observed,'standard').state,'not_observed');observed.prospects.formats.standard.tournamentIndex.score=20;observed.prospects.formats.standard.tournamentIndex.status='repeated';assert.equal(newer.assessment(observed,'standard').rank,20);assert.equal(newer.assessment(observed,'standard').state,'documented');
console.log('PASS: measured tournament share overrides ordinal legacy ranks while preserving observed zero');
