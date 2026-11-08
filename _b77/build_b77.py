# -*- coding: utf-8 -*-
"""第77批 build：把 _b77/modern_*.json 中的译文填入切段骨架，输出 data/modern-translation/<id>.json。
红线：original_preview 一律照抄骨架，只填 intro（若提供）与 modern。"""
import json, os, glob, sys

ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)

def load_modern():
    mp = {}
    for p in sorted(glob.glob("_b77/modern_*.json")):
        d = json.load(open(p, encoding="utf-8"))
        for k, v in d.items():
            if k in mp:
                print("!! 重复经号", k, "in", p)
            mp[k] = v
    return mp

def build(tid, intro, modern):
    sk = json.load(open(f"data/baihua-tasks/{tid}.json", encoding="utf-8"))
    segs = sk["translations"]
    if len(segs) != len(modern):
        print(f"!! {tid} 段数不符 骨架={len(segs)} modern={len(modern)}")
        return False
    if intro:
        sk["intro"] = intro
    for i, s in enumerate(segs):
        m = modern[i]
        if isinstance(m, str) and m.startswith("@@PREVIEW@@"):
            m = m[len("@@PREVIEW@@"):] + "\n" + s["original_preview"]
        s["modern"] = m
    out = f"data/modern-translation/{tid}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(sk, f, ensure_ascii=False, indent=1)
    # 自检
    d2 = json.load(open(out, encoding="utf-8"))
    assert len(d2["translations"]) == len(segs)
    json.dumps(d2, ensure_ascii=False)
    print(f"{tid} 写入完成 段={len(segs)}")
    return True

def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    mp = load_modern()
    ok = 0
    for tid, v in mp.items():
        if only and tid not in only:
            continue
        if build(tid, v.get("intro"), v["modern"]):
            ok += 1
    print(f"== 本批写入 {ok} 部 ==")

if __name__ == "__main__":
    main()
