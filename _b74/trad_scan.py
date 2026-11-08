# -*- coding: utf-8 -*-
import json,re
h2s=json.load(open('data/hant2simp_full.json',encoding='utf-8'))
def load(p): return json.load(open(p,encoding='utf-8'))
IDS=['t2865','t2839','t2784','t2855','t2882','t1275']
for sid in IDS:
    d=load(f'data/modern-translation/{sid}.json')
    print('='*40, sid)
    # scan intro + moderns
    fields=[('intro',d['intro'])]
    for i,t in enumerate(d['translations']):
        fields.append((f'seg{i+1}',t['modern']))
        fields.append((f'seg{i+1}-prev',t['original_preview']))
    for name,txt in fields:
        hits={}
        for ch in txt:
            if ch in h2s and h2s[ch]!=ch:
                # traditional char that maps to a different simplified
                hits.setdefault(ch,0)
                hits[ch]+=1
        if hits and not name.endswith('-prev'):
            # find context
            ctxs=[]
            for ch in hits:
                for m in re.finditer(re.escape(ch),txt):
                    s=max(0,m.start()-12); e=min(len(txt),m.end()+12)
                    ctxs.append((ch,txt[s:e]))
            print(f'  [{name}] trad chars: {hits}')
            for c in ctxs[:8]:
                print('      ',c[0],'|',c[1])
