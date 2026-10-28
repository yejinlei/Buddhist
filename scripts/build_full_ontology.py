import json, os, re

# 加载原有数据
with open('data/concepts.json', 'r', encoding='utf-8') as f:
    concepts = json.load(f)
with open('data/persons.json', 'r', encoding='utf-8') as f:
    persons = json.load(f)
with open('data/sects.json', 'r', encoding='utf-8') as f:
    sects = json.load(f)
with open('data/sutras.json', 'r', encoding='utf-8') as f:
    sutras_old = json.load(f)
with open('data/relations.json', 'r', encoding='utf-8') as f:
    relations = json.load(f)

# 加载清洗后的全量经数据
with open('sutras/index.json', 'r', encoding='utf-8') as f:
    sutras_full = json.load(f)
# 加载部类映射
with open('ontology/category_school_mapping.json', 'r', encoding='utf-8') as f:
    cat_map = json.load(f)
# 加载多译本关系
with open('ontology/parallel_translations.json', 'r', encoding='utf-8') as f:
    parallels = json.load(f)

# ========== 1. 添加部类节点 ==========
category_nodes = []
for code, cat in cat_map.items():
    category_nodes.append({
        'id': f'cat_{code}',
        'type': 'category',
        'name': cat['name'],
        'layer': '部类',
        'definition': f"{cat['name']}，共{cat['count']}部经典，核心典籍包括：{', '.join(cat.get('core_sutras', [])[:5])}",
        'count': cat['count'],
        'school': cat.get('school', '')
    })

# ========== 2. 选择要加入图谱的核心经典（避免节点太多卡顿） ==========
core_sutra_ids = set()
for s in sutras_old:
    core_sutra_ids.add(s['id'])
for group in parallels:
    for s in group['sutras']:
        core_sutra_ids.add(s['id'])
representatives = [
    't0001', 't0026', 't0099', 't0220', 't0221', 't0223', 't0250',
    't0262', 't0263', 't0278', 't0279', 't0310', 't0374', 't0375',
    't0474', 't0475', 't0945', 't1252', 't1448', 't1509', 't1564',
    't1792', 't2060'
]
for tid in representatives:
    core_sutra_ids.add(tid)

sutra_nodes = []
sutra_node_ids = set()
for tid in core_sutra_ids:
    s = sutras_full.get(tid)
    if not s: continue
    title = s.get('title', '')
    short_title = s.get('short_title', title[:8])
    sutra_nodes.append({
        'id': tid,
        'type': 'sutra',
        'name': short_title,
        'full_title': title,
        'translator': s.get('translator', ''),
        'dynasty': s.get('dynasty', ''),
        'vol': s.get('vol', ''),
        'category_code': s.get('category_code', ''),
        'category_name': s.get('category', ''),
        'juan_count': s.get('juan_count', 0),
        'word_count': s.get('word_count', 0)
    })
    sutra_node_ids.add(tid)

# ========== 3. 扩充关系 ==========
# 经 -> 部类
for s in sutra_nodes:
    if s.get('category_code'):
        relations.append({
            'id': f'r{len(relations)+1:03d}',
            'type': 'shuyu',
            'source': s['id'],
            'target': f'cat_{s["category_code"]}',
            'label': '属于',
            'description': f"{s['name']}属于{s['category_name']}"
        })

# 部类 -> 宗派
school_name2id = {s['name']:s['id'] for s in sects}
for code, cat in cat_map.items():
    school_name = cat.get('school')
    if not school_name or school_name not in school_name2id: continue
    relations.append({
        'id': f'r{len(relations)+1:03d}',
        'type': 'yijing',
        'source': f'cat_{code}',
        'target': school_name2id[school_name],
        'label': '为核心依据',
        'description': f"{cat['name']}是{school_name}的核心经典依据"
    })

# 同经异译
for group in parallels:
    sutra_ids = [s['id'] for s in group['sutras']]
    sutra_names = [s['title'] for s in group['sutras']]
    for i in range(len(sutra_ids)):
        for j in range(i+1, len(sutra_ids)):
            if sutra_ids[i] in sutra_node_ids and sutra_ids[j] in sutra_node_ids:
                relations.append({
                    'id': f'r{len(relations)+1:03d}',
                    'type': 'yiyi',
                    'source': sutra_ids[i],
                    'target': sutra_ids[j],
                    'label': '异译本',
                    'description': f"{group['title']}的不同译本"
                })

# 译师 -> 译出的经
translator_map = {}
for p in persons:
    if p['class'] in ['master', 'translator']:
        for alias in [p['name']] + p.get('alias', []):
            name_clean = alias.replace('法师','').replace('大师','').replace('三藏','').replace('尊者','').strip()
            translator_map[name_clean] = p['id']

for s in sutra_nodes:
    translator = s.get('translator', '')
    if not translator: continue
    translator_clean = translator.replace('三藏', '').replace('法师', '').replace('沙门', '').replace('译', '').replace('于阗国', '').strip()
    pid = translator_map.get(translator_clean)
    if pid:
        relations.append({
            'id': f'r{len(relations)+1:03d}',
            'type': 'yi_chu',
            'source': pid,
            'target': s['id'],
            'label': '译出',
            'description': f"译出{s['name']}"
        })

# 保存
with open('data/categories.json', 'w', encoding='utf-8') as f:
    json.dump(category_nodes, f, ensure_ascii=False, indent=2)
with open('data/sutras-full.json', 'w', encoding='utf-8') as f:
    json.dump(sutra_nodes, f, ensure_ascii=False, indent=2)
with open('data/relations.json', 'w', encoding='utf-8') as f:
    json.dump(relations, f, ensure_ascii=False, indent=2)

print("✅ 第一步：本体图谱数据扩充完成")
print(f"   部类节点：{len(category_nodes)}")
print(f"   核心经典节点：{len(sutra_nodes)}")
print(f"   总关系数：{len(relations)}")
