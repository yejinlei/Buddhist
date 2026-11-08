# -*- coding: utf-8 -*-
import json, os, re
BASE="/home/user/workspace/13511660557912876654/buddhist-ontology"
IN=BASE+"/data/baihua-tasks"; OUT=BASE+"/_b80"
IDS=["t0356","t0454","t1612","t1630","t2031","t1714","t0240","t1920","t1680","t0968","t1165","t2055"]
ok=True
for sid in IDS:
    obj=json.load(open(f"{IN}/{sid}.json",encoding="utf-8"))
    tr=json.load(open(f"{OUT}/src_{sid}.json",encoding="utf-8"))
    segs=obj["translations"]
    if len(segs)!=len(tr):
        print("!! 段数不符",sid,len(segs),len(tr)); ok=False; continue
    before=[s["original_preview"] for s in segs]
    for i,(s,t) in enumerate(zip(segs,tr)):
        sec=t["section"]; mod=t["modern"]
        errs=[]
        if not (1<=len(sec)<=14): errs.append(f"seclen={len(sec)}")
        if any(c in sec for c in "【】《》\"'"): errs.append("sec_char")
        if not mod.startswith("【"+sec+"】"): errs.append("head")
        if "【义解】" not in mod: errs.append("no_yijie")
        if mod.rstrip().endswith("】"): errs.append("end_brace")
        if '"' in mod or "'" in mod: errs.append("quote")
        if "```" in mod: errs.append("fence")
        if errs: print("!! ",sid,i,errs); ok=False
        s["section"]=sec; s["modern"]=mod
    after=[s["original_preview"] for s in segs]
    if before!=after: print("!! preview 被改",sid); ok=False
    json.dump(obj,open(f"{OUT}/modern_{sid}.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print(f"{sid}  {len(segs)} 段  OK")
print("ALL OK" if ok else "HAS ERRORS")
