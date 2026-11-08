# -*- coding: utf-8 -*-
"""第64批 修正脚本：
1) 咒文展示块（正文中「」内的陀罗尼）回正为原文原字（繁体/原用字）；
2) 义解中「」引用经文原语者，回正为原文原字；
3) t1658 叙述性引用「盎、阿（引）、吽」简化为「盎、阿、吽」。
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

def dehint(t):
    o = json.load(open(f"{SUT}/{t}.json", encoding="utf-8"))
    raw = norm("".join(c["text"] for c in o["content"]))
    return re.sub(r"（[^）]*）", "", raw)

ALL = "t0924a t1181 t1384 t0841 t0832 t1162 t0693 t0747a t1903 t2047b t1882 t1658".split()

# ---- Step B: 咒文展示块回正（t1384 全部；t1162 idx5-7） ----
CURSE_DISPLAY = {
    "t1384": list(range(1, 15)),   # seg2..seg15 (0-indexed 1..14)
    "t1162": [5, 6, 7],            # seg6,7,8
}
for tid, idxs in CURSE_DISPLAY.items():
    d = load(tid)
    for i in idxs:
        seg = d["translations"][i]
        m = seg["modern"]; p = seg["original_preview"].strip()
        lead = p.startswith("「")
        if lead: p = p[1:]
        # 若有 」 且有后续叙述，截断
        if "」" in p:
            before, after = p.split("」", 1)
            if re.search(r"[\u4e00-\u9fff]", after):
                pcurse = before
                newblock = "「" + pcurse + "」"
            else:
                newblock = "「" + p + "」"
        else:
            newblock = "「" + p + "」"
        yj = m.find("【义解】")
        head = m[:yj]
        tail = m[yj:]
        ti = head.index("】") + 1
        title = head[:ti]
        old = head[ti:]
        if "」" in old:
            # 替换第一个 「...」
            old2 = re.sub(r"「[^」]*」", newblock, old, count=1)
        else:
            old2 = newblock
        seg["modern"] = title + old2 + tail
    save(tid, d)
    print("stepB", tid, "ok")

# ---- Step C: t1658 叙述引用简化 ----
d = load("t1658")
for seg in d["translations"]:
    seg["modern"] = seg["modern"].replace("「盎、阿（引）、吽」", "「盎、阿、吽」")
save("t1658", d)

# ---- Step A: 义解中「」引经文原语回正 ----
for tid in ALL:
    deh = dehint(tid); ds = simp(deh)
    d = load(tid)
    changed = [0]
    for seg in d["translations"]:
        m = seg["modern"]; idx = m.find("【义解】")
        if idx < 0: continue
        head, yj = m[:idx], m[idx:]
        def repl(mo):
            frag = mo.group(1)
            f = re.sub(r"（[^）]*）", "", norm(frag))
            fs = simp(f)
            p = ds.find(fs)
            if p >= 0:
                orig = deh[p:p+len(fs)]
                if orig != f:
                    changed[0] += 1
                    return "「" + orig + "」"
            return mo.group(0)
        yj2 = re.sub(r"「([^」]+)」", repl, yj)
        seg["modern"] = head + yj2
    save(tid, d)
    print("stepA", tid, "changed", changed[0])
