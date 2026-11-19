#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二轮复核脚本 - 核查12部佛经白话译文"""

import json
import os
import re

BASE_DIR = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation"
SUTRA_IDS = ["t1159", "t2773", "t0757", "t1898", "t0566", "t1301", "t1141", "t1986b", "t1837", "t1664", "t1455", "t1560"]

issues = []

def check_sutra(sid):
    """核查单部经"""
    filepath = os.path.join(BASE_DIR, f"{sid}.json")
    if not os.path.exists(filepath):
        issues.append(f"[{sid}] 文件不存在")
        return
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    segments = data.get("translations", [])
    print(f"\n=== 核查 {sid} ({data.get('title', '未知标题')}) ===")
    print(f"  总段落数: {len(segments)}")
    
    # 通用检查项
    template_patterns = [
        r"此段为.*方得论旨",
        r"此段.*需.*结合上下文",
        r"待补译",
        r"待补充",
        r"待译",
    ]
    
    typo_patterns = [
        (r"涅盘", "涅槃"),
        (r"涅磐", "涅槃"),
    ]
    
    has_subtitle_issues = 0
    has_yijie_issues = 0
    has_template = 0
    has_typo = 0
    has_literal_newline = 0
    
    for i, seg in enumerate(segments):
        modern = seg.get("modern", "")
        orig = seg.get("original_preview", "")
        
        # 1. 检查modern以【小标题】开头且为简体
        if not modern.startswith("【"):
            has_subtitle_issues += 1
            if has_subtitle_issues <= 3:
                issues.append(f"[{sid}] 段{i+1}: modern不以【开头，内容开头为: {modern[:30]}")
        
        # 检查是否包含繁体（简单检查，小标题应为简体）
        # 检查第一个】前的小标题
        subtitle_match = re.match(r"【([^】]+)】", modern)
        if subtitle_match:
            subtitle = subtitle_match.group(1)
            # 常见繁体字符检查
            traditional_chars = "體無爲從來國會開關說話問對這那個麼麼後發裏與長"
            for c in traditional_chars:
                if c in subtitle:
                    issues.append(f"[{sid}] 段{i+1}: 小标题可能含繁体字符'{c}': {subtitle}")
                    break
        
        # 2. 检查含【义解】且后面有充分白话正文
        if "【义解】" in modern:
            after_yijie = modern.split("【义解】", 1)[1].strip()
            if len(after_yijie) < 20:
                has_yijie_issues += 1
                if has_yijie_issues <= 3:
                    issues.append(f"[{sid}] 段{i+1}: 【义解】后内容过短({len(after_yijie)}字): {after_yijie[:50]}")
        else:
            # 不要求每段都有义解，但应该有实质内容
            pass
        
        # 3. 检查错字
        for pattern, correct in typo_patterns:
            if re.search(pattern, modern):
                has_typo += 1
                if has_typo <= 5:
                    issues.append(f"[{sid}] 段{i+1}: 疑似错字，应为'{correct}': {modern[max(0, modern.find(pattern)-10):modern.find(pattern)+20]}")
        
        # 4. 检查模板套话残留
        for pat in template_patterns:
            if re.search(pat, modern):
                has_template += 1
                issues.append(f"[{sid}] 段{i+1}: 模板套话残留 /{pat}/: {modern[:80]}")
                break
        
        # 5. 检查t1301换行符 - 检查是否有字面量\n
        if sid == "t1301":
            if "\\n" in modern:
                has_literal_newline += 1
                if has_literal_newline <= 3:
                    issues.append(f"[{sid}] 段{i+1}: 包含字面量\\n而非真正换行")
    
    # 输出通用检查结果
    if has_subtitle_issues > 0:
        issues.append(f"[{sid}] 共{has_subtitle_issues}段modern格式不以【开头")
    if has_yijie_issues > 0:
        issues.append(f"[{sid}] 共{has_yijie_issues}段【义解】后内容过短")
    if has_template > 0:
        issues.append(f"[{sid}] 共{has_template}段存在模板套话残留")
    if has_typo > 0:
        issues.append(f"[{sid}] 共{has_typo}处疑似错字")
    if sid == "t1301" and has_literal_newline > 0:
        issues.append(f"[{sid}] 共{has_literal_newline}段存在字面量\\n问题")
    
    # ===== 专项检查 =====
    
    # t1837: 确认138段全部有实质翻译内容，法相术语准确
    if sid == "t1837":
        print(f"  [专项] t1837《大乘百法明门论疏》检查...")
        if len(segments) < 138:
            issues.append(f"[t1837] 段落数不足138，仅{len(segments)}段")
        else:
            print(f"  [专项] 段落数{len(segments)}，符合预期")
        
        # 检查关键术语
        key_terms = ["五位百法", "八识", "人无我", "法无我", "心法", "心所法", "色法", "心不相应行法", "无为法"]
        found_terms = set()
        for seg in segments:
            modern = seg.get("modern", "")
            for t in key_terms:
                if t in modern:
                    found_terms.add(t)
        missing_terms = set(key_terms) - found_terms
        if missing_terms:
            issues.append(f"[t1837] 缺少关键法相术语: {missing_terms}")
        else:
            print(f"  [专项] 关键法相术语齐全")
        
        # 检查是否有过短内容（<50字的modern可能是模板）
        short_count = 0
        for i, seg in enumerate(segments):
            modern = seg.get("modern", "").strip()
            if len(modern) < 50:
                short_count += 1
                if short_count <= 5:
                    issues.append(f"[t1837] 段{i+1}: 内容过短({len(modern)}字): {modern[:60]}")
        if short_count > 5:
            issues.append(f"[t1837] 共{short_count}段内容过短，疑似未实质翻译")
    
    # t1986b: 确认96段已补译，宝镜三昧、五位君臣等核心内容准确
    if sid == "t1986b":
        print(f"  [专项] t1986b《洞山良价语录》检查...")
        # 检查核心内容
        key_terms = ["宝镜三昧", "五位君臣", "公案", "机锋", "正中偏", "偏中正", "正中来", "偏中至", "兼中到"]
        found_terms = set()
        for seg in segments:
            modern = seg.get("modern", "")
            for t in key_terms:
                if t in modern:
                    found_terms.add(t)
        missing_terms = set(key_terms) - found_terms
        if missing_terms:
            issues.append(f"[t1986b] 缺少核心内容术语: {missing_terms}")
        else:
            print(f"  [专项] 核心术语齐全")
        
        # 统计之前是模板的段落是否已补译 - 检查内容长度
        short_count = 0
        for i, seg in enumerate(segments):
            modern = seg.get("modern", "").strip()
            if len(modern) < 50:
                short_count += 1
                if short_count <= 10:
                    issues.append(f"[t1986b] 段{i+1}: 内容过短({len(modern)}字): {modern[:60]}")
        if short_count > 10:
            issues.append(f"[t1986b] 共{short_count}段内容过短，疑似未补译完成")
        else:
            print(f"  [专项] 仅{short_count}段内容偏短，补译基本完成")
    
    # t1141: 确认五轮配指注释一致正确，小标题已是简体
    if sid == "t1141":
        print(f"  [专项] t1141《慈氏菩萨略修瑜伽念诵法》检查...")
        # 五轮配指：地=小指、水=无名指、火=中指、风=食指/风幢、空=大拇指
        wuxing_mappings = {
            "地": ["小指"],
            "水": ["无名指"],
            "火": ["中指"],
            "风": ["食指", "风幢"],
            "空": ["大拇指", "拇指"],
        }
        
        # 检查五轮相关段落
        wuxing_segments = []
        for i, seg in enumerate(segments):
            modern = seg.get("modern", "")
            orig = seg.get("original_preview", "")
            # 找提到五轮、地水火风空+指的段落
            if ("地轮" in modern or "水轮" in modern or "火轮" in modern or "风轮" in modern or "空轮" in modern) and ("指" in modern):
                wuxing_segments.append((i+1, modern))
        
        print(f"  [专项] 找到{len(wuxing_segments)}段五轮配指相关内容")
        
        # 检查是否有配错的
        # 地轮对应小指，检查是否有错误配对
        wrong_mappings = []
        for seg_num, modern in wuxing_segments:
            # 检查地轮
            if "地轮" in modern:
                if "无名指" in modern and "小指" not in modern:
                    wrong_mappings.append(f"段{seg_num}: 地轮配无名指错误，应配小指")
                if "中指" in modern and "小指" not in modern:
                    wrong_mappings.append(f"段{seg_num}: 地轮配中指错误，应配小指")
            # 检查水轮
            if "水轮" in modern:
                if "小指" in modern and "无名指" not in modern:
                    wrong_mappings.append(f"段{seg_num}: 水轮配小指错误，应配无名指")
                if "中指" in modern and "无名指" not in modern:
                    wrong_mappings.append(f"段{seg_num}: 水轮配中指错误，应配无名指")
            # 检查火轮
            if "火轮" in modern:
                if "无名指" in modern and "中指" not in modern:
                    wrong_mappings.append(f"段{seg_num}: 火轮配无名指错误，应配中指")
                if "食指" in modern and "中指" not in modern:
                    wrong_mappings.append(f"段{seg_num}: 火轮配食指错误，应配中指")
            # 检查风轮
            if "风轮" in modern:
                if "中指" in modern and "食指" not in modern and "风幢" not in modern:
                    wrong_mappings.append(f"段{seg_num}: 风轮配中指错误，应配食指/风幢")
                if "大拇指" in modern and "食指" not in modern and "风幢" not in modern:
                    wrong_mappings.append(f"段{seg_num}: 风轮配大拇指错误，应配食指/风幢")
            # 检查空轮
            if "空轮" in modern:
                if "食指" in modern and "大拇指" not in modern and "拇指" not in modern:
                    wrong_mappings.append(f"段{seg_num}: 空轮配食指错误，应配大拇指")
        
        if wrong_mappings:
            for w in wrong_mappings[:10]:
                issues.append(f"[t1141] 五轮配指错误: {w}")
        else:
            print(f"  [专项] 五轮配指注释未发现错误")
        
        # 检查小标题繁体
        trad_subtitle_count = 0
        traditional_chars = "體無爲從來國會開關說話問對這那個麼麼後發裏與長修瑜伽念誦法輪"
        for i, seg in enumerate(segments):
            modern = seg.get("modern", "")
            subtitle_match = re.match(r"【([^】]+)】", modern)
            if subtitle_match:
                subtitle = subtitle_match.group(1)
                for c in traditional_chars:
                    if c in subtitle:
                        trad_subtitle_count += 1
                        if trad_subtitle_count <= 5:
                            issues.append(f"[t1141] 段{i+1}: 小标题含繁体'{c}': {subtitle}")
                        break
        if trad_subtitle_count > 0:
            issues.append(f"[t1141] 共{trad_subtitle_count}个小标题含繁体字符")
        else:
            print(f"  [专项] 小标题均为简体")
    
    # t1301: 换行符检查（已在通用检查中做了字面量\n检查，这里再确认格式）
    if sid == "t1301":
        print(f"  [专项] t1301 换行符格式检查...")
        if len(segments) > 0:
            # 抽查几段看换行是否正确
            check_indices = [0, len(segments)//4, len(segments)//2, 3*len(segments)//4, len(segments)-1]
            check_indices = [i for i in check_indices if 0 <= i < len(segments)]
            for i in check_indices:
                seg = segments[i]
                modern = seg.get("modern", "")
                if "\n" in modern:
                    # 有真正换行，是好的
                    pass
                # 检查是否有连续多个\n（格式问题）
                if "\n\n\n" in modern:
                    issues.append(f"[t1301] 段{i+1}: 存在过多连续换行")
        print(f"  [专项] 换行格式检查完成")
    
    # 检查咒文/梵文是否被误译（检查是否有"娑婆诃"被译成其他等，主要确保常见梵文咒文保留原字）
    # 这里简单检查：原文有梵文/咒文特征时，modern中是否保留了原字
    mantra_indicators = ["吽", "唵", "娑婆诃", "娑诃", "莎诃", "怛侄他", "曩莫", "南无"]
    mantra_issues = 0
    for i, seg in enumerate(segments):
        orig = seg.get("original_preview", "")
        modern = seg.get("modern", "")
        # 如果原文有咒文特征词，modern中也应该保留
        for ind in mantra_indicators:
            if ind in orig and ind not in modern:
                # 可能是被翻译了，需要记录
                mantra_issues += 1
                if mantra_issues <= 5:
                    issues.append(f"[{sid}] 段{i+1}: 原文含咒文/梵文'{ind}'但译文未保留原字")
                break

# 逐个核查
for sid in SUTRA_IDS:
    check_sutra(sid)

# 输出结果
print("\n" + "="*60)
print("复核结果汇总:")
print("="*60)
if issues:
    print(f"共发现 {len(issues)} 个问题:")
    for idx, issue in enumerate(issues, 1):
        print(f"{idx}. {issue}")
else:
    print("恭喜！所有检查项通过，未发现问题。")
