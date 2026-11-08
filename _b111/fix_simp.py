# -*- coding: utf-8 -*-
import json, re, os
from opencc import OpenCC
cc = OpenCC('t2s')
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
B = "t1361 t1465 t1879b t2760 t0741 t1637 t1628 t1609 t1930 t0277 t0730 t0350".split()

def simp(s):
    parts = re.split(r'(⟪[^⟫]*⟫)', s)
    return ''.join(p if p.startswith('⟪') else cc.convert(p) for p in parts)

for tid in B:
    fp = os.path.join(ROOT, 'data/modern-translation', tid + '.json')
    d = json.load(open(fp, encoding='utf-8'))
    ch = 0
    for t in d['translations']:
        nm = simp(t['modern'])
        if nm != t['modern']:
            ch += 1
        t['modern'] = nm
        mm = re.match(r'(【[^】]+】)', nm)
        if mm:
            t['section'] = mm.group(1)
    ni = simp(d.get('intro', ''))
    if ni != d.get('intro', ''):
        d['intro'] = ni
    json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(tid, 'modern改段=', ch)

print("=== t1930 段18-19, 21-22 ===")
d = json.load(open(os.path.join(ROOT, 'data/modern-translation/t1930.json'), encoding='utf-8'))
for i in [17, 18, 20, 21]:
    print(f"--[{i}]--\nOP: {d['translations'][i]['original_preview'][:120]}\nMD: {d['translations'][i]['modern']}")
print("=== t0350 段52-54, 62-64 ===")
d = json.load(open(os.path.join(ROOT, 'data/modern-translation/t0350.json'), encoding='utf-8'))
for i in [51, 52, 53, 61, 62, 63]:
    print(f"--[{i}]--\nOP: {d['translations'][i]['original_preview'][:120]}\nMD: {d['translations'][i]['modern']}")
