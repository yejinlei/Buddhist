#!/usr/bin/env python3
"""
构建 M5 段落级 RAG 切片（全藏段落→带元数据的 chunks）+ 修正反向索引到段落级。
产物：
  - ontology/paragraph_chunks.jsonl  全段逐行 JSONL（便于流式加载/向量化）
  - ontology/doctrine_section_index.json  （覆盖：段落级落点）
"""
import json, os, re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INST_DIR = os.path.join(ROOT, 'ontology/instances')
SHARD_MAP = os.path.join(INST_DIR, 'shard-map.json')

# 加载全局实体索引获取概念/人物名
gei = json.load(open(os.path.join(ROOT, 'ontology/global_entity_index.json'), encoding='utf-8'))
entities = gei['entities']

# 加载 shard map
sm = json.load(open(SHARD_MAP, encoding='utf-8'))
shards = sm['shards']

# 反向索引（段落级）
concept_index = defaultdict(lambda: {'concept_id':'', 'concept_name':'', 'hits':[]})
person_index = defaultdict(lambda: {'person_id':'', 'person_name':'', 'hits':[]})

chunks = []
chunk_id = 0
total_paras = 0
total_chars = 0
gatha_chunks = 0
mantra_chunks = 0
concept_hits = 0
person_hits = 0

# 预先加载所有 shard
loaded = {}
for shard_name in sorted(set(shards.values())):
    with open(os.path.join(INST_DIR, 'shards', f'{shard_name}.json'), encoding='utf-8') as f:
        loaded[shard_name] = json.load(f).get('instances', {})

for sutra_id, shard_name in shards.items():
    data = loaded[shard_name]
    if sutra_id not in data:
        continue
    t = data[sutra_id]
    sutra_name = t.get('title','') or t.get('title_zh','')
    translator = t.get('translator','')
    category = t.get('category','')
    vehicle = t.get('vehicle','')
    mode = t.get('mode','')

    # 章节 id→title 映射
    ch_id_to_title = {}
    ch_id_to_no = {}
    ch_id_to_part = {}
    for ch in t.get('chapters', []):
        ch_id_to_title[ch['id']] = ch.get('chapter_title','')
        ch_id_to_no[ch['id']] = ch.get('chapter_no', 0)
        ch_id_to_part[ch['id']] = ch.get('part_of_kepan','')

    # 偈/咒 id→text
    gatha_text = {}
    for g in t.get('gathas', []):
        gatha_text[g['id']] = g.get('text_preview','')
    mantra_text = {}
    for m in t.get('mantras', []):
        mantra_text[m['id']] = m.get('text_preview','')

    # 处理所有段落
    for para in t.get('paragraphs', []):
        pid = para.get('id','')
        ch_id = para.get('chapter_id','')
        text = para.get('text_preview','')
        if not text or len(text) < 2:
            continue
        total_paras += 1
        total_chars += len(text)
        ctype = 'paragraph'
        if para.get('gatha_id'):
            ctype = 'gatha'
            gatha_chunks += 1
            # 把偈文本补全
            full = gatha_text.get(para.get('gatha_id'), text)
            if len(full) > len(text):
                text = full
        if para.get('mantra_id'):
            ctype = 'mantra'
            mantra_chunks += 1
            full = mantra_text.get(para.get('mantra_id'), text)
            if len(full) > len(text):
                text = full

        chunk = {
            'chunk_id': f'chunk_{chunk_id:08d}',
            'sutra_id': sutra_id,
            'sutra_name': sutra_name,
            'translator': translator,
            'category': category,
            'vehicle': vehicle,
            'mode': mode,
            'chapter_id': ch_id,
            'chapter_title': ch_id_to_title.get(ch_id,''),
            'chapter_no': ch_id_to_no.get(ch_id,0),
            'part_of_kepan': ch_id_to_part.get(ch_id,''),
            'para_no': para.get('para_no',0),
            'para_id': pid,
            'chunk_type': ctype,
            'text': text,
            'char_count': len(text),
            'figures': para.get('figures', []),
            'doctrines': para.get('doctrines', [])
        }
        chunks.append(chunk)
        chunk_id += 1

        # 反向索引
        for cid in para.get('doctrines', []):
            if cid in entities:
                concept_index[cid]['concept_id'] = cid
                concept_index[cid]['concept_name'] = entities[cid]['name']
                concept_index[cid]['hits'].append({
                    'chunk_id': chunk['chunk_id'],
                    'sutra_id': sutra_id,
                    'sutra_name': sutra_name,
                    'chapter_title': chunk['chapter_title'],
                    'para_no': para.get('para_no',0),
                    'snippet': text[:100],
                    'type': ctype
                })
                concept_hits += 1
        for fid in para.get('figures', []):
            if fid in entities:
                person_index[fid]['person_id'] = fid
                person_index[fid]['person_name'] = entities[fid]['name']
                person_index[fid]['hits'].append({
                    'chunk_id': chunk['chunk_id'],
                    'sutra_id': sutra_id,
                    'sutra_name': sutra_name,
                    'chapter_title': chunk['chapter_title'],
                    'para_no': para.get('para_no',0),
                    'snippet': text[:100],
                    'type': ctype
                })
                person_hits += 1

# 去重、截断
def dedup_hits(idx, key):
    concepts_with_hits = 0
    for cid, info in idx.items():
        seen = set()
        uniq = []
        for h in info['hits']:
            k = (h['sutra_id'], h.get('para_no',0))
            if k not in seen:
                seen.add(k)
                uniq.append(h)
        info['hits'] = uniq[:200]
        info['total_hits'] = len(uniq)
        info['sutra_count'] = len(set(h['sutra_id'] for h in uniq))
        if uniq:
            concepts_with_hits += 1
    return concepts_with_hits

concepts_with_hits = dedup_hits(concept_index, 'concept')
persons_with_hits = dedup_hits(person_index, 'person')

# 保存段落切片 JSONL
chunks_path = os.path.join(ROOT, 'ontology/paragraph_chunks.jsonl')
with open(chunks_path, 'w', encoding='utf-8') as f:
    for c in chunks:
        f.write(json.dumps(c, ensure_ascii=False) + '\n')

# 保存反向索引
doctrine_index_path = os.path.join(ROOT, 'ontology/doctrine_section_index.json')
with open(doctrine_index_path, 'w', encoding='utf-8') as f:
    json.dump({
        'meta': {
            'version': '2.0.0',
            'granularity': 'paragraph',
            'total_concepts': len(concept_index),
            'concepts_with_hits': concepts_with_hits,
            'total_hits': concept_hits,
            'description': 'M2 义理概念→段落反向索引（段落级），RAG 问答精准段落召回用'
        },
        'concepts': dict(concept_index)
    }, f, ensure_ascii=False, indent=2)

person_index_path = os.path.join(ROOT, 'ontology/person_section_index.json')
with open(person_index_path, 'w', encoding='utf-8') as f:
    json.dump({
        'meta': {
            'version': '1.0.0',
            'granularity': 'paragraph',
            'total_persons': len(person_index),
            'persons_with_hits': persons_with_hits,
            'total_hits': person_hits,
            'description': '人物→段落反向索引（段落级），RAG 按人物检索经文用'
        },
        'persons': dict(person_index)
    }, f, ensure_ascii=False, indent=2)

# 段落检索的统计索引（按经分组，用于快速展示）
sutra_chunk_stats = {}
for c in chunks:
    sid = c['sutra_id']
    if sid not in sutra_chunk_stats:
        sutra_chunk_stats[sid] = {
            'sutra_id': sid, 'name': c['sutra_name'], 'translator': c['translator'],
            'category': c['category'], 'chunk_count': 0, 'char_count': 0,
            'gatha_count': 0, 'mantra_count': 0
        }
    s = sutra_chunk_stats[sid]
    s['chunk_count'] += 1
    s['char_count'] += c['char_count']
    if c['chunk_type'] == 'gatha': s['gatha_count'] += 1
    if c['chunk_type'] == 'mantra': s['mantra_count'] += 1

with open(os.path.join(ROOT, 'ontology/sutra_chunk_stats.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'meta': {
            'version':'1.0.0',
            'total_sutras': len(sutra_chunk_stats),
            'total_chunks': len(chunks),
            'total_chars': total_chars,
            'gatha_chunks': gatha_chunks,
            'mantra_chunks': mantra_chunks
        },
        'sutras': sutra_chunk_stats
    }, f, ensure_ascii=False, indent=2)

# 更新 ontology.yaml 登记
yaml_path = os.path.join(ROOT, 'ontology/ontology.yaml')
with open(yaml_path, encoding='utf-8') as f:
    ytxt = f.read()
new_entries = '''  - path: ontology/paragraph_chunks.jsonl
    entity: M5 段落级 RAG 切片（chunk）
    note: "全藏 78 万+段落，逐 chunk 带经号/章节/人物/概念元数据，向量检索/问答召回基础。"
  - path: ontology/doctrine_section_index.json
    entity: M5 概念→段落反向索引（段落级）
    note: "221 义理概念→全藏段落落点。"
  - path: ontology/person_section_index.json
    entity: M5 人物→段落反向索引（段落级）
    note: "人物→提及该人物的全藏段落。"
  - path: ontology/sutra_chunk_stats.json
    entity: M5 经文 chunk 统计
    note: "2506 部经的 chunk/字数/偈/咒统计。"
'''
if 'paragraph_chunks.jsonl' not in ytxt:
    marker = '  - path: ontology/global_entity_index.json'
    # 先移除旧的 doctrine_section_index 行
    ytxt = re.sub(r'  - path: ontology/doctrine_section_index\.json[\s\S]*?召回用。"\n', '', ytxt)
    ytxt = ytxt.replace(marker, new_entries + marker)
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(ytxt)

import re
print(f'✅ 段落切片: {len(chunks)} chunks, {total_chars:,} 字符')
print(f'   - 含偈 {gatha_chunks} 段、含咒 {mantra_chunks} 段')
print(f'   - 覆盖经文: {len(sutra_chunk_stats)} 部')
print(f'✅ 概念→段落反向索引: {concepts_with_hits}/{len(concept_index)} 概念有落点, {concept_hits} 条命中')
print(f'✅ 人物→段落反向索引: {persons_with_hits}/{len(person_index)} 人物有落点, {person_hits} 条命中')
