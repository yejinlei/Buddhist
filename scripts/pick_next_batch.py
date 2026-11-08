#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""挑未译经：可按字数区间或按段数筛选。"""
import json, os, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
tr_dir = "data/modern-translation"
done = set(os.path.basename(p)[:-5] for p in glob.glob(tr_dir + "/*.json"))
SKIP = {"hant2simp","index","index-light","search-index","search-word-index"}
rows = []
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
    rows.append((n, sid, d.get("title",""), d.get("translator",""), d.get("vol",""), len(content)))
print("未译总数:", len(rows))
mode = sys.argv[1] if len(sys.argv)>1 else "seg"
if mode == "seg":
    lo, hi, minseg = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    sel = [r for r in rows if lo<=r[0]<=hi and r[5]>=minseg]
    sel.sort(key=lambda r:(r[0]))
    for r in sel[:60]:
        print(f"{r[1]:10s} {r[0]:5d}字 段{str(r[5]):>3s} {str(r[2])[:30]:32s} {str(r[3])[:16]:18s} {r[4]}")
else:
    lo, hi, cnt = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    sel = [r for r in rows if lo<=r[0]<=hi][:cnt]
    for r in sel:
        print(f"{r[1]:10s} {r[0]:5d}字 段{str(r[5]):>3s} {str(r[2])[:30]:32s} {str(r[3])[:16]:18s} {r[4]}")
