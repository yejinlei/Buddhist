import json, os, re

sutra_ids = ["t2029","t1022b","t1107","t2174a","t2174","t1309","t1392","t1164","t1090","t1377","t1125","t1132"]
trans_dir = "data/modern-translation"

# 繁简转换表（说明文字用，咒文/原文引录部分不转）
# 策略：我们只转换【小标题】和【义解】后的说明文字，对于换行后大段引用原文（咒文/梵赞）的部分不转换
# 实际上modern的结构是：【小标题】【义解】白话说明... 然后换行是大段原文咒文（逐字照录）
# 所以我们只转换【义解】后到第一个换行之前的文字，换行后的原文不转换

fan_to_jian = {
    # 佛教专有名词（非音译字的部分转简体，音译字按规范简化）
    "釋迦": "释迦",
    "沙門": "沙门",
    "尸師": "尸师",
    "須賴": "须赖",
    "菩薩": "菩萨",
    "薩埵": "萨埵",
    "聲聞": "声闻",
    "緣覺": "缘觉",
    "龍": "龙",
    "藥叉": "药叉",
    "羅剎": "罗刹",
    "陀羅尼": "陀罗尼",
    "阿闍梨": "阿阇梨",
    "毘盧遮那": "毗卢遮那",
    "摩訶": "摩诃",
    "金剛": "金刚",
    "薩": "萨",
    "羅": "罗",
    "訶": "诃",
    "闍": "阇",
    "毘": "毗",
    "頂": "顶",
    "經": "经",
    "誦": "诵",
    "軌": "轨",
    "禳災": "禳灾",
    "明鏡": "明镜",
    "請益": "请益",
    "法師": "法师",
    "後記": "后记",
    "國": "国",
    "寺": "寺",
    "長者": "长者",
    "瑠璃": "琉璃",
    "硨磲": "砗磲",
    "須彌": "须弥",
    "灌頂": "灌顶",
    "蓮華": "莲华",
    "波羅蜜": "波罗蜜",
    "羅睺羅": "罗睺罗",
    "阿難": "阿难",
    "龍眾": "龙众",
    "阿修羅": "阿修罗",
    "迦樓羅": "迦楼罗",
    "呪": "咒",
    "儀軌": "仪轨",
    "禎子": "帧子",
    "摩伽陀國": "摩伽陀国",
    "那爛陀寺": "那烂陀寺",
    "憍睒彌國": "憍赏弥国",
    "門": "门",
    "師": "师",
    "賴": "赖",
    "難": "难",
    "曼荼羅": "曼荼罗",
    "聞": "闻",
    "聲": "声",
}

def convert_explain_text(text):
    """只转换【义解】后到第一个换行间的说明文字为简体，换行后的原文/咒文不转换"""
    # 找到【义解】的位置
    yijie_pos = text.find("【义解】")
    if yijie_pos == -1:
        return text
    
    # 找到【义解】后第一个换行的位置
    explain_start = yijie_pos + len("【义解】")
    newline_pos = text.find("\n", explain_start)
    
    if newline_pos == -1:
        # 没有换行，整个后面都是说明文字
        explain = text[explain_start:]
        rest = ""
    else:
        explain = text[explain_start:newline_pos]
        rest = text[newline_pos:]
    
    # 转换说明文字中的繁体为简体，长词优先
    for old, new in sorted(fan_to_jian.items(), key=lambda x: -len(x[0])):
        explain = explain.replace(old, new)
    
    return text[:explain_start] + explain + rest

def replace_unique(s, old, new, desc):
    count = s.count(old)
    if count == 0:
        print(f"  [跳过] 未找到: {desc}")
        return s
    if count > 1:
        print(f"  [警告] 找到{count}处: {desc}，替换第一处")
    print(f"  [修复] {desc}")
    return s.replace(old, new, 1)

for sid in sutra_ids:
    print(f"\n最终修复 {sid}...")
    path = os.path.join(trans_dir, f"{sid}.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for i, seg in enumerate(data["translations"]):
        m = seg["modern"]
        
        # ===== 专项问题修复 =====
        if sid == "t2029" and i == 0:
            # 补"说说"讹字说明
            if "青苑地方有修学比丘" in m and "原文" not in m.split("\n")[0]:
                m = replace_unique(m, "在青苑地方有修学比丘", "在青苑（原文「說說」疑似衍文或讹字，依文义译）地方有修学比丘", "t2029补讹字说明")
            # 补失译题记说明
            if "此经译者失载" not in m:
                m = replace_unique(m, "【义解】", "【义解】此经译者失载，历代经录附于西晋录。", "t2029补失译说明")
        
        if sid == "t1022b":
            # 删除冗余"都"字
            m = replace_unique(m, "都皆大欢喜", "皆大欢喜", "t1022b删除冗余「都」")
        
        if sid == "t2174a":
            # 修正"祯子"为"帧子"
            m = m.replace("禎子", "帧子")
            m = m.replace("祯子", "帧子")
            print(f"  [修复] t2174a段{i}修正「祯子」为「帧子」")
        
        if sid == "t1309":
            # 修正重复标题"虚宿？虚宿？"
            m = m.replace("虚宿？虚宿？", "虚宿？")
            # 补"七俱知"讹字说明（在提到七俱胝准提的段）
            if "七俱知" in m or "七俱胝准提" in m:
                if "原文" not in m:
                    m = m.replace("七俱胝准提陀罗尼", "七俱胝准提陀罗尼（原文「知」为「胝」之形近讹字）")
            # 补"嘴宿"讹字说明
            if "觜宿直日" in m and "原文" not in m:
                m = m.replace("觜宿直日（原文「嘴」为「觜」之俗字）", "觜宿直日（原文「嘴」为「觜」之俗字）")
            # 补漏译"女"字，如果还没补的话
            if "过了三天还不好，就会死亡" in m:
                m = m.replace("过了三天还不好，就会死亡", "过了三天还不好，女人就会死亡")
                print(f"  [修复] t1309补漏译「女」字")
        
        if sid == "t1125":
            # 三密金刚加注
            if "三密金刚" in m and "原文" not in m:
                m = m.replace("三密金刚", "三密金刚（原文「蜜」通「密」）")
        
        # ===== 系统繁简转换说明文字 =====
        m = convert_explain_text(m)
        
        seg["modern"] = m
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{sid} 最终修复完成")

print("\n所有最终修复完成")
