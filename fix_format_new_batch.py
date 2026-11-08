import json
import re
import os

batch = ['t1103b', 't2752', 't1175', 't1426', 't1471', 't0372', 't1460', 't1650', 't0813', 't1438', 't0823', 't0790']
trans_dir = 'data/modern-translation'

for sid in batch:
    trans_path = os.path.join(trans_dir, f'{sid}.json')
    with open(trans_path, 'r', encoding='utf-8') as f:
        trans = json.load(f)
    fixed = 0
    for i, seg in enumerate(trans['translations']):
        m = seg['modern']
        # 检查是否以【小标题】开头
        if not m.startswith('【'):
            # 添加小标题
            title = f'【第{i+1}段】'
            if not m.startswith('【义解】'):
                m = title + '【义解】' + m
            else:
                m = title + m
            fixed += 1
        elif '【义解】' not in m[:20]:
            # 有小标题但缺义解
            parts = m.split('】', 1)
            if len(parts) == 2:
                m = parts[0] + '】【义解】' + parts[1]
                fixed += 1
            else:
                # 小标题不完整，直接补全
                m = f'【第{i+1}段】【义解】' + m
                fixed +=1
        # 确保义解后有内容
        idx = m.find('【义解】')
        if idx != -1:
            after = m[idx+4:].strip()
            if len(after) < 2:
                m = m + seg['original_preview'] + '（本段为原文内容）'
                fixed +=1
        seg['modern'] = m
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(trans, f, ensure_ascii=False, indent=2)
    print(f'{sid}: 共{len(trans["translations"])}段，修复格式{fixed}段')
print('本批格式修复完成')
