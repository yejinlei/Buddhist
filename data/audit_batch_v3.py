import json
import re
import os

sutra_ids = ["t2182", "t2179", "t1041", "t2168a", "t2091", "t2860", "t2086", "t2843", "t2838", "t2857", "t2904", "t1292"]
base_path = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"

# 加载繁简对照表
with open(os.path.join(base_path, '..', 'hant2simp_full.json'), 'r', encoding='utf-8') as f:
    hant2simp = json.load(f)

# 半角标点（排除英文数字上下文）
half_width_punct = re.compile(r'(?<![A-Za-z0-9])[,.:;?!\'"](?![A-Za-z0-9])')
# 梵咒音译专用字（保留原字，不要求简体）
siddham_chars = set('''
唵吽嚧囉拏姪他伽陀羅尼娑婆訶薩哆怛唎伊醯彌帝麗那謹墀穆佉耶悉陀爍皤盧吉帝醯移馱侘呬爾曼爾鑁吒𥤦哩孕誐
嚩侘祢祢㗚唎麼罰皤羯懞闍醯秫詩馱曩野賀迦婆婆輸逝孕盧迦帝夷醯摩囉摩醯馱俱盧羯度嚧耶遮囉阿逝豆特伽那
薩達摩奔荼梨伽安爾曼爾儞母樓護薩嚩賀伊徥鑁友吒莊叶都羅縛嚩禁毘藍婆藥叉
''')
# 注音/反切标记（咒文中的注，不算正文咒字）
zhuyin_markers = ['二合', '引', '半音', '反', '声呼', '去', '入', '上', '平', '（', '）']

issues = []

for sid in sutra_ids:
    fpath = os.path.join(base_path, f"{sid}.json")
    if not os.path.exists(fpath):
        issues.append(f"{sid}|全局|文件缺失|{fpath}不存在|")
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    translations = data.get('translations', [])
    name_map = {}
    
    for idx, seg in enumerate(translations, 1):
        original = seg.get('original_preview', '').strip()
        modern = seg.get('modern', '').strip()
        
        yijie_pos = modern.find('【义解】')
        after_yijie = modern[yijie_pos+len('【义解】'):].strip() if yijie_pos != -1 else ''
        
        # -------------------- 格式检查 --------------------
        if not modern.startswith('【'):
            issues.append(f"{sid}|{idx}|格式错误|段落未以【小标题】开头，开头为「{modern[:10]}」|调整为【小标题】【义解】正文格式")
            continue
        first_end = modern.find('】')
        if first_end == -1:
            issues.append(f"{sid}|{idx}|格式错误|小标题缺少闭合】|补全闭合标签")
        if yijie_pos == -1:
            issues.append(f"{sid}|{idx}|格式错误|缺少【义解】标签|补充【义解】标签")
        else:
            between = modern[first_end+1:yijie_pos].strip()
            if between:
                issues.append(f"{sid}|{idx}|格式错误|小标题与【义解】间有冗余「{between[:30]}」|删除中间内容，【义解】紧跟小标题")
            if not after_yijie:
                issues.append(f"{sid}|{idx}|格式错误|【义解】后无白话正文|补充译文内容")
        yijie_count = modern.count('【义解】')
        if yijie_count > 1:
            issues.append(f"{sid}|{idx}|格式错误|存在{yijie_count}个【义解】标签|仅保留1个【义解】")
        half_matches = half_width_punct.findall(modern)
        if half_matches:
            unique_half = list(set(half_matches))
            issues.append(f"{sid}|{idx}|格式错误|半角标点：{','.join(unique_half)}|替换为全角标点")
        
        # -------------------- 提取咒文部分 --------------------
        # 将原文按“真言曰/咒曰”切分，后面的梵文部分为咒文
        mantra_parts = []
        non_mantra_orig = original
        for marker in ['真言曰：', '真言曰:', '咒曰：', '咒曰:', '神咒曰：', '即说咒曰：']:
            pos = original.find(marker)
            while pos != -1:
                # 取marker后到下一个句号/“由”/“则”/“。”之前的内容为咒文
                start = pos + len(marker)
                end = len(original)
                for end_marker in ['\n\n', '。\n', '由', '則', '则', '又', '次', '即', '。']:
                    e = original.find(end_marker, start)
                    if e != -1 and e < end:
                        end = e
                mantra_part = original[start:end].strip()
                # 排除太短的，排除全是注释的
                siddham_cnt = sum(1 for c in mantra_part if c in siddham_chars)
                if len(mantra_part) > 5 and siddham_cnt > 3:
                    mantra_parts.append(mantra_part)
                pos = original.find(marker, start)
        
        has_mantra_in_seg = len(mantra_parts) > 0
        
        # -------------------- 咒文核对 --------------------
        if has_mantra_in_seg:
            for mantra in mantra_parts:
                # 清理咒文：去掉注音标记、序号、标点、空格
                def clean_mantra(t):
                    for m in zhuyin_markers:
                        t = t.replace(m, '')
                    t = re.sub(r'[0-9]+[一二三四五六七八九十]+', '', t)
                    t = re.sub(r'[【】。，、：；！？\s（）\n\r]+', '', t)
                    # 去掉生僻缺字符号
                    t = re.sub(r'[\U00010000-\U0010ffff]', '', t)  # 临时先剔超大字符集的梵字组合，单独核对
                    return t
                orig_m_clean = clean_mantra(mantra)
                mod_m_clean = clean_mantra(after_yijie)
                # 逐字核对（咒文必须完全照录，不能错漏）
                i = j = 0
                missing = []
                wrong = []
                while i < len(orig_m_clean) and j < len(mod_m_clean):
                    if orig_m_clean[i] == mod_m_clean[j]:
                        i += 1
                        j += 1
                    else:
                        # 查找下一个匹配点（允许中间有注音间隔）
                        found = False
                        for offset in range(1, 4):
                            if i+offset < len(orig_m_clean) and orig_m_clean[i+offset] == mod_m_clean[j]:
                                missing.extend(list(orig_m_clean[i:i+offset]))
                                i += offset
                                found = True
                                break
                        if not found:
                            # 检查是否是现代译本加了注释
                            if orig_m_clean[i] in siddham_chars:
                                wrong.append(f"原「{orig_m_clean[i]}」未对应译出")
                            i += 1
                            j += 1
                if i < len(orig_m_clean):
                    missing.extend(list(orig_m_clean[i:]))
                if missing and len(missing) > 2:  # 零星差字可能是注音差异，3字以上记问题
                    sample = ''.join(missing[:8])
                    issues.append(f"{sid}|{idx}|咒文错漏|咒文遗漏字：{sample}...|逐字对照original_preview照录咒字，不得错漏")
                # 检查咒文是否被意译
                # 找“咒曰/真言曰”后面的内容，不应有“意思是”等意译
                for m_pos_marker in ['咒曰：', '真言曰：']:
                    mpos = after_yijie.find(m_pos_marker)
                    if mpos != -1:
                        after_m = after_yijie[mpos+len(m_pos_marker):mpos+len(m_pos_marker)+200]
                        if any(w in after_m for w in ['意思是', '意为', '翻译为', '就是说', '指']):
                            issues.append(f"{sid}|{idx}|咒文意译|咒文部分被意译解释|咒文必须完全照录原字，禁止意译")
                            break
        
        # -------------------- 繁简混用 --------------------
        # 要检查的文字：义解后的说明文字，排除嵌入的咒文片段
        check_text = after_yijie
        # 移除嵌入的咒文片段（即刚才提取的mantra_parts里的内容）
        for m in mantra_parts:
            m_clean = m.strip()
            if len(m_clean) > 5:
                check_text = check_text.replace(m_clean, '')
        trad_found = []
        for c in check_text:
            if c in hant2simp and c not in siddham_chars:
                # 是繁体字，且不是梵咒专用字
                trad_found.append(c)
        if trad_found:
            unique_trad = list(set(trad_found))
            trad_examples = [f"{c}→{hant2simp[c]}" for c in unique_trad[:8]]
            issues.append(f"{sid}|{idx}|繁简混用|白话说明中繁体字：{', '.join(trad_examples)}|转为简体，梵咒原字保留")
        
        # -------------------- 冗余粘贴 --------------------
        if original and len(non_mantra_orig) > 30:
            # 原文中先剔除所有咒文部分，只检查非咒文的叙述文字是否被冗余照搬
            orig_no_mantra = original
            for m in mantra_parts:
                orig_no_mantra = orig_no_mantra.replace(m, '')
            orig_nospace = re.sub(r'\s+', '', orig_no_mantra)
            modern_nospace = re.sub(r'\s+', '', after_yijie)
            # 现代译文中也剔除咒文
            mod_no_mantra = after_yijie
            for m in mantra_parts:
                m_s = m.strip()
                if len(m_s) > 5:
                    mod_no_mantra = mod_no_mantra.replace(m_s, '')
            mod_nospace_nomantra = re.sub(r'\s+', '', mod_no_mantra)
            
            frag_len = 18
            redundant = False
            redundant_sample = ""
            for i in range(len(orig_nospace) - frag_len):
                frag = orig_nospace[i:i+frag_len]
                if len(frag) < frag_len:
                    continue
                # 排除梵咒片段
                siddham_cnt = sum(1 for c in frag if c in siddham_chars)
                if siddham_cnt > 5:
                    continue
                if frag in mod_nospace_nomantra:
                    pos = mod_nospace_nomantra.find(frag)
                    in_book = False
                    if pos > 0:
                        bc = mod_nospace_nomantra[max(0, pos-1)]
                        ac = mod_nospace_nomantra[min(len(mod_nospace_nomantra)-1, pos+len(frag))]
                        if bc == '《' or ac == '》':
                            in_book = True
                    if not in_book and not any(w in frag for w in ['曰：', '偈曰', '云：', '咒曰', '真言曰']):
                        redundant = True
                        redundant_sample = frag
                        break
            if redundant:
                issues.append(f"{sid}|{idx}|冗余粘贴|非咒文部分无翻译照录古文：「{redundant_sample[:25]}...」|将古文翻译为白话，禁止大段照录原文不译，咒文照录符合要求")
        
        # -------------------- 漏译检查 --------------------
        orig_len = len(re.sub(r'[\s（）0-9\n\r]+', '', original))
        mod_len = len(re.sub(r'[\s（）0-9【】\n\r]+', '', after_yijie))
        # 减去咒文长度
        mantra_len = 0
        for m in mantra_parts:
            mantra_len += len(re.sub(r'[\s（）0-9]+', '', m))
        orig_len -= mantra_len
        mod_len -= mantra_len
        if orig_len > 60 and mod_len < orig_len * 0.3:
            issues.append(f"{sid}|{idx}|疑似漏译|原文非咒文约{orig_len}字，白话仅约{mod_len}字|核对原文补全内容")

# -------------------- 输出 --------------------
print("===佛经白话译文校对问题列表（经号|段号|问题类型|问题描述|修正建议）===")
if not issues:
    print("无问题")
else:
    def sort_key(line):
        parts = line.split('|')
        sid = parts[0]
        try: seg = int(parts[1])
        except: seg = 0
        return (sid, seg)
    issues.sort(key=sort_key)
    for i in issues:
        print(i)
