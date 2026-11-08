#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 2b: apply alias patch 回写实例文件 + 追加同义关系到 relations.json
不修改原 dict 原文，只扩充实例的 alias 字段和 relations.json
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
inst_dir = ROOT/"ontology"/"instances"

patch = json.load(open(ROOT/"ontology"/"dict-alias-patch.json", encoding='utf-8'))
alias_patch = patch['alias_patch']
new_rels = patch['new_relations']

applied = 0; alias_added = 0
for oid, new_aliases in alias_patch.items():
    # 定位文件（注意 sec 要放在 s 之前，否则 sec001.startswith('s') 会误判为 sutras）
    if oid.startswith('sec'): f = inst_dir/"sects"/f"{oid}.json"
    elif oid.startswith('c'): f = inst_dir/"concepts"/f"{oid}.json"
    elif oid.startswith('p'): f = inst_dir/"persons"/f"{oid}.json"
    elif oid.startswith('s'): f = inst_dir/"sutras"/f"{oid}.json"
    else: continue
    d = json.load(open(f, encoding='utf-8'))
    existing = set(d.get('alias') or [])
    new_added_here = 0
    for a in new_aliases:
        if a and a != d.get('name','') and a not in existing:
            existing.add(a); new_added_here += 1
    if new_added_here > 0:
        d['alias'] = sorted(existing)
        d['dict_alias_sources'] = '佛学大词典参见链'
        json.dump(d, open(f,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
        applied += 1; alias_added += new_added_here

print(f"[回写实例] {applied} 个文件追加别名，共 +{alias_added} 个别名")

# 追加同义关系到 relations.json
rel_path = inst_dir/"relations.json"
rel_raw = json.load(open(rel_path, encoding='utf-8'))
if isinstance(rel_raw, dict):
    rel_list = rel_raw.setdefault('relations', [])
else:
    rel_list = rel_raw

# 去重：以 (source,target,type) 为 key
exist_set = {(r.get('source'), r.get('target'), r.get('type')) for r in rel_list}
exist_set |= {(r.get('target'), r.get('source'), r.get('type')) for r in rel_list}  # 对称
added_rel = 0
for r in new_rels:
    key = (r['source'], r['target'], r['type'])
    if key not in exist_set:
        rel_list.append(r); added_rel += 1; exist_set.add(key); exist_set.add((r['target'],r['source'],r['type']))

if isinstance(rel_raw, dict):
    rel_raw['relations'] = rel_list
    rel_raw['summary'] = rel_raw.get('summary', {})
    rel_raw['summary']['total'] = len(rel_list)
    json.dump(rel_raw, open(rel_path,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
else:
    json.dump(rel_list, open(rel_path,'w',encoding='utf-8'), ensure_ascii=False, indent=2)

print(f"[追加同义关系] +{added_rel} 条，总 {len(rel_list)} 条")
print(f"\n[新增的 6 对同义关系示例]")
for r in new_rels:
    print(f"  {r['source']} ↔ {r['target']}  （{r['evidence']}）")
