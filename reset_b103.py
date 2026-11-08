import json, os
ROOT = "."
batch = "jingang_jiumo t2139 t1961 t2101 t2019a t1951 t1897 t2750 t1103a t1867 t1632 t2005".split()
tasks_dir = "data/baihua-tasks"
out_dir = "data/modern-translation"

for sid in batch:
    skel_path = os.path.join(tasks_dir, f"{sid}.json")
    out_path = os.path.join(out_dir, f"{sid}.json")
    with open(skel_path, "r", encoding="utf-8") as f:
        skel = json.load(f)
    with open(out_path, "r", encoding="utf-8") as f:
        out = json.load(f)
    # 用骨架的original_preview覆盖输出中的同字段
    for i, (skel_seg, out_seg) in enumerate(zip(skel["translations"], out["translations"])):
        out_seg["original_preview"] = skel_seg["original_preview"]
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"重置完成：{sid}，段数：{len(out['translations'])}")
print("所有12部original_preview字段已从骨架重置完毕。")
