"""Build-time execution checks for the supported recipe operations, without Node."""
import random


def validate_samples(spec, printings, pack_size):
    """Check reproducible and forced positive-probability paths, not estimated rates."""
    rng=random.Random(0)
    partners=dict(spec.get('partners',[]))
    partners.update({b:a for a,b in spec.get('partners',[])})
    rules={rule['id']:rule for rule in spec['recipe']}

    def pack(forced=None, replacements=None):
        forced=forced or {}
        result=[];drawn={};sequence=0
        for rule in spec['recipe']:
            if rule['op']=='replace':
                chance=rule['chance']
                active=rng.random()<chance if replacements is None else chance>0 and (replacements or chance==1)
                if not active:continue
            selected=[]
            for _ in range(rule.get('count',1)):
                if rule['id'] in forced:branch=rule['branches'][forced[rule['id']]]
                else:
                    value=rng.random();branch=rule['branches'][-1]
                    for candidate in rule['branches']:
                        value-=candidate['weight']
                        if value<0:branch=candidate;break
                excluded={printings[id_]['full'] for previous in rule.get('exclude',[]) for _,id_ in drawn.get(previous,[])}
                if rule.get('unique'):excluded.update(printings[id_]['full'] for _,id_ in selected)
                available=[id_ for id_ in spec['groups'][branch['group']] if printings[id_]['full'] not in excluded]
                if not available:raise ValueError('collazione impossibile nello slot '+rule['id']+': gruppo esaurito dopo unique/exclude')
                id_=rng.choice(available)
                ids=[id_,partners[id_]] if rule['op']=='pair' else [id_]
                for chosen in ids:selected.append((sequence,chosen));sequence+=1
            if rule['op']=='replace':
                target=drawn.get(rule['target'],[])
                if len(target)<len(selected):raise ValueError('sostituzione senza carte sufficienti: '+rule['id'])
                removed=set(target[:len(selected)])
                result=[entry for entry in result if entry not in removed]
                drawn[rule['target']]=target[len(selected):]
            drawn[rule['id']]=selected;result.extend(selected)
        if len(result)!=pack_size:raise ValueError('dimensione della busta non valida')

    for _ in range(128):pack()
    for rule in spec['recipe']:
        for index,branch in enumerate(rule['branches']):
            if branch['weight']<=0:continue
            for replacements in (True,False):pack({rule['id']:index},replacements)
            for previous in rule.get('exclude',[]):
                for other,choice in enumerate(rules[previous]['branches']):
                    if choice['weight']>0:
                        for replacements in (True,False):pack({previous:other,rule['id']:index},replacements)
