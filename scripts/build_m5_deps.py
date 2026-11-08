#!/usr/bin/env python3
"""
构建 M5 应用层依赖数据（全局实体索引 + 反向索引 + 关键词 + 实体字典）
产物：
  - ontology/global_entity_index.json  全局实体 ID 索引（type/id/name/aliases/shard）
  - ontology/entity_aliases.json       实体别名字典（别名 → 规范 id，用于 NER 与检索）
  - ontology/doctrine_section_index.json  义理概念→经段反向索引（M2 全量 221 概念）
  - ontology/sutra_keywords.json       2506 部经关键词向量（人工+自动提取，RAG 召回用）
"""
import json, os, re, glob
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INST_DIR = os.path.join(ROOT, 'ontology/instances')
M2_CONC_DIR = os.path.join(INST_DIR, 'concepts')
M2_PERS_DIR = os.path.join(INST_DIR, 'persons')
M2_SUTRA_DIR = os.path.join(INST_DIR, 'sutras')
M2_SECT_DIR = os.path.join(INST_DIR, 'sects')
SHARD_MAP = os.path.join(INST_DIR, 'shard-map.json')
EVENTS = os.path.join(INST_DIR, 'events.json')
DHARMA = os.path.join(ROOT, 'ontology/dharma_assemblies.json')
PARALLEL = os.path.join(ROOT, 'ontology/parallel_translations.json')
INSTANCE_LINKS = os.path.join(ROOT, 'ontology/instance-links.json')

print("=== 开始构建 M5 依赖数据 ===")

# ============ 1. 读取所有 M2 实例 ============
entities = {}  # id -> {type,name,aliases,layer,...}

def add_entity(eid, etype, name, aliases=None, **kw):
    entities[eid] = {
        'id': eid, 'type': etype, 'name': name,
        'aliases': aliases or [],
        **kw
    }

# 1.1 M2 概念
concept_count = 0
for fp in glob.glob(os.path.join(M2_CONC_DIR, 'c*.json')):
    with open(fp, encoding='utf-8') as f:
        d = json.load(f)
    cid = d['id']
    name = d.get('name', '')
    aliases = d.get('aliases', [])
    if 'sanskrit' in d and d['sanskrit']:
        aliases.append(d['sanskrit'])
    add_entity(cid, 'concept', name, aliases, layer=d.get('layer', ''),
               definition=d.get('definition','')[:80])
    concept_count += 1
print(f'  M2 概念: {concept_count}')

# 1.2 M2 人物
person_count = 0
for fp in glob.glob(os.path.join(M2_PERS_DIR, 'p*.json')):
    with open(fp, encoding='utf-8') as f:
        d = json.load(f)
    pid = d['id']
    name = d.get('name', '')
    aliases = d.get('aliases', [])
    if 'sanskrit' in d and d['sanskrit']:
        aliases.append(d['sanskrit'])
    subtype = d.get('subtype','')
    add_entity(pid, 'person', name, aliases, subtype=subtype,
               era=d.get('era',''), description=d.get('description','')[:80])
    person_count += 1
print(f'  M2 人物: {person_count}')

# 1.3 M2 核心经典（义理层元数据 s###）
sutra_meta_count = 0
for fp in glob.glob(os.path.join(M2_SUTRA_DIR, 's*.json')):
    with open(fp, encoding='utf-8') as f:
        d = json.load(f)
    sid = d['id']
    name = d.get('name', '')
    aliases = d.get('aliases', [])
    taisho = d.get('taisho_id','')
    add_entity(sid, 'sutra_meta', name, aliases, taisho_id=taisho,
               category=d.get('category',''))
    sutra_meta_count += 1
print(f'  M2 核心经典元数据: {sutra_meta_count}')

# 1.4 M2 宗派
sect_count = 0
for fp in glob.glob(os.path.join(M2_SECT_DIR, 'sec*.json')):
    with open(fp, encoding='utf-8') as f:
        d = json.load(f)
    sid = d['id']
    name = d.get('name', '')
    aliases = d.get('aliases', [])
    add_entity(sid, 'sect', name, aliases,
               founder=d.get('founder',''), core_doctrine=d.get('core_doctrine','')[:60])
    sect_count += 1
print(f'  M2 宗派: {sect_count}')

# ============ 2. 全量经文实例 t#### ============
with open(SHARD_MAP, encoding='utf-8') as f:
    shard_map = json.load(f)
text_count = 0
loaded_shards = {}
id_to_shard = shard_map.get('shards', {})
shard_to_ids = defaultdict(list)
for eid, shard_name in id_to_shard.items():
    shard_to_ids[shard_name].append(eid)

for shard_name in sorted(shard_to_ids.keys()):
    shard_path = os.path.join(INST_DIR, 'shards', f'{shard_name}.json')
    with open(shard_path, encoding='utf-8') as f:
        shard_data = json.load(f)
    data = shard_data.get('instances', {})
    loaded_shards[shard_name] = data
    for tid in shard_to_ids[shard_name]:
        if tid not in data:
            continue
        tinfo = data[tid]
        name = tinfo.get('title','') or tinfo.get('title_zh','') or tinfo.get('name','')
        aliases = tinfo.get('aliases', [])
        add_entity(tid, 'sutra_text', name, aliases,
                   shard=f'{shard_name}.json',
                   taisho_id=tinfo.get('taisho',''),
                   category=tinfo.get('category',''),
                   translator=tinfo.get('translator',''),
                   char_count=tinfo.get('actual_char_count',0))
        text_count += 1
print(f'  全量经文实例: {text_count}')

# ============ 3. 事件实例 ============
with open(EVENTS, encoding='utf-8') as f:
    ev = json.load(f)
event_count = 0

# 3.1 法会
with open(DHARMA, encoding='utf-8') as f:
    dharma_data = json.load(f)
for k, item in dharma_data.get('assemblies', {}).items():
    eid = item.get('id', f'event:assembly:{k}')
    name = item.get('name', item.get('label_zh', k))
    aliases = item.get('aliases', [])
    add_entity(eid, 'dharma_assembly', name, aliases,
               location=item.get('place','') or item.get('location',''),
               sutra_count=len(item.get('related_sutras',[])))
    event_count += 1

# 3.2 结集（list）
for item in ev.get('councils', []):
    eid = item['id']
    name = item.get('label_zh','')
    aliases = item.get('aliases', [])
    add_entity(eid, 'council', name, aliases,
               time=item.get('time',''), location=item.get('place',''))
    event_count += 1

# 3.3 译经传法（list）
for item in ev.get('transmission_events', []):
    eid = item['id']
    name = item.get('label_zh','')
    aliases = item.get('aliases', [])
    add_entity(eid, 'transmission_event', name, aliases,
               subtype=item.get('subtype',''), era=item.get('era',''))
    event_count += 1

# 3.4 本生故事（list）
for item in ev.get('story_events', []):
    eid = item['id']
    name = item.get('label_zh', item.get('name',''))
    aliases = item.get('aliases', [])
    add_entity(eid, 'story_event', name, aliases,
               subtype=item.get('subtype',''))
    event_count += 1
print(f'  事件实例: {event_count}')

# ============ 4. 保存全局实体索引 ============
global_index = {
    'meta': {
        'version': '1.0.0',
        'description': 'M5 全局实体索引，统一全部实体 id/类型/别名/分片位置，RAG 检索/NER/跳转基础',
        'total': len(entities),
        'type_stats': {}
    },
    'entities': entities,
    'by_type': defaultdict(list)
}
type_stats = defaultdict(int)
for eid, e in entities.items():
    type_stats[e['type']] += 1
    global_index['by_type'][e['type']].append(eid)
global_index['meta']['type_stats'] = dict(type_stats)
global_index['by_type'] = dict(global_index['by_type'])

with open(os.path.join(ROOT, 'ontology/global_entity_index.json'), 'w', encoding='utf-8') as f:
    json.dump(global_index, f, ensure_ascii=False, indent=2)
print(f'\n✅ 全局实体索引已保存，共 {len(entities)} 个实体')
print(f'   类型分布: {dict(type_stats)}')

# ============ 5. 实体别名字典（别名→规范 id 映射） ============
alias_map = {}
for eid, e in entities.items():
    name = e['name']
    if name and len(name) >= 2:
        alias_map[name] = eid
    for a in e.get('aliases', []):
        if a and len(a) >= 2 and a not in alias_map:
            alias_map[a] = eid

with open(os.path.join(ROOT, 'ontology/entity_aliases.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'meta': {'version':'1.0.0', 'total': len(alias_map),
                 'description': '实体别名→规范 id 映射，用于 NER、检索消歧'},
        'aliases': alias_map
    }, f, ensure_ascii=False, indent=2)
print(f'✅ 实体别名字典已保存，共 {len(alias_map)} 个别名')

# ============ 6. 重建 M2 概念→经文段落反向索引（全量 221 概念） ============
# 先加载旧 instance-links 作基础
with open(INSTANCE_LINKS, encoding='utf-8') as f:
    old_links = json.load(f)
concept_section_index = defaultdict(lambda: {'concept_id':'', 'concept_name':'', 'hits':[]})
for cid, cinfo in old_links.get('concept', {}).items():
    concept_section_index[cid]['concept_id'] = cid
    concept_section_index[cid]['concept_name'] = cinfo.get('name','')
    for hit in cinfo.get('hits', [])[:1000]:
        concept_section_index[cid]['hits'].append(hit)

# 遍历所有经文的 doctrines/figures 标签（chapter 级），补充反向索引
for shard_name, data in loaded_shards.items():
    for tid, tinfo in data.items():
        sutra_name = tinfo.get('title','') or tinfo.get('title_zh','') or tinfo.get('name','')
        for ch in tinfo.get('chapters', []):
            ch_title = ch.get('chapter_title','')
            ch_doctrines = ch.get('doctrines', [])
            ch_figures = ch.get('figures', [])
            paragraphs = ch.get('paragraphs', [])
            para_idx_hits = {}
            for cid in ch_doctrines:
                if cid in entities:
                    # 取第一段作为 snippet
                    snippet = paragraphs[0][:80] if paragraphs else ''
                    concept_section_index[cid]['concept_id'] = cid
                    concept_section_index[cid]['concept_name'] = entities[cid]['name']
                    concept_section_index[cid]['hits'].append({
                        'sutra_id': tid,
                        'sutra_name': sutra_name,
                        'chapter_title': ch_title,
                        'section_no': ch.get('chapter_no', 0),
                        'snippet': snippet,
                        'level': 'chapter'
                    })
            # 偈/咒是顶层列表，仅通过 chapter_id 关联，没有独立 doctrines，用章节标签即可
            # 这里只补顶级 gathas/mantras 的 content 作为 snippet（基于 chapter_id 关联）
            ch_id = ch.get('id')

# 去重 & 统计
hit_total = 0
concepts_with_hits = 0
for cid, info in concept_section_index.items():
    seen = set()
    uniq = []
    for h in info['hits']:
        key = (h['sutra_id'], h.get('section_no',0), h.get('snippet','')[:30])
        if key not in seen:
            seen.add(key)
            uniq.append(h)
    info['hits'] = uniq[:200]  # 每概念最多保留 200 条
    info['total_hits'] = len(uniq)
    info['sutra_count'] = len(set(h['sutra_id'] for h in uniq))
    hit_total += len(uniq)
    if len(uniq) > 0:
        concepts_with_hits += 1

with open(os.path.join(ROOT, 'ontology/doctrine_section_index.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'meta': {
            'version': '1.0.0',
            'total_concepts': len(concept_section_index),
            'concepts_with_hits': concepts_with_hits,
            'total_hits': hit_total,
            'description': 'M2 义理概念→经文段落反向索引（全量），RAG 问答段落召回用'
        },
        'concepts': dict(concept_section_index)
    }, f, ensure_ascii=False, indent=2)
print(f'✅ 义理→经段反向索引已保存: {concepts_with_hits}/{len(concept_section_index)} 概念有落点，共 {hit_total} 条引文')

# ============ 7. 构建 2506 部经关键词向量 ============
# 从 core_content/keywords 字段提取；缺失的自动从章节标题+概念+人物标签统计
# 加载 buddhist_dict 高频词作补充
with open(os.path.join(ROOT, 'data/buddhist_dict.json'), encoding='utf-8') as f:
    bud_dict = json.load(f)
dict_terms = set(t['name'] for t in bud_dict.get('terms', []))
common_dharma_words = ['佛','菩萨','般若','空','涅槃','三昧','法','经','论','戒','慧','定',
                       '舍利弗','阿难','比丘','僧','如来','世尊','菩提','波罗蜜','阿罗汉',
                       '净土','禅','密','华严','法华','楞严','金刚','阿弥陀','药师','地藏',
                       '观','行','识','蕴','处','界','谛','缘起','中道','唯识']

sutra_kws = {}
for shard_name, data in loaded_shards.items():
    for tid, tinfo in data.items():
        kws = []
        # 显式关键词
        if tinfo.get('keywords'):
            if isinstance(tinfo['keywords'], list):
                kws.extend(tinfo['keywords'])
            else:
                kws.extend(re.split(r'[、,，;；\s]+', str(tinfo['keywords'])))
        # 核心教义
        if tinfo.get('core_doctrine'):
            kws.extend(re.split(r'[、,，;；\s]+', str(tinfo['core_doctrine']))[:5])
        # 部类
        if tinfo.get('category'):
            kws.append(tinfo['category'])
        if tinfo.get('vehicle'):
            kws.append(tinfo['vehicle'])
        if tinfo.get('mode'):
            kws.append(tinfo['mode'])
        # 经名分词
        name = tinfo.get('title','') or tinfo.get('title_zh','') or tinfo.get('name','')
        for w in common_dharma_words:
            if w in name and w not in kws:
                kws.append(w)
        # 从人物/概念标签提取
        tags = set()
        for ch in tinfo.get('chapters', []):
            for fid in ch.get('figures', []):
                if fid in entities and len(entities[fid]['name']) >= 2:
                    tags.add(entities[fid]['name'])
            for cid in ch.get('doctrines', []):
                if cid in entities:
                    tags.add(entities[cid]['name'])
        kws.extend(list(tags)[:15])
        # 去重、过滤空、限制长度
        seen = set()
        kws_clean = []
        for k in kws:
            k = k.strip()
            if 1 < len(k) < 20 and k not in seen:
                seen.add(k)
                kws_clean.append(k)
        sutra_kws[tid] = {
            'sutra_id': tid,
            'name': name,
            'category': tinfo.get('category',''),
            'translator': tinfo.get('translator',''),
            'char_count': tinfo.get('actual_char_count', 0),
            'keywords': kws_clean[:30]
        }
        sutra_kws[tid] = {
            'sutra_id': tid,
            'name': tinfo.get('name',''),
            'category': tinfo.get('category',''),
            'translator': tinfo.get('translator',''),
            'keywords': kws_clean[:30]
        }

with open(os.path.join(ROOT, 'ontology/sutra_keywords.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'meta': {
            'version': '1.0.0',
            'total': len(sutra_kws),
            'description': '2506 部经关键词向量，RAG 检索召回第一跳用'
        },
        'sutras': sutra_kws
    }, f, ensure_ascii=False, indent=2)
print(f'✅ 全经关键词向量已保存: {len(sutra_kws)} 部经')

# ============ 8. 更新本体主档 datasets ============
main_yaml_path = os.path.join(ROOT, 'ontology/ontology.yaml')
with open(main_yaml_path, encoding='utf-8') as f:
    yaml_txt = f.read()
new_entries = '''  - path: ontology/global_entity_index.json
    entity: M5 全局实体索引（全部实体统一入口）
    note: "统一 id 规范、类型、别名与分片位置，RAG/NER/跳转基础。"
  - path: ontology/entity_aliases.json
    entity: M5 实体别名字典
    note: "别名→规范 id 映射，用于检索消歧与 NER 识别。"
  - path: ontology/doctrine_section_index.json
    entity: M5 义理→段落反向索引（全量）
    note: "M2 221 概念到具体经文段落的落点，RAG 段落级召回用。"
  - path: ontology/sutra_keywords.json
    entity: M5 全经关键词向量
    note: "2506 部经关键词标签，RAG 第一跳检索召回用。"
'''
if 'global_entity_index.json' not in yaml_txt:
    # 在 datasets 最后一项后插入
    marker = '  - path: js/ontology-data.js'
    yaml_txt = yaml_txt.replace(marker, new_entries + '  - path: js/ontology-data.js')
    with open(main_yaml_path, 'w', encoding='utf-8') as f:
        f.write(yaml_txt)
    print('✅ ontology.yaml 已登记 M5 四个依赖文件')

print('\n=== M5 依赖数据全部构建完成 ===')
