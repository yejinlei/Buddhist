#!/usr/bin/env python3
import json
import os
import re

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology"
out_dir = os.path.join(base_dir, "data/baihua-out")
task_dir = os.path.join(base_dir, "data/baihua-tasks")

sutra_ids = ["t1369b", "t1412", "t1325", "t0960", "t0138", "t0056", "t1369a", "t1206", "t2094", "t0391", "t1178", "t1467b"]

report = []
total_segments = 0
all_issues = {}
all_pass = True

for tid in sutra_ids:
    out_path = os.path.join(out_dir, f"{tid}.json")
    task_path = os.path.join(task_dir, f"{tid}.json")
    
    issues = []
    
    # 读取译文
    with open(out_path, "r", encoding="utf-8") as f:
        baihua_data = json.load(f)
    
    # 读取原文任务
    with open(task_path, "r", encoding="utf-8") as f:
        task_data = json.load(f)
    
    segments = baihua_data.get("translations", [])
    original_segments = task_data.get("segments", task_data.get("texts", []))
    
    seg_count = len(segments)
    total_segments += seg_count
    
    for idx, seg in enumerate(segments, 1):
        original_preview = seg.get("original_preview", "")
        modern = seg.get("modern", "")
        section = seg.get("section", "")
        
        # 检查1: 小标题格式 - modern必须以【小标题】开头
        if not modern.startswith("【"):
            issues.append(f"段{idx}: modern未以【小标题】开头，开头为'{modern[:20]}'")
            all_pass = False
        else:
            bracket_end = modern.find("】")
            if bracket_end == -1:
                issues.append(f"段{idx}: 小标题缺少闭合】")
                all_pass = False
            else:
                title = modern[1:bracket_end].strip()
                if not title:
                    issues.append(f"段{idx}: 【】内小标题为空")
                    all_pass = False
        
        # 检查2: 义解完整性
        if "【义解】" not in modern:
            issues.append(f"段{idx}: 缺少【义解】标记")
            all_pass = False
        else:
            yijie_pos = modern.find("【义解】")
            yijie_content = modern[yijie_pos+4:].strip()
            if len(yijie_content) < 10:
                issues.append(f"段{idx}: 【义解】后内容过短，疑似空义解")
                all_pass = False
        
        # 检查8: original_preview不能改动 - 检查是否为空
        if not original_preview or len(original_preview.strip()) == 0:
            issues.append(f"段{idx}: original_preview为空")
            all_pass = False
        
        # 检查9: 乱码、PUA字符、空段、重复
        # PUA私用区: U+E000 - U+F8FF
        pua_pattern = re.compile(r'[\ue000-\uf8ff]')
        if pua_pattern.search(modern):
            issues.append(f"段{idx}: 包含PUA私用区字符")
            all_pass = False
        if not modern.strip():
            issues.append(f"段{idx}: modern内容为空")
            all_pass = False
        
        # 检查10: 现代网络用语
        modern_banned = ["yyds", "绝绝子", "emo", "打call", "躺平", "内卷", "芭比Q", "咱就是说", "家人们", "老铁", "666"]
        for word in modern_banned:
            if word in modern.lower():
                issues.append(f"段{idx}: 包含现代网络用语'{word}'")
                all_pass = False
        
        # 检查标点引号配对（中文引号「」、""）
        quote_pairs = [('「', '」'), ('『', '』'), ('"', '"'), ('"', '"'), ("'", "'")]
        for lq, rq in quote_pairs:
            lc = modern.count(lq)
            rc = modern.count(rq)
            if lc != rc:
                issues.append(f"段{idx}: 引号{lq}{rq}不配对（左{lc}个，右{rc}个）")
                all_pass = False
        
        # 检查是否有重复段落
        if idx > 1:
            prev_modern = segments[idx-2].get("modern", "")
            if modern.strip() == prev_modern.strip() and len(modern.strip()) > 20:
                issues.append(f"段{idx}: 与前一段内容完全重复")
                all_pass = False
        
        # 检查数字 - 简单查找天界年岁常见错误（人工复核为主）
        # 检查咒文：如果原文含咒，确认音译汉字
        # 这部分需要逐段人工通读
    
    all_issues[tid] = {
        "count": seg_count,
        "issues": issues
    }

# 现在逐经逐段人工通读核查
# 先打印每经段数确认总数63
print("各经段数统计：")
for tid in sutra_ids:
    print(f"  {tid}: {all_issues[tid]['count']}段")
print(f"总计: {total_segments}段")

# 逐经逐段输出内容供人工核查
