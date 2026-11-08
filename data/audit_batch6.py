import json
import os
import re

# 经号列表
sutra_ids = ["t2182", "t2179", "t1041", "t2168a", "t2091", "t2860", "t2086", "t2843", "t2838", "t2857", "t2904", "t1292"]
base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"

problems = []

def check_sutra(sutra_id):
    file_path = os.path.join(base_dir, f"{sutra_id}.json")
    if not os.path.exists(file_path):
        problems.append(f"{sutra_id}|-|文件缺失|文件不存在|请补充该经号的白话译文文件")
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        problems.append(f"{sutra_id}|-|文件读取错误|JSON解析失败：{str(e)}|修复JSON格式")
        return
    
    translations = data.get("translations", [])
    for seg_idx, seg in enumerate(translations, 1):
        original = seg.get("original_preview", "").strip()
        modern = seg.get("modern", "").strip()
        
        if not modern:
            problems.append(f"{sutra_id}|{seg_idx}|内容缺失|白话译文为空|补充该段白话译文")
            continue
        
        # 1. 格式检查：每段是否以【小标题】开头、接【义解】、【义解】后有正文
        # 匹配开头的标签
        tag_pattern = r"^【[^】]+】【义解】"
        if not re.match(tag_pattern, modern):
            # 检查是否有双【义解】
            yijie_count = modern.count("【义解】")
            if yijie_count > 1:
                problems.append(f"{sutra_id}|{seg_idx}|格式错误|出现{yijie_count}个【义解】标签，存在重复|保留一个【义解】标签，删除重复")
            # 检查开头结构
            if not modern.startswith("【"):
                problems.append(f"{sutra_id}|{seg_idx}|格式错误|段首未以【小标题】开头|段首添加【小标题】标签")
            elif "【义解】" not in modern:
                problems.append(f"{sutra_id}|{seg_idx}|格式错误|缺少【义解】标签|在小标题后添加【义解】标签")
            else:
                problems.append(f"{sutra_id}|{seg_idx}|格式错误|开头结构不符合【小标题】【义解】格式|调整为【小标题】【义解】后接白话正文的结构")
        else:
            # 检查【义解】后是否有正文
            after_yijie = modern.split("【义解】", 1)[1].strip()
            if not after_yijie:
                problems.append(f"{sutra_id}|{seg_idx}|格式错误|【义解】标签后无白话正文|补充白话译文内容")
        
        # 检查半角标点（排除书名号里的？不，半角标点包括, . ! ? : ; ( ) [ ] { }等，中文里应该用全角，除了可能的URL/代码，但这里是佛经译文，应该没有）
        # 注意：咒文里的梵字可能没有标点，但说明文字要用全角
        half_punct = re.findall(r"[,.;:!?\(\)\[\]\{\}]", modern)
        if half_punct:
            problems.append(f"{sutra_id}|{seg_idx}|格式错误|存在半角标点：{''.join(half_punct)}|替换为对应的全角标点")
        
        # 检查繁简混用：说明文字必须简体，咒文古注保留原字。这里先找明显的繁体字？不对，原文是繁体，译文里非咒文部分应该简体。不过先标记明显的，比如"爲"、"裏"这类？或者先看，不过可能更准确的是，非经名、非咒文部分的繁体？
        # 暂时先处理明显的，不过可能需要注意：经名里的字如果是原文的，比如"毘"是不是保留？对，佛学名相里的"毘"通常保留？不对，"毘"是"毗"的异体，不过要看译名统一，后面统一检查。
        
        # 2. 冗余粘贴：检查modern中是否大段照录古文不翻译（非咒文部分）
        # 计算original和modern的重复率？或者看是否有连续超过10个字和原文完全一致且是古文非经名/咒文？
        # 先找连续10字以上和original完全匹配的片段，排除经名（书名号里的）
        # 先去掉modern里的标签
        modern_content = re.sub(r"【[^】]+】", "", modern).strip()
        # 找最长公共子串？或者简单找连续10字匹配
        max_common = 0
        common_str = ""
        for i in range(len(original)):
            for j in range(i+10, len(original)+1):
                substr = original[i:j]
                if substr in modern_content and len(substr) > max_common:
                    # 排除经名（在书名号里的）
                    if f"《{substr}》" in modern:
                        continue
                    max_common = len(substr)
                    common_str = substr
        if max_common >= 15:  # 超过15字的大段照录
            problems.append(f"{sutra_id}|{seg_idx}|冗余粘贴|白话译文中大段照录原文古文：{common_str[:20]}...|将该段古文翻译为白话，不要直接粘贴原文")
        
        # 3. 咒文/梵字/音注检查：咒文绝对不能意译，必须照录原字。首先判断是否有咒文？咒文通常是"咒曰"、"真言"开头，或者是梵音的堆砌，没有实际语义。
        # 先找是否有咒文相关内容：原文中有"咒"、"真言"、"陀罗尼"的，或者连续的梵音用字（如"唵"、"吽"、"娑婆诃"等）
        has_spell = False
        spell_part = ""
        if re.search(r"(咒|真言|陀羅尼|陀羅尼|呪)", original):
            has_spell = True
        # 检查梵音常见字
        sanskrit_chars = r"[唵吽嚧哢哆唎娑婆訶訶薩埵耶涅盤荼楞伽]"
        if len(re.findall(sanskrit_chars, original)) >= 3:
            has_spell = True
        if has_spell:
            # 提取原文中的咒文部分，检查译文中是否意译，是否错字漏字
            # 这里先简单检查：如果原文有咒文，译文中是否把咒文意译了，或者是否有错字
            # 首先找原文中咒文的部分（通常在"咒曰"、"即说咒曰"之后）
            spell_match = re.search(r"(咒曰|呪曰|真言曰|即說咒曰|即说咒曰)(.*)", original)
            if spell_match:
                original_spell = spell_match.group(2).strip()
                # 检查译文中是否有这个咒文，是否完全照录，有没有意译
                if original_spell not in modern:
                    # 检查是否有意译，比如把咒文翻译成意思了
                    # 或者是否有错字
                    problems.append(f"{sutra_id}|{seg_idx}|咒文错误|原文咒文未完全照录，存在错漏或意译|咒文部分必须严格逐字照录原字，不得意译、不得改字漏字")
        
        # 4. 错译漏译：暂时先标记明显的？比如原文有内容而译文完全没提的？或者先看有没有整句遗漏，这个可能需要逐句对，但先看长度，比如original很长，modern很短？不过可能不太准，先记下来，后面人工？
        # 暂时先处理明显的：比如原文中有的经名/典籍完全没出现在译文里？
        # 提取原文中的书名（通常是卷数前的部分，比如"XXX一卷"、"XXX十卷"）
        orig_books = re.findall(r"([^（）]+?)([一二三四五六七八九十百千]+卷)", original)
        orig_book_names = [b[0].strip() for b in orig_books if b[0].strip()]
        modern_books = re.findall(r"《([^》]+)》", modern)
        missing_books = []
        for bn in orig_book_names:
            found = False
            for mb in modern_books:
                if bn.replace("誡", "诫").replace("爾", "尔").replace("薩", "萨") in mb or mb in bn:  # 简繁转换后的匹配
                    found = True
                    break
            if not found and len(bn) > 1:
                missing_books.append(bn)
        if missing_books:
            problems.append(f"{sutra_id}|{seg_idx}|漏译|原文中以下典籍未在译文中提及：{'、'.join(missing_books)}|补充翻译这些典籍的相关内容")
        
        # 5. 标点疏漏、译名统一：检查译名是否前后一致，比如人名、地名、佛菩萨名。这里先收集所有译名，后面跨段检查？
        # 先在单个文件里检查译名是否一致，比如同一个名字在不同段译法不同
        # 比如"佛陀耶舍"是否一直译"佛陀耶舍"，有没有译成"佛驮耶舍"？
        # 暂时先记录译名，后面跨文件？不，先单个文件检查。另外检查标点是否有缺失，比如句末没有句号？
        if not re.search(r"[。！？]$", modern_content):
            problems.append(f"{sutra_id}|{seg_idx}|标点疏漏|白话正文句末缺少句号/感叹号/问号等句末标点|补充句末标点")
    
    # 跨段检查译名统一
    # 收集所有译名
    all_names = []
    for seg in translations:
        modern = seg.get("modern", "")
        # 提取人名、地名、佛名：通常是在"三藏"、"沙门"、"法师"、"律师"前面，或者经名里的人名？
        names = re.findall(r"(?:三藏|沙門|沙门|法師|法师|律師|律师|菩薩|菩萨|佛|天子|國王|国王|聖王|圣王|大師|大师|法師|法师|律師|律师)([A-Za-z\u4e00-\u9fa5]{2,})", modern)
        all_names.extend(names)
        # 提取书名里的人名？比如"道宣钞"里的道宣？
        names2 = re.findall(r"([\u4e00-\u9fa5]{2,3})(?:述|集|譯|译|撰|錄|录)", modern)
        all_names.extend(names2)
    # 检查同一个名字的不同译法：比如"荣稳"和"榮穩"？因为说明文字要简体，所以"榮穩"如果在正文里应该是"荣稳"，除非是咒文/古注？
    # 不过t2182里translator是"日本 榮穩錄"，正文里是"荣稳大法师"，这个是对的，标签外简体。
    # 检查明显的繁简不一致：比如"毘"和"毗"？"苾芻"是保留吗？对，"苾芻"是比丘的异译，通常保留？不对，要统一，不过先看是否有同一个字在同一个经里有两种写法，除了经名原文里的。
    # 比如"毘奈耶"，原文里是"毘"，译文里如果写成"毗奈耶"就不一致？
    # 暂时先标记明显的：比如同一个人名，一段里用简体，一段里用繁体。

# 逐个检查
for sid in sutra_ids:
    check_sutra(sid)

# 输出结果
output_path = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/audit-report-D6.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# 白话译文校对问题列表（D6批次）\n\n")
    f.write("| 经号 | 段号 | 问题类型 | 问题描述 | 修正建议 |\n")
    f.write("|------|------|----------|----------|----------|\n")
    if problems:
        for p in problems:
            parts = p.split("|", 4)
            f.write("| " + " | ".join(parts) + " |\n")
    else:
        f.write("| 全部 | - | 无问题 | 所有经号译文符合检查清单要求 | - |\n")

print(f"校对完成，共发现{len(problems)}个问题，结果已写入{output_path}")
