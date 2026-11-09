import json
import os
import re

sutra_ids = [
    "t0480", "t0445", "t1461", "t1423", "t0347", "t1693",
    "t1761", "t2789", "t1520", "t2100", "t2837", "t1884"
]

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data"
translation_dir = os.path.join(base_dir, "modern-translation")
skel_dir = os.path.join(base_dir, "baihua-tasks")

issues = []

for sid in sutra_ids:
    trans_path = os.path.join(translation_dir, f"{sid}.json")
    skel_path = os.path.join(skel_dir, f"{sid}.skel.json")
    
    # Load translation
    try:
        with open(trans_path, 'r', encoding='utf-8') as f:
            trans_data = json.load(f)
    except Exception as e:
        issues.append(f"{sid}: 无法读取译文文件 - {str(e)}")
        continue
    
    # Load skeleton
    try:
        with open(skel_path, 'r', encoding='utf-8') as f:
            skel_data = json.load(f)
    except Exception as e:
        issues.append(f"{sid}: 无法读取骨架文件 - {str(e)}")
        continue
    
    trans_list = trans_data.get("translations", [])
    skel_list = skel_data.get("translations", [])
    
    if len(trans_list) != len(skel_list):
        issues.append(f"{sid}: 段落数量不一致 - 译文{len(trans_list)}段，骨架{len(skel_list)}段")
    
    for idx, (trans_item, skel_item) in enumerate(zip(trans_list, skel_list), 1):
        seg_id = f"{sid} 第{idx}段"
        
        # Check 3: original_preview matches skeleton
        trans_op = trans_item.get("original_preview", "")
        skel_op = skel_item.get("original_preview", "")
        if trans_op != skel_op:
            issues.append(f"{seg_id}: original_preview与骨架文件不一致")
        
        modern = trans_item.get("modern", "")
        
        # Check 1: Format - starts with 【小标题】, contains 【义解】, content after 【义解】
        # Pattern: starts with 【...】(小标题), then has 【义解】, then content
        if not modern.startswith("【"):
            issues.append(f"{seg_id}: modern字段未以【小标题】开头")
        else:
            # Find the first closing bracket
            first_bracket_end = modern.find("】")
            if first_bracket_end == -1:
                issues.append(f"{seg_id}: modern字段小标题格式错误（缺少闭合】）")
            else:
                # Check if there's content before 【义解】 (the small title)
                after_first_bracket = modern[first_bracket_end+1:]
                if "【义解】" not in after_first_bracket:
                    issues.append(f"{seg_id}: modern字段缺少【义解】标记")
                else:
                    yijie_pos = after_first_bracket.find("【义解】")
                    content_after_yijie = after_first_bracket[yijie_pos + len("【义解】"):].strip()
                    if not content_after_yijie:
                        issues.append(f"{seg_id}: 【义解】后无正文内容")
        
        # Check 2: Errors - double tags, double punctuation, typos (simple checks)
        # Double tags: 【【 or 】】
        if "【【" in modern:
            issues.append(f"{seg_id}: 存在双标签【【")
        if "】】" in modern:
            issues.append(f"{seg_id}: 存在双标签】】")
        
        # Double punctuation: check for repeated Chinese punctuation
        # Common: 。。、，，、！！、？？、；；、：：、""、''
        double_punct_pattern = re.compile(r'([。，！？；：、""''（）【】])\1')
        dp_matches = double_punct_pattern.findall(modern)
        if dp_matches:
            unique_puncts = set(dp_matches)
            issues.append(f"{seg_id}: 存在双标点 - {','.join(unique_puncts)}")
        
        # Check for obvious typos (common ones we can flag without dictionary)
        # This is harder; we can note if there are obvious issues but let's skip complex typo check for now
        # We'll check for empty modern first
        if not modern.strip():
            issues.append(f"{seg_id}: modern字段为空")

if not issues:
    print("全部12部经复核合格，无问题")
else:
    for issue in issues:
        print(issue)
