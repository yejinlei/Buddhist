import json
import sys
import os

PROJECT_ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
TASK_DIR = os.path.join(PROJECT_ROOT, "data/baihua-tasks")
TRANS_DIR = os.path.join(PROJECT_ROOT, "data/modern-translation")

sids = sys.argv[1:]
for sid in sids:
    task_path = os.path.join(TASK_DIR, f"{sid}.skel.json")
    trans_path = os.path.join(TRANS_DIR, f"{sid}.json")
    with open(task_path, "r", encoding="utf-8") as f:
        task = json.load(f)
    with open(trans_path, "r", encoding="utf-8") as f:
        trans = json.load(f)
    # Reset original_preview
    previews = [t["original_preview"] for t in task["translations"]]
    for i, t in enumerate(trans["translations"]):
        t["original_preview"] = previews[i]
    with open(trans_path, "w", encoding="utf-8") as f:
        json.dump(trans, f, ensure_ascii=False, indent=2)
    print(f"{sid}: original_preview已重置，共{len(previews)}段")
print("全部重置完成")
