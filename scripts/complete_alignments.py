#!/usr/bin/env python3
"""补齐段级对齐：只补「纯经文/论」异译组，跳过注疏/仪轨/目录/礼忏文。
按「版本组合」判差集（不按文件名），重建 manifest 时保留 file/mode 字段。"""
import json, os, re, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'segment_alignments')

spec = importlib.util.spec_from_file_location('align', os.path.join(ROOT, 'scripts', 'build_segment_alignment.py'))
align = importlib.util.module_from_spec(spec)
spec.loader.exec_module(align)

NON_SUTRA = re.compile(r'(疏$|義記$|义记$|目錄$|目录$|禮懺文|礼忏文|儀軌$|仪轨$|祈願|祈愿|戒本疏|律抄$)')

# 现有版本组合
existing = set()
for fn in os.listdir(OUT_DIR):
    if fn.endswith('.json') and fn != 'manifest.json':
        try:
            d = json.load(open(os.path.join(OUT_DIR, fn), encoding='utf-8'))
            existing.add(tuple(sorted(v['id'] for v in d['versions'])))
        except Exception:
            pass
print(f'现有对齐 {len(existing)} 组版本组合')

pt = json.load(open(os.path.join(ROOT, 'ontology', 'parallel_translations.json'), encoding='utf-8'))

todo, skipped = [], []
for g in pt:
    ids = [s['id'] for s in g['sutras']]
    key = tuple(sorted(ids))
    if key in existing:
        continue
    if NON_SUTRA.search(g['title']):
        skipped.append((g['title'], ids)); continue
    todo.append((g, ids))

print(f'\n纯经文待补 {len(todo)} 组；注疏类跳过 {len(skipped)} 组：')
for t, ids in skipped:
    print('   [跳过注疏]', t, ids)

added = []
for g, ids in todo:
    gid = '_'.join(ids)
    print(f'\n→ 对齐 [{gid}] {g["title"]} {ids}')
    try:
        out = align.build_alignment(gid, g['title'], ids, skip_start=2, skip_noise=True)
        if out:
            fn = f"{g['title']}_{gid}.json"
            with open(os.path.join(OUT_DIR, fn), 'w', encoding='utf-8') as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
            added.append(fn)
            print('   ✅ 写入', fn)
        else:
            print('   ⚠ build_alignment 返回空，跳过')
    except Exception as e:
        import traceback; traceback.print_exc()
        print('   ❌', e)

# 重建 manifest：保留 file/mode，保持既有条目结构
man = []
for fn in sorted(os.listdir(OUT_DIR)):
    if not fn.endswith('.json') or fn == 'manifest.json':
        continue
    d = json.load(open(os.path.join(OUT_DIR, fn), encoding='utf-8'))
    man.append({
        'file': fn,
        'group_id': d['group_id'],
        'group_title': d['group_title'],
        'mode': d.get('mode', 'segment'),
        'n_versions': len(d['versions']),
        'n_alignments': d['n_alignments'],
        'versions': [{'id': v['id'], 'translator': v['translator'], 'title': v['title']} for v in d['versions']],
    })
with open(os.path.join(OUT_DIR, 'manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(man, f, ensure_ascii=False, indent=2)

print(f'\n=== 新增 {len(added)} 组；manifest 总 {len(man)} 组 ===')
