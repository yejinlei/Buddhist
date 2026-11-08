# -*- coding: utf-8 -*-
import json, re
import opencc
cc = opencc.OpenCC('t2s')
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
def load(sid): return json.load(open(f'{ROOT}/data/modern-translation/{sid}.json',encoding='utf-8'))
def save(sid,d): json.dump(d, open(f'{ROOT}/data/modern-translation/{sid}.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
def norm(s): return re.sub(r'\s+','',s)
def srcn(sid):
    d=json.load(open(f'{ROOT}/sutras/{sid}.json',encoding='utf-8'))
    return norm("".join((c.get('text','') if isinstance(c,dict) else str(c)) for c in d.get('content',[])))

def conv_modern(sid, modern, src):
    parts=[]; i=0; n=len(modern); buf=''
    while i<n:
        ch=modern[i]
        if ch in '「『':
            parts.append(('p',buf)); buf=''
            close='」' if ch=='「' else '』'
            j=modern.find(close,i+1)
            if j==-1:
                parts.append(('p',ch)); parts.append(('q',modern[i+1:])); i=n
            else:
                parts.append(('p',ch)); parts.append(('q',modern[i+1:j])); parts.append(('p',close)); i=j+1
        else:
            buf+=ch; i+=1
    parts.append(('p',buf))
    res=[]
    for k,t in parts:
        if k=='p': res.append(cc.convert(t))
        else:
            res.append(t if (norm(t) and norm(t) in src) else cc.convert(t))
    return ''.join(res)

def fix_trad(sid):
    d=load(sid); src=srcn(sid); ch=0
    for s in d['translations']:
        new=conv_modern(sid, s['modern'], src)
        if new!=s['modern']: ch+=1
        s['modern']=new
        m=re.match(r'^【([^】]*)】', new)
        if m: s['section']=m.group(1)
    save(sid,d); print(f"{sid}: 转简 {ch} 段")

for sid in ["t1657","t0516","t0593"]:
    fix_trad(sid)

# t0593 段18/19 咒文回正
d=load('t0593')
mantra18="南謨釋迦牟奈曳　怛他揭多也　阿羅𠿒帝三藐三勃陀也　怛姪他唵　苫謎苫謎薩婆波跛　鉢羅苫末泥（去）"
s18=d['translations'][17]['modern']
assert s18.endswith(cc.convert(mantra18)), s18[-60:]
s18=s18[:-len(cc.convert(mantra18))]+mantra18
d['translations'][17]['modern']=s18
s19=d['translations'][18]['modern']
assert '莎诃' in s19
d['translations'][18]['modern']=s19.replace('莎诃','莎訶')
save('t0593',d)
print("t0593 咒文回正完成")
print("t0593 段18尾:", d['translations'][17]['modern'][-50:])
print("t0593 段19头:", d['translations'][18]['modern'][:40])
