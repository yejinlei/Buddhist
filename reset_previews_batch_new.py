import json
import os

batch = ['t1103b', 't2752', 't1175', 't1426', 't1471', 't0372', 't1460', 't1650', 't0813', 't1438', 't0823', 't0790']
tasks_dir = 'data/baihua-tasks'
trans_dir = 'data/modern-translation'

for sid in batch:
    task_path = os.path.join(tasks_dir, f'{sid}.json')
    trans_path = os.path.join(trans_dir, f'{sid}.json')
    with open(task_path, 'r', encoding='utf-8') as f:
        task = json.load(f)
    with open(trans_path, 'r', encoding='utf-8') as f:
        trans = json.load(f)
    previews = [seg['original_preview'] for seg in task['translations']]
    assert len(previews) == len(trans['translations']), f'{sid} 段数不匹配'
    for i in range(len(previews)):
        trans['translations'][i]['original_preview'] = previews[i]
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(trans, f, ensure_ascii=False, indent=2)
    print(f'{sid}: original_preview已重置，共{len(previews)}段')
print('全部重置完成')
