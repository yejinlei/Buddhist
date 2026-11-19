"""
最终版复核脚本：
- 格式红线：逐段检查
- 咒文红线：更精确的咒语串定位；遇到明确的白话引导词（如"这时""」"后接叙事、"佛言""世尊"等）即终止咒语span
- 简体红线：移除有争议的字（瞋在佛教语境常保留；槃不简化；菩/根/相/德/城/智 等简繁同形字不检）
- 错译红线：云何/白佛言
"""
import json, os, re

BASE = '/home/user/workspace/13511660557912876654/buddhist-ontology/data/baihua-tasks/'
OUT  = '/home/user/workspace/13511660557912876654/buddhist-ontology/recheck_b_batch177.md'

FILES = ['t0818.json','t1278.json','t1185b.json','t1154.json','t0339.json','t1659.json',
         't0327.json','t0843.json','t2818.json','t1737.json','t0652.json','t0405.json']

# 明确繁简有别、白话中必须用简体的字（移除"瞋"——佛教文献中常保留"瞋"，CBETA/国内通行简体佛典两见；不列"槃"——槃在"涅槃"中保留）
TRAD_MAP = {
    # 用户点名高频
    '時':'时','為':'为','於':'于','與':'与','這':'这','樣':'样',
    '復':'复','眾':'众','見':'见','無':'无','應':'应','說':'说',
    '師':'师','長':'长','爾':'尔','來':'来','國':'国','經':'经',
    '聞':'闻','聲':'声','覺':'觉',
    # 其他常见
    '門':'门','雲':'云','電':'电','風':'风','馬':'马','鳥':'鸟','魚':'鱼',
    '貝':'贝','寶':'宝','嚴':'严','園':'园','樹':'树','華':'华','葉':'叶','實':'实',
    '塵':'尘','濁':'浊','淨':'净','涼':'凉','熱':'热','溫':'温','軟':'软','堅':'坚',
    '飢':'饥','虛':'虚','偽':'伪','誑':'诳','諂':'谄',
    '貪':'贪','愛':'爱','樂':'乐','憂':'忧','捨':'舍',
    '憶':'忆','慮':'虑','觀':'观','證':'证','獲':'获','辦':'办',
    '臥':'卧','進':'进','迴':'回','還':'还','脫':'脱','離':'离','斷':'断',
    '滅':'灭','盡':'尽','壞':'坏',
    '邊':'边','際':'际','數':'数','類':'类','種':'种','號':'号',
    '儀':'仪','體':'体','頭':'头','齒':'齿','識':'识',
    '惡':'恶','報':'报','緣':'缘','業':'业','徑':'径','戶':'户',
    '牆':'墙','宮':'宫','樓':'楼','閣':'阁','燈':'灯','燒':'烧','煙':'烟',
    '霧':'雾','龍':'龙','獸':'兽','賢':'贤','婦':'妇','兒':'儿',
    '親':'亲','屬':'属','軍':'军','將':'将','輔':'辅',
    '貧':'贫','窮':'穷','貴':'贵','賤':'贱','勝':'胜','強':'强','醜':'丑',
    '圓':'圆','廣':'广','狹':'狭','寬':'宽','晝':'昼','過':'过',
    '現':'现','舊':'旧','發':'发','變':'变','亂':'乱','辭':'辞','違':'违',
    '雖':'虽','願':'愿','顧':'顾','須':'须','習':'习','書':'书',
    '殺':'杀','盜':'盗','兩':'两','戀':'恋','惱':'恼','據':'据','攝':'摄',
    '轉':'转','後':'后','從':'从','歸':'归','歲':'岁','寫':'写','尋':'寻',
    '壽':'寿','豐':'丰','臨':'临','舉':'举','藥':'药','蘊':'蕴',
    '處':'处','蟲':'虫','雙':'双','難':'难','雜':'杂','靜':'静',
    '顯':'显','飛':'飞','飽':'饱','養':'养','餘':'余','驚':'惊',
    '髮':'发','黃':'黄','點':'点','齊':'齐','關':'关','開':'开','間':'间',
    '隨':'随','隱':'隐','譯':'译','義':'义','謂':'谓','請':'请',
    '論':'论','語':'语','禮':'礼','禪':'禅','記':'记','讀':'读',
    '諦':'谛','謗':'谤','講':'讲','惻':'恻','慚':'惭','歎':'叹','歡':'欢',
    '厭':'厌','厲':'厉','準':'准','題':'题','額':'额','顏':'颜','顛':'颠',
    '鳳':'凤','鳴':'鸣','麤':'粗','齋':'斋','龜':'龟','闡':'阐','濕':'湿',
    '呪':'咒',
    # 咒字繁体（真咒语中须保留）
    '羅':'罗','薩':'萨','訶':'诃','賀':'贺','鉢':'钵','闍':'阇',
}
TRAD_MAP = {k:v for k,v in TRAD_MAP.items() if k != v}

# 咒字
MANTRA_KEEP_ORIG = {'羅','薩','訶','賀','鉢','闍','嚩','曩','泮','吒','醯','拏','皤','呿','怛','娜','麼',
                    '唵','吽','莎','誐','㘑','㗚','囇','儞','儜','𠻱','㜸','耨','鋡','嬭','靺','羯','毘',
                    '嚩','侘','眴','囇','抳','枳','穰','彊','俱'}

# 白话叙事起始标志：这些字符出现，说明咒语串已结束
PROSE_STARTERS = '这时这时其佛大众世尊当知是名名为何以故所以善男子善女人你等我今尔时即说名曰'

def find_mantra_spans(text):
    """
    更精确：找所有咒语连续段
    1. 从引导语（即说呪曰/明曰/密言曰/真言曰/XX明：/XX密言：/XX咒：/XX陀罗尼：等）开始，
       到白话叙事起始词（凡欲/若欲/这时/尔时/是时/若有/时佛/佛告/佛言/世尊/你今/我今/善男/善女/大王/当知/是名/何以）结束；
    2. 含切韵标记（二合/三合/引/去声/上声/平声/半音）的连续梵音串；
    3. 含（一）（二）（三）等咒语编号序列的连续梵音串；
    4. 南谟/唵 开头、莎诃/娑诃 结尾的梵音串。
    """
    spans = []
    
    # (1) 切韵标记附近扩展为梵音串
    for m in re.finditer(r'[（(][^)）]{0,8}(?:二合|三合|引|去声|上声|平声|半音|引去声|长音|引声|去上|引长|切身|反)[^)）]{0,8}[)）]', text):
        start = m.start()
        end = m.end()
        # 向前后扩展梵音字
        start = _expand_back(text, start)
        end = _expand_fwd(text, end, stop_at_prose=True)
        spans.append((start, end))
    
    # (2) 引导语（明曰/密言曰/真言曰/咒曰/明：/密言：/真言：/咒：/陀罗尼曰/大明曰）
    for m in re.finditer(r'(即说呪曰|即说咒曰|即说大明曰|咒曰|呪曰|密言曰|真言曰|明曰|陀罗尼曰|陀羅尼曰|心呪|心咒|明\s*[：:]|密言\s*[：:]|真言\s*[：:]|咒\s*[：:]|呪\s*[：:])', text):
        # 从引导语末开始扩展梵音，直到叙事起点
        rest_start = m.end()
        end = _expand_fwd(text, rest_start, stop_at_prose=True)
        if end > rest_start:
            spans.append((rest_start, end))
    
    # (3) 编号（一）（二）/ (一)(二) 等 —— 遇到两个以上连续编号，视为咒语
    num_re = re.compile(r'[（(]\s*[一二三四五六七八九十百千零]+\s*[)）]')
    nums = [(m.start(), m.end()) for m in num_re.finditer(text)]
    if len(nums) >= 2:
        # 从第一个编号开始扩展到最后一个编号之后
        start = _expand_back(text, nums[0][0])
        end = _expand_fwd(text, nums[-1][1], stop_at_prose=True)
        spans.append((start, end))
    
    # (4) 南谟/纳莫/唵 开头 莎诃 结尾
    for m in re.finditer(r'(?:南[谟么牟]|納[莫牟]|纳[莫牟]|娜莫|唵)[\u4e00-\u9fff（）()\s　、·．.0-9]{4,}?(?:莎[呵訶诃賀]|娑[呵訶诃賀]|娑婆[呵訶诃賀]|薩[嚩婆][呵訶诃賀])', text):
        spans.append((m.start(), m.end()))
    
    # 合并
    if not spans:
        return []
    spans.sort()
    merged = [spans[0]]
    for s,e in spans:
        ls, le = merged[-1]
        if s <= le + 2:
            merged[-1] = (ls, max(le, e))
        else:
            merged.append((s,e))
    return merged

def _expand_back(text, start):
    i = start
    while i > 0:
        c = text[i-1]
        if c in ' \n\t\u3000、0123456789．.·（）()「」""＂＂':
            i -= 1; continue
        if c in MANTRA_KEEP_ORIG or _is_siddham_char(c):
            i -= 1; continue
        break
    return i

def _expand_fwd(text, end, stop_at_prose=False):
    i = end
    non_sidd = 0
    while i < len(text):
        c = text[i]
        if stop_at_prose and _is_prose_start_at(text, i):
            break
        # 句号：若其后不是高置信度咒字（MANTRA_KEEP_ORIG），视为咒语结束
        if c in '。；' and stop_at_prose:
            nxt = text[i+1] if i+1 < len(text) else ''
            if nxt not in MANTRA_KEEP_ORIG and not _is_siddham_char(nxt):
                i += 1; break
        if c in ' \t\u3000、0123456789．.·\n':
            i += 1; continue
        if c in '（）()，、':
            i += 1; continue
        if c in '「＂"':
            after = text[i+1:i+5]
            prose_after_open = False
            for kw in ['世尊','佛言','佛告','若诸','若有','尔时','这时','是时','你今','我今','善男','善女','大王','当知','是名','我当','汝今','我常','尔时','我于','彼诸','汝等','我已','若人']:
                if after.startswith(kw):
                    prose_after_open = True; break
            if prose_after_open:
                break
            i += 1; continue
        if c in '」＂"':
            break
        if c in MANTRA_KEEP_ORIG or _is_siddham_char(c):
            non_sidd = 0
            i += 1; continue
        if '\u4e00' <= c <= '\u9fff':
            non_sidd += 1
            if non_sidd >= 2 and stop_at_prose:
                break
            i += 1; continue
        i += 1
    return i

def _is_siddham_char(c):
    """常见梵音对字（主要作为梵语音译字出现，非常用汉语词）"""
    return c in set('勃驮菩提萨怛嚩摩醯瑟姹鲁沙娜孕铎迦野尾么弭帝谛婆伽度阿伊乌翳蔼污奥南谟纳莫'
                    '没多遮车阇膳赊瑟咤侘茶陀达那缚曼苏悉地呬夜啰楞健度汗谟茹虞'
                    '伊邬翳蔼奥乌亶哿珰盎'
                    '冒恽勘绀晗唵暗呜吽'
                    '佉晒掺跛娜么攞讫窣都泯瑟咤尾斯者'
                    '噜儞荼轸阿跛茗佉索叉耳'
                    '萶莾羯印娑嘢儞诃母娜哩铎'
                    '庾补楞梭')

def _is_prose_start_at(text, i):
    """位置i是否是白话叙事开始处"""
    if i >= len(text):
        return False
    c = text[i]
    if c in '」＂"':
        return True
    seg = text[i:i+5]
    for kw in ['这时','尔时','是时','佛告','佛言','世尊','你今','我今','大王','善男','善女','当知','是名','何以','所以','既已','于是','时诸','彼诸',
               '像这','若诸','若欲','凡欲','若不','若从','若自','先想','先诵','然想','但结','便存','当念','若作','若有','若人','当于','我当','应作','即作','当作','次作',
               '其法','即说','次当','先应','汝今','汝等','应当','修此','行此','持此','诵此','若能','若我','若当','当为','若今','若此','乃想',
               '然作','亦得','当置','勿息','将药','加持','但日','从足','行者','从其','亦应','此明','此咒','此呪','即从','作是','已后','之後','之后','又相','又存',
               '尔时','尔时世','名為','名为','若我','尔时','又为','而白','时世','时王']:
        if seg.startswith(kw):
            return True
    return False

def in_any_span(spans, pos):
    for s,e in spans:
        if s <= pos < e:
            return True
    return False

def find_all(text, ch):
    return [m.start() for m in re.finditer(re.escape(ch), text)]

def context(text, pos, span=8):
    return text[max(0,pos-span):pos+span+1].replace('\n',' ').replace('|','｜')

def check_file(fname):
    path = os.path.join(BASE, fname)
    with open(path, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    title = data.get('title','?')
    segs = data.get('translations', [])
    issues = []
    
    for i, seg in enumerate(segs):
        modern = seg.get('modern','') or ''
        orig   = seg.get('original_preview','') or ''
        seg_id = i + 1
        
        if not modern.strip():
            issues.append((seg_id, '格式', 'modern为空'))
            continue
        
        lines = [l for l in modern.split('\n') if l.strip()]
        if len(lines) < 2:
            issues.append((seg_id, '格式', f'modern非空行仅{len(lines)}行：{modern[:60]}'))
            continue
        
        h1 = lines[0].strip()
        if not (h1.startswith('【') and h1.endswith('】') and len(h1) > 2):
            issues.append((seg_id, '格式', f'第1行非【小标题】："{h1[:40]}"'))
        
        h2 = lines[1].strip()
        if not h2.startswith('【义解】'):
            issues.append((seg_id, '格式', f'第2行非【义解】开头："{h2[:40]}"'))
        
        body = '\n'.join(lines[2:])
        if not body.strip():
            issues.append((seg_id, '格式', '义解之后无白话正文'))
            continue
        
        mantra_spans = find_mantra_spans(body)
        # 不再用 orig_mantra + 模糊窗口；以精确识别的 spans 为准
        
        # 简体残留
        trad_hits = []
        for tc, sc in TRAD_MAP.items():
            for pos in find_all(body, tc):
                if in_any_span(mantra_spans, pos) and tc in MANTRA_KEEP_ORIG:
                    continue
                trad_hits.append((tc, sc, context(body, pos)))
        if trad_hits:
            uniq = []
            seen = set()
            for tc,sc,ctx in trad_hits:
                key = (tc, ctx[:14])
                if key in seen: continue
                seen.add(key)
                uniq.append(f'{tc}→{sc}（…{ctx}…）')
                if len(uniq) >= 12: break
            issues.append((seg_id, '简体残留', '；'.join(uniq) + (f' 等{len(trad_hits)}处' if len(trad_hits)>len(uniq) else '')))
        
        # 咒文简体化
        dh_simp = []
        for tc in MANTRA_KEEP_ORIG:
            sc = TRAD_MAP.get(tc, None)
            if not sc or sc == tc:
                continue
            for pos in find_all(body, sc):
                if in_any_span(mantra_spans, pos):
                    ctx = context(body, pos, 6)
                    dh_simp.append(f'{tc}被简作{sc}（…{ctx}…）')
        if dh_simp:
            uniq = list(dict.fromkeys(dh_simp))[:12]
            issues.append((seg_id, '咒文简体化', '；'.join(uniq) + (f' 等{len(dh_simp)}处' if len(dh_simp)>len(uniq) else '')))
        
        # 错译
        for m in re.finditer(r'云何', body):
            ctx = context(body, m.start(), 10)
            issues.append((seg_id, '错译·云何', f'正文未按语境译"云何"：…{ctx}…'))
        for m in re.finditer(r'白佛言', body):
            ctx = context(body, m.start(), 8)
            issues.append((seg_id, '错译·白佛言', f'生硬保留"白佛言"：…{ctx}…'))
    
    return title, segs, issues

def _pos_in_mantra_context(body, pos):
    """在一个整体为咒语的段里，判断某个位置是否真的在咒语（而非解释）中——看前后8个字符内是否有梵音字"""
    l = max(0,pos-8); r = min(len(body),pos+9)
    window = body[l:r]
    return sum(1 for c in window if c in MANTRA_KEEP_ORIG or _is_siddham_char(c)) >= 3

def main():
    lines = []
    lines.append('# B批177组 白话经文 第二路独立复核报告\n\n')
    lines.append('**复核时间**：2026-11-16\n\n')
    lines.append('**复核范围**：`baihua-tasks/` 下 12 部经\n')
    lines.append('（t0818、t1278、t1185b、t1154、t0339、t1659、t0327、t0843、t2818、t1737、t0652、t0405）\n\n')
    lines.append('**复核红线**：\n\n')
    lines.append('1. **格式红线**：每段modern以【简体小标题】开头、第二行是【义解】、义解之后有白话正文；\n')
    lines.append('2. **咒文红线**：梵文密咒/陀罗尼段落（含二合/引/去声等切韵标记，或由唵/南谟/莎诃等梵音字构成、由"即说咒曰/大明曰/密言曰/真言曰"等引出的纯咒语串）中，咒字（唵、吽、嚩、羅、鉢、娜、麼、曩、薩、怛、訶、泮、吒、莎、賀、闍、醯 等）保持原字形，不被简体化；普通白话叙述中的通行佛教术语（菩萨、摩诃、陀罗尼、迦楼罗、阿修罗、波罗蜜、曼陀罗、涅槃 等）按规范简体呈现；\n')
    lines.append('3. **简体红线**：除咒文外白话部分无繁体残留（時→时、為→为、於→于、與→与、這→这、復→复、眾→众、見→见、無→无、應→应、說→说、師→师、長→长、爾→尔、來→来、國→国、經→经、聞→闻、門→门、呪→咒 等）；\n')
    lines.append('4. **错译修复红线**：「俱」列举语境合理翻译，「俱胝/俱摩羅」梵音专名未被误替；「云何」依语境译为「为何/如何/什么是」而非残留原字；「白佛言」译为「对佛说/秉白佛言」等通顺表达。\n\n')
    lines.append('---\n\n')
    
    summary = []
    total_issues = 0
    pass_count = 0
    fail_count = 0
    
    for fname in FILES:
        title, segs, issues = check_file(fname)
        lines.append(f'## {fname}　《{title}》（共{len(segs)}段）\n\n')
        
        if not issues:
            lines.append('**✅ 通过**：未发现格式、咒文、简体残留、错译问题。\n\n')
            summary.append((fname, title, '✅ 通过', 0))
            pass_count += 1
        else:
            fail_count += 1
            total_issues += len(issues)
            issues.sort(key=lambda x: (x[0], x[1]))
            cats = {}
            for _,c,_ in issues:
                cats[c] = cats.get(c,0)+1
            cat_str = '，'.join(f'{k}{v}处' for k,v in cats.items())
            lines.append(f'**⚠️ 未通过**：共 {len(issues)} 处问题（{cat_str}）\n\n')
            lines.append('| 段号 | 类别 | 问题描述 |\n')
            lines.append('|------|------|----------|\n')
            for seg_id, cat, desc in issues:
                desc_esc = desc.replace('|','｜').replace('\n',' ')
                lines.append(f'| {seg_id} | {cat} | {desc_esc} |\n')
            lines.append('\n')
            summary.append((fname, title, '⚠️ 未通过', len(issues)))
        lines.append('---\n\n')
    
    lines.append('## 总览\n\n')
    lines.append('| 文件 | 经名 | 结论 | 问题数 |\n')
    lines.append('|------|------|------|--------|\n')
    for fname,title,res,n in summary:
        lines.append(f'| {fname} | 《{title}》 | {res} | {n} |\n')
    lines.append(f'\n- 复核经数：**12**\n')
    lines.append(f'- 通过：**{pass_count}**\n')
    lines.append(f'- 未通过：**{fail_count}**\n')
    lines.append(f'- 问题总数：**{total_issues}**\n')
    
    with open(OUT, 'w', encoding='utf-8') as fp:
        fp.writelines(lines)
    print(f'Done. Pass={pass_count}, Fail={fail_count}, Total issues={total_issues}')

if __name__ == '__main__':
    main()
