#!/usr/bin/env python3
import json, re, os
sids = "t1155 t0426 t1422a t1989 t0081 t2105 t1760 t0170 t0329 t1770 t2167 t1185a".split()
root = "/home/user/workspace/13511660557912876654/buddhist-ontology"
for sid in sids:
    path = f"{root}/data/modern-translation/{sid}.json"
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    fixed = 0
    for t in d["translations"]:
        m = t["modern"]
        # 替换繁体【義解】为简体【义解】
        m = m.replace("【義解】", "【义解】")
        # 去除开头空白换行
        m = m.lstrip()
        # 将小标题和【义解】之间的换行空格去掉，保证紧接
        m = re.sub(r'】\s*\n\s*【义解】', '】【义解】', m)
        t["modern"] = m
        # 检查
        ok = re.match(r"^【.+?】", m) and "【义解】" in m and not m.rstrip().endswith("【义解】")
        if ok:
            fixed += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f"{sid}: 共{len(d['translations'])}段，合格格式{fixed}段")
print("全部格式修复完成")
