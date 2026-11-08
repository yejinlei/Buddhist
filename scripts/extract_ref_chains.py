#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 2: 从词典「参见」链抽取别名/同义关系
- 别名：将同义词头回写到本体实例 alias 字段
- 同义关系：写入 ontology/instances/relations.json（r####）
- 经论简称/同经异名：直接补经论实例的 alias
- 不修改原实例，只生成补丁：ontology/dict-alias-patch.json
- 同义关系增量写：ontology/dict-synonym-relations.json（增量 r####）
"""
import json, re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent

# === 加载词典 ===
dict_raw = json.load(open(ROOT/'data'/'buddhist_dict.json', encoding='utf-8'))
terms = dict_raw['terms']
dict_entries = {e['name']: e for e in terms}

# === 加载本体 ===
inst_dir = ROOT / "ontology" / "instances"

def load_dir(d: Path, prefix=None):
    items = []
    for f in sorted(d.glob("*.json")):
        try:
            obj = json.load(open(f, encoding='utf-8'))
            if isinstance(obj, dict) and 'items' not in obj:
                items.append(obj)
            elif isinstance(obj, dict) and 'items' in obj:
                items.extend(obj['items'])
            elif isinstance(obj, list):
                items.extend(obj)
        except Exception as e:
            print(f"  warn: {f.name}: {e}")
    if prefix:
        items = [x for x in items if str(x.get('id','')).startswith(prefix)]
    return items

concepts = {c['id']: c for c in load_dir(inst_dir/'concepts', 'c')}
persons = {p['id']: p for p in load_dir(inst_dir/'persons', 'p')}
sutras = {s['id']: s for s in load_dir(inst_dir/'sutras', 's')}
sects = {sec['id']: sec for sec in load_dir(inst_dir/'sects', 'sec')}

all_instances = {}
all_instances.update(concepts); all_instances.update(persons); all_instances.update(sutras); all_instances.update(sects)
print(f"[总实例] {len(all_instances)}（概念{len(concepts)} 人物{len(persons)} 经论{len(sutras)} 宗派{len(sects)}）")

# === 加载 dict-links（已精确匹配的）===
dl = json.load(open(ROOT/'ontology'/'dict-links.json', encoding='utf-8'))
word_to_onto = {}  # dict_word -> ontology_id
for link in dl['links']:
    word_to_onto[link['dict_word']] = link['ontology_id']
print(f"[已匹配] {len(word_to_onto)} 词头")

# === 抽取所有「参见」条目 ===
refs = [t for t in terms if t.get('category') == '参见' or t.get('ref')]
print(f"[参见条目] {len(refs)}")

# === 参见指向解析：ref 字段可能是 "X" 或 "「X」"，清洗 ===
def parse_ref(ref_text: str):
    """提取真正的被参见词头"""
    if not ref_text:
        return None
    # 先摘 「」 内
    m = re.findall(r'[「「]([^」」]+)[」」]', ref_text)
    if m:
        return m[-1]  # 取最后一个
    # 再看 "见 X" "参见 X" 结构
    m2 = re.search(r'(?:参见|见|即|又作|亦称|亦名|又名|简称)[：:]?\s*([^\s，。；、]+)', ref_text)
    if m2:
        return m2.group(1)
    return ref_text.strip()

# === 建「词头 → 本体实例」的双向映射（含别名扩展）===
word_to_instance = {}
for oid, inst in all_instances.items():
    name = inst.get('name', '')
    if name:
        word_to_instance[name] = oid
    for a in (inst.get('alias') or []):
        word_to_instance[a] = oid

# === 新增别名收集 ===
alias_patch = defaultdict(set)   # oid -> set of new alias strings
synonym_pairs = set()            # (oid1, oid2) 对称去重

# 三轮遍历：第一轮直链→第二轮别名扩展→第三轮补间
def resolve(word):
    """在词典 + 本体里找 oid；若词头在 dict 但未入本体，返回 None 等后续收集"""
    if word in word_to_instance:
        return word_to_instance[word]
    if word in word_to_onto:
        return word_to_onto[word]
    return None

def add_alias(oid, alias_word):
    """给 oid 加别名（不能等于原名）"""
    inst = all_instances[oid]
    existing = set(inst.get('alias') or [])
    name = inst.get('name', '')
    if alias_word and alias_word != name and alias_word not in existing:
        alias_patch[oid].add(alias_word)
        word_to_instance[alias_word] = oid  # 即时扩展，供后续链式解析

round1 = 0; round2 = 0; round3 = 0
unresolved = []

# 第一轮：直接链接
for t in refs:
    src_word = t['name']
    tgt_word = parse_ref(t.get('ref', ''))
    if not tgt_word:
        continue
    src_oid = resolve(src_word)
    tgt_oid = resolve(tgt_word)

    # A. 双方都已在本体：加同义关系
    if src_oid and tgt_oid and src_oid != tgt_oid:
        pair = tuple(sorted([src_oid, tgt_oid]))
        if pair not in synonym_pairs:
            synonym_pairs.add(pair); round1 += 1
        # 互为别名
        src_name = all_instances[src_oid].get('name','')
        tgt_name = all_instances[tgt_oid].get('name','')
        if src_word != src_name and src_word != tgt_name:
            add_alias(tgt_oid, src_word)
        if tgt_word != tgt_name and tgt_word != src_name:
            add_alias(src_oid, tgt_word)
    # B. 只目标在本体：把源词作为目标的别名加入
    elif not src_oid and tgt_oid:
        add_alias(tgt_oid, src_word); round2 += 1
    # C. 都不在本体：入未决，第三轮再看
    else:
        unresolved.append((src_word, tgt_word))

# 第二轮：用第一轮新别名重解 unresolved
still_unresolved = []
for src_word, tgt_word in unresolved:
    src_oid = resolve(src_word)
    tgt_oid = resolve(tgt_word)
    if tgt_oid:
        add_alias(tgt_oid, src_word); round3 += 1
    elif src_oid:
        add_alias(src_oid, tgt_word); round3 += 1
    else:
        still_unresolved.append((src_word, tgt_word))

print(f"\n[别名补丁]")
print(f"  第一轮 双方已在本体: {round1} 对同义关系")
print(f"  第二轮 目标在本体、源词作为别名: {round2} 条")
print(f"  第三轮 经别名扩展后补回: {round3} 条")
print(f"  仍未解析（双方都不在本体）: {len(still_unresolved)}")

# === 类型统计 ===
type_count = defaultdict(int)
for oid in alias_patch:
    t = 'concept' if oid.startswith('c') else 'person' if oid.startswith('p') else 'sutra' if oid.startswith('s') else 'sect'
    type_count[t] += len(alias_patch[oid])
print(f"  新增别名总数: {sum(type_count.values())}")
for t, c in type_count.items():
    print(f"    {t}: +{c}")

# === 生成同义关系（接 r####，先看 relations.json 现有最大 id）===
rel_path = inst_dir / "relations.json"
existing_rels = []
max_rid = 0
if rel_path.exists():
    rel_raw = json.load(open(rel_path, encoding='utf-8'))
    if isinstance(rel_raw, dict) and 'relations' in rel_raw:
        existing_rels = rel_raw['relations']
    elif isinstance(rel_raw, list):
        existing_rels = rel_raw
    for r in existing_rels:
        m = re.match(r'r(\d+)', r.get('id',''))
        if m:
            max_rid = max(max_rid, int(m.group(1)))
print(f"\n[现有关系] {len(existing_rels)} 条，最大 rid=r{max_rid:04d}")

new_rels = []
for i, (a, b) in enumerate(sorted(synonym_pairs), start=1):
    rid = f"r{max_rid + i:04d}"
    a_n = all_instances[a].get('name', a)
    b_n = all_instances[b].get('name', b)
    new_rels.append({
        "id": rid,
        "type": "synonym",
        "type_label": "同义/异名",
        "source": a,
        "target": b,
        "label": "亦称/异名",
        "evidence_source": "佛学大词典参见链",
        "evidence": f"「{a_n}」参见「{b_n}」",
    })
print(f"[新增同义关系] {len(new_rels)} 条")

# === 示例：打印几个人物/概念的别名补全 ===
print("\n[别名补全示例]")
samples = ['p001', 'p002', 'p003', 'p307', 'p305', 'c001', 'c003', 's012', 's030']
for sid in samples:
    if sid in alias_patch:
        inst = all_instances[sid]
        print(f"  {sid} {inst.get('name','')}: +{sorted(alias_patch[sid])[:6]}{'...' if len(alias_patch[sid])>6 else ''}")

# === 输出补丁文件（不直接改实例，交给下一步 apply_patch 写回）===
patch = {
    "summary": {
        "total_new_alias": sum(type_count.values()),
        "alias_by_type": dict(type_count),
        "new_synonym_relations": len(new_rels),
        "unresolved_pairs": len(still_unresolved),
        "rounds": {"round1_synonym_pairs": round1, "round2_target_only": round2, "round3_after_expand": round3}
    },
    "alias_patch": {oid: sorted(aliases) for oid, aliases in alias_patch.items()},
    "new_relations": new_rels,
    "unresolved_pairs_sample": still_unresolved[:50],
}
out_path = ROOT/"ontology"/"dict-alias-patch.json"
json.dump(patch, open(out_path,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\n输出: {out_path}")
