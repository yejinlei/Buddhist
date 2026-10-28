import json, os, re
from collections import defaultdict

SUTRAS_DIR = "sutras"

print("加载全量经目索引...")
with open(os.path.join(SUTRAS_DIR, 'index.json'), 'r', encoding='utf-8') as f:
    index = json.load(f)
print(f"共{len(index)}部经")

# 第一步：提取经名主干，识别同经异译
def extract_main_title(title):
    """去除书名号、卷次、译本说明，提取经名主干"""
    title = title.replace('《', '').replace('》', '')
    # 去掉末尾的"第X卷"、"卷X"、"X卷"
    title = re.sub(r'[（(].*?[）)]', '', title)
    title = re.sub(r'第[一二三四五六七八九十百千0-9]+卷.*$', '', title)
    title = re.sub(r'[一二三四五六七八九十百千0-9]+卷$', '', title)
    # 去掉常见异译标注
    for suffix in ['本', '譯', '译', '異譯', '异译', '經', '经']:
        if title.endswith(suffix) and len(title) > len(suffix)+1:
            pass
    return title.strip()

# 按主干经名分组
title_groups = defaultdict(list)
for s in index:
    main_title = extract_main_title(s['title'])
    # 进一步标准化：去掉"佛说"、"佛说"前缀
    norm_title = main_title.replace('佛說', '').replace('佛说', '')
    s['main_title'] = main_title
    s['norm_title'] = norm_title
    title_groups[norm_title].append(s)

# 提取有多译本的经典
parallel_translations = []
for title, sutras in title_groups.items():
    if len(sutras) >= 2 and len(title) >= 2:
        # 排除过短或明显不相关的分组
        if len(title) < 2: continue
        parallel_translations.append({
            'title': title,
            'count': len(sutras),
            'sutras': sorted(sutras, key=lambda x: x['time_from'] or 0)
        })

parallel_translations.sort(key=lambda x: -x['count'])
print(f"识别到有多个译本的经典：{len(parallel_translations)}组")

# 输出前20组多译本经典
print("\n=== 核心多译本经典（TOP20）===")
for pt in parallel_translations[:20]:
    print(f"【{pt['title']}】{pt['count']}个译本：")
    for s in pt['sutras']:
        print(f"  - {s['id'].upper()} {s['title']} | {s['translator']} | {s['time_from']} | {s['vol']}")

# 保存异译关系到本体数据
os.makedirs('ontology', exist_ok=True)
with open('ontology/parallel_translations.json', 'w', encoding='utf-8') as f:
    json.dump(parallel_translations, f, ensure_ascii=False, indent=2)
print(f"\n异译关系已保存到 ontology/parallel_translations.json")

# 第二步：按部类映射到宗派
category_to_school = {
    '阿含部类': ['阿含部', '原始佛教', '上座部'],
    '般若部类': ['般若', '中观宗', '三论宗'],
    '法華部类': ['天台宗', '法华宗'],
    '華嚴部类': ['华严宗'],
    '寶積部类': ['宝积部', '大乘通教'],
    '涅槃部类': ['涅槃宗'],
    '大集部类': ['大集部'],
    '密教部类': ['密宗', '真言宗'],
    '律部类': ['律宗'],
    '中觀部类': ['三论宗', '中观宗'],
    '瑜伽部类': ['唯识宗', '法相宗', '瑜伽行派'],
    '論集部类': ['论藏', '各宗通依'],
    '禪宗部类': ['禅宗'],
    '淨土宗部类': ['净土宗'],
    '毘曇部类': ['毗昙宗', '俱舍宗', '说一切有部'],
    '本緣部类': ['本缘部', '因果报应'],
    '經集部类': ['经集部', '诸经杂集'],
    '史傳部类': ['史传部', '佛教史'],
    '事彙部类': ['事汇部', '佛教百科'],
    '敦煌寫本部类': ['敦煌写本', '佚典']
}

# 保存部类-宗派映射
with open('ontology/category_school_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(category_to_school, f, ensure_ascii=False, indent=2)

print("\n本体关系构建第一阶段完成，下一步将把这些关系导入图谱")
