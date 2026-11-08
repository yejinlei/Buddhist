# -*- coding: utf-8 -*-
"""第64批 构建：把 data_p1~p4.py 中的 (section, modern) 填入骨架，
逐段生成 data/modern-translation/t*.json。
original_preview 一律取自骨架、一字不动。
"""
import json, os, importlib.util

B = os.path.dirname(os.path.abspath(__file__))
def L(n):
    spec = importlib.util.spec_from_file_location(n, os.path.join(B, n + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

p1, p2, p3, p4 = L("data_p1"), L("data_p2"), L("data_p3"), L("data_p4")
ROOT = os.path.dirname(B)
TASKS = os.path.join(ROOT, "data/baihua-tasks")
OUT = os.path.join(ROOT, "data/modern-translation")

SRC, INTRO = {}, {}
for p in (p1, p2, p3, p4):
    INTRO.update(p.INTRO)
    for k, v in vars(p).items():
        if k.startswith("T") and isinstance(v, list):
            SRC[k.lower()] = v

ok = 0
for tid, segs in sorted(SRC.items()):
    sk = json.load(open(os.path.join(TASKS, tid + ".json"), encoding="utf-8"))
    trs = sk["translations"]
    assert len(trs) == len(segs), "段数不符 %s 骨架%d 数据%d" % (tid, len(trs), len(segs))
    out = {
        "id": tid,
        "title": sk["title"],
        "translator": sk["translator"],
        "mode": "baihua",
        "intro": INTRO[tid],
        "sutraPath": sk.get("sutraPath", "../sutras/%s.json" % tid),
        "translations": [
            {"section": sec, "original_preview": trs[i]["original_preview"], "modern": mod}
            for i, (sec, mod) in enumerate(segs)
        ],
    }
    json.dump(out, open(os.path.join(OUT, tid + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ok += 1
    # 逐段自检体例
    for i, s in enumerate(out["translations"], 1):
        m = s["modern"]
        assert m.startswith("【"), "%s 段%d 未以【开头" % (tid, i)
        assert "【义解】" in m, "%s 段%d 缺【义解】" % (tid, i)
        assert not m.rstrip().endswith("【义解】"), "%s 段%d 义解后无正文" % (tid, i)
print("wrote", ok, "部")
