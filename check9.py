
import json
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'

# 精准看t1058 seg14 原文中「前身呪」位置
data = json.load(open(base+'t1058.json'))
o = data['translations'][13]['original_preview']
m = data['translations'][13].get('modern','')
# 找「前身呪」在原文中的位置
p = o.find('前身呪')
print('orig中「前身呪」上下文:')
print(repr(o[max(0,p-60):p+80]))
print()
# 看modern中对应位置
# 「屈二頭指押二大母指甲上，其頭指甲背相著，用前身呪」——modern里译成什么？
mp = m.find('两个食指的指甲背相靠')
print('modern对应处:')
print(repr(m[mp:mp+120]))
print()

# t1243段12：需要确认段号——段12是索引11还是其他？因为前面说「段12」，我们看原文中包含陀罗尼的段落
data = json.load(open(base+'t1243.json'))
print("=== t1243所有段的orig开头30字+modern长度 ===")
for i, seg in enumerate(data['translations']):
    o = seg['original_preview']
    m = seg.get('modern','')
    has_dh = '二合' in o or '反）' in o or '呪曰' in o or '真言' in o
    print(f'seg{i+1} (modern_len={len(m)}, 梵字/陀罗尼特征={has_dh}): {o[:40].replace(chr(10)," ")}')

print()
# t1080段1
print("=== t1080段1 ===")
data = json.load(open(base+'t1080.json'))
o = data['translations'][0]['original_preview']
m = data['translations'][0].get('modern','')
print(f'orig[:300]: {o[:300]}')
print(f'modern: {m}')
print()

# t1069段23
print("=== t1069段23（索引22）===")
data = json.load(open(base+'t1069.json'))
o = data['translations'][22]['original_preview']
m = data['translations'][22].get('modern','')
print(f'orig: {o}')
print(f'modern: {m}')
