# -*- coding: utf-8 -*-
import json, os, glob, re, sys
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)
sys.path.insert(0,"scripts")
from segment_baihua import segment, load_raw, norm

done=set(os.path.basename(p)[:-5] for p in glob.glob("data/modern-translation/*.json"))
SKIP={"hant2simp","index","index-light","search-index","search-word-index"}

def pua_count(s):
    n=0
    for ch in s:
        o=ord(ch)
        if (0xE000<=o<=0xF8FF) or (0xF0000<=o<=0xFFFFD) or (0x100000<=o<=0x10FFFD):
            n+=1
    return n

BAD_TITLE=re.compile(r'(目錄|目录|佛名|名號|名号|陀羅尼集|真言集|咒|呪|儀軌|仪轨|懺法|忏悔|禮懺|礼忏|贊|赞|音義|音义|字音|悉曇|悉昙)')

cands=[]
for p in glob.glob("sutras/*.json"):
    sid=os.path.basename(p)[:-5]
    if sid in done or sid in SKIP: continue
    if not re.match(r'^t\d+[a-z]?$', sid): continue
    try: d=json.load(open(p,encoding="utf-8"))
    except Exception: continue
    if not isinstance(d,dict): continue
    content=d.get("content",[])
    if not isinstance(content,list): content=[]
    raw="\n".join((c.get("text","") if isinstance(c,dict) else str(c)) for c in content)
    total=norm(raw)
    n=len(total)
    if n<600 or n>60000: continue
    pua=pua_count(total); que=total.count('□')
    if pua/n>0.02 or que/n>0.05: continue
    title=d.get("title","") or ""
    if BAD_TITLE.search(title): continue
    segs=segment(raw)
    ns=len(segs)
    cov=sum(len(norm(s)) for s in segs)/n
    if cov<0.985: continue
    if ns<40 or ns>150: continue
    cands.append((ns,n,sid,title,d.get("translator",""),d.get("vol",""),round(cov,3)))

cands.sort(key=lambda x:x[1])
print("候选总数:",len(cands))
for ns,n,sid,title,tr,vol,cov in cands[:80]:
    print(f"{ns:4d}段 {n:6d}字 {sid:9s} {cov}  {tr[:14]:14s} {title[:34]}")
json.dump([{"id":c[2],"segs":c[0],"chars":c[1],"title":c[3],"translator":c[4],"vol":c[5],"cov":c[6]} for c in cands],
          open("_b120/cands.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
