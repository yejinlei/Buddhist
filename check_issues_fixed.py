import json
import os
import re

sutra_ids = ["t1062b", "t1213", "t1072b", "t1177b", "t0944b", "t1120a", "t0966", "t1120", "t0854", "t0944", "t2133a", "t0860"]
issues = []

def is_half_width_punct(c):
    # 仅ASCII半角标点：!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~  排除字母数字
    return (ord(c) >= 0x21 and ord(c) <= 0x7E) and not c.isalnum()

def check_half_width(s):
    half = []
    for c in s:
        if is_half_width_punct(c):
            half.append(c)
    return half

for sid in sutra_ids:
    path = f"data/modern-translation/{sid}.json"
    if not os.path.exists(path):
        issues.append(f"- 经号：{sid}，段号：全，问题描述：文件不存在，修正建议：创建译文文件")
        continue
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        issues.append(f"- 经号：{sid}，段号：全，问题描述：JSON解析失败：{e}，修正建议：修复JSON格式")
        continue
    
    translations = data.get("translations", [])
    for idx, seg in enumerate(translations):
        seg_no = idx + 1
        orig = seg.get("original_preview", "").strip()
        modern = seg.get("modern", "").strip()
        
        # 1. 咒文错漏：对比original和modern中的所有悉昙梵字（U+20000-U+2FFFF）
        orig_siddham = ''.join([c for c in orig if 0x20000 <= ord(c) <= 0x2FFFF])
        # 在modern中找原文照录后的部分
        if '原文照录如下：\n' in modern:
            modern_text_part = modern.split('原文照录如下：\n')[-1]
        else:
            modern_text_part = modern
        modern_siddham = ''.join([c for c in modern_text_part if 0x20000 <= ord(c) <= 0x2FFFF])
        
        if len(orig_siddham) > 0 and orig_siddham != modern_siddham:
            min_len = min(len(orig_siddham), len(modern_siddham))
            diff_pos = -1
            for i in range(min_len):
                if orig_siddham[i] != modern_siddham[i]:
                    diff_pos = i
                    break
            if diff_pos == -1:
                issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：咒文字数不一致，原文字数{len(orig_siddham)}，译文字数{len(modern_siddham)}，修正建议：核对梵字，补全漏字或删除多字")
            else:
                issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：咒文第{diff_pos+1}字与原文不一致，修正建议：对照original_preview修正梵字错漏")
        
        # 2. 格式错误：双【义解】
        if modern.count('【义解】') > 1:
            issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：出现多个【义解】标签，修正建议：仅保留一个【义解】")
        
        # 半角标点
        half = check_half_width(modern)
        if half:
            issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：存在半角标点{''.join(list(set(half)))}，修正建议：替换为对应全角标点")
        
        # 说明文字简体：义解部分（原文照录前的说明）
        yijie_part = ""
        if "【义解】" in modern:
            parts = modern.split("【义解】", 1)[1]
            if "原文照录如下" in parts:
                yijie_part = parts.split("原文照录如下")[0]
            else:
                yijie_part = parts
        # 非咒语段（无梵字）的全部译文都要是简体白话
        if len(modern_siddham) == 0:
            yijie_part = modern
        
        fantizi_map = {
            '灑':'洒', '為':'为', '經':'经', '來':'来', '個':'个', '麼':'么', '這':'这',
            '裡':'里', '後':'后', '於':'于', '對':'对', '說':'说', '時':'时', '國':'国',
            '會':'会', '發':'发', '見':'见', '體':'体', '菩薩':'菩萨', '聲聞':'声闻',
            '緣覺':'缘觉', '龍':'龙', '問':'问', '答':'答', '爾':'尔', '時':'时', '云':'云',
            '無':'无', '盡':'尽', '邊':'边', '覺':'觉', '證':'证'
        }
        for ft, jt in fantizi_map.items():
            if ft in yijie_part:
                # 排除是专有名词保留？不，说明文字必须简体，梵文标题保留原字的不算在yijie_part里
                issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：说明文字使用繁体字「{ft}」，修正建议：改为简体「{jt}」")
        
        # 4. 冗余粘贴非咒文原文：非咒文段（无梵字），modern汉字和orig汉字重合度高说明是粘贴原文
        if len(orig_siddham) == 0 and len(modern) > 0:
            orig_hanzi_set = set(re.findall(r'[\u4e00-\u9fff]', orig))
            modern_hanzi_set = set(re.findall(r'[\u4e00-\u9fff]', modern))
            modern_hanzi_count = len(re.findall(r'[\u4e00-\u9fff]', modern))
            if len(orig_hanzi_set) > 0:
                common_ratio = len(orig_hanzi_set & modern_hanzi_set) / len(orig_hanzi_set)
                # 重合度>0.85且字数超过30，判定为整段粘贴文言原文
                if common_ratio > 0.85 and modern_hanzi_count > 30:
                    issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：非咒文正文整段粘贴文言原文，未译为白话，修正建议：将文言原文翻译为现代汉语白话")

# 去重
issues = list(dict.fromkeys(issues))
for issue in issues:
    print(issue)

if not issues:
    print("未发现问题")
