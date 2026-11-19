import json
path = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/t1278.json'
with open(path,'r',encoding='utf-8') as f:
    data=json.load(f)
# seg 9
for idx in [8, 9, 14, 18]:
    seg=data['translations'][idx]
    print(f'=== Seg {idx+1} ===')
    print('ORIG:', seg['original_preview'][:300])
    print()
    body='\n'.join([l for l in seg['modern'].split('\n') if l.strip()][2:])
    print('MODERN body:', body[:400])
    print()
