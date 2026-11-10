import os,json,re
trans={f[:-5] for f in os.listdir('data/modern-translation') if f.endswith('.json')}
BAD=re.compile(r'目[录錄]|佛名|名號|陀羅尼集|真言集|呪|咒|儀軌|懺法|贊|音義|悉曇|戒本|戒經|梵本|譯經圖記|陀羅尼')
PUA=set(chr(i) for r in [(0xE000,0xF8FF),(0xF0000,0xFFFFD),(0x100000,0x10FFFD)] for i in range(r[0],r[1]+1))
cand=[]
for f in sorted(os.listdir('sutras')):
    if not f.endswith('.json') or f.startswith('_'): continue
    tid=f[:-5]
    if tid in trans: continue
    try:
        d=json.load(open('sutras/'+f,encoding='utf-8'))
        if not isinstance(d,dict): continue
        title=d.get('title','')
        if BAD.search(title): continue
        c=d.get('content',[])
        parts=[]
        for x in c:
            if isinstance(x,dict): parts.append(x.get('text',''))
            elif isinstance(x,str): parts.append(x)
        text=''.join(parts)
        norm=re.sub(r'\s+','',text)
        if not norm: continue
        p=sum(1 for ch in norm if ch in PUA); b=norm.count('□')
        if p/len(norm)>0.02 or b/len(norm)>0.05: continue
        L=len(norm)
        if 1200<L<14000:
            cand.append((tid,title,L))
    except: pass
cand.sort(key=lambda x:x[2])
for c in cand[:40]: print(c)
