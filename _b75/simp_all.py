# -*- coding: utf-8 -*-
import json
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
TR=ROOT+"/data/modern-translation"
h2s=json.load(open(ROOT+"/data/hant2simp_full.json",encoding="utf-8"))
PROTECT=set("乾徵絺")
def simp(s): return "".join(h2s.get(c,c) if (c in h2s and c not in PROTECT) else c for c in s)
ids=['t0726','t0731','t0737','t0738','t0812','t0828','t0835','t0845','t1011','t1297','t1755','t2757']
for sid in ids:
    d=json.load(open(f"{TR}/{sid}.json",encoding="utf-8"))
    ch=0
    for s in d["translations"]:
        o=s["modern"]; m=simp(o)
        if m!=o: ch+=1
        s["modern"]=m
    if "intro" in d: d["intro"]=simp(d["intro"])
    json.dump(d,open(f"{TR}/{sid}.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
    print(sid,"修改段:",ch)
