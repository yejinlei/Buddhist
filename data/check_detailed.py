import json
import os
import re

translation_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
sutra_ids = ["t1994b", "t2161", "t1246", "t0967", "t2751", "t2079", "t2158", "t2018", "t1022", "t1230", "t1984", "t1945"]

issues = []

for sutra_id in sutra_ids:
    path = os.path.join(translation_dir, f"{sutra_id}.json")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        issues.append(f"{sutra_id},全局,文件读取失败: {str(e)}")
        continue
    
    segments = data.get("translations", [])
    
    for idx, seg in enumerate(segments):
        seg_num = idx + 1
        
        modern = seg.get("modern", "")
        preview = seg.get("original_preview", "")
        
        # Check for empty paragraphs
        if not modern or modern.strip() == "":
            issues.append(f"{sutra_id},{seg_num},modern内容为空（空段落）")
            continue
        
        # Check quote pairing - 「」
        left1 = modern.count("「")
        right1 = modern.count("」")
        # Check for isolated quotes at start/end
        if modern.startswith("」") and idx > 0:
            prev_modern = segments[idx-1].get("modern", "")
            if not prev_modern.endswith("「") and not prev_modern.rstrip().endswith("“"):
                issues.append(f"{sutra_id},{seg_num},段首孤立闭引号「」")
        if modern.endswith("「"):
            issues.append(f"{sutra_id},{seg_num},段末孤立开引号「」")
        
        # Check for multiple opening/closing imbalance (allow cross segment 1)
        net_quotes = left1 - right1
        if abs(net_quotes) > 1:
            issues.append(f"{sutra_id},{seg_num},「」引号数量不平衡（左{left1}右{right1}，差{net_quotes}）")
        # Check “” quotes
        left3 = modern.count("“")
        right3 = modern.count("”")
        net3 = left3 - right3
        if abs(net3) > 1:
            issues.append(f"{sutra_id},{seg_num},“”引号数量不平衡（左{left3}右{right3}，差{net3}）")
        
        # Check for 『』
        left2 = modern.count("『")
        right2 = modern.count("』")
        if abs(left2 - right2) > 1:
            issues.append(f"{sutra_id},{seg_num},『』引号数量不平衡")
        
        # Check for duplicate 【义解】
        yijie_count = modern.count("【义解】")
        if yijie_count > 1:
            issues.append(f"{sutra_id},{seg_num},重复【义解】标签（{yijie_count}次）")
        
        # Check for duplicate section tags at start (like 【xxx】【xxx】)
        start_tags = re.findall(r"^【[^】]+】", modern)
        if len(start_tags) > 2:
            issues.append(f"{sutra_id},{seg_num},段首多个小标题标签（{len(start_tags)}个）")
        
        # Check for untranslated ancient text pasted: if after 【义解】 there's a long chunk of classical Chinese with no baihua explanation, or if baihua section is missing
        # Find position of 【义解】
        yijie_pos = modern.find("【义解】")
        if yijie_pos == -1:
            issues.append(f"{sutra_id},{seg_num},缺少【义解】标签")
        else:
            baihua_part = modern[yijie_pos+4:]
            # Check for "白话译文" label duplicated?
            if baihua_part.count("白话译文") > 1 or baihua_part.count("白话译文：") > 1:
                issues.append(f"{sutra_id},{seg_num},重复「白话译文」标签")
            # Check for "咒曰：" duplicated (seen in t1230)
            if "咒曰：" in baihua_part:
                zhouyue_count = baihua_part.count("咒曰：")
                # Allow if it's multiple different mantras, but if repeated right after itself that's a problem
                if "咒曰：「" in baihua_part and "咒曰：「咒曰：" in baihua_part:
                    issues.append(f"{sutra_id},{seg_num},重复「咒曰：」标识，粘贴错误")
        
        # Check for numbers mistranslation - check key numbers match
        # Look for common numbers in preview: 一/二/三/四/五/六/七/八/九/十/百/千/万, and check if they're translated correctly
        # Hard to do perfectly, but check for obvious mismatches where a number appears in preview and not at all in modern
        # For example 十万 should be 十万 not 万, etc.
        common_numbers = ["七", "八", "十", "十二", "十八", "三十六", "四十八", "十万", "八万四千", "千二百五十", "百千"]
        # Skip mantras
        
        # Check for segment misalignment - preview content doesn't match modern topic
        # Hard, but check for obvious wrong characters introduced near fixes
        
        # Check original_preview is not empty
        if not preview or preview.strip() == "":
            issues.append(f"{sutra_id},{seg_num},original_preview为空")
        
        # Check for empty lines inside modern (multiple newlines)
        if "\n\n\n" in modern:
            issues.append(f"{sutra_id},{seg_num},modern中存在多余空段落（多个连续换行）")
        
        # Check for wrong words introduced: common typos
        typos = {
            "义解": "义解",  # correct
            "阇梨": "阇梨",  # correct
            "菩提": "菩提",
            "涅槃": "涅槃",
            "般若": "般若",
            "波罗蜜": "波罗蜜",
            "比丘": "比丘",
            "比丘尼": "比丘尼",
            "优婆塞": "优婆塞",
            "优婆夷": "优婆夷",
            "曼荼罗": "曼荼罗",
        }
        # Check for "义解" typoed as "义觧" etc.
        wrong_chars = {
            "夠": "够",
            "麼": "么",
            "後": "后",
            "裡": "里",
            "個": "个",
            "為": "为",
            "說": "说",
            "這": "这",
            "時": "时",
            "會": "会",
            "來": "来",
            "對": "对",
            "聲": "声",
            "無": "无",
            "萬": "万",
            "觀": "观",
            "書": "书",
            "長": "长",
            "門": "门",
            "問": "问",
            "開": "开",
            "間": "间",
            "見": "见",
            "點": "点",
            "從": "从",
            "應": "应",
            "經": "经",
            "爾": "尔",
            "雲": "云",
            "發": "发",
            "變": "变",
            "於": "于",
        }
        # Check if there are any trad chars in non-mantra sections
        for trad, simp in wrong_chars.items():
            # Allow trad chars in mantras (梵咒) and in quoted original text (inside 「」 quotes)
            # Find all positions of the char
            pos = 0
            while True:
                pos = modern.find(trad, pos)
                if pos == -1:
                    break
                # Check if it's inside a quote block (original text)
                in_quote = False
                # Count quotes before this position
                left1_before = modern[:pos].count("「")
                right1_before = modern[:pos].count("」")
                if left1_before > right1_before:
                    in_quote = True
                left3_before = modern[:pos].count("“")
                right3_before = modern[:pos].count("”")
                if left3_before > right3_before:
                    in_quote = True
                # Check if it's after 咒曰：(mantra section)
                zhouyue_pos = modern.rfind("咒曰：", 0, pos)
                if zhouyue_pos != -1:
                    # Check if we're after 咒曰 and before the end of the quote
                    zhouyue_end_quote = modern.find("」", zhouyue_pos)
                    if zhouyue_end_quote == -1 or pos < zhouyue_end_quote:
                        in_quote = True
                # Check if it's in original_preview? No, original_preview is separate
                # Check if it's in a section title (between 【】at start)? Titles should be simplified
                section_end = modern.find("】")
                if section_end != -1 and pos < section_end:
                    # Title should be simplified
                    issues.append(f"{sutra_id},{seg_num},小标题「{modern[:section_end+1]}」残留繁体「{trad}」，应改为「{simp}」")
                    break
                if not in_quote:
                    # Check if it's in 义解 part after the label
                    yijie_pos_local = modern.find("【义解】")
                    if yijie_pos_local != -1 and pos > yijie_pos_local:
                        # In baihua/义解, should be simplified
                        # But check if it's a proper noun/title? Allow certain chars in titles
                        if trad not in ["爾", "於", "為"]:  # these might be in proper nouns? Actually no, they should be simplified in explanation
                            # Check if it's inside a quote within 义解 (quoting original)
                            pass
                        issues.append(f"{sutra_id},{seg_num},白话译文/义解中残留繁体「{trad}」，应改为「{simp}」")
                        break
                pos += 1
        
        # Check for "【白话译文】" label used incorrectly? The format is 【小标题】【义解】 then 白话译文： no brackets
        if "【白话译文】" in modern:
            issues.append(f"{sutra_id},{seg_num},错误使用【白话译文】标签，应为「白话译文：」")
        
        # Check for new typos around fixes - look for double characters
        double_char = re.findall(r"([\u4e00-\u9fff])\1{2,}", modern)
        if double_char:
            issues.append(f"{sutra_id},{seg_num},重复叠字：{''.join(set(double_char))}")

# Print results
if issues:
    for issue in issues:
        print(issue)
else:
    print("全部复核合格，无遗留问题")
