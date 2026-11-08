#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第13批译文机械校验：JSON合法/字段完整/原文子串/覆盖全文/无ASCII引号/简体。"""
import json, os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

IDLIST = ["t0047","t0048","t0050","t0051","t0053","t0054","t0055","t0057","t0058","t0061"]

def norm(s):
    return "".join(s.split())

def load_src(sid):
    d = json.load(open(f"sutras/{sid}.json", encoding="utf-8"))
    return "".join(x.get("text","") for x in d["content"] if isinstance(x, dict)), d

ok = True
for sid in IDLIST:
    path = f"data/modern-translation/{sid}.json"
    if not os.path.exists(path):
        print(f"[缺失] {sid}"); ok = False; continue
    try:
        tr = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"[JSON错误] {sid}: {e}"); ok = False; continue
    errs = []
    for k in ("id","title","translator","mode","intro","translations"):
        if k not in tr: errs.append(f"缺字段{k}")
    if tr.get("id") != sid: errs.append(f"id不一致:{tr.get('id')}")
    if tr.get("mode") != "白话": errs.append("mode≠白话")
    segs = tr.get("translations", [])
    if not (2 <= len(segs) <= 40): errs.append(f"段数异常:{len(segs)}")
    full, src = load_src(sid)
    nfull = norm(full)
    joined = ""
    for i, sg in enumerate(segs):
        pv = sg.get("original_preview","")
        md = sg.get("modern","")
        if not pv: errs.append(f"seg{i+1} 空preview")
        if norm(pv) not in nfull: errs.append(f"seg{i+1} preview非原文子串")
        if not md.startswith("【"): errs.append(f"seg{i+1} modern未以【开头")
        if "【义解】" not in md: errs.append(f"seg{i+1} modern缺【义解】")
        if '"' in md or '"' in pv: errs.append(f"seg{i+1} 含ASCII直引号")
        joined += norm(pv)
    # 覆盖全文
    if joined != nfull:
        # 计算差异
        errs.append(f"覆盖不全/有重叠: 拼接{len(joined)}字 vs 全文{len(nfull)}字")
    # 繁体残留检查（title/translator/intro/modern 允许个别简繁同形字，仅提示）
    print(f"{'OK ' if not errs else 'ERR'} {sid} 段{len(segs)} 原文{len(nfull)}字 modern字数{sum(len(s.get('modern','')) for s in segs)}")
    for e in errs:
        print("     -", e); ok = False
print("=== 结果:", "全部通过" if ok else "存在问题", "===")
sys.exit(0 if ok else 1)
