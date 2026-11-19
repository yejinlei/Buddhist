#!/usr/bin/env python3
import json
import os
import re

SUTRA_IDS = ['t0131', 't0102', 't1046', 't1379', 't0560', 't0096', 't2836', 't0655', 't0779', 't0934', 't0218', 't1405']
BASE_TRANS = 'data/modern-translation'
BASE_ORIG = 'data/baihua-tasks'

def check_sutra_detailed(tid):
    trans_path = os.path.join(BASE_TRANS, f'{tid}.json')
    orig_path = os.path.join(BASE_ORIG, f'{tid}.json')
    
    trans_data = json.load(open(trans_path))
    orig_data = json.load(open(orig_path))
    
    trans_segs = trans_data['translations']
    orig_segs = orig_data['translations']
    
    sutra_issues = []
    
    for idx, (tseg, oseg) in enumerate(zip(trans_segs, orig_segs)):
        seg_num = idx + 1
        modern = tseg.get('modern', '').strip()
        orig_preview_t = tseg.get('original_preview', '')
        orig_preview_o = oseg.get('original_preview', '')
        
        # 检查1：modern以【小标题】开头
        if not modern.startswith('【'):
            sutra_issues.append(f'第{seg_num}段：modern不以【小标题】开头，首字为「{modern[0] if modern else "空"}」')
        else:
            close_bracket = modern.find('】')
            if close_bracket == -1:
                sutra_issues.append(f'第{seg_num}段：小标题缺少闭合】')
            else:
                title_part = modern[1:close_bracket]
                if not title_part:
                    sutra_issues.append(f'第{seg_num}段：小标题为空')
        
        # 检查2：包含【义解】且义解后有内容
        if '【义解】' not in modern:
            sutra_issues.append(f'第{seg_num}段：缺少【义解】标记')
        else:
            yijie_pos = modern.find('【义解】')
            after_yijie = modern[yijie_pos+len('【义解】'):]
            next_mark_pos = after_yijie.find('【')
            if next_mark_pos == -1:
                yijie_content = after_yijie.strip()
            else:
                yijie_content = after_yijie[:next_mark_pos].strip()
            if len(yijie_content) < 3:
                sutra_issues.append(f'第{seg_num}段：【义解】后内容为空或过短（仅{len(yijie_content)}字符）')
        
        # 检查3：咒文段照录原文
        # 咒文特征字
        mantra_keywords = ['咒', '陀羅尼', '真言', '莎訶', '娑訶', '薩婆訶', '梭哈', '陀羅尼曰', '呪曰']
        is_mantra_segment = any(kw in orig_preview_o for kw in mantra_keywords) and not any(kw in orig_preview_o for kw in ['聞如是', '一時', '佛告', '佛言', '當時', '爾時'])
        
        # 提取原文中可能的咒文内容（通常是音译汉字，带反切注音）
        # 查找是否有梵音译特征：带反切（X反）、二合、引等注音标记
        has_fanqie = '反）' in orig_preview_o or '二合' in orig_preview_o or '（引）' in orig_preview_o or '反）' in orig_preview_o
        
        # 如果是咒文段（有音译/反切），检查modern中是否照录了音译部分
        if has_fanqie:
            # 提取一段音译文本（连续音译字）
            # 从原文中找有音译特征的片段
            mantra_chars = re.findall(r'[\u4e00-\u9fff（）引二合反]{6,}', orig_preview_o)
            # 取最长的一段作为咒文片段
            if mantra_chars:
                longest_mantra = max(mantra_chars, key=len)
                # 清理：取核心音译部分（8-15字）
                sample = longest_mantra[2:12]
                if sample not in modern:
                    sutra_issues.append(f'第{seg_num}段：原文含咒语音译（含反切/二合标记），但白话文中未完整照录原字，咒文片段「{sample}」未在modern中出现')
        
        # 检查4：original_preview一字不差
        if orig_preview_t != orig_preview_o:
            min_len = min(len(orig_preview_t), len(orig_preview_o))
            diff_pos = -1
            for i in range(min_len):
                if orig_preview_t[i] != orig_preview_o[i]:
                    diff_pos = i
                    break
            if diff_pos == -1:
                diff_pos = min_len
                sutra_issues.append(f'第{seg_num}段：original_preview长度不一致（译文{len(orig_preview_t)}字/原文{len(orig_preview_o)}字），在位置{diff_pos}处截断/多字')
            else:
                t_ctx = orig_preview_t[max(0,diff_pos-5):diff_pos+8].replace('\n','\\n')
                o_ctx = orig_preview_o[max(0,diff_pos-5):diff_pos+8].replace('\n','\\n')
                sutra_issues.append(f'第{seg_num}段：original_preview第{diff_pos}字有误，译文侧「{t_ctx}」≠原文侧「{o_ctx}」')
        
        # 检查5：白话文通顺与错译
        has_zhengwen = '【正文】' in modern
        has_zhouwen = '【咒文】' in modern or '【咒语】' in modern
        
        if not has_zhengwen and not has_zhouwen and not has_fanqie:
            sutra_issues.append(f'第{seg_num}段：缺少【正文】或【咒文】标记')
        
        if has_zhengwen:
            zw_pos = modern.find('【正文】')
            zhengwen = modern[zw_pos+4:].strip()
            # 去除末尾可能的标记（如果有的话）
            next_mark = zhengwen.find('【')
            if next_mark != -1:
                zhengwen = zhengwen[:next_mark].strip()
            
            # 正文过短检查（咒文段可以短，但非咒文应足够长）
            if not has_fanqie and len(zhengwen) < 15:
                sutra_issues.append(f'第{seg_num}段：【正文】后内容过短（仅{len(zhengwen)}字符），内容为「{zhengwen[:30]}」')
            
            # 检查是否有明显文言残留未翻译（纯文言片段）
            # 检查明显错译：如"比丘尼"译成"比丘"等
            # 检查连续重复
            repeat_match = re.search(r'(.)\1{4,}', zhengwen)
            if repeat_match:
                sutra_issues.append(f'第{seg_num}段：正文出现连续重复字「{repeat_match.group()[:10]}」')
            
            # 检查是否有未闭合引号
            open_quotes = zhengwen.count('「') - zhengwen.count('」')
            dq_open = zhengwen.count('"') - zhengwen.count('"')
            if open_quotes != 0:
                pass  # 引号可能跨段，不报错
        
        # 检查是否存在所有段section都相同的问题（可能是结构错误）
    
    return sutra_issues

# 手动逐经输出详细内容辅助复核
for tid in SUTRA_IDS:
    trans_data = json.load(open(f'{BASE_TRANS}/{tid}.json'))
    orig_data = json.load(open(f'{BASE_ORIG}/{tid}.json'))
    print(f'{"="*60}')
    print(f'  {tid} - {trans_data["title"]}')
    print(f'{"="*60}')
    for idx, (tseg, oseg) in enumerate(zip(trans_data['translations'], orig_data['translations'])):
        print(f'--- 第{idx+1}段 [{tseg.get("section","")}] ---')
        print(f'原文预览({len(oseg["original_preview"])}字): {oseg["original_preview"][:80]}...')
        m = tseg['modern']
        print(f'白话文({len(m)}字):')
        # 输出modern前几行概要
        lines = m.split('\n')
        for li, line in enumerate(lines):
            if li < 6:
                print(f'  {line[:100]}')
        if len(lines) > 6:
            print(f'  ...(共{len(lines)}行)')
        print()
