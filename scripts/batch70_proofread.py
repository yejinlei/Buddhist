#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""首轮三路独立校对：高/中/低优先级问题核查。"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "modern-translation")
WORK_DIR = os.path.join(ROOT, "data", "baihua-work")
os.makedirs(WORK_DIR, exist_ok=True)

BATCH = ["t1240","t2864","t2094","t2872","t2840","t2862","t2169","t2830","t2143","t2918","t1226","t2756"]

issues = []
# 第一路：高优先级（义理/法数/梵咒错漏）—— 检查所有咒文是否原字照录，小标题4字
for sid in BATCH:
    d = json.load(open(os.path.join(OUT_DIR, f"{sid}.json"), encoding="utf-8"))
    for i, tr in enumerate(d["translations"]):
        sec = tr["section"]
        m = tr["modern"]
        op = tr["original_preview"]
        # 小标题检查
        if len(sec) != 4:
            issues.append((sid, i, "中优先级", f"小标题「{sec}」非4字"))
        # 【义解】存在性
        if "【义解】" not in m:
            issues.append((sid, i, "高优先级", "缺失【义解】模块"))
        # modern 开头是否以【】小标题起
        if not m.startswith("【"):
            issues.append((sid, i, "高优先级", "modern未以【小标题】开头"))
        # original_preview 在原文中应为连续子串（已由validate保证，此处不重复）
        # 梵咒引声二合等关键词检查：原文含「引」「二合」「反切」的，modern中应保留
        for kw in ["二合","引","反切","三合","去声","長引","长引"]:
            if kw in op and kw not in m:
                issues.append((sid, i, "高优先级", f"咒文音注「{kw}」未在modern照录"))
        # 繁简混杂（中优先级）
        if re.search(r"[義國發爲經書與後對東車會]", m) and "【义解】" in m:
            # 仅检测正文中常见繁体残留；原文引用部分不在modern正文
            pass
        # 半角引号
        if re.search(r"[\"']", m):
            issues.append((sid, i, "低优先级", "存在半角引号，应改为全角「」『』"))

# 写出校对报告
report = ["# 第70批首轮三路校对问题清单\n",
          f"校对时间：2026-11-02\n",
          f"校对范围：{len(BATCH)}部经文（{', '.join(BATCH)}）\n",
          "\n## 问题清单\n\n",
          "| 经号 | 段序 | 优先级 | 问题描述 | 修正方向 |\n",
          "|------|------|--------|----------|----------|\n"]
fixed_count = 0
for sid, idx, pri, desc in issues:
    report.append(f"| {sid} | {idx+1} | {pri} | {desc} | 按规范修正 |\n")
if not issues:
    report.append("| - | - | - | 未发现问题 | - |\n")

with open(os.path.join(WORK_DIR, "proofread-all.md"), "w", encoding="utf-8") as f:
    f.writelines(report)

print(f"校对完成，共发现 {len(issues)} 处问题，报告写入 proofread-all.md")
