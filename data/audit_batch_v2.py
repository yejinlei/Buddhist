import json
import re
import os

sutra_ids = ["t2182", "t2179", "t1041", "t2168a", "t2091", "t2860", "t2086", "t2843", "t2838", "t2857", "t2904", "t1292"]
base_path = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"

# 加载繁简对照表
with open(os.path.join(base_path, '..', 'hant2simp_full.json'), 'r', encoding='utf-8') as f:
    hant2simp = json.load(f)

# 半角标点集合（译文正文不应使用半角标点，数字、英文专有名词除外）
half_width_punct = re.compile(r'(?<![A-Za-z0-9])[,.:;?!\'"](?![A-Za-z0-9])')
# 咒文标识：明确的咒文/真言开头
mantra_markers = ['咒曰', '真言曰', '陀罗尼曰', '神咒曰', '即说咒曰', '说此咒曰', '唵', '曩谟', '娜谟', '南无佛陀耶']
# 梵音译字特征：大段口字旁/生僻音译字判定为咒文
siddham_chars = set('唵吽嚧囉拏姪他伽陀羅尼娑婆訶薩哆怛唎伊醯彌帝麗那謹墀穆佉耶悉陀爍皤盧吉帝醯移馱侘呬爾曼爾鑁吒𥤦吽哩孕誐'
                    '唵啊吽啪嘛呢叭咪吽娑婆诃萨婆诃怛侄他')

issues = []

for sid in sutra_ids:
    fpath = os.path.join(base_path, f"{sid}.json")
    if not os.path.exists(fpath):
        issues.append(f"{sid}|全局|文件缺失|{fpath}不存在|")
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    translations = data.get('translations', [])
    
    # 先收集全经译名，检查统一
    name_map = {}
    
    for idx, seg in enumerate(translations, 1):
        original = seg.get('original_preview', '').strip()
        modern = seg.get('modern', '').strip()
        
        yijie_pos = modern.find('【义解】')
        after_yijie = modern[yijie_pos+len('【义解】'):].strip() if yijie_pos != -1 else ''
        
        # -------------------- 格式检查 --------------------
        # 1. 必须以【小标题】开头
        if not modern.startswith('【'):
            issues.append(f"{sid}|{idx}|格式错误|段落未以【小标题】开头，开头字符为「{modern[:10]}」|调整段落格式，以【小标题】开头")
            # 跳过后续格式检查，避免连锁误判
            continue
        # 2. 小标题闭合
        first_end = modern.find('】')
        if first_end == -1:
            issues.append(f"{sid}|{idx}|格式错误|开头的小标题缺少闭合】|补全小标题闭合括号")
        # 3. 必须有【义解】
        if yijie_pos == -1:
            issues.append(f"{sid}|{idx}|格式错误|段落缺少【义解】标签|在小标题后补充【义解】标签")
        else:
            # 4. 小标题和【义解】之间不能有内容
            between = modern[first_end+1:yijie_pos].strip()
            if between:
                issues.append(f"{sid}|{idx}|格式错误|小标题与【义解】之间存在冗余内容「{between[:30]}」|删除中间冗余，确保【义解】紧跟小标题闭合后")
            # 5. 【义解】后必须有正文
            if not after_yijie:
                issues.append(f"{sid}|{idx}|格式错误|【义解】后无白话正文内容|补充【义解】后的白话译文")
        # 6. 不能有多个【义解】
        yijie_count = modern.count('【义解】')
        if yijie_count > 1:
            issues.append(f"{sid}|{idx}|格式错误|存在{yijie_count}个【义解】标签|仅保留1个【义解】标签，删除重复标签")
        # 7. 半角标点（排除英文/数字中的标点）
        half_matches = half_width_punct.findall(modern)
        if half_matches:
            unique_half = list(set(half_matches))
            issues.append(f"{sid}|{idx}|格式错误|正文使用了半角标点：{','.join(unique_half)}|替换为全角中文标点")
        
        # -------------------- 判定是否为咒文段 --------------------
        is_mantra = False
        # 显式标记
        if any(m in original for m in mantra_markers):
            is_mantra = True
        # 大段梵音译字
        siddham_count = sum(1 for c in original if c in siddham_chars)
        if siddham_count / max(len(original),1) > 0.4 and len(original) > 10:
            is_mantra = True
        # 排除目录/序言段
        if '卷' in original and '譯' in original and any(c in original for c in ['（', '）']) and siddham_count < 5:
            is_mantra = False
        
        # -------------------- 咒文检查 --------------------
        if is_mantra:
            # 咒文必须完全照录，不能意译
            # 清理标签和标点，对比原文字
            orig_clean = re.sub(r'[【】。，、：；！？\s（）0-9]', '', original)
            mod_clean = re.sub(r'[【】。，、：；！？\s（）0-9]', '', after_yijie)
            # 逐字核对咒字
            missing_chars = []
            wrong_chars = []
            oi = 0
            mi = 0
            while oi < len(orig_clean) and mi < len(mod_clean):
                if orig_clean[oi] == mod_clean[mi]:
                    oi += 1
                    mi += 1
                else:
                    # 找下一个匹配
                    found = False
                    for offset in range(1, min(5, len(orig_clean)-oi)):
                        if orig_clean[oi+offset] == mod_clean[mi]:
                            missing_chars.extend(list(orig_clean[oi:oi+offset]))
                            oi += offset
                            found = True
                            break
                    if not found:
                        wrong_chars.append(f"原:{orig_clean[oi]}/译:{mod_clean[mi]}")
                        oi += 1
                        mi += 1
            if oi < len(orig_clean):
                missing_chars.extend(list(orig_clean[oi:]))
            if missing_chars:
                sample = ''.join(missing_chars[:10])
                issues.append(f"{sid}|{idx}|咒文错误|咒文遗漏字：{sample}...|逐字对照original_preview照录原字，不得错漏")
            if wrong_chars:
                sample = '; '.join(wrong_chars[:5])
                issues.append(f"{sid}|{idx}|咒文错误|咒文存在错字：{sample}|对照原文修正错字")
            # 检查是否意译咒文
            if any(w in after_yijie for w in ['意思是', '意为', '就是说', '表示', '指的是']):
                issues.append(f"{sid}|{idx}|咒文意译|咒文部分被意译|咒文必须完全照录原字，禁止解释意译")
        
        # -------------------- 繁简混用检查 --------------------
        # 说明文字（【义解】后）必须简体，咒文古注保留原字
        check_text = after_yijie if not is_mantra else ''
        # 咒文段里的非咒文解释部分也要简体
        if is_mantra:
            # 找【义解】后非咒文的解释部分
            for part in re.split(r'[。；]', after_yijie):
                if any(w in part for w in ['意思是', '意为', '此咒', '功德', '利益', '修法']) and sum(1 for c in part if c in siddham_chars) < 3:
                    check_text += part
        trad_found = []
        for c in check_text:
            if c in hant2simp:
                # 是繁体字，检查是否是梵音译专用字（允许保留原字）
                if c not in siddham_chars:  # 梵字保留，繁体普通字必须转简体
                    trad_found.append(c)
        if trad_found:
            unique_trad = list(set(trad_found))
            trad_examples = [(c + '→' + hant2simp[c]) for c in unique_trad[:8]]
            issues.append(f"{sid}|{idx}|繁简混用|白话说明中存在繁体字：{', '.join(trad_examples)}|将繁体字转为简体，仅咒文梵字保留原字")
        
        # -------------------- 冗余粘贴检查 --------------------
        if not is_mantra and original and len(original) > 20:
            # 检查是否有连续15字以上原文照搬，且不是书名/专有名词引用
            orig_nospace = re.sub(r'\s+', '', original)
            modern_nospace = re.sub(r'\s+', '', modern)
            frag_len = 15
            redundant = False
            redundant_sample = ""
            for i in range(len(orig_nospace) - frag_len):
                frag = orig_nospace[i:i+frag_len]
                if frag in modern_nospace:
                    # 排除书名号里的内容
                    pos = modern_nospace.find(frag)
                    in_book = False
                    if pos > 0:
                        before_char = modern_nospace[max(0, pos-1)]
                        after_char = modern_nospace[min(len(modern_nospace)-1, pos+len(frag))]
                        if before_char == '《' or after_char == '》':
                            in_book = True
                    # 排除偈颂引用？不，偈颂也要翻译，除非是专门引原文
                    if not in_book and not any(w in frag for w in ['曰：', '云：', '偈云']):
                        redundant = True
                        redundant_sample = frag
                        break
            if redundant:
                issues.append(f"{sid}|{idx}|冗余粘贴|白话中无翻译照录古文原文片段：「{redundant_sample[:20]}...」|将古文翻译为白话，禁止大段照录原文不译")
        
        # -------------------- 漏译检查 --------------------
        orig_clean_len = len(re.sub(r'[\s（）0-9]', '', original))
        mod_clean_len = len(re.sub(r'[\s（）0-9【】]', '', after_yijie))
        if orig_clean_len > 80 and mod_clean_len < orig_clean_len * 0.25:
            issues.append(f"{sid}|{idx}|疑似漏译|原文约{orig_clean_len}字，白话仅约{mod_clean_len}字，篇幅过短|核对原文补全遗漏内容")
        
        # -------------------- 译名不统一记录 --------------------
        # 提取佛菩萨、经名
        names = re.findall(r'[《]([^》]+)[》]', after_yijie)
        for n in names:
            if n in name_map and name_map[n] != n:
                pass
            name_map[n] = n
        buddha_names = re.findall(r'[\u4e00-\u9fa5]{2,4}(?:佛|菩萨|罗汉|天王|法师|三藏)', after_yijie)
        for n in buddha_names:
            if len(n) < 2: continue
            if n in name_map and name_map[n] != n:
                issues.append(f"{sid}|{idx}|译名不统一|「{n}」与经内其他位置译法不一致|统一译名")
            name_map[n] = n

# -------------------- 输出结果 --------------------
print("===佛经白话译文校对问题列表（经号|段号|问题类型|问题描述|修正建议）===")
if not issues:
    print("无问题")
else:
    # 按经号、段号排序
    def sort_key(line):
        parts = line.split('|')
        sid = parts[0]
        try:
            seg = int(parts[1])
        except:
            seg = 0
        return (sid, seg)
    issues.sort(key=sort_key)
    for i in issues:
        print(i)
