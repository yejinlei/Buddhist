#!/usr/bin/env python3
"""最终独立复核脚本：批次177（12经）"""
import json
import os
import re
import sys

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
MODERN_DIR = os.path.join(BASE, "data/modern-translation")
SUTRAS_DIR = os.path.join(BASE, "sutras")
TIDS = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659",
        "t0327", "t0843", "t2818", "t1737", "t0652", "t0405"]

# 已知错译串
WRONG_STRS = ["菩萨菩萨", "一起胝", "一起摩罗", "一起致", "一起力迦", "一起起",
              "白佛陀说", "译像这样", "译这时", "译如是", "译一时"]

# 密咒简体梵字（正文中必须为繁体）
FANZI_SIMP = ["罗", "阇", "萨", "诃", "贺", "楼", "弥", "输", "达", "驮", "鲁", "乌", "卢"]

results = {}
overall_wrong = []
overall_fanzi = []

for tid in TIDS:
    mod_path = os.path.join(MODERN_DIR, f"{tid}.json")
    sut_path = os.path.join(SUTRAS_DIR, f"{tid}.json")
    with open(mod_path, "r", encoding="utf-8") as f:
        mod = json.load(f)
    with open(sut_path, "r", encoding="utf-8") as f:
        sut = json.load(f)

    # ---------- 覆盖率 / 连续子串 ----------
    raw = sut.get("content", "")
    if isinstance(raw, list):
        orig_text = "".join(item.get("text", "") if isinstance(item, dict) else str(item) for item in raw)
    else:
        orig_text = str(raw)
    orig_stripped = re.sub(r"\s+", "", orig_text)
    previews = []
    for seg in mod.get("translations", []):
        op = seg.get("original_preview", "")
        previews.append(re.sub(r"\s+", "", op))
    concat_preview = "".join(previews)
    # 覆盖率：concat_preview 在原文中出现的比例
    if concat_preview in orig_stripped:
        is_sub = True
        cov = len(concat_preview) / len(orig_stripped) * 100 if orig_stripped else 0
    else:
        is_sub = False
        # 逐段检查最大匹配
        pos = 0
        matched = 0
        for pv in previews:
            idx = orig_stripped.find(pv, pos)
            if idx >= 0:
                matched += len(pv)
                pos = idx + len(pv)
            else:
                # 部分匹配
                pass
        cov = matched / len(orig_stripped) * 100 if orig_stripped else 0

    # ---------- 白话段规则 ----------
    mod_issues = []
    fanzi_hits = []
    wrong_hits = []
    in_mizhou = False
    mizhou_after_header = 0  # 计数密咒正文行（跳过前两行）
    for i, seg in enumerate(mod.get("translations", [])):
        modern = seg.get("modern", "")
        # 规则3: 以【开头；含【义解】；义解后非空；不含半角逗号/句号在白话中
        # 检查半角逗号/句号（注意：允许专有名词、梵音等——这里只统计出现情况）
        # 先看是否以【开头
        if not modern.startswith("【"):
            mod_issues.append((i+1, "modern不以【开头", modern[:30]))
        # 是否含【义解】
        if "【义解】" not in modern:
            mod_issues.append((i+1, "modern缺【义解】", modern[:30]))
        else:
            # 义解后非空
            parts = modern.split("【义解】", 1)
            if len(parts) < 2 or parts[1].strip() == "":
                mod_issues.append((i+1, "【义解】后为空", modern[:30]))
        # 半角逗号/句号
        half = [c for c in modern if c in (",", ".")]
        # 允许数字里的点、梵音拼音里的？ 简化：直接记录
        # 仅统计【义解】之后的白话部分
        yijie_idx = modern.find("【义解】")
        if yijie_idx >= 0:
            baihua_part = modern[yijie_idx + len("【义解】"):]
            half_in_baihua = [c for c in baihua_part if c in (",", ".")]
            if half_in_baihua:
                mod_issues.append((i+1, f"白话含半角{','.join(set(half_in_baihua))}", baihua_part[:40]))

        # 规则4: 【密咒照录】段
        if modern.startswith("【密咒照录】"):
            in_mizhou = True
            mizhou_after_header = 0
            # 正文从换行后开始，前两行（标题行 + 第1行正文？）跳过
            # 用户说"前两行之后的行"——即密咒标签行算第一行，再跳过第二行
            lines = modern.split("\n")
            # 跳过前两行
            for j, line in enumerate(lines):
                if j < 2:
                    continue
                for ch in FANZI_SIMP:
                    if ch in line:
                        fanzi_hits.append((i+1, ch, line[:40]))
            continue
        # 规则5: 错译串
        for ws in WRONG_STRS:
            if ws in modern:
                wrong_hits.append((i+1, ws, modern[:50]))

    results[tid] = {
        "orig_len": len(orig_stripped),
        "preview_len": len(concat_preview),
        "coverage": round(cov, 2),
        "is_continuous": is_sub,
        "mod_issues": mod_issues,
        "fanzi_hits": fanzi_hits,
        "wrong_hits": wrong_hits,
        "seg_count": len(mod.get("translations", [])),
    }
    overall_fanzi.extend([(tid,)+h for h in fanzi_hits])
    overall_wrong.extend([(tid,)+h for h in wrong_hits])

# ---------- 特殊检查 ----------
special_notes = []
# t0652 段85 沙门绍德/诏德
with open(os.path.join(MODERN_DIR, "t0652.json"), "r", encoding="utf-8") as f:
    t0652 = json.load(f)
seg85 = t0652["translations"][84]
modern85 = seg85.get("modern", "")
has_shaode = "沙门绍德" in modern85
has_zhaode = "诏德" in modern85
special_notes.append(("t0652 seg85", f"含'沙门绍德':{has_shaode}, 含'诏德':{has_zhaode}", modern85[:80]))

# t2818 □缺字保留
with open(os.path.join(MODERN_DIR, "t2818.json"), "r", encoding="utf-8") as f:
    t2818 = json.load(f)
kou_count = 0
for seg in t2818.get("translations", []):
    kou_count += seg.get("modern", "").count("□")
special_notes.append(("t2818 □缺字", f"共{kou_count}个□", "OK" if kou_count > 0 else "FAIL"))

# 输出
print("=== 覆盖率 & 连续子串 ===")
for tid in TIDS:
    r = results[tid]
    tag = "PASS" if r["is_continuous"] and r["coverage"] > 95 else "CHECK"
    print(f"{tid}: orig={r['orig_len']}, preview={r['preview_len']}, cov={r['coverage']}%, continuous={r['is_continuous']}  [{tag}]")

print("\n=== 白话格式问题 ===")
for tid in TIDS:
    r = results[tid]
    if r["mod_issues"]:
        print(f"{tid}: {len(r['mod_issues'])} issues")
        for x in r["mod_issues"][:5]:
            print(f"  seg{x[0]}: {x[1]} -> {x[2]}")
    else:
        print(f"{tid}: 格式PASS")

print("\n=== 密咒简体梵字 ===")
if overall_fanzi:
    for h in overall_fanzi:
        print(f"  {h[0]} seg{h[1]}: 简体'{h[2]}' in '{h[3]}'")
else:
    print("无")

print("\n=== 错译串扫描 ===")
if overall_wrong:
    for h in overall_wrong:
        print(f"  {h[0]} seg{h[1]}: '{h[2]}' in '{h[3]}'")
else:
    print("无")

print("\n=== 特殊检查 ===")
for n in special_notes:
    print(f"  {n[0]}: {n[1]}  {n[2]}")
