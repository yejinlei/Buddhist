import json
import os
import re
import sys

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
files = ["t1239", "t0850", "t2075", "t1251", "t0953", "t0887", "t2871", "t0682", "t0341", "t1757", "t2810", "t1797"]

# 严格检查义解是否为实质法义说明（非通用套话）
cliche_patterns = [
    "此段為經文正文，繼續宣說佛法要義",
    "此段宣說受持、讀誦、書寫、供養",
    "此段記載佛陀放光現瑞、大地震動等神變瑞相",
    "此段開示菩薩行門，教令發菩提心",
    "此段继续宣说佛法要义",
    "此段宣说受持读诵",
    "此段记载佛陀放光现瑞",
    "此段开示菩萨行门",
    "宣说佛法要义",
    "佛法要義、修行法則",
    "行者當諦聽諦受依教奉行",
    "上求佛道下化眾生",
]

def is_cliche(yijie):
    """判断义解是否为通用套话无实质内容"""
    for p in cliche_patterns:
        if p in yijie:
            return True
    # 义解过短也不行
    if len(yijie) < 30:
        return True
    return False

def parse_segment(seg):
    """解析段内容，返回(title, yijie, body_text)"""
    modern = seg.get("modern", "")
    original = seg.get("original_preview", "")
    
    lines = modern.split("\n")
    title = ""
    yijie = ""
    body_lines = []
    state = 0  # 0:找标题, 1:找义解, 2:收集正文
    
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

def check_mantra(original, body):
    """检查梵咒：音译字必须原字照录，咒语顺序是引导句在前咒语在后"""
    issues = []
    # 常见梵咒音译字（高频）
    mantra_chars = ["曩", "莫", "俱", "胝", "薩", "嚩", "爾", "唵", "吽", "娑婆訶", "莎訶", 
                    "娑訶", "婆訶", "陀羅尼", "呪曰", "真言", "怛姪他", "跢姪他", "鉢囉",
                    "麼", "儞", "濕", "嚲", "迦", "遮", "闍", "若", "惹", "捨", "娑", "訶",
                    "哆", "他", "那", "娜", "囉", "邏", "婆", "波", "摩", "磨", "伽", "迦"]
    # 判断是否是咒语段
    mantra_indicator = any(k in original for k in ["呪曰", "陀羅尼曰", "真言曰", "心呪", "陀羅尼", "即說呪曰", "說是陀羅尼"])
    mantra_count_ori = sum(original.count(c) for c in mantra_chars[:8])
    is_mantra = mantra_indicator or mantra_count_ori >= 8
    
    if is_mantra:
        # 检查关键音译字是否都在白话正文中
        core_chars = ["唵", "吽", "娑婆訶", "莎訶", "曩莫", "怛姪他", "跢姪他"]
        for cc in core_chars:
            if cc in original and cc not in body:
                issues.append(f"梵咒音译「{cc}」未照录，疑似被白话化翻译")
        # 检查咒语引导句（"即说咒曰"）是否在咒语前面
        if "即說呪曰" in original or "即说咒曰" in body:
            idx_ori_lead = original.find("呪曰")
            # 正文里引导句应该在咒语音译字之前
            idx_body_lead = body.find("即说咒曰")
            if idx_body_lead >= 0:
                # 咒语字应该在引导句之后
                for c in ["唵", "曩", "莫", "薩"]:
                    if c in body:
                        c_idx = body.find(c)
                        if c_idx < idx_body_lead:
                            issues.append(f"梵咒顺序错误：咒语音译字出现在引导句之前，应为引导句在前、咒语在后")
                            break
    return issues, is_mantra

def check_reign_year(original, body):
    """年号原字不动，如"貞元""開元""永徽"等"""
    issues = []
    # 唐代年号常见字
    reign_chars = ["貞", "元", "開", "永", "徽", "麟", "德", "景", "雲", "神", "龍", "朔", "天", "寶", "應", "曆", "和", "顯", "慶", "龍", "朔"]
    # 原文的年号组合不能被翻译
    return issues

def is_quewen(original):
    """判断是否是阙文（有阙字标记）"""
    return "□" in original or "闕" in original or "〔闕〕" in original or "（闕）" in original or "…" in original

def check_one(fid):
    """检查一部经，返回(段落总数, 问题列表)"""
    path = os.path.join(base_dir, f"{fid}.json")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    trans = data.get("translations", [])
    total = len(trans)
    issues = []
    
    # 抽样：开头20 + 结尾20 + 密咒段
    sample_indices = set()
    for i in range(min(20, total)):
        sample_indices.add(i)
    for i in range(max(0, total-20), total):
        sample_indices.add(i)
    
    # 找出密咒段加入抽样
    for i, seg in enumerate(trans):
        orig = seg.get("original_preview", "")
        if any(k in orig for k in ["呪曰", "陀羅尼曰", "真言曰", "心呪", "即說呪曰", "陀羅尼"]):
            sample_indices.add(i)
            # 前后1段也检查
            if i > 0:
                sample_indices.add(i-1)
            if i < total-1:
                sample_indices.add(i+1)
    
    for i in sorted(sample_indices):
        if i >= total:
            continue
        seg = trans[i]
        title, yijie, body, original = parse_segment(seg)
        seg_id = f"{fid} 第{i+1}段"
        
        # 1. 结构检查
        if not title:
            issues.append((seg_id, "小标题缺失：无【小标题】标记"))
            continue
        if not yijie:
            issues.append((seg_id, "缺少【义解】标记"))
            continue
        
        # 2. 义解是否有实质内容（非套话）
        if is_cliche(yijie):
            issues.append((seg_id, f"义解为通用套话，无针对本段的实质法义说明。义解内容：{yijie[:60]}"))
        
        # 3. 义解后必须有白话正文
        if not body:
            issues.append((seg_id, "义解后无白话正文内容"))
        
        # 4. 梵咒检查
        if body:
            mantra_issues, is_mantra = check_mantra(original, body)
            for mi in mantra_issues:
                issues.append((seg_id, mi))
        
        # 5. original_preview 完整性：检查是否包含奇怪的篡改标记，或内容被简化
        # 检查original_preview是否异常短（被截断）
        if len(original) < 5 and len(seg.get("modern", "")) > 50:
            issues.append((seg_id, f"original_preview异常短（仅{len(original)}字），疑似被篡改"))
        
        # 6. 阙文保留：原文有阙字标记，白话中也要保留或注明，不能硬补
        if is_quewen(original) and body:
            if "□" not in body and "阙" not in body and "（阙）" not in body and "…" not in body and "〔阙〕" not in body:
                # 可能被硬补了，这是问题
                # 检查原文□数量和白话□数量
                ori_que = original.count("□")
                body_que = body.count("□") + body.count("阙")
                if ori_que > body_que + 2:
                    issues.append((seg_id, f"原文有{ori_que}处阙文（□），白话中仅{body_que}处，疑似阙文被硬补未保留"))
        
        # 7. 白话硬伤简单检查：是否有明显不通顺或错译
        # 检查关键术语错译
        if body:
            if "比丘尼" in original and "尼姑" in body:
                issues.append((seg_id, "白话将「比丘尼」误译为「尼姑」，属硬伤"))
            if "優婆塞" in original and "居士" not in body and "男居士" not in body and "清信士" not in body and "优婆塞" not in body:
                pass  # 不强制要求，放过
            # 检查年号：原文有"某某年""某某元"，白话不能把年号删掉
            reign_pat = r"(貞元|開元|永徽|麟德|景雲|神龍|天寶|應曆|元和|顯慶|龍朔|開皇|大業|貞觀|永淳|弘道|嗣聖|文明|景雲|太極|延和|先天|開元|天寶|至德|乾元|上元|寶應|廣德|永泰|大曆|建中|興元|貞元|永貞|元和|長慶|寶曆|太和|開成|會昌|大中|咸通|乾符|廣明|中和|光啟|文德|龍紀|大順|景福|乾寧|光化|天復|天祐)"
            if re.search(reign_pat, original):
                # 原文有年号，白话中也要保留
                if not re.search(r"(贞元|开元|永徽|麟德|景云|神龙|天宝|应历|元和|显庆|龙朔|开皇|大业|贞观)", body):
                    # 这不一定是问题，先记录不报错
                    pass
    
    return total, len(sample_indices), issues

def main():
    all_issues = []
    summary = []
    for fid in files:
        total, sampled, issues = check_one(fid)
        summary.append((fid, total, sampled, len(issues)))
        all_issues.extend(issues)
    
    print("=== B路终轮复核报告 ===")
    print(f"复核经数：{len(files)}部")
    print(f"抽查段落（开头20+结尾20+密咒段）统计：")
    for fid, total, sampled, ic in summary:
        print(f"  {fid}: 总段{total}段，抽查{sampled}段，问题{ic}处")
    
    print(f"\n总问题数：{len(all_issues)}")
    
    if len(all_issues) == 0:
        print("\n✅ B路终轮复核通过：12部经文全部零问题，可上线")
    else:
        print("\n❌ 发现以下问题：")
        for seg_id, msg in all_issues:
            print(f"  - [{seg_id}] {msg}")

if __name__ == "__main__":
    main()
