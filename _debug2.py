import json
path = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/t0843.json'
with open(path,'r',encoding='utf-8') as f:
    data=json.load(f)
seg = data['translations'][124]  # seg125
body = '\n'.join([l for l in seg['modern'].split('\n') if l.strip()][2:])
# 找 罗 和 诃
for ch in ['罗','诃','訶','羅']:
    for i,c in enumerate(body):
        if c == ch:
            ctx = body[max(0,i-6):i+7]
            print(f'  pos {i} "{ch}": ...{ctx}...')
