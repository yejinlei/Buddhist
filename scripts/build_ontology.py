#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从权威主档 ontology/ontology.yaml 导出前端可消费的 JSON。

产物:
  data/ontology-schema.json  —— 主档的 JSON 镜像(含 stats), 供页面渲染
  data/ontology-meta.json    —— 轻量统计, 供首页/导航读取

用法: python3 scripts/build_ontology.py
"""
import json
import os
import datetime

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'ontology', 'ontology.yaml')
OUT_SCHEMA = os.path.join(ROOT, 'data', 'ontology-schema.json')
OUT_META = os.path.join(ROOT, 'data', 'ontology-meta.json')


def count_classes(items):
    n = 0
    for c in items:
        n += 1
        n += count_classes(c.get('subclasses', []) or [])
    return n


def main():
    with open(SRC, encoding='utf-8') as f:
        od = yaml.safe_load(f)

    classes = od.get('classes', []) or []
    relations = od.get('relations', {}) or {}
    properties = od.get('properties', []) or []
    datasets = od.get('datasets', []) or []

    rel_flat = []
    for group, items in relations.items():
        for r in items or []:
            r = dict(r)
            r['group'] = group
            rel_flat.append(r)

    axes = od.get('axes', []) or []
    process = (od.get('meta', {}).get('process') or {})

    stats = {
        'axes': len(axes),
        'layers': len(od.get('layers', []) or []),
        'classes': count_classes(classes),
        'class_roots': len(classes),
        'properties': len(properties),
        'relations': len(rel_flat),
        'relation_groups': len(relations),
        'datasets': len(datasets),
    }

    out = {
        'meta': od.get('meta', {}),
        'axes': axes,
        'layers': od.get('layers', []),
        'classes': classes,
        'properties': properties,
        'relations': relations,
        'relations_flat': rel_flat,
        'datasets': datasets,
        'process': process,
        'fixes': od.get('fixes', []),
        'stats': stats,
        'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    with open(OUT_SCHEMA, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    with open(OUT_META, 'w', encoding='utf-8') as f:
        json.dump({
            'name': od.get('meta', {}).get('name'),
            'version': od.get('meta', {}).get('version'),
            'structure': od.get('meta', {}).get('structure'),
            'namespace': od.get('meta', {}).get('namespace'),
            'stats': stats,
            'axes': [{'id': a['id'], 'name': a['name'], 'key': a['key']} for a in axes],
            'layers': [{'id': l['id'], 'name': l['name'], 'key': l['key']} for l in od.get('layers', [])],
            'generated_at': out['generated_at'],
        }, f, ensure_ascii=False, indent=2)

    print('导出完成:', os.path.relpath(OUT_SCHEMA, ROOT), os.path.relpath(OUT_META, ROOT))
    print('stats:', json.dumps(stats, ensure_ascii=False))


if __name__ == '__main__':
    main()
