#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第146批选经：筛选适合白话义解的经论"""
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SUTRA_DIR = ROOT / "sutras"
MODERN_DIR = ROOT / "data" / "modern-translation"

# 已上线清单（含永久排除的t1545）
DONE = set()
if MODERN_DIR.exists():
    for f in MODERN_DIR.glob("t*.json"):
        DONE.add(f.stem)
DONE.add("t1545")  # 永久排除
DONE.update({"t2002a","t1969b"})  # 自定义id已完成

# 标题黑名单：仪轨/咒/佛名/目录/音义/悉昙/赞/忏法/真言等
BAD_TITLE = re.compile(r'(目錄|目录|佛名|名號|名号|陀羅尼集|真言集|咒|呪|儀軌|仪轨|懺法|忏法|贊|赞|音義|音义|悉曇|悉昙|禮讚|礼赞|念誦|念诵|法數|法数)')

# 私用区字符范围检测（覆盖第0/15/16平面）
def has_pua(s: str) -> bool:
    for ch in s:
        cp = ord(ch)
        if (0xE000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0xFFFFD) or (0x100000 <= cp <= 0x10FFFD):
            return True
    return False

candidates = []
for f in sorted(SUTRA_DIR.glob("t*.json")):
    tid = f.stem
    if tid in DONE:
        continue
    try:
        d = json.loads(f.read_text("utf-8"))
    except Exception as e:
        continue
    title = d.get("title", "")
    if BAD_TITLE.search(title):
        continue
    # 提取正文段落，去除卷号标记、空行
    paras = []
    for item in d.get("content", []):
        text = item.get("text", "")
        # 去除卷号标记行
        if re.match(r'^卷[0-9上下中]+$', text.strip()):
            continue
        t = re.sub(r'\s+', '', text)
        if len(t) < 20:  # 过短标题/品名跳过
            continue
        if has_pua(t):
            continue
        paras.append(t)
    n = len(paras)
    if n < 40 or n > 160:
        continue
    total_chars = sum(len(p) for p in paras)
    if total_chars < 600 or total_chars > 60000:
        continue
    avg_len = total_chars / n
    if avg_len < 50 or avg_len > 400:
        continue
    # 标点覆盖率
    punct = sum(1 for ch in ''.join(paras) if ch in '。，？！：；「」『』、')
    punct_ratio = punct / total_chars if total_chars else 0
    if punct_ratio < 0.08:  # 无标点偈颂连写剔除
        continue
    # 阙文比例
    que = sum(1 for ch in ''.join(paras) if ch == '□')
    if que / total_chars > 0.05:
        continue
    # 初步看译者/作者
    tr = d.get("translator", "失译")
    candidates.append({
        "tid": tid,
        "title": title,
        "tr": tr,
        "n": n,
        "chars": total_chars,
        "avg": round(avg_len, 1),
        "punct": round(punct_ratio, 3),
    })

# 按字符数排序，优先选中型经论
candidates.sort(key=lambda x: x["chars"])
print(f"=== 候选经文共 {len(candidates)} 部 ===")
for i, c in enumerate(candidates[:50], 1):
    print(f"{i:2d}. {c['tid']:6s} {c['title'][:30]:30s} {c['tr'][:15]:15s} {c['n']:3d}段 {c['chars']:5d}字 段均{c['avg']} 标点{c['punct']}")

# 保存候选
with open("_b146/candidates.json", "w", encoding="utf-8") as f:
    json.dump(candidates, f, ensure_ascii=False, indent=2)
print(f"\n候选已保存到 _b146/candidates.json")
