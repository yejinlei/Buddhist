# -*- coding: utf-8 -*-
import json,re
from collections import defaultdict
def load(p): return json.load(open(p,encoding='utf-8'))
IDS=['t2865','t2839','t2784','t2855','t2882','t1275']
# check duplicated long sentences across segments (>=12 chars) within a file
for sid in IDS:
    d=load(f'data/modern-translation/{sid}.json')
    segs=[t['modern'] for t in d['translations']]
    # split into sentences
    sents=[]
    for i,s in enumerate(segs):
        for part in re.split(r'[，。；、！？：\n]', s):
            part=part.strip('「」『』（）() ')
            if len(part)>=12:
                sents.append((i+1,part))
    seen=defaultdict(list)
    for idx,p in sents:
        seen[p].append(idx)
    dups={p:idx for p,idx in seen.items() if len(set(idx))>1}
    if dups:
        print('='*20,sid)
        for p,idx in dups.items():
            print('  DUPLICATE across segs',idx,'::',p)
