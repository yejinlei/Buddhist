#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科判字段归一化：把节点里的 desc 统一为 description，并规范化 meaning_points。
处理对象：kepan/core.json（古德单档） + kepan/shards/*.json
"""
import json, glob, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEPAN_DIR = ROOT / 'kepan'
SHARD_DIR = KEPAN_DIR / 'shards'


def norm_node(n):
    if not isinstance(n, dict):
        return n
    if 'desc' in n:
        if 'description' not in n:
            n['description'] = n.pop('desc')
        else:
            n.pop('desc')
    # 归一 points -> meaning_points（节点级义理要点）
    if 'points' in n and 'meaning_points' not in n:
        n['meaning_points'] = n.pop('points')
    if isinstance(n.get('children'), list):
        n['children'] = [norm_node(c) for c in n['children']]
    return n


def norm_entry(e):
    if isinstance(e.get('kepan'), list):
        e['kepan'] = [norm_node(n) for n in e['kepan']]
    return e


def process(path):
    path = str(path)
    d = json.load(open(path, encoding='utf-8'))
    n = 0
    for k, v in d.items():
        if isinstance(v, dict):
            norm_entry(v)
            n += 1
    with open(path, 'w', encoding='utf-8') as f:
        if path.endswith('core.json'):
            json.dump(d, f, ensure_ascii=False, indent=1)
        else:
            json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
    return n


print("归一 core.json ...")
print("  ", process(KEPAN_DIR / 'core.json'), "部")
for p in sorted(glob.glob(str(SHARD_DIR / 'shard-*.json'))):
    print(f"归一 {os.path.basename(p)} ...", process(p), "部")
print("完成")
