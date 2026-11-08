# -*- coding: utf-8 -*-
"""第60批：将精译内容写入 data/modern-translation/<tid>.json
严格保证 original_preview 取自骨架（=原文连续子串，一字不动）。
"""
import json, os, sys, glob
ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ROOT)   # buddhist-ontology
sys.path.insert(0, os.path.join(ROOT, '_b60'))

import data_part1, data_part2, data_part3
ALL = {}
for m in (data_part1, data_part2, data_part3):
    ALL.update(m.T)

TASK = os.path.join(ROOT, 'data', 'baihua-tasks')
OUT  = os.path.join(ROOT, 'data', 'modern-translation')

def build(tid):
    sk = json.load(open(os.path.join(TASK, tid + '.json'), encoding='utf-8'))
    segs = sk['translations']
    tr = ALL[tid]
    assert len(tr) == len(segs), f'{tid}: 数据段数 {len(tr)} != 骨架段数 {len(segs)}'
    out_trans = []
    for i, (sk_seg, (sec, modern)) in enumerate(zip(segs, tr)):
        out_trans.append({
            'section': sec,
            'original_preview': sk_seg['original_preview'],   # 骨架原文，一字不动
            'modern': '【%s】%s' % (sec, modern),
        })
    obj = {
        'id': tid,
        'title': sk.get('title', ''),
        'translator': sk.get('translator', ''),
        'mode': 'baihua',
        'intro': '',
        'sutraPath': '../sutras/%s.json' % tid,
        'translations': out_trans,
    }
    json.dump(obj, open(os.path.join(OUT, tid + '.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return len(out_trans)

if __name__ == '__main__':
    tids = sys.argv[1:] or sorted(ALL.keys())
    for tid in tids:
        n = build(tid)
        print(f'{tid}  写入 {n} 段')
