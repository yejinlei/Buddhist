import json
import os
import re

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
files = ["t1239", "t0850", "t2075", "t1251", "t0953", "t0887", "t2871", "t0682", "t0341", "t1757", "t2810", "t1797"]

total_segments = 0
issues = []

# 梵咒音译字，咒语部分必须完全照录，不能翻译
mantra_keywords = ["陀羅尼", "咒曰", "真言曰", "神咒", "咒", "陀羅尼曰", "即說咒曰"]

# 严格套话模板（完全匹配的才算套话）
strict_cliche = [
    "此段為經文正文，繼續宣說佛法要義、修行法則與法門功德，行者當諦聽諦受依教奉行。",
    "此段宣說受持、讀誦、書寫、供養、為他人解說此經法門的殊勝功德利益，能滅罪生善、植菩提種、不退菩提、蒙佛授記。",
    "此段記載佛陀放光現瑞、大地震動等神變瑞相，預示將說殊勝大法，昭示法義深妙。",
    "此段開示菩薩行門，教令發菩提心、行六波羅蜜、四攝四無量，上求佛道下化眾生，積集福智資糧。"
]

def check_segment(seg, file_id, seg_idx):
    seg_issues = []
    modern = seg.get("modern", "")
    original_preview = seg.get("original_preview", "")
    
    # 1. 检查小标题开头
    if not modern.startswith("【"):
        seg_issues.append("modern字段未以【小标题】开头")
    else:
        title_match = re.match(r"【(.*?)】", modern)
        if not title_match:
            seg_issues.append("小标题格式错误，未正确闭合")
        else:
            title = title_match.group(1)
            if len(title) < 2 or len(title) > 10:
                seg_issues.append(f"小标题长度异常：{title}")
    
    # 2. 拆分modern字段结构
    parts = modern.split("\n")
    title = ""
    yijie = ""
    text_after_yijie = []
    step = 0  # 0:找标题, 1:找义解, 2:收集正文
    
    for part in parts:
        part_stripped = part.strip()
        if step == 0:
            if part_stripped.startswith("【") and part_stripped.endswith("】"):
                title = part_stripped[1:-1]
                step = 1
            continue
        if step == 1:
            if part_stripped.startswith("【义解】"):
                yijie = part_stripped[4:].strip()
                step = 2
            continue
        if step == 2:
            text_after_yijie.append(part)
    
    text_after_yijie_str = "\n".join(text_after_yijie).strip()
    original_stripped = original_preview.strip()
    
    # 3. 检查义解是否存在
    if step < 2:
        seg_issues.append("缺少【义解】部分")
    else:
        # 检查是否完全是套话（一字不差匹配模板）
        if yijie in strict_cliche:
            # 如果正文和小标题不匹配，才算套话问题；比如列菩萨名号的段落，用"法义宣说"+套话就不对
            # 检查正文内容：如果是罗列菩萨名、大众名，用"圣众云集"才对，用"法义宣说"就不对
            is_listing_names = False
            if "菩薩、" in original_stripped and original_stripped.count("菩薩") > 3:
                is_listing_names = True
            if "龍王、" in original_stripped and original_stripped.count("、") > 5:
                is_listing_names = True
            if title == "法義宣說" and is_listing_names:
                seg_issues.append(f"义解为套话，且小标题与段意不符（{title}用于罗列圣众名单段落）")
            # 检查是否完全套话无实质内容：义解长度<20字，且完全匹配模板
            if len(yijie) < 40:
                seg_issues.append(f"义解为通用套话，无对应本段的实质法义说明：{yijie[:40]}...")
    
    # 4. 检查义解后是否有正文
    if step == 2 and not text_after_yijie_str:
        seg_issues.append("义解后无正文白话内容")
    
    # 5. 检查末尾标点错误：原文以顿号/逗号结尾，正文末尾错误多了句号
    if text_after_yijie_str and original_stripped:
        orig_last_char = original_stripped[-1]
        text_last_char = text_after_yijie_str[-1]
        if orig_last_char in ["、", "，", "："] and text_after_yijie_str.endswith(orig_last_char + "。"):
            seg_issues.append(f"正文末尾错误多加句号，原文以「{orig_last_char}」结尾，译文变成「{orig_last_char}。」")
        # 检查末尾多加句号的情况：原文末尾不是句末标点，译文末尾多了。
        if orig_last_char not in ["。", "！", "？", "」", "』", "…", "—", "”", "』"] and text_last_char == "。":
            # 排除原文是半句话，到这里正好断句，但原文最后是顿号逗号的情况我们已经查了
            # 比如原文最后是"名"，译文应该加"叫："，但如果最后是菩萨名号后面加句号，肯定错
            if orig_last_char in ["菩薩", "王", "天", "眾", "俱", "首", "上", "大", "人", "等", "也", "言"] and len(original_stripped) > 10:
                if original_stripped[-2:] in ["菩薩", "為上", "俱。", "首，", "首。"]:
                    pass
                else:
                    # 检查是否只是最后多了句号：去掉译文最后一个句号后和原文是否一致（除了个别白话字）
                    text_without_last_period = text_after_yijie_str[:-1]
                    if text_without_last_period.endswith(orig_last_char) and len(text_without_last_period) >= len(original_stripped) - 5:
                        seg_issues.append(f"正文末尾错误多加句号，原文末尾为「{orig_last_char}」，译文多加了句末句号")
    
    # 6. 检查梵咒部分是否照录：如果原文是咒语，正文必须完全照录原文，不能翻译
    is_mantra_section = False
    for kw in mantra_keywords:
        if kw in original_stripped:
            is_mantra_section = True
            break
    # 检测音译字组合
    mantra_char_sets = ["曩莫", "俱胝", "薩嚩", "薩婆", "娑婆訶", "莎訶", "唵", "吽", "怛他", "蘗多", "冒地", "薩埵"]
    mantra_count = 0
    for ms in mantra_char_sets:
        if ms in original_stripped:
            mantra_count +=1
    if mantra_count >=2:
        is_mantra_section = True
    
    if is_mantra_section:
        # 咒语部分必须完全照录，不能翻译；检查音译字是否被替换
        # 提取正文去掉白话虚词
        mantra_chars_original = re.findall(r'[曩莫俱胝薩嚩爾婆訶喃娑唵吽怛囉迦耶摩訶莎曳帝醯嚧呬鉢他伽踰闥姪你也阿謨牟含]', original_stripped)
        mantra_chars_text = re.findall(r'[曩莫俱胝薩嚩爾婆訶喃娑唵吽怛囉迦耶摩訶莎曳帝醯嚧呬鉢他伽踰闥姪你也阿謨牟含]', text_after_yijie_str)
        if len(mantra_chars_original) != len(mantra_chars_text):
            # 简单检查是否有缺失
            missing = []
            for c in set(mantra_chars_original):
                if mantra_chars_text.count(c) < mantra_chars_original.count(c) -1:
                    missing.append(c)
            if missing:
                seg_issues.append(f"梵咒部分音译字{missing}未照录，疑似被翻译")
    
    # 7. 检查是否把原文的"吾"等字改了但其他地方照搬却错误（简单检查）
    # 检查"其名曰"是否改成了"其名叫"，这个是对的；但检查是否有错误：比如原文"莫呼羅伽"等专有名词被改
    return seg_issues

for file_id in files:
    file_path = os.path.join(base_dir, f"{file_id}.json")
    if not os.path.exists(file_path):
        issues.append(f"{file_id}: 文件不存在")
        continue
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        translations = data.get("translations", [])
        total_segments += len(translations)
        file_issues = []
        for idx, seg in enumerate(translations):
            seg_issues = check_segment(seg, file_id, idx+1)
            for issue in seg_issues:
                file_issues.append(f"{file_id} 段落{idx+1}: {issue}")
        issues.extend(file_issues)
        print(f"检查{file_id}: {len(translations)}段，发现{len(file_issues)}个问题")
    except Exception as e:
        issues.append(f"{file_id}: 文件读取错误：{str(e)}")

print(f"\n=== B路复核结果 ===")
print(f"总段落数：{total_segments}")
print(f"总问题数：{len(issues)}")

if issues:
    print("\n问题详情（按文件分类，每类最多10条）：")
    from collections import defaultdict
    issues_by_file = defaultdict(list)
    for issue in issues:
        fid = issue.split(" ")[0]
        issues_by_file[fid].append(issue)
    
    for fid in files:
        if fid in issues_by_file:
            print(f"\n--- {fid} ({len(issues_by_file[fid])}个问题) ---")
            for i, issue in enumerate(issues_by_file[fid][:10]):
                print(f"- {issue}")
            if len(issues_by_file[fid]) > 10:
                print(f"  ...还有{len(issues_by_file[fid])-10}个问题")
else:
    print("全部合格")
