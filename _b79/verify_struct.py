# -*- coding: utf-8 -*-
import json, os, re
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
IDS=["t0470","t0784","t1927","t1657","t0593","t0516","t0709","t0556","t0831","t0746","t0074","t1083"]
ASCII_PUNCT=set(',.;:!?()[]{}<>~`@#$%^&*_+=|\\/')
for sid in IDS:
    d=json.load(open(os.path.join(ROOT,"data/modern-translation",sid+".json"),encoding="utf-8"))
    segs=d["translations"]
    maxsec=max(len(s["section"]) for s in segs)
    structbad=[]; punctbad=[]; longsec=[]
    for i,s in enumerate(segs):
        sec=s["section"]; mod=s["modern"]
        if len(sec)>14: longsec.append((i+1,sec,len(sec)))
        if not mod.startswith("【"+sec+"】"): structbad.append((i+1,"head",mod[:20]))
        if "【义解】" not in mod: structbad.append((i+1,"no_yijie",""))
        else:
            if len(re.sub(r"\s+","",mod.split("【义解】",1)[1]))==0: structbad.append((i+1,"empty_yijie",""))
        if mod.rstrip().endswith("】"): structbad.append((i+1,"ends_with_bracket",""))
        # ascii punct adjacent to CJK
        for m in re.finditer(r'[\u4e00-\u9fff]\s*([,;:!?()\[\]<>])\s*[\u4e00-\u9fff]', mod):
            punctbad.append((i+1,m.group(0)))
    print("### %s  max_section_len=%d  longsec=%s  structbad=%s  ascii_punct_cjk=%s"%(
        sid,maxsec,longsec if longsec else "-",structbad if structbad else "-",
        punctbad[:5] if punctbad else "-"))
