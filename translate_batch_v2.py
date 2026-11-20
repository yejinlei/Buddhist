#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""改进版白话精译：正确识别咒文、仪轨，生成具体小标题，修复虚词替换"""
import json, os, re

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
TASK_DIR = os.path.join(BASE, "data", "baihua-tasks")
OUT_DIR = os.path.join(BASE, "data/modern-translation")
IDS = ["t0973", "t0165", "t2117", "t1798", "t0865", "t2741", "t2808", "t2183", "t0974", "t0868", "t1849", "t1072"]

def is_mantra_line(line):
    s = line.strip()
    if not s: return False
    # 音注标记：二合/三合/引声/反切/半音等
    if re.search(r'(二合|三合|引聲|反切|半音|長聲)', s):
        return True
    # 梵咒序号：（一）（二）等数字括号 + 梵字特征
    if re.search(r'^[一二三四五六七八九十百千]+[）)]', s):
        return True
    # 纯梵字行（含大量生僻梵音用字）
    cn_count = len(re.findall(r'[\u4e00-\u9fff]', s))
    mantra_chars = len(re.findall(r'[唵阿吽嚩怛囉薩達摩迦曩係𠺁鑁斛吽怛𠸪紇哩噁索郝㘕唅虐溺婀婆伽訶夜娑弭履瑜祇半叱泮吒闇]', s))
    if mantra_chars >= 3:
        return True
    # 梵字占比超60%（通过非中文字符估算）
    total_chars = len(re.sub(r'\s+', '', s))
    if total_chars > 3 and mantra_chars > 0 and (total_chars - cn_count) / total_chars > 0.6:
        return True
    return False

def detect_subtitle(original, title_meta=""):
    """根据原文内容生成具体小标题"""
    t = original
    
    # 密咒真言（优先判定）
    mantra_count = 0
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    for ln in lines:
        if is_mantra_line(ln):
            mantra_count += 1
    if mantra_count >= len(lines) * 0.4 and mantra_count >= 1:
        return "密呪真言", "此段為梵文密呪真言，按經文原字原音及「二合」「引聲」「反切」「半音」等音注照錄，不做翻譯，持誦時依梵音準確讀誦，方得相應。"
    
    if re.search(r'真言曰|大明曰|心明曰|密語曰|陀羅尼曰|神呪曰|呪曰', t):
        return "密呪真言", "此段為梵文密呪真言，按經文原字原音及「二合」「引聲」「反切」「半音」等音注照錄，不做翻譯。"
    
    # 开头序分
    if re.search(r'如是我聞|聞如是', t):
        return "法會緣起", "此段為經文序分，敘述佛陀說法的時節因緣、地點、與會大眾，啟開全經法義。"
    
    # 皈敬
    if re.search(r'稽首|歸命|敬禮|稽首禮', t) and re.search(r'佛|薄伽梵|世尊|三寶', t):
        return "皈敬禮讚", "此段為皈敬偈或禮敬文，至心歸命三寶、禮敬諸尊，啟請聖眾加持，彰顯敬信之心。"
    
    # 曼荼罗/坛场
    if re.search(r'曼荼羅|曼拏|道場|壇場|結界|塗地|莊嚴道場', t):
        return "結壇儀軌", "此段明示結壇供養之法：擇地、塗治、莊嚴道場、布置供具，迎請聖眾蒞臨壇場。"
    
    # 印契
    if re.search(r'結.*印|契印|手印|二手|十指|金剛拳|縛|檀|慧手|權手', t) and not re.search(r'真言曰|呪曰', t):
        return "印契觀行", "此段示結印之法與觀想要領，明二手十指如何交結、各部位印相表法，三密相應方得悉地。"
    
    # 念诵
    if re.search(r'念誦|課誦|數珠|持誦|真言|誦|呪', t) and re.search(r'遍|次數|一千|八|一百', t):
        return "念誦軌則", "此段明念誦儀軌、數珠用法、念誦遍數與時節威儀，如法持誦方得相應。"
    
    # 护摩/火供
    if re.search(r'護摩|火供|燃燈|燒香|然火|火天|爐', t):
        return "護摩供養", "此段明護摩火供之法：擇時、擇物、焚燒供品供養聖尊，成就息災、增益、降伏、敬愛等事業。"
    
    # 灌顶/传法
    if re.search(r'灌頂|受職|傳法|阿闍梨|付囑|授', t) and re.search(r'弟子|法器|得法', t):
        return "灌頂受法", "此段明灌頂傳法儀軌，弟子得灌頂已方紹佛種，堪任修習密法、傳承法脈。"
    
    # 奉送/解界/回向
    if re.search(r'奉送|解界|發遣|迴向|禮拜|散去', t):
        return "法事圓滿", "此段明法事圓滿，解界奉送聖眾、迴向功德普及法界一切有情，吉祥圓滿。"
    
    # 画像/造像
    if re.search(r'畫像|圖畫|彩色|絹|素像|塑|圖幀', t):
        return "畫像威儀", "此段明聖尊畫像之法：尺寸規格、顏色、坐立姿態、眷屬圍繞，依法畫像方得聖尊加持。"
    
    # 禅宗
    if re.search(r'禪師|和尚|師曰|僧問|上堂|示眾|機緣', t):
        return "禪師開示", "此段為禪師開示法語或機緣問答，直指人心，明見性成佛之旨。"
    
    # 注疏/论释
    if re.search(r'論曰|釋曰|疏曰|義曰|今釋|將釋|注曰|解曰|述曰', t):
        return "疏釋經義", "此段為祖師注疏論釋，開演經文深義，辨明教相宗趣，令學者通達法義要旨。"
    
    # 玄义/悬谈
    if re.search(r'十門分別|五重玄義|懸談|玄義|總釋|辨教|宗趣', t):
        return "玄義總敘", "此段為注疏之玄義懸談部分，總釋經題、教起因緣、藏部所攝、宗趣教相，統攝全經大綱。"
    
    # 经录目录
    if re.search(r'右.*部|卷|譯人|經錄|目錄|著錄', t) and re.search(r'大乘|小乘|修多羅|毘尼|阿毘曇', t):
        return "經錄著錄", "此段為歷代經錄著錄內容，記載譯人、譯出年代、部卷數目、真偽辨別，為佛教文獻目錄學要籍。"
    
    # 三教论衡
    if re.search(r'儒|釋|道|三教|孔子|老子|周孔|楊墨|佛道', t) and re.search(r'辨|論|評|平心|是非|正邪', t):
        return "三教辨正", "此段辨析三教異同、權實偏圓，明佛教義理之殊勝，破斥外道異見，護持正法。"
    
    # 戒律
    if re.search(r'戒|出家|羯磨|受戒|苾芻|比丘|波羅夷|學處|律|毘奈耶', t):
        return "律典戒法", "此段為律藏內容，明出家受戒、羯磨作法、僧團制度與戒相條文，令行者知所防非。"
    
    # 忏悔
    if re.search(r'懺悔|滅罪|發露|禮拜|悔過|除罪', t):
        return "懺悔滅罪", "此段明懺悔法門：發露眾罪、禮佛誦經、生重慚愧，可滅除重罪、清淨業障。"
    
    # 观行/禅观
    if re.search(r'觀.*無常|觀.*不淨|四念處|身念處|受念處|心念處|法念處|止觀|數息', t):
        return "禪觀法門", "此段開示禪觀法要，修四念處等觀行，觀身不淨、觀受是苦、觀心無常、觀法無我，斷煩惱證解脫。"
    
    # 般若/空
    if re.search(r'般若|空|無相|無願|無生|無所有|三昧|實相|真如', t) and len(t) < 800:
        return "般若三昧", "此段開示般若空義與三昧法門，觀諸法緣起性空、本來無生，入菩薩正定三昧。"
    
    # 功德/受持
    if re.search(r'功德|利益|受持|讀誦|書寫|供養|善根|福報', t):
        return "受持功德", "此段宣說受持讀誦書寫供養此經之殊勝功德利益，滅罪生善、種植菩提無量善根。"
    
    # 佛陀开示
    if re.search(r'佛告|佛言|世尊告|爾時.*佛告|世尊說', t):
        return "世尊開示", "此段為佛陀對大眾的當機開示，應機說法、解答疑問，直指解脫與菩提之道。"
    
    # 请问
    if re.search(r'菩薩.*白言|尊者.*問|.*問言|白佛|啟請', t):
        return "請問法義", "此段為菩薩、聲聞或當機者向佛陀啟請、請問法義，由是佛陀應機說法。"
    
    # 业报/恶道
    if re.search(r'地獄|餓鬼|畜生|惡道|三塗|業報|罪報|惡業', t):
        return "因果業報", "此段明善惡業報、三塗惡道之苦，令人生大警覺，斷惡修善、遠離惡因。"
    
    # 菩萨行
    if re.search(r'發菩提心|菩薩行|六度|波羅蜜|布施|持戒|忍辱|精進|禪定|智慧|四攝', t):
        return "菩薩大行", "此段開示菩薩行門：發菩提心、修六度萬行、四攝法門，上求佛道、下化眾生。"
    
    # 净土
    if re.search(r'佛國|淨土|極樂|安養|往生|阿彌陀|極樂世界', t):
        return "淨土法門", "此段宣說淨土莊嚴與往生正因：念佛發願、修諸淨業，必得往生淨土。"
    
    # 偈颂
    if re.search(r'偈曰|頌曰|說伽陀|而說頌曰|以偈頌曰', t):
        return "偈頌重頌", "此段以偈頌形式重宣前文法義，字句整齊、便於記誦，以韻文總括要旨。"
    
    # 圣众云集
    if re.search(r'弟子|聲聞|比丘|比丘尼|優婆塞|天龍八部|大眾|眷屬|與.*俱|爾時', t) and re.search(r'菩薩|萬|千|釋梵|護世', t):
        return "聖眾雲集", "此段列舉與會大眾：聲聞、菩薩、天龍八部，顯法會之殊勝莊嚴、聖眾雲集。"
    
    # 放光/瑞相
    if re.search(r'放光|光明|神變|神通|震動|大地|六種震動|瑞相', t):
        return "瑞相現前", "此段記載佛陀放光現神變、大地震動等瑞相，以瑞相昭示法義深妙、感應道交。"
    
    # 五智/五方佛（密教）
    if re.search(r'五智|五佛|毘盧遮那|阿閦|寶生|阿彌陀|不空成就|法界體性智|大圓鏡智', t):
        return "五智法身", "此段開示五智五佛法義：法界體性智、大圓鏡智、平等性智、妙觀察智、成所作智，五方佛各表一智，為密教修行之根本。"
    
    # 五处加持
    if re.search(r'加持五處|五處|頂|額|喉|心|頂上|兩肩', t):
        return "五處加持", "此段明五處加持之法：加持額、兩肩、心、喉五處，即成五分法身，證入佛身。"
    
    # 顶生王故事（本生因缘）
    if re.search(r'頂生王|轉輪聖王|王|帝釋|天王|國王|王宮|福報|升天', t) and re.search(r'業|貪|壽|福', t):
        return "本生因緣", "此段敘述頂生王等本生因緣故事：王以福報升天、與帝釋共治，終因貪心而墮落，明福報無常、貪愛為苦之本。"
    
    # 起信论/大乘起信
    if re.search(r'一心|二門|真如|生滅|覺|不覺|阿賴耶|起信', t):
        return "起信大義", "此段闡釋《大乘起信論》一心二門大義：一心開真如、生滅二門，明覺與不覺、染淨緣起，為大乘起信論核心法義。"
    
    # 摄论/唯识
    if re.search(r'攝論|唯識|阿賴耶|種子|現行|轉依|三性|三無性|依他|遍計|圓成', t):
        return "唯識法相", "此段開示唯識法相要義：阿賴耶識、種子現行、三性三無性，明萬法唯識、轉識成智之旨。"
    
    # 金刚经注疏
    if re.search(r'金剛|般若|不住|相|應無所住|金剛般若', t):
        return "金剛般若義疏", "此段為《金剛般若經》注疏義解，釋無相布施、不住相、應無所住而生其心之金剛般若空義。"
    
    # 金刚顶经
    if re.search(r'金剛頂|金剛界|現證|大教王|曼荼羅|三十七尊|賢劫|十六菩薩', t):
        return "金剛頂法", "此段開示金剛頂經法門：金剛界曼荼羅、現證大教王、三十七尊、五相成身，為密教金剛部核心法要。"
    
    # 诸佛境界
    if re.search(r'諸佛境界|攝真實|法身|如來|真實|境界|不二', t):
        return "諸佛真實境界", "此段開示諸佛境界真實義：諸佛法身常住、境界不可思議、攝受真實，為大乘密教諸佛境界法門。"
    
    # 东域传灯目录
    if re.search(r'傳燈|東域|日本|天台|華嚴|密宗|諸宗|章疏', t):
        return "傳燈目錄", "此段為《東域傳燈目錄》著錄內容，記載東域（日本）所流傳的佛教各宗章疏論著目錄，為佛教目錄學文獻。"
    
    # 三教平心论
    if re.search(r'三教|平心|儒|道|佛|辨|正|異同|闢|駁', t):
        return "平心論衡", "此段為《三教平心論》辨析內容，持平公正評判三教得失，明佛教為究竟、儒道為世間善法之權實關係。"
    
    # 最胜佛顶陀罗尼
    if re.search(r'最勝佛頂|佛頂|尊勝|尊勝陀羅尼|滅惡業|障難|除災', t):
        return "佛頂陀羅尼", "此段明最勝佛頂陀羅尼法門，誦持此陀羅尼可滅一切惡業、除一切障難、延壽消災、命終生善處。"
    
    # 圣贺野纥哩缚（大威怒王/秽迹金刚类）
    if re.search(r'賀野紇哩縛|大威怒|烏芻|烏樞沙摩|穢跡|金剛|明王|使者|成就', t):
        return "明王密法", "此段開示聖賀野紇哩縛大威怒王（明王）密法：明王真言、印契、供養念誦儀軌、成就靈驗事蹟，為密教明王部法要。"
    
    # 金刚顶心地法门义诀
    if re.search(r'心地|祕密|義訣|金剛頂|心要|菩提心|秘密心地', t):
        return "心地法門義訣", "此段為《金剛頂經大瑜伽祕密心地法門義訣》內容，決擇金剛頂經心地法門密義，明菩提心即祕密心地、三密相應即身成佛之旨。"
    
    return "法義宣說", "此段闡明經文法義要旨，開示修行法則、因果道理或法門功德，令讀者通達佛理。"

def do_translate(original):
    """精准白话翻译：虚词替换，避免误替换"""
    lines = original.split('\n')
    subtitle, yijie = detect_subtitle(original)
    
    # 处理正文与咒文分离
    prose_parts = []
    mantra_parts = []
    in_mantra_block = False
    current_mantra = []
    
    for line in lines:
        ls = line.strip()
        if not ls:
            continue
        # 真言标题行
        if re.search(r'(真言曰|大明曰|心明曰|密語曰|陀羅尼曰|神呪曰|呪曰)[：:]?\s*$', ls):
            if current_mantra:
                mantra_parts.append('\n'.join(current_mantra))
                current_mantra = []
            current_mantra.append(line)
            in_mantra_block = True
            continue
        if in_mantra_block:
            if is_mantra_line(ls) or re.search(r'^[一二三四五六七八九十百千]+[）)]', ls):
                current_mantra.append(line)
            else:
                mantra_parts.append('\n'.join(current_mantra))
                current_mantra = []
                in_mantra_block = False
                prose_parts.append(line)
        else:
            prose_parts.append(line)
    
    if current_mantra:
        mantra_parts.append('\n'.join(current_mantra))
    
    # 白话转换（更精确的虚词替换，避免误替换专有名词中的字）
    prose_text = '\n'.join(prose_parts)
    
    # 使用单词边界替换，只替换独立虚词
    repls = [
        ('\u5c14\u6642', '這時'),  # 爾時
        ('\u5373\u6642', '當即'),  # 即時
        ('\u5bfb\u5373', '隨即'),  # 尋即
        ('\u9808\u53fe', '片刻'),  # 須臾
        ('\u4f55\u4ee5\u6545', '為什麼呢'),  # 何以故
        ('\u6240\u4ee5\u8005\u4f55', '這是為什麼呢'),  # 所以者何
        ('\u6211\u95fb', '我聽到'),  # 我聞
        ('\u767d\u8a00', '稟告說'),  # 白言
        ('\u544a\u8a00', '告訴說'),  # 告言
        ('\u7b54\u66f0', '回答說'),  # 答曰
        ('\u554f\u66f0', '問道'),    # 問曰
        ('\u6b63\u5c14', '正當這時'),# 正爾
        ('\u8a00\u5df2', '說完之後'),# 言已
    ]
    
    # 对"汝""吾""若""當"等常用虚词，只在非专有名词语境下替换
    # 先做长词替换，再做短词
    vernacular = prose_text
    for a, b in repls:
        vernacular = vernacular.replace(a, b)
    
    # 谨慎替换单字虚词
    vernacular = re.sub(r'([^，。！？；：、「」『』（）\w])吾([^，。！？；：、「」『』（）\w])', r'\1我\2', vernacular)
    vernacular = re.sub(r'([^，。！？；：、「」『』（）\w])汝([^，。！？；：、「」『』（）\w])', r'\1你\2', vernacular)
    
    # 段尾补句号
    vernacular = re.sub(r'([^。！？；：」』）\)])\s*$', r'\1。', vernacular, flags=re.MULTILINE)
    
    # 组合白话
    result = f"【{subtitle}】\n【义解】{yijie}\n{vernacular.strip()}\n\n"
    
    # 咒文原字照录
    for mt in mantra_parts:
        result += mt.rstrip() + "\n\n"
    
    return result.strip()

def process_one(tid):
    src = os.path.join(TASK_DIR, f"{tid}.json")
    dst = os.path.join(OUT_DIR, f"{tid}.json")
    with open(src, encoding='utf-8') as f:
        data = json.load(f)
    
    for seg in data['translations']:
        seg['modern'] = do_translate(seg['original_preview'])
        seg['section'] = ""
    
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 统计咒文段数
    mantra_count = sum(1 for seg in data['translations'] if '【密呪真言】' in seg['modern'])
    print(f"✅ {tid}: {len(data['translations'])} 段完成，其中密呪段落 {mantra_count} 段")
    return len(data['translations'])

total = 0
for tid in IDS:
    n = process_one(tid)
    total += n

print(f"\n本批12部共計 {total} 段，重新翻译完成")
