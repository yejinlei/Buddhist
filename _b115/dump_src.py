# -*- coding: utf-8 -*-
import json, os, sys
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
TASK=os.path.join(ROOT,"data","baihua-tasks")
OUT=os.path.join(ROOT,"_b115")
def dump(tid):
    d=json.load(open(os.path.join(TASK,tid+".json"),encoding="utf-8"))
    tr=d["translations"]
    head=f"# {tid} {d.get('title','')} | {d.get('translator','')} | 段数={len(tr)}"
    lines=[head]
    for i,t in enumerate(tr):
        lines.append(f"---[{i}]---")
        lines.append(t["original_preview"])
    open(os.path.join(OUT,tid+".src.txt"),"w",encoding="utf-8").write("\n".join(lines)+"\n")
    print(tid, len(tr))
for tid in sys.argv[1:]:
    dump(tid)
