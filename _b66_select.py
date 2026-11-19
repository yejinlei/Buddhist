#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, glob, re
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)
done = set(os.path.basename(p)[:-5] for p in glob.glob("data/modern-translation/*.json"))
SKIP = {"hant2simp","index","index-light","search-index","search-word-index"}

def pua_count(s):
    n=0
    for ch in s:
        o=ord(ch)
        if (0xE000<=o<=0xF8FF) or (0xF0000<=o<=0xFFFFD) or (0x100000<=o<=0x10FFFD):
            n+=1
    return n

rows=[]
for p in glob.glob("sutras/*.json"):
    sid=os.path.basename(p)[:-5]
    if sid in done or sid in SKIP: continue
    try: d=json.load(open(p,encoding="utf-8"))
    except Exception: continue
    if not isinstance(d,dict): continue
    content=d.get("content",[])
    if not isinstance(content,list): content=[]
    txt="".join((c.get("text","") if isinstance(c,dict) else str(c)) for c in content)
    nlen=len("".join(txt.split()))
    pua=pua_count(txt)
    rows.append((nlen,sid,d.get("title",""),d.get("translator",""),d.get("vol",""),len(content),pua))

clean=[r for r in rows if r[6]==0]
dirty=[r for r in rows if r[6]>0]
print("未译总数:",len(rows)," 干净:",len(clean)," 含PUA:",len(dirty))
for lo,hi in [(800,1500),(1501,2500),(2501,8000),(8000,999999)]:
    c=[r for r in clean if lo<=r[0]<=hi]
    print(f"  {lo}-{hi}字: 干净 {len(c)} 部")
json.dump([{"id":r[1],"chars":r[0],"title":r[2],"translator":r[3],"vol":r[4],"segs":r[5]} for r in clean],
          open("_b66_clean.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
