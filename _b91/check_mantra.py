import json,re
def norm(s): return re.sub(r'\s+','',s)
tids=['t0679','t1066','t1126','t1174','t1524']
allbad=0
for tid in tids:
    d=json.load(open(f'data/modern-translation/{tid}.json',encoding='utf-8'))
    src=json.load(open(f'sutras/{tid}.json',encoding='utf-8'))
    orig=norm("\n".join(c["text"] for c in src["content"]))
    bad=[]; total=0
    for i,s in enumerate(d["translations"]):
        for frag in re.findall(r'⟪(.*?)⟫', s["modern"], re.S):
            f=norm(frag)
            if not f: continue
            total+=1
            if f not in orig:
                bad.append((i,frag[:50]))
    print(tid,'咒文/照录片段数',total,'不在原文',len(bad))
    for b in bad[:8]: print('    异常:',b)
    allbad+=len(bad)
print('合计异常',allbad)
