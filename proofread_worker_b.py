#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""首轮独立校对 Worker B - 义解充实度与固定译语检查"""
import json, os, re

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
MOD = os.path.join(BASE, "data/modern-translation")
SRC = os.path.join(BASE, "sutras")
IDS = ["t0973", "t0165", "t2117", "t1798", "t0865", "t2741", "t2808", "t2183", "t0974", "t0868", "t1849", "t1072"]

def ws(s): return re.sub(r"[\s\u3000]+", "", s or "")

issues = []

def add(sid, where, desc, detail=""):
    issues.append({"sutra": sid, "location": where, "desc": desc, "detail": detail})

for sid in IDS:
    with open(os.path.join(MOD, f"{sid}.json"), encoding='utf-8') as f:
        m = json.load(f)
    with open(os.path.join(SRC, f"{sid}.json"), encoding='utf-8') as f:
        s = json.load(f)
    
    title = m.get("title", "")
    segs = m.get("translations", [])
    
    for i, seg in enumerate(segs):
        sn = i + 1
        op = seg.get("original_preview", "") or ""
        md = seg.get("modern", "") or ""
        
        # 检查义解充实度：【义解】后内容长度至少20字
        yj_match = re.search(r"【义解】([^\n【]+)", md)
        if yj_match:
            yj_content = yj_match.group(1).strip()
            if len(yj_content) < 20:
                add(sid, f"第{sn}段", "义解内容过短，不足20字，需充实法义说明", f"当前义解: {yj_content}")
        
        # 检查固定译语保留：薄伽梵、如是我聞、苾芻等应保留原字
        fixed_terms = ["薄伽梵", "如是我聞", "苾芻", "苾芻尼", "鄔波索迦", "鄔波斯迦", "阿耨多羅三藐三菩提", "闕文", "□"]
        op_nows = ws(op)
        md_nows = ws(md)
        for term in fixed_terms:
            if term in op_nows and term not in md_nows:
                # 如是我聞特殊处理（通常是开头）
                if term == "如是我聞" and "聞如是" in md_nows:
                    continue
                add(sid, f"第{sn}段", f"固定译语「{term}」未在白话中保留原字", f"原文含「{term}」但白话未出现")
        
        # 检查原文阙文□是否保留
        if "□" in op and "□" not in md:
            add(sid, f"第{sn}段", "原文阙文□未在白话中保留", "")
    
    # 检查段数合理性
    if len(segs) < 50:
        add(sid, "全局", f"段落数异常偏少: {len(segs)}段，长篇经文通常>150段", "")

# 保存结果
out_path = os.path.join(BASE, "proofread", "proofread_B_batch205.md")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"# 首轮校对报告 Worker B（义解充实度+固定译语）\n本批12部经文，共发现 {len(issues)} 处问题：\n\n")
    for it in issues:
        f.write(f"- [{it['sutra']}] {it['location']}: {it['desc']}")
        if it['detail']:
            f.write(f"\n  > {it['detail']}")
        f.write("\n")
    if not issues:
        f.write("\n**全批12部经文，经Worker B核查，零问题。**\n")

print(f"Worker B 校对完成，发现 {len(issues)} 处问题")
print(f"报告写入: {out_path}")
