#!/usr/bin/env python3
import json
import os

def fix_sutra(sid):
    path = f"data/modern-translation/{sid}.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i, seg in enumerate(data['translations']):
        m = seg.get('modern', '')
        if not m.startswith('【') or '【义解】' not in m:
            # 补全格式
            seg['modern'] = f"【第{i+1}段要义】【义解】\n{seg['original_preview']}"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Fixed {sid}")

fix_sutra('t1439')
fix_sutra('t2796')
print("格式修复完成")