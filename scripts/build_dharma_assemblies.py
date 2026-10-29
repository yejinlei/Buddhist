#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于抽取结果构建 DharmaAssembly 实例：
- 生成 ontology/dharma_assemblies.json  （法会实例索引）
- 在每部经的 ontology/instances/<sid>.json 增加 dharma_assembly 字段（通过分片合并写入）
- 不改动经文正文，仅添加事件层实例和关联。
"""
import json, os, glob, re, shutil
from collections import defaultdict

RAW = 'ontology/dharma_assemblies_raw.json'
SHARD_DIR = 'ontology/instances/shards'
OUT = 'ontology/dharma_assemblies.json'
INSTANCES_OUT_DIR = 'ontology/instances/shards'

# 经典法会的标准信息（以经文原文为依据，避免编造）
CLASSIC_ASSEMBLIES = {
    'shewei_jishu': {
        'id': 'da:shewei_jishu',
        'name': '舍卫国祇树给孤独园法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '舍卫国祇树给孤独园（祇园精舍）',
        'buddha': '释迦牟尼佛',
        'description': '佛陀在舍卫国祇树给孤独园说法之会，是佛在人间说法最频繁的道场，《金刚经》《阿弥陀经》等多部经典均在此宣说。',
        'canonical_sutras': ['t0235','t0366','t0001'],
        'significance': '佛在人间说法最主要的道场之一，涵盖般若、净土、阿含等多类经典。',
    },
    'shewei_shituolin': {
        'id': 'da:shewei_shituolin',
        'name': '舍卫国逝多林给孤独园法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '舍卫国逝多林给孤独园（祇园精舍的异译）',
        'buddha': '释迦牟尼佛',
        'description': '即祇树给孤独园，为玄奘译本常用译名，如《称赞净土佛摄受经》等。',
        'canonical_sutras': ['t0367'],
        'significance': '同祇树给孤独园。',
    },
    'wangshe_lingjiu': {
        'id': 'da:wangshe_lingjiu',
        'name': '王舍城耆阇崛山法会（灵鹫山法会）',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '王舍城耆阇崛山（灵鹫山）',
        'buddha': '释迦牟尼佛',
        'description': '佛陀在王舍城耆阇崛山（灵鹫山）宣说大乘经典之会，《法华经》《大般若经》《无量寿经》等均在此宣说。',
        'canonical_sutras': ['t0262','t0220','t0223','t0360'],
        'significance': '大乘经典主要说法处之一，与祇园并称两大主要法会地。',
    },
    'wangshe_zhulinyuan': {
        'id': 'da:wangshe_zhulinyuan',
        'name': '王舍城迦兰陀竹园法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '王舍城迦兰陀竹园',
        'buddha': '释迦牟尼佛',
        'description': '佛陀在王舍城迦兰陀竹园说法之会，为早期僧团重要精舍。',
        'canonical_sutras': [],
        'significance': '佛在王舍城最早的精舍之一，诸多阿含经典在此宣说。',
    },
    'wangshe': {
        'id': 'da:wangshe',
        'name': '王舍城法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '王舍城',
        'buddha': '释迦牟尼佛',
        'description': '佛陀在王舍城各处宣说之法会（未明指具体地点者归此）。',
        'canonical_sutras': [],
        'significance': '摩竭提国首都，佛陀长期驻锡说法之地。',
    },
    'pi ye li_anluo': {
        'id': 'da:piye_anluo',
        'name': '毗耶离庵罗树园法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '毗耶离庵罗树园',
        'buddha': '释迦牟尼佛',
        'description': '佛陀在毗耶离城庵罗树园说法之会，《维摩诘经》在此宣说。',
        'canonical_sutras': ['t0475'],
        'significance': '维摩诘居士示疾说法处。',
    },
    'pi_ye_li': {
        'id': 'da:piyeli',
        'name': '毗耶离城法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '毗耶离城',
        'buddha': '释迦牟尼佛',
        'description': '佛陀在毗耶离城内各处宣说之法会。',
        'canonical_sutras': [],
        'significance': '跋祇国首都，庵罗树园、猕猴池等均在城外。',
    },
    'boluonai_luyeyuan': {
        'id': 'da:boluonai',
        'name': '波罗奈国鹿野苑法会（初转法轮）',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '波罗奈国鹿野苑（仙人堕处施鹿林）',
        'buddha': '释迦牟尼佛',
        'description': '佛成道后在鹿野苑初转法轮，度五比丘说四圣谛八正道，为僧团建立之始。',
        'canonical_sutras': [],
        'significance': '初转法轮处，佛教僧团诞生地，四圣谛与八正道在此宣说。',
    },
    'jiushi_shuanglin': {
        'id': 'da:jiushi',
        'name': '拘尸那城娑罗双树间法会（涅槃法会）',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '拘尸那城力士生地阿夷罗跋提河边娑罗双树间',
        'buddha': '释迦牟尼佛',
        'description': '佛在拘尸那城娑罗双树间将入涅槃，最后宣说《大般涅槃经》《佛遗教经》等。',
        'canonical_sutras': ['t0374','t0375','t0389'],
        'significance': '佛涅槃处，最后遗教宣说地。',
    },
    'daoli_tiangong': {
        'id': 'da:daoli',
        'name': '忉利天宫法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '忉利天宫',
        'buddha': '释迦牟尼佛',
        'description': '佛陀上升忉利天为母摩耶夫人说法之会，《地藏菩萨本愿经》在此宣说。',
        'canonical_sutras': ['t0412','t0815'],
        'significance': '佛升天为母说法处，地藏法门源头。',
    },
    'guangyancheng_leyinshu': {
        'id': 'da:guangyan',
        'name': '广严城乐音树下法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '广严城乐音树下',
        'buddha': '释迦牟尼佛（薄伽梵）',
        'description': '佛陀游化广严城，在乐音树下宣说《药师琉璃光如来本愿功德经》。',
        'canonical_sutras': ['t0450'],
        'significance': '药师法门宣说地。',
    },
    'mojieti_potichang': {
        'id': 'da:poti',
        'name': '摩竭提国菩提树下法会（华严经最初成道会）',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '摩竭提国寂灭道场（菩提树下）',
        'buddha': '释迦牟尼佛',
        'description': '佛初成正觉，在菩提树下寂灭道场宣说《华严经》，为华严经七处九会之首。',
        'canonical_sutras': ['t0278','t0279'],
        'significance': '佛成道后华严大法会，七处九会之始。',
    },
    'jiaweiluowei': {
        'id': 'da:jiaweiluo',
        'name': '迦毗罗卫国法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '迦毗罗卫国（尼拘律园）',
        'buddha': '释迦牟尼佛',
        'description': '佛陀回故国迦毗罗卫为释迦族说法之会，包括尼拘律园等处。',
        'canonical_sutras': [],
        'significance': '佛陀故乡，回国为父族说法处。',
    },
    'jile_shijie': {
        'id': 'da:jile',
        'name': '极乐世界法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '西方极乐世界',
        'buddha': '阿弥陀佛',
        'description': '阿弥陀佛在极乐世界说法之会（他方佛国说法处）。',
        'canonical_sutras': [],
        'significance': '净土宗核心佛国，阿弥陀佛常宣妙法。',
    },
    'lengjia_shan': {
        'id': 'da:lengjia',
        'name': '南海楞伽山顶法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '南海滨楞伽山顶',
        'buddha': '释迦牟尼佛',
        'description': '佛陀在南海楞伽山顶宣说《楞伽经》。',
        'canonical_sutras': [],
        'significance': '楞伽经说法处，如来藏法系重要经源。',
    },
    'putuoluojia': {
        'id': 'da:putuo',
        'name': '补陀洛迦山观音道场法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '补陀洛迦山圣观自在菩萨宫中',
        'buddha': '释迦牟尼佛（或观音菩萨）',
        'description': '观世音菩萨在补陀洛迦山为众宣说密法等之会。',
        'canonical_sutras': [],
        'significance': '观音菩萨根本道场。',
    },
    'shewei_generic': {
        'id': 'da:shewei',
        'name': '舍卫国法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '舍卫国（未明指具体精舍）',
        'buddha': '释迦牟尼佛',
        'description': '佛陀在舍卫国各处宣说之法会（未指明祇树给孤独园/东园/鹿子母堂等具体处者归此）。',
        'canonical_sutras': [],
        'significance': '憍萨罗国首都，佛长期驻锡处。',
    },
    'mojieti_generic': {
        'id': 'da:mojieti',
        'name': '摩竭提国法会',
        'type': 'DharmaAssembly',
        'axis': 'A4', 'layer': 'L4',
        'place': '摩竭提国',
        'buddha': '释迦牟尼佛',
        'description': '佛陀在摩竭提国各处宣说之法会。',
        'canonical_sutras': [],
        'significance': '佛陀常行化之大国，含王舍城、伽耶、菩提场等多处圣地。',
    },
}

# place_norm -> 法会 id
PLACE_TO_DA = {
    '舍卫国祇树给孤独园': 'da:shewei_jishu',
    '舍卫国逝多林给孤独园': 'da:shewei_shituolin',
    '王舍城耆阇崛山（灵鹫山）': 'da:wangshe_lingjiu',
    '王舍城迦兰陀竹园': 'da:wangshe_zhulinyuan',
    '王舍城': 'da:wangshe',
    '毗耶离庵罗树园': 'da:piye_anluo',
    '毗耶离城': 'da:piyeli',
    '波罗奈国鹿野苑（初转法轮处）': 'da:boluonai',
    '波罗奈国': 'da:boluonai',
    '拘尸那城娑罗双树间（佛涅槃处）': 'da:jiushi',
    '拘尸那城': 'da:jiushi',
    '忉利天宫': 'da:daoli',
    '广严城乐音树下': 'da:guangyan',
    '广严城': 'da:guangyan',
    '摩竭提国寂灭道场（菩提树下成道处）': 'da:poti',
    '摩竭提国菩提树下': 'da:poti',
    '摩竭提国菩提场（菩提树下）': 'da:poti',
    '摩竭提国伽耶山（初成道处）': 'da:poti',
    '摩竭提国伽耶城': 'da:poti',
    '迦毗罗卫国': 'da:jiaweiluo',
    '迦毗罗卫国尼拘律园': 'da:jiaweiluo',
    '极乐世界': 'da:jile',
    '南海楞伽山顶（楞伽经说处）': 'da:lengjia',
    '补陀洛迦山（观音道场）': 'da:putuo',
    '舍卫国': 'da:shewei',
    '舍卫国东园鹿讲堂': 'da:shewei',
    '舍卫国迦利罗石室': 'da:shewei',
    '舍卫国迦利罗窟': 'da:shewei',
    '摩竭提国': 'da:mojieti',
    '摩竭提国伽耶山': 'da:poti',
}

def slugify_name(name):
    s = name.replace('(','').replace(')','').replace('（','').replace('）','')
    s = re.sub(r'[^0-9A-Za-z\u4e00-\u9fff]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s[:40]

def main():
    raw = json.load(open(RAW))

    # 第一步：聚合每处法会下的经文
    da_sutras = defaultdict(list)
    da_place_known = {}  # da_id -> place_norm
    other_places = defaultdict(list)  # 未归类的 place_norm -> [(sid,title)]
    for sid,v in raw.items():
        p = v.get('place_norm','')
        if not p: continue
        da_id = PLACE_TO_DA.get(p)
        if da_id:
            da_sutras[da_id].append((sid,v['title']))
            da_place_known[da_id] = p
        else:
            other_places[p].append((sid,v['title']))

    # 第二步：为未归类的地点自动生成法会实例（只对有2部及以上经的）
    auto_das = {}
    for p,lst in other_places.items():
        if len(lst) < 2: continue
        if p in ('(不明地点)','大眾中','日前分','至','」','某處說某經教'): continue
        slug = slugify_name(p)
        da_id = f'da:{slug}'
        auto_das[da_id] = {
            'id': da_id,
            'name': f'{p}法会',
            'type': 'DharmaAssembly',
            'axis': 'A4', 'layer': 'L4',
            'place': p,
            'buddha': '释迦牟尼佛',
            'description': f'佛陀在{p}宣说之法会。',
            'canonical_sutras': [],
            'significance': '依经文序分所记地点归组。',
            'auto_generated': True,
        }
        da_sutras[da_id] = lst
        PLACE_TO_DA[p] = da_id

    # 合并所有法会
    assemblies = {}
    for da_id, info in CLASSIC_ASSEMBLIES.items():
        assemblies[info['id']] = dict(info)
    for da_id, info in auto_das.items():
        assemblies[da_id] = info

    # 关联经文
    for da_id, lst in da_sutras.items():
        if da_id not in assemblies: continue
        # 合并（去重）
        cur = set(assemblies[da_id].get('sutras', []))
        cur.update(sid for sid,_ in lst)
        for sid in assemblies[da_id].get('canonical_sutras',[]):
            cur.add(sid)
        assemblies[da_id]['sutras'] = sorted(cur)
        assemblies[da_id]['sutra_count'] = len(cur)

    # 第三步：更新 ontology/instances 分片，给每部经加 dharma_assembly 字段
    # 建立 sid -> da_id
    sid2da = {}
    for sid,v in raw.items():
        p = v.get('place_norm','')
        da_id = PLACE_TO_DA.get(p)
        if da_id:
            sid2da[sid] = da_id

    modified = 0
    for sp in sorted(glob.glob(os.path.join(SHARD_DIR, 'shard-*.json'))):
        shard = json.load(open(sp))
        changed = False
        for sid, inst in shard.items():
            if sid in sid2da:
                if inst.get('dharma_assembly') != sid2da[sid]:
                    inst['dharma_assembly'] = sid2da[sid]
                    changed = True
                    modified += 1
        if changed:
            json.dump(shard, open(sp,'w',encoding='utf-8'), ensure_ascii=False, indent=2)

    # 输出 assemblies 索引
    out = {
        'version': '3.0.0-m4',
        'type': 'DharmaAssemblyIndex',
        'description': 'M4 事件层·法会实例（DharmaAssembly）',
        'total': len(assemblies),
        'sutras_linked': len(sid2da),
        'assemblies': assemblies,
    }
    json.dump(out, open(OUT,'w',encoding='utf-8'), ensure_ascii=False, indent=2)

    print(f'生成法会实例：{len(assemblies)} 个（经典 {len(CLASSIC_ASSEMBLIES)} + 自动聚合 {len(auto_das)}）')
    print(f'已关联经文：{len(sid2da)} 部（实例已写入分片 dharma_assembly 字段，共更新 {modified} 条）')
    print()
    print('=== 经典法会 ===')
    for da_id, info in CLASSIC_ASSEMBLIES.items():
        cnt = len(assemblies[info['id']].get('sutras',[]))
        print(f'  {info["name"]}：{cnt} 部经')
    print(f'\n=== 自动聚合法会（{len(auto_das)} 个，共含 {sum(len(v["sutras"]) for k,v in assemblies.items() if v.get("auto_generated"))} 部经）===')
    for da_id, info in sorted(auto_das.items(), key=lambda x:-len(assemblies[x[0]].get('sutras',[]))):
        cnt = len(assemblies[da_id].get('sutras',[]))
        print(f'  {info["name"]}：{cnt} 部经')

if __name__ == '__main__':
    main()
