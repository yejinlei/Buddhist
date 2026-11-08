# -*- coding: utf-8 -*-
"""第40批：把 worker 输出文本组装为规范译文 JSON。
解析 worker 输出中的 [段N] 块，回填到机械切段骨架，保留 original_preview 原样（保证原文子串）。
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK = os.path.join(ROOT, "data", "baihua-tasks")
OUT  = os.path.join(ROOT, "_b40", "out")
TR   = os.path.join(ROOT, "data", "modern-translation")

def parse_out(path):
    txt = open(path, encoding="utf-8").read()
    blocks = re.split(r'=====\s*经号\s*(\S+?)\s*=====', txt)
    res = {}
    for i in range(1, len(blocks), 2):
        tid = blocks[i].strip()
        body = blocks[i + 1]
        segs = {}
        parts = re.split(r'\[段(\d+)\]', body)
        for j in range(1, len(parts), 2):
            n = int(parts[j])
            t = re.sub(r'\s+', '', parts[j + 1])
            segs[n] = t
        res[tid] = segs
    return res

def main():
    files = sys.argv[1:]
    parsed = {}
    for f in files:
        p = f if os.path.isabs(f) else os.path.join(OUT, f)
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
        # 修正顶层字段
        skel["sutraPath"] = "sutras/%s.json" % tid
        if not skel.get("mode") or skel["mode"] == "baihua":
            skel["mode"] = "直译"
        for i, seg in enumerate(trs, 1):
            m = segs.get(i, "")
            seg["modern"] = m
            mm = re.match(r'【([^】]+)】', m)
            seg["section"] = mm.group(1) if mm else ""
        out = os.path.join(TR, tid + ".json")
        json.dump(skel, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("OK %s -> %s (%d段)" % (tid, out, len(trs)))

if __name__ == "__main__":
    main()
