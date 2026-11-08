# -*- coding: utf-8 -*-
"""为第54批生成独立校对材料（原文全文 + 逐段白话），供校对 worker 复核。"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUT = os.path.join(ROOT, "sutras")
TR = os.path.join(ROOT, "data", "modern-translation")
OUT = os.path.join(ROOT, "data", "baihua-review")
os.makedirs(OUT, exist_ok=True)

GROUPS = {
    "b54-g1": ["t1601", "t1872"],
    "b54-g2": ["t2861", "t1570"],
    "b54-g3": ["t1886", "t0617"],
}

TITLES = {
    "t1601": "辯中邊論頌（彌勒菩薩說・唐 玄奘譯）",
    "t1872": "華嚴策林（唐 法藏述）",
    "t2861": "泉州千佛新著諸祖師頌",
    "t1570": "廣百論本（聖天菩薩造・唐 玄奘譯）",
    "t1886": "原人論（唐 宗密述）",
    "t0617": "思惟略要法（姚秦 鳩摩羅什譯）",
}

for gname, tids in GROUPS.items():
    lines = [f"# 白话译文校对材料（{gname}）\n",
             "请逐段核对：译文是否忠实原文、有无错译/漏译/增译、有无杜撰、法数与术语是否准确、体例是否规范（每段白话须以【小标题】开头、含【义解】且其后有正文）、有无半角引号。\n"]
    for tid in tids:
        d = json.load(open(os.path.join(SUT, tid + ".json"), encoding="utf-8"))
        raw = "\n".join(c["text"] for c in d["content"])
        tr = json.load(open(os.path.join(TR, tid + ".json"), encoding="utf-8"))
        lines.append(f"\n\n{'='*70}\n## {tid} {TITLES.get(tid, '')}\n{'='*70}\n")
        lines.append("### 经文原文（全文）\n\n```\n" + raw + "\n```\n")
        lines.append(f"### 逐段白话译文（共 {len(tr['translations'])} 段）\n")
        for i, s in enumerate(tr["translations"], 1):
            lines.append(f"\n**段{i}**\n\n【原文切片】{s['original_preview']}\n\n【白话】{s['modern']}\n")
    p = os.path.join(OUT, gname + ".md")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    print("已写", p)
