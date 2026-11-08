# -*- coding: utf-8 -*-
import json,re
def load(p): return json.load(open(p,encoding='utf-8'))
IDS=['t2865','t2839','t2784','t2855','t2882','t1275']
for sid in IDS:
    d=load(f'data/modern-translation/{sid}.json')
    n=len(d['translations'])
    probs=[]
    for i,t in enumerate(d['translations']):
        m=t['modern']
        if not m.strip(): probs.append((i+1,'EMPTY'))
        # count 义解
        c=m.count('【义解】')
        if c!=1: probs.append((i+1,f'义解count={c}'))
        # first bracket
        mb=re.match(r'^【([^】]*)】',m)
        if not mb: probs.append((i+1,'no leading 【】'))
        elif mb.group(1)=='义解': probs.append((i+1,'leading bracket is 义解'))
        # 义解 must not be last with nothing after
        if '【义解】' in m and len(m.split('【义解】')[-1].strip())<5:
            probs.append((i+1,'义解 too short/empty'))
        # quote pairing (「」)
        if m.count('「')!=m.count('」'):
            probs.append((i+1,f'「」unpaired {m.count("「")}/{m.count("」")}'))
        if m.count('『')!=m.count('』'):
            probs.append((i+1,f'『』unpaired'))
        if m.count('（')!=m.count('）'):
            probs.append((i+1,f'（）unpaired {m.count("（")}/{m.count("）")}'))
        if m.count('《')!=m.count('》'):
            probs.append((i+1,f'《》unpaired'))
    print(sid,'n=',n,'problems:',probs if probs else 'NONE')
