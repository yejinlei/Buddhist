# -*- coding: utf-8 -*-
import json,re
from parse import parse_review, IDS
BASE="/home/user/workspace/13511660557912876654/buddhist-ontology"
h=json.load(open(f"{BASE}/sutras/hant2simp.json",encoding="utf-8"))
trad=set(h.keys())
def strip_quotes(t):
    # remove content inside 「」 (and nested simple)
    prev=None
    while prev!=t:
        prev=t
        t=re.sub(r"「[^「」]*」","",t)
    return t
for tid in IDS:
    segs=parse_review(tid)
    for s in segs:
        mod=s["modern"]
        core=strip_quotes(mod)
        hits=[]
        for i,c in enumerate(core):
            if c in trad:
                hits.append((i,c))
        if hits:
            print(f"=== {tid} 段{s['idx']:02d} ===")
            for i,c in hits:
                print(f"   [{c}] ...{core[max(0,i-14):i+15]}...")
