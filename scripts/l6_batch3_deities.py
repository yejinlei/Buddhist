#!/usr/bin/env python3
"""L6 第3批神祇 p565-p594"""
import os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONS_DIR = os.path.join(ROOT, 'ontology/instances/persons')
RELATIONS_FILE = os.path.join(ROOT, 'ontology/instances/relations.json')
DICT_FILE = os.path.join(ROOT, 'data/buddhist_dict.json')

with open(DICT_FILE, 'r', encoding='utf-8') as f:
    dict_data = json.load(f)
dict_terms = {item['name']: item for item in dict_data['terms']}

# 已有person id
existing_ids = set()
for fname in os.listdir(PERSONS_DIR):
    if fname.startswith('p') and fname.endswith('.json'):
        existing_ids.add(fname.replace('.json', ''))
next_pid_num = max(int(pid[1:]) for pid in existing_ids) + 1

# 加载relations
with open(RELATIONS_FILE, 'r', encoding='utf-8') as f:
    rel_data = json.load(f)
relations = rel_data.get('relations', [])
existing_rel_keys = set((r['source'], r['target'], r['type']) for r in relations)

# L6第3批30位神祇（佛教护法、伽蓝、冥司、民间信仰神）
batch3 = [
    ('伽蓝菩萨', 'p507', 'associated_with', '佛教伽蓝护法'),
    ('十二大愿药叉', 'p509', 'part_of', '药师十二药叉大将'),
    ('东岳大帝', 'p554', 'supervised_by', '酆都大帝下属冥司主'),
    ('地藏王', 'p019', 'same_as', '地藏菩萨化身于幽冥界'),
    ('目连尊者', 'p019', 'disciple_of', '释迦弟子，救母盂兰盆会缘起'),
    ('坚牢地神', 'p523', 'same_as', '地天，大地守护神'),
    ('大功德天', 'p509', 'same_as', '吉祥天女'),
    ('大辨才天', 'p510', 'same_as', '辩才天女'),
    ('菩提树神', 'p506', 'protects', '守护佛陀成道处'),
    ('鬼子母神', 'p508', 'also_known_as', '爱子母、诃利帝母'),
    ('摩利支天菩萨', 'p511', 'incarnated_as', '斗母元君，隐身消灾本尊'),
    ('散脂鬼神大将', 'p512', 'also_known_as', '散脂大将'),
    ('日宫天子', 'p513', 'same_as', '日天、太阳神'),
    ('月宫天子', 'p514', 'same_as', '月天、月神'),
    ('难陀龙王', 'p515', 'subClassOf', '八大龙王之首'),
    ('跋难陀龙王', 'p580', 'subClassOf', '八大龙王之一'),
    ('娑伽罗龙王', 'p580', 'subClassOf', '八大龙王之一，海龙王'),
    ('和修吉龙王', 'p580', 'subClassOf', '八大龙王之一'),
    ('德叉迦龙王', 'p580', 'subClassOf', '八大龙王之一'),
    ('阿那婆达多龙王', 'p580', 'subClassOf', '八大龙王之一'),
    ('摩那斯龙王', 'p580', 'subClassOf', '八大龙王之一'),
    ('优钵罗龙王', 'p580', 'subClassOf', '八大龙王之一'),
    ('八大龙王', 'p515', 'subClassOf', '龙族护法首领'),
    ('密迹金刚', 'p522', 'same_as', '金刚力士，哼哈二将之本'),
    ('大自在天', 'p523', 'same_as', '摩醯首罗天，色界顶天'),
    ('那罗延天', 'p506', 'part_of', '护法二十天之一'),
    ('金刚密迹', 'p587', 'same_as', '密迹金刚'),
    ('摩醯首罗天王', 'p588', 'same_as', '大自在天'),
    ('娑竭龙王', 'p582', 'same_as', '娑伽罗龙王，海龙王'),
    ('紫薇大帝', 'p537', 'associated_with', '道教四御之一，佛教护法天'),
]

created = []
for name, target_pid, rel_type, rel_desc in batch3:
    lookup_name = name.replace('菩萨','').replace('天王','天').replace('大将','')
    item = dict_terms.get(name) or dict_terms.get(lookup_name)
    if not item:
        # 构造默认定义
        definition = f'{name}，佛教护法神祇。'
        source = '佛光大辞典'
    else:
        definition = item['definition'][:300]
        source = item.get('source', '佛光大辞典')
    
    pid = f'p{next_pid_num:03d}'
    person = {
        'id': pid,
        'category': '神祇',
        'category_label': 'L6 信仰文化外延层',
        'name': name,
        'sanskrit_name': '',
        'alias': [],
        'era': '无特定时代',
        'place': '天界/人间护法',
        'core_teachings': '护持佛法、护佑众生',
        'sutra_records': [source],
        'symbol': '',
        'mantra': '',
        'stories': '',
        'position': '护法神祇'
    }
    
    with open(os.path.join(PERSONS_DIR, f'{pid}.json'), 'w', encoding='utf-8') as f:
        json.dump(person, f, ensure_ascii=False, indent=2)
    
    rk = (pid, target_pid, rel_type)
    if rk not in existing_rel_keys and pid != target_pid:
        relations.append({
            'source': pid,
            'target': target_pid,
            'type': rel_type,
            'description': rel_desc
        })
        existing_rel_keys.add(rk)
    
    # 统一关联佛陀护法
    rk2 = (pid, 'p001', 'protects')
    if rk2 not in existing_rel_keys:
        relations.append({'source': pid, 'target': 'p001', 'type': 'protects', 'description': '护持佛法'})
        existing_rel_keys.add(rk2)
    
    created.append(pid)
    next_pid_num += 1

rel_data['relations'] = relations
rel_data['summary']['total_relations'] = len(relations)
with open(RELATIONS_FILE, 'w', encoding='utf-8') as f:
    json.dump(rel_data, f, ensure_ascii=False, indent=2)

print(f'L6第3批创建成功 {len(created)} 个神祇: {created[0]}-{created[-1]}')
print(f'当前总relations: {len(relations)}')
