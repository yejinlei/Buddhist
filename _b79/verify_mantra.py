# -*- coding: utf-8 -*-
import json, os, re, difflib
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
IDS=["t0470","t0784","t1927","t1657","t0593","t0516","t0709","t0556","t0831","t0746","t0074","t1083"]
def nows(s): return re.sub(r"\s+","",s)
# mantra indicator: contains （二合 or 呪曰/咒曰 with transliteration, or （句）
PAT=re.compile(r'（(?:[二三四五]合|引|去|上|入|句|一|二|三|四|五|六|七|八|九|十|平|長音|重音|半聲|台邏反|詩債反|持債反|無詣反)[^）]*）')
for sid in IDS:
    d=json.load(open(os.path.join(ROOT,"data/modern-translation",sid+".json"),encoding="utf-8"))
    for i,s in enumerate(d["translations"]):
        prev=s["original_preview"]; mod=s["modern"]
        if not (('呪曰' in prev) or ('咒曰' in prev) or PAT.search(prev)):
            continue
        pn=nows(prev); mn=nows(mod)
        # longest common substring
        sm=difflib.SequenceMatcher(None, pn, mn, autojunk=False)
        blocks=[b for b in sm.get_matching_blocks() if b.size>0]
        biggest=max(blocks,key=lambda b:b.size)
        lcs=pn[biggest.a:biggest.a+biggest.size]
        # does the mantra (portion of preview containing 合/引 markers) survive?
        print("=== %s seg%d [%s]"%(sid,i+1,s["section"]))
        print("   prev_len=%d  biggest_match=%d  covers=%.0f%%"%(len(pn),biggest.size,100*biggest.size/len(pn)))
        # mantralike chars in preview
        mm=PAT.findall(prev)
        # check each mantra marker substring present in modern
        missing=[]
        for m in re.finditer(r'[^\s「」，。；：！？]{2,}', prev):
            pass
        # count annotated tokens in prev vs modern
        print("   markers_prev=%d markers_mod=%d"%(len(PAT.findall(prev)),len(PAT.findall(mod))))
        # find preview annotated tokens not in modern
        toks=re.findall(r'[\u4e00-\u9fff]{1,6}（[^）]*）', prev)
        miss=[t for t in toks if t not in mod]
        if miss: print("   MISSING annotated tokens in modern:",miss[:8])
        if biggest.size < len(pn)*0.5:
            print("   >>> LOW coverage — possible dropped mantra text")
            print("   prev:",pn[:120])
            print("   mod :",mn[:120])
