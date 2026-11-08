# -*- coding: utf-8 -*-
"""第54批构建公共模块。
preview 由原文按锚点机械切片，保证各段拼接 = 原文连续子串（一字不差）。
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUT = os.path.join(ROOT, "sutras")
TR = os.path.join(ROOT, "data", "modern-translation")


def raw_of(tid):
    d = json.load(open(os.path.join(SUT, tid + ".json"), encoding="utf-8"))
    return "\n".join(c["text"] for c in d["content"])


def build(tid, anchors, moderns, **meta):
    raw = raw_of(tid)
    assert anchors[0] == raw[:len(anchors[0])], f"{tid} 首锚点不在文首"
    pos, cur = [], 0
    for a in anchors:
        i = raw.find(a, cur)
        assert i >= 0, f"{tid} 锚点未找到: {a!r}"
        pos.append(i)
        cur = i + 1
    pos.append(len(raw))
    segs = []
    for k, a in enumerate(anchors):
        prev = raw[pos[k]:pos[k + 1]]
        segs.append({"section": re.match(r"^【(.+?)】", moderns[k]).group(1),
                     "original_preview": prev,
                     "modern": moderns[k]})
    out = {"id": tid, "title": meta.get("title", tid),
           "translator": meta.get("translator", ""), "mode": "full",
           "sutraPath": f"sutras/{tid}.json", "translations": segs}
    json.dump(out, open(os.path.join(TR, tid + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"OK {tid} 段数={len(segs)} 覆盖字符={sum(len(s['original_preview']) for s in segs)}/{len(raw)}")
