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
            issues.append(f"[{filename}-第{seg_idx}段] {field_name}字段残留繁体「{trad}」→应改为「{simp}」")
    for wrong, correct in SPECIAL_TERMS.items():
        if wrong in text:
            issues.append(f"[{filename}-第{seg_idx}段] {field_name}字段术语错误「{wrong}」→应改为「{correct}」")

def check_mother(text, filename, seg_idx, field_name):
    """检查mother笔误"""
    if MOTHER_ERROR in text:
        issues.append(f"[{filename}-第{seg_idx}段] {field_name}字段残留笔误「mother」→应改为「{CORRECT_MOTHER}」")

def check_isolated_quotes_per_line(text, filename, seg_idx):
    """检查每一行是否有单独成行的孤立「或」，即该行只有引号没有内容"""
    lines = text.split('\n')
    for line_idx, line in enumerate(lines):
        stripped = line.strip()
        # 单独成行的开引号「
        if stripped == '「':
            issues.append(f"[{filename}-第{seg_idx}段] 存在孤立行首单独引号「（单独成行无内容）→应清除或补全引文")
        # 单独成行的闭引号」
        if stripped == '」':
            issues.append(f"[{filename}-第{seg_idx}段] 存在孤立结尾单独引号」（单独成行无内容）→检查上下文引号配对，补全开引号或删除多余闭引号")

def check_yijie_mark(text, filename, seg_idx):
    """检查每段modern是否有【义解】标记"""
    if "【义解】" not in text:
        issues.append(f"[{filename}-第{seg_idx}段] modern字段缺少【义解】标记→应补充义解部分")

def check_section_simplified(section_text, filename, seg_idx):
    """检查小标题（section字段）是否是简体中文，没有繁体残留"""
    for trad, simp in TRADITIONAL_RESIDUAL.items():
        if trad in section_text:
            issues.append(f"[{filename}-第{seg_idx}段] 小标题「{section_text}」残留繁体「{trad}」→应改为简体「{simp}」")

def check_mode(mode_val, filename):
    """检查mode字段是否是baihua"""
    if mode_val != "baihua":
        issues.append(f"[{filename}] mode字段为「{mode_val}」→应保持为「baihua」（注：此建议按要求视为无效建议，仅记录）")

def check_punctuation_simple(text, filename, seg_idx):
    """只检查括号配对，引号因为佛经跨段引文属于正常现象，不按单段计数检查，只检查单独成行的孤立引号"""
    # 检查括号配对：中文括号（）
    open_paren = text.count('（')
    close_paren = text.count('）')
    if open_paren != close_paren:
        issues.append(f"[{filename}-第{seg_idx}段] 中文括号（）不配对：开{open_paren}个，闭{close_paren}个→检查补全")
    open_bracket = text.count('[')
    close_bracket = text.count(']')
    if open_bracket != close_bracket:
        issues.append(f"[{filename}-第{seg_idx}段] 方括号[]不配对：开{open_bracket}个，闭{close_bracket}个→检查补全")
    # 检查句子断裂：即段落中间出现无意义的半截？无法自动判断，跳过
    
def check_preview_integrity(preview_text, filename, seg_idx):
    """检查original_preview是否有简体字（原文是繁体，出现简体说明被改动），按要求此类建议无效仅记录"""
    simp_chars_in_preview = []
    for trad, simp in TRADITIONAL_RESIDUAL.items():
        if simp in preview_text:
            simp_chars_in_preview.append(simp)
    if simp_chars_in_preview:
        issues.append(f"[{filename}-第{seg_idx}段] original_preview疑似被改动，出现简体字{','.join(simp_chars_in_preview)}→应恢复原文繁体（注：此建议按要求视为无效建议，仅记录）")

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
            # 检查original_preview完整性
            check_preview_integrity(original_preview, fname, seg_idx)
            
            # 2. 检查mother笔误
            check_mother(modern_text, fname, seg_idx, "modern")
            
            # 3. 检查段首孤立引号（单独成行的）
            check_isolated_quotes_per_line(modern_text, fname, seg_idx)
            
            # 4. 检查【义解】标记
            check_yijie_mark(modern_text, fname, seg_idx)
            
            # 6. 检查新引入问题：括号不配对
            check_punctuation_simple(modern_text, fname, seg_idx)
    
    # 输出结果
    invalid_suggestions = [i for i in issues if "无效建议" in i or "不采纳" in i]
    valid_issues = [i for i in issues if "无效建议" not in i and "不采纳" not in i]
    
    print(f"共发现有效问题 {len(valid_issues)} 个，无效建议 {len(invalid_suggestions)} 个")
    print("="*50)
    if not valid_issues and not invalid_suggestions:
        print("本批12部经修正到位，未引入新错误，复核通过")
    else:
        if valid_issues:
            print("复核发现以下待修正问题：")
            for issue in valid_issues:
                print(f"- {issue}")
        if invalid_suggestions:
            print("\n以下为按要求不采纳的建议（original_preview/mode修改类）：")
            for issue in invalid_suggestions:
                print(f"- {issue}")

if __name__ == "__main__":
    main()
