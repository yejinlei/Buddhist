# -*- coding: utf-8 -*-
import json, os, re
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
IDS=["t0470","t0784","t1927","t1657","t0593","t0516","t0709","t0556","t0831","t0746","t0074","t1083"]
def nows(s): return re.sub(r"\s+","",s)
# annotation marker pattern
M=re.compile(r'（(?:[二三四五]合|引|去聲|上聲|半聲|平|長音|重音|句|一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十|二十一|二十二|二十三|二十四|二十五|二十六|二十七|二十八|二十九|三十|台邏反|詩債反|持債反|無詣反)[^）]*）')
for sid in IDS:
    d=json.load(open(os.path.join(ROOT,"data/modern-translation",sid+".json"),encoding="utf-8"))
    has=False
    for i,s in enumerate(d["translations"]):
        prev=s["original_preview"]
        if '呪' in prev or '咒' in prev or M.search(prev):
            has=True
            print("### %s seg%d [%s]"%(sid,i+1,s["section"]))
            # extract mantra = from first annotation marker backwards to include the run, and forward
            # simply: find quoted dharani region: between 呪曰/咒曰 and end of that quoted string
            pn=nows(prev); mn=nows(s["modern"])
            # every annotated token in prev must appear verbatim in mod
            toks=M.findall(prev)
            miss=[t for t in toks if t not in mn]
            print("   annotated_tokens=%d  token_missing_in_modern=%s"%(len(toks),miss if miss else "none"))
            # check transliteration runs (CJK sequences adjacent to markers)
            # find maximal runs of preview containing markers or CJK, split by 。！？narrative
            # check: is the longest preview run (between 。) that contains a marker a substring of mod?
            for run in re.split(r'(?<=[。！？」])', prev):
                rn=nows(run)
                if M.search(run) and len(rn)>4:
                    if rn not in mn:
                        print("   RUN not verbatim in modern:", rn[:90])
    if not has: print("### %s  (no mantra)"%sid)
