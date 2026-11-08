#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抽取第16批10部经的繁体质文，供翻译 worker 使用。不改动一字。"""
import json, os

BATCH = ["t0067", "t0070", "t0090", "t0113", "t0118",
         "t0119", "t0121", "t0122", "t0123", "t0124"]

OUT = "_translate_src_b16"
os.makedirs(OUT, exist_ok=True)

for tid in BATCH:
    src = f"sutras/{tid}.json"
    d = json.load(open(src, encoding="utf-8"))
    parts = []
    for seg in d["content"]:
        parts.append(seg["text"])
    full = "\n".join(parts)
    rec = {
        "id": tid,
        "title": d["title"],
        "translator": d["translator"],
        "chars": d.get("chars"),
        "category": d.get("category", ""),
        "full_text": full,
    }
    with open(f"{OUT}/{tid}.json", "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    print(f"{tid} {d['title']} chars={d.get('chars')} -> {len(parts)} chapters")
print("done")
