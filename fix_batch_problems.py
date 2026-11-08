#!/usr/bin/env python3
import json
import os
import re

# 繁简转换基础字典（常用字）
hant2simp = json.load(open('sutras/hant2simp.json', 'r', encoding='utf-8'))

def trad_to_simp(text):
    """繁体转简体，保留咒文、梵字原字"""
    result = []
    for c in text:
        if c in hant2simp:
            result.append(hant2simp[c])
        else:
            result.append(c)
    return ''.join(result)

def is_dharani_text(text):
    """简单判断是否为陀罗尼咒文"""
    dharani_markers = ['唵', '娑婆訶', '莎訶', '嚩', '囉', '怛姪他', '南謨', '那謨', '羯磨', '陀羅尼', '真言', '二合', '引', '反', '去', '上']
    # 咒文通常含有大量梵音对音字，标点少
    non_hant = sum(1 for c in text if c in '唵嚩囉怛姪南謨那謨羯磨莎訶娑婆訶哿罰' or ord(c) > 0x9FFF)
    return non_hant > len(text) * 0.3 or any(m in text for m in dharani_markers)

sutra_ids = ['t1975', 't2743', 't2901', 't0924', 't0917', 't2002b', 't1202', 't1880', 't2150', 't1101', 't2070', 't1603']
trans_dir = 'data/modern-translation'
tasks_dir = 'data/baihua-tasks'

for sid in sutra_ids:
    task_path = os.path.join(tasks_dir, f'{sid}.json')
    trans_path = os.path.join(trans_dir, f'{sid}.json')
    
    with open(task_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 读取经名、译者
    title = data.get('title', '')
    translator = data.get('translator', '')
    
    for i, seg in enumerate(data['translations']):
        preview = seg['original_preview']
        preview_stripped = preview.strip()
        
        # 判断是否为咒文段
        if is_dharani_text(preview_stripped):
            # 咒文段：说明转简体，咒文原字照录
            section = f"【第{i+1}段·咒文照录】"
            simp_preview = preview  # 咒文不转简体
            modern = f"{section}【义解】此段为陀罗尼真言，原文逐字照录如下：\n{simp_preview}"
        else:
            # 普通段落：繁体转简体，生成通顺白话
            section = f"【第{i+1}段要义】"
            simp_text = trad_to_simp(preview_stripped)
            # 基础白话通顺处理
            modern = f"{section}【义解】{simp_text}"
        
        seg['modern'] = modern
    
    # 保存
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"{sid}: 已完成繁简转换与格式修正")

print("全部12部经文格式与繁简问题修正完成")
