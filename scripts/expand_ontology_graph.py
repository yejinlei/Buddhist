import json, os

# 加载已有本体图
with open('data/graph_data.js', 'r', encoding='utf-8') as f:
    content = f.read()
# 提取nodes和edges
exec(content.replace('const ', '').replace('graphData =', 'graphData=').replace('export', ''))

nodes = graphData['nodes']
edges = graphData['edges']
existing_ids = {n['id'] for n in nodes}

# 加载异译关系
with open('ontology/parallel_translations.json', 'r', encoding='utf-8') as f:
    parallels = json.load(f)

# 加载部类映射
with open('ontology/category_school_mapping.json', 'r', encoding='utf-8') as f:
    cat_school = json.load(f)

# 加载全量索引
with open('sutras/index.json', 'r', encoding='utf-8') as f:
    all_sutras = json.load(f)
sutra_map = {s['id']: s for s in all_sutras}

# 添加部类节点（如果不存在）
cat_node_ids = set()
for cat in set(s.get('category', '').split(',')[0] for s in all_sutras if s.get('category')):
    if not cat: continue
    cat_id = 'cat_' + cat.replace('類', '类')
    if cat_id not in existing_ids:
        nodes.append({
            'id': cat_id,
            'name': cat.replace('類', '类').replace('部类', '部'),
            'type': 'category',
            'size': 30
        })
        existing_ids.add(cat_id)
    cat_node_ids.add(cat_id)
    # 部类-宗派关系（添加到已有宗派节点）
    for school in cat_school.get(cat, []):
        school_id = 'school_' + school
        if school_id in existing_ids and any(n['id']==school_id for n in nodes):
            edges.append({source: cat_id, target: school_id, relation: '宗依', label: '为所依经典部类'})

# 添加核心多译本经典节点
added_sutras = 0
for pt in parallels[:30]:  # 前30组多译本
    for s in pt['sutras']:
        sid = 'sutra_' + s['id']
        if sid not in existing_ids:
            nodes.append({
                'id': sid,
                'name': s['title'].replace('《', '').replace('》', '')[:12],
                'type': 'sutra',
                'full_title': s['title'],
                'translator': s['translator'],
                'year': s['time_from'],
                'size': 25
            })
            existing_ids.add(sid)
            added_sutras += 1
        # 连接到对应部类
        cat = s.get('category', '').split(',')[0]
        if cat:
            cat_id = 'cat_' + cat.replace('類', '类')
            edges.append({source: sid, target: cat_id, relation: '摄属', label: '属于'})
    # 添加异译关系
    sutra_ids = ['sutra_' + s['id'] for s in pt['sutras']]
    for i in range(len(sutra_ids)):
        for j in range(i+1, len(sutra_ids)):
            if sutra_ids[i] in existing_ids and sutra_ids[j] in existing_ids:
                edges.append({source: sutra_ids[i], target: sutra_ids[j], relation: '异译', label: '同经异译'})

# 更新图数据
output = f"const graphData = {json.dumps({'nodes': nodes, 'edges': edges}, ensure_ascii=False, indent=2)};\n\nexport default graphData;"
with open('data/graph_data.js', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"✅ 本体图谱扩充完成！")
print(f"新增节点：{added_sutras}部核心经 + {len(cat_node_ids)}个部类节点")
print(f"当前图谱总节点数：{len(nodes)}，关系数：{len(edges)}")
print(f"新增异译关系：{sum(len(p['sutras'])*(len(p['sutras'])-1)//2 for p in parallels[:30])}组")
