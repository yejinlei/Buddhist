import json
import os

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
files = ["t1239", "t0850", "t2075", "t1251", "t0953", "t0887", "t2871", "t0682", "t0341", "t1757", "t2810", "t1797"]

# 找出各经的密咒段
for fid in files:
    path = os.path.join(base_dir, f"{fid}.json")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    trans = data["translations"]
    mantra_segs = []
    for i, seg in enumerate(trans):
        orig = seg.get("original_preview", "")
        if any(k in orig for k in ["呪曰", "陀羅尼曰", "真言曰", "心呪", "即說呪曰"]):
            mantra_segs.append(i)
    print(f"\n===== {fid}: 密咒段索引 {mantra_segs[:5]}...共{len(mantra_segs)}段 =====")
    # 看第一个咒段
    if mantra_segs:
        seg = trans[mantra_segs[0]]
        print(f"原文: {seg['original_preview'][:150]}")
        print(f"白话: {seg['modern'][:300]}")
