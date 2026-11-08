# -*- coding: utf-8 -*-
import json, re, sys, os
def probe(tid, seeds):
    task=json.load(open(f'data/baihua-tasks/{tid}.json',encoding='utf-8'))
    texts=[t['original_preview'] for t in task['translations']]
    full='';ranges=[]
    for t in texts:
        a=len(full);full+=t;ranges.append((a,len(full)))
    def seg_of(pos):
        for i,(a,b) in enumerate(ranges):
            if a<=pos<b: return i
        return -1
    flag=[False]*len(full)
    for seed in seeds:
        pos=0
        while True:
            k=full.find(seed,pos)
            if k<0: break
            a=full.find('「',k)
            if a<0: break
            e1=full.find('」',a+1);e2=full.find('』',a+1)
            b1=len(full)
            for e in (e1,e2):
                if e>=0: b1=min(b1,e+1)
            b2=len(full);j=a+1
            while True:
                j=full.find('「',j)
                if j<0: break
                if '\n' in full[a:j]: b2=j;break
                j+=1
            b=min(b1,b2)
            print(f'  seed={seed!r} k@seg{seg_of(k)} -> a@seg{seg_of(a)}, b@seg{seg_of(b-1)}')
            for x in range(a,b): flag[x]=True
            pos=b
    def chunks(a,b):
        out=[];cur=[];i=a
        while i<b:
            if flag[i]:
                c=full[i]
                if c=='（':
                    j=i+1
                    while j<b and full[j]!='）': j+=1
                    i=j+1;continue
                if c not in '「」『』\n':
                    if not c.isspace(): cur.append(c)
                i+=1
            else:
                if cur: out.append(re.sub(r'\s+','',''.join(cur)));cur=[]
                i+=1
        if cur: out.append(re.sub(r'\s+','',''.join(cur)))
        return out
    print('  每段 chunk 数（仅列非零）：')
    tot=0
    for i,(a,b) in enumerate(ranges):
        ch=chunks(a,b)
        if ch:
            tot+=len(ch)
            print(f'    seg{i}: {len(ch)}  {[c[:36] for c in ch]}')
    print(f'  合计 chunk={tot}, 段数={len(ranges)}')
if __name__=='__main__':
    tid=sys.argv[1]
    rest=sys.argv[2:]
    if rest:
        seeds=tuple(rest)
    else:
        seeds=('呪曰：',)
    print(f'== {tid} seeds={seeds} ==')
    probe(tid,seeds)
