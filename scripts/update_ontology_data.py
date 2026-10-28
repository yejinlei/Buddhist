import json, os

# 加载已有本体数据
with open('data/sutras-expanded.json', 'r', encoding='utf-8') as f:
    sutras = json.load(f)
with open('data/concepts-expanded.json', 'r', encoding='utf-8') as f:
    concepts = json.load(f)
with open('data/sects-expanded.json', 'r', encoding='utf-8') as f:
    sects = json.load(f)
with open('data/relations-expanded.json', 'r', encoding='utf-8') as f:
    relations = json.load(f)

# 加载全量索引和异译关系
with open('sutras/index.json', 'r', encoding='utf-8') as f:
    all_sutras = json.load(f)
with open('ontology/parallel_translations.json', 'r', encoding='utf-8') as f:
    parallels = json.load(f)
with open('ontology/category_school_mapping.json', 'r', encoding='utf-8') as f:
    cat_school_map = json.load(f)

# 1. 添加部类节点到概念体系
existing_ids = {c['id'] for c in concepts}
cat_count = 0
for cat_name in set(s.get('category', '').split(',')[0] for s in all_sutras if s.get('category')):
    if not cat_name: continue
    cat_id = 'cat_' + cat_name.replace('類', '类')
    if cat_id not in existing_ids:
        concepts.append({
            'id': cat_id,
            'name': cat_name.replace('類', '类'),
            'type': 'canon_category',
            'description': f'大正藏{cat_name.replace("類","类")}，共{len([s for s in all_sutras if s.get("category","").startswith(cat_name)])}部经',
            'layer': 'L4_文本载体层'
        })
        existing_ids.add(cat_id)
        cat_count += 1

# 2. 添加核心多译本经典到sutras
existing_sutra_ids = {s['id'] for s in sutras}
added_sutra_count = 0
for pt in parallels[:30]:  # 前30组多译本经典
    for s in pt['sutras']:
        sid = 'sutra_' + s['id']
        if sid not in existing_sutra_ids:
            sutras.append({
                'id': sid,
                'title': s['title'],
                'sutra_id': s['id'].upper(),
                'translator': s['translator'],
                'year': s.get('time_from', ''),
                'vol': s.get('vol', ''),
                'category': s.get('category', ''),
                'char_count': s.get('actual_char_count', 0),
                'juan_count': s.get('juan_count', 0),
                'layer': 'L4_文本载体层'
            })
            existing_sutra_ids.add(sid)
            added_sutra_count += 1

# 3. 添加关系：经→部类、部类→宗派、异译关系
added_relations = 0
# 经→部类
for s in sutras:
    cat = s.get('category', '').split(',')[0]
    if cat:
        cat_id = 'cat_' + cat.replace('類', '类')
        rel = {'source': s['id'], 'target': cat_id, 'type': '摄属', 'label': '属于', 'evidence': '大正藏经目分类'}
        if rel not in relations:
            relations.append(rel)
            added_relations += 1

# 部类→宗派
for cat, schools in cat_school_map.items():
    cat_id = 'cat_' + cat.replace('類', '类')
    for school_name in schools:
        school_id = 'school_' + school_name
        # 找宗派节点
        if any(s['id'] == school_id for s in sects):
            rel = {'source': cat_id, 'target': school_id, 'type': '宗依', 'label': '所依经典部类', 'evidence': '判教体系'}
            if rel not in relations:
                relations.append(rel)
                added_relations += 1

# 异译关系
for pt in parallels:
    sutra_ids = ['sutra_' + s['id'] for s in pt['sutras']]
    for i in range(len(sutra_ids)):
        for j in range(i+1, len(sutra_ids)):
            if sutra_ids[i] in existing_sutra_ids and sutra_ids[j] in existing_sutra_ids:
                rel = {'source': sutra_ids[i], 'target': sutra_ids[j], 'type': '异译', 'label': f'同本异译（{pt["title"]}）', 'evidence': f'均为{pt["title"]}的不同译本'}
                if rel not in relations:
                    relations.append(rel)
                    added_relations += 1

# 保存更新后的数据
with open('data/concepts-expanded.json', 'w', encoding='utf-8') as f:
    json.dump(concepts, f, ensure_ascii=False, indent=2)
with open('data/sutras-expanded.json', 'w', encoding='utf-8') as f:
    json.dump(sutras, f, ensure_ascii=False, indent=2)
with open('data/relations-expanded.json', 'w', encoding='utf-8') as f:
    json.dump(relations, f, ensure_ascii=False, indent=2)

print(f"✅ 本体数据扩充完成！")
print(f"- 新增部类节点：{cat_count}个（共{len(concepts)}个概念/部类节点）")
print(f"- 新增经典节点：{added_sutra_count}部（共{len(sutras)}部经典）")
print(f"- 新增本体关系：{added_relations}条（共{len(relations)}条关系）")
print(f"- 识别到多译本经典：{len(parallels)}组，包含心经、华严、涅槃、金刚经等核心经典")
