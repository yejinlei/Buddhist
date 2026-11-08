# -*- coding: utf-8 -*-
import json,re
def load(p): return json.load(open(p,encoding='utf-8'))

def alltext(sid):
    d=load(f'data/modern-translation/{sid}.json')
    out=[]
    for i,t in enumerate(d['translations']):
        out.append((i,t['modern']))
    return d,out

print("###### 修正1: t2865 段7")
d,segs=alltext('t2865')
print("-- 段7 modern --")
print(segs[6][1])
print()
print("段7含'种种恶疫之气不得靠近'?", '种种恶疫之气不得靠近' in segs[6][1])
print("段7含'一切灭尽不留残余'?", '一切灭尽不留残余' in segs[6][1])
print()
print("-- 段8 modern --")
print(segs[7][1][:300])
print()
print("义解'依音译保留用字' in 段7?", '依音译保留用字' in segs[6][1])
print("义解'依音译用字作简体转写' in 段7?", '依音译用字作简体转写' in segs[6][1])

print()
print("###### 修正2: t2839 intro")
d=load('data/modern-translation/t2839.json')
print('intro:',d['intro'])
print("含'自覺、覺他、覺滿'?", '自覺、覺他、覺滿' in d['intro'])
print("含'自觉、觉他、觉满'?", '自觉、觉他、觉满' in d['intro'])
