#!/usr/bin/env python3
"""批量段对齐：按最长译本字数升序，逐组生成对齐文件，避免长经错配。
- 自动跳过不完整译本（<200 字）
- 自动跳过已有对齐
- 自动过滤标题带"疏/鈔/記/目錄/禮懺"等非经本文（注疏、礼忏文多为祖师著，DTW对齐意义不大）
"""
import json, os, sys, importlib.util, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(ROOT, 'scripts', 'build_segment_alignment.py')

spec = importlib.util.spec_from_file_location('align', SCRIPT_PATH)
align = importlib.util.module_from_spec(spec)
spec.loader.exec_module(align)

OUT_DIR = os.path.join(ROOT, 'data', 'segment_alignments')
os.makedirs(OUT_DIR, exist_ok=True)

# 已有
existing_ids = set()
for fn in os.listdir(OUT_DIR):
    if fn.endswith('.json') and fn != 'manifest.json':
        try:
            d = json.load(open(os.path.join(OUT_DIR, fn), encoding='utf-8'))
            vids = tuple(sorted(v['id'] for v in d['versions']))
            existing_ids.add(vids)
        except: pass
print(f'已有对齐版本组合：{len(existing_ids)}')

def get_chars(sid):
    p = os.path.join(ROOT, 'sutras', f'{sid}.json')
    if not os.path.exists(p): return 0
    try:
        s = json.load(open(p, encoding='utf-8'))
        # 兼容字段：优先使用实际内容长度，其次 chars 字段，再次 actual_char_count
        total = sum(len(c.get('text','')) for c in s.get('content',[]))
        if total > 0: return total
        return s.get('chars', 0) or s.get('actual_char_count', 0) or s.get('char_count', 0)
    except: return 0

groups = json.load(open(os.path.join(ROOT, 'ontology', 'parallel_translations.json'), encoding='utf-8'))

# 过滤：跳过注疏/目录/礼忏/仪轨/佛名经（非原经本文；且佛名经以佛名罗列为主，对齐无意义）
SKIP_KEYS = ['疏','鈔','記','目錄','目录','禮懺','礼忏','儀軌','仪轨','護摩','佛名經']
# 收集候选
candidates = []
for g in groups:
    title = g.get('title','')
    if any(k in title for k in SKIP_KEYS):
        continue
    sutras = g['sutras']
    ids = [s['id'] for s in sutras]
    chars = [get_chars(sid) for sid in ids]
    if min(chars) < 500:
        # 存在残缺译本，跳过
        continue
    vkey = tuple(sorted(ids))
    if vkey in existing_ids:
        continue
    max_c = max(chars)
    # 按最长字数分批：第一批做≤1万字；后续批次逐步放宽
    candidates.append((max_c, title, ids, chars))

candidates.sort()
print(f'可对齐异译组（排除注疏/残缺）共 {len(candidates)} 组\n')

# 第一批：最长本 ≤ 10000 字（短经/短论）
batch1 = [c for c in candidates if c[0] <= 10000]
print(f'=== 第一批（最长本 ≤ 10000字）共 {len(batch1)} 组 ===')
for max_c, title, ids, chars in batch1:
    print(f'  · {title} ({len(ids)}译, 最长{max_c}字)  {ids}')

success = []
for max_c, title, ids, chars in batch1:
    gid = 'seg_' + '_'.join(sorted(ids))
    print(f'\n→ [{gid}] {title}')
    try:
        out = align.build_alignment(gid, title, ids, skip_start=2, skip_noise=True)
        if out:
            # 把结果写到正确位置（build_alignment 内部已写文件）
            success.append(out)
    except Exception as e:
        import traceback; traceback.print_exc()
        print(f'  ❌ 异常: {e}')

# 重生成完整 manifest（包括已有）
manifest = []
for fn in sorted(os.listdir(OUT_DIR)):
    if fn.endswith('.json') and fn != 'manifest.json':
        d = json.load(open(os.path.join(OUT_DIR, fn), encoding='utf-8'))
        manifest.append({
            'group_id': d['group_id'],
            'group_title': d['group_title'],
            'n_versions': len(d['versions']),
            'n_alignments': d['n_alignments'],
            'versions': [{'id': v['id'], 'translator': v['translator'], 'title': v['title']} for v in d['versions']],
        })
with open(os.path.join(OUT_DIR, 'manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f'\n=== 本批次新增 {len(success)} 组，manifest 总 {len(manifest)} 组 ===')
