# -*- coding: utf-8 -*-
import json,re
def load(p): return json.load(open(p,encoding='utf-8'))
def getmodern(sid):
    d=load(f'data/modern-translation/{sid}.json')
    return d, [t['modern'] for t in d['translations']]
def getpreviews(sid):
    d=load(f'data/modern-translation/{sid}.json')
    return d, [t['original_preview'] for t in d['translations']]

print("###### 修正3: t2784")
d,segs=getmodern('t2784')
full='\n'.join(segs)
print("全文含'捨'?", '捨' in full, "次数:",full.count('捨'))
print("全文含'不捨'?", '不捨' in full, "次数:",full.count('不捨'))
print("全文含'不舍'?", '不舍' in full, "次数:",full.count('不舍'))
print("全文含'反覆'?", '反覆' in full, "次数:",full.count('反覆'))
print("全文含'反复'?", '反复' in full, "次数:",full.count('反复'))
# also check previews(原文) contain 捨
_,pvs=getpreviews('t2784')
pf='\n'.join(pvs)
print("原文预览含'捨'?", '捨' in pf, pf.count('捨'))

print()
print("###### 修正4: t2855 段11")
d,segs=getmodern('t2855')
print("-- 段11 modern --")
print(segs[10])
print()
print("段11含'借貸'?", '借貸' in segs[10], "含'借贷'?", '借贷' in segs[10])
print("段11含'拨无因果'?", '拨无因果' in segs[10], "含'拨无因过'?", '拨无因过' in segs[10])
full='\n'.join(segs)
print("全文含'借貸'?", '借貸' in full, "含'拨无因果'?", '拨无因果' in full, "含'拨无因过'?", '拨无因过' in full)
