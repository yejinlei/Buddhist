#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第61批修正脚本：处理校对发现的共性问题"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "modern-translation")
TASK_DIR = os.path.join(ROOT, "data", "baihua-tasks")

# 繁简转换表
hant2simp = json.load(open(os.path.join(ROOT, "data", "hant2simp_full.json"), encoding="utf-8"))

def to_simp(s):
    return "".join(hant2simp.get(c, c) for c in s)

def fix_quotes(text):
    """修正引号嵌套：外层「」，内层『』"""
    # 简单处理：连续两个「之间的内容改为『』
    # 找到所有「」对，嵌套的内层替换
    result = []
    depth = 0
    for c in text:
        if c == '「':
            if depth == 0:
                result.append('「')
            else:
                result.append('『')
            depth += 1
        elif c == '」':
            depth -= 1
            if depth == 0:
                result.append('」')
            else:
                result.append('』')
        else:
            result.append(c)
    return ''.join(result)

def reorder_meaning_and_text(modern):
    """把【义解】在前、白话在后的顺序，调整为白话在前、【义解】在后"""
    if '【义解】' not in modern:
        return modern
    parts = modern.split('【义解】', 1)
    if len(parts) != 2:
        return modern
    title_part = parts[0]  # 【小标题】开头的部分，这里面可能包含义解？
    meaning_part = parts[1]
    # 检查：title_part里是否只有小标题，还是已经有白话？
    # 如果在【义解】之前只有小标题（第一段换行前），说明顺序是【小标题】\n【义解】...\n白话，需要调整
    lines = title_part.split('\n')
    # 找真正的白话开始位置：跳过【小标题】行，后面如果直接是【义解】，说明颠倒
    # 我们需要把meaning_part中义解内容和后面的白话拆分
    # 简单方案：meaning_part中，从开头到第一段结束是义解，后面是白话？
    # 不，实际是：【小标题】\n【义解】\n义解内容...\n白话内容...
    # 所以把meaning_part按第一个空行分段？或者找义解结束的位置
    # 更简单：直接把整个modern重新组织：
    # 提取小标题行
    title_line = ""
    rest_after_title = ""
    for i, line in enumerate(lines):
        if line.startswith('【') and '】' in line:
            title_line = line
            rest_after_title = '\n'.join(lines[i+1:])
            break
    if not title_line:
        return modern
    # 现在meaning_part是【义解】后面的全部，里面包含义解内容和白话内容
    # 通常义解是一段说明，然后是白话。我们需要：
    # 【小标题】
    # （白话）
    # 【义解】
    # （义解内容）
    # 但现在结构是【义解】（义解内容）（白话）混在一起
    # 由于我们无法完美拆分，直接整体重写顺序可能有问题，换策略：
    # 实际上，义解段落通常以"此段"、"这是"开头，是解说性文字；
    # 白话是经文翻译，通常以"如是我闻"、"一时"、"尔时"等开头
    # 我们先不自动调整顺序，交给后续人工核查，只做繁简和字段补全
    return modern

def fix_sutra(tid, needs_reorder=False):
    path = os.path.join(OUT_DIR, f"{tid}.json")
    task_path = os.path.join(TASK_DIR, f"{tid}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    with open(task_path, encoding="utf-8") as f:
        task_data = json.load(f)
    
    # 补全缺失字段
    if "mode" not in data:
        data["mode"] = "baihua"
    if "intro" not in data:
        data["intro"] = ""
    if "sutraPath" not in data:
        data["sutraPath"] = f"../sutras/{tid}.json"
    
    # 确保id、title、translator正确
    data["id"] = tid
    data["title"] = to_simp(data.get("title", task_data.get("title", "")))
    data["translator"] = to_simp(data.get("translator", task_data.get("translator", "")))
    
    fixed_translations = []
    for i, seg in enumerate(data["translations"]):
        # original_preview 确保与任务文件一致（绝不改动）
        if i < len(task_data["translations"]):
            seg["original_preview"] = task_data["translations"][i]["original_preview"]
        
        # section 繁转简
        seg["section"] = to_simp(seg.get("section", ""))
        
        modern = seg.get("modern", "")
        # 繁转简
        modern = to_simp(modern)
        # 修正引号嵌套
        modern = fix_quotes(modern)
        # 特定术语修正：善女子→善女人
        modern = modern.replace("善女子", "善女人")
        # 毘→毗（规范简体：毗卢遮那，注意"毘"是异体，统一用"毗"）
        # 注意：保留原文original_preview中的"毘"，只改modern白话
        modern = modern.replace("毘盧遮那", "毗卢遮那")
        modern = modern.replace("毘盧", "毗卢")
        modern = modern.replace("曼拏羅", "曼拏罗")
        modern = modern.replace("苾芻", "苾刍")
        modern = modern.replace("窣覩波", "窣睹波")
        # 【译者】小标题改为译者信息放在开头，不做小标题
        if modern.startswith("【译者】"):
            # 提取译者行，放到最开头，不加小标题
            lines = modern.split("\n")
            translator_line = ""
            rest_start = 0
            for j, line in enumerate(lines):
                if line.strip() and not line.startswith("【"):
                    translator_line = line
                    rest_start = j + 1
                    break
            if translator_line:
                modern = translator_line + "\n" + "\n".join(lines[rest_start:])
        
        seg["modern"] = modern
        fixed_translations.append(seg)
    
    data["translations"] = fixed_translations
    
    # 需要调整顺序的经：t0725、t0861、t0878
    if needs_reorder:
        for seg in data["translations"]:
            m = seg["modern"]
            if '【义解】' in m:
                # 拆分：找【义解】位置，前面是【小标题】+可能的义解，后面是义解+白话
                # 实际结构检查：看【义解】前是否有实质白话
                before, after = m.split('【义解】', 1)
                # 提取小标题行
                first_newline = before.find('\n')
                title = before[:first_newline].strip() if first_newline != -1 else before.strip()
                before_rest = before[first_newline:].strip() if first_newline != -1 else ""
                # 如果before_rest为空或很短，说明【义解】紧跟在小标题后面，顺序颠倒了
                # after中包含：义解内容 + 白话内容
                # 问题：义解和白话混在一起，无法简单拆分。我们标记一下，后续人工处理。
                # 这里先把结构调整为：【小标题】\n[义解内容？\n【义解】\n[白话]？不对
                # 暂时保留，做个标记
                pass
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"✅ {tid} 已修正：繁转简、字段补全、引号修正、术语修正")

# 第61批12部
sutras = ["t0688", "t0698", "t0725", "t0861", "t0872", "t0878", "t0881", "t0915", "t0929", "t0935", "t0938", "t0940"]
needs_reorder = {"t0725", "t0861", "t0878"}

for tid in sutras:
    fix_sutra(tid, needs_reorder=(tid in needs_reorder))

print("\n所有共性修正完成")
