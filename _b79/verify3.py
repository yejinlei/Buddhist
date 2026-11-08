# -*- coding: utf-8 -*-
import json, os, re
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
IDS=["t0470","t0784","t1927","t1657","t0593","t0516","t0709","t0556","t0831","t0746","t0074","t1083"]
def nows(s): return re.sub(r"\s+","",s)
def src_text(sid):
    d=json.load(open(os.path.join(ROOT,"sutras",sid+".json"),encoding="utf-8"))
    return "".join((c.get("text","") if isinstance(c,dict) else str(c)) for c in d.get("content",[]))
for sid in IDS:
    d=json.load(open(os.path.join(ROOT,"data/modern-translation",sid+".json"),encoding="utf-8"))
    src=nows(src_text(sid)); segs=d["translations"]
    cat=nows("".join(s["original_preview"] for s in segs))
    ok=cat in src
    print("### %s segs=%d src=%d cat=%d cat_in_src=%s"%(sid,len(segs),len(src),len(cat),ok))
    pos=0; bad=[]
    for i,s in enumerate(segs):
        p=nows(s["original_preview"]); idx=src.find(p,pos)
        if idx<0: bad.append((i+1,idx))
        else: pos=idx+len(p)
    print("   preview_mismatch:",bad if bad else "none")
    allmod="".join(s["modern"] for s in segs)
    print("   ascii_dq:",allmod.count('"'),"ascii_sq:",allmod.count("'"),"curly:",allmod.count('“')+allmod.count('”'))
