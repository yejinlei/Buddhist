#!/usr/bin/env python3
import json
import os

batch = "t2021 t1964 t0694 t1065 t2050 t0763 t0314 t0101 t1289 t1922 t0459 t0543".split()

for sid in batch:
    task_path = f'data/baihua-tasks/{sid}.json'
    trans_path = f'data/modern-translation/{sid}.json'
    
    with open(task_path, 'r', encoding='utf-8') as f:
        task = json.load(f)
    with open(trans_path, 'r', encoding='utf-8') as f:
        trans = json.load(f)
    
    # 重置original_preview
    for i, t_item in enumerate(task['translations']):
        trans['translations'][i]['original_preview'] = t_item['original_preview']
    
    # 确保其他字段一致
    for key in ['id', 'title', 'translator', 'vol', 'juan']:
        if key in task:
            trans[key] = task[key]
    
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(trans, f, ensure_ascii=False, indent=2)
    print(f"已重置 {sid} 的original_preview，共 {len(trans['translations'])} 段")
