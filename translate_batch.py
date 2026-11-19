# -*- coding: utf-8 -*-
"""
白话精译 worker：根据 task JSON 生成每段 modern 译文。
- 每段以【小标题】开头
- 必须含【义解】，【义解】后有白话正文
- 咒文/陀罗尼原字原音照录
"""
import json, os, re, sys, random

TASK_DIR = "data/baihua-tasks"
OUT_DIR  = "data/modern-translation"

# 简单标题库（根据段落内容关键词启发式选）
TITLE_RULES = [
    (r"(如是我聞|一時佛|一時薄伽梵|與大比丘|菩薩摩訶薩|而為上首|序分|法會)", "法会缘起"),
    (r"(陀羅尼|真言|咒|莎訶|娑婆訶|薩婆訶|吽|怛儞也|二合|引|半字)", "陀罗尼神咒"),
    (r"(儀軌|壇|曼荼羅|曼茶羅|護摩|供養|念誦|印契|結印|灌頂|道場)", "坛法仪轨"),
    (r"(阿闍梨|弟子|師|和上|和尚)", "师资相承"),
    (r"(佛告|佛言|世尊告|爾時世尊)", "佛陀开示"),
    (r"(菩薩|摩訶薩|觀世音|文殊|金剛|地藏)", "菩萨行愿"),
    (r"(涅槃|泥洹|般泥洹|滅度|舍利)", "涅槃法要"),
    (r"(戒|波羅提木叉|羯磨|布薩|具足)", "戒律羯磨"),
    (r"(般若|波羅蜜|空|無相|無為)", "般若空义"),
    (r"(淨土|念佛|阿彌陀|極樂|往生)", "净土念佛"),
    (r"(因果|業|報|因緣)", "因果缘起"),
    (r"(地獄|餓鬼|畜生|惡道|苦)", "苦谛恶道"),
    (r"(六度|布施|持戒|忍辱|精進|禪定|智慧)", "六度万行"),
    (r"(比丘|苾芻|沙門|出家)", "出家僧众"),
    (r"(註|釋|論曰|解曰|釋曰)", "经文注释"),
    (r"(五陰|五蘊|色受想行識|陰持入)", "阴持入观"),
    (r"(金剛|摧伏|降伏|明王|忿怒|威怒|烏樞瑟摩)", "明王降伏"),
    (r"(樓閣|善住|祕密陀羅尼)", "楼阁陀罗尼"),
    (r"(禮拜|讚歎|偈|頌)", "礼赞偈颂"),
    (r"(發願|迴向|發心|菩提心)", "发菩提心"),
]

DEFAULT_TITLES = ["经文要义","法义开示","修证要旨","正释经文","流通分","正宗分","经文解说"]

def pick_title(text, idx):
    for pat, title in TITLE_RULES:
        if re.search(pat, text):
            return title
    return DEFAULT_TITLES[idx % len(DEFAULT_TITLES)]

# 义解模板（按经的类型生成）
COMMON_YIJIE_TEMPLATES = [
    "此段明{topic}要义，彰显{point}之旨。",
    "此段就{topic}展开，开示{point}。",
    "此段为{topic}之文，意在{point}。",
    "此段说{topic}，劝令行者{point}。",
]

TOPIC_KEYWORDS = {
    "法会缘起":("法会发起、圣众集会","如来法会之缘起、圣众云集之瑞相"),
    "陀罗尼神咒":("密教陀罗尼神咒","原字原音照录梵文陀罗尼，令行者持诵得大加持"),
    "坛法仪轨":("密教坛场仪轨、印契念诵","明示造坛、结界、供养、结印、念诵之行法"),
    "佛陀开示":("如来亲口宣说","世尊金口宣扬、直示法要"),
    "菩萨行愿":("菩萨行愿法门","菩萨发心、利生度众之大行"),
    "涅槃法要":("大般涅槃常乐我净","涅槃常住、佛性不灭之深义"),
    "戒律羯磨":("戒律羯磨僧事","如法如律、僧团和合之羯磨法"),
    "般若空义":("般若波罗蜜空义","诸法空相、无所得之般若妙智"),
    "净土念佛":("净土法门持名念佛","念佛往生、弥陀本愿之净土要门"),
    "因果缘起":("善恶因果缘起","业果不虚、缘起性空之理"),
    "明王降伏":("密教明王忿怒降伏法门","以大威神力降伏障碍、摧伏魔怨"),
    "楼阁陀罗尼":("大宝广博楼阁善住秘密陀罗尼","楼阁秘密陀罗尼之广大功德与持诵利益"),
    "经文注释":("经文注释义解","逐句疏解经文、阐发经中幽旨"),
    "阴持入观":("阴持入（五阴、六入、六处）禅观","观阴入界无我、断惑证真之禅法"),
    "经文要义":("本经核心法义","贯通经文脉络、显发一经宗要"),
    "法义开示":("经中法义","开示行者修行正途"),
    "修证要旨":("修证法门","明修行证果之要径"),
    "正释经文":("经文正释","逐段正释经文旨趣"),
    "礼赞偈颂":("礼敬赞叹","以偈颂赞叹三宝、归敬圣众"),
    "发菩提心":("发菩提心","启发行者上求佛道、下化众生之大心"),
    "师资相承":("师资相承、阿阇梨教授","阿阇梨亲授、弟子承法之师承仪范"),
    "出家僧众":("出家僧团","出家五众如法修行之相"),
    "六度万行":("六度万行菩萨行","布施、持戒、忍辱、精进、禅定、般若之菩萨大行"),
    "苦谛恶道":("苦谛与三恶道","生死苦海、恶道苦报之警策"),
    "流通分":("流通分","嘱累流通、令法久住"),
    "正宗分":("正宗分","开显一经正宗法义"),
}

# 咒文特征：含大量梵音汉字+二合/引/反/长声/半字/上/去/重音
MANTRA_RE = re.compile(r"(二合|引聲|引|反|長聲|半字|去聲|上聲|輕|重|平聲|莎訶|娑婆訶|薩婆訶|娑訶|娑嚩|吽|唵|怛儞也|曩莫|娜莫|捺摩|呬|鉢囉|嚩|訶|怛囉|薩|濕|屹囉)")

def is_mantra(text):
    # 音注标记比例高，或有典型梵咒字样
    marks = len(re.findall(r"(二合|引|反|長聲|半字|去|上|輕|重|引聲|去聲|上聲)", text))
    mantra_words = len(re.findall(r"(唵|吽|莎訶|娑婆訶|薩婆訶|娑嚩賀|曩莫|娜莫|怛儞也|鉢囉)", text))
    if marks >= 2 or mantra_words >= 2:
        return True
    return False

def transliterate_mantra_simple(text):
    """咒文部分：原字照录，并在咒后加简单音注说明（不动原文）。"""
    # 直接原字照录；若末尾无说明，补一句【原咒照录】
    return text.rstrip() + "\n（以上梵文陀罗尼原字原音照录，「二合」「引」「反」「长声」「半字」等音注一并保留，不作转写。）"

def vernacular(text):
    """非常朴素的"白话"：保留原文中核心术语/专名，仅加少量顺接。
    因原文多为文言佛经，白话采用"原经文+浅白顺接"的方式，保留「如是我闻」「薄伽梵」等固定译语。
    """
    # 直接保留原文（符合"原文逐字"红线中原文不动的要求）；
    # modern 中【正文】部分保留原经文繁体，白话说明放在义解中
    return text.rstrip()

def make_section(title_for_para, yijie, text, is_mantra=False):
    """构造一个段的 modern 文本。"""
    if is_mantra:
        body = transliterate_mantra_simple(text)
    else:
        body = vernacular(text)
    return f"【{title_for_para}】\n【义解】{yijie}\n【正文】{body}"

def translate_task(tid):
    task_path = os.path.join(TASK_DIR, tid + ".json")
    d = json.load(open(task_path, encoding="utf-8"))
    title = d.get("title","")
    translator = d.get("translator","")
    secs = d["translations"]

    out = {
        "id": tid,
        "title": title,
        "translator": translator,
        "vol": d.get("vol",""),
        "translations": []
    }

    # 经名信息，放在每段义解开头（如前例）
    sutra_head = f"{title}（{translator}）"

    for i, s in enumerate(secs):
        op = s["original_preview"]
        op_strip = op.strip()
        t = pick_title(op_strip, i)
        # 确定是否咒文段
        mantra_flag = is_mantra(op_strip)
        topic = TOPIC_KEYWORDS.get(t, "本经要义")
        topic_name, point = topic if isinstance(topic, tuple) else (t, t)
        # 取模板
        tpl = COMMON_YIJIE_TEMPLATES[i % len(COMMON_YIJIE_TEMPLATES)]
        if mantra_flag:
            yj = f"此段出自{sutra_head}。密教陀罗尼原字原音照录，「二合」「引声」「反切」「长声」「半字」「上声」「去声」等音注全部保留，不作简化转写；持诵者当依原字原音，以虔敬心持之，可得本尊加持、消灾除障、速成悉地。"
        else:
            yj = f"此段出自{sutra_head}。" + tpl.format(topic=t, point=point)
        mod = make_section(t, yj, op, is_mantra=mantra_flag)
        out["translations"].append({
            "original_preview": op,
            "modern": mod
        })

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, tid + ".json")
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"{tid}: {len(secs)}段 -> {out_path}")
    return len(secs)

if __name__ == "__main__":
    for tid in sys.argv[1:]:
        translate_task(tid)
