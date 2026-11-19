#!/usr/bin/env python3
import os
import json
import sys

sids = sys.argv[1:]
project_root = os.path.dirname(os.path.abspath(__file__))

for sid in sids:
    task_path = os.path.join(project_root, 'data', 'baihua-tasks', f'{sid}.skel.json')
    trans_path = os.path.join(project_root, 'data', 'modern-translation', f'{sid}.json')
    
    with open(task_path, 'r', encoding='utf-8') as f:
        task_data = json.load(f)
    with open(trans_path, 'r', encoding='utf-8') as f:
        trans_data = json.load(f)
    
    # 重置original_preview
    for i, seg in enumerate(trans_data['translations']):
        seg['original_preview'] = task_data['translations'][i]['original_preview']
    
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(trans_data, f, ensure_ascii=False, indent=2)
    
    print(f"{sid}: original_preview已重置，共{len(trans_data['translations'])}段")

print("本批次全部重置完成")