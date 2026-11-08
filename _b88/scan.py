# -*- coding: utf-8 -*-
import json, glob, os, sys, re, collections
tab = json.load(open("sutras/hant2simp.json", encoding="utf-8"))
tids = sys.argv[1:] or [os.path.basename(f)[:-5] for f in sorted(glob.glob("data/modern-translation/t*.json"))]
half_q, sec_mismatch, tail_yi, trad = [], [], [], collections.Counter()
trad_files = collections.Counter()
for tid in tids:
    p = f"data/modern-translation/{tid}.json"
    if not os.path.exists(p): continue
    d = json.load(open(p, encoding="utf-8"))
    for i, s in enumerate(d.get("translations", [])):
        m = s.get("modern", ""); sec = s.get("section", "")
        if '"' in m or "'" in m: half_q.append((tid, i))
        mm = re.match(r"^【(.+?)】", m)
        if not mm or mm.group(1) != sec: sec_mismatch.append((tid, i, sec))
        if m.rstrip().endswith("【义解】"): tail_yi.append((tid, i))
        for ch in m:
            if ch in tab:
                trad[ch] += 1; trad_files[tid] += 1
print("半角引号:", len(half_q), half_q[:5])
print("标题不一致:", len(sec_mismatch), sec_mismatch[:5])
print("以义解结尾:", len(tail_yi), tail_yi[:5])
print("繁体残留(受保护咒文除外应查):", sum(trad.values()), "字")
print("  涉及文件:", dict(trad_files))
print("  高频字:", trad.most_common(30))
