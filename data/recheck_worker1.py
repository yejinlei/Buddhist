import json
import os
import re

translation_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
sutras_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/sutras/"
sutra_ids = ["t0131", "t0102", "t1046", "t1379", "t0560", "t0096", "t2836", "t0655", "t0934", "t0218", "t1405", "t0779"]

issues = []

def add(sutra, seg, desc):
    issues.append((sutra, str(seg), desc))

def is_siddham(c):
    return 0x100000 <= ord(c) <= 0x10FFFD

for sutra_id in sutra_ids:
    # 读译文
    trans_path = os.path.join(translation_dir, f"{sutra_id}.json")
    try:
        with open(trans_path, 'r', encoding='utf-8') as f:
            trans_data = json.load(f)
    except Exception as e:
        add(sutra_id, "全局", f"译文文件读取失败: {e}")
        continue
    
    # 读原文
    sutra_path = os.path.join(sutras_dir, f"{sutra_id}.json")
    try:
        with open(sutra_path, 'r', encoding='utf-8') as f:
            sutra_data = json.load(f)
    except Exception as e:
        add(sutra_id, "全局", f"原文文件读取失败: {e}")
        continue
    
    segs = trans_data.get("translations", [])
    orig_segs = sutra_data.get("content", [])
    
    # 检查section字段
    if "section" not in trans_data:
        add(sutra_id, "全局", "缺少section字段")
    else:
        sections = trans_data["section"]
        if not sections or not isinstance(sections, list):
            add(sutra_id, "全局", "section字段为空或格式错误")
    
    for idx, seg in enumerate(segs):
        segnum = idx + 1
        modern = seg.get("modern","") or ""
        preview = seg.get("original_preview","") or ""
        section = seg.get("section","")
        
        # 检查original_preview是否非空
        if not preview.strip():
            add(sutra_id, segnum, "original_preview为空")
            continue
        
        # 检查是否以【小标题】开头
        if not modern.startswith("【"):
            add(sutra_id, segnum, f"段未以【小标题】开头，段首为：{modern[:20]}")
        else:
            head_match = re.match(r'^【([^】]+)】', modern)
            if not head_match:
                add(sutra_id, segnum, f"段首小标题标签不完整：{modern[:20]}")
            else:
                title = head_match.group(1)
                # 小标题字数检查，通常4-8字？先记录超长或过短
                if len(title) < 2 or len(title) > 12:
                    add(sutra_id, segnum, f"小标题字数异常：「{title}」（{len(title)}字）")
        
        # 检查是否有【义解】
        yj_count = modern.count("【义解】")
        if yj_count == 0:
            add(sutra_id, segnum, "缺少【义解】标签")
        elif yj_count > 1:
            add(sutra_id, segnum, f"出现{yj_count}次【义解】标签")
        else:
            yj_pos = modern.find("【义解】")
            after_yj = modern[yj_pos + len("【义解】"):].strip()
            if not after_yj:
                add(sutra_id, segnum, "【义解】后无内容")
            else:
                # 检查义解后是否有正文白话文（不是直接全是咒文原文）
                # 先看有没有原文照录标记，之前的部分应该有白话
                orig_mark = re.search(r"原文照录如下[：:]?", after_yj)
                if orig_mark:
                    baihua_part = after_yj[:orig_mark.start()].strip()
                    if len(baihua_part) < 10:
                        add(sutra_id, segnum, f"【义解】后白话文过短（{len(baihua_part)}字），疑似缺少正文翻译")
                else:
                    # 没有原文照录标记，看后面是否有足够白话，或者直接是咒文
                    # 统计梵字和汉字
                    sid_count = len([c for c in after_yj if is_siddham(c)])
                    han_count = len([c for c in after_yj if '\u4e00' <= c <= '\u9fff'])
                    if sid_count > han_count and han_count < 20:
                        add(sutra_id, segnum, "【义解】后直接是咒文，缺少正文白话文翻译")
        
        # 检查咒文部分：如果preview中有梵字或音译咒，检查modern中是否完整
        # 提取preview中的梵字
        p_sid = [c for c in preview if is_siddham(c)]
        m_sid = [c for c in modern if is_siddham(c)]
        if p_sid:
            if len(m_sid) < len(p_sid):
                add(sutra_id, segnum, f"梵字缺失：原文{len(p_sid)}字，译文{len(m_sid)}字，漏{len(p_sid)-len(m_sid)}字")
            elif m_sid != p_sid:
                # 检查是否有差异
                diff = False
                for a,b in zip(m_sid, p_sid):
                    if a != b:
                        diff = True
                        break
                if diff:
                    add(sutra_id, segnum, "梵字与原文不一致")
        
        # 检查咒文中的汉字音译是否完整（含反切、二合等注音）
        # 查找preview中的二合、引、反等标记，看modern中是否存在
        mantra_marks_p = re.findall(r'(二合|三合|引|反|去声|上声|半音)', preview)
        mantra_marks_m = re.findall(r'(二合|三合|引|反|去声|上声|半音)', modern)
        if len(mantra_marks_p) > len(mantra_marks_m) + 2:
            add(sutra_id, segnum, f"咒文注音标记缺失：原文{len(mantra_marks_p)}处，译文{len(mantra_marks_m)}处，可能漏录音注")
        
        # 检查original_preview是否被修改：对照原文对应段的content
        # 先找原文中对应的段
        # 简单匹配：preview应该是原文某段的开头
        found = False
        for orig_seg in orig_segs:
            orig_text = orig_seg.get("text","") or orig_seg.get("content","") or ""
            if preview in orig_text or orig_text.startswith(preview[:20]):
                found = True
                break
        # 不强制匹配，因为可能分段不同，但记录明显不一致
        # 先跳过，后续逐段看

# 输出结果
for s,seg,d in issues:
    print(f"- 经号：{s}，段号：{seg}，问题：{d}")

if not issues:
    print("自动检查未发现明显格式问题")
