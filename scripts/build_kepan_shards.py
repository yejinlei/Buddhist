#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科判分片构建器
把全量科判 core.json（2501 部，约 18.8MB）拆成：
  1) kepan/core.json         —— 仅 73 部古德/传统注疏科判（精简，供页面优先加载）
  2) kepan/shard-map.json    —— {id: shard_index}
  3) kepan/shards/shard-XXX.json —— 全量完整科判树（含古德），每片 <= TARGET_MB
  4) kepan/index.json        —— 全量索引（每部摘要，供列表渲染）
"""
import json, os, glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEPAN_DIR = ROOT / 'kepan'
SHARD_DIR = KEPAN_DIR / 'shards'
TARGET_MB = 3.0
TARGET = int(TARGET_MB * 1024 * 1024)

SHARD_DIR.mkdir(parents=True, exist_ok=True)

print("[1/5] 读取全量科判...")
full = json.load(open(KEPAN_DIR / 'core.json', encoding='utf-8'))
print("  部数:", len(full))

# ---------- 1) 古德科判单档 ----------
print("[2/5] 提取古德科判单档...")
ancient = {k: v for k, v in full.items() if v.get('ancient')}
with open(KEPAN_DIR / 'core.json', 'w', encoding='utf-8') as f:
    json.dump(ancient, f, ensure_ascii=False, indent=1)
print("  古德科判:", len(ancient))

# ---------- 2) 全量分片（按 id 升序，贪心分桶） ----------
print("[3/5] 写入分片...")
# 清空旧分片
for old in glob.glob(str(SHARD_DIR / 'shard-*.json')):
    os.remove(old)

ids = sorted(full.keys())
shard_map = {}
shards = []          # [ {id: entry} ]
cur = {}
cur_size = 0
idx = 0
for sid in ids:
    entry = full[sid]
    blob = json.dumps(entry, ensure_ascii=False)
    esize = len(blob.encode('utf-8')) + len(sid) + 6
    if cur and cur_size + esize > TARGET:
        shards.append(cur)
        cur = {}
        cur_size = 0
    cur[sid] = entry
    shard_map[sid] = len(shards)   # 当前正在填充的片索引（shards 已 append 的数量）
    cur_size += esize
if cur:
    shards.append(cur)

max_size = 0
for i, sh in enumerate(shards):
    p = SHARD_DIR / f'shard-{i:03d}.json'
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(sh, f, ensure_ascii=False, separators=(',', ':'))
    sz = p.stat().st_size
    max_size = max(max_size, sz)
    print(f"  {p.name}: {sz/1024/1024:.2f} MB  ({len(sh)} 部)")

with open(KEPAN_DIR / 'shard-map.json', 'w', encoding='utf-8') as f:
    json.dump({'total': len(full), 'shards': len(shards), 'map': shard_map}, f,
              ensure_ascii=False, separators=(',', ':'))

# ---------- 3) 索引 ----------
print("[4/5] 写索引 kepan/index.json...")
index = {
    'meta': {
        'version': '2.0.0-full',
        'total': len(full),
        'ancient': len(ancient),
        'structural': sum(1 for v in full.values() if v.get('auto')),
        'shards': len(shards),
        'updated_at': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M'),
    },
    'sutras': {}
}
for sid, v in full.items():
    kp = v.get('kepan') or []
    cnt = {'序分': 0, '正宗分': 0, '流通分': 0}
    for n in kp:
        t = n.get('type')
        if t in cnt:
            cnt[t] = len(n.get('children') or [])
    index['sutras'][sid] = {
        'title': v.get('title', ''),
        'taisho': v.get('taisho', ''),
        'translator': v.get('translator', ''),
        'juan': v.get('juan', 0),
        'chars': v.get('chars', 0),
        'category': v.get('category', ''),
        'ancient': v.get('ancient', False),
        'auto': v.get('auto', True),
        'points_count': len(v.get('meaning_points') or []),
        'xu': cnt['序分'], 'zheng': cnt['正宗分'], 'liu': cnt['流通分'],
    }
with open(KEPAN_DIR / 'index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, separators=(',', ':'))

print("[5/5] 完成")
print(f"  古德单档 core.json: {(KEPAN_DIR/'core.json').stat().st_size/1024:.0f} KB")
print(f"  分片: {len(shards)} 片，最大 {max_size/1024/1024:.2f} MB")
print(f"  索引 index.json: {(KEPAN_DIR/'index.json').stat().st_size/1024:.0f} KB")
