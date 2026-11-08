# -*- coding: utf-8 -*-
"""第65批 构建：把 _b66/data_tXXXX.py 中的 (section, modern) 填入骨架，
生成 data/modern-translation/t*.json。original_preview 一律取自骨架、一字不动。
用法：python3 _b66/build_b66.py t0735 t0742 ...   （不传则处理 _b66 下全部 data_t*.py）
"""
import json, os, glob, importlib.util, re, sys

B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(B)
TASKS = os.path.join(ROOT, "data/baihua-tasks")
OUT = os.path.join(ROOT, "data/modern-translation")

def L(path):
    spec = importlib.util.spec_from_file_location("m", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def norm(s): return re.sub(r"\s+", "", s)

def load_orig(tid):
    d = json.load(open(os.path.join(ROOT, "sutras", tid + ".json"), encoding="utf-8"))
    return norm("\n".join(c["text"] for c in d["content"]))

args = sys.argv[1:]
files = sorted(glob.glob(os.path.join(B, "data_t*.py")))
if args:
    files = [os.path.join(B, "data_%s.py" % a) for a in args]

ok = 0
for f in files:
    m = L(f)
    INTRO = getattr(m, "INTRO", {})
    SRC = {k.lower(): v for k, v in vars(m).items()
           if k.startswith("T") and isinstance(v, list)}
    for tid, segs in sorted(SRC.items()):
        sk = json.load(open(os.path.join(TASKS, tid + ".json"), encoding="utf-8"))
        trs = sk["translations"]
        assert len(trs) == len(segs), "段数不符 %s 骨架%d 数据%d" % (tid, len(trs), len(segs))
        out = {
            "id": tid,
            "title": sk["title"],
            "translator": sk["translator"],
            "mode": "baihua",
            "intro": INTRO.get(tid, ""),
            "sutraPath": sk.get("sutraPath", "../sutras/%s.json" % tid),
            "translations": [
                {"section": sec, "original_preview": trs[i]["original_preview"], "modern": mod}
                for i, (sec, mod) in enumerate(segs)
            ],
        }
        # 体例自检
        for i, s in enumerate(out["translations"], 1):
            mo = s["modern"]
            assert mo.startswith("【"), "%s 段%d 未以【开头" % (tid, i)
            assert "【义解】" in mo, "%s 段%d 缺【义解】" % (tid, i)
            assert not mo.rstrip().endswith("【义解】"), "%s 段%d 义解后无正文" % (tid, i)
        # 红线：preview 拼接 = 原文连续子串
        cat = norm("".join(s["original_preview"] for s in out["translations"]))
        orig = load_orig(tid)
        assert cat in orig, "%s preview 非原文连续子串" % tid
        json.dump(out, open(os.path.join(OUT, tid + ".json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        ok += 1
        print("wrote %s 段%d cover=%.4f" % (tid, len(segs), len(cat)/len(orig)))
print("wrote", ok, "部")
