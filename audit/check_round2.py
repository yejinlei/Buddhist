#!/usr/bin/env python3
import json
import os
import re

BASE_DIR = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
FILES = [
    "t0983a.json", "t1113a.json", "t1113b.json", "t1120b.json",
    "t1134a.json", "t1156a.json", "t1156b.json", "t1168b.json",
    "t1302.json", "t1303.json", "t1304.json", "t1313.json"
]

# 需要检查的残留繁体字映射：繁体→正确简体
TRADITIONAL_RESIDUAL = {
    "萬": "万", "難": "难", "會": "会", "緣": "缘", "輪": "轮", "說": "说",
    "羅": "罗", "壽": "寿", "護": "护", "壇": "坛", "場": "场", "觀": "观",
    "種": "种", "調": "调", "愛": "爱", "題": "题", "記": "记", "寫": "写",
    "懺": "忏", "盡": "尽", "滅": "灭", "無": "无", "來": "来", "虛": "虚",
    "聲": "声", "斷": "断", "體": "体", "廣": "广", "國": "国"
}
SPECIAL_TERMS = {
    "毘": "毗",
    "苾刍": "比丘",
    "曼陀罗": "曼荼罗"
}
MOTHER_ERROR = "mother"
CORRECT_MOTHER = "摩多"

issues = []

def check_traditional_chars(text, filename, seg_idx, field_name):
    """检查modern字段中的残留繁体字"""
    for trad, simp in TRADITIONAL_RESIDUAL.items():
        if trad in text:
            # 排除咒语音译部分？不，用户明确要求这些字必须修正
            issues.append(f"[{filename}-第{seg_idx}段] {field_name}字段残留繁体「{trad}」→应改为「{simp}」")
    for wrong, correct in SPECIAL_TERMS.items():
        if wrong in text:
            issues.append(f"[{filename}-第{seg_idx}段] {field_name}字段术语错误「{wrong}」→应改为「{correct}」")

def check_mother(text, filename, seg_idx, field_name):
    """检查mother笔误"""
    if MOTHER_ERROR in text:
        issues.append(f"[{filename}-第{seg_idx}段] {field_name}字段残留笔误「mother」→应改为「{CORRECT_MOTHER}」")

def check_isolated_quotes(text, filename, seg_idx):
    """检查段首孤立的「」引号，即段落开头只有「或者」，没有配对"""
    lines = text.split('\n')
    for line_idx, line in enumerate(lines):
        stripped = line.strip()
        # 检查行首只有「没有」的情况，或者行尾只有」没有「配对的情况？用户说段首孤立「」引号
        # 孤立的「：就是段落开头单独一个「，后面没有内容或者没有闭合
        if stripped == '「' or stripped.startswith('「') and stripped.endswith('」') == False and '」' not in stripped[1:]:
            # 可能是多行引号？但用户说段首孤立，比如单独一行「或者」
            pass
        # 更精确：检查有没有单独成行的「或者」
        if stripped == '「':
            issues.append(f"[{filename}-第{seg_idx}段] 存在孤立行首引号「→应清除或补全内容")
        if stripped == '」':
            # 结尾单独的」，如果前面没有配对开头？可能是前一段没闭合？
            issues.append(f"[{filename}-第{seg_idx}段] 存在孤立结尾引号」→检查引号配对，补全或清除")

def check_yijie_mark(text, filename, seg_idx):
    """检查每段modern是否有【义解】标记"""
    if "【义解】" not in text:
        issues.append(f"[{filename}-第{seg_idx}段] modern字段缺少【义解】标记→应补充义解部分")

def check_section_simplified(section_text, filename, seg_idx):
    """检查小标题（section字段）是否是简体中文，没有繁体残留"""
    # 检查section里有没有繁体字
    for trad, simp in TRADITIONAL_RESIDUAL.items():
        if trad in section_text:
            issues.append(f"[{filename}-第{seg_idx}段] 小标题「{section_text}」残留繁体「{trad}」→应改为简体「{simp}」")

def check_mode(mode_val, filename):
    """检查mode字段是否是baihua"""
    if mode_val != "baihua":
        issues.append(f"[{filename}] mode字段为「{mode_val}」→应保持为「baihua」（注：此建议按要求视为无效建议，仅记录）")

def check_punctuation(text, filename, seg_idx):
    """检查标点问题：括号不匹配、引号不配对、句子断裂、JSON错误（由json.loads保证，这里检查文本内）"""
    # 检查括号配对：中文括号（）、[]、{}
    open_paren = text.count('（')
    close_paren = text.count('）')
    if open_paren != close_paren:
        issues.append(f"[{filename}-第{seg_idx}段] 中文括号（）不配对：开{open_paren}个，闭{close_paren}个→检查补全")
    open_bracket = text.count('[')
    close_bracket = text.count(']')
    if open_bracket != close_bracket:
        issues.append(f"[{filename}-第{seg_idx}段] 方括号[]不配对：开{open_bracket}个，闭{close_bracket}个→检查补全")
    # 检查「」引号配对
    open_quote = text.count('「')
    close_quote = text.count('」')
    if open_quote != close_quote:
        issues.append(f"[{filename}-第{seg_idx}段] 中文引号「」不配对：开{open_quote}个，闭{close_quote}个→检查补全或清除孤立引号")
    # 检查句子有没有明显断裂：比如结尾没有标点，或者半截话？这个难以自动判断，先不做
    
def main():
    for fname in FILES:
        fpath = os.path.join(BASE_DIR, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            issues.append(f"[{fname}] JSON解析错误：{str(e)}→修正JSON语法错误")
            continue
        except Exception as e:
            issues.append(f"[{fname}] 文件读取错误：{str(e)}")
            continue
        
        # 检查mode字段
        check_mode(data.get('mode', ''), fname)
        
        # 检查翻译段
        translations = data.get('translations', [])
        for seg_idx, seg in enumerate(translations, 1):
            modern_text = seg.get('modern', '')
            section_text = seg.get('section', '')
            original_preview = seg.get('original_preview', '')
            
            # 1. 检查modern中的残留繁体和错误术语
            check_traditional_chars(modern_text, fname, seg_idx, "modern")
            # 检查section中的繁体
            check_section_simplified(section_text, fname, seg_idx)
            # original_preview本来就是繁体原文，不需要检查繁体，只需要确认没被改动？用户要求original_preview保持原文连续子串不被改动
            # 这个我们无法自动验证是否是原文，因为没有对照原文，只能检查有没有被改成简体？不，original_preview应该是繁体原文，如果里面有简体字说明被改动了？
            # 对，original_preview应该是古籍原文，是繁体，如果出现简体字说明被改动了。但用户说"original_preview是否仍保持为原文连续子串、未被改动"，改original_preview的建议视为无效，所以我们只记录，但注明不采纳
            # 不过先检查original_preview里有没有简体修改的痕迹，比如出现我们刚才列表里的简体字
            simp_chars_in_preview = []
            for trad, simp in TRADITIONAL_RESIDUAL.items():
                if simp in original_preview:
                    simp_chars_in_preview.append(simp)
            if simp_chars_in_preview:
                issues.append(f"[{fname}-第{seg_idx}段] original_preview疑似被改动，出现简体字{','.join(simp_chars_in_preview)}→应恢复原文繁体（注：此建议按要求视为无效建议，仅记录）")
            
            # 2. 检查mother笔误
            check_mother(modern_text, fname, seg_idx, "modern")
            
            # 3. 检查段首孤立引号
            check_isolated_quotes(modern_text, fname, seg_idx)
            
            # 4. 检查【义解】标记
            check_yijie_mark(modern_text, fname, seg_idx)
            
            # 6. 检查新引入问题：标点、括号、引号不配对
            check_punctuation(modern_text, fname, seg_idx)
    
    # 输出结果
    if not issues:
        print("本批12部经修正到位，未引入新错误，复核通过")
    else:
        print("复核发现以下问题：")
        for issue in issues:
            if "无效建议" in issue:
                print(f"- {issue}（不采纳）")
            else:
                print(f"- {issue}")

if __name__ == "__main__":
    main()
