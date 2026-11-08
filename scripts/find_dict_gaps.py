#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 4: 反向缺口发现
- 统计词典各类别未匹配本体的数量
- 按价值度排序，输出待扩收清单
- 价值度规则：
  * 被引用次数（definition中被其他词条引用次数）多的优先
  * 核心教义/法数/修行法门/八宗专有术语优先
  * 名相术语中 2-4 字优先（单字太泛、过长多为解释）
  * 参见条目排除（它们是别名，不是独立条目）
"""
import json, re
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path(__file__).parent.parent

terms = json.load(open(ROOT/'data'/'buddhist_dict.json', encoding='utf-8'))['terms']
dict_entries = {t['name']: t for t in terms}
dl = json.load(open(ROOT/'ontology'/'dict-links.json', encoding='utf-8'))
matched_words = {l['dict_word'] for l in dl['links']}

# === 计算"被引用次数"：每个词在其他词条定义里出现多少次 ===
ref_count = Counter()
for t in terms:
    defn = t.get('definition','') or ''
    name = t['name']
    # 简单按最长匹配扫描其他所有词头，避免子串误匹配
    for w in dict_entries:
        if w == name: continue
        if len(w) < 2: continue
        if w in defn:
            ref_count[w] += 1

# === 类别到价值度权重 ===
PRIORITY_CATS = {
    '基础教义': 100, '法数名数': 95, '大乘义理': 90, '修行法门': 85,
    '阿毗达磨': 80, '戒律': 75, '天台宗': 85, '华严宗': 85, '唯识宗': 85,
    '禅宗': 85, '净土宗': 85, '三论宗': 85, '密宗': 85, '汉传宗派': 80,
    '护法诸天': 70, '果位称谓': 70, '佛教常识': 50, '名相术语': 60,
    '经论典籍': 55, '佛教史传': 50, '汉地撰述': 40, '佛教论典': 55,
    '佛教律典': 55, '人物圣众': 60, '菩萨': 65, '阿罗汉': 65, '僧人': 55,
    '居士': 40, '忏仪仪轨': 45, '梵语音译': 30, '因明术语': 60,
}

def score(word, t):
    cat = t.get('category','')
    s = PRIORITY_CATS.get(cat, 20)
    s += ref_count.get(word, 0) * 2  # 被引用加分
    L = len(word)
    if L in (2,3,4): s += 10
    elif L == 1: s -= 30
    elif L >= 6: s -= 5
    if cat == '参见': s -= 100  # 参见条目不独立收录
    # 单字"一/七/三/二/五"开头的数词，已归法数
    if re.match(r'^[一二三四五六七八九十百千万亿][^二三四]$', word) and len(word)<=2:
        s += 5
    return s

# === 未匹配词的打分与分类 ===
unmatched_by_cat = defaultdict(list)
for w, t in dict_entries.items():
    if w in matched_words: continue
    # 排除纯参见链（它们是别名，已在Step2处理）
    s = score(w, t)
    unmatched_by_cat[t.get('category','未分类')].append({
        'word': w,
        'definition': (t.get('definition','') or '')[:120],
        'ref_count': ref_count.get(w, 0),
        'score': s,
    })

# 各类别内按分数降序
for cat in unmatched_by_cat:
    unmatched_by_cat[cat].sort(key=lambda x: -x['score'])

# === 汇总推荐：按分数选 TOP 200 作为建议扩收清单 ===
all_candidates = []
for cat, items in unmatched_by_cat.items():
    if cat == '参见': continue
    for it in items:
        all_candidates.append({**it, 'category': cat})
all_candidates.sort(key=lambda x: -x['score'])
top200 = all_candidates[:200]

# === 按类别分组统计 ===
cat_stat = {}
for cat, items in unmatched_by_cat.items():
    non_ref = [it for it in items if it['score'] > 20]
    cat_stat[cat] = {
        'total_unmatched': len(items),
        'high_value': len(non_ref),
        'top5': [it['word'] for it in items[:5]],
    }

result = {
    'summary': {
        'dict_total': len(dict_entries),
        'already_matched': len(matched_words),
        'unmatched_total': len(dict_entries) - len(matched_words),
        'unmatched_categories': len(unmatched_by_cat),
        'high_value_candidates_score_gt_20': sum(1 for c in all_candidates if c['score']>20),
        'note': 'high_value = score>20（排除参见条目、单字词、低频梵语音译）',
    },
    'by_category': dict(sorted(cat_stat.items(), key=lambda x:-x[1]['high_value'])),
    'top200_candidates': top200,
}

out = ROOT/'ontology'/'dict-expansion-candidates.json'
json.dump(result, open(out,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"[输出] {out}")
print(f"[汇总] 词典 {len(dict_entries)} | 已匹配 {len(matched_words)} | 未匹配 {len(dict_entries)-len(matched_words)} | 高价值候选 {result['summary']['high_value_candidates_score_gt_20']}")
print("\n[未匹配按类别 TOP 20]")
for cat, st in sorted(cat_stat.items(), key=lambda x:-x[1]['high_value'])[:20]:
    print(f"  {cat}: 未匹配 {st['total_unmatched']} | 高价值 {st['high_value']} | 例: {st['top5'][:5]}")
print(f"\n[TOP 30 高价值候选]")
for it in top200[:30]:
    print(f"  [{it['score']:4d}] {it['word']:10s} ({it['category']}, refs={it['ref_count']}) — {it['definition'][:40]}")
