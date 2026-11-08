#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, glob
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
tr_dir = "data/modern-translation"
done = set(os.path.basename(p)[:-5] for p in glob.glob(tr_dir + "/*.json"))
SKIP = {"hant2simp","index","index-light","search-index","search-word-index"}
rows = []
# PUA私用区Unicode范围
def is_pua(c):
    cp = ord(c)
    return (0xF000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0xFFFFD) or (0x100000 <= cp <= 0x10FFFD)

count_total = 0
count_seg_ok = 0
count_bad = 0
for p in glob.glob("sutras/*.json"):
    sid = os.path.basename(p)[:-5]
    if sid in done or sid in SKIP: continue
    count_total +=1
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception: continue
    if not isinstance(d, dict): continue
    content = d.get("content", [])
    if not isinstance(content, list): content = []
    txt = "".join((c.get("text","") if isinstance(c,dict) else str(c)) for c in content)
    txt_clean = "".join(txt.split())
    n = len(txt_clean)
    if n == 0: continue
    nseg = len(content)
    if nseg <3: continue
    count_seg_ok +=1
    # 计算PUA和□占比
    pua_count = sum(1 for c in txt_clean if is_pua(c))
    missing_count = txt_clean.count("□")
    bad_ratio = (pua_count + missing_count) / n
    if bad_ratio > 0.05:
        count_bad +=1
        continue
    rows.append((n, sid, d.get("title",""), d.get("translator",""), d.get("vol",""), nseg, bad_ratio))

print(f"未译总数: {count_total}")
print(f"段数≥3: {count_seg_ok}")
print(f"坏字占比超5%被过滤: {count_bad}")
print(f"合格候选数: {len(rows)}")
# 按字数从低到高排序
rows.sort(key=lambda r:(r[0]))
print("\n前20部最短的合格经文：")
for r in rows[:20]:
    print(f"{r[1]:10s} {r[0]:5d}字 段{str(r[5]):>3s} 坏字占比{r[6]:.2%} {str(r[2])[:40]}")
