import json, os, re, glob
root='.'
avail=set()
with open(f'{root}/pages/sutras.html','r',encoding='utf-8') as f:
    html=f.read()
m=re.search(r'const BAIHUA_AVAILABLE\s*=\s*new Set\(\[(.*?)\]\);', html, re.S)
avail=set(re.findall(r"'([^']+)'", m.group(1)))
print('avail:', len(avail))

def norm(s):
    return re.sub(r'\s+', '', s or '')

BAD=re.compile(r'(目[录錄]|佛名|名號|陀羅尼集|陀羅尼經|真言集|真言經|咒|呪|儀軌|懺法|禮懺|贊|音義|悉曇|名數|傳記|傳|行狀|燒香|偈頌?$|名相|品目|科判|目次|目錄|像法|出三藏記集)')

cands=[]
for i in range(1,2500):
    for suf in ['','a','b','c','d']:
        tid=f't{i:04d}{suf}'
        sp=f'{root}/sutras/{tid}.json'
        if not os.path.exists(sp): continue
        if tid in avail: continue
        try:
            s=json.load(open(sp,encoding='utf-8'))
        except: continue
        title=s.get('title','')
        if BAD.search(title): continue
        text=''.join(c.get('text','') for c in s.get('content',[]))
        nt=norm(text)
        # PUA
        pua=sum(1 for ch in nt if ('\ue000'<=ch<='\uf8ff') or ('\U000f0000'<=ch<='\U000ffffd') or ('\U00100000'<=ch<='\U0010fffd'))
        if len(nt)==0: continue
        if pua/len(nt)>0.02: continue
        if nt.count('□')/len(nt)>0.05: continue
        paras=[c.get('text','').strip() for c in s.get('content',[]) if c.get('text','').strip()]
        # 段数
        n=len(paras)
        if n<40 or n>160: continue
        if len(nt)<600 or len(nt)>60000: continue
        # 段均长（过滤偈颂连写不可切段）
        avglen=len(nt)/n
        if avglen<50 or avglen>400: continue
        # 标点覆盖
        punct=sum(1 for ch in nt if ch in '。，、；：？！「」『』（）')
        if punct/len(nt)<0.06: continue
        cands.append((tid,title,n,len(nt),avglen))
cands.sort(key=lambda x:x[3])
for c in cands[:20]:
    print(c)
