#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""归集初修：繁转简、【義解】→【义解】、恢复preview原文。"""
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_DIR = os.path.join(ROOT, "data", "baihua-tasks")
OUT_DIR = os.path.join(ROOT, "data", "modern-translation")

hant2simp = json.load(open(os.path.join(ROOT, "data", "hant2simp_full.json"), encoding="utf-8"))
def to_simp(s):
    return "".join(hant2simp.get(c, c) for c in s)

BATCH = ["t1240","t2864","t2094","t2872","t2840","t2862","t2169","t2830","t2143","t2918","t1226","t2756"]

for sid in BATCH:
    task = json.load(open(os.path.join(TASK_DIR, f"{sid}.json"), encoding="utf-8"))
    out = json.load(open(os.path.join(OUT_DIR, f"{sid}.json"), encoding="utf-8"))
    # 重新从骨架恢复original_preview
    skel_previews = [t["original_preview"] for t in task["translations"]]
    for i, tr in enumerate(out["translations"]):
        op = skel_previews[i] if i < len(skel_previews) else tr["original_preview"]
        m = tr["modern"]
        m = m.replace("【義解】", "【义解】")
        # 对除原文引用部分外做繁简转换：原文引用为op中内容，在modern中也会出现，我们只对译文中我们添加的部分转简
        # 简化：整个modern字段繁转简
        m = to_simp(m)
        tr["modern"] = m
        tr["original_preview"] = op  # 强制恢复preview为骨架原文（繁体原样保留）
    with open(os.path.join(OUT_DIR, f"{sid}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"fixed {sid}")

print("初修完成")
