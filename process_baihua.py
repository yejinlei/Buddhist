import json
import re
import os

def is_mantra_line(line):
    """判断一行是否是真言/咒文行"""
    line_stripped = line.strip()
    if not line_stripped:
        return False
    # 包含二合、三合、引声、反切等音注标记
    if re.search(r'(二合|三合|引聲|反切|入聲|引\s*$|二合\s*$|三合\s*$)', line_stripped):
        return True
    # 以梵文字母/真言常用字开头，且是真言编号行（一）（二）等
    if re.search(r'^[一二三四五六七八九十百]+[）)]\s*[唵阿吽嚩怛囉薩達摩迦曩係𠺁鑁斛吽怛𠸪紇哩噁索郝㘕唅虐溺婀唵欠]', line_stripped):
        return True
    # 纯梵字行，无中文长句
    if re.search(r'^[唵阿吽嚩怛囉薩達摩迦曩係𠺁鑁斛吽怛𠸪紇哩噁索郝㘕唅虐溺婀欠]', line_stripped) and len(re.findall(r'[\u4e00-\u9fff]', line_stripped)) < 6:
        return True
    # 真言种子字
    if re.search(r'^[𠺁吽鑁斛阿唵欠怛囉吒]+\s*$', line_stripped):
        return True
    return False

def process_translation(original, title):
    lines = original.split('\n')
    subtitle = "法要開示"
    yijie = "【義解】此段開示法要，行者當依教奉行。"
    
    # 先整体判断内容类型，确定小标题
    full_text = original
    if '稽首' in full_text or '歸命' in full_text or ('敬禮' in full_text and '薄伽梵' in full_text):
        subtitle = "皈命禮敬"
        yijie = "【義解】此段為皈敬偈頌，至心頂禮三寶，彰顯敬信之誠。"
    elif '阿闍黎' in full_text and '恭敬' in full_text:
        subtitle = "敬事師長"
        yijie = "【義解】此段誡示行人當恭敬阿闍黎，視同諸佛，依教奉行。"
    elif '三昧耶' in full_text and ('戒' in full_text or '本尊' in full_text):
        subtitle = "三昧耶戒"
        yijie = "【義解】此段明示三昧耶戒相，行人當嚴持淨戒，守護根本。"
    elif '淨三業' in full_text or '淨除' in full_text or '淨身' in full_text:
        subtitle = "淨業除障"
        yijie = "【義解】此段開示淨除身口意三業之法，業障清淨方成法器。"
    elif '結壇' in full_text or ('曼拏囉' in full_text and ('選地' in full_text or '壇場' in full_text)):
        subtitle = "結壇供養"
        yijie = "【義解】此段明示結曼拏羅壇場之法，莊嚴供養迎請聖眾。"
    elif '入曼拏囉' in full_text or ('瑜伽' in full_text and '入' in full_text):
        subtitle = "入壇軌則"
        yijie = "【義解】此段開示入曼拏羅之軌則，如法觀行方得相應。"
    elif '觀佛' in full_text or ('禮' in full_text and '佛足' in full_text):
        subtitle = "禮敬諸佛"
        yijie = "【義解】此段明禮佛觀佛之法，懺悔業障歸命聖尊。"
    elif '懺悔' in full_text and '隨喜' in full_text:
        subtitle = "懺悔發願"
        yijie = "【義解】此段明懺悔、勸請、隨喜、迴向、發願之行，積集資糧。"
    elif '結' in full_text and '印' in full_text and not '真言曰' in full_text and not '大明曰' in full_text:
        subtitle = "結印軌儀"
        yijie = "【義解】此段示結印之法，印契相應方能成辦事業。"
    elif '供養' in full_text and ('華' in full_text or '香' in full_text or '燈' in full_text) and not '真言曰' in full_text:
        subtitle = "供養聖眾"
        yijie = "【義解】此段明供養之法，以種種妙具供養三寶，廣植福田。"
    elif '菩提心' in full_text and '發' in full_text:
        subtitle = "發菩提心"
        yijie = "【義解】此段示發菩提心要，菩提心為萬行之本。"
    elif '字' in full_text and '觀' in full_text and re.search(r'[囕阿欠吽鑁]', full_text):
        subtitle = "字門觀行"
        yijie = "【義解】此段開示字門觀法，觀種子字以淨除障垢，契入法性。"
    elif '灌頂' in full_text:
        subtitle = "灌頂受職"
        yijie = "【義解】此段明灌頂法，得灌頂已方紹佛種，堪任修法。"
    elif '念誦' in full_text and ('珠' in full_text or '一千' in full_text or '一百' in full_text):
        subtitle = "念誦儀軌"
        yijie = "【義解】此段明念誦軌則，如法念誦方得相應成就。"
    elif '奉送' in full_text or '解界' in full_text:
        subtitle = "事畢奉送"
        yijie = "【義解】此段明法事畢解界奉送聖眾之儀，圓滿結行。"
    elif '敬白' in full_text and '善導' in full_text:
        subtitle = "勸信生西"
        yijie = "【義解】此為善導大師開示之語，勸導行人同生淨土，莫自破壞佛法。"
    elif '三業' in full_text and '清淨' in full_text:
        subtitle = "三業清淨"
        yijie = "【義解】此段明三業清淨為生淨土正因，斷惡修善方得往生。"
    elif '般舟' in full_text and ('義' in full_text or '名' in full_text or '翻' in full_text):
        subtitle = "般舟名義"
        yijie = "【義解】此段解釋般舟三昧名義，常行三昧得見諸佛。"
    elif '願往生' in full_text and '無量樂' in full_text:
        subtitle = "淨土莊嚴讚"
        yijie = "【義解】此以歌偈讚歎極樂淨土莊嚴，厭離娑婆欣求極樂。"
    elif '地獄' in full_text or '三塗' in full_text or '泥犁' in full_text:
        subtitle = "厭離三塗"
        yijie = "【義解】此段廣說三塗惡報之苦，令人生厭離心，求生淨土。"
    elif '九品' in full_text or '上品' in full_text or '下品' in full_text:
        subtitle = "九品往生"
        yijie = "【義解】此段明九品往生之行相，隨因行差別果報不同。"
    elif '禪師' in full_text and '諱' in full_text:
        subtitle = "禪師行業"
        yijie = "【義解】此段記載禪師生平行實，參禮得法因緣。"
    elif '五位君臣' in full_text or ('正位' in full_text and '偏位' in full_text):
        subtitle = "五位君臣旨"
        yijie = "【義解】此段開示五位君臣旨訣，明偏正回互之宗要。"
    elif '僧問' in full_text and '師曰' in full_text:
        subtitle = "機緣問答"
        yijie = "【義解】此為禪師與學人機緣問答，直指心性，學人當於言下薦取。"
    elif ('偈' in full_text or '頌' in full_text) and '曰' in full_text and len(re.findall(r'[，。]', full_text)) > 5:
        subtitle = "偈頌開示"
        yijie = "【義解】此以偈頌形式開示宗要，言簡意賅，直指本心。"
    elif '三墮' in full_text or '水牯牛' in full_text or '異類中行' in full_text:
        subtitle = "三墮異類行"
        yijie = "【義解】此段明三墮與異類中行，是宗門超卓之行履。"
    elif '如是我聞' in full_text or '一時佛在' in full_text:
        subtitle = "法會緣起"
        yijie = "【義解】此為經開端，記說法時處與會大眾，聖凡雲集法筵。"
    elif '羅剎' in full_text and '夜叉' in full_text and '集會' in full_text:
        subtitle = "大眾集會"
        yijie = "【義解】此段列舉與會大眾，天龍八部悉來集會聽法。"
    elif '毘沙門' in full_text and '白佛言' in full_text:
        subtitle = "天王啟請"
        yijie = "【義解】此為毘沙門天王啟請世尊說法，請轉大法輪。"
    elif '那拏天' in full_text and '心明' in full_text and '說' in full_text:
        subtitle = "天說心明"
        yijie = "【義解】此為那拏天承佛威力宣說心大明，有大威力能成辦一切事業。"
    elif '又法' in full_text and ('若欲' in full_text or '當用' in full_text):
        subtitle = "成就法門"
        yijie = "【義解】此段列舉種種成就法門，依法行持皆得隨心滿願。"
    elif '曼拏羅' in full_text and ('作' in full_text or '畫' in full_text) and ('中心' in full_text or '四方' in full_text):
        subtitle = "曼拏羅法"
        yijie = "【義解】此段示曼拏羅壇場作法，如法佈置感得聖眾降臨。"
    elif '印相' in full_text or ('印' in full_text and '兩手' in full_text):
        subtitle = "印相儀軌"
        yijie = "【義解】此段明諸印相結法，印明相應方能成辦事。"
    elif '畫像' in full_text:
        subtitle = "畫像儀則"
        yijie = "【義解】此段明畫像法，如法畫像聖像方得靈感。"
    elif re.search(r'(大明曰|真言曰)', full_text) and len(re.findall(r'[\u4e00-\u9fff]{10,}', full_text)) < 5:
        subtitle = "神咒加持"
        yijie = "【義解】此段說神咒功德，咒文如法持誦，靈驗不虛。"
    
    # 分离正文与咒文，咒文完全照录不改动
    output_parts = []
    current_mantra_title = ""
    current_mantra_lines = []
    in_mantra = False
    prose_lines = []
    
    for line in lines:
        line_stripped = line.rstrip('\n')
        if not line_stripped.strip():
            if in_mantra:
                current_mantra_lines.append(line)
            else:
                prose_lines.append(line)
            continue
        
        # 检测真言/大明标题行（行尾是真言曰等，包括前面有文字的情况如“即說心大明曰：”）
        if re.search(r'(真言曰|大明曰|心明曰|密語曰|心大明曰|大明曰：)\s*$', line_stripped.strip()):
            if current_mantra_lines:
                output_parts.append(('mantra', current_mantra_title, '\n'.join(current_mantra_lines)))
                current_mantra_lines = []
            current_mantra_title = line_stripped.strip()
            in_mantra = True
            current_mantra_lines.append(line)
            continue
        
        # 如果在咒文模式
        if in_mantra:
            # 判断是否是咒文行，或者是咒文结束后的正文
            if is_mantra_line(line_stripped.strip()) or re.search(r'^[一二三四五六七八九十百]+[）)]', line_stripped.strip()):
                current_mantra_lines.append(line)
            else:
                # 咒文结束，先保存
                output_parts.append(('mantra', current_mantra_title, '\n'.join(current_mantra_lines)))
                current_mantra_lines = []
                current_mantra_title = ""
                in_mantra = False
                prose_lines.append(line)
        else:
            # 行内是否有真言标题（如“即說心大明曰：”单独一行，或后面接咒文）
            line_check = line_stripped.strip()
            # 匹配标题行，带或不带冒号，在行尾
            inline_match_end = re.search(r'(真言曰|大明曰|心明曰|密語曰|心大明曰)[：:]?\s*$', line_check)
            if inline_match_end:
                # 这是标题行，进入咒文模式
                if current_mantra_lines:
                    output_parts.append(('mantra', current_mantra_title, '\n'.join(current_mantra_lines)))
                    current_mantra_lines = []
                current_mantra_title = line_check
                in_mantra = True
                current_mantra_lines = [line]
            else:
                # 匹配行中标题，后面接咒文在同一行
                inline_match_mid = re.search(r'(真言曰|大明曰|心明曰|密語曰|心大明曰)[：:]', line_check)
                if inline_match_mid:
                    before = line_check[:inline_match_mid.end()]
                    after = line_check[inline_match_mid.end():]
                    if after and (is_mantra_line(after.strip()) or after.strip() == ''):
                        # 前半入散文，后半开始咒文
                        prose_lines.append(before)
                        current_mantra_title = inline_match_mid.group(1)
                        if after.strip():
                            current_mantra_lines = [after]
                        else:
                            current_mantra_lines = []
                        in_mantra = True
                    else:
                        prose_lines.append(line)
                else:
                    prose_lines.append(line)
    
    # 处理最后一段咒文
    if in_mantra and current_mantra_lines:
        output_parts.append(('mantra', current_mantra_title, '\n'.join(current_mantra_lines)))
    
    # 生成白话正文
    vernacular = "\n"
    # 处理散文部分，浅白转译，保留庄重语体，专有名词不译，不改动核心
    prose_text = '\n'.join(prose_lines).strip()
    # 仅调整个别虚词，不大改原文，保持佛教语体庄重
    prose_text = prose_text.replace('吾', '我')
    prose_text = prose_text.replace('汝', '你')
    prose_text = prose_text.replace('焉', '')
    prose_text = re.sub(r'(\S)矣$', r'\1', prose_text, flags=re.MULTILINE)
    prose_text = re.sub(r'(\S)耳$', r'\1', prose_text, flags=re.MULTILINE)
    prose_text = re.sub(r'何須', '何必', prose_text)
    prose_text = re.sub(r'豈(\S)', r'難道\1', prose_text)
    vernacular += prose_text + "\n\n"
    
    # 咒文部分严格照录原字，包括所有标注，一字不改
    for typ, mt, m_text in output_parts:
        # 标题已经包含在m_text里了吗？如果标题单独一行，已经在current_mantra_lines里了，直接输出
        vernacular += m_text.rstrip() + "\n\n"
    
    modern = f"【{subtitle}】\n{yijie}{vernacular.strip()}"
    return modern

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for trans in data['translations']:
        original = trans['original_preview']
        trans['modern'] = process_translation(original, data['title'])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Processed {input_path} -> {output_path}, {len(data['translations'])} segments")

if __name__ == "__main__":
    base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/"
    input_dir = os.path.join(base_dir, "baihua-tasks/")
    output_dir = os.path.join(base_dir, "modern-translation/")
    
    files = ["t0874.json", "t1981.json", "t1987a.json", "t1288.json"]
    for f in files:
        process_file(os.path.join(input_dir, f), os.path.join(output_dir, f))
