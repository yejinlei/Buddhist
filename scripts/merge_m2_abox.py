#!/usr/bin/env python3
"""M2 ABox 整合：把旧 js/ontology-data.js (216/100/100/984) 与
data/*-expanded.json (50/54/20/109) 合并去重，生成统一实例。
输出到 ontology/instances/{concepts,persons,sutras,sects,relations}/。
"""
import json, os, re, subprocess, sys
from pathlib import Path

BASE = Path('/home/user/workspace/13511660557912876654/buddhist-ontology')

# ---------- 1. 加载旧 JS ----------
js = (BASE/'js/ontology-data.js').read_text(encoding='utf-8')
js = js.replace('const ontologyData =', 'ontologyData =', 1)
js_out = '/tmp/_load_old.js'
Path(js_out).write_text("""
const fs = require('fs');
const vm = require('vm');
let src = fs.readFileSync(process.argv[1],'utf8');
const sandbox = { ontologyData: null };
vm.createContext(sandbox);
vm.runInContext(src, sandbox);
process.stdout.write(JSON.stringify(sandbox.ontologyData));
""", encoding='utf-8')
# 把替换后的 js 写到临时文件
tmp_js = '/tmp/_old_ont.js'
Path(tmp_js).write_text(js, encoding='utf-8')
r = subprocess.run(['node', '-e', open(js_out).read().replace("process.argv[1]", repr(tmp_js))],
                   capture_output=True, text=True)
if r.returncode != 0:
    print('node err:', r.stderr); sys.exit(1)
old = json.loads(r.stdout)
print(f"旧数据: concepts={len(old['concepts'])} persons={len(old['persons'])} "
      f"sects={len(old['sects'])} core_sutras={len(old['core_sutras'])} "
      f"relations={len(old['relations'])} panjiao_keys={list(old['panjiao_comparison'].keys())}")

# ---------- 2. 加载新 expanded ----------
def load(name):
    p = BASE/'data'/f'{name}-expanded.json'
    return json.loads(p.read_text(encoding='utf-8'))
newC = load('concepts')
newP = load('persons')
newS = load('sutras')
newR = load('relations')
newSec = load('sects')
print(f"新数据: concepts={len(newC['concepts'])} persons={len(newP['persons'])} "
      f"sutras={len(newS['sutras'])} relations={len(newR['relations'])} sects={len(newSec['sects'])}")

# ---------- 3. 合并 concepts ----------
# 新字段完整，旧字段简（id/name/layer/definition/sect）
# 策略：新已有的用新，旧里 sect 字段合并进 sect_interpretation 标注
old_c_by_id = {c['id']: c for c in old['concepts']}
merged_concepts = {}
for c in newC['concepts']:
    cid = c['id']
    oc = old_c_by_id.get(cid, {})
    # 补 sect 元信息（如果新有 sect_interpretation，旧 sect 作为"主属宗派"写入）
    if 'primary_sect' not in c and oc.get('sect'):
        c['primary_sect'] = oc['sect']
    # 层字段标准化：L1/L2/L3 统一
    if 'layer_label' not in c:
        layer_map = {'L1':'L1 教理本体层','L2':'L2 义理范畴层','L3':'L3 宗派行持层'}
        c['layer_label'] = layer_map.get(c.get('layer',''), c.get('layer',''))
    # 字段兜底
    for f in ['sanskrit','definition','sutra_source','sect_interpretation',
              'modern_interpretation','alias']:
        c.setdefault(f, '' if f in ['sanskrit','definition','modern_interpretation'] else [])
    merged_concepts[cid] = c

# 旧里有但新没有的 → 从旧补，字段标"待考"
added_c = 0
for cid, oc in old_c_by_id.items():
    if cid in merged_concepts:
        continue
    nc = {
        'id': cid,
        'layer': oc.get('layer',''),
        'layer_label': {'L1':'L1 教理本体层','L2':'L2 义理范畴层','L3':'L3 宗派行持层'}.get(oc.get('layer',''),''),
        'name': oc['name'],
        'sanskrit': '',
        'alias': [],
        'definition': oc.get('definition','（待考）'),
        'primary_sect': oc.get('sect','通途'),
        'sutra_source': ['（待考）'],
        'sect_interpretation': {oc.get('sect','通途'): oc.get('definition','（待考）')} if oc.get('sect') else {},
        'modern_interpretation': '（待考，已从旧版迁入）',
        '_source': 'merged_from_old_js'
    }
    merged_concepts[cid] = nc
    added_c += 1
print(f"合并后 concepts={len(merged_concepts)}（从旧补 {added_c} 条）")

# 层分布
layer_count = {}
for c in merged_concepts.values():
    L = c.get('layer','?')
    layer_count[L] = layer_count.get(L,0)+1
print('  层分布:', layer_count)

# ---------- 4. 合并 persons ----------
# 新 id 不连续（p001-xxx, 然后跳到 p400+）；旧是 p001-p100。
# 策略：建立 name→id 映射，同名即合并；其余从旧补入；最后重新按 category 重排。
merged_persons = {}
name2pid_new = {}
for p in newP['persons']:
    pid = p['id']
    merged_persons[pid] = p
    name2pid_new[p['name']] = pid

# 旧的 class → category 映射
cls2cat = {
    'buddha':'佛陀', 'bodhisattva':'菩萨', 'arhat':'阿罗汉/十大弟子',
    'master':'历代祖师译经师', 'scholar':'现代学者', 'folk':'民间信仰人物'
}
added_p = 0
for p in old['persons']:
    pid_old = p['id']; name = p['name']; cat = cls2cat.get(p.get('class',''), '历代祖师译经师')
    if name in name2pid_new:
        # 合并：补 primary_sect / class 标记
        ex = merged_persons[name2pid_new[name]]
        ex.setdefault('old_class', p.get('class',''))
        continue
    # 新里没有 → 从旧创建
    # 新 id 可能冲突（旧 p001-p100 与新 p001 段重叠）。需要找空位。
    # 计算新的 pid：从 p101 起找空
    new_pid = None
    for cand in range(101, 999):
        cid = f'p{cand:03d}'
        if cid not in merged_persons:
            new_pid = cid; break
    np = {
        'id': new_pid,
        'old_id': pid_old,
        'category': cat,
        'name': name,
        'sanskrit_name': '',
        'alias': [],
        'era': '（待考）',
        'place': '',
        'sect': '',
        'core_teachings': [],
        'sutra_records': ['（待考）'],
        'symbol': [],
        'mantra': '',
        'stories': [],
        'achievements': [],
        '_source': 'merged_from_old_js'
    }
    merged_persons[new_pid] = np
    name2pid_new[name] = new_pid
    added_p += 1
print(f"合并后 persons={len(merged_persons)}（从旧补 {added_p} 条）")
cat_count = {}
for p in merged_persons.values():
    cat_count[p['category']] = cat_count.get(p['category'],0)+1
print('  分类分布:', cat_count)

# ---------- 5. 合并核心经典 sutras ----------
# 新字段：id/taisho_id/category/name/volume_count/translations/core_content...
# 旧字段：id/sutra_id/name/translator/vol/category
merged_sutras = {}
taisho2id = {}
for s in newS['sutras']:
    sid = s['id']; merged_sutras[sid] = s
    tid = s.get('taisho_id','').replace('T','').lstrip('0') or ''
    if tid: taisho2id[tid.zfill(4)] = sid
added_s = 0
# 旧 id 重映射：新 s001-s020 已占，从 s021 起补
next_sid = 21
for s in old['core_sutras']:
    # 匹配 taisho_id
    tid_old = (s.get('sutra_id') or '').replace('t','').lstrip('0').zfill(4)
    if tid_old in taisho2id:
        ex = merged_sutras[taisho2id[tid_old]]
        # 补 translator 简写字段
        ex.setdefault('translator_brief', s.get('translator',''))
        ex.setdefault('category', s.get('category',''))
        continue
    sid = f's{next_sid:03d}'; next_sid += 1
    taisho_formal = 'T' + tid_old if tid_old else ''
    ns = {
        'id': sid,
        'old_id': s['id'],
        'taisho_id': taisho_formal,
        'category': s.get('category','经集部'),
        'name': s['name'],
        'volume_count': 0,
        'volume': s.get('vol',''),
        'translator_brief': s.get('translator','（待考）'),
        'translations': [{'id':f'{sid}_1','name':s['name'],'translator':s.get('translator','（待考）')}],
        'core_content': '（待考，已从旧版迁入）',
        'core_concept': [],
        'core_practice': [],
        '_source': 'merged_from_old_js'
    }
    merged_sutras[sid] = ns
    if tid_old: taisho2id[tid_old] = sid
    added_s += 1
print(f"合并后 core_sutras={len(merged_sutras)}（从旧补 {added_s} 条）")
cat_s = {}
for s in merged_sutras.values(): cat_s[s['category']] = cat_s.get(s['category'],0)+1
print('  部类分布:', cat_s)

# ---------- 6. 合并 relations ----------
# 新用 type 英文码 + description；旧用中文 relation 文本。
# 类型映射（旧中文 → 新英文码）
rel_type_map = {
    '细分':'subdivision', '摄属':'subsumption', '含':'contains', '即':'identity',
    '相即':'nonduality', '蕴含':'implies', '体现':'manifests', '所显':'reveals',
    '宗依':'based_on', '核心':'core_of', '根本':'root_of', '总纲':'outline_of',
    '破':'refutes', '所依':'depends_on', '对':'contrast_with', '为体':'essence_of',
    '成':'establishes', '化法':'contains', '化仪':'contains', '性具':'inherent_in',
    '相':'aspect_of', '一念具':'instantly_contains', '阶位':'stage_of', '定慧':'samadhi_prajna',
    '阐发':'elaborates', '四法界':'subdivision', '门':'gate_of', '喻':'metaphor_of',
    '判':'classifies', '位':'stage_of', '旨归':'points_to', '宗':'school_of',
    '本':'root_of', '法':'dharma_of', '用':'function_of', '机用':'function_of',
    '资粮':'provision_of', '行':'practice_of', '生处':'birthplace_of', '本愿':'vow_of',
    '开宗':'founds', '开宗/弘传':'propagates', '付法':'transmits_dharma_to',
    '门人':'disciple_of', '弟子':'disciple_of', '胁侍':'attendant_of',
    '护法':'protects', '化身':'emanation_of', '译出/著':'translated_by',
    '同经异译':'parallel_translation', '互熏':'mutual_perfuming', '观行':'practice_of',
    '印':'seal_of', '无常印':'seal_of', '无我印':'seal_of', '涅槃印':'seal_of',
    '灭谛':'truth_of', '道谛':'truth_of', '戒学':'shila_of', '施度':'paramita_of',
    '胜义':'ultimate_of', '世俗':'conventional_of', '为始':'begins_with',
    '为灭':'ceases_with', '为导':'guided_by', '牵引':'leads_to', '感':'responds_to',
    '印证':'verifies', '缘起':'arises_from', '体':'essence_of', '义':'meaning_of',
    '为归':'returns_to', '间':'relates_to', '':'generic'
}
# 先放新关系
merged_rels = {}
for r in newR['relations']:
    key = (r['source'], r['target'], r.get('type',''), r.get('description',''))
    merged_rels[key] = r
added_r = 0
# 旧关系需要做 id 映射（person 旧 p### → 新 p### 不连续，需用 name2pid_new 反查）
# 构建旧pid→新pid：已合并但改名的人
oldpid2newpid = {}
for np in merged_persons.values():
    if 'old_id' in np:
        oldpid2newpid[np['old_id']] = np['id']
# 没改名的：p001-p054 段
for pid, p in merged_persons.items():
    if 'old_id' not in p and pid.startswith('p'):
        try:
            n = int(pid[1:])
            if n <= 54:
                oldpid2newpid[pid] = pid
        except: pass

def map_id(x):
    # 概念 c### → 原样；人物 p### → 查映射；经典 s### → 原样（旧 s001-s100 与新冲突时已合并为新id）
    if x.startswith('p'):
        return oldpid2newpid.get(x, x)
    return x

for r in old['relations']:
    src = map_id(r['source']); tgt = map_id(r['target'])
    rel_cn = r.get('relation','').strip()
    rtype = rel_type_map.get(rel_cn, 'generic')
    desc = rel_cn if rel_cn else '（待考）'
    # 描述扩展：如果 target 是 concept，尽量拼
    key = (src, tgt, rtype, desc)
    if key in merged_rels:
        continue
    rid = f"r{len(merged_rels)+1+added_r:04d}"
    nr = {
        'id': rid,
        'source': src, 'target': tgt,
        'type': rtype,
        'relation_cn': rel_cn,
        'description': desc,
        '_source': 'merged_from_old_js'
    }
    merged_rels[key] = nr
    added_r += 1
print(f"合并后 relations={len(merged_rels)}（从旧补 {added_r} 条）")
type_count = {}
for r in merged_rels.values():
    t = r.get('type','generic')
    type_count[t] = type_count.get(t,0)+1
print('  类型分布 top10:', sorted(type_count.items(), key=lambda x:-x[1])[:10])

# ---------- 7. 宗派（直接用新数据，补旧 panjiao 字段） ----------
merged_sects = {s['id']: s for s in newSec['sects']}
# panjiao_comparison 新的更全（在 pages/panjiao.html），这里保持新 sects-expanded 里的为准
# 额外补 5 家：三论/禅/律/密/天台
# （后续 panjiao.html 数据源可以直接吃 sects-expanded）
print(f"宗派={len(merged_sects)}（沿用新数据 8 家）")

# ---------- 8. 落盘 ----------
out_base = BASE/'ontology'/'instances'
for sub in ['concepts','persons','sutras','sects']:
    (out_base/sub).mkdir(parents=True, exist_ok=True)

# concepts
for cid, c in merged_concepts.items():
    (out_base/'concepts'/f'{cid}.json').write_text(
        json.dumps(c, ensure_ascii=False, indent=2), encoding='utf-8')
# persons
for pid, p in merged_persons.items():
    (out_base/'persons'/f'{pid}.json').write_text(
        json.dumps(p, ensure_ascii=False, indent=2), encoding='utf-8')
# sutras
for sid, s in merged_sutras.items():
    (out_base/'sutras'/f'{sid}.json').write_text(
        json.dumps(s, ensure_ascii=False, indent=2), encoding='utf-8')
# sects
for secid, s in merged_sects.items():
    (out_base/'sects'/f'{secid}.json').write_text(
        json.dumps(s, ensure_ascii=False, indent=2), encoding='utf-8')
# relations（一个聚合文件）
rel_list = list(merged_rels.values())
(out_base/'relations.json').write_text(
    json.dumps({'meta':{'total':len(rel_list)},'relations':rel_list},
               ensure_ascii=False, indent=2), encoding='utf-8')

# manifest
manifest = {
    'meta': {
        'version': '3.1.0-M2',
        'generated_at': '2026-10-29',
        'layer': 'M2_ABox'
    },
    'counts': {
        'concepts': len(merged_concepts),
        'concepts_L1': layer_count.get('L1',0),
        'concepts_L2': layer_count.get('L2',0),
        'concepts_L3': layer_count.get('L3',0),
        'persons': len(merged_persons),
        'core_sutras': len(merged_sutras),
        'sects': len(merged_sects),
        'relations': len(rel_list)
    },
    'id_spaces': {
        'concepts': 'c001-c{:03d}'.format(max(int(c['id'][1:]) for c in merged_concepts.values())),
        'persons': 'p001-p{:03d}'.format(max(int(p['id'][1:]) for p in merged_persons.values() if p['id'][1:].isdigit())),
        'sutras': 's001-s{:03d}'.format(max(int(s['id'][1:]) for s in merged_sutras.values())),
        'sects': 'sec001-sec{:03d}'.format(max(int(s['id'][3:]) for s in merged_sects.values()))
    }
}
(out_base/'m2_manifest.json').write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print('\n=== 落盘完成 ===')
print(json.dumps(manifest, ensure_ascii=False, indent=2))
