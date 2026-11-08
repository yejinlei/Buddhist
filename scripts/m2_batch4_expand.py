#!/usr/bin/env python3
"""M2 第4批概念扩充 c312-c341"""
import os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONCEPTS_DIR = os.path.join(ROOT, 'ontology/instances/concepts')
RELATIONS_FILE = os.path.join(ROOT, 'ontology/instances/relations.json')
DICT_FILE = os.path.join(ROOT, 'data/buddhist_dict.json')
M2_INDEX_FILE = os.path.join(ROOT, 'ontology/instances/m2_index.json')

with open(DICT_FILE, 'r', encoding='utf-8') as f:
    dict_data = json.load(f)
dict_terms = {item['name']: item for item in dict_data['terms']}

# 已有concept id
existing_ids = set()
for fname in os.listdir(CONCEPTS_DIR):
    if fname.startswith('c') and fname.endswith('.json'):
        existing_ids.add(fname.replace('.json', ''))
next_cid_num = max(int(cid[1:]) for cid in existing_ids) + 1

# 加载现有relations
with open(RELATIONS_FILE, 'r', encoding='utf-8') as f:
    rel_data = json.load(f)
relations = rel_data.get('relations', [])
existing_rel_keys = set((r['source'], r['target'], r['type']) for r in relations)

# 加载m2_index
with open(M2_INDEX_FILE, 'r', encoding='utf-8') as f:
    m2_index = json.load(f)
dict_links = m2_index.get('dict_links', [])
existing_dict_links = {l['dict_entry'] for l in dict_links}

# 第4批概念
batch4 = [
    ('三身', 'c019', 'has_part', '佛之法、报、应三身'),
    ('报身', 'c312', 'subClassOf', '佛三身之一'),
    ('性空', 'c052', 'related_to', '缘起性空核心义理'),
    ('涅槃寂静', 'c228', 'related_to', '三法印之一'),
    ('律宗', 'c031', 'subClassOf', '汉传八宗之一'),
    ('天台宗', 'c031', 'subClassOf', '汉传八宗之一，法华宗'),
    ('华严宗', 'c031', 'subClassOf', '汉传八宗之一，贤首宗'),
    ('三论宗', 'c031', 'subClassOf', '汉传八宗之一，空宗'),
    ('一真法界', 'c052', 'related_to', '华严宗核心概念'),
    ('话头', 'c264', 'practiced_by', '禅宗参究方法'),
    ('念佛三昧', 'c021', 'subClassOf', '三昧之一，净业核心'),
    ('十善业', 'c028', 'subClassOf', '善业之一'),
    ('三聚净戒', 'c073', 'subClassOf', '菩萨戒三大类'),
    ('俗谛', 'c052', 'related_to', '二谛之一'),
    ('真谛', 'c052', 'related_to', '二谛之一，胜义谛'),
    ('忍辱', 'c044', 'subClassOf', '六度之一'),
    ('七觉支', 'c294', 'part_of', '三十七道品之一'),
    ('五根', 'c294', 'part_of', '三十七道品之一'),
    ('五力', 'c294', 'part_of', '三十七道品之一'),
    ('五逆', 'c028', 'subClassOf', '重罪之一'),
    ('十恶', 'c028', 'subClassOf', '恶业之一'),
    ('八苦', 'c233', 'related_to', '苦谛之八相'),
    ('贪嗔痴', 'c222', 'subClassOf', '三毒根本烦恼'),
    ('圆融三谛', 'c316', 'core_of', '天台宗核心义理'),
    ('四禅八定', 'c021', 'subClassOf', '世间禅定'),
    ('一实相印', 'c052', 'related_to', '大乘一法印'),
    ('水陆法会', 'c085', 'part_of', '佛教法会仪轨'),
    ('焰口', 'c085', 'part_of', '施食仪轨'),
    ('八关斋戒', 'c073', 'subClassOf', '在家戒法'),
    ('盂兰盆会', 'c085', 'part_of', '孝亲超度法会'),
]

created = []
for name, parent_cid, rel_type, rel_desc in batch4:
    if name not in dict_terms:
        print(f'跳过 {name}：词典无释义')
        continue
    item = dict_terms[name]
    cid = f'c{next_cid_num:03d}'
    
    concept = {
        'id': cid,
        'layer': 'L2',
        'layer_label': '义理层',
        'name': name,
        'sanskrit': '',
        'alias': [],
        'definition': item['definition'][:300],
        'sutra_source': [f'《{n}》' for n in item.get('source', '').replace('佛学常见辞汇(陈义孝编)', '佛学常见辞汇').split('、') if n and not n.startswith('http')][:3],
        'sect_interpretation': {},
        'modern_interpretation': '',
        'primary_sect': ''
    }
    
    # 根据名称补宗派归属
    if name in ['天台宗', '圆融三谛', '一心三观', '五时八教']:
        concept['primary_sect'] = 'sec002'
        concept['sect_interpretation'] = {'天台宗': '依《法华经》立教，主张三谛圆融、一心三观'}
    elif name in ['华严宗', '一真法界', '法界缘起', '六相圆融', '十玄门']:
        concept['primary_sect'] = 'sec003'
        concept['sect_interpretation'] = {'华严宗': '依《华严经》立教，主张法界缘起、圆融无碍'}
    elif name in ['三论宗']:
        concept['primary_sect'] = 'sec001'
        concept['sect_interpretation'] = {'三论宗': '依《中论》《百论》《十二门论》立宗，阐扬性空中道'}
    elif name in ['律宗']:
        concept['primary_sect'] = 'sec004'
        concept['sect_interpretation'] = {'律宗': '依《四分律》立宗，南山道宣开创，重戒律持守'}
    elif name in ['念佛三昧', '三辈往生', '九品往生']:
        concept['primary_sect'] = 'sec007'
    
    with open(os.path.join(CONCEPTS_DIR, f'{cid}.json'), 'w', encoding='utf-8') as f:
        json.dump(concept, f, ensure_ascii=False, indent=2)
    
    # 加关系
    rel_key = (cid, parent_cid, rel_type)
    if rel_key not in existing_rel_keys and parent_cid != cid:
        relations.append({
            'source': cid,
            'target': parent_cid,
            'type': rel_type,
            'description': rel_desc
        })
        existing_rel_keys.add(rel_key)
    
    # 三身特殊关系
    if name == '三身':
        for sub in ['c267', 'c313']:  # 化身、报身
            rk = (cid, sub, 'has_part')
            if rk not in existing_rel_keys:
                relations.append({'source': cid, 'target': sub, 'type': 'has_part', 'description': '三身之一'})
                existing_rel_keys.add(rk)
    if name == '报身':
        # 关联法身 c081
        rk = (cid, 'c081', 'related_to')
        if rk not in existing_rel_keys:
            relations.append({'source': cid, 'target': 'c081', 'type': 'related_to', 'description': '报身依法身显现'})
            existing_rel_keys.add(rk)
    
    # dict link
    if name not in existing_dict_links:
        dict_links.append({'type': 'concept', 'id': cid, 'dict_entry': name})
        existing_dict_links.add(name)
    
    created.append(cid)
    next_cid_num += 1

# 保存relations
rel_data['relations'] = relations
rel_data['summary']['total_relations'] = len(relations)
with open(RELATIONS_FILE, 'w', encoding='utf-8') as f:
    json.dump(rel_data, f, ensure_ascii=False, indent=2)

# 保存m2_index
if 'dict_links' not in m2_index:
    m2_index['dict_links'] = []
m2_index['dict_links'] = list({(l['type'], l['id'], l['dict_entry']): l for l in m2_index['dict_links']}.values())
if 'meta' in m2_index:
    m2_index['meta']['total_dict_links'] = len(m2_index['dict_links'])
else:
    m2_index['meta'] = {'total_dict_links': len(m2_index['dict_links'])}
with open(M2_INDEX_FILE, 'w', encoding='utf-8') as f:
    json.dump(m2_index, f, ensure_ascii=False, indent=2)

print(f'第4批创建成功 {len(created)} 个概念: {created[0]}-{created[-1]}')
print(f'当前总relations: {len(relations)}, dict_links: {len(dict_links)}')
