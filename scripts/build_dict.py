#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建佛学大词典数据"""
import json, os
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. 本体数据（JS文件，提取const ontologyData = {...}部分）
import re
onto_path = os.path.join(BASE, 'js', 'ontology-data.js')
raw = open(onto_path, 'r', encoding='utf-8').read()
m = re.search(r'const\s+ontologyData\s*=\s*(\{.*?\});\s*$', raw, re.S)
if not m:
    raise RuntimeError('ontologyData not found')
onto = json.loads(m.group(1))
concepts = {c['name']: {'name': c['name'], 'type': '义理概念', 'layer': c.get('layer',''),
                         'desc': c.get('desc', c.get('description','')), 'source': '佛学本体库'}
            for c in onto.get('concepts', [])}
persons = {p['name']: {'name': p['name'], 'type': '人物',
                        'desc': p.get('desc', p.get('description','')), 'source': '佛学本体库'}
           for p in onto.get('persons', [])}
sutras = {s['name']: {'name': s['name'], 'type': '经论',
                       'desc': s.get('desc', s.get('description','')), 'source': '佛学本体库'}
          for s in onto.get('sutras', [])}
print(f"本体: 概念{len(concepts)} 人物{len(persons)} 经典{len(sutras)}")

all_terms = {}
all_terms.update(concepts)
all_terms.update(persons)
all_terms.update(sutras)

# 2. 读取外部术语列表文件
TERMS_FILE = os.path.join(BASE, 'scripts', 'dict_terms.json')
if os.path.exists(TERMS_FILE):
    extra = json.load(open(TERMS_FILE, 'r', encoding='utf-8'))
    print(f"外部术语文件: {len(extra)} 条")
    for k, v in extra.items():
        v.setdefault('name', k)
        v.setdefault('source', '佛学大词典')
        all_terms[k] = v

out = sorted(all_terms.values(), key=lambda x: x['name'])

data_dir = os.path.join(BASE, 'data')
os.makedirs(data_dir, exist_ok=True)
dict_path = os.path.join(data_dir, 'buddhist_dict.json')
with open(dict_path, 'w', encoding='utf-8') as f:
    json.dump({
        'meta': {
            'name': '佛学大词典',
            'sources': ['丁福保《佛学大辞典》(1922)精选', '佛学本体库义理概念', '佛学常见辞汇'],
            'total': len(out),
            'version': '1.0'
        },
        'terms': out
    }, f, ensure_ascii=False)
print(f"✅ 写入 {dict_path}：{len(out)} 条")

# 首字索引
char_index = defaultdict(list)
for i, t in enumerate(out):
    if t['name']:
        char_index[t['name'][0]].append(i)
idx_path = os.path.join(data_dir, 'dict_index.json')
with open(idx_path, 'w', encoding='utf-8') as f:
    json.dump({'first_char': {k: v for k, v in sorted(char_index.items())}}, f, ensure_ascii=False)
print(f"✅ 首字索引: {len(char_index)} 个首字")
