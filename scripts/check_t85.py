# -*- coding: utf-8 -*-
"""T85 古逸部/疑似部 完整性核对"""
import json, glob, os
rows = []
for f in glob.glob('sutras/t*.json'):
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception: continue
    if str(d.get('vol','')) != 'T85': continue
    actual = sum(len(c.get('text','')) for c in d.get('content', []))
    off = d.get('official_char_count') or 0
    ratio = (actual/off) if off else None
    rows.append((d.get('id'), d.get('title'), off, actual, d.get('juan_count'), ratio))
rows.sort(key=lambda r: (r[5] if r[5] is not None else 9))
print('T85 收录经数:', len(rows))
bad = [r for r in rows if r[5] is not None and r[5] < 0.7]
print('完整度 <70% 的:', len(bad))
for r in bad[:20]:
    print(f'  {r[0]} {str(r[1])[:20]:22s} 官方{r[2]:>8d} 实际{r[3]:>8d} {r[5]*100:5.1f}%')
noff = [r for r in rows if r[5] is None]
print('缺官方字数参照:', len(noff))
