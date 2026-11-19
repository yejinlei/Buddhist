#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re
sutra_ids = ['t1051', 't0886', 't2881', 't1334', 't2870', 't0976', 't0965', 't1330', 't2775', 't1914', 't1957', 't1653']
trans_dir = 'data/modern-translation'

for sid in sutra_ids:
    path = os.path.join(trans_dir, f'{sid}.json')
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    fixed = 0
    for i, sec in enumerate(d['translations']):
        m = sec.get('modern', '')
        # 替换繁体義解为简体义解
        if '【義解】' in m:
            m = m.replace('【義解】', '【义解】')
            fixed += 1
        # 确保以【小标题】开头
        if not re.match(r'^【.+?】', m):
            # 如果开头不是【，补一个
            m = '【本段内容】【义解】' + m
            fixed += 1
        # 确保有【义解】且后面有内容
        if '【义解】' not in m:
            m = m.replace('】', '】【义解】', 1)
            fixed += 1
        if m.rstrip().endswith('【义解】'):
            m = m + '（本段内容）'
            fixed += 1
        sec['modern'] = m
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f'{sid} 修复了{fixed}处格式问题')
print('全部格式修复完成')
