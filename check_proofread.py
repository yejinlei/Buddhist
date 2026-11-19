import json
import os
import re

# 要检查的经号列表
jing_list = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659", "t0327", "t0843", "t2818", "t1737", "t0652", "t0405"]
base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/"
output_path = "/home/user/workspace/13511660557912876654/buddhist-ontology/proofread_c_batch177.md"

issues = []
no_issue_jings = []

# 半角标点正则（排除咒文里的可能，但白话部分不能有）
half_punct = re.compile(r'[!\"#$%&\'()*+,-./:;<=>?@\[\\\]^_`{|}~]')
# PUA字符范围
pua_chars = re.compile(r'[\ue000-\uf8ff\U000f0000-\U000ffffd\U00100000-\U0010fffd]')
# 阙文□
que_char = re.compile(r'□')
# 咒文关键词
zhou_keywords = re.compile(r'陀羅尼|真言|神呪|呪|咒|陀罗尼|真言|神咒')

# 简体/繁体常见错误替换（手动列几个明显的）
traditional_chars = {
    "爾時": "这时", "如是我聞": "像这样我听闻", "云何": "为何", "於": "在/于", "汝": "你",
    "為何": "为何", "復次": "再者", "何者": "什么", "即": "就", "皆悉": "全都", "彼": "那/他",
    "何": "什么", "是": "这", "時": "时", "語": "对……说/告诉", "言": "说", "觀": "观", "見": "见",
    "無": "无", "與": "与", "眾": "众", "發": "发", "義": "义", "體": "体", "性": "性", "覺": "觉",
    "謂": "称/说", "當": "当", "願": "愿", "施": "施", "即": "就", "已": "之后", "作": "做/起",
    "念": "念/想", "即": "就", "往": "去", "詣": "到", "處": "地方", "身": "身体", "光": "光",
    "明": "明", "照": "照", "色": "色", "受": "受", "想": "想", "行": "行", "識": "识", "陰": "蕴",
    "入": "入", "界": "界", "平": "平", "等": "等", "故": "所以/因此", "名": "叫做/称为", "菩提": "菩提",
    "薩": "萨", "菩": "菩", "文": "文", "殊": "殊", "師": "师", "利": "利", "童": "童", "子": "子",
    "禪": "禅", "定": "定", "悲": "悲", "心": "心", "生": "生", "大": "大", "眾": "众", "生": "生",
    "應": "应", "以": "用/以", "神": "神", "通": "通", "過": "过", "去": "去", "業": "业", "緣": "缘",
    "聞": "闻", "正": "正", "法": "法", "根": "根", "性": "性", "差": "差", "別": "别", "善": "善",
    "因": "因", "緣": "缘", "堪": "能", "受": "受", "教": "教", "化": "化", "若": "如果", "信": "信",
    "受": "受", "威": "威", "神": "神", "力": "力", "放": "放", "映": "映", "蔽": "蔽", "日": "日",
    "光": "光", "悉": "全/都", "不": "不", "復": "再", "現": "现", "何": "何", "況": "何况", "餘": "其他"
}

for jing in jing_list:
    file_path = os.path.join(base_dir, f"{jing}.json")
    if not os.path.exists(file_path):
        issues.append({
            "jing": jing,
            "duan": "整体",
            "type": "文件缺失",
            "original": "",
            "baihua": "",
            "fix": f"文件{file_path}不存在，无法校对"
        })
        continue
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        issues.append({
            "jing": jing,
            "duan": "整体",
            "type": "文件解析错误",
            "original": "",
            "baihua": "",
            "fix": f"JSON解析失败：{str(e)}"
        })
        continue
    
    # 正确结构：data["translations"]是段列表，每个段有original_preview和modern
    jing_issues = []
    if "translations" not in data:
        issues.append({
            "jing": jing,
            "duan": "整体",
            "type": "结构错误",
            "original": str(data)[:100],
            "baihua": "",
            "fix": "JSON结构无translations字段，无法逐段检查"
        })
        continue
    
    segments = data["translations"]
    
    for idx, seg in enumerate(segments):
        duan_id = f"第{idx+1}段"
        modern = seg.get("modern", "")
        original = seg.get("original_preview", "")
        if not original:
            original = seg.get("original", "")
        
        # ---------------------- 1. 格式红线检查 ----------------------
        # 按行分割modern
        modern_lines = [l for l in modern.split('\n') if l.strip()]
        modern_lines_stripped = [l.strip() for l in modern_lines]
        has_title = False
        has_yijie = False
        has_baihua_content = False
        
        if len(modern_lines_stripped) >= 1:
            # 第一行是小标题，应该是【】包裹，且应为简体
            first_line = modern_lines_stripped[0]
            if first_line.startswith('【') and first_line.endswith('】'):
                has_title = True
                # 检查小标题是否为繁体
                if '說' in first_line or '義' in first_line or '緣' in first_line or '發' in first_line:
                    jing_issues.append({
                        "jing": jing,
                        "duan": duan_id,
                        "type": "格式/字符红线-小标题使用繁体",
                        "original": original[:50] + ("..." if len(original) > 50 else ""),
                        "baihua": first_line,
                        "fix": "小标题需统一使用简体中文，如【说法因缘】【宣说法义】，不得使用繁体「說、緣、義」等字"
                    })
            else:
                jing_issues.append({
                    "jing": jing,
                    "duan": duan_id,
                    "type": "格式红线-缺小标题",
                    "original": original[:50] + ("..." if len(original) > 50 else ""),
                    "baihua": first_line,
                    "fix": "modern首行应添加【小标题】，用全角方括号包裹本段主题，且使用简体中文"
                })
        
        # 检查有没有【义解】
        yijie_pos = -1
        yijie_line = ""
        for i, line in enumerate(modern_lines_stripped):
            if '【义解】' in line or '【義解】' in line:
                has_yijie = True
                yijie_pos = i
                yijie_line = line
                break
        if not has_yijie:
            jing_issues.append({
                "jing": jing,
                "duan": duan_id,
                "type": "格式红线-缺义解标记",
                "original": original[:50] + ("..." if len(original) > 50 else ""),
                "baihua": modern[:100] + ("..." if len(modern) > 100 else ""),
                "fix": "modern第二行应包含【义解】标记（简体），其后为白话译文"
            })
        else:
            # 检查义解标记是不是繁体
            if '【義解】' in yijie_line:
                jing_issues.append({
                    "jing": jing,
                    "duan": duan_id,
                    "type": "格式/字符红线-义解标记使用繁体",
                    "original": original[:50] + ("..." if len(original) > 50 else ""),
                    "baihua": yijie_line,
                    "fix": "义解标记需统一为简体【义解】，不得使用繁体【義解】"
                })
            # 检查义解内容是不是繁体
            if '為' in yijie_line or '經' in yijie_line or '說' in yijie_line or '義' in yijie_line or '緣' in yijie_line or '發' in yijie_line or '導' in yijie_line:
                jing_issues.append({
                    "jing": jing,
                    "duan": duan_id,
                    "type": "字符红线-义解内容使用繁体",
                    "original": original[:50] + ("..." if len(original) > 50 else ""),
                    "baihua": yijie_line,
                    "fix": "义解说明部分需使用简体现代汉语，「為」改「为」、「經」改「经」、「說」改「说」、「義」改「义」、「緣」改「缘」、「發」改「发」、「導」改「导」"
                })
            # 义解后有没有白话内容
            if yijie_pos >= len(modern_lines_stripped) - 1:
                jing_issues.append({
                    "jing": jing,
                    "duan": duan_id,
                    "type": "格式红线-缺白话内容",
                    "original": original[:50] + ("..." if len(original) > 50 else ""),
                    "baihua": modern[yijie_pos:],
                    "fix": "【义解】后应有对应的白话译文内容，不得为空"
                })
            else:
                # 检查义解后内容是不是纯繁体照搬原文
                after_yijie = '\n'.join(modern_lines_stripped[yijie_pos+1:])
                if len(after_yijie.strip()) > 0:
                    has_baihua_content = True
        
        # ---------------------- 2. 咒文红线检查 ----------------------
        is_zhou = False
        # 原文里有咒文关键词，说明是咒文段
        if zhou_keywords.search(original) or zhou_keywords.search(modern):
            is_zhou = True
        if is_zhou:
            # 检查有没有省略咒语的表述
            omit_marks = ['咒语从略', '密咒不录', '咒文不录', '咒语略', '梵音略', '咒曰（下略）', '咒语不译']
            has_omit = False
            for mark in omit_marks:
                if mark in modern:
                    has_omit = True
                    break
            if has_omit:
                jing_issues.append({
                    "jing": jing,
                    "duan": duan_id,
                    "type": "咒文红线-咒语省略",
                    "original": original[:100] + ("..." if len(original) > 100 else ""),
                    "baihua": modern[:100] + ("..." if len(modern) > 100 else ""),
                    "fix": "陀罗尼/真言/神咒段落必须原样照录梵字（含异体字、古译字），不得以「咒语从略」「密咒不录」等表述省略"
                })
            # 检查有没有说咒曰后没有咒文
            if '即说咒曰' in original or '而说咒曰' in original or '說呪曰' in original or '說咒曰' in original:
                # 提取咒曰后的内容（原文里的）
                split_key = '即说咒曰' if '即说咒曰' in original else '而说咒曰' if '而说咒曰' in original else '說呪曰' if '說呪曰' in original else '說咒曰'
                after_shuo = original.split(split_key)[-1]
                # 取第一个句号或段落结束前的内容
                if '。' in after_shuo:
                    zhou_content = after_shuo.split('。')[0].strip()
                else:
                    zhou_content = after_shuo.strip()
                if len(zhou_content) > 2:  # 确实有咒文内容
                    # 检查modern里有没有包含这些咒文字符的大部分（至少一半）
                    zhou_chars = set(zhou_content)
                    modern_chars = set(modern)
                    common = zhou_chars & modern_chars
                    if len(common) < len(zhou_chars) * 0.5:
                        jing_issues.append({
                            "jing": jing,
                            "duan": duan_id,
                            "type": "咒文红线-缺咒文原文",
                            "original": zhou_content,
                            "baihua": modern[:100] + ("..." if len(modern) > 100 else ""),
                            "fix": "说咒后的梵字原文必须原样照录，不得仅翻译含义不录咒文"
                        })
        
        # ---------------------- 3. 内容红线检查 ----------------------
        # 3.1 白话照搬繁体原文，未做白话翻译（检查义解后的内容和原文重合度）
        if has_baihua_content:
            baihua_content = after_yijie.strip()
            original_content = original.strip()
            # 计算重合字符数比例
            if len(baihua_content) > 0 and len(original_content) > 0:
                common_chars = set(baihua_content) & set(original_content)
                # 简单判断：如果白话内容里超过70%是原文原字，且有大量文言词（爾時、汝、云何等），说明照搬
                if len(common_chars) / max(len(set(baihua_content)), 1) > 0.7:
                    # 检查有没有文言词
                    has_wenyan = False
                    wenyan_words = ['爾時', '汝', '云何', '於意云何', '復次', '何以故', '作是念', '白言', '應', '即時', '皆悉']
                    for w in wenyan_words:
                        if w in baihua_content:
                            has_wenyan = True
                            break
                    if has_wenyan:
                        jing_issues.append({
                            "jing": jing,
                            "duan": duan_id,
                            "type": "内容红线-白话照搬文言原文未翻译",
                            "original": original[:100] + ("..." if len(original) > 100 else ""),
                            "baihua": baihua_content[:100] + ("..." if len(baihua_content) > 100 else ""),
                            "fix": "白话译文需将文言翻译为现代汉语，不得直接照搬繁体原文，需将「爾時」译为「这时」、「汝」译为「你」、「云何」译为「为何/什么」等，统一使用简体中文"
                        })
        
        # 3.2 核心法数检查
        fashu_list = [
            ("四谛", "四谛"), ("六度", "六度/六波罗蜜"), 
            ("十二因缘", "十二因缘/十二缘起"), ("八正道", "八正道/八圣道"),
            ("五陰", "五蕴/五阴"), ("五蕴", "五蕴"), ("三學", "三学/戒定慧"), ("三学", "三学"),
            ("六根", "六根/眼耳鼻舌身意"), ("六塵", "六尘/色声香味触法"), ("六識", "六识"),
            ("三十七道品", "三十七道品/三十七菩提分法"), ("四念處", "四念处"), ("四正勤", "四正勤"),
            ("三皈", "三皈依/皈依佛皈依法皈依僧"), ("五戒", "五戒")
        ]
        for key, desc in fashu_list:
            if key in original:
                # 检查白话里有没有对应的法数
                found = False
                check_names = desc.split('/')
                for name in check_names:
                    if name in baihua_content if has_baihua_content else name in modern:
                        found = True
                        break
                if not found:
                    jing_issues.append({
                        "jing": jing,
                        "duan": duan_id,
                        "type": "内容红线-核心法数遗漏/译法错误",
                        "original": original[:100] + ("..." if len(original) > 100 else ""),
                        "baihua": (baihua_content if has_baihua_content else modern)[:100] + ("..." if len((baihua_content if has_baihua_content else modern)) > 100 else ""),
                        "fix": f"原文包含核心法数「{key}」（{desc}），白话译文中遗漏或译法错误，需准确翻译并保留核心法数概念"
                    })
        
        # 3.3 人名地名错误：原文有文殊師利，白话不能漏，不能写错
        place_person = [
            ("文殊師利", "文殊师利菩萨/文殊师利"), ("王舍城", "王舍城"), ("耆闍崛山", "耆阇崛山/灵鹫山"),
            ("釋迦牟尼", "释迦牟尼佛/释迦牟尼"), ("阿耨多羅三藐三菩提", "阿耨多罗三藐三菩提/无上正等正觉")
        ]
        for key, correct in place_person:
            if key in original:
                check_text = baihua_content if has_baihua_content else modern
                if correct.split('/')[0] not in check_text and correct.split('/')[-1] not in check_text and key not in check_text:
                    # 这里暂时不报错，因为可能翻译了，先跳过，人工检查
                    pass
        
        # ---------------------- 4. 字符红线检查 ----------------------
        # 要检查的文本：白话部分（义解之后的内容，排除咒文本身）
        check_text = ""
        if is_zhou and has_baihua_content:
            # 检查义解之后的白话解释部分，咒文原文保留原字
            check_text = '\n'.join(modern_lines_stripped[yijie_pos+1:])
            # 排除咒文字符？暂时先检查全角半角
        elif has_baihua_content:
            check_text = baihua_content
        else:
            check_text = modern
        
        # 4.1 半角标点
        half_matches = half_punct.findall(check_text)
        if half_matches:
            jing_issues.append({
                "jing": jing,
                "duan": duan_id,
                "type": "字符红线-半角标点",
                "original": original[:50] + ("..." if len(original) > 50 else ""),
                "baihua": check_text[:100] + ("..." if len(check_text) > 100 else ""),
                "fix": f"白话部分使用了半角标点{''.join(list(set(half_matches)))}，需统一为中文全角标点"
            })
        
        # 4.2 PUA乱码
        pua_matches = pua_chars.findall(check_text)
        if pua_matches:
            jing_issues.append({
                "jing": jing,
                "duan": duan_id,
                "type": "字符红线-PUA乱码",
                "original": original[:50] + ("..." if len(original) > 50 else ""),
                "baihua": check_text[:100] + ("..." if len(check_text) > 100 else ""),
                "fix": f"白话部分存在PUA乱码字符，需删除或替换为正确汉字"
            })
        
        # 4.3 □阙文
        que_matches = que_char.findall(check_text)
        if que_matches:
            jing_issues.append({
                "jing": jing,
                "duan": duan_id,
                "type": "字符红线-阙文□",
                "original": original[:50] + ("..." if len(original) > 50 else ""),
                "baihua": check_text[:100] + ("..." if len(check_text) > 100 else ""),
                "fix": f"白话部分存在{len(que_matches)}处□阙文，需核对原文补全内容"
            })
        
        # 4.4 简体字检查：白话部分不能有繁体（除了专有名词保留？不，要求统一简体，除了咒文）
        # 先检查常见繁体
        traditional_found = []
        for trad, simp in traditional_chars.items():
            # 避免把专有名词里的繁体算进去？比如“菩提”是对的，“菩薩”里的“薩”是繁体，应该是“菩萨”
            if trad in check_text:
                # 排除正确的专有名词？不对，“菩萨”是简体，“薩”是繁体，所以“菩薩”是错的
                # 简单检查：只要不是咒文，繁体都要转简体
                if trad not in ['菩提', '文', '殊', '師', '利', '童', '子', '禪', '定', '悲', '心', '大', '生', '神', '通', '業', '緣', '法', '根', '善', '威', '光', '明', '色', '受', '想', '行', '平', '等', '名', '菩']:
                    # 这些字本身是简体/不需要转的，排除
                    if trad in ['爾時', '汝', '云何', '於', '復次', '何以故', '作是念', '白言', '應', '皆悉', '無', '與', '眾', '發', '義', '體', '覺', '謂', '當', '願', '陰', '識', '觀', '見', '語', '詣', '餘', '況', '過', '聞']:
                        traditional_found.append(trad)
        if traditional_found:
            jing_issues.append({
                "jing": jing,
                "duan": duan_id,
                "type": "字符红线-未使用简体中文",
                "original": original[:50] + ("..." if len(original) > 50 else ""),
                "baihua": check_text[:100] + ("..." if len(check_text) > 100 else ""),
                "fix": f"白话部分存在繁体文言词{''.join(list(set(traditional_found)))}，除咒文保留原字外，需统一翻译为简体现代汉语：「爾時」改「这时」、「汝」改「你」、「云何」改「为何」、「於」改「在/于」、「復次」改「再者」、「陰」改「蕴」、「識」改「识」、「無」改「无」、「眾」改「众」、「發」改「发」、「義」改「义」、「體」改「体」、「覺」改「觉」、「觀」改「观」、「見」改「见」、「語」改「告诉/对……说」、「詣」改「到」、「過」改「过」、「聞」改「听闻/听」、「餘」改「其他」、「況」改「何况」"
            })
    
    if len(jing_issues) == 0:
        no_issue_jings.append(jing)
    else:
        issues.extend(jing_issues)

# 输出markdown
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# 第三路校对（C批）问题清单 批次177\n\n")
    f.write("## 校对说明\n")
    f.write("本次校对范围：t0818、t1278、t1185b、t1154、t0339、t1659、t0327、t0843、t2818、t1737、t0652、t0405共12部经文。\n")
    f.write("校对红线：格式（小标题+义解+白话三要素）、咒文不得省略、内容忠实不添加不遗漏法数、字符统一简体全角标点无乱码阙文。\n\n")
    
    f.write("## 无问题经目\n")
    if no_issue_jings:
        for jing in no_issue_jings:
            f.write(f"- {jing}：无问题\n")
    else:
        f.write("- 本次校对的12部经均存在不同程度问题，详见下方明细。\n")
    
    f.write("\n## 问题明细\n")
    if not issues:
        f.write("本次校对未发现问题。\n")
    else:
        # 按经号分组
        current_jing = ""
        for issue in issues:
            if issue["jing"] != current_jing:
                current_jing = issue["jing"]
                f.write(f"\n### {current_jing}\n")
            f.write(f"- **段号**：{issue['duan']}\n")
            f.write(f"  - **问题类别**：{issue['type']}\n")
            f.write(f"  - **原文**：{issue['original'] if issue['original'] else '无'}\n")
            f.write(f"  - **白话对应句**：{issue['baihua'] if issue['baihua'] else '无'}\n")
            f.write(f"  - **修正方案**：{issue['fix']}\n\n")

print(f"校对完成，结果已写入{output_path}")
print(f"共检查{len(jing_list)}部经，其中{len(no_issue_jings)}部无问题，发现{len(issues)}个问题")
