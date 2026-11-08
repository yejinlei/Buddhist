# -*- coding: utf-8 -*-
"""第67批 生成器：把 _b67/notes_*.py 的 (section, modern模板) 填入骨架，
生成 data/modern-translation/t*.json。
- modern 模板中的 {P} 程序化替换为该段 original_preview 原文（一字不动），
  保证音译/咒文照录零差错。
- original_preview 一律取自骨架；生成后做体例自检与红线（连续子串）校验。
用法：python3 _b67/gen_b67.py            # 处理全部 notes_*.py
      python3 _b67/gen_b67.py t1682 ...  # 只处理指定经号
"""
import json, os, glob, importlib.util, re, sys

B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(B)
TASKS = os.path.join(ROOT, "data/baihua-tasks")
OUT = os.path.join(ROOT, "data/modern-translation")

def L(path):
    spec = importlib.util.spec_from_file_location("m_" + os.path.basename(path)[:-3], path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def norm(s): return re.sub(r"\s+", "", s)

def load_orig(tid):
    d = json.load(open(os.path.join(ROOT, "sutras", tid + ".json"), encoding="utf-8"))
    return norm("\n".join(c["text"] for c in d["content"]))

NOTES = {}
for f in sorted(glob.glob(os.path.join(B, "notes_*.py"))):
    NOTES.update(L(f).NOTES)

args = sys.argv[1:]
tids = args if args else sorted(NOTES.keys())

ok = 0
for tid in tids:
    cfg = NOTES[tid]
    sk = json.load(open(os.path.join(TASKS, tid + ".json"), encoding="utf-8"))
    trs = sk["translations"]
    segs = cfg["segs"]
    assert len(segs) == len(trs), "段数不符 %s 骨架%d 数据%d" % (tid, len(trs), len(segs))
    trs_out = []
    for i, (sec, tmpl) in enumerate(segs):
        P = trs[i]["original_preview"]

        def _c(m, _P=P, _tid=tid, _n=i + 1):
            a, b = m.group(1), m.group(2)
            k = _P.find(a)
            assert k >= 0, "%s 段%d 起点定位失败: %r" % (_tid, _n, a)
            if b == "":
                return _P[k:]
            j = _P.find(b, k)
            assert j >= 0, "%s 段%d 终点定位失败: %r" % (_tid, _n, b)
            return _P[k:j + len(b)]

        mod = re.sub(r"\{C\|(.*?)\|(.*?)\}", _c, tmpl)
        mod = mod.replace("{P}", P)
        assert mod.startswith("【"), "%s 段%d 未以【开头" % (tid, i + 1)
        assert "【义解】" in mod, "%s 段%d 缺【义解】" % (tid, i + 1)
        assert not mod.rstrip().endswith("【义解】"), "%s 段%d 义解后无正文" % (tid, i + 1)
        trs_out.append({"section": sec, "original_preview": P, "modern": mod})
    out = {
        "id": tid,
        "title": sk["title"],
        "translator": sk["translator"],
        "mode": "baihua",
        "intro": cfg["intro"],
        "sutraPath": sk.get("sutraPath", "../sutras/%s.json" % tid),
        "translations": trs_out,
    }
    cat = norm("".join(t["original_preview"] for t in trs_out))
    orig = load_orig(tid)
    assert cat in orig, "%s preview 非原文连续子串" % tid
    json.dump(out, open(os.path.join(OUT, tid + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ok += 1
    print("wrote %s 段%d cover=%.4f" % (tid, len(trs_out), len(cat) / len(orig)))
print("wrote", ok, "部")
