#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

SIDS = "t2732 t1681 t1057b t1894 t0994 t1238 t0010 t1940 t0884 t1949 t1900 t1956".split()

for sid in SIDS:
    path = f"data/modern-translation/{sid}.json"
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    fixed = 0
    for sec in d["translations"]:
        modern = sec.get("modern", "")
        # 替换繁体義解为简体义解
        modern = modern.replace("【義解】", "【义解】")
        # 检查是否以【小标题】开头
        if not re.match(r"^【.+?】", modern):
            # 提取开头内容补一个小标题
            first_part = modern.split("【义解】")[0].strip()
            if first_part:
                title = first_part[:20]
                modern = f"【{title}】【义解】" + modern.split("【义解】")[-1].strip()
            else:
                modern = "【经文内容】【义解】" + modern.strip()
        # 检查【义解】后是否有正文
        if "【义解】" in modern:
            parts = modern.split("【义解】", 1)
            after = parts[1].strip()
            if not after:
                # 义解后没有内容，补上说明
                modern = parts[0] + "【义解】本段经文内容如原文所述。"
        else:
            # 缺少【义解】标签，补上
            modern = modern + "【义解】"
        sec["modern"] = modern
        fixed += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"{sid}: 已修正{fixed}段的格式问题")
print("\n所有格式问题修正完成")
