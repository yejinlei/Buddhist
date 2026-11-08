# -*- coding: utf-8 -*-
import json, re, os
BASE="/home/user/workspace/13511660557912876654/buddhist-ontology"
IDS=["t0356","t0454","t1612","t1630","t2031","t1714"]

def strip_ws(s):
    return re.sub(r"\s+","",s)

def parse_review(tid):
    path=f"{BASE}/_b80/review_{tid}.txt"
    lines=open(path,encoding="utf-8").read().split("\n")
    segs=[]
    cur=None
    for ln in lines:
        m=re.match(r"^\[(\d+)\] SECTION: (.*)$",ln)
        if m:
            if cur: segs.append(cur)
            cur={"idx":int(m.group(1)),"section":m.group(2),"orig":[],"modern":[]}
            continue
        if cur is None: continue
        if ln.startswith("ORIG: "):
            cur["orig"].append(ln[6:])
        elif ln.startswith("MODERN: "):
            cur["modern"].append(ln[8:])
        elif ln.startswith("-"*10):
            continue
        elif ln.startswith("="*10):
            continue
        elif ln.startswith(tid):  # header line
            continue
        else:
            # continuation of orig or modern
            if cur["modern"]:
                cur["modern"].append(ln)
            elif cur["orig"]:
                cur["orig"].append(ln)
    if cur: segs.append(cur)
    for s in segs:
        s["orig"]="\n".join(s["orig"])
        s["modern"]="\n".join(s["modern"])
    return segs

def load_content(tid):
    o=json.load(open(f"{BASE}/sutras/{tid}.json",encoding="utf-8"))
    return "\n".join(ch["text"] for ch in o["content"])

if __name__=="__main__":
    for tid in IDS:
        segs=parse_review(tid)
        content=load_content(tid)
        cw=strip_ws(content)
        # find ORIG positions
        pos=[]; ok=True; cursor=0
        for s in segs:
            ow=strip_ws(s["orig"])
            p=cw.find(ow,cursor)
            if p<0:
                # try whole
                p2=cw.find(ow)
                print(f"!! {tid} 段{s['idx']:02d} ORIG 非连续子串 (anywhere={p2})")
                ok=False
                pos.append(None)
                continue
            pos.append(p)
            cursor=p+len(ow)
        # check contiguity/coverage
        cov=[]
        for s,p in zip(segs,pos):
            if p is None: cov.append((s['idx'],None,None)); continue
            cov.append((s['idx'],p,p+len(strip_ws(s['orig']))))
        # check monotonic & contiguous
        contiguous=True
        prev_end=None
        for idx,p,e in cov:
            if p is None: continue
            if prev_end is not None and p!=prev_end:
                contiguous=False
                print(f"   {tid}: 段{idx} 起始{p} != 前段末{prev_end} (gap/overlap {p-prev_end})")
            prev_end=e
        covered = strip_ws("".join(s["orig"] for s in segs))
        print(f"{tid}: 段数={len(segs)} ORIG子串OK={ok} 连续={contiguous} 覆盖长度={len(covered)}/原文{len(cw)}")
