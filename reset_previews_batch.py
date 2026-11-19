#!/usr/bin/env python3
import json
import os

sutra_ids = ['t1975', 't2743', 't2901', 't0924', 't0917', 't2002b', 't1202', 't1880', 't2150', 't1101', 't2070', 't1603']
tasks_dir = 'data/baihua-tasks'
trans_dir = 'data/modern-translation'

for sid in sutra_ids:
    task_path = os.path.join(tasks_dir, f'{sid}.json')
    trans_path = os.path.join(trans_dir, f'{sid}.json')
    
    with open(task_path, 'r', encoding='utf-8') as f:
        task_data = json.load(f)
    with open(trans_path, 'r', encoding='utf-8') as f:
        trans_data = json.load(f)
    
    # 从骨架文件读取original_preview覆盖到译文
    for i, task_seg in enumerate(task_data['translations']):
        if i < len(trans_data['translations']):
            trans_data['translations'][i]['original_preview'] = task_seg['original_preview']
    
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(trans_data, f, ensure_ascii=False, indent=2)
    
    print(f'{sid}: original_preview已重置完成')

print('全部12部经文original_preview重置完毕')
