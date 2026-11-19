#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修正modern格式顺序：【小标题】+正文白话+【义解】+义解说明"""
import json, os, re, sys

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
TR = os.path.join(BASE, "data/modern-translation")
BATCH = "t2764a t1169 t1185 t1272 t1592 t2002 t0378 t2803 t1839 t2109 t0588 t1482 ".split()

def fix_one(sid):
    p = os.path.join(TR, sid+".json")
    d = json.load(open(p, encoding="utf-8"))
    fixed = 0
    for i, sec in enumerate(d["translations"]):
        m = sec.get("modern", "")
        # 匹配：【小标题】\n【义解】...\n【正文】...
        m1 = re.match(r"^【(.+?)】\n【义解】(.+?)\n【正文】(.+)$", m, re.DOTALL)
        if m1:
            title = m1.group(1)
            yj = m1.group(2).strip()
            body = m1.group(3).strip()
            new_m = f"【{title}】{body}\n【义解】{yj}"
            sec["modern"] = new_m
            fixed += 1
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    # 同步到baihua-tasks
    tp = os.path.join(BASE, "data/baihua-tasks", sid+".json")
    json.dump(d, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"{sid}: 修正 {fixed} 段格式")

for sid in BATCH:
    fix_one(sid)
print("格式修正完成")
