#!/usr/bin/env python3
"""第103批 P2 精细修复"""
import json, re

PROJECT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
kids = 't1001 t0162 t2873 t2886 t1102 t0905 t1203 t1905 t0911 t1105 t0076 t0972'.split()

def clean_mess(m):
    """彻底清理【义解">【义解"> 及嵌套问题"""
    # 多次替换直到稳定
    for _ in range(5):
        orig = m
        m = m.replace('【义解">', '【义解】')
        m = m.replace('【义解\">', '【义解】')
        m = m.replace('">', '')
        m = re.sub(r'【义解】\s*【义解】', '【义解】', m)
        # 模式：【经文内容】【义解】【XXX】【义解】正文 → 【XXX】【义解】正文
        m = re.sub(r'【经文内容】【义解】\s*【([^】]+)】【义解】\s*', r'【\1】【义解】', m)
        m = re.sub(r'【经文要义】【义解】\s*【([^】]+)】【义解】\s*', r'【\1】【义解】', m)
        if m == orig:
            break
    return m

for kid in kids:
    fp = f'{PROJECT}/data/modern-translation/{kid}.json'
    with open(fp, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    
    # t1203: 重写33-40段的小标题以匹配其内容（根据preview内容匹配方位）
    if kid == 't1203':
        # 各段preview前10字
        titles_for_1203 = {}
        for i, seg in enumerate(obj['translations']):
            pv = seg['original_preview']
            if '東行' in pv[:40] and '天帝釋' in pv[:80]:
                titles_for_1203[i] = '东方帝释旗'
            elif '東南' in pv[:60] and '火' in pv[:60] and '焰摩' in pv:
                titles_for_1203[i] = '东南火天旗'
            elif '南方' in pv[:60] and '閻' in pv[:60]:
                titles_for_1203[i] = '南方焰摩旗'
            elif '西南' in pv[:60] and '羅剎' in pv:
                titles_for_1203[i] = '西南罗刹旗'
            elif '西方' in pv[:60] and '水天' in pv[:60] and '龜' in pv[:80]:
                titles_for_1203[i] = '西方水天旗'
            elif '西北' in pv[:60] and '風天' in pv[:60]:
                titles_for_1203[i] = '西北风天旗'
            elif '北方' in pv[:60] and '毘沙門' in pv:
                titles_for_1203[i] = '北方毗沙门旗'
            elif '東北' in pv[:60] and '伊舍' in pv:
                titles_for_1203[i] = '东北伊舍那旗'
        # 应用
        for i, title in titles_for_1203.items():
            m = obj['translations'][i]['modern']
            # 替换段首小标题
            m = re.sub(r'^【[^】]*】', f'【{title}】', m, count=1)
            obj['translations'][i]['modern'] = m
        print(f't1203: 重写{len(titles_for_1203)}段方位小标题')
    
    # t1102: 清理草稿残留（找所有带「不对」「？哦」「应该是」的段）
    if kid == 't1102':
        for i, seg in enumerate(obj['translations']):
            m = seg['modern']
            if '？不对' in m or '？哦' in m or '不对，应该是' in m or '哦原文明明' in m:
                # 定位是哪段印相
                pv = seg['original_preview']
                if '檀慧禪智' in pv or '極喜' in pv or '俱摩羅' in pv:
                    # 极喜三昧印段（檀慧禅智竖相著）
                    m = '【极喜三昧印】【义解】再结极喜三昧的印相：双手先结坚固金刚缚，将檀（拇指）、慧（小指）、禅（无名指）、智（食指）四指竖直相靠，中指（忍辱愿）向内交叉相合，这就是极喜三昧印。'
                    obj['translations'][i]['modern'] = m
                    print(f'  t1102[{i}] 清理草稿')
    
    # t1905: 删除译者计数注释
    if kid == 't1905':
        for i, seg in enumerate(obj['translations']):
            m = seg['modern']
            if '注：原文是十条' in m or '第十一条（注：' in m:
                m = re.sub(r'第十一条（注：原文是十条，应是四药过限为第十条）', '第十一条', m)
                m = re.sub(r'\(注：原文是十条，应是四药过限为第十条\)', '', m)
                obj['translations'][i]['modern'] = m
                print(f'  t1905[{i}] 清理译者注释')
    
    # t0905: 名色译反 再扫描
    if kid == 't0905':
        for i, seg in enumerate(obj['translations']):
            m = seg['modern']
            if '名就是四大、五根' in m:
                m = m.replace('名就是四大、五根（色法），色就是想、行等四阴（心法）',
                              '色就是四大、五根（色法），名就是想、行等四阴（心法）')
                obj['translations'][i]['modern'] = m
                print(f'  t0905[{i}] 名色译反修复')
            if '览、唅、欠' in m or '阿鑁览' in m:
                m = m.replace('阿、鑁、览、唅、欠', '阿、鑁、藍、唅、欠').replace('阿鑁览唅欠', '阿鑁藍唅欠')
                obj['translations'][i]['modern'] = m
                print(f'  t0905[{i}] 藍字修复')
    
    # 统一清理
    for i, seg in enumerate(obj['translations']):
        m = seg['modern']
        m = clean_mess(m)
        # 确保开头格式
        if not re.match(r'^【[^】]{1,12}】【义解】', m):
            # 如果开头是【XX】但没有【义解】紧跟
            m = re.sub(r'^【([^】]{1,12})】\s*', r'【\1】【义解】', m, count=1)
            if not m.startswith('【'):
                m = '【经文要义】【义解】' + m
        seg['modern'] = m
    
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

print("=== phase 2 done ===")
