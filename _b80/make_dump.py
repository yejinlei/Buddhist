# -*- coding: utf-8 -*-
import json, os
BASE="/home/user/workspace/13511660557912876654/buddhist-ontology"
IDS=["t0356","t0454","t1612","t1630","t2031","t1714","t0240","t1920","t1680","t0968","t1165","t2055"]
os.makedirs(BASE+"/_b80",exist_ok=True)
for tid in IDS:
    obj=json.load(open(f"{BASE}/data/baihua-tasks/{tid}.json",encoding="utf-8"))
    trs=obj["translations"]
    lines=[]
    lines.append("="*70)
    lines.append(f"FILE {tid}.json | {obj['title']} | {obj.get('translator','')} | intro={obj.get('intro','')!r}")
    lines.append("-"*70)
    for i,t in enumerate(trs):
        lines.append(f"[{i:02d}]")
        lines.append("ORIG: "+t["original_preview"].rstrip())
    open(f"{BASE}/_b80/dump_{tid}.txt","w",encoding="utf-8").write("\n".join(lines)+"\n")
    print(tid, len(trs), "segs")
