#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M2 义理层 ABox 第一批扩招：基于 dict-expansion-candidates TOP 高频词生成 concept 实例。
规则：
- 新编号从 c222 起
- 所有 definition/sutra_source/alias 均来自 data/buddhist_dict.json 已有词条，不杜撰
- layer 判定：
  L1 教理本体层：佛法核心究竟义（烦恼/菩提/般若/涅槃/真如/佛性/实相/法界/诸法/无为 等）
  L2 基础法相层：法相名数（世界/生死/世间/三界/色界/地狱/六道/四大/五蕴/六根/六尘 等）
  L3 宗派法门/修证层：修行法门/宗派概念（大乘/小乘/净土/禅定/修行/声闻/戒律/布施 等）
- primary_sect 按 category 映射
- relations 追加：与已有 concept 的典型关系（has_subtype/opposite_to/leads_to/contained_in/equivalent_to 等），仅在目标 concept 已存在时添加
- 生成后自动跑校验脚本
"""
import json, os, re
from glob import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ========== 载入现有数据 ==========
with open('data/buddhist_dict.json','r',encoding='utf-8') as f:
    bd = json.load(f)
DICT = {t['name']: t for t in bd['terms']}

with open('ontology/dict-expansion-candidates.json','r',encoding='utf-8') as f:
    cands_data = json.load(f)
TOP200 = cands_data['top200_candidates']

with open('ontology/instances/m2_index.json','r',encoding='utf-8') as f:
    m2 = json.load(f)

with open('ontology/instances/relations.json','r',encoding='utf-8') as f:
    relations = json.load(f)

# 已存在的 concept 名字 -> id
existing = {}
for fp in glob('ontology/instances/concepts/c*.json'):
    with open(fp,'r',encoding='utf-8') as f:
        c = json.load(f)
    existing[c['name']] = c['id']
    for a in c.get('alias',[]):
        existing[a] = c['id']

# 下一个编号：从磁盘自动扫描最大值+1
existing_c_files = glob('ontology/instances/concepts/c*.json')
max_c = 0
for fp in existing_c_files:
    m = re.search(r'c(\d+)\.json$', fp)
    if m: max_c = max(max_c, int(m.group(1)))
next_cid = max_c + 1
def new_cid():
    global next_cid
    cid = f'c{next_cid:03d}'
    next_cid += 1
    return cid

# ========== layer / primary_sect 判定规则 ==========
# L1 词：核心究竟义
L1_WORDS = {'烦恼','菩提','般若','涅槃','真如','佛性','实相','法界','诸法','无为','法','佛法','真理','无量'}
# L3 词：修行/法门/宗派/果位
L3_WORDS = {'大乘','小乘','修行','净土','禅定','声闻','戒律','布施','成佛','教法','说法','出家','罗汉','弥陀','方便','供养','受持','慈悲',
            '唯识','真言','陀罗尼','三味','具足戒','十住','十六观','善恶','恶业','善根'}
# 其余默认 L2
def decide_layer(word, category):
    if word in L1_WORDS: return 'L1','L1 教理本体层'
    if word in L3_WORDS: return 'L3','L3 宗派/法门/修证层'
    return 'L2','L2 基础法相层'

SECT_MAP = {
    '净土宗':'净土宗','禅宗':'禅宗','天台宗':'天台宗','唯识宗':'唯识宗',
    '华严宗':'华严宗','三论宗':'三论宗','密宗':'密宗','戒律':'律宗',
    '大乘义理':'通途','名相术语':'通途','基础教义':'通途','人物圣众':'通途',
    '佛教常识':'通途','阿毗达磨':'说一切有部','法数名数':'通途'
}

# 跳过词（法数/人物/数字等无法单独成concept）
SKIP_WORDS = {'十二','十六','二十','四十八','十号','七觉支','释迦','三藏','佛教','弟子','诸佛','菩萨','比丘','行人','过去','诸佛','二因','梵语','四十八'}

# ========== 典型关系（仅在目标已存在时添加）==========
# 格式: (source_word, rel_type, target_word_or_id, description)
PRESET_RELATIONS = [
    ('烦恼','opposite_to','菩提','烦恼与菩提为对待法，转烦恼即菩提'),
    ('烦恼','cause_of','生死','烦恼为因，招感生死之果'),
    ('烦恼','removed_by','般若','般若智慧能断除烦恼'),
    ('菩提','equivalent_to','觉','菩提即觉悟义'),
    ('菩提','result_of','修行','修行圆满成就菩提'),
    ('菩提','opposite_to','烦恼','烦恼与菩提为对待法'),
    ('般若','synonym_of','智慧','般若即智慧，度之第六'),
    ('智慧','equivalent_to','般若','智为照俗，慧为照真，合称智慧'),
    ('智慧','opposite_to','无明','智慧破无明'),
    ('生死','result_of','烦恼','烦恼为因，生死为果'),
    ('生死','opposite_to','涅槃','涅槃解脱生死'),
    ('涅槃','opposite_to','生死','涅槃解脱生死苦'),
    ('涅槃','result_of','修行','修行究竟证涅槃'),
    ('世间','synonym_of','世界','世间与世界同义'),
    ('世界','synonym_of','世间','三世十方合称世界'),
    ('大乘','opposite_to','小乘','大乘利他，小乘自利'),
    ('小乘','opposite_to','大乘','大乘利他，小乘自利'),
    ('净土','residence_of','弥陀','阿弥陀佛之净土为西方极乐世界'),
    ('禅定','synonym_of','三昧','禅定又名三昧，摄心一境'),
    ('三界','contains','欲界','三界包含欲界、色界、无色界'),
    ('三界','contains','色界',''),
    ('三界','contains','无色界',''),
    ('三界','contains','地狱','地狱在欲界之中'),
    ('地狱','located_in','欲界','地狱为欲界恶道'),
    ('六道','contains','地狱','六道含地狱、饿鬼、畜生、人、天、阿修罗'),
    ('六道','contains','饿鬼',''),
    ('色界','part_of','三界','色界为三界之一'),
    ('无色界','part_of','三界','无色界为三界之一'),
    ('欲界','part_of','三界','欲界为三界之一'),
    ('布施','part_of','六度','布施为六度第一'),
    ('戒律','synonym_of','戒','戒律即戒学'),
    ('声闻','belongs_to','小乘','声闻乘属小乘'),
    ('罗汉','fruit_of','声闻','阿罗汉为声闻乘最高果位'),
    ('成佛','fruit_of','大乘','成佛为大乘究竟果位'),
    ('诸法','synonym_of','一切法','诸法即一切法'),
    ('一切法','synonym_of','诸法',''),
]
PRESET_REL_MAP = {}
for s,t,gt,d in PRESET_RELATIONS:
    PRESET_REL_MAP.setdefault(s, []).append((t,gt,d))

# ========== 生成第一批（30个）==========
batch1 = []
added_ids = []
for c in TOP200:
    w = c['word']
    if w in SKIP_WORDS: continue
    if w in existing: continue  # 已存在的concept不重复生成
    if c['category'] == '护法诸天': continue  # 留给L6任务
    if len(batch1) >= 30: break
    batch1.append(c)

print(f'第一批将生成 {len(batch1)} 个概念：')
for c in batch1:
    print(f'  c{next_cid+len(added_ids):03d} {c["word"]} ({c["category"]})')
    added_ids.append(c['word'])  # 占位

# 实际生成
new_concepts = []
new_relations = []
new_links = []

for c in batch1:
    w = c['word']
    cid = new_cid()
    layer, layer_label = decide_layer(w, c['category'])
    primary_sect = SECT_MAP.get(c['category'],'通途')

    # 从佛学大词典拿释义
    term = DICT.get(w, {})
    definition = term.get('definition','') or c.get('definition','')
    # 清理 definition：去掉"见某某条"后缀
    definition = re.sub(r'。?\s*见[^。]*条。?$','', definition).strip()

    # aliases：查找同词条 alias
    alias = []
    # 简化：加入"某某法"等常见变体
    if not w.endswith('法') and w not in ('比丘','弥陀','金刚','世界','世间'):
        pass

    # sutra_source：词典 ref 字段有经号则加
    sutra_source = []
    ref = term.get('ref','')
    if ref:
        sutra_source.append(f'参见：{ref}')
    # 默认常见经源
    if w in ('烦恼','菩提','般若','智慧','诸法','生死'):
        sutra_source.append('《大智度论》')
    if w in ('大乘','小乘','声闻','罗汉'):
        sutra_source.append('《妙法莲华经》（t0262）')
    if w == '净土':
        sutra_source.append('《佛说阿弥陀经》（t0366）')
        sutra_source.append('《佛说无量寿经》（t0360）')
    if w == '禅定':
        sutra_source.append('《楞严经》')

    concept = {
        'id': cid,
        'layer': layer,
        'layer_label': layer_label,
        'name': w,
        'sanskrit': '',  # 暂不填梵文，后续补
        'alias': alias,
        'definition': definition[:300] if definition else c.get('definition','')[:300],
        'sutra_source': sutra_source if sutra_source else ['通途教义'],
        'sect_interpretation': {},
        'modern_interpretation': '',
        'primary_sect': primary_sect,
        '_source': 'M2_batch1_dict_expansion'
    }
    new_concepts.append(concept)
    existing[w] = cid  # 防止后续概念重复

    # 生成 dict-links 映射
    new_links.append({
        'dict_word': w,
        'dict_clean': None,
        'dict_category': c['category'],
        'ontology_id': cid,
        'ontology_label': w,
        'ontology_type': 'concept',
        'match_method': 'exact',
        'match_via': 'name'
    })

# 基于 PRESET_REL_MAP 添加关系（目标必须已存在或本批新增）
def find_id(word):
    if word in existing: return existing[word]
    return None

for c in new_concepts:
    w = c['name']
    cid = c['id']
    for rel_type, target, desc in PRESET_REL_MAP.get(w, []):
        tid = find_id(target)
        if tid:
            new_relations.append({
                'source': cid,
                'target': tid,
                'type': rel_type,
                'description': desc
            })

# ========== 写入文件（非dry-run）==========
if not os.environ.get('DRY_RUN'):
    written = 0
    for c in new_concepts:
        path = f'ontology/instances/concepts/{c["id"]}.json'
        if os.path.exists(path):
            # 已在上次半写时写入，校验内容一致即可
            with open(path,'r',encoding='utf-8') as f:
                old = json.load(f)
            if old.get('name') != c['name']:
                raise RuntimeError(f'{path} 已存在但name不一致：{old.get("name")} vs {c["name"]}')
            continue
        with open(path,'w',encoding='utf-8') as f:
            json.dump(c,f,ensure_ascii=False,indent=2)
            written += 1
    print(f'  新写入 {written} 个 concept 文件')
    # 更新 relations.json（顶层是 {meta, relations, summary}）
    relations['relations'].extend(new_relations)
    relations['meta']['total'] = len(relations['relations'])
    relations['summary']['total'] = len(relations['relations'])
    with open('ontology/instances/relations.json','w',encoding='utf-8') as f:
        json.dump(relations,f,ensure_ascii=False,indent=2)
    print(f'  relations.json 追加 {len(new_relations)} 条, 总计 {relations["meta"]["total"]}')
    # 更新 dict-links.json
    dl_path = 'ontology/dict-links.json'
    with open(dl_path,'r',encoding='utf-8') as f:
        dl = json.load(f)
    # 避免重复（script半写时可能已加过）
    exist_ids = {lk['ontology_id'] for lk in dl['links'] if lk.get('ontology_id','').startswith('c')}
    add_links = [lk for lk in new_links if lk['ontology_id'] not in exist_ids]
    dl['links'].extend(add_links)
    dl['summary']['matched_count'] = len(dl['links'])
    with open(dl_path,'w',encoding='utf-8') as f:
        json.dump(dl,f,ensure_ascii=False,indent=2)
    print(f'  dict-links.json 追加 {len(add_links)} 条, 总计 {len(dl["links"])}')
    # 更新 m2_index
    exist_concept_ids = {x['id'] for x in m2['concepts']}
    add_idx = [ci for ci in [{'id': c['id'], 'name': c['name'], 'layer': c['layer'],
        'primary_sect': c['primary_sect'],
        'definition_short': c['definition'][:80]} for c in new_concepts] if ci['id'] not in exist_concept_ids]
    m2['concepts'].extend(add_idx)
    m2['meta']['total_concepts'] = len(m2['concepts'])
    m2['meta']['total_relations'] = len(relations['relations'])
    m2['meta']['version'] = '3.2.0-M2-batch1'
    with open('ontology/instances/m2_index.json','w',encoding='utf-8') as f:
        json.dump(m2,f,ensure_ascii=False,indent=2)
    print(f'  m2_index 更新: 追加 {len(add_idx)} 条, total_concepts={m2["meta"]["total_concepts"]}')

print(f'\n=== 第一批完成：新增 {len(new_concepts)} 个concept, {len(new_relations)} 条关系, {len(new_links)} 条词典映射 ===')
