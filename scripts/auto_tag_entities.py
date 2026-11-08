#!/usr/bin/env python3
"""
基于实体名/别名做精确字符串匹配，为 2506 部经段落补标 doctrines/figures。
规则：
  1. 仅匹配长度≥2 的中文实体名/别名（单字"法/心/行/道/佛/识/空"等全部跳过，避免误标）；
  2. 用最长优先匹配，避免"阿罗汉"被"罗汉"覆盖；
  3. 不写入原实例文件，直接在段落 chunks 上标，生成增强版反向索引。
产物：
  - ontology/paragraph_chunks_tagged.jsonl（带补全标签的 chunks）
  - 覆盖更新 doctrine_section_index.json / person_section_index.json
"""
import json, os, re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 加载全局实体
gei = json.load(open(os.path.join(ROOT, 'ontology/global_entity_index.json'), encoding='utf-8'))
entities = gei['entities']

# 过滤单字 & 过泛词
STOP_WORDS = {'法','心','行','道','佛','识','空','性','有','无','我','见','定','慧',
              '戒','经','论','义','理','德','智','悲','愿','因','果','缘','念','相',
              '真','俗','谛','乘','宗','教','僧','俗','圣','凡','善','恶','净','染',
              '修','证','悟','迷','觉','妄','烦恼','菩提'}  # 烦恼/菩提 2字但通用，由专门概念 c010/c009 处理时再放开

concept_terms = []  # (term, cid, len)
person_terms = []
for eid, e in entities.items():
    if e['type'] not in ('concept','person'):
        continue
    names = set()
    if e['name'] and len(e['name']) >= 2:
        names.add(e['name'])
    for a in e.get('aliases', []):
        if a and len(a) >= 2 and re.search(r'[\u4e00-\u9fff]', a):
            names.add(a)
    # 去停用词
    for n in list(names):
        if n in STOP_WORDS:
            names.discard(n)
    term_list = [(n, eid, len(n)) for n in names]
    if e['type'] == 'concept':
        concept_terms.extend(term_list)
    else:
        person_terms.extend(term_list)

# 按词长降序，保证长词优先
concept_terms.sort(key=lambda x: -x[2])
person_terms.sort(key=lambda x: -x[2])

print(f'概念匹配词: {len(concept_terms)} 条')
print(f'人物匹配词: {len(person_terms)} 条')
print(f'概念前10词: {[t[0] for t in concept_terms[:10]]}')
print(f'人物前10词: {[t[0] for t in person_terms[:10]]}')

# 读取原 chunks
chunks_in = os.path.join(ROOT, 'ontology/paragraph_chunks.jsonl')
chunks_out = os.path.join(ROOT, 'ontology/paragraph_chunks_tagged.jsonl')

# 构建统一正则：按词长降序，长词优先，用 named group 区分概念/人物
# 为性能，所有词一起匹配，一次 finditer 完成
all_terms = []  # (term, id, type, len)
for term, cid, l in concept_terms:
    all_terms.append((term, cid, 'c', l))
for term, pid, l in person_terms:
    all_terms.append((term, pid, 'p', l))
all_terms.sort(key=lambda x: -x[3])  # 长词优先

# 用 Aho-Corasick 思想：直接用一个大正则，所有词用 | 连接，长词在前
# 780k 段 × 数百词，用 re 应该能在几十秒跑完
term_pattern = re.compile('|'.join(re.escape(t[0]) for t in all_terms))
term_to_info = {t[0]: t for t in all_terms}

new_chunks = []
c_match_total = 0
p_match_total = 0
concept_hit_count = defaultdict(int)
person_hit_count = defaultdict(int)
concepts_hit = set()
persons_hit = set()

with open(chunks_in, encoding='utf-8') as f:
    for line in f:
        c = json.loads(line)
        text = c['text']
        existing_d = set(c.get('doctrines', []))
        existing_f = set(c.get('figures', []))

        matched_d = set()
        matched_p = set()
        used_spans = []
        for m in term_pattern.finditer(text):
            term = m.group(0)
            s, e = m.start(), m.end()
            # 不重叠
            if any(not (e <= us or s >= ue) for us, ue in used_spans):
                continue
            used_spans.append((s,e))
            _, tid, ttype, _ = term_to_info[term]
            if ttype == 'c' and tid not in existing_d:
                matched_d.add(tid)
                concept_hit_count[tid] += 1
            elif ttype == 'p' and tid not in existing_f:
                matched_p.add(tid)
                person_hit_count[tid] += 1

        c['doctrines'] = sorted(existing_d | matched_d)
        c['figures'] = sorted(existing_f | matched_p)
        c['auto_tagged_doctrines'] = sorted(matched_d)
        c['auto_tagged_figures'] = sorted(matched_p)
        new_chunks.append(c)
        c_match_total += len(matched_d)
        p_match_total += len(matched_p)
        concepts_hit.update(matched_d)
        persons_hit.update(matched_p)

# 写 tagged chunks
with open(chunks_out, 'w', encoding='utf-8') as f:
    for c in new_chunks:
        f.write(json.dumps(c, ensure_ascii=False) + '\n')

print(f'\n✅ 自动标引完成:')
print(f'   概念新增匹配: {c_match_total} 次, 覆盖 {len(concepts_hit)} 个新概念')
print(f'   人物新增匹配: {p_match_total} 次, 覆盖 {len(persons_hit)} 个新人物')

# 重建反向索引（用增强后标签）
concept_index = defaultdict(lambda: {'concept_id':'', 'concept_name':'', 'hits':[], 'auto_tagged_hits':0})
person_index = defaultdict(lambda: {'person_id':'', 'person_name':'', 'hits':[], 'auto_tagged_hits':0})

for c in new_chunks:
    for cid in c['doctrines']:
        if cid in entities:
            concept_index[cid]['concept_id'] = cid
            concept_index[cid]['concept_name'] = entities[cid]['name']
            is_auto = cid in c.get('auto_tagged_doctrines', [])
            concept_index[cid]['hits'].append({
                'chunk_id': c['chunk_id'],
                'sutra_id': c['sutra_id'],
                'sutra_name': c['sutra_name'],
                'chapter_title': c['chapter_title'],
                'para_no': c['para_no'],
                'snippet': c['text'][:100],
                'type': c['chunk_type'],
                'auto_tagged': is_auto
            })
            if is_auto: concept_index[cid]['auto_tagged_hits'] += 1
    for fid in c['figures']:
        if fid in entities:
            person_index[fid]['person_id'] = fid
            person_index[fid]['person_name'] = entities[fid]['name']
            is_auto = fid in c.get('auto_tagged_figures', [])
            person_index[fid]['hits'].append({
                'chunk_id': c['chunk_id'],
                'sutra_id': c['sutra_id'],
                'sutra_name': c['sutra_name'],
                'chapter_title': c['chapter_title'],
                'para_no': c['para_no'],
                'snippet': c['text'][:100],
                'type': c['chunk_type'],
                'auto_tagged': is_auto
            })
            if is_auto: person_index[fid]['auto_tagged_hits'] += 1

def trim_idx(idx):
    with_hits = 0
    for cid, info in idx.items():
        seen=set(); uniq=[]
        for h in info['hits']:
            k=(h['sutra_id'], h['para_no'])
            if k not in seen:
                seen.add(k); uniq.append(h)
        info['hits']=uniq[:200]
        info['total_hits']=len(uniq)
        info['sutra_count']=len(set(h['sutra_id'] for h in uniq))
        if uniq: with_hits += 1
    return with_hits

cwh = trim_idx(concept_index)
pwh = trim_idx(person_index)

with open(os.path.join(ROOT, 'ontology/doctrine_section_index.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'meta': {
            'version': '3.0.0',
            'granularity': 'paragraph',
            'total_concepts': len(concept_index),
            'concepts_with_hits': cwh,
            'auto_tagged_concepts': len(concepts_hit),
            'description': 'M2 义理概念→段落反向索引（段落级，含自动标引补全），RAG 段落召回用'
        },
        'concepts': dict(concept_index)
    }, f, ensure_ascii=False, indent=2)

with open(os.path.join(ROOT, 'ontology/person_section_index.json'), 'w', encoding='utf-8') as f:
    json.dump({
        'meta': {
            'version': '2.0.0',
            'granularity': 'paragraph',
            'total_persons': len(person_index),
            'persons_with_hits': pwh,
            'auto_tagged_persons': len(persons_hit),
            'description': '人物→段落反向索引（段落级，含自动标引补全），RAG 人物检索用'
        },
        'persons': dict(person_index)
    }, f, ensure_ascii=False, indent=2)

print(f'\n✅ 反向索引（含自动标引）:')
print(f'   概念: {cwh}/{len(concept_index)} 有落点')
print(f'   人物: {pwh}/{len(person_index)} 有落点')

# 展示最常被命中的 Top10 概念和人物
top_c = sorted(concept_hit_count.items(), key=lambda x:-x[1])[:10]
top_p = sorted(person_hit_count.items(), key=lambda x:-x[1])[:10]
print('\nTop10 自动匹配概念（新增命中）:')
for cid, n in top_c:
    print(f'  {entities[cid]["name"]} ({cid}): {n} 段')
print('Top10 自动匹配人物（新增命中）:')
for pid, n in top_p:
    print(f'  {entities[pid]["name"]} ({pid}): {n} 段')

# 零命中概念/人物
zero_c = [cid for cid in entities if entities[cid]['type']=='concept' and cid not in concept_index]
zero_p = [pid for pid in entities if entities[pid]['type']=='person' and pid not in person_index]
print(f'\n零命中概念: {len(zero_c)} 个')
print(f'零命中人物: {len(zero_p)} 个')
if zero_c[:10]:
    print('  概念示例:', [entities[c]['name'] for c in zero_c[:10]])
if zero_p[:10]:
    print('  人物示例:', [entities[p]['name'] for p in zero_p[:10]])
