import json,re,sys
tid=sys.argv[1]
d=json.load(open(f'sutras/{tid}.json',encoding='utf-8'))
c=d['content']
text=''.join(x.get('text','') for x in c if isinstance(x,dict)) if isinstance(c,list) and c and isinstance(c[0],dict) else str(c)
text=text.replace('\r\n','\n').replace('\r','\n')
lines=[l.strip() for l in text.split('\n') if l.strip()]
# 按句号切,每段 target 130
segs=[];buf=''
for line in lines:
    if re.match(r'^卷\d+$',line):
        if buf:segs.append(buf)
        segs.append(line);buf=''
        continue
    buf+=line
    while len(re.sub(r'\s+','',buf))>=80:
        cut=-1
        for m in re.finditer(r'[。！？]',buf):
            pos=m.end()
            if 80<=pos<=300 and pos<=len(buf)-8:
                cut=pos;break
        if cut==-1:break
        segs.append(buf[:cut]);buf=buf[cut:]
if buf.strip():segs.append(buf)
final=[]
for s in segs:
    ns=re.sub(r'\s+','',s)
    if final and len(ns)<25: final[-1]+=s
    else: final.append(s)
joined=''.join(re.sub(r'\s+','',s) for s in final)
orig=re.sub(r'\s+','',text)
print(f'segs={len(final)} len orig={len(orig)} joined={len(joined)}')
assert orig.startswith(joined[:200]) or joined.startswith(orig[:200])
json.dump({'id':tid,'title':d['title'],'translator':d['translator'],'category':d.get('category',''),'paragraphs':[{'text':s} for s in final]},open(f'data/baihua-tasks/{tid}.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('written')
