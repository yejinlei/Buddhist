
import json
base = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/'

# t1243段12（索引11）：原文和modern
print("=== t1243 seg12（索引11）===")
data = json.load(open(base+'t1243.json'))
o = data['translations'][11]['original_preview']
m = data['translations'][11].get('modern','')
print(f'orig: {o}')
print(f'modern: {m}')
print()

# t1080段1已确认没有梵字，段2才是——再看t1080所有段开头找陀罗尼段
print("=== t1080所有段开头 ===")
data = json.load(open(base+'t1080.json'))
for i, seg in enumerate(data['translations']):
    o = seg['original_preview']
    m = seg.get('modern','')
    has_dh = '二合' in o or '反）' in o or '反)' in o
    if has_dh:
        print(f'seg{i+1} (modern_len={len(m)}): {o[:80].replace(chr(10)," ")}')

# t1069段23（索引22）modern里梵字的反切"（二合）"有没有保留？
print()
print("=== t1069 seg23 modern梵字检查 ===")
data = json.load(open(base+'t1069.json'))
m = data['translations'][22].get('modern','')
# 梵字部分
import re
fanqie_mod = re.findall(r'（二合[^）]*）', m)
print(f'modern中二合标记: {fanqie_mod}')
# 原文中的二合
o = data['translations'][22]['original_preview']
fanqie_orig = re.findall(r'（二合[^）]*）', o)
print(f'orig中二合标记: {fanqie_orig}')

# 现在看首轮问题6明确说的是「t1243段12、t1080段1、t1069段23等陀罗尼段落必须从original_preview逐字照录梵字、反切注音，不得有"……"省略」
# t1080段1（索引0）没有梵字，t1080段2（索引1）才是陀罗尼段？
# 看t1080段2（索引1）
print()
print("=== t1080 seg2（索引1）===")
o = data['translations'][1]['original_preview'] if False else json.load(open(base+'t1080.json'))['translations'][1]['original_preview']
m = json.load(open(base+'t1080.json'))['translations'][1].get('modern','')
print(f'orig[:500]: {o[:500]}')
print(f'modern[:800]: {m[:800]}')
fanqie_o = re.findall(r'（[^）]*(?:二合|反)[^）]*）', o)
fanqie_m = re.findall(r'（[^）]*(?:二合|反)[^）]*）', m)
print(f'orig反切数={len(fanqie_o)}, modern反切数={len(fanqie_m)}')
print(f'modern缺的反切: {[x for x in fanqie_o if x not in m][:10]}')
