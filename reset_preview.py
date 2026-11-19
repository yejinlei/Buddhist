#!/usr/bin/env python3
import json, os
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)

sids = ["t1439","t0322","t0947","t1792","t2796","t0173","t2065","t0720","t1667","t1201","t1437","t0323"]

for sid in sids:
    task_path = f"data/baihua-tasks/{sid}.json"
    trans_path = f"data/modern-translation/{sid}.json"
    print(f"仅重置 {sid} 的original_preview字段 ...")
    with open(task_path,"r",encoding="utf-8") as f:
        task = json.load(f)
    with open(trans_path,"r",encoding="utf-8") as f:
        trans = json.load(f)
    n_task = len(task["translations"])
    n_trans = len(trans["translations"])
    if n_trans < n_task:
        for i in range(n_trans, n_task):
            trans["translations"].append({
                "original_preview": task["translations"][i]["original_preview"],
                "modern": "【小标题】【义解】本段待补。"
            })
    elif n_trans > n_task:
        trans["translations"] = trans["translations"][:n_task]
    for i in range(n_task):
        trans["translations"][i]["original_preview"] = task["translations"][i]["original_preview"]
    with open(trans_path,"w",encoding="utf-8") as f:
        json.dump(trans, f, ensure_ascii=False, indent=2)
    empty = sum(1 for t in trans["translations"] if not str(t.get("modern","")).strip() or str(t.get("modern","")).strip()=="【小标题】【义解】本段待补。")
    print(f"  完成: 共{n_task}段，待补={empty}")
print("全部original_preview重置完成！")
