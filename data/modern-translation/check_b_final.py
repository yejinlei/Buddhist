import json
import os
import re

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
files = ["t1239", "t0850", "t2075", "t1251", "t0953", "t0887", "t2871", "t0682", "t0341", "t1757", "t2810", "t1797"]

# 问题分类统计
stats = {
    "套话义解无实质内容": 0,
    "小标题与段意不符": 0,
    "句末多余句号": 0,
    "梵咒被翻译": 0,
    "缺少义解/结构错误": 0,
    "无正文白话": 0,
    "original_preview篡改": 0
}

strict_cliche = [
    "此段為經文正文，繼續宣說佛法要義、修行法則與法門功德，行者當諦聽諦受依教奉行。",
    "此段宣說受持、讀誦、書寫、供養、為他人解說此經法門的殊勝功德利益，能滅罪生善、植菩提種、不退菩提、蒙佛授記。",
    "此段記載佛陀放光現瑞、大地震動等神變瑞相，預示將說殊勝大法，昭示法義深妙。",
    "此段開示菩薩行門，教令發菩提心、行六波羅蜜、四攝四無量，上求佛道下化眾生，積集福智資糧。"
]

all_issues = []

def check_segment(seg, file_id, seg_idx):
    issues = []
    modern = seg.get("modern", "")
    original = seg.get("original_preview", "")
    orig_len = len(original)
    
    # 结构解析
    parts = modern.split("\n")
    title = ""
    yijie = ""
    text_after = []
    step = 0
    
    for p in parts:
        ps = p.strip()
        if step == 0:
            if ps.startswith("【") and ps.endswith("】"):
                title = ps[1:-1]
                step = 1
            continue
        if step == 1:
            if ps.startswith("【义解】"):
                yijie = ps[4:].strip()
                step = 2
            continue
        if step == 2:
            text_after.append(p)
    
    text_str = "\n".join(text_after).strip()
    
    # 1. 结构缺失
    if step < 2:
        issues.append(("缺少义解/结构错误", f"{file_id}段{seg_idx}: 缺少【义解】或结构错误"))
        return issues
    if not text_str:
        issues.append(("无正文白话", f"{file_id}段{seg_idx}: 义解后无正文内容"))
    
    # 2. 义解套话
    if yijie in strict_cliche:
        issues.append(("套话义解无实质内容", f"{file_id}段{seg_idx}: 义解为通用模板，无针对本段的实质法义说明，义解内容：{yijie[:40]}..."))
    
    # 3. 小标题与段意不符
    is_listing_names = False
    if original.count("菩薩") >=3 and "菩薩、" in original:
        is_listing_names = True
    if original.count("龍王") >=2 or original.count("夜叉") >=2 or original.count("天王") >=2:
        if original.count("、") >=5:
            is_listing_names = True
    if title == "法義宣說" and is_listing_names:
        issues.append(("小标题与段意不符", f"{file_id}段{seg_idx}: 段落为罗列与会圣众/菩萨名号，小标题误用【法義宣說】，应为【聖眾雲集】类标题"))
    if title == "瑞相現前" and ("放光" not in original and "震動" not in original and "雨華" not in original and "天鼓" not in original):
        # 段落中没有瑞相内容
        if not any(k in original for k in ["光", "動", "華", "瑞", "變", "天"]):
            issues.append(("小标题与段意不符", f"{file_id}段{seg_idx}: 段落无瑞相内容，小标题误用【瑞相現前】"))
    
    # 4. 句末多余句号
    if text_str and original:
        olast = original.rstrip()[-1] if original.rstrip() else ""
        tlast = text_str.rstrip()[-1] if text_str.rstrip() else ""
        if olast in ["、", "，", "："] and text_str.rstrip().endswith(olast + "。"):
            issues.append(("句末多余句号", f"{file_id}段{seg_idx}: 原文以「{olast}」结尾，译文末尾多加句号变成「{olast}。」"))
        elif olast not in ["。", "！", "？", "」", "』", "…", "—", "”", "』", "」"] and tlast == "。":
            # 检查是否只是末尾多了句号：去掉末尾。后，与原文最后一字相同
            t_noperiod = text_str.rstrip()[:-1]
            if len(t_noperiod) > 0 and t_noperiod[-1] == olast:
                issues.append(("句末多余句号", f"{file_id}段{seg_idx}: 原文未结束，译文末尾错误多加句号"))
    
    # 5. 梵咒检查：原文有咒语，正文必须完全照录
    is_mantra = False
    if any(k in original for k in ["呪曰", "陀羅尼曰", "真言曰", "心呪："]):
        is_mantra = True
    mantra_chars = ["曩", "莫", "俱", "胝", "薩", "嚩", "爾", "唵", "吽", "娑婆訶", "莎訶"]
    mc_count = sum(1 for c in mantra_chars if c in original)
    if mc_count >= 3:
        is_mantra = True
    if is_mantra:
        for c in ["曩", "莫", "俱", "胝", "薩", "嚩", "爾", "唵", "吽"]:
            if original.count(c) > text_str.count(c) + 1:  # 允许个别误差，但不能差太多
                issues.append(("梵咒被翻译", f"{file_id}段{seg_idx}: 梵咒音译字「{c}」未照录，疑似被翻译"))
                break
    
    # 6. original_preview是否被修改？我们无法对比原始，但检查是否和text_after差太多（除了白话字替换）
    # 简单检查：original里的生僻专有名词是否在text里都有
    return issues

total = 0
for fid in files:
    path = os.path.join(base_dir, f"{fid}.json")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    trans = data.get("translations", [])
    total += len(trans)
    for i, seg in enumerate(trans):
        seg_issues = check_segment(seg, fid, i+1)
        for cat, msg in seg_issues:
            stats[cat] +=1
            all_issues.append((cat, msg))

print(f"=== B路复核结果：总段落数{total} ===")
print(f"总问题数：{len(all_issues)}")
print("\n问题分类统计：")
for cat, cnt in stats.items():
    if cnt >0:
        print(f"- {cat}: {cnt}处")

print("\n=== 典型问题示例 ===")
# 每类取3个例子
shown = set()
for cat, msg in all_issues:
    if cat not in shown:
        print(f"\n【{cat}】")
        count =0
        for c,m in all_issues:
            if c == cat and count <3:
                print(f"- {m}")
                count +=1
        shown.add(cat)
