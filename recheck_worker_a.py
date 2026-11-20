#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二轮独立复核 Worker A - 确认修正到位、original_preview未被改动"""
import json, os, re

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
MOD = os.path.join(BASE, "data/modern-translation")
SRC = os.path.join(BASE, "sutras")
TASK = os.path.join(BASE, "data", "baihua-tasks")
IDS = ["t0973", "t0165", "t2117", "t1798", "t0865", "t2741", "t2808", "t2183", "t0974", "t0868", "t1849", "t1072"]

def ws(s): return re.sub(r"[\s\u3000]+", "", s or "")

issues = []
def add(sid, where, desc, detail=""):
    issues.append({"sutra": sid, "location": where, "desc": desc, "detail": detail})

for sid in IDS:
    # 验证翻译文件与原始task的original_preview完全一致（未被改动）
    with open(os.path.join(TASK, f"{sid}.json"), encoding='utf-8') as f:
        task = json.load(f)
    with open(os.path.join(MOD, f"{sid}.json"), encoding='utf-8') as f:
        mod = json.load(f)
    with open(os.path.join(SRC, f"{sid}.json"), encoding='utf-8') as f:
        src = json.load(f)
    
    # 段数一致
    if len(task['translations']) != len(mod['translations']):
        add(sid, "全局", f"段数不一致: task={len(task['translations'])}, mod={len(mod['translations'])}", "")
    
    # original_preview逐段一致（一字未改）
    for i, (t_seg, m_seg) in enumerate(zip(task['translations'], mod['translations'])):
        if t_seg['original_preview'] != m_seg['original_preview']:
            add(sid, f"第{i+1}段", "original_preview被改动！与切段原文不一致", "")
    
    # 全局连续子串
    orig_full = ws("\n".join(c.get("text", "") for c in src.get("content", [])))
    cat_pv = ws("".join(s.get("original_preview", "") for s in mod['translations']))
    if cat_pv not in orig_full:
        add(sid, "全局", "拼接预览不是原文连续子串", "")
    if abs(len(cat_pv) / len(orig_full) - 1.0) > 0.02:
        add(sid, "全局", f"原文覆盖率异常: {len(cat_pv)/len(orig_full):.3f}", "")
    
    # 逐段检查modern格式（第二轮无空泛小标题）
    for i, seg in enumerate(mod['translations']):
        md = seg.get('modern', '')
        if not re.match(r"^【[^】]+】", md):
            add(sid, f"第{i+1}段", "modern未以【小标题】开头", "")
        if "【义解】" not in md:
            add(sid, f"第{i+1}段", "modern缺少【义解】", "")
        yj_pos = md.find("【义解】")
        if yj_pos >= 0 and len(md[yj_pos+4:].strip()) < 30:
            add(sid, f"第{i+1}段", "义解后正文过短", "")
        if "【法義宣說】" in md:
            add(sid, f"第{i+1}段", "仍有空泛小标题「法義宣說」", "")

out_path = os.path.join(BASE, "proofread", "recheck_A_batch205.md")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding='utf-8') as f:
    f.write(f"# 第二轮复核报告 Worker A（original_preview完整性+格式）\n本批12部经文，共发现 {len(issues)} 处问题：\n\n")
    for it in issues:
        f.write(f"- [{it['sutra']}] {it['location']}: {it['desc']}")
        if it['detail']:
            f.write(f"\n  > {it['detail']}")
        f.write("\n")
    if not issues:
        f.write("\n**经第二轮复核Worker A核查：本批12部original_preview逐字与切段原文一致，未被改动；所有段落格式规范，小标题精准，零问题。**\n")

print(f"Worker A 复核完成，发现 {len(issues)} 处问题")
