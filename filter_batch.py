#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""筛选合格经文：段数≥3，剔除PUA和阙文占比超5%"""
import json, os, glob, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if __name__ != "__main__" else os.getcwd()
os.chdir(ROOT)
tr_dir = "data/modern-translation"
done = set(os.path.basename(p)[:-5] for p in glob.glob(tr_dir + "/*.json"))
SKIP = {"hant2simp","index","index-light","search-index","search-word-index"}
rows = []

# PUA字符范围
pua_pattern = re.compile(r'[\uF000-\uF8FF\U000F0000-\U000FFFFD\U00100000-\U0010FFFD]')
que_pattern = re.compile(r'□')

for p in glob.glob("sutras/*.json"):
    sid = os.path.basename(p)[:-5]
    if sid in done or sid in SKIP: continue
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception: continue
    if not isinstance(d, dict): continue
    content = d.get("content", [])
    if not isinstance(content, list): content = []
    txt = "".join((c.get("text","") if isinstance(c,dict) else str(c)) for c in content)
    n = len("".join(txt.split()))
    if n == 0: continue
    # 统计问题字符数
    pua_count = len(pua_pattern.findall(txt))
    que_count = len(que_pattern.findall(txt))
    bad_ratio = (pua_count + que_count) / n
    if bad_ratio > 0.05: continue
    if len(content) < 3: continue # 段数≥3
    rows.append((n, sid, d.get("title",""), d.get("translator",""), d.get("vol",""), len(content), bad_ratio))

# 按字数升序排序
rows.sort(key=lambda r:(r[0]))
print(f"段数≥3、问题占比<5%的合格经文总数: {len(rows)}")
print("-"*90)
print(f"{'经号':12s} {'字数':>5s} {'段数':>3s} {'问题占比':>8s} {'经名':32s} {'译者':18s} {'册号'}")
print("-"*90)
batch = []
for r in rows[:20]:
    ratio_str = f"{r[6]*100:>5.2f}%"
    print(f"{r[1]:12s} {r[0]:5d} {r[5]:3d} {ratio_str:8s} {str(r[2])[:32]:34s} {str(r[3])[:18]:20s} {r[4]}")
    batch.append(r[1])

print("\n本批选取经号:")
sids = batch[:12]
print(" ".join(sids))
# 输出前12个经号到文件
with open("/tmp/batch_sids.txt", "w", encoding="utf-8") as f:
    f.write(" ".join(sids))
