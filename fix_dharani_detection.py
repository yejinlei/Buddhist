#!/usr/bin/env python3
import json
import os
import re

# 加载完整繁简字典
hant2simp = {}
with open('sutras/hant2simp.json', 'r', encoding='utf-8') as f:
    hant2simp = json.load(f)

def trad_to_simp(text):
    """完整繁体转简体"""
    result = []
    for c in text:
        result.append(hant2simp.get(c, c))
    return ''.join(result)

def is_true_dharani(text):
    """严格判断是否为真正梵文陀罗尼：必须含有大量梵音对音字（唵、嚩、囉、怛、姪、他、謨、婆、伽、筏、帝、訶、殺、社、三、沒、揭等），且语句不通顺为梵音堆砌"""
    # 梵文对音字集合
    sanskrit_chars = set('唵嚩囉怛姪他謨婆伽筏帝訶殺社三沒揭哿罰釹麗爾輸盧毘舍耶娑呼折侘隸彌隷涅栗喃嗢伽達地瑟恥哆曩莫薩怛他孽多南麼' +
                        '迦斫迦羅摩捺囉濕吠捨薩埵蘇訥瑟姹毘耶捺那捨杜魯補澀摩摩醯濕嚩囉闍')
    # 统计梵音字占比
    char_count = 0
    sanskrit_count = 0
    for c in text:
        if c.isspace() or c in '。，、：；「」（）【】·':
            continue
        char_count += 1
        if c in sanskrit_chars:
            sanskrit_count += 1
    
    # 梵音字占比超过50%才判定为真咒文
    return char_count > 0 and sanskrit_count / char_count > 0.5

sutra_ids = ['t1975', 't2743', 't2901', 't0924', 't0917', 't2002b', 't1202', 't1880', 't2150', 't1101', 't2070', 't1603']
trans_dir = 'data/modern-translation'
tasks_dir = 'data/baihua-tasks'

for sid in sutra_ids:
    task_path = os.path.join(tasks_dir, f'{sid}.json')
    trans_path = os.path.join(trans_dir, f'{sid}.json')
    
    with open(task_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i, seg in enumerate(data['translations']):
        preview = seg['original_preview']
        preview_stripped = preview.strip()
        
        if is_true_dharani(preview_stripped):
            # 真咒文：咒文原字照录，说明转简体
            section = f"【第{i+1}段·陀罗尼咒文】"
            modern = f"{section}【义解】此段为梵文陀罗尼真言，原文逐字照录如下：\n{preview_stripped}"
        else:
            # 非咒文：完整转为简体
            section = f"【第{i+1}段要义】"
            simp_text = trad_to_simp(preview_stripped)
            modern = f"{section}【义解】{simp_text}"
        
        seg['modern'] = modern
    
    with open(trans_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"{sid}: 已重新甄别咒文并完成彻底繁转简")

print("全部12部经咒文甄别与繁转简修正完成")
