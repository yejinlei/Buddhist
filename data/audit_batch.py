import json
import re
import os

sutra_ids = ["t2182", "t2179", "t1041", "t2168a", "t2091", "t2860", "t2086", "t2843", "t2838", "t2857", "t2904", "t1292"]
base_path = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"

# 半角标点集合（排除URL、代码，但这里是佛经译文，不应有半角标点）
half_width_punct = re.compile(r'[,.:;?!\'"()\[\]{}<>/\\]')
# 繁体常见字（简单扫明显繁简混用，主要检查说明文字）
traditional_chars = {'藥','師','經','國','譯','錄','勅','聖','律','卷','藏','鳩','摩','羅','什','義','解','體','國','寶','華','嚴','經','阿','彌','陀','觀','世','音','勢','至','菩','薩','聲','聞','緣','覺','無','為','識','智','惱','習','氣','證','涅槃','波','羅','蜜','訶','薩','哆','他','伽','梵','釋','迦','牟','尼','淨','土','業','報','應','供','養','辯','才','總','持','陀','羅','尼','咒','祕','密','顯','現','變','化','壽','命','相好','光','明','照','耀','普','度','一','切','眾','生','離','苦','得','樂'}
# 咒文特征：通常是音译无实义，多为梵音转写，如"唵""吽""娑婆诃""萨婆诃""怛侄他""南无"等开头或集中的音译词
mantra_keywords = ['唵', '吽', '娑婆诃', '萨婆诃', '娑诃', '怛侄他', '怛他', '南无', '娜谟', '曩谟', '佛陀', '达摩', '僧伽', '般若', '波罗蜜', '咒曰', '真言曰', '陀罗尼曰']

issues = []

for sid in sutra_ids:
    fpath = os.path.join(base_path, f"{sid}.json")
    if not os.path.exists(fpath):
        issues.append(f"{sid}|全局|文件缺失|{fpath}不存在|")
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    translations = data.get('translations', [])
    total = len(translations)
    for idx, seg in enumerate(translations, 1):
        original = seg.get('original_preview', '').strip()
        modern = seg.get('modern', '').strip()
        
        # 格式检查1：段必须以【小标题】开头
        if not modern.startswith('【'):
            issues.append(f"{sid}|{idx}|格式错误|段落未以【小标题】开头，开头为：{modern[:20]}|调整段落开头为【小标题】格式")
        else:
            # 检查【义解】位置：必须紧跟在小标题后
            yijie_pos = modern.find('【义解】')
            if yijie_pos == -1:
                issues.append(f"{sid}|{idx}|格式错误|段落缺少【义解】标签|在小标题后补充【义解】标签")
            else:
                # 小标题是第一个【】，检查【义解】是否紧跟其后（中间无其他正文）
                first_end = modern.find('】')
                if first_end == -1:
                    issues.append(f"{sid}|{idx}|格式错误|小标题未闭合，缺少】|补全小标题闭合标签")
                else:
                    between = modern[first_end+1:yijie_pos].strip()
                    if between:
                        issues.append(f"{sid}|{idx}|格式错误|小标题与【义解】之间存在冗余内容：{between[:30]}|删除小标题与【义解】之间的内容，确保【义解】紧跟小标题")
                # 检查【义解】后是否有正文
                after_yijie = modern[yijie_pos+len('【义解】'):].strip()
                if not after_yijie:
                    issues.append(f"{sid}|{idx}|格式错误|【义解】后无白话正文|补充【义解】后的白话译文内容")
        # 格式检查2：是否有多个【义解】标签
        yijie_count = modern.count('【义解】')
        if yijie_count > 1:
            issues.append(f"{sid}|{idx}|格式错误|存在{yijie_count}个【义解】标签，出现双/多【义解】|保留仅一个【义解】标签，删除重复")
        # 格式检查3：半角标点
        half_matches = half_width_punct.findall(modern)
        if half_matches:
            # 排除可能的数字序号？不，佛经译文里不应有半角标点，除非是特殊，但半角逗号句号问号肯定错
            unique_half = list(set(half_matches))
            issues.append(f"{sid}|{idx}|格式错误|存在半角标点：{','.join(unique_half)}|将半角标点替换为全角中文标点")
        # 格式检查4：繁简混用（说明文字，咒文古注除外）
        # 先排除咒文部分，再检查简体说明里的繁体字
        modern_no_mantra = modern
        # 粗略排除咒文段（如果original是咒文，modern里的咒文保留原字不查繁简）
        is_mantra_seg = any(k in original for k in mantra_keywords) and len(original) < 200 and not any(c in original for c in ['。', '，', '：', '；'])
        if not is_mantra_seg:
            # 检查说明文字中的繁体字（即【义解】后的内容）
            yijie_pos = modern.find('【义解】')
            if yijie_pos != -1:
                explanation = modern[yijie_pos+len('【义解】'):]
                trad_found = []
                for c in explanation:
                    if c in traditional_chars and c not in ['菩','薩','阿','彌','陀','波','羅','蜜','訶','伽','梵','釋','迦','牟','尼','陀','羅','尼','唵','吽']:
                        trad_found.append(c)
                if trad_found:
                    unique_trad = list(set(trad_found))
                    # 过滤掉专有名词里允许的字？比如"菩萨"是简体，哦不对，"菩""薩"里"薩"是繁体？不对，简体是"萨"，哦对，我刚才的traditional_chars里有"薩"，简体是"萨"。不过等下，专有名词如果是统一译名的话，必须简体，除了咒文原字。
                    # 再仔细看：比如"经"繁体是"經"，简体是"经"；"译"繁体"譯"，简体"译"；"国"繁体"國"，简体"国"
                    issues.append(f"{sid}|{idx}|繁简混用|白话说明中存在繁体字：{','.join(unique_trad)}|将繁体字转为简体中文，仅咒文古注保留原字")
        
        # 咒文检查：original是咒文的话，modern里不能意译，必须照录原字
        if is_mantra_seg:
            # 检查modern里的咒文部分是否和original一致，没有意译
            # 咒文部分应该在modern里原样保留，不能翻译
            mantra_in_modern = after_yijie if yijie_pos != -1 else modern
            # 去除【】标签和标点，对比核心咒字
            orig_clean = re.sub(r'[【】。，、：；！？\s]', '', original)
            mod_clean = re.sub(r'[【】。，、：；！？\s]', '', mantra_in_modern)
            if orig_clean not in mod_clean:
                # 检查是否有遗漏咒字或意译
                # 找不同的字
                missing = []
                for c in orig_clean:
                    if c not in mod_clean:
                        missing.append(c)
                if missing:
                    issues.append(f"{sid}|{idx}|咒文错误|咒文存在错漏字，遗漏字：{','.join(missing[:10])}|逐字对照original_preview照录原字，禁止意译咒文")
                # 检查是否有意译的词，比如出现"意思是""即指"等翻译咒文的表述
                if any(w in mantra_in_modern for w in ['意思是', '即指', '意为', '译为', '就是说', '表示']):
                    issues.append(f"{sid}|{idx}|咒文意译|咒文部分被意译，违反要求|咒文必须完全照录原字，删除所有意译解释")
        
        # 冗余粘贴检查：modern中非咒文部分大段照录original古文
        if not is_mantra_seg and original:
            # 取original中连续12字以上的片段，看是否在modern里原样出现（非专有名词）
            orig_len = len(original)
            has_redundant = False
            redundant_sample = ""
            for i in range(orig_len - 12):
                frag = original[i:i+12]
                # 跳过全是专有名词/书名的片段？不，普通句子如果原样照搬就是冗余
                if frag in modern and not any(k in frag for k in ['《', '》', '曰', '云', '偈曰']):
                    # 检查这个片段不是书名号里的
                    in_book = False
                    book_pos = modern.find(frag)
                    if book_pos != -1:
                        before = modern[max(0, book_pos-1):book_pos]
                        after = modern[book_pos+len(frag):book_pos+len(frag)+1]
                        if before == '《' or after == '》':
                            in_book = True
                    if not in_book:
                        has_redundant = True
                        redundant_sample = frag
                        break
            if has_redundant:
                issues.append(f"{sid}|{idx}|冗余粘贴|白话中冗余照录非咒文原文片段：{redundant_sample}...|将古文原文翻译为白话，禁止大段照录古文不翻译")
        
        # 漏译检查：如果original有内容，但modern只有标题和【义解】，正文过短
        orig_text_len = len(re.sub(r'\s+', '', original))
        mod_text_len = len(re.sub(r'\s+', '', after_yijie)) if yijie_pos != -1 else len(re.sub(r'\s+', '', modern))
        if orig_text_len > 50 and mod_text_len < orig_text_len * 0.3:
            issues.append(f"{sid}|{idx}|疑似漏译|原文长度{orig_text_len}字，白话译文仅{mod_text_len}字，篇幅过短|核对原文，补全遗漏未译的内容")
        
        # 译名统一：同经内先记录译名，后面检查？先简单检查同一段内同名异译，比如"阿弥陀佛"和"阿弥陀"不统一？不，先标记明显的，比如"佛驮耶舍"和"佛陀耶舍"在同段出现
        # 这个后面人工看，先自动检查明显的重复译名

# 输出结果
print("===佛经白话译文校对问题列表===")
if not issues:
    print("无问题")
else:
    for i in issues:
        print(i)
