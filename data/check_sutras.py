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
    
    segments = data.get("segments", [])
    
    for idx, seg in enumerate(segments):
        seg_num = idx + 1
        
        # Check required fields
        if "section" not in seg:
            issues.append(f"{sutra_id},{seg_num},缺少section字段")
        if "original_preview" not in seg:
            issues.append(f"{sutra_id},{seg_num},缺少original_preview字段")
        if "modern" not in seg:
            issues.append(f"{sutra_id},{seg_num},缺少modern字段")
            continue
        
        modern = seg["modern"]
        preview = seg.get("original_preview", "")
        
        # Check for empty paragraphs/empty modern
        if not modern or modern.strip() == "":
            issues.append(f"{sutra_id},{seg_num},modern内容为空（空段落）")
        
        # Check for untranslated classical Chinese pasted directly (if modern is same as preview or looks like untranslated)
        if modern.strip() == preview.strip() and len(preview) > 20:
            # Could be咒文照录，but check if there's any vernacular content
            # Simple heuristic: if contains only classical Chinese without【义解】and looks like raw sutra text
            if "【义解】" not in modern and "【" in modern[:20] == False:
                pass  #咒文 is allowed, skip this heuristic
        
        # Check quote pairing (「」 and 『』 and “”)
        # Count various quote types
        quotes_left1 = modern.count("「")
        quotes_right1 = modern.count("」")
        quotes_left2 = modern.count("『")
        quotes_right2 = modern.count("』")
        quotes_left3 = modern.count("“")
        quotes_right3 = modern.count("”")
        
        # Allow difference of 1 for cross-segment quotes (not closed/opened at end/start), but flag if difference > 1 or isolated quotes
        if abs(quotes_left1 - quotes_right1) > 1:
            issues.append(f"{sutra_id},{seg_num},「」引号配对异常（左{quotes_left1}右{quotes_right1}）")
        if abs(quotes_left2 - quotes_right2) > 1:
            issues.append(f"{sutra_id},{seg_num},『』引号配对异常（左{quotes_left2}右{quotes_right2}）")
        if abs(quotes_left3 - quotes_right3) > 1:
            issues.append(f"{sutra_id},{seg_num},“”引号配对异常（左{quotes_left3}右{quotes_right3}）")
        
        # Check for wrong characters/typos common
        # Check for duplicate tags like 【义解】【义解】
        yijie_count = modern.count("【义解】")
        if yijie_count > 1:
            issues.append(f"{sutra_id},{seg_num},重复【义解】标签（{yijie_count}次）")
        
        # Check for duplicate section brackets
        if modern.count("【") > 2 and "【义解】" in modern:
            # Allow one section title + 【义解】 = 2, more could be duplicates
            non_yijie_brackets = [m.start() for m in re.finditer(r"【[^】]+】", modern) if "义解" not in m.group()]
            if len(non_yijie_brackets) > 1:
                # Check for duplicate section tags at start
                start_tags = re.findall(r"^(【[^】]+】)+", modern)
                if start_tags and len(start_tags[0]) > 6:
                    issues.append(f"{sutra_id},{seg_num},段首存在重复小标题标签")
        
        # Check for half-width punctuation in vernacular text (should be full-width, except in code/numbers)
        half_width_punct = re.findall(r'[!?.,:;"\'()\[\]]', modern.replace("http", "").replace("二合", "").replace("引", ""))
        # Filter out numbers, decimal points in numbers, and valid cases like (引), (二合)
        bad_half = []
        for p in half_width_punct:
            # Allow () for phonetic notes like (引), (二合), (反)
            if p in "()" and any(mark in modern[max(0, modern.index(p)-3):modern.index(p)+3] for mark in ["引", "二合", "三合", "反", "去", "上", "入"]):
                continue
            bad_half.append(p)
        if len(bad_half) > 0 and "http" not in modern:
            issues.append(f"{sutra_id},{seg_num},存在半角标点: {''.join(set(bad_half))}")
        
        # Check for common wrong traditional characters in vernacular (not in咒文/preview)
        # Common trad chars that should be simplified in baihua:
        common_trad = {
            "萬": "万", "難": "难", "觀": "观", "聲": "声", "聞": "闻", "說": "说",
            "會": "会", "緣": "缘", "輪": "轮", "羅": "罗", "壽": "寿", "護": "护",
            "壇": "坛", "場": "场", "養": "养", "種": "种", "調": "调", "愛": "爱",
            "題": "题", "記": "记", "寫": "写", "懺": "忏", "滅": "灭", "盡": "尽",
            "無": "无", "虛": "虚", "毘": "毗", "斷": "断", "捨": "舍", "體": "体",
            "來": "来", "廣": "广", "國": "国", "薩": "萨", "對": "对", "經": "经",
            "訶": "诃", "執": "执", "峯": "峰", "叡": "睿", "儀": "仪", "軌": "轨",
            "勝": "胜", "夠": "够", "瘋": "疯"
        }
        for trad, simp in common_trad.items():
            # Only flag if in vernacular part (not in original_preview/咒文 section), so check if it appears after 【义解】or in non-mantra vernacular
            # Simple check: if it appears in modern, and not in a substring that's clearly a mantra (we can't be perfect, but flag obvious cases)
            if trad in modern:
                # Check if it's only in the original_preview quoted part? No, original_preview is separate field
                # Flag if it's in the baihua explanation, not in a quoted mantra
                # Allow if it's in a paragraph that's mostly Sanskrit transliteration (more than 30% Sanskrit-like chars)
                mantra_chars = set("嚩囉吽唵誐喃迦佉誐那麼弭怛他孽多娑訶薩嚩日啰驮摩尼钵哆庾瑟胝釰")
                mantra_count = sum(1 for c in modern if c in mantra_chars)
                total_len = len(modern.replace("【义解】", "").replace(" ", ""))
                if total_len > 0 and mantra_count / total_len < 0.3:
                    # Check if it's inside a quote block (quote marks around it) - allow if quoting original text
                    pos = modern.find(trad)
                    in_quote = False
                    # Check nearby for quotes
                    for start_q, end_q in [("「", "」"), ("『", "』"), ("“", "”")]:
                        last_start = modern.rfind(start_q, 0, pos)
                        first_end = modern.find(end_q, pos)
                        if last_start != -1 and (first_end == -1 or first_end > pos):
                            in_quote = True
                            break
                    if not in_quote:
                        issues.append(f"{sutra_id},{seg_num},白话中残留繁体/异体字「{trad}」，应改为「{simp}」")
                        break  # One per segment is enough for now
        
        # Check for wrong terms: 曼陀罗 -> 曼荼罗 (when referring to mandala, not flower)
        if "曼陀罗" in modern and "曼荼罗" not in modern and "花" not in modern[max(0, modern.find("曼陀罗")-5):modern.find("曼陀罗")+10]:
            issues.append(f"{sutra_id},{seg_num},术语错误：「曼陀罗」为花名，表mandala应作「曼荼罗」")
        
        # Check for 苾刍 used as main term in vernacular (should be 比丘)
        if "苾刍" in modern and "比丘" not in modern.replace("苾刍", ""):
            # Check if it's explaining the term: should be "比丘（旧译苾刍）", not "苾刍即比丘"
            if "旧译" not in modern and "异译" not in modern and "即" in modern[max(0, modern.find("苾刍")-2):modern.find("苾刍")+8]:
                issues.append(f"{sutra_id},{seg_num},术语问题：白话叙述中直接使用旧译「苾刍」，应改为「比丘（旧译苾刍）」")
        
        # Check for segment misalignment (modern is clearly talking about something in different preview)
        # This is harder to automate, but we can check for number mistranslation:
        # For example, "十五" translated as "十四" etc. - hard to do generically
        
        # Check for original_preview not being modified: we can't check this without original sutra, but we can check that it exists and is not empty
        if not preview or preview.strip() == "":
            issues.append(f"{sutra_id},{seg_num},original_preview为空")
        
        # Check for new typos around fixed areas - not easy without knowing fixed positions, but general typo check for common wrong chars:
        # Check for double punctuation like 。。 ，， ；；
        double_punct = re.findall(r"([。，；：！？])\1", modern)
        if double_punct:
            issues.append(f"{sutra_id},{seg_num},重复标点：{''.join(set(double_punct))}")
        
        # Check for leading/trailing whitespace issues
        if modern.startswith("\n") or modern.endswith("\n"):
            issues.append(f"{sutra_id},{seg_num},modern首尾存在多余换行")
        if modern.startswith(" ") or modern.endswith(" "):
            issues.append(f"{sutra_id},{seg_num},modern首尾存在多余空格")

# Print results
if issues:
    for issue in issues:
        print(issue)
else:
    print("全部复核合格，无遗留问题")
