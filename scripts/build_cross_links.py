#!/usr/bin/env python3
"""
构建跨页关联数据 (cross-links.json)
"""
import json, os, re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

print("=== 加载数据 ===")
kepan_data = load_json(os.path.join(ROOT, 'kepan/core.json'))
notes_data = load_json(os.path.join(ROOT, 'data/scholar-notes.json'))
dict_data = load_json(os.path.join(ROOT, 'data/buddhist_dict.json'))
dict_terms_list = dict_data.get('terms', [])
dict_terms = set()
term_meta = {}  # term -> {id, category, summary}
for t in dict_terms_list:
    title = t.get('name','') or t.get('t','') or t.get('title','')
    tid = t.get('id','')
    cat = t.get('category','') or t.get('c','')
    sm = (t.get('definition','') or t.get('s','') or t.get('summary','') or '')[:80]
    if title:
        dict_terms.add(title)
        term_meta[title] = {'id': tid, 'c': cat, 's': sm}
print(f"词典词条: {len(dict_terms)}")

# 过滤停用词（太通用的单字/虚词不参与自动匹配）
STOP = set('''如是 尔时 世尊 弟子 如是我闻 大 故 即 不 无 有 一 二 三 四 五 六 七 八 九 十 中 上 下 时 名 言 说 曰 彼 此 是 非 若 如 者 也 矣 乎 所 以 为 与 及 而 何 其 于 则 乃 诸 等 复 又 应 当 可 能 得 已 未 皆 悉 俱 同 异 去 来 我 人 众 生 法 心 行 相 见 知 觉 道 果 德 福 慧 智 力 愿 业 因 缘 苦 集 灭 善 恶 净 染 真 俗 空 假 常 乐 色 受 想 识 眼 耳 鼻 舌 身 意 地 水 火 风 天 龙 鬼 神'''.split())
core_terms = set()
for t in dict_terms:
    if len(t) >= 2 and t not in STOP and not re.match(r'^[0-9a-zA-Z\s]+$', t):
        core_terms.add(t)
print(f"可用关联术语: {len(core_terms)}")

def sutra_key(s):
    if not s: return ''
    if re.match(r'^[tT]\d+[a-z]?$', s):
        return s.lower()
    if re.match(r'^\d+$', s):
        return f't{int(s):04d}'
    return s.lower()

def dedup(lst, key_fn, limit=20):
    seen, out = set(), []
    for it in lst:
        k = key_fn(it)
        if k not in seen:
            seen.add(k); out.append(it)
        if len(out) >= limit: break
    return out

# ============ 1. 学者注关联 ============
print("\n=== 1. 学者注关联 ===")
term_to_notes = defaultdict(list)
note_to_terms = defaultdict(set)
note_to_sutras = defaultdict(list)
term_to_sutras = defaultdict(list)
note_to_kepan = defaultdict(list)

def walk_note_anchors(notes_list, sutra_id='', sutra_title=''):
    for n in notes_list:
        sid = sutra_key(n.get('sutra_id') or sutra_id)
        st_title = n.get('title') or sutra_title
        anchors = n.get('anchors', [])
        # 旧格式单anchor
        if 'anchor' in n and not anchors:
            anchors = [{'text': n['anchor'], 'scholars': [{'name': n.get('scholar',''), 'work': n.get('work',''), 'note': n.get('viewpoint','')}]}]
        for a in anchors:
            anchor_text = a.get('text','')
            for sc in a.get('scholars', []):
                nid = f"{sid}__{anchor_text[:10]}_{sc.get('name','')[:4]}"
                note_info = {
                    'note_id': nid, 'sutra_id': sid, 'sutra_title': st_title,
                    'anchor': anchor_text, 'scholar': sc.get('name',''),
                    'work': sc.get('work',''), 'note': sc.get('note','')
                }
                # 关键词提取：anchor本身是关键词
                for kw_phrase in [anchor_text]:
                    if kw_phrase:
                        term_to_notes[kw_phrase].append(note_info)
                        note_to_terms[nid].add(kw_phrase)
                # note 文本里的术语
                full_text = anchor_text + ' ' + sc.get('note','')
                for term in core_terms:
                    if term in full_text:
                        term_to_notes[term].append(note_info)
                        note_to_terms[nid].add(term)
                # note → sutra
                if sid and anchor_text:
                    note_to_sutras[nid].append({
                        'sutra_id': sid, 'anchor': anchor_text,
                        'sutra_title': st_title
                    })
                    # term → sutra (anchor点)
                    for term in core_terms:
                        if term in anchor_text:
                            term_to_sutras[term].append({
                                'sutra_id': sid, 'anchor': anchor_text,
                                'sutra_title': st_title, 'source': 'scholar_note'
                            })

walk_note_anchors(notes_data.get('notes', []))
print(f"  学者锚点: {sum(len(n.get('anchors',[])) for n in notes_data.get('notes',[]))}")
print(f"  term→notes: {len(term_to_notes)}")
print(f"  term→sutras via notes: {len(term_to_sutras)}")

# ============ 2. 科判关联 ============
print("\n=== 2. 科判关联 ===")
term_to_kepan = defaultdict(list)
kepan_to_sutra = {}
_kepan_count = [0]

def walk_kepan(nodes, sid, path=''):
    if not nodes: return
    for n in nodes:
        title = n.get('name','') or n.get('title','')
        desc = n.get('description','') or n.get('desc','') or ''
        content = n.get('content','') or n.get('quote','') or ''
        juan = n.get('juan','')
        cur_path = path + ' → ' + title if path else title
        nid = f"{sid}__{title}"
        # kepan → sutra
        if content.strip() and sid:
            kepan_to_sutra[nid] = {
                'kepan_id': nid, 'sutra_id': sid, 'title': title, 'path': cur_path,
                'quote': content[:100], 'juan': juan
            }
            _kepan_count[0] += 1
            # term → sutra via kepan content
            for term in core_terms:
                if term in content:
                    term_to_sutras[term].append({
                        'sutra_id': sid, 'anchor': content[:30],
                        'sutra_title': title, 'source': 'kepan', 'kepan_id': nid
                    })
        # term → kepan
        node_text = title + ' ' + desc + ' ' + content
        for term in core_terms:
            if term in node_text:
                term_to_kepan[term].append({
                    'kepan_id': nid, 'sutra_id': sid, 'title': title,
                    'path': cur_path, 'quote': content[:40]
                })
        # 递归
        children = n.get('children', n.get('subnodes', [])) or []
        walk_kepan(children, sid, cur_path)

for sid, kdata in kepan_data.items():
    walk_kepan(kdata.get('kepan', []), sutra_key(sid))
print(f"  科判节点(含原文): {_kepan_count[0]}")
print(f"  term→kepan: {len(term_to_kepan)}")

# note → kepan (via common term)
for nid, tset in note_to_terms.items():
    for t in tset:
        for k in term_to_kepan.get(t, []):
            if k['sutra_id'] == note_to_sutras.get(nid, [{}])[0].get('sutra_id','') if note_to_sutras.get(nid) else True:
                if not any(x['kepan_id'] == k['kepan_id'] for x in note_to_kepan[nid]):
                    note_to_kepan[nid].append(k)
                if len(note_to_kepan[nid]) >= 5: break

# ============ 3. 异译组 ============
print("\n=== 3. 异译组 ===")
para_path = os.path.join(ROOT, 'ontology/parallel_translations.json')
para = load_json(para_path) if os.path.exists(para_path) else []
sutra_to_parallel = defaultdict(list)
for grp in para:
    gid = grp.get('id','') or ''
    name = grp.get('title','') or grp.get('group_name','') or grp.get('name','')
    for ver in (grp.get('sutras',[]) or grp.get('versions',[])):
        sid = sutra_key(ver.get('id','') or ver.get('sutra_id',''))
        if sid:
            sutra_to_parallel[sid].append({
                'group_id': gid, 'group_name': name,
                'translator': ver.get('translator',''), 'dynasty': ver.get('dynasty','')
            })
print(f"  有异译组的经: {len(sutra_to_parallel)}")

# ============ 4. 汇总去重 ============
def dedup_term_links(d, key_fn, limit):
    return {k: dedup(v, key_fn, limit) for k,v in d.items()}

cross = {
    'meta': {
        'version': '1.0',
        'total_terms': len(dict_terms),
        'stats': {
            'terms_with_sutras': len(term_to_sutras),
            'terms_with_notes': len(term_to_notes),
            'terms_with_kepan': len(term_to_kepan),
            'kepan_to_sutra_count': len(kepan_to_sutra),
            'note_count': len(note_to_sutras),
            'sutras_with_parallel': len(sutra_to_parallel),
        }
    },
    'term_to_sutras': dedup_term_links(term_to_sutras, lambda x: x.get('sutra_id','')+'|'+x.get('anchor','')[:20], 15),
    'term_to_notes': dedup_term_links(term_to_notes, lambda x: x.get('note_id',''), 8),
    'term_to_kepan': dedup_term_links(term_to_kepan, lambda x: x.get('kepan_id',''), 8),
    'kepan_to_sutra': kepan_to_sutra,
    'note_to_sutras': {k: v[:2] for k,v in note_to_sutras.items()},
    'note_to_terms': {k: sorted(list(v))[:12] for k,v in note_to_terms.items()},
    'note_to_kepan': {k: v[:3] for k,v in note_to_kepan.items()},
    'sutra_to_parallel': dict(sutra_to_parallel),
}

out_path = os.path.join(ROOT, 'data/cross-links.json')
save_json(out_path, cross)
sz = os.path.getsize(out_path)/1024
print(f"\n=== 写入 {out_path} ({sz:.1f} KB) ===")
print(f"stats: {json.dumps(cross['meta']['stats'], ensure_ascii=False, indent=2)}")
# 抽样检查
print("\n抽样: 般若 → sutras:", len(term_to_sutras.get('般若',[])), "notes:", len(term_to_notes.get('般若',[])), "kepan:", len(term_to_kepan.get('般若',[])))
print("抽样: 阿耨多罗三藐三菩提 → sutras:", len(term_to_sutras.get('阿耨多罗三藐三菩提',[])))
print("抽样: 色不异空 → notes:", len(term_to_notes.get('色不异空',[])))
