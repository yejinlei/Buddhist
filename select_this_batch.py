#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, glob, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
tr_dir = "data/modern-translation"
done = set(os.path.basename(p)[:-5] for p in glob.glob(tr_dir + "/*.json"))
SKIP = {"hant2simp","index","index-light","search-index","search-word-index"}

def is_pua(c):
    cp = ord(c)
    return (0xF000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0xFFFFD) or (0x100000 <= cp <= 0x10FFFD)

lo = 400
hi = 2500
selected = []
remaining_needed = 12

# 先看所有未译的
all_untrans = []
for p in glob.glob("sutras/*.json"):
    sid = os.path.basename(p)[:-5]
    if sid in done or sid in SKIP: continue
    try: d = json.load(open(p, encoding="utf-8"))
    except Exception: continue
    if not isinstance(d, dict): continue
    content = d.get("content", [])
    if not isinstance(content, list): content = []
    txt = "".join((c.get("text","") if isinstance(c,dict) else str(c)) for c in content)
    clean_txt = "".join(txt.split())
    n = len(clean_txt)
    if n == 0: continue
    # 计算PUA和阙文占比
    pua_count = sum(1 for c in clean_txt if is_pua(c))
    que_count = clean_txt.count("□")
    total = len(clean_txt)
    pua_ratio = pua_count / total
    que_ratio = que_count / total
    if pua_ratio > 0.05 or que_ratio > 0.05:
        continue
    all_untrans.append((n, sid, d.get("title",""), d.get("translator",""), len(content), pua_ratio, que_ratio))

print(f"总合格未译经文数: {len(all_untrans)}")
# 按字数排序
all_untrans.sort(key=lambda r:(r[0]))
# 打印前30部看看
print("前30部最短合格经文：")
for r in all_untrans[:30]:
    print(f"{r[1]:10s} {r[0]:5d}字 段{str(r[4]):>3s} pua={r[5]:.3f} que={r[6]:.3f} {str(r[2])[:30]}")

# 选前12部
selected = [r[1] for r in all_untrans[:12]]
print(f"\n选定本批{len(selected)}部经文：")
for sid in selected:
    print(sid)

# 保存到文件
with open("current_batch.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(selected))
