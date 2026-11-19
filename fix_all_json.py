#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re
sutra_ids = ['t1051', 't0886', 't2881', 't1334', 't2870', 't0976', 't0965', 't1330', 't2775', 't1914', 't1957', 't1653']
task_dir = 'data/baihua-tasks'
trans_dir = 'data/modern-translation'

def fix_json_format(content):
    """修复常见的JSON格式错误：modern字段缺少引号、转义问题"""
    # 先修复modern字段开头缺少引号的问题
    content = re.sub(r'"modern":\s*【', r'"modern": "【', content)
    
    # 逐行处理，确保modern字段正确闭合
    lines = content.split('\n')
    fixed_lines = []
    in_modern = False
    modern_content = []
    for line in lines:
        if in_modern:
            # 检查是否到了original_preview行
            if '"original_preview"' in line:
                # 闭合modern字段
                modern_str = ''.join(modern_content)
                # 转义内部双引号
                modern_str = modern_str.replace('"', '\\"')
                fixed_lines.append('      "modern": "' + modern_str + '",')
                fixed_lines.append(line)
                in_modern = False
                modern_content = []
            else:
                # 收集modern内容，去掉开头的空格
                stripped = line.lstrip()
                if stripped.endswith('",'):
                    stripped = stripped[:-2]
                elif stripped.endswith(',') and not '"original_preview"' in stripped:
                    stripped = stripped[:-1]
                modern_content.append(stripped)
        else:
            if '"modern": "【' in line:
                # 已经有开头引号，检查是否闭合
                # 数一下引号数量，如果是奇数说明没闭合
                quote_count = line.count('"')
                # "modern": " 这里有3个引号
                if quote_count % 2 == 1:
                    # 没闭合，开始收集
                    in_modern = True
                    # 提取开头部分
                    idx = line.find('"modern": "【')
                    start_content = line[idx + len('"modern": "'):]
                    modern_content.append(start_content)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    return content

for sid in sutra_ids:
    trans_path = os.path.join(trans_dir, f'{sid}.json')
    task_path = os.path.join(task_dir, f'{sid}.json')
    
    print(f'处理 {sid}...')
    with open(trans_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 尝试解析，如果失败就修复
    trans = None
    try:
        trans = json.loads(content)
        print(f'  {sid} 格式正确')
    except:
        print(f'  {sid} 格式错误，尝试修复...')
        content = fix_json_format(content)
        try:
            trans = json.loads(content)
            print(f'  {sid} 修复成功')
        except Exception as e:
            print(f'  {sid} 修复失败: {e}，直接使用骨架')
            # 直接从骨架重新生成
            with open(task_path, 'r', encoding='utf-8') as f:
                task = json.load(f)
            trans = task
            # 给每段加空modern占位
            for item in trans['translations']:
                item['modern'] = "【待补】【义解】待补"
            print(f'  {sid} 使用骨架重新初始化')
    
    # 从骨架重置original_preview
    with open(task_path, 'r', encoding='utf-8') as f:
        task = json.load(f)
    
    # 确保段数一致
    if len(trans['translations']) != len(task['translations']):
        print(f'  {sid} 段数不一致，使用骨架')
        trans = task
        for item in trans['translations']:
            item['modern'] = "【待补】【义解】待补"
    
    for i in range(len(task['translations'])):
        trans['translations'][i]['original_preview'] = task['translations'][i]['original_preview']
    
    # 写回
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(trans, f, ensure_ascii=False, indent=2)
    cnt = len(trans['translations'])
    print(f'  {sid} original_preview已重置，共{cnt}段')

print('所有文件处理完成')
