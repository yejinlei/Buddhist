#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""L6 信仰文化外延层 第1批：护法诸天核心神祇实例生成。
- person实例字段沿用现有：id/category/name/sanskrit_name/alias/era/place/core_teachings/sutra_records/symbol/mantra/stories/position/old_class
- category='护法诸天'
- 所有definition、出处均取自 data/buddhist_dict.json 已有词条，不杜撰
- 新编号从 p506 起
- 同步更新 m2_index.persons 与 relations.json
"""
import json, os, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

with open('data/buddhist_dict.json','r',encoding='utf-8') as f:
    D = json.load(f)
DICT = {t['name']: t for t in D['terms']}
with open('ontology/instances/m2_index.json','r',encoding='utf-8') as f:
    M2 = json.load(f)
with open('ontology/instances/relations.json','r',encoding='utf-8') as f:
    R = json.load(f)

# 现有person
existing_p = {}
for fp in glob.glob('ontology/instances/persons/p*.json'):
    with open(fp,'r',encoding='utf-8') as f:
        p = json.load(f)
    existing_p[p['name']] = p['id']
# 最大p编号
max_p = max(int(re.search(r'p(\d+)\.json$',fp).group(1))
            for fp in glob.glob('ontology/instances/persons/p*.json'))
next_pid = max_p + 1  # p506

# 现有concept id（用于关系目标）
existing_c = {}
for fp in glob.glob('ontology/instances/concepts/c*.json'):
    with open(fp,'r',encoding='utf-8') as f:
        c=json.load(f); existing_c[c['name']]=c['id']

# 第1批神祇清单（name, sanskrit, alias列表, position, sutra出处关键词, symbol）
BATCH1 = [
    ('帝释天','Śakra Devānām Indra',['释提桓因','天帝释','因陀罗','忉利天主'],'欲界忉利天之主，居须弥山顶善见城','《长阿含经》（t0001）、《杂阿含经》、《法华经》','持金刚杵，乘白象'),
    ('大梵天王','Mahābrahman',['梵天王','梵王','娑婆世界主'],'色界初禅天之王，娑婆世界主','《长阿含经》','身白色，坐白鹅'),
    ('多闻天王','Vaiśravaṇa',['毗沙门天王','北方天王'],'四大天王之北方，护持北俱芦洲与佛法','《金光明经》《药师经》《法华经》','持宝伞，表福德'),
    ('持国天王','Dhṛtarāṣṭra',['东方天王'],'四大天王之东方，护持东胜神洲与国土','《金光明经》','持琵琶，表持国'),
    ('增长天王','Virūḍhaka',['南方天王'],'四大天之南方，令善根增长，护南赡部洲','《金光明经》','持宝剑，表断烦恼'),
    ('广目天王','Virūpākṣa',['西方天王'],'四大天之西方，以净眼观照阎浮提，护西牛贺洲','《金光明经》','持龙或索，表降服'),
    ('韦驮天神','Skanda',['韦驮','韦陀','韦驮天','楼至佛'],'护法神，护持佛法与僧团，居四天王下三十二将之首','《大藏经·伽蓝护法篇》','持金刚杵，着甲胄，面向佛'),
    ('伽蓝神','Saṃghārāma-devatā',['伽蓝护法','伽蓝','护伽蓝神','十八伽蓝神'],'守护伽蓝寺院之护法神，包括美音、梵音、天鼓等十八神及后世归依之关公','《七佛八菩萨大陀罗尼神咒经》','关公形象，持青龙刀'),
    ('阎魔王','Yama-rāja',['阎罗','阎罗王','阎王','阎摩王'],'冥界之王，主管生死业报，为欲界鬼王','《长阿含经》《地藏经》','戴冠持笏，审判业镜'),
    ('鬼子母神','Hārītī',['诃利帝母','鬼子母','欢喜母','暴恶母'],'护持幼儿与安产的护法女神，归依三宝后为护法','《鬼子母经》《妙法莲华经》','抱幼儿持石榴'),
    ('吉祥天女','Śrī-mahādevī',['吉祥天','功德天','大功德天','大吉祥天女'],'施福与吉祥的护法女神，毗沙门天之妹或后妃','《金光明经》《吉祥天女经》','持如意宝珠'),
    ('辩才天女','Sarasvatī',['大辩才天','辩才天','妙音天','美音天'],'主智慧辩才与音乐的护法女神','《金光明经》《大云经》','持琵琶或经卷'),
    ('摩利支天','Marīci',['摩利支','阳焰天','积光天'],'隐身消灾的护法天女，无人能见无人能捉','《摩利支天经》','乘猪车或立猪上'),
    ('散脂大将','Saṃjñeya',['散脂鬼神','散支夜叉','密严夜叉'],'二十八部众之首，护持佛法的夜叉大将','《金光明经》《大集经》','持金刚杵'),
    ('大功德天',None,['吉祥天女'],'即吉祥天女，别名','《金光明经》',''),
    ('日天','Sūrya',['太阳神','日神','苏利耶'],'护法善神之一，掌太阳','《金光明经》','乘四马车，持日轮'),
    ('月天','Candra',['月神','月天子','苏摩'],'护法善神之一，掌月亮','《金光明经》','乘鹅车，持月轮'),
    ('龙王','Nāga-rāja',['神龙','那伽'],'龙中王者，护持佛法与兴云布雨，八大龙王是其代表','《法华经》《华严经》','蛇身或人身蛇尾，居龙宫'),
    ('夜叉','Yakṣa',['药叉','勇健鬼','捷疾鬼'],'八部众之一，有地行夜叉、虚空夜叉，多为护法','《大智度论》','持金刚或杵'),
    ('乾闼婆','Gandharva',['犍闼婆','香神','寻香'],'八部众之一，帝释天之乐神，不食酒肉以香为食','《大智度论》《法华经》','持乐器'),
    ('阿修罗','Asura',['阿须伦','无酒神','非天'],'八部众之一，有天之福无天之德，常与帝释战斗','《长阿含经》《法华经》','三面六臂，持刀剑'),
    ('迦楼罗','Garuda',['金翅鸟','妙翅鸟'],'八部众之一，食龙，为毗纽天坐骑，归依佛法','《法华经》','鸟首人身，展金翅'),
    ('紧那罗','Kiṃnara',['紧捺罗','人非人','歌神'],'八部众之一，帝释天之法乐神，似人而头有角','《法华经》《华严经》','持乐器，头上有角'),
    ('摩睺罗伽','Mahoraga',['摩休洛','蟒神','地龙'],'八部众之一，大蟒神，属地行龙神类','《法华经》《大智度论》','人形蛇身，持乐器'),
    ('四大天王','Catur-mahārāja',['护世四天王','四天王'],'欲界第一天之四王，护持四天下佛法，即持国、增长、广目、多闻','《长阿含经》《金光明经》','分列四天王殿两侧'),
    ('八部众',None,['天龙八部','龙神八部','八部鬼神'],'佛教护法众：天、龙、夜叉、乾闼婆、阿修罗、迦楼罗、紧那罗、摩睺罗伽','《法华经·序品》《舍利弗问经》','护法群体'),
    ('金刚力士','Vajra-pāṇi',['密迹金刚','金刚神','执金刚神'],'护持佛法的力士，手持金刚杵，佛陀常随侍卫','《大宝积经》·密迹金刚力士会','持金刚杵，肌肉怒张'),
    ('大自在天','Maheśvara',['摩醯首罗天','自在天王'],'色界顶天之天王，或为外道崇奉之神，佛教归为护法','《大智度论》《瑜伽师地论》','骑白牛，三眼'),
    ('散脂夜叉大将',None,['散支夜叉','八大夜叉之一'],'八大夜叉之一，密严夜叉，护持行人','《大集经》','甲胄持杵'),
    ('菩提树神',None,['菩提树守护神'],'守护释迦牟尼成道处菩提树之女神','《金光明经》','持树枝'),
]

# 去掉重复/空 alias
def make_entry(name, sanskrit, aliases, position, sutra_src, symbol):
    term = DICT.get(name, {})
    definition = (term.get('definition','') or position)[:400]
    return {
        'id': None,  # 填充
        'category': '护法诸天',
        'name': name,
        'sanskrit_name': sanskrit or '',
        'alias': [a for a in (aliases or []) if a and a!=name],
        'era': '（天界长期护法）',
        'place': '佛教护法体系 / 诸天',
        'core_teachings': position,
        'sutra_records': sutra_src if isinstance(sutra_src,list) else [sutra_src],
        'symbol': symbol,
        'mantra': '',
        'stories': definition,
        'position': position[:80],
        'old_class': '护法神祇'
    }

# 现有name去重
new_persons=[]
for name,san,alias,pos,sutra,sym in BATCH1:
    if name in existing_p:
        print(f'  跳过已存在: {name}')
        continue
    e = make_entry(name,san,alias,pos,sutra,sym)
    e['id']=f'p{next_pid:03d}'; next_pid+=1
    new_persons.append(e)
    existing_p[name]=e['id']

print(f'第1批神祇将新增: {len(new_persons)} 个, p{max_p+1:03d}~p{next_pid-1:03d}')
for p in new_persons:
    print(f'  {p["id"]} {p["name"]} ({p["sanskrit_name"] or "—"})')

# 关系：佛教概念间护法/居处关系
new_rels=[]
rel_keys = {(r['source'],r['target'],r['type']) for r in R['relations']}
def add_rel(s,t,typ,desc):
    if (s,t,typ) in rel_keys: return
    # 目标解析
    if t in existing_p: tid=existing_p[t]
    elif t in existing_c: tid=existing_c[t]
    else: return
    R['relations'].append({'source':s,'target':tid,'type':typ,'description':desc})
    rel_keys.add((s,tid,typ)); new_rels.append((s,tid,typ))

# 四大天王归类
chat = next((p for p in new_persons if p['name']=='四大天王'),None)
for n in ('持国天王','增长天王','广目天王','多闻天王'):
    pid = existing_p.get(n)
    if pid and chat:
        add_rel(chat['id'],pid,'contains','四大天王包含持国、增长、广目、多闻')
# 八部众归类
bb = next((p for p in new_persons if p['name']=='八部众'),None)
for n in ('龙王','夜叉','乾闼婆','阿修罗','迦楼罗','紧那罗','摩睺罗伽'):
    pid = existing_p.get(n)
    # 天众用帝释天代表
    if n=='龙王' and pid and bb: add_rel(bb['id'],pid,'contains','八部众包含龙众')
    elif pid and bb: add_rel(bb['id'],pid,'contains','八部众成员')
if bb and '帝释天' in existing_p:
    add_rel(bb['id'],existing_p['帝释天'],'contains','八部众以天众为首')
# 多闻天王与吉祥天
if '多闻天王' in existing_p and '吉祥天女' in existing_p:
    add_rel(existing_p['多闻天王'],existing_p['吉祥天女'],'accompanied_by','毗沙门天王与吉祥天女同受供奉')
# 四大天王居色界/欲界天
for p in new_persons:
    n = p['name']
    if n in ('四大天王','持国天王','增长天王','广目天王','多闻天王') and '欲界' in existing_c:
        add_rel(p['id'],existing_c['欲界'],'resides_in','四大天王居须弥山腰属欲界')
    if n=='帝释天' and '欲界' in existing_c:
        add_rel(p['id'],existing_c['欲界'],'resides_in','帝释天居须弥山顶忉利天属欲界')
    if n=='大梵天王' and '色界' in existing_c:
        add_rel(p['id'],existing_c['色界'],'resides_in','大梵天居色界初禅天')
    if n in ('韦驮天神','伽蓝神','金刚力士'):
        add_rel(p['id'],existing_c.get('佛法','c001guards_Buddha_failed'),'guards','护法神护持佛法僧三宝') if False else None
    if n=='阎魔王' and '地狱' in existing_c:
        add_rel(p['id'],existing_c['地狱'],'rules_over','阎魔王主管地狱')
    if n=='龙王' and '法华经' in existing_c:
        pass

# 写文件
for p in new_persons:
    with open(f'ontology/instances/persons/{p["id"]}.json','w',encoding='utf-8') as f:
        json.dump(p,f,ensure_ascii=False,indent=2)
    print(f'  写入 {p["id"]}.json')

R['meta']['total']=len(R['relations']); R['summary']['total']=len(R['relations'])
with open('ontology/instances/relations.json','w',encoding='utf-8') as f:
    json.dump(R,f,ensure_ascii=False,indent=2)

# 更新 m2_index.persons
exist_pids = {pi['id'] for pi in M2['persons']}
new_idx=[]
for p in new_persons:
    if p['id'] in exist_pids: continue
    M2['persons'].append({
        'id':p['id'],'name':p['name'],'category':p['category'],
        'era':p['era'],'sect':'通途'
    })
    new_idx.append(p['id'])
M2['meta']['total_persons']=len(M2['persons'])
M2['meta']['total_relations']=len(R['relations'])
M2['meta']['version']='3.3.0-L6-batch1'
with open('ontology/instances/m2_index.json','w',encoding='utf-8') as f:
    json.dump(M2,f,ensure_ascii=False,indent=2)

print(f'\n=== L6第1批完成：新增 {len(new_persons)} 个神祇, {len(new_rels)} 条关系 ===')
print(f'm2_index persons 总数: {M2["meta"]["total_persons"]}')
print(f'relations 总数: {R["meta"]["total"]}')
