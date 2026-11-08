# -*- coding: utf-8 -*-
"""
机械切段：把经文原文切成若干段，供翻译 worker 逐段译白话。
核心保证：每段 original_preview 都是原文的【连续子串】（一字不差）。
用法：
  python3 scripts/segment_baihua.py t0014 t0027 ...        # 生成骨架
  python3 scripts/segment_baihua.py --check t0014 ...      # 校验预览子串性
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUT  = os.path.join(ROOT, "sutras")
TASK = os.path.join(ROOT, "data", "baihua-tasks")

def norm(s): return re.sub(r"\s+", "", s)

def load_raw(tid):
    p = os.path.join(SUT, tid + ".json")
    d = json.load(open(p, encoding="utf-8"))
    if isinstance(d, list):
        texts = [c["text"] if isinstance(c, dict) else str(c) for c in d]
        meta = {}
    else:
        texts = [c["text"] if isinstance(c, dict) else str(c) for c in d.get("content", [])]
        meta = d
    raw = "\n".join(texts)
    return raw, meta

SPLIT_RE = re.compile(r'(?<=[。！？；：」』）\)\n])')

def segment(raw, lo=90, hi=400):
    parts = [p for p in SPLIT_RE.split(raw) if p != ""]
    segs, buf = [], ""
    for p in parts:
        # 单句过长时按逗号再切
        if len(norm(p)) > hi:
            sub = re.split(r'(?<=[，、])', p)
            for q in sub:
                if not q: continue
                buf += q
                if len(norm(buf)) >= lo:
                    segs.append(buf); buf = ""
            continue
        buf += p
        if len(norm(buf)) >= lo:
            segs.append(buf); buf = ""
    if buf.strip():
        if segs and len(norm(buf)) < 30:
            segs[-1] += buf
        else:
            segs.append(buf)
    return segs

def build_task(tid):
    raw, meta = load_raw(tid)
    segs = segment(raw)
    total = norm(raw)
    cov = sum(len(norm(s)) for s in segs)
    print(f"{tid:6s}  {meta.get('title','')[:30]:30s}  段={len(segs)}  覆盖={cov/len(total):.3f}")
    os.makedirs(TASK, exist_ok=True)
    task = {
        "id": tid,
        "title": meta.get("title", ""),
        "translator": meta.get("translator", ""),
        "vol": meta.get("vol", ""),
        "translations": [{"original_preview": s, "modern": ""} for s in segs]
    }
    json.dump(task, open(os.path.join(TASK, tid+".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return len(segs), cov/len(total)

def check_task(tid):
    task = json.load(open(os.path.join(TASK, tid+".json"), encoding="utf-8"))
    raw, _ = load_raw(tid)
    raw_norm = norm(raw)
    pos = 0
    ok = True
    for i, t in enumerate(task["translations"]):
        op = norm(t["original_preview"])
        idx = raw_norm.find(op, pos)
        if idx < 0:
            print(f"  ❌ 段{i}: 预览不是原文连续子串")
            ok = False
        else:
            pos = idx + len(op)
    if pos != len(raw_norm):
        print(f"  ❌ 总长度不匹配: 拼接={pos}, 原文={len(raw_norm)}")
        ok = False
    if ok:
        print(f"  ✅ {tid} 校验通过")
    return ok

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("用法: python3 segment_baihua.py t0014 t0027 ...")
        sys.exit(1)
    if args[0] == "--check":
        for tid in args[1:]:
            check_task(tid)
    else:
        for tid in args:
            build_task(tid)
