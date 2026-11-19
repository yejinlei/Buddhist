import json
import os

src_path = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/t1994.json"
with open(src_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 重构为标准translations格式，每个para作为一个条目
translations = []
para_titles = [
    "杨岐开堂",
    "入院上堂一",
    "入院上堂二",
    "云盖开堂",
    "兴化开堂",
    "上堂机缘",
    "勘辨机缘",
    "道吾语要一",
    "道吾语要二",
    "偈颂法语",
    "语录序跋",
    "兴化录上堂",
    "勘辨自赞"
]

for i, para in enumerate(data['paras']):
    title = para_titles[i]
    yi_jie = "此段为杨岐方会和尚（临济宗杨岐派祖师）的上堂开示、机缘勘辨、偈颂及序跋，机锋峻烈，直指人心，棒喝交驰，显禅宗临济宗风，专有名词如机锋、棒喝、公案、衲僧、菩提、涅槃等保留原称。"
    modern = f"【{title}】\n【义解】{yi_jie}\n{para}"
    translations.append({
        "original_preview": para,
        "modern": modern
    })

data['translations'] = translations

out_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "t1994.json")
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"t1994 处理完成，共 {len(translations)} 段，保存到 {out_path}")
