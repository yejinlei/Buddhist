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

# 严格义解套话列表
strict_cliche = {
    "此段宣說受持、讀誦、書寫、供養、為人解說此經法門的殊勝功德，能滅罪生善、不退菩提、蒙佛授記。",
    "此段開示菩薩行門，教令發菩提心、行六波羅蜜、四攝四無量，上求佛道下化眾生，積集福智二種資糧。",
    "此段為經文正文，繼續宣說佛法要義、修行法則與法門功德，行者當諦聽諦受依教奉行。",
    "此段記載佛陀放光現瑞、大地震動等神變瑞相，預示將說殊勝大法，昭示法義深妙。",
}

# 非严格套话：以"此段續明經中所說法義，記載"开头的截取式义解（也不合格，因为只是把原文开头几个字塞进去，没有法义说明）
def is_bad_yijie(yijie):
    if yijie in strict_cliche:
        return "严格通用套话"
    # "此段續明經中所說法義，記載"开头 + 截取原文 + "等內容，行者當諦聽諦受，依教奉行。"结尾
    if yijie.startswith("此段續明經中所說法義，記載"):
        if "等內容" in yijie and "依教奉行" in yijie:
            return "截取原文凑数式义解，无法义说明"
        if len(yijie) < 50:
            return "义解过短，仅截取原文开头，无实质法义说明"
    # 明显内容不符：
    if "禪師之開示" in yijie or "宗門直指" in yijie or "機緣問答" in yijie or "見性成佛" in yijie:
        # 这是禅宗内容模板，需要检查经文是否是禅宗典籍
        return "义解内容与经文属性错配（误用禅宗模板）"
    if "結壇" in yijie or "壇場" in yijie:
        return "义解内容可能错配"
    if "瑞相" in yijie or "放光" in yijie:
        return "义解内容可能错配（指为瑞相段但实际不是）"
    return None

def title_mismatch(title, original, yijie):
    """检查小标题是否错配"""
    issues = []
    # 【瑞相現前】必须有瑞相内容
    if title == "瑞相現前" or "瑞相" in title:
        rui_keys = ["放光", "震動", "雨華", "天鼓", "光明", "大地震", "眉间", "白毫", "瑞", "神變", "天樂", "華", "地動"]
        rui_count = sum(1 for k in rui_keys if k in original)
        if rui_count < 2:
            issues.append(f"小标题【{title}】错配：段落无瑞相内容（放光/震动/雨华等）")
    # 【受持功德】必须是讲功德/利益
    if title == "受持功德" or "功德" in title:
        gongde_keys = ["功德", "福", "善", "利益", "受持", "讀誦", "書寫", "供養", "滅罪", "授記"]
        gk_count = sum(1 for k in gongde_keys if k in original)
        if gk_count == 0 and ("大將" in original or "元帥" in original or "阿吒" in original or "菩薩行" in original):
            # t1239第9段是元帅召鬼神，不是受持功德
            if "召" in original or "瞋怒" in original or "鎧甲" in original or "悉備" in original:
                issues.append(f"小标题【{title}】错配：段为阿吒薄俱元帅召集鬼神/示现威德，非受持功德")
    # 【禪宗機緣】/【宗門】类必须是禅宗典籍
    if "禪" in title or "機緣" in title or "宗門" in title:
        # 如果是陀罗尼经、密教经，错配
        if "陀羅尼" in original or "真言" in original or "呪曰" in original or "金剛" in original or "曼荼羅" in original:
            issues.append(f"小标题【{title}】错配：密教经/陀罗尼经不应使用禅宗机缘类标题")
    return issues

all_problems = []
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
        
        # 义解问题
        bad = is_bad_yijie(yijie)
        if bad:
            all_problems.append((seg_id, f"【义解问题-类型：{bad}】{yijie[:80]}"))
        
        # 小标题错配
        tm = title_mismatch(title, original, yijie)
        for t in tm:
            all_problems.append((seg_id, t))
        
        # 义解后无白话
        if not body:
            all_problems.append((seg_id, "义解后无白话正文"))
        
        # 梵咒问题
        is_mantra = any(k in original for k in ["呪曰", "陀羅尼曰", "真言曰", "心呪", "即說呪曰"])
        core = ["唵", "吽", "娑婆訶", "莎訶", "曩莫", "怛姪他", "跢姪他", "娑嚩賀", "娑嚩（二合）賀"]
        if is_mantra and body:
            for cc in core:
                if cc in original and cc not in body:
                    all_problems.append((seg_id, f"梵咒音译「{cc}」未照录，疑似被白话化"))
                    break
        
        # original_preview异常
        if len(original) < 10 and len(seg.get("modern","")) > 100:
            all_problems.append((seg_id, "original_preview异常短，疑似被篡改"))
        
        # 阙文保留
        ori_que = original.count("□") + original.count("〔闕〕")
        if ori_que > 0 and body:
            body_que = body.count("□") + body.count("（阙）") + body.count("〔阙〕")
            if body_que < ori_que - 2:
                all_problems.append((seg_id, f"原文有{ori_que}处阙文，白话中阙文保留不足"))

print(f"===== B路终轮复核：共发现{len(all_problems)}处问题 =====\n")
# 按经分类统计
from collections import defaultdict
by_file = defaultdict(list)
for sid, msg in all_problems:
    fid = sid.split()[0]
    by_file[fid].append((sid, msg))

for fid in files:
    probs = by_file.get(fid, [])
    print(f"\n===== {fid}: {len(probs)}处问题 =====")
    for sid, msg in probs[:20]:
        print(f"  - [{sid}] {msg}")
    if len(probs) > 20:
        print(f"  ...（共{len(probs)}处，其余省略）")
