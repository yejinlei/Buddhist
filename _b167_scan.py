import json, os, re
done=set()
for fn in os.listdir('data/modern-translation'):
    if fn.endswith('.json'): done.add(fn[:-5])
h=open('pages/sutras.html',encoding='utf-8').read()
m=re.search(r"const BAIHUA_AVAILABLE = new Set\(\[(.*?)\]\);",h,re.S)
listed=set(re.findall(r"'([^']+)'",m.group(1)))
skip = done | listed
BAD = re.compile(r'目錄|目录|佛名|名號|名号|陀羅尼集|真言集|呪|咒|儀軌|仪轨|懺|忏|贊|赞|音義|音义|悉曇|悉昙|禮讚|礼赞|念誦|念诵|法數|法数|陀羅尼經|陀罗尼经|儀|轨|經疏|经疏|偈|圖|图|禮|礼|論疏|论疏|頌|颂|願文|愿文|發願|发愿|齋|斋|齋法|齋儀')

def load_text(path):
    d=json.load(open(path,encoding='utf-8'))
    c=d.get('content')
    if isinstance(c,list):
        if c and isinstance(c[0],dict):
            return d.get('title',''),d.get('translator',''),''.join(seg.get('text','') for seg in c if isinstance(seg,dict))
        return d.get('title',''),d.get('translator',''),''.join(str(x) for x in c)
    return d.get('title',''),d.get('translator',''),str(c)

def split(text,target=1500,min_len=800,max_len=2500):
    text=text.replace('\r\n','\n').replace('\r','\n')
    lines=[l.strip() for l in text.split('\n') if l.strip()]
    cleaned=[]
    for l in lines:
        if re.match(r'^卷[上下0-9０-９一二三四五六七八九十百]+$',l): continue
        if re.match(r'^第[一二三四五六七八九十百0-9]+[卷品篇部]',l) and len(l)<20: continue
        cleaned.append(l)
    segs=[];buf=''
    for line in cleaned:
        if buf=='' and len(line)<40 and ('經' in line or '論' in line or '譯' in line or '疏' in line):
            buf=line; continue
        buf+=line
        while len(buf)>=min_len:
            cut=-1
            for i,ch in enumerate(buf):
                if ch in '。！？；' and i+1>=min_len: cut=i+1;break
            if cut==-1 or cut>max_len:
                for i,ch in enumerate(buf):
                    if ch in '、，' and i+1>=min_len: cut=i+1;break
                if cut==-1 or cut>max_len:
                    if len(buf)>max_len: cut=max_len
                    else: break
            s=buf[:cut].strip()
            if s: segs.append(s)
            buf=buf[cut:].strip()
    if buf.strip():
        if segs and len(buf)<100: segs[-1]+=buf
        else: segs.append(buf.strip())
    clean=re.sub(r'\s+','',text)
    joined=''.join(re.sub(r'\s+','',s) for s in segs)
    cov=len(joined)/len(clean) if clean else 0
    return segs,cov

rows=[]
for fn in sorted(os.listdir('sutras')):
    if not fn.endswith('.json'): continue
    tid=fn[:-5]
    if tid in skip or tid.startswith('t1') and tid=='t1545': continue
    try: title,tr,text=load_text(f'sutras/{fn}')
    except: continue
    if BAD.search(title): continue
    pua=sum(1 for ch in text if 0xE000<=ord(ch)<=0xF8FF or ch=='□')
    if pua/max(1,len(text))>0.02: continue
    n=len(re.sub(r'\s+','',text))
    if n<1200 or n>60000: continue
    segs,cov=split(text)
    ns=len(segs)
    if ns<8 or ns>170: continue
    if cov<0.98: continue
    punct=sum(text.count(p) for p in '，。、；：！？')/max(1,n)
    if punct<0.06: continue
    avg=n/ns
    if avg<45 or avg>4000: continue
    rows.append([tid,ns,n,round(punct,3),round(cov,3),title,tr])
rows.sort(key=lambda x:-x[2])
print('候选总数:',len(rows))
for r in rows:
    print(f"{r[0]}\t{r[1]}段\t{r[2]}字\tpunct={r[3]}\tcov={r[4]}\t{r[5]}\t{r[6]}")
json.dump(rows,open('_b167_candidates.json','w'),ensure_ascii=False,indent=1)
