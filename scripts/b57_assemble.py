# -*- coding: utf-8 -*-
"""第57批：把 worker 输出组装为规范译文 JSON，保留 original_preview 原样。"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK = os.path.join(ROOT, "data", "baihua-tasks")
OUT  = os.path.join(ROOT, "_b57", "out")
TR   = os.path.join(ROOT, "data", "modern-translation")

def norm(s): return re.sub(r"\s+", "", s)

def parse_out(path):
    txt = open(path, encoding="utf-8").read()
    blocks = re.split(r'=====\s*经号\s*(\S+?)\s*\|', txt)
    res = {}
    for i in range(1, len(blocks), 2):
        tid = blocks[i].strip()
        body = blocks[i + 1]
        segs = {}
        parts = re.split(r'\[段(\d+)\]', body)
        for j in range(1, len(parts), 2):
            n = int(parts[j])
            t = parts[j + 1].strip()
            segs[n] = t
        res[tid] = segs
    return res

def main():
    files = sys.argv[1:]
    parsed = {}
    for f in files:
        p = os.path.join(OUT, f)
        parsed.update(parse_out(p))
    for tid, segs in parsed.items():
        skel = json.load(open(os.path.join(TASK, tid + ".json"), encoding="utf-8"))
        trs = skel["translations"]
        if len(trs) != len(segs):
            print("!! %s 段数不符 骨架%d vs 输出%d" % (tid, len(trs), len(segs)))
            continue
        missing = [i for i in range(1, len(trs) + 1) if not segs.get(i)]
        if missing:
            print("!! %s 缺段 %s" % (tid, missing))
        skel["sutraPath"] = "sutras/%s.json" % tid
        if not skel.get("mode") or skel["mode"] == "baihua":
            skel["mode"] = "直译"
        # 原文子串校验
        raw = open(os.path.join(ROOT, "sutras", tid + ".json"), encoding="utf-8")
        d = json.load(raw)
        otext = norm("\n".join(c["text"] for c in d.get("content", [])))
        for i, seg in enumerate(trs, 1):
            m = segs.get(i, "")
            seg["modern"] = m
            mm = re.match(r'【([^】]+)】', m)
            seg["section"] = mm.group(1) if mm else ""
            if norm(seg["original_preview"]) not in otext:
                print("!! %s 第%d段 preview 非子串" % (tid, i))
        out = os.path.join(TR, tid + ".json")
        json.dump(skel, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("OK %s -> %s (%d段)" % (tid, out, len(trs)))

if __name__ == "__main__":
    main()
