# -*- coding: utf-8 -*-
"""把指定译文 modern/intro 中的弯引号 “ ” 规范为 「 」（体例要求：全角「」『』，无半角引号）。
只改引号，不动 original_preview 与其它字符。"""
import json, sys

for tid in sys.argv[1:]:
    p = f'data/modern-translation/{tid}.json'
    d = json.load(open(p, encoding='utf-8'))
    d['intro'] = d['intro'].replace('“', '「').replace('”', '」')
    n = 0
    for s in d['translations']:
        m = s['modern']
        if '“' in m or '”' in m:
            n += m.count('“') + m.count('”')
            s['modern'] = m.replace('“', '「').replace('”', '」')
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(tid, '引号已规范，改动', n)
