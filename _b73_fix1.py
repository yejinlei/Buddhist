# -*- coding: utf-8 -*-
import json, re
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
TR=ROOT+"/data/modern-translation"; TK=ROOT+"/data/baihua-tasks"
h2s=json.load(open(ROOT+"/data/hant2simp_full.json",encoding="utf-8"))

def simplify(m, protect_quotes):
    out=[]; inq=False
    for ch in m:
        if ch=="「": inq=True; out.append(ch)
        elif ch=="」": inq=False; out.append(ch)
        elif inq and protect_quotes: out.append(ch)
        else: out.append(h2s.get(ch,ch))
    return "".join(out)

# tid -> protect_quotes
jobs={"t2821":None,"t2863":None,"t2817":False,"t1265":True}
for tid,prot in jobs.items():
    tf=f"{TR}/{tid}.json"; kf=f"{TK}/{tid}.json"
    d=json.load(open(tf,encoding="utf-8"))
    tk=json.load(open(kf,encoding="utf-8"))
    assert len(d["translations"])==len(tk["translations"]), tid
    for i,s in enumerate(d["translations"]):
        s["original_preview"]=tk["translations"][i]["original_preview"]
        if prot is not None:
            s["modern"]=simplify(s["modern"], prot)
    json.dump(d,open(tf,"w",encoding="utf-8"),ensure_ascii=False,indent=2)
    # 报告
    ntr=sum((1 for s in d["translations"] for ch in s["modern"] if ch in h2s))
    print(f"{tid} 修复完成 段={len(d['translations'])} 剩余可转简字数={ntr}")
