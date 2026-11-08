#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 1: 佛学大词典 ↔ 本体实例名称归一匹配
输出: ontology/dict-links.json
"""
import json, re, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent

# === 1. 加载词典 ===
dict_path = ROOT / "data" / "buddhist_dict.json"
with open(dict_path, encoding='utf-8') as f:
    raw = json.load(f)
terms = raw.get('terms', raw if isinstance(raw, list) else [])
dict_entries = {e['name']: e for e in terms}
print(f"[词典] 共 {len(dict_entries)} 条")

# === 2. 加载本体实例（每文件 1 条） ===
inst_dir = ROOT / "ontology" / "instances"

def load_dir(d: Path, prefix=None):
    items = []
    for f in sorted(d.glob("*.json")):
        try:
            obj = json.load(open(f, encoding='utf-8'))
            if isinstance(obj, list):
                items.extend(obj)
            elif isinstance(obj, dict):
                if 'items' in obj:
                    items.extend(obj['items'])
                else:
                    items.append(obj)
        except Exception as e:
            print(f"  warn: {f.name}: {e}")
    if prefix:
        items = [x for x in items if str(x.get('id','')).startswith(prefix)]
    return items

concepts = load_dir(inst_dir / "concepts", 'c')
persons = load_dir(inst_dir / "persons", 'p')
sutras_meta = load_dir(inst_dir / "sutras", 's')
sects = load_dir(inst_dir / "sects", 'sec')

print(f"[本体] 概念 {len(concepts)} | 人物 {len(persons)} | 经典 {len(sutras_meta)} | 宗派 {len(sects)}")

# === 3. 名称归一化函数 ===
HONORIFICS = [
    '菩萨', '尊者', '阿罗汉', '罗汉', '如来', '世尊', '大师',
    '法师', '论师', '禅师', '律师', '上人', '和尚', '阇梨',
    '比丘', '比丘尼', '沙门', '居士', '天女', '天王', '大士', '善知识'
    # 注意：'佛'、'三藏' 不放入全局敬称——
    #  - '佛' 单字是概念词（佛法、佛性），剥离会误伤
    #  - '三藏' 是经律论总名（概念），仅"唐三藏/三藏法师"作人名敬称，
    #    已靠别名显式覆盖，不需全局剥离，否则"三藏"名相术语会错挂到玄奘
]

# 但别名中含"三藏法师"这类时，若词典词头是"三藏"这种纯概念词，应该拒绝归一匹配
# 在 match 的类型优先级里用 type_pref 已经做了；更保险：归一化如果导致只剩"三藏""佛"这类单字概念词，丢弃
FORBIDDEN_STRIPPED = {'三藏', '佛', '法', '经', '论', '律', '僧'}

def strip_honorifics(name: str) -> set:
    """返回所有可能的归一化名称集合"""
    candidates = {name}
    # 完整原名
    # 从后向前剥离敬称（最多剥两层，避免"佛佛"之类误剥）
    work = name
    for _ in range(2):
        changed = False
        for h in HONORIFICS:
            if work.endswith(h) and len(work) > len(h):
                stripped = work[:-len(h)]
                if len(stripped) >= 1:
                    candidates.add(stripped)
                    work = stripped
                    changed = True
        if not changed:
            break
    return candidates

def normal_forms(name: str) -> set:
    """生成所有可能的匹配形式"""
    forms = set()
    forms.add(name)
    forms |= strip_honorifics(name)
    return {f for f in forms if f and f not in FORBIDDEN_STRIPPED}

# === 4. 构建本体索引 ===
# 格式: normalized_name -> [(id, label_zh, type, match_type)]
ontology_index = defaultdict(list)

def register(name: str, inst_id: str, label_zh: str, itype: str, mtype: str):
    if not name or len(name) < 1:
        return
    for nf in normal_forms(name):
        ontology_index[nf].append((inst_id, label_zh, itype, mtype))
    # 同时把 id 也索引进去（方便反向查）

for c in concepts:
    cid = c['id']; cn = c.get('name', '')
    register(cn, cid, cn, 'concept', 'label')
    for a in c.get('alias', []) or []:
        register(a, cid, cn, 'concept', 'alias')

for p in persons:
    pid = p['id']; pn = p.get('name', '')
    register(pn, pid, pn, 'person', 'label')
    for a in p.get('alias', []) or []:
        register(a, pid, pn, 'person', 'alias')

for s in sutras_meta:
    sid = s['id']; sn = s.get('name', '') or s.get('title', '')
    register(sn, sid, sn, 'sutra', 'label')
    for a in (s.get('alias', []) or []) + (s.get('alt_titles', []) or []):
        register(a, sid, sn, 'sutra', 'alias')

for sec in sects:
    sid = sec['id']; sn = sec.get('name', '')
    register(sn, sid, sn, 'sect', 'label')
    for a in sec.get('alias', []) or []:
        register(a, sid, sn, 'sect', 'alias')

print(f"[本体索引] 归一化名称共 {len(ontology_index)} 种")

# === 5. 匹配：精确匹配 + 归一化匹配 ===
links = []  # {dict_word, dict_cat, ontology_id, ontology_label, ontology_type, match_method}
matched_count = defaultdict(int)
unmatched_by_cat = defaultdict(list)

# 特殊词典头清洗："（…）" 注释
paren_re = re.compile(r'（[^）]*）|\([^)]*\)')

for word, entry in dict_entries.items():
    cat = entry.get('category', '')
    # 清洗词头中的括号注释（如"佛（术语）"）
    clean_word = paren_re.sub('', word).strip()
    if not clean_word:
        clean_word = word

    candidates = ontology_index.get(clean_word, [])
    method = 'exact'

    # 对匹配不到的人名类，尝试剥离敬称
    if not candidates and ('人名' in cat or '人物' in cat or '圣众' in cat or '菩萨' in cat or '佛' in cat or '罗汉' in cat or '诸天' in cat):
        for nf in normal_forms(clean_word):
            if nf in ontology_index:
                candidates = ontology_index[nf]
                method = 'normalized'
                break

    if candidates:
        # 优先选同类型的匹配
        type_pref = {
            '名相术语': ['concept'],
            '基础教义': ['concept'],
            '修行法门': ['concept'],
            '名数': ['concept'],
            '果位称谓': ['concept', 'person'],
            '梵语音译': ['concept'],
            '因明术语': ['concept'],
            '戒律术语': ['concept'],
            '天台宗术语': ['concept'],
            '华严宗术语': ['concept'],
            '唯识宗术语': ['concept'],
            '禅宗术语': ['concept'],
            '净土宗术语': ['concept'],
            '三论宗术语': ['concept'],
            '密宗术语': ['concept'],
            '汉传宗派': ['sect'],
            '人物圣众': ['person'],
            '菩萨': ['person'],
            '阿罗汉': ['person'],
            '护法诸天': ['person'],
            '僧人': ['person'],
            '居士': ['person'],
            '经论典籍': ['sutra'],
            '佛教论典': ['sutra'],
            '佛教律典': ['sutra'],
            '佛教经典': ['sutra'],
            '汉地撰述': ['sutra'],
            '佛教史传': ['sutra'],
            '忏仪仪轨': ['sutra'],
        }
        pref_types = type_pref.get(cat, [])
        chosen = None
        # 找首选项
        for cand in candidates:
            if cand[2] in pref_types:
                chosen = cand; break
        if not chosen:
            chosen = candidates[0]
        oid, olabel, otype, mtype = chosen
        links.append({
            'dict_word': word,
            'dict_clean': clean_word if clean_word != word else None,
            'dict_category': cat,
            'ontology_id': oid,
            'ontology_label': olabel,
            'ontology_type': otype,
            'match_method': method,
            'match_via': mtype,
        })
        matched_count[otype] += 1
    else:
        unmatched_by_cat[cat].append(word)

# === 6. 输出 ===
out = {
    'summary': {
        'total_dict_entries': len(dict_entries),
        'total_matched': len(links),
        'matched_by_type': dict(matched_count),
        'match_rate_by_type': {k: f"{v}/{sum(1 for e in dict_entries.values() if e.get('category','')==k)}" for k,v in matched_count.items()},
    },
    'links': sorted(links, key=lambda x: (x['ontology_type'], x['ontology_id'])),
}

out_path = ROOT / "ontology" / "dict-links.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"\n[结果] 匹配成功 {len(links)}/{len(dict_entries)}")
for t, c in matched_count.items():
    print(f"  - {t}: {c}")
print(f"\n输出: {out_path}")

# 未匹配摘要
print("\n[未匹配按词典类别TOP 15]")
um_sorted = sorted(unmatched_by_cat.items(), key=lambda x: -len(x[1]))
for cat, words in um_sorted[:15]:
    print(f"  {cat}: {len(words)} 条未匹配（例: {words[:5]}）")
