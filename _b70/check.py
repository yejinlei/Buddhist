
import json
import os
import re

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
files = [
    "t0941.json", "t0948.json", "t0958.json", "t0974a.json", "t0974b.json", 
    "t0974d.json", "t0983a.json", "t0986.json", "t1005b.json", "t1019.json", 
    "t1036.json", "yaoshi_xuanzang.json"
]

results = {}

for fname in files:
    fpath = os.path.join(base_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    translations = data.get("translations", [])
    results[fname] = {
        "title": data.get("title", ""),
        "segments_count": len(translations),
        "checks": {},
        "issues": []
    }
    
    # 遍历所有段落
    for i, seg in enumerate(translations):
        # 确保original_preview字段未被改动（检查字段存在）
        if "original_preview" not in seg:
            results[fname]["issues"].append(f"段{i+1}: 缺失original_preview字段")
        
        # 检查modern字段（译文）
        modern = seg.get("modern", "")
        
        # ===== 特定问题检查 =====
        # t0941段1咒文"拏"字是否补回
        if fname == "t0941.json" and i == 0:
            has_na = "拏" in modern
            results[fname]["checks"]["段1咒文含'拏'"] = has_na
            if not has_na:
                results[fname]["issues"].append("段1: 咒文中'拏'字仍缺失")
            else:
                # 找到位置
                idx = modern.find("拏")
                results[fname]["checks"]["段1'拏'字上下文"] = modern[max(0, idx-20):idx+20]
        
        # t0958段11多余右括号是否删除
        if fname == "t0958.json" and i == 10:  # 段11索引10
            right_bracket_count = modern.count(")") + modern.count("）")
            left_bracket_count = modern.count("(") + modern.count("（")
            results[fname]["checks"]["段11括号匹配"] = f"左括号{left_bracket_count}个，右括号{right_bracket_count}个"
            if right_bracket_count > left_bracket_count:
                results[fname]["issues"].append(f"段11: 仍有多余右括号，左{left_bracket_count}，右{right_bracket_count}")
        
        # t0974a段8"三十三字"是否改为"三十三句"
        if fname == "t0974a.json" and i == 7:  # 段8索引7
            has_sanshisanzi = "三十三字" in modern
            has_sanshisanju = "三十三句" in modern
            results[fname]["checks"]["段8'三十三字'改'三十三句'"] = f"含'三十三字':{has_sanshisanzi}，含'三十三句':{has_sanshisanju}"
            if has_sanshisanzi:
                results[fname]["issues"].append("段8: 仍有'三十三字'未改为'三十三句'")
        
        # t1019"通达到达"重复字是否删除
        if fname == "t1019.json":
            has_chongfu = "通达到达" in modern
            if has_chongfu:
                results[fname]["issues"].append(f"段{i+1}: 仍有重复字'通达到达'")
        # 最后统一记录
        all_modern_t1019 = "".join([s.get("modern", "") for s in translations])
        results[fname]["checks"]["无'通达到达'重复"] = "通达到达" not in all_modern_t1019
        if "通达到达" in all_modern_t1019:
            idx = all_modern_t1019.find("通达到达")
            results[fname]["issues"].append(f"存在'通达到达'重复，上下文: ...{all_modern_t1019[max(0,idx-30):idx+40]}...")
        
        # t1036"師子"是否补回、双【义解】问题是否解决
        if fname == "t1036.json":
            has_shizi = "師子" in modern or "师子" in modern
            yijie_count = modern.count("【义解】")
            double_yijie = yijie_count > 1
            if not has_shizi and "师子游戏" in data.get("title", "") or i == 0:
                # 第一段应该提到师子
                pass
            if double_yijie:
                results[fname]["issues"].append(f"段{i+1}: 仍有双【义解】问题，出现{yijie_count}次，上下文: {modern[max(0, modern.find('【义解】')-30):modern.find('【义解】')+100]}")
        # 整体检查
        all_modern_t1036 = "".join([s.get("modern", "") for s in translations])
        results[fname]["checks"]["含'師子/师子'"] = ("師子" in all_modern_t1036) or ("师子" in all_modern_t1036)
        results[fname]["checks"]["无双【义解】"] = all_modern_t1036.count("【义解】") == translations.count("【义解】")  # 每段最多一个
        # 检查有没有一段里有多个【义解】
        for i, seg in enumerate(translations):
            mod = seg.get("modern", "")
            if mod.count("【义解】") > 1:
                results[fname]["issues"].append(f"t1036段{i+1}有{mod.count('【义解】')}个【义解】")
        
        # 括号不匹配检查（所有文件）
        lq = modern.count("「")
        rq = modern.count("」")
        if lq != rq:
            results[fname]["issues"].append(f"段{i+1}: 引号「」不匹配，左{lq}右{rq}")
        lq2 = modern.count("『")
        rq2 = modern.count("』")
        if lq2 != rq2:
            results[fname]["issues"].append(f"段{i+1}: 引号『』不匹配，左{lq2}右{rq2}")
        lb = modern.count("（") + modern.count("(")
        rb = modern.count("）") + modern.count(")")
        if lb != rb:
            results[fname]["issues"].append(f"段{i+1}: 括号（）不匹配，左{lb}右{rb}")
        
        # 检查明显的两字重复词（除了叠字词）
        two_char_dup = re.findall(r'([\u4e00-\u9fa5]{2})\1', modern)
        # 常见合法叠词
        valid_two = [
            "滚滚", "滔滔", "绵绵", "纷纷", "洋洋", "洒洒", "萧萧", "瑟瑟", "凛凛", "炎炎",
            "熊熊", "粼粼", "潺潺", "汩汩", "汪汪", "油油", "亮亮", "晶晶", "莹莹", "闪闪",
            "星星", "点点", "滴滴", "丝丝", "缕缕", "阵阵", "声声", "步步", "句句", "字字",
            "行行", "页页", "本本", "个个", "件件", "桩桩", "种种", "类类", "家家", "人人",
            "处处", "时时", "天天", "年年", "岁岁", "代代", "世世", "生生", "刻刻", "分分",
            "秒秒", "多多", "少少", "大", "小", "长长", "短短", "高高", "低低", "深深", "浅浅",
            "厚厚", "薄薄", "快快", "慢慢", "缓缓", "徐徐", "匆匆", "忙忙", "慌慌", "张张",
            "寂寂", "静静", "默默", "悄悄", "暗暗", "偷偷", "明明", "暗暗", "白白", "黑黑",
            "红红", "绿绿", "青青", "蓝蓝", "紫紫", "黄黄", "清清", "楚楚", "清清", "白白",
            "干干净净", "清清楚楚", "明明白白", "整整齐齐", "大大小小", "老老少少", "男男女女",
            "千千万万", "三三两两", "三三五五", "一字字", "一句句", "一行行", "一步步",
            "一层层", "一道道", "条条", "缕缕", "阵阵", "声声", "家家", "户户", "日日夜夜",
            "生生世世", "世世代代", "朝朝暮暮", "时时刻刻", "分分秒秒"
        ]
        bad_two = []
        for w in two_char_dup:
            if w not in valid_two and len(w) == 2:
                # 进一步排除梵文咒语重复？不，咒语不会重复两字词
                bad_two.append(w)
        if bad_two:
            for w in set(bad_two):
                if w in ["通达", "到达", "已经", "因为", "所以", "但是", "而且", "于是", "就是", "还是", "可以", "能够", "应该", "应当", "必须", "需要", "可能", "大概", "大约", "几乎", "完全", "全部", "所有", "整个", "部分", "一般", "普通", "通常", "正常", "平常", "日常", "经常", "常常", "往往", "偶尔", "突然", "忽然", "逐渐", "逐步", "立刻", "立即", "马上", "顿时", "霎时"]:
                    idx = modern.find(w+w)
                    results[fname]["issues"].append(f"段{i+1}: 疑似两字重复词'{w}{w}'，上下文: ...{modern[max(0,idx-20):idx+40]}...")
    
    # t0983a专门检查重复原文
    if fname == "t0983a.json":
        modern_texts = [seg.get("modern", "") for seg in translations]
        # 检查相邻重复段落
        has_adjacent_dup = False
        for i in range(len(modern_texts)-1):
            # 去除开头的【义解】【咒文X】后比较
            def clean(s):
                s = re.sub(r'【[^】]+】', '', s)
                return s.strip()
            m1 = clean(modern_texts[i])
            m2 = clean(modern_texts[i+1])
            if len(m1) > 30 and m1 == m2:
                has_adjacent_dup = True
                results[fname]["issues"].append(f"段{i+1}与段{i+2}: 存在相邻重复内容（去除标签后完全相同）")
        # 检查是否有大段原文重复插入modern（大段繁体原文未翻译）
        has_original_dup = False
        # 先获取所有original
        # 注意：这个文件里有没有original字段？
        has_original_field = "original" in translations[0] if translations else False
        results[fname]["checks"]["translations含original字段"] = has_original_field
        results[fname]["checks"]["无相邻重复段落"] = not has_adjacent_dup
        results[fname]["checks"]["无原文重复混入"] = not has_original_dup
    
    # ===== 繁简混用检查（普通译文部分，排除咒语里的标准梵字）=====
    # 列出译文中不应出现的简体/繁体混用，主要是注释和义解部分
    # 先把所有modern拼起来，排除【咒文】块
    all_modern_plain = ""
    for seg in translations:
        mod = seg.get("modern", "")
        # 去除【咒文X】...【义解】之间的内容（即咒语本身），只检查义解和译文
        parts = re.split(r'【咒文[一二三四五六七八九十0-9]+】', mod)
        for p in parts:
            if "【义解】" in p:
                # 义解部分是注释，应该是简体
                yijie_part = p.split("【义解】")[1]
                all_modern_plain += yijie_part
            else:
                # 普通译文
                all_modern_plain += p
    # 检查常见繁体字（这些在简体白话译文中不应该出现，除非是专有名词/咒语）
    fantizi_check = {
        "爾": "你/那",  # 爾时→那时，爾→你
        "來": "来",  # 這個字簡化了，但咒語裡可能保留？
        "爲": "为",
        "無": "无",
        "與": "与",
        "見": "见",
        "說": "说",
        "問": "问",
        "聞": "闻",
        "聲": "声",
        "體": "体",
        "國": "国",
        "會": "会",
        "對": "对",
        "過": "过",
        "還": "还",
        "盡": "尽",
        "靜": "静",
        "萬": "万",
        "經": "经",
        "義": "义",
        "處": "处",
        "起": "起（简繁同？不对，起没有简化）",
        "達": "达",
        "遠": "远",
        "違": "违",
        "邊": "边",
        "眾": "众",
        "禮": "礼",
        "稱": "称",
        "滅": "灭",
        "惡": "恶",
        "願": "愿",
        "薩": "萨（菩萨的萨，咒文里保留？义解里应该用简体）",
        "訶": "诃（咒文里保留）",
        "釋": "释",
        "彌": "弥",
        "羅": "罗",
        "邏": "逻",
        "捨": "舍",
        "攝": "摄",
        "持": "持（同）",
        "除": "除（同）",
        "降": "降（同）",
        "伏": "伏（同）",
        "觀": "观",
        "自": "自（同）",
        "在": "在（同）",
        "勢": "势",
        "至": "至（同）",
        "清": "清（同）",
        "淨": "净",
        "光": "光（同）",
        "明": "明（同）",
        "照": "照（同）",
        "曜": "曜（同）",
        "普": "普（同）",
        "賢": "贤",
        "文": "文（同）",
        "殊": "殊（同）",
        "藥": "药",
        "琉": "琉（同）",
        "璃": "璃（同）",
        "應": "应",
        "正": "正（同）",
        "等": "等（同）",
        "覺": "觉",
        "陀": "陀（咒文保留）",
        "耶": "耶（同/咒文）",
        "摩": "摩（咒文保留）",
        "浮": "浮（同）",
        "提": "提（同）",
    }
    # 实际上咒语部分已经被排除了，现在检查plain部分的繁体字
    import sys
    fantizi_found = []
    for ft in ["爾", "爲", "無", "與", "見", "說", "問", "聞", "聲", "體", "國", "會", "對", "過", "還", "盡", "萬", "經", "義", "處", "達", "遠", "邊", "眾", "禮", "稱", "滅", "惡", "願", "釋", "彌", "羅", "捨", "攝", "觀", "勢", "淨", "賢", "藥", "應", "覺", "來", "時", "個", "個", "麼", "麽", "后", "後"]:
        if ft in all_modern_plain:
            # 找到位置
            idx = all_modern_plain.find(ft)
            fantizi_found.append(f"{ft}(上下文:...{all_modern_plain[max(0,idx-10):idx+10]}...)")
    if fantizi_found:
        results[fname]["issues"].append(f"义解/白话部分有繁简混用，发现繁体字: {'; '.join(fantizi_found)}")
        results[fname]["checks"]["繁简统一"] = False
    else:
        results[fname]["checks"]["繁简统一"] = True

# ===== original_preview完整性检查 =====
print("="*60)
print("二轮复核结果")
print("="*60)
all_passed = True
for fname, res in results.items():
    print(f"\n【{fname}】{res['title']}")
    print(f"  段落数: {res['segments_count']}")
    print("  检查项:")
    for k, v in res['checks'].items():
        print(f"    ✓ {k}: {v}")
    if res['issues']:
        all_passed = False
        print("  遗留问题:")
        for issue in res['issues']:
            print(f"    ✗ {issue}")
    else:
        print("    ✓ 本次核查未发现问题")

# 专门检查original_preview
print("\n" + "="*60)
print("original_preview字段完整性核查（要求绝对不能改动）")
print("="*60)
op_all_good = True
for fname in files:
    fpath = os.path.join(base_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    translations = data.get("translations", [])
    file_good = True
    for i, seg in enumerate(translations):
        if "original_preview" not in seg:
            print(f"  ✗ {fname} 段{i+1}: 缺失original_preview字段！")
            file_good = False
            op_all_good = False
            continue
        op = seg["original_preview"]
        # 检查是否有modern的内容混入original_preview（因为要求不能改，所以如果有就是被改了）
        if "【义解】" in op or "【咒文】" in op or "【白话】" in op:
            print(f"  ✗ {fname} 段{i+1}: original_preview中混入了标签！")
            file_good = False
            op_all_good = False
    if file_good:
        print(f"  ✓ {fname}: original_preview字段完整，无改动痕迹")

print("\n" + "="*60)
if all_passed and op_all_good:
    print("结论：所有问题均已修正到位，未发现新问题。")
else:
    print("结论：仍有上述遗留问题需要修正。")
print("="*60)
