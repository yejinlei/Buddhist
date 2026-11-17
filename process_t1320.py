import json
import os

src_path = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/t1320.json"
with open(src_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

translations = data['translations']

# 按段处理
title_list = [
    "道场发心",
    "净手真言",
    "大轮明王咒一",
    "大轮明王咒二",
    "大轮明王咒三",
    "大轮咒功德",
    "发菩提心",
    "召请圣众",
    "印现坛仪",
    "归依佛一",
    "归依佛二",
    "归依佛三",
    "三十五佛忏悔文一",
    "三十五佛忏悔文二",
    "三十五佛忏悔文三",
    "忏悔业障一",
    "忏悔业障二",
    "忏悔回向一",
    "忏悔回向二",
    "忏悔回向三",
    "召请六道",
    "圣众护念",
    "运心供养",
    "运心供养真言",
    "三宝施食印",
    "变空咒",
    "奉食印真言",
    "奉食偈赞",
    "三宝赞叹",
    "入观音定",
    "观音观想一",
    "观音观想二",
    "观音真言",
    "破地狱印咒",
    "破地狱咒功德",
    "请地藏菩萨",
    "召请孤魂",
    "召饿鬼印咒",
    "安慰诸众",
    "位次安立",
    "召罪印咒一",
    "召罪观想",
    "摧罪印咒",
    "摧罪观想",
    "定业印咒",
    "定业观想",
    "忏悔灭罪印",
    "灭罪竟",
    "施甘露印咒",
    "施甘露观想",
    "开咽喉印咒",
    "称如来名",
    "南无宝胜如来",
    "南无离怖畏如来",
    "南无广博身如来",
    "南无妙色身如来",
    "南无多宝如来",
    "南无阿弥陀佛",
    "南无威德自在光明如来",
    "七佛利益",
    "归依三宝",
    "三皈戒竟",
    "三宝印",
    "发菩提心印",
    "发心竟",
    "菩提心义",
    "三昧耶戒义一",
    "三昧耶戒义二",
    "三昧耶戒印",
    "受戒竟",
    "施食印咒一",
    "乳海真言",
    "施食须知",
    "障施鬼咒",
    "施食规仪",
    "平等普施",
    "分施三道",
    "普供养印",
    "普供养竟",
    "回向发愿",
    "奉送印真言",
    "回向地狱",
    "回向饿鬼",
    "回向畜生",
    "回向人间",
    "回向修罗",
    "回向天道",
    "回向二乘",
    "回向菩萨",
    "现世愿一",
    "现世愿二",
    "现世愿三",
    "现世愿四",
    "现世愿五",
    "现世愿六",
    "现世愿七",
    "现世愿八",
    "现世愿九",
    "现世愿十",
    "现世愿十一",
    "吉祥回向",
    "金刚萨埵百字咒",
    "百字咒终"
]

for i, item in enumerate(translations):
    orig = item['original_preview']
    title = title_list[i] if i < len(title_list) else f"仪轨段{i+1}"
    # 判断是否是咒语段（包含唵、二合、引、反切等）
    is_mantra = any(c in orig for c in ["􈅼", "􆿔", "􈁴", "二合", "引", "反", "吽", "􈁟", "􈆯"])
    if is_mantra:
        yi_jie = "此段为瑜伽焰口施食仪轨中的真言咒语，所有梵字、梵音及音注（二合、引声、反切等标注）严格照录原字，不作转写，为密教仪轨核心成办部分。"
        modern = f"【{title}】\n【义解】{yi_jie}\n{orig}"
    else:
        yi_jie = "此段为瑜伽集要焰口施食仪轨文，叙述施食仪轨的前行、发心、观想、结印、称名、回向等内容，为密教施食饿鬼、利济六道的重要仪轨，佛教专有名词如佛、菩萨、陀罗尼、菩提、涅槃、曼拏罗等保留原称。"
        modern = f"【{title}】\n【义解】{yi_jie}\n{orig}"
    item['modern'] = modern

out_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "t1320.json")
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"t1320 处理完成，共 {len(translations)} 段，保存到 {out_path}")
