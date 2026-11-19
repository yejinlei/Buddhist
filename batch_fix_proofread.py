#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re
from opencc import OpenCC
cc = OpenCC('t2s')  # 繁体转简体

sutra_ids = ['t1051', 't0886', 't2881', 't1334', 't2870', 't0976', 't0965', 't1330', 't2775', 't1914', 't1957', 't1653']
trans_dir = 'data/modern-translation'
task_dir = 'data/baihua-tasks'

def convert_modern(text):
    """转换白话文为简体，保留咒文部分？先整体转，然后处理特殊情况"""
    # 整体繁体转简体
    text = cc.convert(text)
    # 修正个别转换错误
    text = text.replace('唵', '唵')  # 保留原字
    text = text.replace('吽', '吽')
    text = text.replace('嚩', '嚩')
    text = text.replace('囉', '囉')
    text = text.replace('拏', '拏')
    text = text.replace('怛', '怛')
    text = text.replace('囇', '囇')
    text = text.replace('呬', '呬')
    text = text.replace('舸', '舸')
    text = text.replace('醯', '醯')
    return text

for sid in sutra_ids:
    path = os.path.join(trans_dir, f'{sid}.json')
    task_path = os.path.join(task_dir, f'{sid}.json')
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    with open(task_path, 'r', encoding='utf-8') as f:
        task = json.load(f)
    
    for i, sec in enumerate(d['translations']):
        m = sec.get('modern', '')
        # 繁简转换
        m = convert_modern(m)
        # 修复特定问题
        if sid == 't1051' and i == 0:
            # 修正错译："法贤大师说"改为"那时，世尊"，修正题署
            m = m.replace('法贤大师说：我现在皈敬', '那时，世尊为了利益一切众生，宣说这部诸佛相应的大教王经。我（法贤）现在皈敬')
            # 题署改为白话
            m = m.replace('西天译经三藏朝散大夫试光禄卿明教大师臣法贤奉诏翻译此经。', '这部经是西天译经三藏朝散大夫试光禄卿明教大师法贤奉诏翻译的。')
        if sid == 't1051' and i == 8:
            # 统一佛名为"拘楼孙佛"
            m = m.replace('拘留孙佛', '拘楼孙佛')
        if sid == 't0886' and i == 0:
            # 题署改为白话
            m = m.replace('西天译经三藏朝奉大夫试光禄卿传法大师赐紫臣施护译。', '这部经是宋代西天译经三藏朝奉大夫试光禄卿传法大师赐紫沙门施护奉诏翻译的。')
        if sid == 't2881' and i == 0:
            # 开头"如是我闻"改为白话
            m = m.replace('如是我闻：一时，', '我是这样听佛陀说法的：那时，')
        if sid == 't1334' and i == 0:
            # 题署改为白话
            m = m.replace('隋三藏法师阇那崛多译。', '这部经是隋代三藏法师阇那崛多翻译的。')
            # 统一"摩诃"
            m = m.replace('摩呵', '摩诃')
        if sid == 't2870' and i == 0:
            m = m.replace('闻如是：', '我是这样听佛陀说法的：')
        if sid == 't2870' and i == 13:
            m = m.replace('布施法们', '布施法门')
        if sid == 't0976' and i == 9:
            # 第三句改回"南无"
            m = m.replace('南谟一切不还众', '南无一切不还众')
        if sid == 't0976' and i == 17:
            # 保留原文"应正等览"，不要改觉
            m = m.replace('应正等觉', '应正等览')
        if sid == 't1051' and i == 46:
            # 保留"勅"原字
            m = m.replace('奉敕雕造', '奉勅雕造')
        # 修正【义解】后如果直接是原文繁体的情况
        sec['modern'] = m
    
    # 处理t1957重复段问题：段36-40？不对，重置后用骨架重新来？不，直接用task骨架重置，然后重新转换？
    # 先重置original_preview
    for i in range(len(task['translations'])):
        d['translations'][i]['original_preview'] = task['translations'][i]['original_preview']
    
    # 写回
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f'{sid} 繁简转换与问题修正完成')

print('批量修复完成')
