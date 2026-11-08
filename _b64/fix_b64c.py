# -*- coding: utf-8 -*-
"""第64批 修正 v3（段号最终订正）。original_preview 一字不动。"""
import json, re, os
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"; os.chdir(ROOT)
TR="data/modern-translation"; SUT="sutras"
def norm(s): return re.sub(r"\s+","",s)
h2s=json.load(open("data/hant2simp_full.json",encoding="utf-8"))
def simp(s): return "".join(h2s.get(c,c) for c in s)
def load(t): return json.load(open(f"{TR}/{t}.json",encoding="utf-8"))
def save(t,d): json.dump(d,open(f"{TR}/{t}.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)

# ---- 1. 咒文展示块 ----
# t1384: idx2..14 咒；idx15 咒末
d=load("t1384")
for i in range(2,15):
    seg=d["translations"][i]; p=seg["original_preview"].strip()
    if p.startswith("「"): p=p[1:]
    seg["modern"]=re.sub(r"「[^」]*」", lambda m:"「"+p+"」", seg["modern"], count=1)
seg=d["translations"][15]
seg["modern"]=re.sub(r"「[^」]*」", "「賀（引）（六十）」", seg["modern"], count=1)
save("t1384",d)
# t1162: idx6,7,8
d=load("t1162")
def headtail(m):
    yj=m.find("【义解】"); return (m[:yj], m[yj:]) if yj>=0 else (m,"")
# idx6
seg=d["translations"][6]; h,t=headtail(seg["modern"]); ti=h.index("】")+1
pv=seg["original_preview"]
aq=pv.split("「",1)[1]
seg["modern"]=h[:ti]+"陀罗尼曰：「"+aq+t
# idx7
seg=d["translations"][7]; h,t=headtail(seg["modern"]); ti=h.index("】")+1
pv=seg["original_preview"].strip()
seg["modern"]=h[:ti]+"「"+pv+t
# idx8
seg=d["translations"][8]; pv=seg["original_preview"]
cur=pv[:pv.index("』")+1]
seg["modern"]=re.sub(r"「[^」]*」", lambda m:"「"+cur+"」", seg["modern"], count=1)
save("t1162",d)

# ---- 2. t1658 叙述性引用 ----
d=load("t1658")
for seg in d["translations"]:
    seg["modern"]=seg["modern"].replace("「盎、阿（引）、吽」","「盎、阿、吽」").replace("「盎、阿（引）」","「盎、阿」")
save("t1658",d)

# ---- 3. 「」引经文原语回正 ----
ALL="t0924a t1181 t1384 t0841 t0832 t1162 t0693 t0747a t1903 t2047b t1882 t1658".split()
for tid in ALL:
    o=json.load(open(f"{SUT}/{tid}.json",encoding="utf-8"))
    raw=norm("".join(c["text"] for c in o["content"])); od=re.sub(r"（[^）]*）","",raw); ds=simp(od)
    d=load(tid); cnt=[0]
    for seg in d["translations"]:
        def repl(mo):
            f=re.sub(r"（[^）]*）","",norm(mo.group(1))); fs=simp(f); p=ds.find(fs)
            if p>=0:
                o2=od[p:p+len(fs)]
                if o2!=f: cnt[0]+=1; return "「"+o2+"」"
            return mo.group(0)
        seg["modern"]=re.sub(r"「([^」]+)」", repl, seg["modern"])
    save(tid,d)
    print("回正",tid,cnt[0])
