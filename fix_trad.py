#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

# 加载繁简转换表
with open("data/hant2simp_full.json", encoding="utf-8") as f:
    h2s = json.load(f)

def trad2simp(text):
    # 保留咒文、梵字不转换，只转换说明文字
    # 简单逐字转换，先处理常见繁体
    result = []
    for c in text:
        if c in h2s:
            result.append(h2s[c])
        else:
            result.append(c)
    return "".join(result)

SIDS = "t2732 t1681 t1057b t1894 t0994 t1238 t0010 t1940 t0884 t1949 t1900 t1956".split()

for sid in SIDS:
    path = f"data/modern-translation/{sid}.json"
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    for sec in d["translations"]:
        m = sec["modern"]
        # 分离咒文部分？简单先全转，专有名词后续修正
        m = trad2simp(m)
        # 修正特定错误：
        m = m.replace("欝多罗僧", "郁多罗僧")
        m = m.replace("毘卢遮那", "毗卢遮那")
        m = m.replace("迴向", "回向")
        m = m.replace("懺悔", "忏悔")
        m = m.replace("梵箧", "梵夹")
        sec["modern"] = m
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"{sid}: 繁简转换完成")

print("批量繁简转换完成")
