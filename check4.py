
import json
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'

# 1. t1058段10（索引9）：前身咒
print("=== t1058 段9-11（索引8,9,10）原文与译文 ===")
data = json.load(open(base+'t1058.json'))
for idx in [8,9,10]:
    o = data['translations'][idx]['original_preview']
    m = data['translations'][idx].get('modern','')
    print(f'--- seg{idx+1} orig ---')
    print(o[:300])
    print(f'--- seg{idx+1} modern ---')
    print(m[:500])
    print()
