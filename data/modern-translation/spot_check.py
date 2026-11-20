import json
import os

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"

# 抽查几个问题段实际内容
samples = [
    ("t1239", 9), ("t1239", 19), ("t1239", 58),
    ("t0850", 2), ("t0850", 81), ("t0850", 128), ("t0850", 175),
    ("t2075", 1),  # 零问题，对比看
    ("t2810", 1),  # 零问题，对比看
]

for fid, seg_num in samples:
    path = os.path.join(base_dir, f"{fid}.json")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    trans = data["translations"]
    seg = trans[seg_num-1]
    print(f"===== {fid} 第{seg_num}段 =====")
    print(f"original_preview: {repr(seg.get('original_preview', '')[:200])}")
    print(f"modern:\n{seg.get('modern', '')[:500]}")
    print()
