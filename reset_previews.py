#!/usr/bin/env python3
import os
import json
import sys

TASKS_DIR = "data/baihua-tasks"
MODERN_DIR = "data/modern-translation"

def main():
    batch = sys.argv[1:]
    if not batch:
        print("请传入经号列表")
        return
    
    for sutra_id in batch:
        task_path = os.path.join(TASKS_DIR, f"{sutra_id}.json")
        modern_path = os.path.join(MODERN_DIR, f"{sutra_id}.json")
        
        with open(task_path, 'r', encoding='utf-8') as f:
            task_data = json.load(f)
        with open(modern_path, 'r', encoding='utf-8') as f:
            modern_data = json.load(f)
        
        # 提取任务中的original_preview
        task_previews = [t['original_preview'] for t in task_data['translations']]
        
        # 覆盖到译文中，确保不改动
        for i, t in enumerate(modern_data['translations']):
            if i < len(task_previews):
                t['original_preview'] = task_previews[i]
        
        with open(modern_path, 'w', encoding='utf-8') as f:
            json.dump(modern_data, f, ensure_ascii=False, indent=2)
        
        print(f"已重置 {sutra_id} 的original_preview字段，共{len(task_previews)}段")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
