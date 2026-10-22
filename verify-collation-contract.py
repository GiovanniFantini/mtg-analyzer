"""Cross-check recipe validation against the actual JavaScript pack engine."""
import json
import subprocess
from collation_validation import validate_samples


def draw(id_,group,**extra):
    return {'id':id_,'op':'draw','branches':[{'weight':1,'group':group}],**extra}


cards=[{'id':name,'full':name,'rarity':'common','set':'TST','number':i} for i,name in enumerate('abcdef')]
cases=[
    {'name':'correlated exclusions','valid':True,'packSize':5,'groups':{'ab':['a','b'],'abc':['a','b','c']},'recipe':[
        draw('first','ab'),draw('complement','abc',count=2,unique=True,exclude=['first']),
        draw('same','ab',exclude=['complement']),draw('other','ab',exclude=['first','same'])]},
    {'name':'three distinct pairs from four candidate fronts','valid':True,'packSize':6,'groups':{'pairs':['a','b','c','e']},'partners':[['a','b'],['c','d'],['e','f']],
     'recipe':[{'id':'pairs','op':'pair','count':3,'unique':True,'branches':[{'weight':1,'group':'pairs'}]}]},
    {'name':'exhausted pair group','valid':False,'packSize':3,'groups':{'pairs':['a','b']},'partners':[['a','b']],
     'recipe':[{'id':'pair','op':'pair','branches':[{'weight':1,'group':'pairs'}]},draw('third','pairs',exclude=['pair'])]},
    {'name':'not enough distinct pairs','valid':False,'packSize':4,'groups':{'pairs':['a','b']},'partners':[['a','b']],
     'recipe':[{'id':'pairs','op':'pair','count':2,'unique':True,'branches':[{'weight':1,'group':'pairs'}]}]},
]
formats=[]
for case in cases:
    spec={'schemaVersion':1,'groups':case['groups'],'partners':case.get('partners',[]),'recipe':case['recipe']}
    valid=True
    try:validate_samples(spec,{c['id']:c for c in cards},case['packSize'])
    except ValueError:valid=False
    assert valid==case['valid'],case['name']
    formats.append({'name':case['name'],'valid':case['valid'],'packSize':case['packSize'],'cards':cards,'collation':spec})
script="""
const assert=require('node:assert/strict'),C=require('./collation.js');
for(const data of FORMATS){let seed=1;const rng=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);let valid=true;
try{const collator=C.createCollator(data,rng);for(let i=0;i<512;i++)assert.equal(collator.pack().length,data.packSize);}catch{valid=false;}
assert.equal(valid,data.valid,data.name);}
console.log('PASS: Python validation and JavaScript engine agree on correlated exclusions, feasible pairs and exhausted groups.');
"""
result=subprocess.run(['node','-'],input='const FORMATS='+json.dumps(formats)+';\n'+script,text=True,encoding='utf-8')
raise SystemExit(result.returncode)
