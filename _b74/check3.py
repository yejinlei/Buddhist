# -*- coding: utf-8 -*-
import json,re
def load(p): return json.load(open(p,encoding='utf-8'))
def getmodern(sid):
    d=load(f'data/modern-translation/{sid}.json')
    return d, [t['modern'] for t in d['translations']]

print("###### 修正5: t2882 intro")
d=load('data/modern-translation/t2882.json')
print('intro:',d['intro'])
for kw in ['疑伪','敦煌','写本','偽','疑偽']:
    print(f"  intro含'{kw}'?", kw in d['intro'])
print("title:",d['title'],"translator:",repr(d['translator']))
print("mode:",d['mode'])

print()
print("###### 修正6: t1275")
d,segs=getmodern('t1275')
print("段数:",len(segs))
# 段16 (1-based) = index 15
print("-- 段16 modern --")
print(segs[15])
print()
full='\n'.join(segs)
print("全文含'阙伽'?", '阙伽' in full, full.count('阙伽'))
print("全文含'阏伽'?", '阏伽' in full, full.count('阏伽'))
print("全文含'閼伽'?", '閼伽' in full, full.count('閼伽'))
print()
print("-- 段3 modern --")
print(segs[2])
print()
print("段3含'一百四十俱胝'?", '一百四十俱胝' in segs[2])
print("段3含'一百四千俱胝'?", '一百四千俱胝' in segs[2])
print()
print("全文含'附録'?", '附録' in full, "含'附录'?", '附录' in full)
print("全文含'毘沙门天'?", '毘沙门天' in full, full.count('毘沙门天'))
print("全文含'毗沙门天'?", '毗沙门天' in full, full.count('毗沙门天'))
print("全文含'毘'?", '毘' in full, full.count('毘'))
