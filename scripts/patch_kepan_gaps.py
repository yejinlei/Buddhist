#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科判复审后补丁：
  1. 9 部论典规范三分 type（总序→序分、末品→流通分），缺失分补显式占位；加 genre=论典
  2. 全量义理要点过滤：剔除 source 非 keyword/doctrine 的项（如"重点核心经典"分类标记）
处理对象：kepan/shards/*.json + kepan/core.json
"""
import json, glob, re, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEPAN_DIR = ROOT / 'kepan'
SHARD_DIR = KEPAN_DIR / 'shards'

LUN_IDS = ['t1509', 't1558', 't1568', 't1579', 't1594', 't1851', 't1881', 't1911', 't1931']
XU_NAME = re.compile(r'序|歸敬|归敬|緣起|缘起|總序|总序')
LIU_NAME = re.compile(r'末|結|结|回向|迴向|流通|附錄|附录|破我|結論|结论')


def clean_points(pts):
    return [p for p in (pts or []) if isinstance(p, dict) and p.get('source') in ('keyword', 'doctrine')]


def fix_lun(sid, v):
    kp = v.get('kepan') or []
    if not kp:
        return v
    if sid == 't1579':
        # 瑜伽师地论：唯一节点装了全论，拆为 序分 + 正宗分 + 流通分
        n0 = kp[0]
        v['kepan'] = [
            {'name': '序分——论首', 'type': '序分',
             'description': ('论典体例，论首归敬。' + '弥勒菩萨说、无著菩萨记' + ('，' + v['translator'] + '译' if v.get('translator') else '')),
             'children': []},
            {'name': '正宗分——五分十七地', 'type': '正宗分',
             'description': '本地分（十七地）·摄决择分·摄释分·摄异门分·摄事分',
             'children': n0.get('children') or []},
            {'name': '流通分（论典体例）', 'type': '流通分',
             'description': '论典不设经式流通分；论末以回向付嘱结', 'children': []},
        ]
        v['genre'] = '论典'
        return v
    # 幂等：先移除上次补的占位节点
    kp = [n for n in kp if '（论典体例）' not in (n.get('name') or '')]
    # 论典首节点即"归敬/总纲"，判为序分
    kp[0]['type'] = '序分'
    kp[0].pop('auto', None)
    # 末节点按结劝特征判流通分
    if len(kp) > 1 and LIU_NAME.search(kp[-1].get('name', '')):
        kp[-1]['type'] = '流通分'
    types = [n.get('type') for n in kp]
    if '序分' not in types:
        kp.insert(0, {'name': '序分（论典体例）', 'type': '序分',
                      'description': '论典不设经式序分；论首以归敬、造论意趣起', 'children': []})
    if '流通分' not in types:
        kp.append({'name': '流通分（论典体例）', 'type': '流通分',
                   'description': '论典不设经式流通分；论末以回向付嘱结', 'children': []})
    # 其余无 type / 非三分的中间节点 → 正宗分
    for n in kp:
        if n.get('type') not in ('序分', '正宗分', '流通分'):
            n['type'] = '正宗分'
    v['kepan'] = kp
    v['genre'] = '论典'
    return v


def process(path):
    path = str(path)
    d = json.load(open(path, encoding='utf-8'))
    changed = 0
    for sid, v in d.items():
        if not isinstance(v, dict):
            continue
        # 1) 过滤非法义理要点
        if isinstance(v.get('meaning_points'), list):
            v['meaning_points'] = clean_points(v['meaning_points'])
        # 2) 论典三分规范
        if sid in LUN_IDS:
            fix_lun(sid, v)
            changed += 1
    with open(path, 'w', encoding='utf-8') as f:
        if path.endswith('core.json'):
            json.dump(d, f, ensure_ascii=False, indent=1)
        else:
            json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
    return changed


print("处理 core.json(古德) ...", process(KEPAN_DIR / 'core.json'), "部论典")
for p in sorted(glob.glob(str(SHARD_DIR / 'shard-*.json'))):
    print(f"处理 {os.path.basename(p)} ...", process(p), "部论典")
print("完成")
