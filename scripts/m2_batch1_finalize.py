#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为第一批 30 个新增 concept（c222~c251，烦恼/智慧/诸法/生死/世界/大乘/修行/小乘/清净/佛法/菩提/禅定/净土/功德/世间/真理/成佛/声闻/弥陀/色界/三界/般若/无量/地狱/分别/金刚/教法/说法/一切法/道理）补全：
1. relations.json 关系
2. dict-links.json 词典映射
3. m2_index.json 索引条目
脚本幂等，重复执行不重复添加。
"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BATCH1 = ['c222','c223','c224','c225','c226','c227','c228','c229','c230','c231',
          'c232','c233','c234','c235','c236','c237','c238','c239','c240','c241',
          'c242','c243','c244','c245','c246','c247','c248','c249','c250','c251']

# 读取现有
with open('ontology/instances/relations.json','r',encoding='utf-8') as f:
    R = json.load(f)
with open('ontology/dict-links.json','r',encoding='utf-8') as f:
    DL = json.load(f)
with open('ontology/instances/m2_index.json','r',encoding='utf-8') as f:
    M2 = json.load(f)
with open('data/buddhist_dict.json','r',encoding='utf-8') as f:
    BD = json.load(f)
DICT = {t['name']: t for t in BD['terms']}

# 读取 30 个新 concept
new_concepts = {}
for cid in BATCH1:
    with open(f'ontology/instances/concepts/{cid}.json','r',encoding='utf-8') as f:
        new_concepts[cid] = json.load(f)

# 已存在的 concept name->id（用于关系目标解析）
existing_name_to_id = {}
import glob
for fp in glob.glob('ontology/instances/concepts/c*.json'):
    with open(fp,'r',encoding='utf-8') as f:
        c = json.load(f)
    existing_name_to_id[c['name']] = c['id']

# ===== 1. 追加 relations（去重）=====
existing_rel_keys = {(r['source'],r['target'],r['type']) for r in R['relations']}
new_rels = []

def add_rel(s, t, typ, desc):
    key = (s,t,typ)
    if key in existing_rel_keys: return
    if t not in existing_name_to_id.values() and not t.startswith(('c','p','s','sec','t')):
        # target 是词名，需转换
        if t in existing_name_to_id:
            t = existing_name_to_id[t]
        else:
            return  # 目标未实例化，跳过
    R['relations'].append({'source':s,'target':t,'type':typ,'description':desc})
    existing_rel_keys.add(key)
    new_rels.append((s,t,typ))

# 手动定义本批概念间及与已有概念的关系（基于佛学共识，不杜撰）
# 烦恼 c222
add_rel('c222','c232','opposite_to','烦恼与菩提为对待法，转烦恼即菩提')  # 烦恼-菩提
add_rel('c222','c225','cause_of','烦恼为因，招感生死之果')  # 烦恼-生死
add_rel('c222','c243','removed_by','般若智慧能断除烦恼')  # 烦恼-般若
# 菩提 c232
add_rel('c232','c222','opposite_to','烦恼与菩提为对待法')
add_rel('c232','c228','result_of','修行圆满成就菩提')
# 智慧 c223
add_rel('c223','c243','synonym_of','般若即智慧，六度之第六度')  # 智慧-般若
# 般若 c243
add_rel('c243','c223','synonym_of','般若译曰智慧，照见诸法实相')
# 生死 c225
add_rel('c225','c222','result_of','烦恼为因，生死为果')
# 世间 c236
add_rel('c236','c226','synonym_of','世间即世界，三世十方之合称')
# 世界 c226
add_rel('c226','c236','synonym_of','世界又名世间')
# 大乘 c227
add_rel('c227','c229','opposite_to','大乘利他，小乘自利，各有宗趣')  # 大乘-小乘
# 小乘 c229
add_rel('c229','c227','opposite_to','小乘自利，大乘利他')
add_rel('c229','c239','contains','小乘含声闻乘、缘觉乘')  # 小乘-声闻
# 声闻 c239
add_rel('c239','c229','belongs_to','声闻乘属小乘')
# 净土 c234
add_rel('c234','c240','residence_of','西方极乐净土为阿弥陀佛所居')  # 净土-弥陀
# 三界 c242
add_rel('c242','c241','contains','三界包含欲界、色界、无色界')  # 三界-色界
add_rel('c242','c245','contains','地狱位于欲界之中，为三界所摄')  # 三界-地狱
# 色界 c241
add_rel('c241','c242','part_of','色界为三界之一')
# 地狱 c245
add_rel('c245','c242','located_in','地狱位于三界内欲界之下')
# 诸法 c224
add_rel('c224','c250','synonym_of','诸法即一切法')
# 一切法 c250
add_rel('c250','c224','synonym_of','一切法即诸法')
# 禅定 c233
add_rel('c233','c243','cooperates_with','禅定与般若相资，定慧等持')
# 成佛 c238
add_rel('c238','c227','fruit_of','成佛为大乘菩萨道究竟果位')
# 分别 c246
add_rel('c246','c222','type_of','虚妄分别为根本烦恼之一')

# ===== 2. 追加 dict-links（去重）=====
exist_links = {(lk['dict_word'],lk['ontology_id']) for lk in DL['links']}
new_links = []
for cid, c in new_concepts.items():
    w = c['name']
    term = DICT.get(w,{})
    key = (w,cid)
    if key in exist_links: continue
    DL['links'].append({
        'dict_word': w,
        'dict_clean': None,
        'dict_category': term.get('category','名相术语'),
        'ontology_id': cid,
        'ontology_label': w,
        'ontology_type': 'concept',
        'match_method': 'exact',
        'match_via': 'name'
    })
    new_links.append(w)
    exist_links.add(key)

# ===== 3. 追加 m2_index.concepts（去重）=====
exist_idx_ids = {ci['id'] for ci in M2['concepts']}
new_idx = []
for cid, c in new_concepts.items():
    if cid in exist_idx_ids: continue
    M2['concepts'].append({
        'id': cid, 'name': c['name'], 'layer': c['layer'],
        'primary_sect': c['primary_sect'],
        'definition_short': c['definition'][:80]
    })
    new_idx.append(cid)

# 更新 meta
R['meta']['total'] = len(R['relations'])
R['summary']['total'] = len(R['relations'])
DL['summary']['matched_count'] = len(DL['links'])
M2['meta']['total_concepts'] = len(M2['concepts'])
M2['meta']['total_relations'] = len(R['relations'])
M2['meta']['version'] = '3.2.0-M2-batch1'

# 写回
with open('ontology/instances/relations.json','w',encoding='utf-8') as f:
    json.dump(R,f,ensure_ascii=False,indent=2)
with open('ontology/dict-links.json','w',encoding='utf-8') as f:
    json.dump(DL,f,ensure_ascii=False,indent=2)
with open('ontology/instances/m2_index.json','w',encoding='utf-8') as f:
    json.dump(M2,f,ensure_ascii=False,indent=2)

print(f'新增/确认 relations: {len(new_rels)} 条（总数 {len(R["relations"])}）')
print(f'新增 dict-links: {len(new_links)} 条（总数 {len(DL["links"])}）: {new_links}')
print(f'新增 m2_index 条目: {len(new_idx)} 条（total_concepts={M2["meta"]["total_concepts"]}）')
