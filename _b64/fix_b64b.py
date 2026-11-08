# -*- coding: utf-8 -*-
"""第64批 修正（v2，段号订正）：
1) 咒文展示块回正为原文原字（t1384 seg2-16；t1162 seg6-8）；
2) 正文与义解中「」引经文原语者回正为原字；
3) t1658 叙述性引用「盎、阿（引）、吽」简化。
original_preview 一字不动。
"""
import json, re, os

ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)
TR = "data/modern-translation"
SUT = "sutras"

def norm(s): return re.sub(r"\s+", "", s)
h2s = json.load(open("data/hant2simp_full.json", encoding="utf-8"))
def simp(s): return "".join(h2s.get(c, c) for c in s)
def load(t): return json.load(open(f"{TR}/{t}.json", encoding="utf-8"))
def save(t, d): json.dump(d, open(f"{TR}/{t}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- 1. 咒文展示块（精确段号） ----------
# t1384: seg2..seg15 为咒文（idx1..14），seg16（idx15）咒末
d = load("t1384")
for i in range(1, 15):                      # 段2~段15
    seg = d["translations"][i]
    p = seg["original_preview"].strip()
    if p.startswith("「"): p = p[1:]
    seg["modern"] = re.sub(r"「[^」]*」", lambda m: "「" + p + "」", seg["modern"], count=1)
# seg16: 「賀（引）（六十）」
seg = d["translations"][15]
seg["modern"] = re.sub(r"「[^」]*」", "「賀（引）（六十）」", seg["modern"], count=1)
save("t1384", d)

# t1162: seg6(idx5) 咒首、seg7(idx6)、seg8(idx7)
d = load("t1162")
def curse_of(preview):
    p = preview.strip()
    if "「" in p:
        p = p[p.index("「") + 1:]
    if "」" in p:
        b, a = p.split("」", 1)
        if re.search(r"[\u4e00-\u9fff]", a):
            return b, True
        return b, True
    return p, False
# idx5: 形如  陀罗尼曰：「『...（去聲）【义解】
seg = d["translations"][5]
cur, closed = curse_of(seg["original_preview"])
yj = seg["modern"].find("【义解】")
head, tail = seg["modern"][:yj], seg["modern"][yj:]
ti = head.index("】") + 1
seg["modern"] = head[:ti] + "陀罗尼曰：「" + cur + tail
# idx6: 形如 【...】「罰栗殺尼...（去聲）【义解】
seg = d["translations"][6]
cur, closed = curse_of(seg["original_preview"])
yj = seg["modern"].find("【义解】")
head, tail = seg["modern"][:yj], seg["modern"][yj:]
ti = head.index("】") + 1
seg["modern"] = head[:ti] + "「" + cur + tail
# idx7: 形如 【...】「凡...莎呵』」。「此陀羅尼...
seg = d["translations"][7]
cur, closed = curse_of(seg["original_preview"])
seg["modern"] = re.sub(r"「[^」]*」", lambda m: "「" + cur + "」", seg["modern"], count=1)
save("t1162", d)

# ---------- 2. t1658 叙述性引用 ----------
d = load("t1658")
for seg in d["translations"]:
    seg["modern"] = seg["modern"].replace("「盎、阿（引）、吽」", "「盎、阿、吽」").replace("「盎、阿（引）」", "「盎、阿」")
save("t1658", d)

# ---------- 3. 「」内引经文原语回正（正文 + 义解） ----------
ALL = "t0924a t1181 t1384 t0841 t0832 t1162 t0693 t0747a t1903 t2047b t1882 t1658".split()
for tid in ALL:
    o = json.load(open(f"{SUT}/{tid}.json", encoding="utf-8"))
    raw = norm("".join(c["text"] for c in o["content"]))
    od = re.sub(r"（[^）]*）", "", raw)
    ds = simp(od)
    d = load(tid)
    cnt = [0]
    for seg in d["translations"]:
        def repl(mo):
            frag = mo.group(1)
            f = re.sub(r"（[^）]*）", "", norm(frag))
            fs = simp(f)
            p = ds.find(fs)
            if p >= 0:
                o2 = od[p:p + len(fs)]
                if o2 != f:
                    cnt[0] += 1
                    return "「" + o2 + "」"
            return mo.group(0)
        seg["modern"] = re.sub(r"「([^」]+)」", repl, seg["modern"])
    save(tid, d)
    print("回正", tid, cnt[0])
