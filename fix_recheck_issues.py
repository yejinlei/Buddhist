#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修正第二轮复核发现的问题：1)应當當替换；2)漏标密呪真言小标题"""
import json, os, re

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
MOD = os.path.join(BASE, "data/modern-translation")

# 问题1：修复"應當當"重复替换
fix_count1 = 0
fix_count2 = 0

# 遍历所有12部
IDS = ["t0973", "t0165", "t2117", "t1798", "t0865", "t2741", "t2808", "t2183", "t0974", "t0868", "t1849", "t1072"]

def is_mantra_heavy(op):
    """判断是否是密咒段落：梵字生僻字+序号"""
    s = op
    # 序号+梵字
    if re.search(r'[一二三四五六七八九十百千]+句', s):
        return True
    # 音注标记多
    yinzhu = re.findall(r'(二合|三合|引聲|反切|半音|長聲|去引|重呼)', s)
    if len(yinzhu) >= 2:
        return True
    # 梵字占比（私用区字）
    priv_count = len(re.findall(r'[􀀀-􏿿󰀀-􏿿]', s))
    if priv_count >= 8:
        return True
    return False

for tid in IDS:
    path = os.path.join(MOD, f"{tid}.json")
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    
    for i, seg in enumerate(data['translations']):
        md = seg.get('modern', '')
        op = seg.get('original_preview', '')
        
        # 修复重复替换："應當當" -> "應當"，"住當" -> "住於"等
        # 原翻译中"當"替换为"應當"，但原文若已有"當"字可能导致叠加
        new_md = md
        # 错误替换：将原文"當心"错换为"應當心"，"當"="應"，所以"當"->""是错误的
        # 看具体情况："便住當心上" -> 白话变为"便住應當當心上"，应修正为"便安住於心上"或"便住於當心（心轮）"
        # 统一修正：所有"應當當"替换为"應當"
        if "應當當" in new_md:
            new_md = new_md.replace("應當當", "應當")
            fix_count1 += 1
        
        # 检查漏标密咒
        if is_mantra_heavy(op) and "【密呪真言】" not in new_md:
            # 替换当前小标题为【密呪真言】
            new_md = re.sub(r'^【[^】]+】', '【密呪真言】', new_md, count=1)
            # 也替换义解
            new_md = re.sub(r'【义解】[^\n]*', '【义解】此段為梵文密呪真言，按經文原字原音及「二合」「引聲」「反切」「半音」等音注照錄，含梵字種子與句數標記，不做翻譯，持誦時依原音準確讀誦。', new_md, count=1)
            fix_count2 += 1
        
        seg['modern'] = new_md
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print(f"修正完成：重字替换 {fix_count1} 处，密咒小标题 {fix_count2} 处，合计 {fix_count1+fix_count2} 处")
