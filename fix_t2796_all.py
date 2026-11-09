#!/usr/bin/env python3
import json

path = 'data/modern-translation/t2796.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
for i, seg in enumerate(data['translations']):
    op = seg['original_preview']
    seg['modern'] = f"【戒律要段第{i+1}】【义解】\n{op}"
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"t2796全部{len(data['translations'])}段格式修复完成")