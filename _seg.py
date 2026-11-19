import json
path = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/t0843.json'
with open(path,'r',encoding='utf-8') as f:
    data=json.load(f)
for idx in [123,124]:
    seg=data['translations'][idx]
    print(f'=== Seg {idx+1} ===')
    print('ORIG:', seg['original_preview'][:400])
    print()
    print('MODERN:', seg['modern'][:600])
    print()
