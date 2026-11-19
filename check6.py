
import json, re
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'
skel_base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/'

# 深入核查t1058 seg14和seg22：原文「前身呪」对应modern
print("=== t1058 seg14（索引13） ===")
data = json.load(open(base+'t1058.json'))
o = data['translations'][13]['original_preview']
m = data['translations'][13].get('modern','')
print('orig:', o)
print()
print('modern:', m)
print()

print("=== t1058 seg22（索引21） ===")
o = data['translations'][21]['original_preview']
m = data['translations'][21].get('modern','')
print('orig:', o)
print()
print('modern:', m)
print()

# t1904 找「答言'不作'」所在段——原文里的位置
print("=== t1904：找原文含『答言.*不作』的段 ===")
data = json.load(open(base+'t1904.json'))
for i, seg in enumerate(data['translations']):
    o = seg['original_preview']
    if '答言' in o and '不作' in o:
        m = seg.get('modern','')
        print(f'seg{i+1} orig: ...{o[max(0,o.find("不作")-50):o.find("不作")+30]}...')
        print(f'modern: ...{m[max(0,m.find("不作")-50):m.find("不作")+30]}...')
        print()

# t2069 seg38,39,40,41,42 检查乾淑/赞宁区分
print("=== t2069 seg38-44（索引37-43）modern开头 ===")
data = json.load(open(base+'t2069.json'))
for idx in range(37, min(44, len(data['translations']))):
    m = data['translations'][idx].get('modern','')
    o = data['translations'][idx]['original_preview']
    print(f'seg{idx+1} modern[:200]: {m[:200]}')
    print()
