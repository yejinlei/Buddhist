import json
import os
import re

sutra_ids = ["t1062b", "t1213", "t1072b", "t1177b", "t0944b", "t1120a", "t0966", "t1120", "t0854", "t0944", "t2133a", "t0860"]
issues = []

def check_half_width(s):
    # 检查半角标点：!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ 除了可能的梵字编码
    half_punct = re.findall(r'[!\"#\$%&\'\(\)\*\+,-\./:;<=>\?@\[\\\]\^_`\{\|\}~]', s)
    return [p for p in half_punct if not (ord(p) > 0x10000)]

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
        
        # 1. 咒文错漏：提取咒文梵字部分对比
        # 提取梵字（U+10000以上的悉昙字，以及咒文标题中的中文？）这里逐字对比：咒文原文和modern里的梵字串
        # 先找出original和modern里的所有梵字序列
        orig_chars = [c for c in orig if ord(c) >= 0xE000 or (ord(c) >= 0x20000 and ord(c) <= 0x2FFFF) or c in '：。、（），']
        modern_chars = [c for c in modern if ord(c) >= 0xE000 or (ord(c) >= 0x20000 and ord(c) <= 0x2FFFF) or c in '：。、（），']
        
        # 提取梵字本身（大编码字符）
        orig_siddham = ''.join([c for c in orig if ord(c) >= 0x20000])
        modern_siddham_part = modern.split('原文照录如下：\n')[-1] if '原文照录如下：\n' in modern else modern
        modern_siddham = ''.join([c for c in modern_siddham_part if ord(c) >= 0x20000])
        
        if orig_siddham != modern_siddham:
            # 找第一个不同位置
            min_len = min(len(orig_siddham), len(modern_siddham))
            diff_pos = -1
            for i in range(min_len):
                if orig_siddham[i] != modern_siddham[i]:
                    diff_pos = i
                    break
            if diff_pos == -1:
                issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：咒文字数不一致，原文字数{len(orig_siddham)}，译文字数{len(modern_siddham)}，修正建议：核对梵字，补全或删除多余字符")
            else:
                issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：咒文第{diff_pos+1}字与原文不一致，修正建议：对照original_preview修正梵字错漏")
        
        # 2. 检查双【义解】
        if modern.count('【义解】') > 1:
            issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：出现多个【义解】标签，修正建议：仅保留一个【义解】")
        # 检查半角标点
        half = check_half_width(modern)
        if half:
            issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：存在半角标点{''.join(half)}，修正建议：替换为全角标点")
        
        # 检查说明文字是否简体（找常见繁体：灑、淨、為、麼、這、裡等，除了咒文保留原字）
        # 提取义解部分（标签后的说明，在原文照录前）
        yijie_part = ""
        if "【义解】" in modern:
            yijie_part = modern.split("【义解】")[1].split("原文照录如下")[0] if "原文照录如下" in modern else modern.split("【义解】")[1]
        # 繁体检测列表（说明中应简体）
        fantizi_check = {'灑':'洒','為':'为','經':'经','來':'来','個':'个','麼':'么','這':'这','裡':'里','後':'后','於':'于','對':'对','說':'说','時':'时','國':'国','會':'会','發':'发','見':'见','體':'体'}
        for ft, jt in fantizi_check.items():
            if ft in yijie_part:
                issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：说明文字使用繁体字「{ft}」，修正建议：改为简体「{jt}」")
        
        # 4. 非咒文原文整段粘贴：检查modern中除梵字、标题、义解说明外，是否有大段非咒文的文言原文（比如长行散文原文）
        # 咒文是梵字，标题短；如果是长行经文，modern应该是白话，不是原文
        # 检查：modern中如果不是纯咒语（即没有梵字，而大段是古文）
        siddham_count = len([c for c in modern if ord(c) >= 0x20000])
        hanzi_count = len(re.findall(r'[\u4e00-\u9fff]', modern))
        if siddham_count == 0 and hanzi_count > 50:
            # 没有梵字，且汉字多，检查是不是整段粘贴原文（不是白话）
            # 简单判断：如果原文和modern的汉字重合度>80%，说明是粘贴原文
            orig_hanzi = re.findall(r'[\u4e00-\u9fff]', orig)
            modern_hanzi = re.findall(r'[\u4e00-\u9fff]', modern)
            common = len(set(orig_hanzi) & set(modern_hanzi))
            if len(orig_hanzi) > 0 and common / len(set(orig_hanzi)) > 0.9 and len(modern_hanzi) > 30:
                # 再排除是咒文标题的情况（咒文标题短）
                if len(modern_hanzi) > len(re.findall(r'[\u4e00-\u9fff]', "【义解】此为某某真言，乃梵文悉昙体真言咒语，依法持诵即可，原文照录如下：")) + 20:
                    issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：非咒文部分整段粘贴原文文言，非白话译文，修正建议：将文言原文翻译为现代汉语白话")
        
        # 5. 标点疏漏、译名统一：检查常见译名：佛、菩萨、真言、涅槃等是否统一
        # 比如：「菩薩」和「菩萨」混用？说明中应简体「菩萨」，古注保留繁体
        if "菩薩" in yijie_part:
            issues.append(f"- 经号：{sid}，段号：{seg_no}，问题描述：说明文字中译名「菩薩」为繁体，修正建议：改为简体「菩萨」")
        if "真言" not in yijie_part and "陀羅尼" in yijie_part:
            pass # 不统一时再说

for issue in issues:
    print(issue)

if not issues:
    print("未发现问题")
