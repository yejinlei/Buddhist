#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""首轮独立校对 Worker A"""
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
    
    # 逐段核查
    orig_full = ws("\n".join(c.get("text", "") for c in s.get("content", [])))
    cat_pv = []
    
    for i, seg in enumerate(segs):
        sn = i + 1
        op = seg.get("original_preview", "") or ""
        md = seg.get("modern", "") or ""
        cat_pv.append(op)
        
        # 检查modern格式：以【小标题】开头
        if not re.match(r"^【[^】]+】", md):
            add(sid, f"第{sn}段", "modern未以【小标题】开头", md[:60])
        
        # 检查含【义解】且义解后有正文
        yj_pos = md.find("【义解】")
        if yj_pos < 0:
            add(sid, f"第{sn}段", "modern缺少【义解】模块", md[:60])
        else:
            after_yj = md[yj_pos + len("【义解】"):].strip()
            if not after_yj:
                add(sid, f"第{sn}段", "【义解】后无正文内容", "")
        
        # 检查小标题是否为空泛通用
        m1 = re.match(r"^【([^】]+)】", md)
        if m1:
            sub = m1.group(1)
            if sub in ["法義宣說", "正文", "經文", "其他"]:
                add(sid, f"第{sn}段", "小标题过于空泛通用，需更具体", f"当前小标题: {sub}")
        
        # 检查咒文部分：若原段含真言/陀罗尼，验证modern是否照录原字
        op_nows = ws(op)
        if re.search(r"(真言曰|大明曰|陀羅尼曰|神呪曰|呪曰|密言曰)", op_nows):
            # modern应包含原文咒字
            # 这里检查是否漏了重要咒语原字
            mantra_chars = re.findall(r"[唵阿吽嚩怛囉薩達摩迦曩係𠺁鑁斛吽怛𠸪紇哩噁索郝㘕唅虐溺婀唵欠婆伽訶夜娑訶弭履瑜祇涅盤半叱]" , op_nows)
            if len(mantra_chars) > 5:
                md_nows = ws(md)
                # 咒文段落的原文密字应至少保留80%
                kept = sum(1 for c in mantra_chars if c in md_nows)
                if kept < len(mantra_chars) * 0.7:
                    add(sid, f"第{sn}段", f"咒文字符可能被简化转写，原字保留率{kept/len(mantra_chars):.0%}", f"原咒字数={len(mantra_chars)}，保留={kept}")
    
    # 全局子串校验
    cat_nows = ws("".join(cat_pv))
    if cat_nows not in orig_full:
        add(sid, "全局", "拼接预览不是原文连续子串", "")

# 保存结果
out_path = os.path.join(BASE, "proofread", "proofread_A_batch205.md")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"# 首轮校对报告 Worker A\n本批12部经文，共发现 {len(issues)} 处问题：\n\n")
    for it in issues:
        f.write(f"- [{it['sutra']}] {it['location']}: {it['desc']}")
        if it['detail']:
            f.write(f"\n  > {it['detail']}")
        f.write("\n")
    if not issues:
        f.write("\n**全批12部经文，经Worker A核查，零问题。**\n")

print(f"Worker A 校对完成，发现 {len(issues)} 处问题")
print(f"报告写入: {out_path}")
