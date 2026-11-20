#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, json, re, glob

ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
SUT = os.path.join(ROOT, "sutras")

# 收集已完成经号：从各 _bXXX/out/ 以及 PROGRESS.md 里记录的
done = set()
# 从批次 out 目录收集
for d in glob.glob(os.path.join(ROOT, "_b*/out")):
    for f in os.listdir(d):
        if f.endswith(".txt"):
            done.add(f.replace(".txt", ""))

# 明确排除历史已出现的经号（来自去重列表 + PROGRESS已出现）
exclude_list = {
    # 用户给的去重列表
    "t2075","t1251","t0953","t0887","t2871","t0682","t0341","t1757","t2810","t1797","t2812","t2089",
    "t0299","t0424","t0342","t1864","t2073","t1758","t0649","t2156","t2800","t1339","t1006","t0853",
    "t0889","t1050","t1722","t1890","t0362","t0434","t0626",
    "t2799","t1550","t2146","t1986","t1444","t2151","t0627","t0291","t0722","t1955","t1332","t0946",
    # 第200批
    "t2147","t0288","t1308","t1584","t2155","t0635","t1670b","t1819","t1769","t1424","t1532","t2797",
}
done.update(exclude_list)

# PUA私用区字符区间 U+E000 - U+F8FF
def has_pua(s):
    for ch in s:
        cp = ord(ch)
        if 0xE000 <= cp <= 0xF8FF:
            return True
    return False

candidates = []
for fn in os.listdir(SUT):
    if not fn.endswith(".json"):
        continue
    tid = fn.replace(".json","")
    if tid in done:
        continue
    try:
        d = json.load(open(os.path.join(SUT, fn), encoding="utf-8"))
        if isinstance(d, list):
            texts = [c["text"] if isinstance(c, dict) else str(c) for c in d]
            title = tid
            translator = ""
        else:
            texts = [c["text"] if isinstance(c, dict) else str(c) for c in d.get("content", [])]
            title = d.get("title", tid)
            translator = d.get("translator", "")
        raw = "\n".join(texts)
        raw_norm = re.sub(r"\s+","",raw)
        n = len(raw_norm)
        if n < 8000:  # 短篇中篇已尽，取长篇>=8000字
            continue
        # 检查PUA
        if has_pua(raw_norm):
            continue
        # 阙文占比
        missing = raw_norm.count("□")
        miss_ratio = missing / n if n>0 else 1
        if miss_ratio > 0.05:  # 阙文超过5%跳过
            continue
        # 标题含咒/陀罗尼/真言暂放后面
        candidates.append((tid, title, translator, n, miss_ratio, missing))
    except Exception as e:
        pass

# 按字数升序，先取较短长篇
candidates.sort(key=lambda x: x[3])
print(f"共找到候选经文 {len(candidates)} 部，取前12部：")
print(f"{'经号':8s} {'字数':6s} {'阙文%':6s} {'经名':30s}  译者")
for c in candidates[:20]:
    print(f"{c[0]:8s} {c[3]:6d} {c[4]*100:5.2f}% {c[1][:28]:30s}  {c[2][:20]}")

# 保存本批列表
batch = candidates[:12]
with open(os.path.join(ROOT, "_batch205.txt"), "w", encoding="utf-8") as f:
    for c in batch:
        f.write(c[0] + "\n")
print("\n本批12部经号已写入 _batch205.txt")
