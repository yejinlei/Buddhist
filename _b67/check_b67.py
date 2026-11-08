# -*- coding: utf-8 -*-
"""第67批 独立校检：体例（半角引号/标点）、繁简混排、标题一致性、繁简泄漏。
用法：python3 _b67/check_b67.py t1682 ...
"""
import json, os, re, sys, glob

B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(B)
TR = os.path.join(ROOT, "data/modern-translation")

# 繁简对照：key 为繁体
H2S = json.load(open(os.path.join(ROOT, "data/hant2simp_full.json"), encoding="utf-8"))
def is_hant(ch):
    return ch in H2S and H2S[ch] != ch

def strip_quotes(s):
    # 去掉「...」『...』引用部分（原文照录/引文），只留叙述
    return re.sub(r"「[^」]*」", "", re.sub(r"『[^』]*』", "", s))

def check(tid):
    p = os.path.join(TR, tid + ".json")
    d = json.load(open(p, encoding="utf-8"))
    probs = []
    for i, s in enumerate(d["translations"], 1):
        mo = s["modern"]
        # 1) 半角引号
        if re.search(r'["\']', mo):
            probs.append((i, "半角引号", re.findall(r'.{0,8}["\'].{0,8}', mo)[:2]))
        # 2) 标题一致性
        m = re.match(r"^【(.+?)】", mo)
        if m and s["section"] and m.group(1) != s["section"]:
            probs.append((i, "标题不符", (m.group(1), s["section"])))
        # 3) 繁简泄漏（叙述部分）
        narr = strip_quotes(mo)
        hant = sorted({c for c in narr if is_hant(c)})
        if hant:
            probs.append((i, "繁简", "".join(hant[:12])))
        # 4) 义解标记
        if "【义解】" not in mo:
            probs.append((i, "缺义解", ""))
    return probs

ids = sys.argv[1:] or [os.path.basename(f)[:-5] for f in glob.glob(TR + "/t*.json")]
tot = 0
for tid in ids:
    pr = check(tid)
    if pr:
        tot += len(pr)
        print("==", tid)
        for x in pr[:8]:
            print("   段%d %s %s" % x)
print("问题合计", tot)
