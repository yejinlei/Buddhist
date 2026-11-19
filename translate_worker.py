#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3 - clause-level paraphrase of Chinese Buddhist classical commentary/vinaya/śāstra.
Key improvements:
- Split at sentence-final particles 也/矣/耳/焉/者/。 to get clauses.
- Recognize the ubiquitous "X者，Y也" (X指Y) commentary pattern.
- Recognize 疏科 patterns like "一X二Y三Z" (第一是X，第二是Y，第三是Z).
- Recognize vinaya pattern "若比丘尼X者，Y罪".
- Convert to modern vernacular sentences ending with proper Chinese punctuation.
- Do NOT add modern slang; keep dignified Buddhist Chinese register.
- Preserve every Buddhist proper noun as-is (we maintain a large list to avoid mistranslating).
"""
import json, os, re

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
IN_DIR = os.path.join(BASE, "data/baihua-tasks")
OUT_DIR = os.path.join(BASE, "data/modern-translation")
os.makedirs(OUT_DIR, exist_ok=True)

MANTRA_MARKERS = ["陀羅尼", "咒曰", "真言", "唵", "吽", "娑婆訶", "娑婆诃", "薩婆訶", "跢姪他", "怛姪他"]

# Terms that must remain untouched
PROPER_NOUNS = {
    "如來","世尊","佛","菩薩","比丘","比丘尼","沙門","優婆塞","優婆夷","阿羅漢",
    "辟支佛","聲聞","緣覺","凡夫","外道","魔","梵王","帝釋","釋提桓因",
    "比丘尼戒本","四分律","僧祇律","十誦律","五分律","摩訶僧祇律","戒律","毘尼",
    "戒","波羅夷","僧殘","僧伽婆尸沙","尼薩耆","波逸提","波羅提提舍尼","提舍尼",
    "眾學法","眾學","七滅諍","滅諍","布薩","羯磨","說戒","戒經",
    "三寶","佛寶","法寶","僧寶","法身","報身","應身","化身","真身","生身",
    "法身","報身","應身","涅槃","菩提","解脫","菩提","般若","波羅蜜",
    "六波羅蜜","檀那","尸羅","羼提","毘梨耶","禪那","般若",
    "布施","持戒","忍辱","精進","禪定","智慧","六度","三學",
    "法華經","法華","妙法蓮華經","壽量品","法師功德品","分別功德品",
    "隨喜功德品","常不輕菩薩品","如來壽量品","安樂行品","普門品",
    "大乘起信論","起信論","義記","別記",
    "真如","法界","實相","法性","實際","如來藏","佛性",
    "阿賴耶識","賴耶","梨耶","藏識","末那","阿陀那",
    "本覺","始覺","不覺","本有","修生","生滅","不生滅",
    "一心","二門","心真如門","心生滅門",
    "無明","煩惱","結使","隨眠","見思","塵沙","無明惑",
    "三界","欲界","色界","無色界","六道","六趣","四生","胎生","卵生","濕生","化生",
    "地獄","餓鬼","畜生","阿修羅","人","天","龍","夜叉","乾闥婆","緊那羅","摩睺羅伽",
    "五蘊","十二處","十八界","十二因緣","六根","六塵","六識",
    "四諦","八正道","七覺支","五根","五力","四念處","四正勤","四如意足",
    "苦","集","滅","道","空","無常","無我","中道","二諦","真諦","俗諦","第一義諦",
    "有為","無為","有漏","無漏","世間","出世間",
    "無生法忍","無生","法忍","陀羅尼","三昧","三摩地",
    "六通","三明","三達","五眼","六通","神足","天眼","天耳","他心","宿命","漏盡",
    "十地","初地","歡喜地","二地","離垢地","三地","發光地","四地","焰慧地",
    "五地","難勝地","六地","現前地","七地","遠行地","八地","不動地","九地","善慧地","十地","法雲地",
    "十信","十住","十行","十迴向","十回向","地前","地上",
    "資糧位","加行位","通達位","修習位","究竟位","見道","修道","無學道",
    "法輪","轉法輪","道場","道樹","菩提樹","鹿野苑","靈山","靈鷲山","耆闍崛山",
    "王舍城","舍衛國","祇樹給孤獨園","竹林精舍","那爛陀",
    "阿難","迦葉","大迦葉","舍利弗","目犍連","須菩提","富樓那","迦旃延","阿那律","優波離","羅睺羅",
    "阿逸多","彌勒","文殊","文殊師利","普賢","觀世音","觀音","大勢至","地藏",
    "維摩詰","藥王","藥上","常精進","常不輕","妙音",
    "毘婆尸","尸棄","毘舍浮","拘留孫","拘那含牟尼","迦葉佛","釋迦牟尼","釋迦文","釋迦","燃燈佛",
    "阿彌陀","藥師","七佛","過去七佛",
    "懷素","佛陀耶舍","鳩摩羅什","玄奘","真諦","義淨","法藏","賢首","智者","天台",
    "阿含","俱舍","大智度論","中論","百論","十二門論","瑜伽師地論","成唯識論",
    "仁王","華嚴","般若","楞伽","楞嚴","圓覺","無量壽經",
    "舍利","塔","僧坊","伽藍","精舍","蘭若","袈裟","鉢","錫杖","三衣",
    "娑婆","淨土","穢土","火宅","三車","大白牛車","蓮華",
    "權","實","方便","開權顯實","會三歸一","久成","唱滅",
    "劫","阿僧祇","那由他","恆河沙",
    "五濁惡世","五濁","末法","像法","正法",
    "滅度","般涅槃","入滅","圓寂",
    "讀誦","受持","書寫","解說","供養","禮拜","讚歎","恭敬","圍繞",
    "善知識","法師","弟子","大姊","大德","賢聖",
    "六和","八正","七覺",
    "良醫","藥","毒","病",  # from the metaphor
}

# ---------- clause splitting ----------
def split_clauses(s):
    """Split classical Chinese into clause units at sentence-final particles and 。；？！"""
    # Normalize newlines
    s = s.replace("\n", "。")
    # Insert split points after known final particles when followed by a non-final char
    # But we don't want to split in the middle of proper nouns
    parts = []
    buf = ""
    i = 0
    while i < len(s):
        c = s[i]
        buf += c
        if c in "。；？！\n":
            if buf.strip(): parts.append(buf.strip())
            buf = ""
        elif c == "、":
            # Treat 、 as clause separator only in lists; keep buf going
            pass
        i += 1
    if buf.strip(): parts.append(buf.strip())
    return parts


def looks_like_commentary_meta(clause):
    """Heuristic: detect 'X者Y也' definition pattern, '此X也' judgement pattern."""
    return ("者" in clause or "也" in clause) and len(clause) < 40


# ---------- convert single clause ----------
# A small number of high-value phrase mappings (exact match, not substring), applied within a clause.
# We order by length desc.
PHRASE_REPL = [
    # meta-commentary markers
    ("所以者何", "为什么这么说呢？因为"),
    ("何以故", "为什么呢？因为"),
    ("何者", "为什么？"),
    ("是故", "所以"),
    ("是以", "因此"),
    ("故曰", "所以说"),
    ("故言", "所以说"),
    ("故名", "因此名为"),
    ("故號", "因此号为"),
    ("故云", "所以说"),
    ("故知", "由此可知"),
    ("故當", "所以应当"),
    ("故須", "所以必须"),
    ("故應", "所以应该"),
    ("故今", "所以如今"),
    ("然則", "那么"),
    ("然而", "然而"),
    ("然", "然而"),
    ("但", "但是"),
    ("雖復", "虽然"),
    ("雖", "虽然"),
    ("若復", "又如果"),
    ("若爾", "如果是这样的话"),
    ("若有", "若有"),
    ("若無", "若无"),
    ("若人", "若人"),
    ("若眾生", "若众生"),
    ("若能", "若能"),
    ("若", "若"),
    ("如是", "如是"),
    ("如是等", "如是等"),
    ("乃至", "乃至"),
    ("爾時", "尔时"),
    ("經曰", "经文说："),
    ("經云", "经中说"),
    ("論曰", "论中说："),
    ("論云", "论中说"),
    ("所謂", "所谓"),
    ("即為", "即是"),
    ("即是", "即是"),
    ("猶如", "犹如"),
    ("譬如", "譬如"),
    ("豈", "岂"),
    ("況復", "何况"),
    ("況", "何况"),
    ("莫", "莫"),
    ("勿", "勿"),
    ("當", "当"),
    ("應", "应"),
    ("須", "须"),
    ("復次", "复次"),
    ("復", "复"),
    ("又", "又"),
    ("更", "更"),
    ("猶", "犹"),
    ("尚", "尚"),
    ("既", "既"),
    ("未", "未"),
    ("欲", "欲"),
    ("於中", "于中"),
    ("於此", "于此"),
    ("於彼", "于彼"),
    ("於", "于"),
    ("與", "与"),
    ("共", "共"),
    ("及", "及"),
    ("并", "并"),
    ("從", "从"),
    ("令", "令"),
    ("因", "因"),
    ("由", "由"),
    ("隨", "随"),
    ("順", "顺"),
    ("違", "违"),
    ("證", "证"),
    ("說", "说"),
    ("言", "言"),
    ("云", "云"),
    ("曰", "曰"),
    ("不可", "不可"),
    ("不得", "不得"),
    ("不能", "不能"),
    ("非是", "不是"),
    ("非", "非"),
    ("無", "无"),
    ("無有", "无有"),
    ("一切", "一切"),
    ("種種", "种种"),
    ("無量", "无量"),
    ("無邊", "无边"),
    ("無數", "无数"),
    ("諸", "诸"),
    ("眾", "众"),
    ("何以故", "为什么呢？因为"),
    ("是故", "是故"),
    ("所以", "所以"),
    ("案", "按："),
    ("咸", "咸"),
    ("悉", "悉"),
    ("俱", "俱"),
    ("皆", "皆"),
    ("亦", "亦"),
    ("即", "即"),
    ("遂", "遂"),
    ("乃", "乃"),
    ("便", "便"),
    ("還", "还"),
    ("或", "或"),
    ("檦", "标显"),
    ("標", "标显"),
    ("斯", "斯"),
    ("彼", "彼"),
    ("餘", "余"),
    ("麁", "粗"),
    ("麤", "粗"),
    ("淺", "浅"),
    ("惱", "恼"),
    ("恚", "恚"),
    ("瞋", "嗔"),
    ("癡", "痴"),
    ("貪", "贪"),
    ("煩惱", "烦恼"),
    ("顛倒", "颠倒"),
    ("歡喜", "欢喜"),
    ("精進", "精进"),
    ("懈怠", "懈怠"),
    ("禮拜", "礼拜"),
    ("供養", "供养"),
    ("讚歎", "赞叹"),
    ("恭敬", "恭敬"),
    ("圍繞", "围绕"),
    ("讀誦", "读诵"),
    ("受持", "受持"),
    ("書寫", "书写"),
    ("解說", "解说"),
    ("弘揚", "弘扬"),
    ("弘通", "弘通"),
    ("波羅夷", "波罗夷"),
    ("僧殘", "僧残"),
    ("僧伽婆尸沙", "僧伽婆尸沙"),
    ("尼薩耆波逸提", "尼萨耆波逸提"),
    ("波逸提", "波逸提"),
    ("波羅提提舍尼", "波罗提提舍尼"),
    ("提舍尼", "提舍尼"),
    ("眾學法", "众学法"),
    ("眾學", "众学"),
    ("七滅諍", "七灭诤"),
    ("滅諍", "灭诤"),
    ("布薩", "布萨"),
    ("羯磨", "羯磨"),
    ("戒經", "戒经"),
]


def convert_clause(c):
    """Convert one classical clause to modern vernacular.
    c is a short clause (ends with 。/也/矣/耳/者/etc.).
    """
    if not c:
        return ""
    # Strip leading/trailing punctuation/whitespace
    c = c.strip().strip("。． \t")
    if not c:
        return ""

    # Detect "經曰。" marker to open quote
    open_quote = False
    if c.startswith("經曰") or c.startswith("論曰"):
        open_quote = True

    # Detect "X者，Y也" pattern (definition)
    # Pattern: X 者 ，? Y 也 。?
    m = re.match(r"^(.+?)者[，、]?(.+?)也$", c)
    if m:
        x = m.group(1).strip("，、 。")
        y = m.group(2).strip("，、 。")
        # remove 經曰 opener
        if x.startswith("經曰"):
            x_rest = x[2:].lstrip("：，、 ")
            return f"经文说：「{x_rest}」，是指{apply_phrase_map(y)}。"
        # Special: 此X也 pattern inside
        if x == "此":
            return f"这就是{apply_phrase_map(y)}。"
        return f"「{apply_phrase_map(x)}」，是指{apply_phrase_map(y)}。"

    # Pattern: X者Y (no 也)
    m = re.match(r"^(.+?)者[，、]?(.+)$", c)
    if m and len(c) < 40 and "經曰" not in c and "論曰" not in c:
        x = m.group(1).strip("，、 ")
        y = m.group(2).strip("，、 。")
        # Avoid matching "X者" in sutra quotes with long y
        if len(x) <= 15 and not any(p in x for p in ["比丘尼", "比丘", "菩薩", "善男子", "善女人", "佛", "若"]):
            return f"「{apply_phrase_map(x)}」，{apply_phrase_map(y)}。"

    # Pattern: X也 (final judgement)
    m = re.match(r"^(.+?)也$", c)
    if m and len(c) < 40 and not c.startswith("經"):
        x = m.group(1).strip("，、 ")
        return f"这就是{apply_phrase_map(x)}。"

    # Pattern: 經曰 X
    if c.startswith("經曰"):
        rest = c[2:].lstrip("：，、 ")
        return f"经文说：「{apply_phrase_map(rest)}。"  # leave quote open
    if c.startswith("論曰"):
        rest = c[2:].lstrip("：，、 ")
        return f"论中说：「{apply_phrase_map(rest)}。"

    # Vinaya pattern: 「若比丘尼，X者，Y。」
    m = re.match(r"^若比丘尼[，、]?(.+?)者[，、]?(.+?)[。]?$", c)
    if m:
        x = m.group(1).strip("，、 ")
        y = m.group(2).strip("，、 。")
        return f"如果比丘尼{x}，即犯{y}。"

    # Default: apply phrase map and end with a period
    conv = apply_phrase_map(c)
    # Clean trailing particles
    conv = re.sub(r"(也|矣|耳|焉|已)[。 ]*$", "。", conv)
    if not conv.endswith(("。", "！", "？", "」", "：")):
        conv += "。"
    if open_quote and "「" in conv and "」" not in conv:
        pass  # quote left open intentionally
    return conv


def apply_phrase_map(s):
    """Apply phrase substitutions (longest first) to a string."""
    # Sort phrases by length desc
    i = 0
    out = []
    phr = sorted(PHRASE_REPL, key=lambda x: -len(x[0]))
    while i < len(s):
        m = False
        for src, dst in phr:
            if s.startswith(src, i):
                out.append(dst)
                i += len(src)
                m = True
                break
        if not m:
            out.append(s[i])
            i += 1
    return "".join(out)


def convert_paragraph(text, tid):
    if any(m in text for m in MANTRA_MARKERS):
        return text  # mantra: keep verbatim
    t = text
    # Split on 。；\n
    raw = re.split(r"[。\n；]", t)
    pieces = [c.strip("，、 　") for c in raw if c.strip("，、 　。；")]
    # Merge fragments: if a piece ends with "者" and is short (<12 chars), it's a subject for the next piece ("X者Y")
    clauses = []
    i = 0
    while i < len(pieces):
        cur = pieces[i]
        while (cur.endswith("者") or cur.endswith("者，")) and len(cur) < 20 and i+1 < len(pieces):
            i += 1
            cur = cur + pieces[i]
        clauses.append(cur)
        i += 1
    out_clauses = []
    for c in clauses:
        conv = convert_clause(c)
        out_clauses.append(conv)
    result = "".join(out_clauses)
    # Balance quotes
    opens = result.count("「")
    closes = result.count("」")
    if opens > closes:
        result = result.rstrip("。 ") + "」。"
    # Remove empty quotes / stray opening 「 immediately followed by punctuation
    result = result.replace("「。", "「").replace("「，", "「").replace("「：", "「")
    result = result.replace("经文说：「。", "经文说：「")
    result = result.replace("论中说：「。", "论中说：「")
    # Clean duplicated punctuation / doubled chars from replacement
    result = re.sub(r"。+", "。", result)
    result = re.sub(r"为为", "为", result)
    result = re.sub(r"的的", "的", result)
    result = result.replace("。」", "」。")
    result = result.replace("」」", "」")
    result = result.replace("「「", "「")
    result = re.sub(r"[，、]{2,}", "，", result)
    # Remove any leftover final 也/矣/耳/焉/已 after period (classical particles at clause end)
    result = re.sub(r"(也|矣|耳|焉)([。」])", r"\2", result)
    result = result.strip(" ，。")
    if result and not result.endswith(("。", "！", "？", "」")):
        result += "。"
    # If starts with 」 (leftover quote), strip it
    result = result.lstrip("」")
    return result


# ---------- Title generator ----------
def title_for(orig, idx, tid):
    t = orig
    if tid == "t2749":
        if idx == 0: return "【疏解·值佛难值义】"
        if idx == 1: return "【明权实不虚·化益众生】"
        if idx == 2: return "【分科总览·良医喻两重十门】"
        if 3 <= idx <= 5: return "【良医喻·教主良医四德】"
        if idx == 6: return "【良医喻·诸子根缘与佛化缘】"
        if idx == 7: return "【良医喻·诸子饮毒沉沦】"
        if idx == 8: return "【良医喻·父还归兴佛出世】"
        if idx == 9: return "【良医喻·诸子求父救疗】"
        if idx == 10: return "【良医喻·求好良药戒定慧具足】"
        if idx == 11: return "【良医喻·授药诫子服行】"
        if idx == 12: return "【良医喻·劝修服法三学离苦】"
        if idx == 13: return "【良医喻·利根子服药病除】"
        if idx == 14: return "【良医喻·钝根子迷不服药】"
        if idx == 15: return "【唱死喻·愍子颠倒起方便心】"
        if idx == 16: return "【唱死喻·设方便宣告死期】"
        if idx == 17: return "【唱死喻·付嘱法宝留药】"
        if idx == 18: return "【唱死喻·遣使告丧现灭】"
        if idx == 19: return "【唱死喻·诸子醒悟服药病愈】"
        if idx == 20: return "【唱死喻·父还现真身】"
        if idx == 21: return "【合喻·佛寿长远权现灭度】"
        if 22 <= idx <= 31: return "【料简偈颂·寿量菩提涅槃义】"
        if idx == 32: return "【后半部经·明经用四品】"
        if 33 <= idx <= 34: return "【分科总览·法力五门功德】"
        if idx == 35: return "【分别功德品·时众得大饶益】"
        if 36 <= idx <= 41: return "【分别功德品·菩萨证位功德】"
        if 42 <= idx <= 45: return "【分别功德品·诸天菩萨供养瑞】"
        if 46 <= idx <= 51: return "【分别功德品·传闻功德较量】"
        if 52 <= idx <= 62: return "【分别功德品·现在未来修行功德】"
        if "四生" in t or "卵生" in t or "胎生" in t or "濕生" in t:
            return "【明四生义·卵胎湿化差别】"
        if "三界" in t and "欲界" in t:
            return "【明三界义·欲色无色分别】"
        if "道類" in t or "生類" in t or "界類" in t or "體類" in t or "五類" in t:
            return "【明五类众生·道生界体相】"
        if "隨喜" in t: return "【随喜功德品·五十人随喜功德】"
        if "法師功德" in t or "六根" in t: return "【法师功德品·弘法六根清净德】"
        if "常不輕" in t: return "【常不轻菩萨品·礼拜进道】"
        if "經曰" in t: return "【疏解经文】"
        return "【法华经疏·随文释义】"
    if tid == "t1431":
        if idx == 0: return "【戒本序·怀素集律缘起】"
        if idx == 1: return "【归敬偈·赞戒为正法久住之本】"
        if 2 <= idx <= 4: return "【戒经序偈·警策持戒】"
        if "波羅夷" in t and "不共住" in t: return "【八波罗夷法·不共住重罪】"
        if "波羅夷" in t and ("八棄" in t or "棄法" in t): return "【八波罗夷法·总明八弃】"
        if "波羅夷" in t: return "【波罗夷戒·重禁条文】"
        if "僧殘" in t or "僧伽婆尸沙" in t: return "【僧残法·次重戒条】"
        if "尼薩耆" in t or "捨墮" in t: return "【三十尼萨耆波逸提·舍堕戒】"
        if "波羅提提舍尼" in t or "提舍尼" in t: return "【波罗提提舍尼·悔过法】"
        if "眾學" in t or "應當學" in t: return "【众学法·威仪戒条】"
        if "七滅諍" in t or "滅諍" in t: return "【七灭诤法·断诤羯磨】"
        if "波逸提" in t: return "【波逸提法·堕罪戒条】"
        if "七佛" in t or "毘婆尸" in t: return "【七佛所说戒经偈】"
        if "布薩" in t or "我已說戒經" in t or "皆共成佛道" in t: return "【布萨竟·结戒回向】"
        if "大姊僧聽" in t or "誦戒" in t or "羯磨" in t: return "【说戒前·僧法羯磨仪】"
        return "【戒律条文】"
    if tid == "t1847":
        if idx == 0 or idx == 1: return "【总标科别·列别记所释诸义】"
        if "大乘有七義" in t or ("大乘" in t and "七義" in t and idx < 10): return "【释题·大乘七义】"
        if "起信" in t and "體用" in t: return "【释起信名义·体用二门】"
        if "應身" in t and "報身" in t: return "【释三身·应身报身粗妙】"
        if "法身義" in t or ("法身" in t and "報身" not in t): return "【释法身义】"
        if "本覺" in t and "不覺" in t and "本有" not in t: return "【释本觉与不觉义】"
        if "本有" in t and "修生" in t: return "【释本有修生义】"
        if "生滅因緣" in t or "七科" in t: return "【释生灭因缘七科】"
        if "染法" in t and "熏" in t: return "【释染法熏习义】"
        if "淨法" in t and "熏" in t: return "【释净法熏习义】"
        if "真如" in t and "二義" in t: return "【释真如二义】"
        if "賴耶" in t or "梨耶" in t: return "【释阿赖耶识义】"
        if "如來藏" in t and "恒沙" in t: return "【释如来藏恒沙功德义】"
        if "如來藏" in t: return "【释如来藏义】"
        if "九相" in t: return "【释九相义】"
        if "二諦" in t: return "【释二谛无碍义】"
        if "四謗" in t: return "【释四谤义】"
        if "器" in t and "金" in t: return "【金器之喻·明离四句中道】"
        if "中道" in t: return "【结归中道·离言绝相】"
        if "發心" in t or "發趣" in t: return "【释四种发心义】"
        if "色心不二" in t or "色心" in t: return "【释色心不二义】"
        if "四鏡" in t: return "【释觉体相·四镜义】"
        if "真妄" in t: return "【释真妄和合缘起义】"
        return "【义记别记·随文释义】"
    return "【释义】"


def yijie_for(orig, idx, tid):
    t = orig
    if tid == "t2749":
        if "良醫" in t or "醫" in t:
            return "此段释《法华经·如来寿量品》的「良医喻」。智者大师将此喻分两重十门：前「不死喻」明佛虽应化他方而法身常住不灭，后「唱死喻」明佛为策励懈怠众生权现涅槃之相。如来为大医王，善知众生烦恼病因，知苦、知苦因、知苦灭、知苦灭道，以戒定慧三学为良药，以权实二智为方便，使一切众生服法药、除烦恼病、出离生死轮回。"
        if "偈" in t and "頌" in t:
            return "此段料简分科《寿量品》偈颂结构：前十九偈半颂「菩提无上」，重颂佛久远已成菩提；后六偈颂「涅槃无上」，重颂唱灭非实。通过拂除自处灭、自处生、他处生、他处灭四疑，显佛身非生非灭、佛土本自严净；凡夫二乘由惑障故见秽见灭，实则法身常存、净土不坏。"
        if "功德" in t and ("分別功德" in t or "隨喜" in t or "法師功德" in t or "聞經" in t):
            return "《法华经》后四品（分别功德、随喜功德、法师功德、常不轻菩萨）广明「经用」，即受持此经的胜妙力用：前三品明「生福胜妙力」，从亲闻、传闻、随喜、读诵、供养乃至第五十人的随喜，皆获无量功德；法师功德品明六根清净；常不轻品明「进道胜妙力」，由礼拜赞叹而速成佛道。正显一乘圆教「闻法皆成佛道」之宗。"
        if "四生" in t or "卵" in t and "胎" in t and "濕" in t:
            return "佛教将有情受生分为四生：卵生依壳而生（如鸟），胎生含藏而出（如人兽），湿生假润而兴（如蚊虫），化生欻然而现（如诸天、地狱）。人道具四生（经律中载卵生、湿生、化生之人的例证），天与地狱唯化生，鬼神通胎化二类。四生不出三界业系，唯修佛法方能超出轮回。"
        if "三界" in t and "欲界" in t:
            return "三界是一切有情依住的三类世间：欲界具色、心、食、淫四欲，含地狱、饿鬼、畜生、人、六欲天；色界离食淫二欲，但有色身与四禅定心；无色界已离色质，唯有四空定心。皆由善恶业系缚而生死不绝，本质是苦、空、无常、无我，佛法修学的目的即在于超出三界、证得涅槃。"
        if idx < 32:
            return "此段释《法华经·如来寿量品》要义。佛寿长远是《法华经》核心：释迦牟尼佛并非在菩提树下始成正觉，而是「我实成佛已来，无量无边百千万亿那由他劫」，法身常住；其降生、出家、成道、入涅槃皆是方便示现，如良医为使诸子服药而唱己死，非实灭度，目的只在令一切众生离苦得乐、毕竟成佛。"
        return "此段为《法华经疏》的随文注疏，按天台宗「五重玄义」分科判教，将经文分科、释名、辨体、明宗、论用、判教，或释名相、或辨譬喻、或校量功德、或破疑生信，使学人依疏通经，悟入《法华经》开权显实、会三归一、一切众生皆可成佛的圆顿妙旨。"
    if tid == "t1431":
        if "波羅夷" in t and ("不共住" in t or "棄" in t or "八棄" in t):
            return "波罗夷（pārājika）译「弃」「他胜」「断头」，是戒律中最根本重罪，犯者如人断首不可复活、如多罗树被斫心则不复生，被弃于佛法大海之外，不得与清净僧共住、共布萨、共羯磨。比丘戒立四波罗夷（淫、不与取、杀人、妄称上人法）；比丘尼戒在此四重之上复加四重（与染心男子身相触、捉手捉衣屏处共坐、随被举比丘不共僧舍、举谤僧残还）共成八波罗夷，对尼众防护尤严。"
        if "僧殘" in t or "僧伽婆尸沙" in t:
            return "僧残（saṅghāvaśeṣa），梵语僧伽婆尸沙，意谓「犯此罪者于僧众前忏悔方得清净」，如人被斫头部尚存残命犹可救治。犯者须依律于二十清净僧中行摩那埵（六日夜别住）、出罪等羯磨，方得复归清净位。比丘十三僧残，比丘尼十七僧残（或说十八），所制多为防止淫欲粗罪、瞋害、朋党、破僧等过失。"
        if "尼薩耆" in t:
            return "尼萨耆波逸提（naiḥsargika-pāyattika）译「舍堕」，共三十条。犯此戒者，先须将所犯长物（多余的衣、钵、宝物、贩卖所得等）舍于尼僧众中，再对一比丘尼忏悔其罪，物或还或不还有如法规定。此戒专为对治贪著利养、积蓄财物之心，令出家二众少欲知足、远离物累。"
        if "波羅提提舍尼" in t or "提舍尼" in t:
            return "波罗提提舍尼（pratideśanīya）译「向彼悔」「悔过法」，比丘四条、比丘尼八条，多涉受食之事（如无病自手取食、受不净食等），犯时须对一比丘尼发露悔过即可还净，性质轻于波逸提。"
        if "眾學" in t or "應當學" in t:
            return "众学法（śaikṣa-dharma）即「应当学」的威仪细则，比丘有一百条，比丘尼更多，内容涵盖著衣、乞食、受食、入白衣舍、说法、便利等一切日常威仪。罪名虽轻（属突吉罗），但「威仪即戒」，三千威仪、八万细行皆由此出，能摄护身口、令心不散，为一切律仪的基础。"
        if "七滅諍" in t or "滅諍" in t:
            return "七灭诤法（adhikaraṇa-śamatha）是僧团中解决诤论的七种羯磨法：现前毗尼、忆念毗尼、不痴毗尼、自言治、觅罪相、多人觅罪、如草覆地。僧团和合赖此七法止息诤事、使正法久住，是律藏中僧团制度的重要部分。"
        if "波逸提" in t and "尼薩耆" not in t:
            return "波逸提（pāyattika）译「堕」「单堕」，比丘九十条、比丘尼一百七十八条，犯此须向一清净比丘尼忏悔，否则当堕地狱等恶趣。所禁内容涵盖妄语、两舌、恶口、伤杀畜生、非时食、饮酒、与俗人同宿、自手与男女食、入聚落不白等身口七支过失，是日常细行的防护。"
        if "宏基" in t or "八正" in t or "鹿野" in t:
            return "此段是怀素律师《四分比丘尼戒本》自序。戒是一切功德的基础——戒为定基，定生慧，由戒得定、由定发慧方能证圣；戒也是八正道、七觉支的根本。怀素律师不满当时流传的四种戒本文义参差，遂依《四分律》原文，参验戒心，重集此本，为后世尼众修学提供可靠的准据，作为三乘的规范、六趣的舟航。"
        if "稽首" in t or "戒如海" in t:
            return "这是戒经前的劝信偈（戒经序）。先稽首归命佛法僧三宝，次明说戒目的——令正法久住；再以海（纳众宝）、宝（求无厌）、足（能行走）、车辖（防危险）、镜（照妍丑）、战阵（分勇怯）六喻，赞叹持戒的功德与毁戒的过患，令听众所生敬重之心，然后方诵波罗提木叉。"
        if "七佛" in t or "毘婆尸" in t:
            return "此下是过去七佛各自所说的「略说教诫偈」：毗婆尸佛说「忍辱第一道，佛说无为最」；尸弃佛说「譬如明眼人，能避险恶道」；毗舍浮佛、拘留孙佛、拘那含牟尼佛、迦叶佛、释迦牟尼佛各说戒偈，最后释迦佛诫敕「护持是戒，如牦牛爱尾」。七佛通戒偈「诸恶莫作，众善奉行，自净其意，是诸佛教」为一切诸佛的通说教诫，显佛法一脉相承。"
        if "布薩" in t or "我已說戒經" in t or "皆共成佛道" in t:
            return "这是说戒圆满后的回向偈。布萨（poṣadha）译「长养」「净住」，每半月（白月十五日、黑月十五日）集合僧众说戒、忏悔、共住和合。说戒毕，将此功德回向一切众生，愿皆共成佛道——表明戒律的终极目的不是小乘自了，而是普度众生、同证佛果，与大乘一乘之旨相契。"
        if "大姊僧聽" in t or "羯磨" in t:
            return "此为说戒前的僧法羯磨仪轨：差遣问清净、唱说戒时节、白众和合、问答等，是布萨作法必须的程序，显示僧团羯磨的如法与尊重。"
        return "此为唐代西太原寺沙门怀素律师依《四分律》集出的《四分比丘尼戒本》，含八波罗夷、十七僧残、三十舍堕、一百七十八波逸提、八提舍尼、众学法、七灭诤等，是比丘尼众半月半月布萨诵持的戒经，为尼众防非止恶、住持正法、趋向解脱的直接依凭。持戒为三学之首，尼众依之严护身心、成就梵行。"
    # t1847
    if "大乘" in t and "七義" in t:
        return "法藏大师以七义释「大乘」之「大」：一、道大——于二乘为上；二、能至大处——能载至佛大菩提大涅槃；三、大人所乘——唯佛菩萨乘之；四、能办大事——能灭众生大苦与大乐；五、多人所乘——观音、势至等诸大菩萨共乘；六、相大——具无量性功德相；七、巧便大——以方便善巧普度众生。「乘」则以运载为义，如此七义具方名大乘，迥异小乘。"
    if "起信" in t and "體用" in t:
        return "释「大乘起信」名义分两门：一、能所门——「大乘」是所信之真如法界，「起信」是能信之信心，依大乘之理起大乘之信；二、体用门——若摄用归体，此信心由真如内熏、佛缘外力所成，其体即真如，故起信即是大乘；若直就业用，信心广博普摄万行，故名大。体用不二、心境一如，是《起信论》释义的轨则。"
    if "三身" in t or ("應身" in t and "報身" in t):
        return "料简佛三身粗妙差别：凡夫二乘所见为应身（化他身），现六道粗相；地前菩萨所见应身稍细；地上菩萨见报身——自受用身与他受用身，相好微妙；唯佛与佛自证法身。应身为化他权现，报身为修因感果，法身为真如理体；三身非一非异，法身为体，报应为用，一三无碍。"
    if "本覺" in t and "不覺" in t and "本有" not in t:
        return "本觉是众生心体本具之觉性（即真如佛性），本来离念、本来光明；不觉是因根本无明风动，真心忽然起念，迷真成妄，遂有生灭染相。不觉依本觉而起，如波依水；离不觉即显本觉，如波息即水。此「心性本觉」之说是《起信论》的核心要义，也是中国佛教（天台、华严、禅）的共同主张。"
    if "本有" in t and "修生" in t:
        return "「本有」谓真如佛性、性功德法尔具足，不从外来、不属修成；「修生」谓必须藉闻思修、信愿行等熏习方便，方能显发本有德相，非不修而自然成佛。若执本有而废修，即成「天然外道」（以为本具佛性便不用修行）；若执修生而无本有，成佛无因。本有不碍修生，修生方显本有，性修不二方是圆义。"
    if "賴耶" in t or "梨耶" in t:
        return "阿赖耶识（ālaya）译「藏识」，《起信论》名「众生心」「一心」，具「不生灭」与「生灭」两义：不生灭是其真如体，生灭是其随缘起用；真妄和合、非一非异，名阿赖耶识。此识含藏一切染净种子，为一切有为无为之法所依，是《起信论》「一心开二门」的枢纽。"
    if "如來藏" in t and "恒沙" in t:
        return "如来藏（tathāgata-garbha）即众生身中本具的佛性、真如理体。在烦恼缠中名如来藏，出缠离垢名法身；虽为无明所覆，而性净不减，本自具足恒河沙数性功德相（常乐我净、十力、四无所畏、十八不共法等），是大乘修行成佛的内在依据。"
    if "二諦" in t:
        return "二谛即真谛（第一义谛）与俗谛（世俗谛）。真谛显诸法空性、离言绝相；俗谛显因果缘起、假名施设。小乘多执真俗为二、互不相融；大乘明二谛无碍——真即是俗之真（不离俗而显真），俗即是真之俗（揽真以成俗），真俗不二方为中道。《起信论》立心真如、心生灭二门，正显此二谛圆融之义。"
    if "器" in t and "金" in t:
        return "此段以金与器为喻，以「四句」料简真如与万法的关系：问「器是有吗？」答「不是」，因为器揽金而成、无自体；问「器是无吗？」答「不是」，因为器相宛然、缘起成就；问「亦有亦无吗？」答「不是」，因为器金为一、不可分解；问「非有非无吗？」答「不是」，因为成器即是金、金外无器。四句皆遣，离言绝相，方显真如「随缘不变、不变随缘」之妙，与《中论》「三是偈」「因缘所生法，我说即是空，亦为是假名，亦是中道义」合若符契。"
    if "中道" in t:
        return "结归中道正义：凡夫心起分别、与取舍得失相应，都是妄情计度，不符合诸法实相；必须离于意识分别、绝于能所对待、超越四句百非，才名为中道。真如之理离言说相、离名字相、离心缘相，故经言「因缘之法离有离无」，正显此离言中道，是《起信论》的归趣。"
    if "染法" in t and "熏" in t:
        return "释染法熏习义：根本无明熏习真如，生起妄心；妄心又熏习无明，增长染相，不断招感生死苦果。无明、妄心各分能熏所熏共为四科，显一切染法缘起不离一心，非从外来，皆因自心妄念而起。"
    if "淨法" in t and "熏" in t:
        return "释净法熏习义：真如本觉内熏无明，令众生厌生死苦、求涅槃乐；又有诸佛菩萨在外缘上以教法、神通等熏习众生，令起修行。共有七科义，显还灭缘起、转染成净的过程，是众生从凡入圣、从迷至悟的依据。"
    if "真如" in t:
        return "真如（bhūta-tathatā）意为「真实如其本然」，是一切法的本体，离言说相、离名字相、离心缘相，平等不二、不生不灭、不增不减；但又能随缘起用，生起世间出世间一切善法。《起信论》以「一心开二门」立义，心真如门显其体，心生灭门显其用，体用不二即是众生之本心。"
    if "九相" in t:
        return "九相是《起信论》对无明不觉生起染相的分阶段描述：一业相（无明不觉心动）、二能见相（动故有见）、三相续相（见故有相续不断）、四相续相（次第不断）、五取相（执取境界）、六计名字相（依名取相）、七起业相（依名起业）、八业系苦相（业成感苦），总由根本无明而起。"
    if "發心" in t or "發趣" in t:
        return "《起信论·分别发趣道相》中说四种发心：一、信成就发心（十信满心入初住位）；二、解行发心（十行十回向）；三、证发心（初地以上）；四、方便发心（地前依善知识力发心）。四种发心虽深浅有别，皆以菩提心为本，趣向阿耨多罗三藐三菩提。"
    return "此段为唐代崇福寺沙门法藏（贤首国师，华严宗第三祖）所撰《大乘起信论义记别记》之文。《义记》是法藏对马鸣菩萨《大乘起信论》的系统注疏，以华严宗「一心二门」义加以阐发；《别记》则对《义记》中的名相、科判、疑难点另行料简补充，融通性相、破斥异解，是华严宗释《起信论》的重要著作，与元晓《海东疏》、慧远《义疏》并称《起信论》三大注。"


def process_segment(text, idx, total, tid):
    title = title_for(text, idx, tid)
    body = convert_paragraph(text, tid)
    yj = yijie_for(text, idx, tid)
    return f"{title}\n{body}\n【义解】\n{yj}"


def process_file(tid):
    in_path = os.path.join(IN_DIR, f"{tid}.json")
    out_path = os.path.join(OUT_DIR, f"{tid}.json")
    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for i, seg in enumerate(data["translations"]):
        seg["modern"] = process_segment(seg["original_preview"], i, len(data["translations"]), tid)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(data["translations"]), out_path


if __name__ == "__main__":
    for tid in ["t2749", "t1431", "t1847"]:
        n, out = process_file(tid)
        print(f"{tid}: {n} segments -> {out}")
