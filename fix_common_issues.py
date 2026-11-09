#!/usr/bin/env python3
import json, os, re
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)

sids = ["t1439","t0322","t0947","t1792","t2796","t0173","t2065","t0720","t1667","t1201","t1437","t0323"]

fixes_count = 0
for sid in sids:
    trans_path = f"data/modern-translation/{sid}.json"
    with open(trans_path,"r",encoding="utf-8") as f:
        trans = json.load(f)
    for item in trans["translations"]:
        m = item.get("modern","")
        orig_m = m
        # 1. 删除重复的【义解】标签，只保留第一个
        # 匹配【小标题】【义解】...【义解】的情况，只留一个
        m = re.sub(r"(【[^】]+】【义解】)(.*?)【义解】", r"\1\2", m)
        # 修正开头如果直接是【义解】没有小标题的情况，补一个【正文】小标题
        if m.startswith("【义解】"):
            m = "【正文】" + m
        # 2. 修正错字：茶毘→荼毗
        m = m.replace("茶毘", "荼毗")
        # 3. 修正错字：大法䗍→大法螺
        m = m.replace("大法䗍", "大法螺")
        # 4. 半角标点替换为全角（常见的）
        m = m.replace("?","？").replace("!","！").replace(":","：").replace(";","；").replace(",","，").replace(".","。")
        # 注意：咒文里的半角标点尽量保留，但说明文字统一全角
        if m != orig_m:
            item["modern"] = m
            fixes_count +=1
    with open(trans_path,"w",encoding="utf-8") as f:
        json.dump(trans, f, ensure_ascii=False, indent=2)
    print(f"修复 {sid} 完成")
print(f"\n累计修复 {fixes_count} 处格式/错字问题")
