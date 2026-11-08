# -*- coding: utf-8 -*-
import json,re
from parse import parse_review, IDS
BASE="/home/user/workspace/13511660557912876654/buddhist-ontology"
h=json.load(open(f"{BASE}/sutras/hant2simp.json",encoding="utf-8"))
trad=set(h.keys())
for tid in IDS:
    segs=parse_review(tid)
    for s in segs:
        mod=s["modern"]
        hits=[]
        for i,c in enumerate(mod):
            if c in trad:
                hits.append((i,c))
        if hits:
            print(f"=== {tid} 段{s['idx']:02d} ===")
            for i,c in hits:
                ctx=mod[max(0,i-12):i+13]
                print(f"   [{c}] ...{ctx}...")
