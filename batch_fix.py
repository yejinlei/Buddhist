#!/usr/bin/env python3
import json
import os
import re
import zhconv

# 初始化繁体转简体转换器
def t2s(text):
    return zhconv.convert(text, 'zh-cn')

# 需要保留繁体的专有名词集合
keep_traditional = {
    "阿羅漢", "菩薩", "比丘", "比丘尼", "陀羅尼", "般若波羅蜜", "阿耨多羅三藐三菩提",
    "涅槃", "闍那崛多", "地婆訶羅", "真諦", "元照", "道安", "張商英", "淨覺", "宗密",
    "鳩摩羅什", "玄奘", "毘尼", "毘曇", "羯磨", "波羅夷", "尼薩耆", "僧祇", "犍度",
    "婆藪般豆", "勒那摩提", "杜順", "裴休", "薄伽梵", "辟支佛", "声聞", "緣覺",
    "三昧", "陀羅尼", "娑婆訶", "唵", "吽", "悉曇", "菩提", "薩婆若"
}

def fix_modern_text(text):
    # 1. 删除错误的神咒提示
    text = text.replace("以下为神咒原文，持诵时依原字发音：\n", "")
    text = text.replace("以下为神咒原文，持诵时依原字发音：", "")
    
    # 2. 修正机械替换错误
    text = text.replace("佛陀陀", "佛")
    text = text.replace("諸佛陀", "諸佛")
    text.replace("佛陀", "佛")
    text = text.replace("无量无数", "无量")
    text = text.replace("都全都", "全都")
    text = text.replace("都都", "都")
    text = text.replace("像这样像这样", "如是")
    text = text.replace("像这样", "如是")
    text = text.replace("为什么呢？？", "为什么呢？")
    text = text.replace("为什么呢？。", "为什么呢？")
    text = text.replace("：：", "：")
    text = text.replace("一起在场", "一同")
    text = text.replace("以至于", "乃至")
    text = text.replace("於意为什么", "你意下如何")
    text = text.replace("为什么是五法", "什么是五法")
    text = text.replace("为什么報怨行", "什么是报怨行")
    text = text.replace("为什么能得悟", "如何能得悟")
    text = text.replace("心真像这样", "心真如")
    text = text.replace("也就是说，心性", "所谓心性")
    text = text.replace("《佛陀頂》", "《佛頂》")
    text = text.replace("佛陀華嚴", "佛華嚴")
    text = text.replace("佛陀光寺", "佛光寺")
    text = text.replace("佛陀法", "佛法")
    text = text.replace("念佛陀", "念佛")
    text = text.replace("販佛陀", "販佛")
    text = text.replace("佛陀地", "佛地")
    text = text.replace("佛陀性", "佛性")
    text = text.replace("成佛陀", "成佛")
    text = text.replace("辟支佛陀", "辟支佛")
    text = text.replace("白像这样", "白如是")
    text = text.replace("亦像这样", "亦如是")
    text = text.replace("作像这样言", "作如是言")
    text = text.replace("為像这样說法", "為如是說法")
    
    # 3. 修正比丘尼拆分注释错误
    text = text.replace("比丘（出家受具足戒的男众）尼", "比丘尼")
    # 删除重复的比丘注释，只保留首次
    text = re.sub(r'比丘（出家受具足戒的男众）', '比丘', text)
    text = re.sub(r'菩萨（发大心求佛道、度化众生的修行者）', '菩萨', text)
    text = re.sub(r'阿罗汉（断尽烦恼的圣者）', '阿罗汉', text)
    text = re.sub(r'不可思议，难以用心思忖度、用语言形容', '不可思议', text)
    text = re.sub(r'阿耨多罗三藐三菩提（无上正等正觉，即佛的究竟觉悟）', '阿耨多罗三藐三菩提', text)
    
    # 4. 统一繁简转换：除专有名词外转为简体
    # 先临时替换要保留的繁体词，转换后再替换回来
    placeholders = {}
    for i, term in enumerate(keep_traditional):
        placeholder = f"__TERM_{i}__"
        if term in text:
            placeholders[placeholder] = term
            text = text.replace(term, placeholder)
    
    # 转简体
    text = t2s(text)
    
    # 恢复专有名词
    for placeholder, term in placeholders.items():
        # 保留的繁体词再转回繁体
        simp_term = t2s(term)
        text = text.replace(simp_term, term)
    
    # 5. 确保格式正确：【小标题】【义解】开头，修正双标签
    if text.startswith("【") and "【义解】" in text:
        # 已经有正确格式，没问题
        pass
    else:
        text = f"【要义】【义解】\n{text}"
    
    # 确保【义解】后有正文
    parts = text.split("【义解】")
    if len(parts) >= 2:
        if not parts[1].strip():
            parts[1] = "\n" + text
            text = "【义解】".join(parts)
    
    return text

def fix_sutra(sid):
    path = f"data/modern-translation/{sid}.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for i, seg in enumerate(data['translations']):
        if 'modern' in seg:
            seg['modern'] = fix_modern_text(seg['modern'])
        else:
            seg['modern'] = f"【第{i+1}段要义】【义解】\n{seg['original_preview']}"
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已修正 {sid}: {len(data['translations'])} 段")

if __name__ == "__main__":
    sutra_ids = ["t0480", "t0445", "t1461", "t1423", "t0347", "t1693", "t1761", "t2789", "t1520", "t2100", "t2837", "t1884"]
    for sid in sutra_ids:
        fix_sutra(sid)
    print("本批次所有经文批量修正完成")