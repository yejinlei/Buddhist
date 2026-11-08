#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M2 第2批扩招：从 dict-expansion-candidates 取第31-60个有效高频概念。"""
import json, os, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

with open('data/buddhist_dict.json','r',encoding='utf-8') as f:
    bd = json.load(f)
DICT = {t['name']: t for t in bd['terms']}
with open('ontology/dict-expansion-candidates.json','r',encoding='utf-8') as f:
    cands = json.load(f)['top200_candidates']
with open('ontology/instances/m2_index.json','r',encoding='utf-8') as f:
    m2 = json.load(f)
with open('ontology/instances/relations.json','r',encoding='utf-8') as f:
    R = json.load(f)
with open('ontology/dict-links.json','r',encoding='utf-8') as f:
    DL = json.load(f)

# 现有概念名->id
existing = {}
for fp in glob.glob('ontology/instances/concepts/c*.json'):
    with open(fp,'r',encoding='utf-8') as f:
        c = json.load(f)
    existing[c['name']] = c['id']
# 已在dict-links中的词
linked_words = {lk['dict_word'] for lk in DL['links']}
# 已在m2_index中的concept id
existing_idx_ids = {ci['id'] for ci in m2['concepts']}
# 下一个c编号
max_c = max(int(re.search(r'c(\d+)\.json$',fp).group(1))
            for fp in glob.glob('ontology/instances/concepts/c*.json'))
next_cid = max_c + 1

SKIP = {'十二','十六','二十','四十八','十号','七觉支','释迦','三藏','佛教','弟子','诸佛','菩萨','比丘',
        '行人','过去','二因','梵语','诸佛','弥陀','金刚','道理','凡夫','方便','二十','二十唯识论'}

L1_WORDS = {'涅槃','真如','佛性','空性','实相','法身','佛','自性','如来藏','中道','第一义','无为法','实相','法性','一如','真心'}
L3_WORDS = {'三昧','出家','罗汉','方便','具足戒','陀罗尼','十住','十六观','唯识','真言','出家','受戒','持戒','念佛','止观','六度','忍辱','精进','般若','菩提心','出家','僧','丛林','公案','棒喝'}
SECT_MAP = {'净土宗':'净土宗','禅宗':'禅宗','天台宗':'天台宗','唯识宗':'唯识宗',
            '华严宗':'华严宗','三论宗':'三论宗','密宗':'密宗','戒律':'律宗',
            '大乘义理':'通途','名相术语':'通途','基础教义':'通途','人物圣众':'通途',
            '佛教常识':'通途','阿毗达磨':'说一切有部','法数名数':'通途','修行法门':'通途'}

def decide_layer(w, cat):
    if w in L1_WORDS: return 'L1','L1 教理本体层'
    if w in L3_WORDS: return 'L3','L3 宗派/法门/修证层'
    return 'L2','L2 基础法相层'

batch2=[]
for c in cands:
    w=c['word']
    if w in SKIP or w in existing or w in linked_words: continue
    if c['category']=='护法诸天': continue
    batch2.append(c)
    if len(batch2)>=30: break

print(f'第2批生成 {len(batch2)} 个概念, 编号 c{next_cid:03d}~c{next_cid+len(batch2)-1:03d}')

new_cs = []
new_rels=[]
new_links=[]

PRESETS = {
    '凡夫':[('opposite_to','圣人','凡圣相对')],
    '方便':[('opposite_to','真实','方便为权宜之法，别于真实'), ('leads_to','究竟','方便为究竟之手段')],
    '无明':[('cause_of','烦恼','无明为烦恼根本'), ('opposite_to','智慧','智慧破无明'), ('type_of','烦恼','无明为根本烦恼之一')],
    '法华':[('belongs_to','大乘','法华经为大乘经'), ('short_for','法华经','')],
    '自在':[('result_of','解脱','解脱后得大自在')],
    '罗汉':[('fruit_of','声闻','阿罗汉为声闻乘最高果位'),('belongs_to','小乘','阿罗汉属小乘果位')],
    '出家':[('opposite_to','在家','出家与在家为二众'),('leads_to','修行','出家为修行初门')],
    '三昧':[('synonym_of','禅定','三昧即正定')],
    '欲界':[('part_of','三界','欲界为三界之一'),('contains','地狱','地狱在欲界中')],
    '过去':[('part_of','三世','过去世为三世之一')],
    '极乐':[('synonym_of','净土','极乐世界即阿弥陀佛净土')],
    '六道':[('contains','地狱','六道含地狱'),('contains','饿鬼','六道含饿鬼'),('contains','畜生',''),('contains','人',''),('contains','天',''),('contains','阿修罗','')],
    '无色界':[('part_of','三界','无色界为三界之一')],
    '四大':[('composes','色法','四大为色法基本元素')],
    '法相':[('basis_of','唯识','法相宗又名唯识宗')],
    '无碍':[('result_of','解脱','解脱后通达无碍')],
    '相应':[('type_of','瑜伽','相应即瑜伽义')],
    '法门':[('part_of','教法','法门为教法之门户')],
    '虚空':[('metaphor_for','法界','虚空常比喻法界广大')],
    '化身':[('part_of','三身','化身与法身、报身为佛三身')],
    '戒律':[('part_of','三学','戒定慧三学之一'),('synonym_of','戒','')],
    '平等':[('result_of','智慧','智慧现前证平等性')],
    '缘觉':[('belongs_to','小乘','缘觉乘属二乘'),('synonym_of','辟支佛','')],
    '不生':[('synonym_of','涅槃','涅槃即不生不灭'),('aspect_of','无为法','不生不灭是无为法相')],
    '供养':[('part_of','修行','供养为修行方便')],
    '受持':[('result_of','信仰','信受奉持')],
    '赖耶':[('short_for','阿赖耶','赖耶为阿赖耶识简称'),('synonym_of','阿赖耶','')],
    '阿赖耶':[('short_for','阿赖耶识',''),('core_of','唯识','阿赖耶识为唯识宗核心')],
    '唯识':[('belongs_to','大乘','唯识宗为大乘宗派'),('based_on','法相','')],
    '国土':[('synonym_of','佛土','佛所化度国土')],
    '心所':[('belongs_to','法相','心所为心王所属心所有法')],
}

added_names_in_batch = set()
for c in batch2:
    w = c['word']
    cid = f'c{next_cid:03d}'; next_cid += 1
    layer, ll = decide_layer(w, c['category'])
    sect = SECT_MAP.get(c['category'],'通途')
    term = DICT.get(w,{})
    definition = (term.get('definition','') or c.get('definition',''))[:300]
    definition = re.sub(r'。?\s*见[^。]*条。?$','',definition).strip()
    sutra_src = []
    if w in ('法华',): sutra_src = ['《妙法莲华经》（t0262）']
    elif w in ('唯识','阿赖耶','赖耶','心所'): sutra_src=['《成唯识论》（t1585）','《解深密经》（t0676）']
    elif w in ('极乐',): sutra_src=['《佛说阿弥陀经》（t0366）']
    elif w in ('三昧','自在'): sutra_src=['《大智度论》']
    elif w in ('罗汉','出家'): sutra_src=['《阿含经》']
    else: sutra_src=['通途教义']
    concept = {
        'id':cid,'layer':layer,'layer_label':ll,'name':w,
        'sanskrit':'','alias':[],'definition':definition,'sutra_source':sutra_src,
        'sect_interpretation':{},'modern_interpretation':'','primary_sect':sect,
        '_source':'M2_batch2_dict_expansion'
    }
    new_cs.append(concept)
    existing[w]=cid; added_names_in_batch.add(w)
    new_links.append({'dict_word':w,'dict_clean':None,'dict_category':c['category'],
        'ontology_id':cid,'ontology_label':w,'ontology_type':'concept','match_method':'exact','match_via':'name'})

# 关系
rel_keys = {(r['source'],r['target'],r['type']) for r in R['relations']}
for c in new_cs:
    w=c['name']; cid=c['id']
    for typ,target,desc in PRESETS.get(w,[]):
        tid = existing.get(target)
        if tid and (cid,tid,typ) not in rel_keys:
            R['relations'].append({'source':cid,'target':tid,'type':typ,'description':desc})
            rel_keys.add((cid,tid,typ)); new_rels.append((cid,tid,typ))

# 写文件
for c in new_cs:
    with open(f'ontology/instances/concepts/{c["id"]}.json','w',encoding='utf-8') as f:
        json.dump(c,f,ensure_ascii=False,indent=2)

R['meta']['total']=len(R['relations']); R['summary']['total']=len(R['relations'])
with open('ontology/instances/relations.json','w',encoding='utf-8') as f:
    json.dump(R,f,ensure_ascii=False,indent=2)

DL['links'].extend(new_links); DL['summary']['matched_count']=len(DL['links'])
with open('ontology/dict-links.json','w',encoding='utf-8') as f:
    json.dump(DL,f,ensure_ascii=False,indent=2)

new_idx=[]
for c in new_cs:
    if c['id'] not in existing_idx_ids:
        m2['concepts'].append({'id':c['id'],'name':c['name'],'layer':c['layer'],'primary_sect':c['primary_sect'],'definition_short':c['definition'][:80]})
        new_idx.append(c['id'])
m2['meta']['total_concepts']=len(m2['concepts']); m2['meta']['total_relations']=len(R['relations'])
m2['meta']['version']='3.2.0-M2-batch2'
with open('ontology/instances/m2_index.json','w',encoding='utf-8') as f:
    json.dump(m2,f,ensure_ascii=False,indent=2)

print(f'新增concept: {len(new_cs)}')
print('新增词:', [c['name'] for c in new_cs])
print(f'新增relations: {len(new_rels)}')
print(f'新增dict-links: {len(new_links)} (总{len(DL["links"])})')
print(f'新增m2_index: {len(new_idx)} (总concepts={m2["meta"]["total_concepts"]})')
