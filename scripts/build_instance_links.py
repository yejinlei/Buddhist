#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打通义理本体的两拨实例：生成「义理 ↔ 文本」双向链接索引。

输入:
  ontology/instances/shards/*.json   —— 全量文本本体(2506 部经的标引)
  data/concepts-expanded.json        —— 义理概念实例(c###)
  data/persons-expanded.json         —— 人物实例(p###)
  data/sects-expanded.json           —— 宗派实例(sec###)

输出:
  ontology/instance-links.json       —— concept/figure/school/category → 经 列表
                                        以及 text → 其所标引的概念/人物/宗派

用法: python3 scripts/build_instance_links.py
"""
import glob
import json
import os
import datetime
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'ontology', 'instance-links.json')


def main():
    concepts = {c['id']: c for c in json.load(open(os.path.join(ROOT, 'data', 'concepts-expanded.json')))['concepts']}
    persons = {p['id']: p for p in json.load(open(os.path.join(ROOT, 'data', 'persons-expanded.json')))['persons']}
    sects = {s['id']: s for s in json.load(open(os.path.join(ROOT, 'data', 'sects-expanded.json')))['sects']}
    sutras = {s['id']: s for s in json.load(open(os.path.join(ROOT, 'data', 'sutras-expanded.json')))['sutras']}

    concept_texts = defaultdict(list)
    figure_texts = defaultdict(list)
    school_texts = defaultdict(list)
    category_texts = defaultdict(list)
    text_index = {}
    total = 0

    for f in sorted(glob.glob(os.path.join(ROOT, 'ontology', 'instances', 'shards', 'shard-*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        for tid, v in d.items():
            total += 1
            cs = [m['concept_id'] for m in v.get('doctrine_mentions', [])]
            fs = [m['figure_id'] for m in v.get('figure_mentions', [])]
            sch = v.get('belongs_to_school', []) or []
            cat = v.get('category')
            for c in cs:
                concept_texts[c].append(tid)
            for p in fs:
                figure_texts[p].append(tid)
            for s in sch:
                school_texts[s].append(tid)
            if cat:
                category_texts[cat].append(tid)
            text_index[tid] = {
                'title': v.get('title'),
                'category': cat,
                'vehicle': v.get('vehicle'),
                'schools': sch,
                'concepts': cs,
                'figures': fs,
            }

    def pack(ids, names):
        out = {}
        for k, lst in ids.items():
            nm = names.get(k, {})
            out[k] = {
                'name': nm.get('name', k),
                'count': len(lst),
                'texts': lst,
            }
        return out

    result = {
        'meta': {
            'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ontology_version': '3.0.0',
            'structure': '四轴 × 七层',
            'total_texts': total,
            'concepts_with_texts': len(concept_texts),
            'figures_with_texts': len(figure_texts),
            'schools_with_texts': len(school_texts),
            'categories_with_texts': len(category_texts),
            'events': 0,
            'note': 'concept/figure id 与 data/*-expanded.json 完全对齐，无悬空引用。事件轴（DharmaAssembly/StoryEvent/TransmissionEvent/Council）实例待 M4 填充，当前 events=0。',
        },
        'concept': pack(concept_texts, concepts),
        'figure': pack(figure_texts, persons),
        'school': pack(school_texts, sects),
        'category': pack(category_texts, {}),
        'text': text_index,
        'all_concepts': [{'id': c['id'], 'name': c['name'], 'layer': c.get('layer'),
                          'sutra_source': c.get('sutra_source')} for c in concepts.values()],
        'all_figures': [{'id': p['id'], 'name': p['name'], 'category': p.get('category')} for p in persons.values()],
        'all_sutras': [{'id': s['id'], 'name': s['name'], 'taisho_id': s.get('taisho_id')} for s in sutras.values()],
    }

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, separators=(',', ':'))

    print('导出:', os.path.relpath(OUT, ROOT), os.path.getsize(OUT), 'bytes')
    print('stats:', json.dumps(result['meta'], ensure_ascii=False))


if __name__ == '__main__':
    main()
