#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, glob, re
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)
done = set(os.path.basename(p)[:-5] for p in glob.glob("data/modern-translation/*.json"))
SKIP = {"hant2simp","index","index-light","search-index","search-word-index"}
# 排除_b102已选10部
b102_selected = set(open("selected_batch.txt").read().split())
SKIP.update(b102_selected)
print("b102已选:", len(b102_selected), b102_selected)

def pua_count(s):
    n=0
    for ch in s:
        o=ord(ch)
        if (0xE000<=o<=0xF8FF) or (0xF0000<=o<=0xFFFFD) or (0x100000<=o<=0x10FFFD):
            n+=1
    return n
def que_count(s):
    return s.count("□")

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
    que=que_count(txt)
    rows.append((nlen,sid,d.get("title",""),d.get("translator",""),d.get("vol",""),len(content),pua,que,nlen))

clean=[r for r in rows if r[6]==0 and r[7]/max(r[0],1) < 0.05]
dirty=[r for r in rows if r[6]>0 or r[7]/max(r[0],1) >=0.05]
print("未译总数:",len(rows)," 干净无阙文:",len(clean)," 问题:",len(dirty))
clean.sort(key=lambda x:x[0])
for lo,hi in [(400,2500),(2501,3000),(3001,3500),(3501,4000),(4001,999999)]:
    c=[r for r in clean if lo<=r[0]<=hi]
    print(f"  {lo}-{hi}字: 干净 {len(c)} 部")
print("\n前15部最短干净经文:")
for r in clean[:15]:
    print(f"  {r[1]:8s} {r[0]:5d}字 {r[3]:10s} {r[2][:30]}")
json.dump([{"id":r[1],"chars":r[0],"title":r[2],"translator":r[3],"vol":r[4],"segs":r[5]} for r in clean],
          open("_b103_clean.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
