import json,re,sys
tid=sys.argv[1]
d=json.load(open(f'sutras/{tid}.json',encoding='utf-8'))
c=d['content']
if isinstance(c,list) and c and isinstance(c[0],dict):
    text=''.join(x.get('text','') for x in c if isinstance(x,dict))
else: text=str(c)
text=text.replace('\r\n','\n').replace('\r','\n')
lines=[l.strip() for l in text.split('\n') if l.strip()]
segments=[];buf=''
for line in lines:
    # 卷号行并入上一段不单独分段
    if re.match(r'^卷\d+$',line):
        if buf: segments.append(buf)
        buf=line
        continue
    buf+=line
    while len(re.sub(r'\s+','',buf))>=60:
        # 在句末标点处分
        cut=-1
        for m in re.finditer(r'[。！？]',buf):
            pos=m.end()
            if pos>=40 and pos<=len(buf)-10:
                cut=pos
            if cut!=-1 and cut>=60 and cut<=len(buf)-5:
                break
        if cut==-1 or cut<40: break
        segments.append(buf[:cut]);buf=buf[cut:]
if buf.strip(): segments.append(buf)
# 合并过短
final=[]
for s in segments:
    ns=re.sub(r'\s+','',s)
    if final and len(ns)<30:
        final[-1]+=s
    else: final.append(s)
# 保证连续
joined=''.join(re.sub(r'\s+','',s) for s in final)
orig=re.sub(r'\s+','',text)
print(f'tid={tid} title={d["title"]} translator={d["translator"]} segs={len(final)} cover={len(set(joined)&set(orig))/len(set(orig)):.3f}')
assert orig[:200] in joined or joined[:200] in orig
json.dump({'id':tid,'title':d['title'],'translator':d['translator'],'category':d.get('category',''),'paragraphs':[{'text':s} for s in final]},open(f'data/baihua-tasks/{tid}.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('written')
