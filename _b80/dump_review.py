# -*- coding: utf-8 -*-
import json, os
BASE="/home/user/workspace/13511660557912876654/buddhist-ontology"
IDS=["t0356","t0454","t1612","t1630","t2031","t1714","t0240","t1920","t1680","t0968","t1165","t2055"]
for tid in IDS:
    o=json.load(open(f"{BASE}/sutras/{tid}.json",encoding="utf-8"))
    m=json.load(open(f"{BASE}/data/modern-translation/{tid}.json",encoding="utf-8"))
    trs=m["translations"]
    L=[]
    L.append("="*80)
    L.append(f"{tid} | {m['title']} | {m.get('translator','')} | 段数={len(trs)}")
    L.append("="*80)
    for i,t in enumerate(trs):
        L.append(f"[{i:02d}] SECTION: {t['section']}")
        L.append("ORIG: "+t["original_preview"].rstrip())
        L.append("MODERN: "+t["modern"].rstrip())
        L.append("-"*60)
    open(f"{BASE}/_b80/review_{tid}.txt","w",encoding="utf-8").write("\n".join(L)+"\n")
    print(tid,len(trs))
