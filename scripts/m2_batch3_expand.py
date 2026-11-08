#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M2 第3批扩招：30 个高频概念（c282 起）。"""
import json, os, re, glob
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
with open('data/buddhist_dict.json','r',encoding='utf-8') as f: bd=json.load(f)
DICT={t['name']:t for t in bd['terms']}
with open('ontology/dict-expansion-candidates.json','r',encoding='utf-8') as f: cands=json.load(f)['top200_candidates']
with open('ontology/instances/m2_index.json','r',encoding='utf-8') as f: m2=json.load(f)
with open('ontology/instances/relations.json','r',encoding='utf-8') as f: R=json.load(f)
with open('ontology/dict-links.json','r',encoding='utf-8') as f: DL=json.load(f)
existing={}
for fp in glob.glob('ontology/instances/concepts/c*.json'):
    with open(fp,'r',encoding='utf-8') as f:
        c=json.load(f); existing[c['name']]=c['id']
linked={lk['dict_word'] for lk in DL['links']}
existing_idx={ci['id'] for ci in m2['concepts']}
max_c=max(int(re.search(r'c(\d+)\.json',fp).group(1)) for fp in glob.glob('ontology/instances/concepts/c*.json'))
next_c=max_c+1
SKIP={'十二','十六','二十','四十八','十号','七觉支','释迦','三藏','佛教','弟子','诸佛','菩萨','比丘','行人','过去','二因','梵语','法华经'}
L1={'空性','真如','佛性','涅槃','自性','如来藏','第一义','中道','法身'}
L3={'布施','六度','忍辱','精进','止观','念佛','戒律','出家','持戒','具足戒','十住','十六观','陀罗尼','证悟','波罗蜜'}
SECT_MAP={'净土宗':'净土宗','禅宗':'禅宗','天台宗':'天台宗','唯识宗':'唯识宗','华严宗':'华严宗','三论宗':'三论宗','密宗':'密宗','戒律':'律宗','大乘义理':'通途','名相术语':'通途','基础教义':'通途','人物圣众':'通途','佛教常识':'通途','阿毗达磨':'说一切有部','法数名数':'通途','经论典籍':'通途','修行法门':'通途'}
def layer(w,c):
    if w in L1: return 'L1','L1 教理本体层'
    if w in L3: return 'L3','L3 宗派/法门/修证层'
    return 'L2','L2 基础法相层'
batch=[]
for c in cands:
    w=c['word']
    if w in existing or w in linked or w in SKIP or c['category']=='护法诸天': continue
    batch.append(c)
    if len(batch)>=30: break
print(f'第3批 {len(batch)} 个概念, c{next_c:03d}~c{next_c+len(batch)-1:03d}')
new_cs=[]; new_rels=[]; new_links=[]
PRE={
    '凡夫':[('opposite_to','圣人','凡圣相对')],
    '方便':[('leads_to','究竟','方便为入究竟之门径'),('opposite_to','真实','方便为权宜施设')],
    '应身':[('part_of','三身','应身与法身报身合称三身')],
    '具足戒':[('belongs_to','戒律','具足戒为比丘比丘尼所受大戒')],
    '赖耶识':[('short_for','阿赖耶',''),('core_of','唯识','')],
    '陀罗尼':[('belongs_to','真言','陀罗尼即总持法门')],
    '恶业':[('type_of','业',''),('cause_of','生死','恶业招感苦果')],
    '慈悲':[('part_of','六度','慈悲为大乘根本')],
    '有情':[('synonym_of','众生','有情即众生')],
    '善恶':[('pair_with','恶业','善恶为业之二分')],
    '执著':[('type_of','烦恼','执著为烦恼所摄'),('removed_by','般若','般若能破执著')],
    '正法':[('opposite_to','邪见','正法对治邪见')],
    '饿鬼':[('part_of','六道','饿鬼为六道之一')],
    '布施':[('part_of','六度','布施为六度第一度')],
    '善根':[('result_of','修行','修行增长善根')],
    '六尘':[('object_of','六根','六根缘六尘')],
    '万法':[('synonym_of','诸法','万法即诸法')],
    '六根':[('contacts','六尘','六根触六尘而起识')],
    '有为':[('opposite_to','无为','有为与无为为法之二分')],
    '邪见':[('type_of','烦恼','邪见为根本烦恼之一'),('opposite_to','正法','')],
    '不二':[('synonym_of','中道','不二法门即中道义')],
    '精进':[('part_of','六度','精进度为六度之一')],
    '三宝':[('core_of','佛法','佛法僧三宝为佛教归依处')],
    '比丘尼':[('female_of','比丘','比丘尼为女性出家受具足戒者')],
    '二乘':[('synonym_of','小乘','二乘即声闻缘觉')],
    '神通':[('result_of','禅定','依禅定发神通')],
    '波罗蜜':[('synonym_of','度','波罗蜜即到彼岸度'),('contains','布施','六度各为一波罗蜜')],
    '意识':[('belongs_to','唯识','意识为八识之第六识')],
    '证悟':[('result_of','修行','修行究竟证悟菩提')],
    '差别':[('opposite_to','平等','差别对平等')],
}
for c in batch:
    w=c['word']; cid=f'c{next_c:03d}'; next_c+=1
    L,ll=layer(w,c['category']); sect=SECT_MAP.get(c['category'],'通途')
    t=DICT.get(w,{}); d=(t.get('definition','') or c.get('definition',''))[:300]
    d=re.sub(r'。?\s*见[^。]*条。?$','',d).strip()
    src=['通途教义']
    if w in ('赖耶识','阿赖耶','意识','唯识'): src=['《成唯识论》（t1585）']
    elif w in ('法华经',): src=['《妙法莲华经》（t0262）']
    elif w in ('六度','布施','精进','忍辱'): src=['《大智度论》']
    elif w in ('具足戒','比丘尼'): src=['《四分律》']
    elif w in ('十六观',): src=['《观无量寿佛经》（t0365）']
    elif w in ('波罗蜜',): src=['《大般若经》']
    conc={'id':cid,'layer':L,'layer_label':ll,'name':w,'sanskrit':'','alias':[],'definition':d,'sutra_source':src,'sect_interpretation':{},'modern_interpretation':'','primary_sect':sect,'_source':'M2_batch3_dict_expansion'}
    new_cs.append(conc); existing[w]=cid
    new_links.append({'dict_word':w,'dict_clean':None,'dict_category':c['category'],'ontology_id':cid,'ontology_label':w,'ontology_type':'concept','match_method':'exact','match_via':'name'})
rel_keys={(r['source'],r['target'],r['type']) for r in R['relations']}
for c in new_cs:
    w=c['name']; cid=c['id']
    for typ,tgt,desc in PRE.get(w,[]):
        tid=existing.get(tgt)
        if tid and (cid,tid,typ) not in rel_keys:
            R['relations'].append({'source':cid,'target':tid,'type':typ,'description':desc})
            rel_keys.add((cid,tid,typ)); new_rels.append((cid,tid,typ))
for c in new_cs:
    with open(f'ontology/instances/concepts/{c["id"]}.json','w',encoding='utf-8') as f: json.dump(c,f,ensure_ascii=False,indent=2)
R['meta']['total']=len(R['relations']); R['summary']['total']=len(R['relations'])
with open('ontology/instances/relations.json','w',encoding='utf-8') as f: json.dump(R,f,ensure_ascii=False,indent=2)
DL['links'].extend(new_links); DL['summary']['matched_count']=len(DL['links'])
with open('ontology/dict-links.json','w',encoding='utf-8') as f: json.dump(DL,f,ensure_ascii=False,indent=2)
new_idx=[]
for c in new_cs:
    if c['id'] not in existing_idx:
        m2['concepts'].append({'id':c['id'],'name':c['name'],'layer':c['layer'],'primary_sect':c['primary_sect'],'definition_short':c['definition'][:80]})
        new_idx.append(c['id'])
m2['meta']['total_concepts']=len(m2['concepts']); m2['meta']['total_relations']=len(R['relations']); m2['meta']['version']='3.2.0-M2-batch3'
with open('ontology/instances/m2_index.json','w',encoding='utf-8') as f: json.dump(m2,f,ensure_ascii=False,indent=2)
print(f'新增concept: {len(new_cs)}: {[c["name"] for c in new_cs]}')
print(f'新增relations: {len(new_rels)}, dict-links: {len(new_links)}(总{len(DL["links"])}), m2_index追加{len(new_idx)}(总concepts={m2["meta"]["total_concepts"]})')
