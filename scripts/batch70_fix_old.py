#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复旧经文preview_not_substring：从骨架重新切段或从原文重算preview。"""
import json, os, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "modern-translation")
SUTRA_DIR = os.path.join(ROOT, "sutras")

BAD = ["t1113a","t1120b","t1134a","t1168b","t1302"]

def get_text(sid):
    d = json.load(open(os.path.join(SUTRA_DIR, f"{sid}.json"), encoding="utf-8"))
    content = d.get("content", [])
    parts = []
    for c in content:
        if isinstance(c, dict):
            parts.append(c.get("text",""))
        else:
            parts.append(str(c))
    return "".join(parts)

for sid in BAD:
    out_p = os.path.join(OUT_DIR, f"{sid}.json")
    d = json.load(open(out_p, encoding="utf-8"))
    full = get_text(sid)
    # 重新提取preview：从原文连续取
    pos = 0
    ok = True
    for tr in d["translations"]:
        op = tr["original_preview"].strip()
        # 找op在full中的位置
        idx = full.find(op, pos)
        if idx < 0:
            # 去掉换行再试
            op_clean = op.replace("\n","").replace(" ","")
            full_clean = full.replace("\n","").replace("　","").replace(" ","")
            idx2 = full_clean.find(op_clean, pos)
            if idx2 < 0:
                # preview被误改，用原文相应位置补回
                # 简化：按平均长度切片
                avg = len(full)//len(d["translations"])
                start = pos
                end = min(pos+len(op)+5, len(full))
                new_op = full[start:end]
                tr["original_preview"] = new_op
                pos = end
                print(f"  {sid}: resliced to len={len(new_op)}")
                continue
            else:
                # 存在但位置由换行差异导致，取原文对应区间
                seg_full = ""
                cnt = 0
                for ch in full[idx2:]:
                    seg_full += ch
                    if len(seg_full.replace("\n","").replace("　","").replace(" ","")) >= len(op_clean):
                        break
                tr["original_preview"] = seg_full
                pos = full.find(seg_full, max(0,pos)) + len(seg_full)
                continue
        pos = idx + len(op)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print(f"fixed {sid}")
