import json
import os
import re

sutra_ids = ["t1062b", "t1213", "t1072b", "t1177b", "t0944b", "t1120a", "t0966", "t1120", "t0854", "t0944", "t2133a", "t0860"]
issues = []

def is_half_width_punct(c):
    return (ord(c) >= 0x21 and ord(c) <= 0x7E) and not c.isalnum()

for sid in sutra_ids:
    path = f"data/modern-translation/{sid}.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    translations = data.get("translations", [])
    for idx, seg in enumerate(translations):
        seg_no = idx + 1
        orig = seg.get("original_preview", "").strip()
        modern = seg.get("modern", "").strip()
        
        # 1. 梵字（悉昙，所有非BMP字符ord>0xFFFF）对比
        orig_siddham = ''.join([c for c in orig if ord(c) > 0xFFFF])
        if '原文照录如下：\n' in modern:
            modern_text_part = modern.split('原文照录如下：\n')[-1]
        else:
            modern_text_part = modern
        modern_siddham = ''.join([c for c in modern_text_part if ord(c) > 0xFFFF])
        
        if len(orig_siddham) > 0:
            if orig_siddham != modern_siddham:
                min_len = min(len(orig_siddham), len(modern_siddham))
                diff_pos = -1
                for i in range(min_len):
                    if orig_siddham[i] != modern_siddham[i]:
                        diff_pos = i
                        break
                if diff_pos == -1:
                    issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：咒文梵字数量不一致，原文{len(orig_siddham)}字，译文{len(modern_siddham)}字，存在漏字或多字，修正建议：对照original_preview逐字核对梵字，补全漏字、删除多字")
                else:
                    issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：咒文第{diff_pos+1}个梵字与原文不一致，修正建议：对照original_preview修正该梵字错漏")
        
        # 2. 格式错误：双【义解】
        if modern.count('【义解】') > 1:
            issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：出现多个【义解】标签，修正建议：仅保留一个【义解】标签")
        
        # 半角标点
        half = []
        for c in modern:
            if is_half_width_punct(c):
                half.append(c)
        if half:
            uniq_half = list(sorted(set(half)))
            issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：存在半角标点{''.join(uniq_half)}，修正建议：全部替换为对应全角标点")
        
        # 提取说明文字（义解部分，原文照录前的内容；无梵字段落则全部为说明/译文）
        yijie_part = ""
        if "【义解】" in modern:
            parts = modern.split("【义解】", 1)[1]
            if "原文照录如下" in parts:
                yijie_part = parts.split("原文照录如下")[0]
            else:
                yijie_part = parts
        if len(orig_siddham) == 0:
            yijie_part = modern
        
        # 3. 说明文字简体（排除本身是简体的字：答、云、后（後的简体）、发、这些不要误判）
        fantizi_map = {
            '灑':'洒', '為':'为', '經':'经', '來':'来', '個':'个', '麼':'么', '這':'这',
            '裡':'里', '後':'后', '於':'于', '對':'对', '說':'说', '時':'时', '國':'国',
            '會':'会', '發':'发', '見':'见', '體':'体', '菩薩':'菩萨', '聲聞':'声闻',
            '緣覺':'缘觉', '龍':'龙', '問':'问', '爾':'尔', '無':'无', '盡':'尽',
            '邊':'边', '覺':'觉', '證':'证'
        }
        for ft, jt in fantizi_map.items():
            if ft in yijie_part:
                issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：说明文字使用繁体字「{ft}」，修正建议：改为简体「{jt}」")
        
        # 4. 非咒文冗余粘贴：无梵字段落，译文和原文字符重合度高
        if len(orig_siddham) == 0 and len(modern) > 0:
            orig_chars = re.findall(r'[\u4e00-\u9fff]', orig)
            modern_chars = re.findall(r'[\u4e00-\u9fff]', modern)
            orig_set = set(orig_chars)
            modern_set = set(modern_chars)
            if len(orig_set) > 0:
                ratio = len(orig_set & modern_set) / len(orig_set)
                if ratio > 0.85 and len(modern_chars) > 30:
                    # 排除只有义解一句话的短段落，义解模板是固定简体，不会重合
                    if '原文照录如下' not in modern:
                        issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：非咒文正文整段粘贴文言原文，未译为白话，修正建议：将文言原文翻译为通顺的现代汉语白话")

# 去重
issues = list(dict.fromkeys(issues))
for issue in issues:
    print(issue)
