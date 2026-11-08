# -*- coding: utf-8 -*-
import json,re
def load(p): return json.load(open(p,encoding='utf-8'))
IDS=['t2865','t2839','t2784','t2855','t2882','t1275']
for sid in IDS:
    d=load(f'data/modern-translation/{sid}.json')
    print('='*30,sid)
    for i,t in enumerate(d['translations']):
        m=t['modern']
        ascii_chars=sorted(set(ch for ch in m if ord(ch)<128 and not ch.isalnum() and ch not in ' \n'))
        if ascii_chars:
            print(f'  seg{i+1} ascii punct: {ascii_chars}')
    # intro
    ascii_chars=sorted(set(ch for ch in d['intro'] if ord(ch)<128 and not ch.isalnum() and ch not in ' \n'))
    if ascii_chars: print('  intro ascii punct:',ascii_chars)
