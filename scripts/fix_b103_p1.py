#!/usr/bin/env python3
"""第103批批量修正脚本 - 三路校对问题修复"""
import json, re, os
from opencc import OpenCC

cc = OpenCC('t2s')

PROJECT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
kids = 't1001 t0162 t2873 t2886 t1102 t0905 t1203 t1905 t0911 t1105 t0076 t0972'.split()

def fix_modern(kid, idx, modern):
    """逐段修复modern，返回修正后的modern"""
    m = modern

    # === 通用修复：清理【义解"> 残留 ===
    m = m.replace('【义解">', '【义解】')
    m = m.replace('【义解\">', '【义解】')
    
    # === 通用修复：清理【段落X】占位标签 ===
    m = re.sub(r'【段落\d+】', '', m)
    
    # === t0162, t2873 的双【义解】问题：【义解】【小标题】【义解"> → 【小标题】【义解】 ===
    # 匹配形如 【义解】【XXX】【义解】 并重组
    m = re.sub(r'【义解】\s*【([^】]+)】\s*【义解】\s*', r'【\1】【义解】', m)
    m = re.sub(r'【义解】\s*【([^】]+)】\s*【义解[">]+\s*', r'【\1】【义解】', m)
    
    # === 特殊处理：如果开头直接是【义解】而没有【小标题】，加一个 ===
    if m.startswith('【义解】'):
        m = '【经文内容】' + m
    
    # === 经号特定修复 ===
    if kid == 't1102':
        # 段13（索引13，0-based=13？先找草稿残留特征）
        if '禅？不对' in m or '？哦' in m or '？不对' in m:
            # 这是混入草稿的段，替换为正确印相
            m = re.sub(r'【[^】]*】【义解】[^。]*禅[？?].*?竖起来互相靠着[。.]?',
                      '【极喜三昧印】【义解】双手结坚固金刚缚，中指（忍辱）、无名指（愿）向内交叉相合，拇指（檀）、小指（慧）、食指（智）竖直相靠，这就是极喜三昧的印相。', m)
            if '无名指（禅）和食指（智）？不对' in m:
                m = m.replace('双手（定慧二羽）紧紧缚成坚固金刚缚，将中指（忍辱）和无名指（愿）在中间交叉相合，拇指（檀）、小指（慧）、无名指（禅）、食指（智）竖直互相靠住。',
                              '双手结坚固金刚缚，中指（忍辱）、无名指（愿）向内交叉相合，拇指（檀）、小指（慧）、食指（智）竖直相靠。')
        # 段61（index around 60）指位错译 - 找「食指（进）、中指（力）抵在无名指（禅）、小指（慧）上」相关
        # 不做强行改动，靠复核处理
    
    if kid == 't0905':
        # 藍→览 错字修复（种子字中）
        m = m.replace('阿、鑁、览、唅、欠', '阿、鑁、藍、唅、欠')
        m = m.replace('阿鑁览唅欠', '阿鑁藍唅欠')
        # 名色译反 - 找 "名就是四大、五根" 模式
        m = m.replace('名就是四大、五根（色法），色就是想、行等四阴（心法）',
                      '色就是四大、五根（色法），名就是想、行等四阴（心法）')
    
    # === 小标题简体化：抽取开头的【小标题】部分用OpenCC转换，咒文/原文部分保留 ===
    # 匹配开头的【XXX】
    title_match = re.match(r'^【([^】]+)】【义解】(.*)', m, re.DOTALL)
    if title_match:
        title = title_match.group(1)
        body = title_match.group(2)
        # 小标题整体转简体（佛、菩萨、经、咒、陀罗尼等也会转，这是允许的-人名/专名里的常见字转简体可）
        title_s = cc.convert(title)
        m = f'【{title_s}】【义解】{body}'
    else:
        # 开头没有小标题？补一个【经文要义】
        if not m.startswith('【'):
            m = '【经文要义】【义解】' + m
        else:
            # 可能格式有问题，尝试修复
            m = re.sub(r'^【([^】]+)】\s*', r'【\1】【义解】', m, count=1)
            if '【义解】' not in m[:30]:
                m = re.sub(r'^【([^】]+)】', r'【\1】【义解】', m)
    
    return m


def is_mantra_paragraph(preview):
    """判断是否是纯/主要咒文段 - 含大量梵字/真言/二合引反切"""
    mantra_markers = ['真言曰', '明曰', '呪曰', '陀罗尼曰', '二合', '反', '引）', '引」', '引，', '曩莫', '娑嚩', '莎訶', '娑嚩贺', '唵', '怛他', '娑婆']
    n_marker = sum(1 for mk in mantra_markers if mk in preview)
    # 有种子字/梵文PUA
    n_pua = sum(1 for c in preview if (0xF000 <= ord(c) <= 0xF8FF) or (0xF0000 <= ord(c) <= 0xFFFFD))
    return n_marker >= 2 or n_pua >= 3

for kid in kids:
    fp = f'{PROJECT}/data/modern-translation/{kid}.json'
    with open(fp, 'r', encoding='utf-8') as f:
        obj = json.load(f)
    fixed_count = 0
    for i, seg in enumerate(obj['translations']):
        old = seg['modern']
        preview = seg['original_preview']
        new = fix_modern(kid, i, old)
        
        # === 说明文字简体化：非咒文段、非引原文段的白话说明用 OpenCC 转简体，但要保留特定原字 ===
        if not is_mantra_paragraph(preview):
            # 整体转简体，再还原需要保留的音译字/繁体
            new = cc.convert(new)
            # 注意：但是咒文中的原字必须保留——咒文是从original_preview照录的，它们仍应是原繁体
            # 如果 new 中包含「真言曰：」或「明曰：」，冒号/引号后到结尾的部分需要恢复 preview 中的原字形
            # 简单做法：用正则找出「真言曰：「...」」「明曰：「...」」「陀罗尼曰：「...」」区间，
            # 从preview中抠出对应原文回填
            for mk in ['真言曰', '明曰', '呪曰', '陀罗尼曰', '咒曰', '明曰：']:
                pattern = re.compile(r'(' + mk + r'[：:])([「"])(.*?)([」"])', re.DOTALL)
                # 找到preview中对应的位置
                pv_idx = preview.find(mk)
                if pv_idx >= 0:
                    # 取 preview 中 mk 之后的引语部分（直到下一个 」/引号）
                    pv_after = preview[pv_idx + len(mk):]
                    # 跳过冒号、引号、空格、换行
                    pv_stripped = pv_after.lstrip('：:「『『“ \n　')
                    # 寻找结尾 」
                    end_idx = pv_stripped.find('」')
                    if end_idx < 0:
                        end_idx = pv_stripped.find('"')
                    if end_idx < 0:
                        end_idx = len(pv_stripped)
                    pv_mantra = pv_stripped[:end_idx]
                    # 在 new 中替换：mk：「XXX」 中的 XXX 为 pv_mantra（只替换mk后第一个引号块）
                    def repl_mantra(match, pv_m=pv_mantra):
                        return match.group(1) + '「' + pv_m + '」'
                    new = pattern.sub(repl_mantra, new, count=1)
        
        # 验证格式：开头是【小标题】【义解】
        if not re.match(r'^【[^】]+】【义解】', new):
            # 再补一次
            if new.startswith('【义解】'):
                new = '【经文要义】' + new
            elif not new.startswith('【'):
                new = '【经文要义】【义解】' + new
            else:
                # 确保有【义解】
                new = re.sub(r'^【([^】]+)】', r'【\1】【义解】', new, count=1)
        
        seg['modern'] = new
        if new != old:
            fixed_count += 1
    
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(f'{kid}: fixed {fixed_count} segs, total {len(obj["translations"])}')
print("=== phase 1 done ===")
