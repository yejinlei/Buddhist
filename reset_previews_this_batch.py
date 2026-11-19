#!/usr/bin/env python3
import json, os
sids = "t1155 t0426 t1422a t1989 t0081 t2105 t1760 t0170 t0329 t1770 t2167 t1185a".split()
root = "/home/user/workspace/13511660557912876654/buddhist-ontology"
for sid in sids:
    skel_path = f"{root}/data/baihua-tasks/{sid}.skel.json"
    trans_path = f"{root}/data/modern-translation/{sid}.json"
    try:
        with open(skel_path, encoding="utf-8") as f:
            skel = json.load(f)
    except Exception as e:
        print(f"{sid} 骨架读取失败: {e}")
        continue
    try:
        with open(trans_path, encoding="utf-8") as f:
            content = f.read()
        # 替换非法控制字符
        content = content.replace('\r', '').replace('\t', '')
        trans = json.loads(content, strict=False)
    except Exception as e:
        print(f"{sid} 译文读取失败: {e}，尝试用骨架重建")
        # 从骨架重建，modern字段暂时空，后面重译
        trans = skel.copy()
        for t in trans["translations"]:
            t["modern"] = ""
    # 确保translations数组长度匹配骨架
    if len(trans["translations"]) != len(skel["translations"]):
        print(f"{sid}: 段数不匹配 译文{len(trans['translations'])} vs 骨架{len(skel['translations'])}，重建")
        trans = skel.copy()
        for t in trans["translations"]:
            t["modern"] = ""
    # 覆盖original_preview
    skel_previews = [t["original_preview"] for t in skel["translations"]]
    for i, t in enumerate(trans["translations"]):
        if i < len(skel_previews):
            t["original_preview"] = skel_previews[i]
        # 修复modern中的繁体标签
        if "modern" in t and t["modern"]:
            m = t["modern"].replace("【義解】", "【义解】")
            m = m.replace('\r', '')
            t["modern"] = m
    # 保存
    with open(trans_path, "w", encoding="utf-8") as f:
        json.dump(trans, f, ensure_ascii=False, indent=2)
    print(f"{sid}: original_preview已重置，共{len(trans['translations'])}段")
print("全部重置完成")
