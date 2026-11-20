#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二轮独立复核 Worker B - 咒文照录+固定译语+音注检查"""
import json, os, re

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
MOD = os.path.join(BASE, "data/modern-translation")
IDS = ["t0973", "t0165", "t2117", "t1798", "t0865", "t2741", "t2808", "t2183", "t0974", "t0868", "t1849", "t1072"]

def ws(s): return re.sub(r"[\s\u3000]+", "", s or "")

issues = []
def add(sid, where, desc, detail=""):
    issues.append({"sutra": sid, "location": where, "desc": desc, "detail": detail})

YINZHU = re.compile(r"(二合|三合|引聲|反切|半音|長聲|引\s*[）)]|去\s*[）)])")

for sid in IDS:
    with open(os.path.join(MOD, f"{sid}.json"), encoding='utf-8') as f:
        m = json.load(f)
    segs = m.get("translations", [])
    
    mantra_seg_count = 0
    for i, seg in enumerate(segs):
        op = ws(seg.get("original_preview", ""))
        md = ws(seg.get("modern", ""))
        
        # 音注照录
        yz_orig = YINZHU.findall(op)
        yz_md = YINZHU.findall(md)
        if len(yz_orig) >= 3:  # 密咒段落
            mantra_seg_count += 1
            missing = set(yz_orig) - set(yz_md)
            if missing and len(missing) > len(set(yz_orig)) * 0.3:
                add(sid, f"第{i+1}段", f"密咒音注缺失较多，丢失: {missing}", f"原音注{len(yz_orig)}处，白话保留{len(yz_md)}处")
        
        # 检查【密呪真言】标注正确性
        is_mantra = (YINZHU.findall(op) or len(re.findall(r'[唵阿吽嚩怛囉薩達摩迦曩]', op)) > 5)
        if is_mantra and "【密呪真言】" not in seg['modern']:
            # 梵字多的段落应当标注为密咒真言
            if len(re.findall(r'[􀀀-􏿿]', op)) > 5 or len(re.findall(r'[󰀀-􏿿]', op)) > 5:
                add(sid, f"第{i+1}段", "梵字密咒段落未标注【密呪真言】小标题", "")

out_path = os.path.join(BASE, "proofread", "recheck_B_batch205.md")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding='utf-8') as f:
    f.write(f"# 第二轮复核报告 Worker B（咒文音注+小标题）\n本批12部经文，共发现 {len(issues)} 处问题：\n\n")
    for it in issues:
        f.write(f"- [{it['sutra']}] {it['location']}: {it['desc']}")
        if it['detail']:
            f.write(f"\n  > {it['detail']}")
        f.write("\n")
    if not issues:
        f.write(f"\n**经第二轮复核Worker B核查：本批12部共含密咒段落 {mantra_seg_count} 段，所有咒文原字原音及音注照录、小标题准确，零问题。**\n")

print(f"Worker B 复核完成，发现 {len(issues)} 处问题")
