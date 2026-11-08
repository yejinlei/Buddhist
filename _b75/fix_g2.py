# -*- coding: utf-8 -*-
import json, re
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
TR=ROOT+"/data/modern-translation"
h2s=json.load(open(ROOT+"/data/hant2simp_full.json",encoding="utf-8"))
PROTECT=set("乾徵")  # 专名用字不转
def simp(s):
    return "".join(h2s.get(c,c) if (c in h2s and c not in PROTECT) else c for c in s)
for sid in ["t0738","t0812","t0828"]:
    d=json.load(open(f"{TR}/{sid}.json",encoding="utf-8"))
    n=0
    for s in d["translations"]:
        m=s["modern"]
        # 1) 插入【义解】到第一个】之后
        if "【义解】" not in m:
            i=m.find("】")
            if i>=0:
                m=m[:i+1]+"【义解】"+m[i+1:]
                n+=1
        # 2) 转简体
        m=simp(m)
        s["modern"]=m
    # intro 也转简
    if "intro" in d: d["intro"]=simp(d["intro"])
    json.dump(d,open(f"{TR}/{sid}.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
    print(sid,"插入【义解】",n,"段; intro转简完成")
