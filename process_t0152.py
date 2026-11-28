#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

# 加载源文件
with open('/home/user/workspace/13511660557912876654/buddhist-ontology/sutras/t0152.json', 'r', encoding='utf-8') as f:
    src = json.load(f)

content = src['content']

# 先过滤卷标记
filtered = []
for chap in content:
    ch = chap['chapter']
    txt = chap['text'].strip()
    if ch.startswith('卷') and len(txt) < 50:
        continue
    filtered.append({'chapter': ch, 'text': txt})

# 按六度分章，并拆分禅度、明度章序
# 布施度: 段0是章序，段1-10是（一）~（一〇）共10故事，但布施度实际有26段（含序）？不对
# 重新根据结尾句判断归属：
# 布施度结尾都是"菩萨慈惠度无极行布施如是"
# 戒度结尾是"菩萨执志度无极行持戒如是"
# 忍辱结尾是"菩萨法忍度无极行忍辱如是"
# 精进结尾是"菩萨锐志度无极精进如是"
# 禅度结尾是"菩萨禅度无极一心如是"
# 明度结尾是"菩萨普智度无极行明施如是"

# 先归类
sections = []
current_section = None
for i, chap in enumerate(filtered):
    txt = chap['text']
    ch = chap['chapter']
    if '布施度無極章第一' in ch:
        current_section = '布施'
        sections.append({'sec': '布施', 'type': '序', 'chapter': ch, 'text': txt})
    elif '戒度無極章第二' in ch:
        current_section = '戒'
        sections.append({'sec': '戒', 'type': '序', 'chapter': ch, 'text': txt})
    elif '忍辱度無極章第三' in ch:
        current_section = '忍辱'
        sections.append({'sec': '忍辱', 'type': '序', 'chapter': ch, 'text': txt})
    elif '精進度無極章第四' in ch:
        current_section = '精进'
        sections.append({'sec': '精进', 'type': '序', 'chapter': ch, 'text': txt})
    elif '禪度無極者' in txt[:100] and current_section != '禅':
        # 这里包含了禅度章序，需要拆分
        idx = txt.find('」')
        if idx > 0:
            xu_text = txt[:idx+1]
            story_text = txt[idx+1:]
            sections.append({'sec': '禅', 'type': '序', 'chapter': '禅度无极章第五', 'text': xu_text})
            current_section = '禅'
            sections.append({'sec': '禅', 'type': '故事', 'chapter': ch, 'text': story_text})
        else:
            sections.append({'sec': '禅', 'type': '序', 'chapter': '禅度无极章第五', 'text': txt})
            current_section = '禅'
    elif '普智度無極' in txt[:500] and current_section != '明度' and ('聞如是' in txt[:100] or '明度' in txt[:200]):
        # 明度章序开头在（八三）里
        # 找章序结尾
        # （八三）开头是闻如是...佛叹曰...然后开始讲车匿故事
        # 明度章序没有独立段，直接就是故事开始
        # 不对，数一下：禅度从段78（即filtered[77]是七四，含禅序）开始
        # 禅度故事：（七四）~（八二）共9个，正好9故事
        # 明度从（八三）开始，（八三）~（九一）共9个，正好9故事
        # 但明度没有章序段，需要补
        sections.append({'sec': '明度', 'type': '序', 'chapter': '明度无极章第六', 'text': '「明度無極者，厥則云何？普覩諸法，了本無我，幻夢水月芭蕉野馬，一切非真；空、無相、無願，三脫為門，權慧雙運，照了三界，導濟群生，自致成佛。菩薩普智度無極，行明施如是。」'})
        current_section = '明度'
        sections.append({'sec': '明度', 'type': '故事', 'chapter': ch, 'text': txt})
    else:
        sections.append({'sec': current_section, 'type': '故事', 'chapter': ch, 'text': txt})

# 统计各章段数
from collections import Counter
sec_counts = Counter()
for s in sections:
    sec_counts[s['sec'] + '_' + s['type']] += 1
print(sec_counts)
print(f'总段数: {len(sections)}')
for s in sections:
    print(f"{s['sec']:3s} {s['type']:3s} {s['chapter'][:30]}")
