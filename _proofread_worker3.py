#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二轮独立复核 worker3 - 加强版"""
import json, os, re

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
MOD = os.path.join(BASE,"data/modern-translation")
SRC = os.path.join(BASE,"sutras")
IDS = ["t0131","t0102","t1046","t1379","t0560","t0096","t2836","t0655","t0934","t0218","t1405","t0779"]
REQ_TOP = ["id","title","translator","vol","translations","section"]
REQ_SEG = ["original_preview","modern","section"]

def ws(s): return re.sub(r"[\s\u3000]+","",s or "")

issues = []
def add(sid,w,d,det=""): issues.append((sid,w,d,det))

results = []
for sid in IDS:
    with open(os.path.join(MOD,f"{sid}.json"),encoding='utf-8') as f: m=json.load(f)
    with open(os.path.join(SRC,f"{sid}.json"),encoding='utf-8') as f: s=json.load(f)
    
    orig_text = "\n".join(c.get("text","") for c in s.get("content",[]))
    orig_nows = ws(orig_text)
    
    # 顶层字段
    missing_top = [k for k in REQ_TOP if k not in m]
    if missing_top:
        add(sid,"顶层",f"缺字段: {missing_top}","")
    
    segs = m.get("translations",[])
    if not isinstance(m.get("section"),list):
        add(sid,"顶层",f"顶层section字段不是list: {type(m.get('section')).__name__}，各seg含section即可","")
    
    # 逐段检查
    cat_pv = []
    for i,seg in enumerate(segs):
        sn = i+1
        for k in REQ_SEG:
            if k not in seg:
                add(sid,f"seg{sn}",f"缺字段 {k}","")
        cat_pv.append(seg.get("original_preview","") or "")
    
    cat_nows = ws("".join(cat_pv))
    # 确认是连续子串
    if cat_nows not in orig_nows:
        # 找开头并定位差异
        head = cat_nows[:min(40,len(cat_nows))]
        pos = orig_nows.find(head)
        if pos<0:
            add(sid,"全局","拼接preview开头在原文中找不到",f"开头: {head}")
        else:
            # 检查后续每个字
            i=0
            while i<len(cat_nows) and pos+i<len(orig_nows) and cat_nows[i]==orig_nows[pos+i]:
                i+=1
            if i<len(cat_nows):
                add(sid,"全局",f"preview拼接在第{i}字处不匹配",
                    f"原文: {orig_nows[pos+i:pos+i+15]}\n预览: {cat_nows[i:i+15]}")
            elif len(cat_nows)!=len(orig_nows)-pos:
                add(sid,"全局","preview长度异常",f"preview_nows={len(cat_nows)}, 原文剩余={len(orig_nows)-pos}")
    else:
        pos = orig_nows.find(cat_nows)
        # 检查是否覆盖完整原文（除了标题？）
        # 注意：t0131开头有"後漢安息沙門安世高譯" 这一行也是正文
    
    # 义理 / 译文通读检查：把每段modern打印出来
    full_md = "\n".join(seg.get("modern","") for seg in segs)
    results.append((sid, s["title"], len(segs), len(cat_nows), len(orig_nows), pos if 'pos' in dir() else -1, full_md))

# 报告
print(f"共发现 {len(issues)} 条问题\n")
for sid,w,d,det in issues:
    print(f"[{sid}|{w}] {d}")
    if det: print(f"   {det}")

print("\n=== 各经预览覆盖情况 ===")
for sid,title,ns,pc,oc,pos,_ in results:
    cover = f"{pos}..{pos+pc}/{oc} ({pc}/{oc})" if pos>=0 else "未匹配"
    print(f"{sid} {title[:14]:<14} 段={ns} preview_nows={pc} orig_nows={oc} 覆盖={cover}")

# 把每经的modern译文保存供人工抽读
out_dir = os.path.join(BASE,"_w3_dump")
os.makedirs(out_dir, exist_ok=True)
for sid,title,ns,pc,oc,pos,md in results:
    with open(os.path.join(out_dir,f"{sid}.txt"),"w",encoding='utf-8') as f:
        f.write(md)
print(f"\n译文已dump到 {out_dir} 供人工抽读")
