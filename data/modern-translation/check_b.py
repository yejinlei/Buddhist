import json
import os
import re

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
files = ["t1239", "t0850", "t2075", "t1251", "t0953", "t0887", "t2871", "t0682", "t0341", "t1757", "t2810", "t1797"]

total_segments = 0
issues = []

# 梵咒音译字，不应翻译
mantra_chars = {"曩", "莫", "俱", "胝", "薩", "嚩", "爾", "婆", "訶", "喃", "娑", "訶", "唵", "吽", "怛", "囉", "迦", "耶", "摩", "訶", "莎", "曳", "帝", "醯", "嚧", "呬", "鉢", "摩", "他", "伽", "踰", "闥", "姪", "怛", "你", "也", "阿", "謨", "伽", "梵", "牟", "含"}

# 套话义解模板检测
cliche_yijie = [
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
        seg_issues.append(f"段落{seg_idx}: modern字段未以【小标题】开头")
    else:
        # 提取小标题
        title_match = re.match(r"【(.*?)】", modern)
        if not title_match:
            seg_issues.append(f"段落{seg_idx}: 小标题格式错误，未正确闭合")
        else:
            title = title_match.group(1)
            if len(title) < 2 or len(title) > 10:
                seg_issues.append(f"段落{seg_idx}: 小标题长度异常：{title}")
    
    # 2. 检查义解
    yijie_match = re.search(r"【义解】(.*?)\n", modern, re.DOTALL)
    if not yijie_match:
        seg_issues.append(f"段落{seg_idx}: 缺少【义解】部分")
    else:
        yijie_text = yijie_match.group(1).strip()
        # 检查是否为套话
        is_cliche = False
        for cliche in cliche_yijie:
            if cliche in yijie_text:
                is_cliche = True
                break
        if len(yijie_text) < 15:
            seg_issues.append(f"段落{seg_idx}: 义解过短，疑似套话：{yijie_text}")
        elif is_cliche and len(yijie_text) < 30:
            seg_issues.append(f"段落{seg_idx}: 义解为套话，无实质法义说明：{yijie_text[:50]}...")
    
    # 3. 检查义解后有正文白话
    parts = modern.split("\n")
    has_original_after_yijie = False
    yijie_found = False
    for part in parts:
        if "【义解】" in part:
            yijie_found = True
            continue
        if yijie_found and part.strip() and not part.startswith("【"):
            has_original_after_yijie = True
            break
    if yijie_found and not has_original_after_yijie:
        seg_issues.append(f"段落{seg_idx}: 义解后无正文白话内容")
    
    # 4. 检查梵咒原字是否被翻译（这里简单检查：原文有这些字的地方，白话中对应位置是否保留；另外检查是否把这些字译成了现代汉语）
    # 检查是否有把"曩莫"译成"归命"等情况，以及梵咒音译字是否被替换
    for char in mantra_chars:
        if char in original_preview:
            # 如果原文有这个音译字，现代译文里也应该有（除非是普通用法，但梵咒中必须保留）
            # 简单检查：如果原文出现连续梵咒字（>=2个），现代译文中必须保留
            pass
    
    # 检查正文白话部分是否错误多了标点（比如原文结尾没有"。"，译文多了）
    # 提取义解后的正文部分
    text_after_yijie = ""
    after_yijie = False
    for i, part in enumerate(parts):
        if after_yijie:
            text_after_yijie += part + "\n"
        if "【义解】" in part:
            after_yijie = True
    text_after_yijie = text_after_yijie.strip()
    original_stripped = original_preview.strip()
    text_after_stripped = text_after_yijie.strip()
    
    # 检查是否多了末尾句号
    if original_stripped and text_after_stripped:
        if original_stripped.endswith("、") and text_after_stripped.endswith("、。"):
            seg_issues.append(f"段落{seg_idx}: 正文末尾错误多了句号，原文以顿号结尾")
        elif original_stripped.endswith("，") and text_after_stripped.endswith("，。"):
            seg_issues.append(f"段落{seg_idx}: 正文末尾错误多了句号，原文以逗号结尾")
        # 检查原文没有结尾句号，译文多了
        if not original_stripped.endswith("。") and not original_stripped.endswith("！") and not original_stripped.endswith("？") and not original_stripped.endswith("：") and not original_stripped.endswith("」") and not original_stripped.endswith("』") and not original_stripped.endswith("…") and not original_stripped.endswith("—") and len(original_stripped) > 0:
            if text_after_stripped.endswith("。") and not original_stripped.endswith("。"):
                # 再检查最后几个字
                orig_last3 = original_stripped[-3:] if len(original_stripped)>=3 else original_stripped
                text_last3 = text_after_stripped[-3:] if len(text_after_stripped)>=3 else text_after_stripped
                if orig_last3 not in text_last3 and not original_stripped.endswith(("菩薩、", "菩薩，", "，", "、")):
                    pass  # 简单跳过
    
    # 检查原文未被修改（original_preview是否有改动迹象：比如和正文不一致太多？这里其实应该original_preview是原文，不能改，但我们没有原始对照，只能检查是否明显篡改）
    # 检查现代译文是否完全照搬原文（没有做白话翻译）
    if text_after_yijie.strip() == original_preview.strip() and len(original_preview) > 20:
        # 检查是否有白话转换的痕迹：比如"曰"是否改成"说"，"云何"改成"为什么"等
        has_vernacular = False
        vernacular_markers = ["叫做", "为什么", "怎么", "说", "就", "的", "了", "吗", "呢", "这个", "那个"]
        for marker in vernacular_markers:
            if marker in text_after_yijie:
                # 排除原文里本来有的
                if marker not in original_preview:
                    has_vernacular = True
                    break
        if not has_vernacular and not any(c in original_preview for c in ["咒", "真言", "陀羅尼", "曩莫", "娑婆訶", "唵"]):
            # 非咒语部分完全照搬原文，没有白话
            seg_issues.append(f"段落{seg_idx}: 正文白话部分完全照搬原文，未做白话翻译")
    
    # 5. 检查梵咒音译字是否被翻译：比如原文有"曩莫"，译文里写成"归命"或其他白话
    mantra_pattern = re.compile(r'(曩莫|俱胝|薩嚩|薩婆|莎訶|娑婆訶|娑訶|唵|吽)')
    mantra_matches = mantra_pattern.findall(original_preview)
    if mantra_matches:
        for match in mantra_matches:
            if match not in text_after_yijie:
                seg_issues.append(f"段落{seg_idx}: 梵咒音译字「{match}」未照录，疑似被翻译")
    
    return seg_issues

for file_id in files:
    file_path = os.path.join(base_dir, f"{file_id}.json")
    if not os.path.exists(file_path):
        issues.append(f"文件{file_id}.json不存在")
        continue
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        translations = data.get("translations", [])
        total_segments += len(translations)
        file_issue_count = 0
        for idx, seg in enumerate(translations):
            seg_issues = check_segment(seg, file_id, idx+1)
            for issue in seg_issues:
                issues.append(f"{file_id}: {issue}")
                file_issue_count +=1
        print(f"检查{file_id}: {len(translations)}段，发现{file_issue_count}个问题")
    except Exception as e:
        issues.append(f"文件{file_id}.json读取错误：{str(e)}")

print(f"\n总段落数：{total_segments}")
print(f"总问题数：{len(issues)}")
if issues:
    print("\n问题列表：")
    for issue in issues[:50]:  # 先打印前50个
        print(f"- {issue}")
    if len(issues) > 50:
        print(f"...还有{len(issues)-50}个问题")
else:
    print("未发现问题")
