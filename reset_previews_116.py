import json, os
sutra_ids = ["t2029","t1022b","t1107","t2174a","t2174","t1309","t1392","t1164","t1090","t1377","t1125","t1132"]
task_dir = "data/baihua-tasks"
trans_dir = "data/modern-translation"

for sid in sutra_ids:
    task_path = os.path.join(task_dir, f"{sid}.json")
    trans_path = os.path.join(trans_dir, f"{sid}.json")
    
    with open(task_path, "r", encoding="utf-8") as f:
        task = json.load(f)
    with open(trans_path, "r", encoding="utf-8") as f:
        trans = json.load(f)
    
    # 从骨架提取original_preview
    task_previews = [seg["original_preview"] for seg in task["translations"]]
    # 覆盖写入译文的original_preview
    for i, seg in enumerate(trans["translations"]):
        seg["original_preview"] = task_previews[i]
    
    with open(trans_path, "w", encoding="utf-8") as f:
        json.dump(trans, f, ensure_ascii=False, indent=2)
    
    print(f"已重置 {sid} 的 original_preview，共 {len(task_previews)} 段")

print("全部重置完成")
