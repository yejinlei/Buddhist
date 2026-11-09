#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t1917《六妙法门》白话精译构建（隋·智顗说，114段）。
- 读取 data/baihua-tasks/t1917.json（114段，traditional），original_preview 一字不改；
- 每段 modern = 【小标题】【义解】<白话义解>\n<原文逐字>；
- section 留空，由 _b122/finalize.py 简体化时从 modern 首【...】自动提取；
- 输出 data/modern-translation/t1917.json。
"""
import json, os

ROOT = '/home/user/workspace/13511660557912876654/buddhist-ontology'
SRC  = os.path.join(ROOT, 'data/baihua-tasks/t1917.json')
OUT  = os.path.join(ROOT, 'data/modern-translation/t1917.json')
SEG_JSON = '/tmp/t1917_seg.json'

INTRO = ("《六妙法门》一卷，隋天台智者大师智顗于金陵瓦官寺所说。"
         "「六妙门」即数、随、止、观、还、净六种安那般那（数息观）禅法，为宗门禅修纲要。"
         "智者大师依次第相生、随便宜、随对治、相摄、通别、旋转、观心、圆观、证相共十门开示："
         "从凡夫、外道、声闻、缘觉的次第禅，到菩萨旋转陀罗尼、观心、圆顿六妙门，"
         "终以《法华经》六根清净、《华严经》初发心便成正觉、阿字门茶字门、"
         "十住十行十回向十地等觉妙觉的圆证相收束，系统建立天台止观修行体系。")

def main():
    SEG = json.load(open(SEG_JSON, encoding='utf-8'))
    assert len(SEG) == 114, f"SEG={len(SEG)}"
    src = json.load(open(SRC, encoding='utf-8'))
    trans_src = src['translations']
    assert len(trans_src) == 114
    out = {
        "id": src["id"], "title": src["title"], "translator": src["translator"],
        "mode": "baihua", "intro": INTRO, "sutraPath": "../sutras/t1917.json",
        "translations": []
    }
    for i,(s,(title,yj)) in enumerate(zip(trans_src, SEG)):
        orig = s['original_preview']
        modern = f"【{title}】【义解】{yj}\n{orig}"
        assert '"' not in modern and "'" not in modern, f"seg{i+1} half quote"
        # section 留空，由 finalize.py 自动填入首【...】（含括号）
        out['translations'].append({"section": "", "original_preview": orig, "modern": modern})
    json.dump(out, open(OUT,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
    print("wrote", OUT, "segments", len(out['translations']))

if __name__ == '__main__':
    main()
