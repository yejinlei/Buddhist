import json, os

# 加载原有图谱数据
with open('js/graph-data.js', 'r', encoding='utf-8') as f:
    content = f.read()
    old_data = json.loads(content.replace('const graphData = ', ''))

old_nodes = old_data['nodes']
old_edges = old_data['edges']

# 加载清洗后的经数据
with open('sutras/index.json', 'r', encoding='utf-8') as f:
    sutras = json.load(f)

# 加载部类映射
with open('ontology/category-mapping.json', 'r', encoding='utf-8') as f:
    cat_map = json.load(f)

# 加载多译本关系
with open('ontology/parallel-translations.json', 'r', encoding='utf-8') as f:
    parallels = json.load(f)

# 加载本体现有定义（宗派、概念、人物）
with open('ontology/relations.json', 'r', encoding='utf-8') as f:
    rel = json.load(f)
with open('ontology/concepts.json', 'r', encoding='utf-8') as f:
    concepts = json.load(f)
with open('ontology/people.json', 'r', encoding='utf-8') as f:
    people = json.load(f)
with open('ontology/schools.json', 'r', encoding='utf-8') as f:
    schools = json.load(f)

# ========== 添加节点 ==========
nodes = []
existing_ids = set()

# 1. 添加部类节点
for code, cat in cat_map.items():
    nid = f'cat_{code}'
    if nid not in existing_ids:
        nodes.append({
            'id': nid,
            'name': cat['name'],
            'type': 'category',
            'label': cat['name'],
            'category': '部类',
            'count': cat['count'],
            'symbolSize': min(20 + cat['count']//5, 60)
        })
        existing_ids.add(nid)

# 2. 添加核心经典节点（每部类选3-5部核心经，避免节点太多太卡）
core_sutras = ['t0001','t0026','t0099','t0220','t0235','t0251','t0262','t0263',
               't0285','t0278','t0279','t0310','t0374','t0375','t0474','t0475',
               't0945','t1252','t1509','t1564','t1509','t1448','t1484','t1792','t2060']
for tid in core_sutras:
    s = sutras.get(tid)
    if s and tid not in existing_ids:
        nodes.append({
            'id': tid,
            'name': s['title'],
            'type': 'sutra',
            'label': s['short_title'],
            'category': '经典',
            'translator': s.get('translator',''),
            'symbolSize': 18
        })
        existing_ids.add(tid)

# 3. 添加多译本组里的所有译本
for group in parallels:
    for sutra in group['sutras']:
        tid = sutra['id']
        s = sutras.get(tid)
        if s and tid not in existing_ids:
            nodes.append({
                'id': tid,
                'name': s['title'],
                'type': 'sutra',
                'label': s['short_title'],
                'category': '经典',
                'translator': s.get('translator',''),
                'symbolSize': 18
            })
            existing_ids.add(tid)

# 4. 添加原有节点
for n in old_nodes:
    if n['id'] not in existing_ids:
        nodes.append(n)
        existing_ids.add(n['id'])

# ========== 添加边 ==========
edges = []
existing_edges = set()

def add_edge(s, t, label):
    key = f"{s}__{t}"
    if key not in existing_edges and s in existing_ids and t in existing_ids:
        edges.append({'source': s, 'target': t, 'label': label})
        existing_edges.add(key)

# 1. 经 -> 部类 边
for tid in core_sutras:
    s = sutras.get(tid)
    if s and s.get('category_code'):
        add_edge(tid, f'cat_{s["category_code"]}', '属於')

for group in parallels:
    for sutra in group['sutras']:
        tid = sutra['id']
        s = sutras.get(tid)
        if s and s.get('category_code'):
            add_edge(tid, f'cat_{s["category_code"]}', '属於')

# 2. 同经异译边
for group in parallels:
    sutra_ids = [s['id'] for s in group['sutras']]
    for i in range(len(sutra_ids)):
        for j in range(i+1, len(sutra_ids)):
            add_edge(sutra_ids[i], sutra_ids[j], '异译本')

# 3. 部类 -> 宗派 边
for code, cat in cat_map.items():
    if cat.get('school'):
        add_edge(f'cat_{code}', f'school_{cat["school"]}', '为其核心依据')

# 4. 添加原有边
for e in old_edges:
    s = e['source']
    t = e['target']
    key = f"{s}__{t}"
    if key not in existing_edges and s in existing_ids and t in existing_ids:
        edges.append(e)
        existing_edges.add(key)

# 更新类型配置
categories = [
    {'name': '部类', 'itemStyle': {'color': '#8B4513'}},
    {'name': '经典', 'itemStyle': {'color': '#B22222'}},
    {'name': '宗派', 'itemStyle': {'color': '#DAA520'}},
    {'name': '概念', 'itemStyle': {'color': '#2E8B57'}},
    {'name': '佛', 'itemStyle': {'color': '#FFD700'}},
    {'name': '菩萨', 'itemStyle': {'color': '#FFB6C1'}},
    {'name': '罗汉', 'itemStyle': {'color': '#DDA0DD'}},
    {'name': '译师', 'itemStyle': {'color': '#4682B4'}},
    {'name': '祖师', 'itemStyle': {'color': '#708090'}},
    {'name': '学者', 'itemStyle': {'color': '#20B2AA'}}
]

output = f"const graphData = {json.dumps({'nodes': nodes, 'edges': edges, 'categories': categories}, ensure_ascii=False, indent=2)};"
with open('js/graph-data.js', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"✅ 图谱扩充完成：")
print(f"   节点总数：{len(nodes)}")
print(f"   边总数：{len(edges)}")
print(f"   新增部类节点：{len(cat_map)}")
print(f"   新增经典节点：{len([n for n in nodes if n['type']=='sutra'])}")
print(f"   新增异译关系：{len(parallels)}组")
