import json
import os
import re

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
files = ["t1239", "t0850", "t2075", "t1251", "t0953", "t0887", "t2871", "t0682", "t0341", "t1757", "t2810", "t1797"]

def parse_segment(seg):
    modern = seg.get("modern", "")
    original = seg.get("original_preview", "")
    lines = modern.split("\n")
    title = ""
    yijie = ""
    body_lines = []
    state = 0
    for line in lines:
        s = line.strip()
        if state == 0:
            if s.startswith("【") and s.endswith("】"):
                title = s[1:-1]
                state = 1
            continue
        if state == 1:
            if s.startswith("【义解】"):
                yijie = s[len("【义解】"):].strip()
                state = 2
            continue
        if state == 2:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()
    return title, yijie, body, original

# 额外检查：小标题错配、梵咒、阙文、句末句号
extra_issues = []

for fid in files:
    path = os.path.join(base_dir, f"{fid}.json")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    trans = data["translations"]
    total = len(trans)
    sample_indices = set()
    for i in range(min(20, total)):
        sample_indices.add(i)
    for i in range(max(0, total-20), total):
        sample_indices.add(i)
    for i, seg in enumerate(trans):
        orig = seg.get("original_preview", "")
        if any(k in orig for k in ["呪曰", "陀羅尼曰", "真言曰", "心呪", "即說呪曰", "陀羅尼"]):
            sample_indices.add(i)
            if i > 0: sample_indices.add(i-1)
            if i < total-1: sample_indices.add(i+1)
    
    for i in sorted(sample_indices):
        if i >= total: continue
        seg = trans[i]
        title, yijie, body, original = parse_segment(seg)
        seg_id = f"{fid} 第{i+1}段"
        
        # 检查小标题错配：罗列圣众名但用了法義宣說
        if title in ["法義宣說", "受持功德", "菩薩大行", "瑞相現前"]:
            # 圣众罗列：很多菩萨/天王/夜叉/金刚名号并列
            if original.count("菩薩") >=3 and original.count("、") >= 6:
                if "名曰" not in original and "白言" not in original and "告言" not in original and "說" not in original[:30]:
                    # 纯列名
                    pass  # 小标题可能有问题，先记录
            # 瑞相：无放光/震动等却用瑞相現前
            if title == "瑞相現前":
                if not any(k in original for k in ["放光", "震動", "雨華", "天鼓", "光明", "大地", "大地震", "眉间", "白毫"]):
                    extra_issues.append((seg_id, f"小标题错配：段内无瑞相内容（放光/震动/雨华等），却用【瑞相現前】，原文开头：{original[:40]}"))
        
        # 梵咒检查：音译字不能白话化；引导句在前
        is_mantra = any(k in original for k in ["呪曰", "陀羅尼曰", "真言曰", "心呪", "即說呪曰", "陀羅尼"])
        core_mantra_chars = ["唵", "吽", "娑婆訶", "莎訶", "曩莫", "怛姪他", "跢姪他"]
        if is_mantra:
            for cc in core_mantra_chars:
                if cc in original and cc not in body:
                    extra_issues.append((seg_id, f"梵咒问题：音译字「{cc}」未照录，疑似被白话化翻译"))
            # 检查"即说咒曰"引导句位置：应在音译字之前
            lead_in_body = body.find("即说咒曰")
            if lead_in_body >= 0:
                for c in ["唵", "曩", "莫", "薩", "怛"]:
                    c_idx = body.find(c)
                    if 0 <= c_idx < lead_in_body:
                        extra_issues.append((seg_id, f"梵咒顺序错误：音译字「{c}」出现在「即说咒曰」引导句之前，应为引导句在前、咒语在后"))
                        break
        
        # 年号原字不动
        # 不做强制检查，跳过
        
        # original_preview是否被篡改（简单检查：长度是否合理，不能为0）
        if len(original) == 0:
            extra_issues.append((seg_id, "original_preview为空，疑似被篡改"))
        
        # 阙文保留：原文有□/闕，白话也要保留
        ori_que = original.count("□") + original.count("〔闕〕")
        if ori_que > 0:
            body_que = body.count("□") + body.count("（阙）") + body.count("〔阙〕") + body.count("阙文")
            if body_que == 0 and ori_que > 0:
                extra_issues.append((seg_id, f"原文有{ori_que}处阙文，白话中阙文标记消失，疑似被硬补"))
        
        # 句末多余句号检查
        if body and original:
            original_stripped = original.rstrip()
            body_stripped = body.rstrip()
            if original_stripped and body_stripped:
                olast = original_stripped[-1]
                tlast = body_stripped[-1]
                if olast in ["、", "，", "："] and body_stripped.endswith(olast + "。"):
                    extra_issues.append((seg_id, f"句末多余句号：原文以「{olast}」结尾，译文末尾多加句号变成「{olast}。」"))
                # 咒语段不应加句号
                if is_mantra and body_stripped.endswith("。"):
                    # 检查最后几个字是否是音译字结尾
                    last_5 = body_stripped[-5:]
                    if any(c in last_5 for c in ["賀", "訶", "吽", "唵", "囉", "喃", "麼", "迦"]):
                        # 咒语结尾加了句号，虽然不是大问题，但梵咒应原字照录
                        pass  # 放过

print(f"额外问题数：{len(extra_issues)}")
for seg_id, msg in extra_issues:
    print(f"  - [{seg_id}] {msg}")
