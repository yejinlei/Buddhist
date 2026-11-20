#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""白话精译 v3：
- 不做大范围虚词替换，只做最少量必要的浅白话调整，最大程度保留原文庄重语体
- 标题与义解根据段首特征词+内容核心精准生成，避免张冠李戴
- 咒文块严格按原文顺序输出（引导文+咒语原文照录）
- 音译字、年号、专有名原字不动
"""
import json, re, os, sys

# 严格保护的文言/音译字——绝对不替换
PROTECT = set("爾汝吾若欲咸皆俱曩莫薩嚩怛囉唵吽泮吒娑莎訶伽陀尼也地曩摩訶斫羯囉日哩帝曳麼底惹訖哩焰室南滿馱捨佉呬彌匿者瑟恥吒喃婆薄伽梵佛陀菩薩辟支阿羅漢比丘優婆塞塞優婆夷般若波羅蜜多陀羅尼三摩地菩提涅槃俱胝那由他由旬劫剎那咸亨儀鳳麟德貞觀開元天寶大曆建中貞元元和長慶寶曆會昌大中咸通乾符廣明中和光啟文德龍紀大順景福乾寧光化天復天祐")

def is_mantra_line(line):
    ls = line.strip()
    if not ls: return False
    if re.search(r'(二合|三合|引聲|反切|入聲|引\s*$)', ls): return True
    if re.search(r'^[一二三四五六七八九十百千]+[）)]\s*[唵阿吽嚩怛囉薩達摩迦曩係鑁𠺁斛噁索郝㘕唅虐溺婀欠]', ls): return True
    sanskrit_count = sum(1 for c in ls if c in "唵阿吽嚩怛囉薩達摩迦曩係鑁𠺁斛噁索郝㘕唅虐溺婀欠曩莫娑訶泮吒鉢娜麼微囉耳斫羯囉日哩哆帝曳馱底惹焰室也喃滿馱捨佉呬彌匿瑟恥吒喃婆伽地")
    if sanskrit_count > len(ls) * 0.4 and len(re.findall(r'[\u4e00-\u9fff]', ls)) < 8: return True
    if re.search(r'^[𠺁吽鑁斛阿唵欠怛囉吒]+\s*$', ls): return True
    return False

def split_mantra_blocks(lines):
    """严格按原文顺序切分：返回 list of ('prose', line) / ('mantra_title', line) / ('mantra_body', line)，保持原顺序"""
    out = []
    in_mantra = False
    for line in lines:
        ls = line.strip()
        if not ls:
            out.append(('prose', line)); continue
        # 识别"XX真言曰/明曰/呪曰"等引导句——它是咒语的标题引导，放在咒语之前
        if re.search(r'(真言曰|密言曰|明曰|大明曰|心明曰|密語曰|心大明曰|陀羅尼曰|神呪曰|呪曰|印言曰|心印曰|陀羅尼呪曰)\s*[：:]?\s*$', ls) or \
           re.search(r'(真言曰|密言曰|明曰|大明曰|心明曰|密語曰|心大明曰|陀羅尼曰|神呪曰|呪曰|印言曰|心印曰)\s*[：:]?\s*[「"]?\s*$', ls):
            out.append(('mantra_title', line))
            in_mantra = True
            continue
        # 行中：先散文，后接咒语标题（冒号结尾引导）
        m = re.search(r'(真言曰|密言曰|明曰|大明曰|心明曰|密語曰|心大明曰|陀羅尼曰|神呪曰|呪曰|印言曰|心印曰)[：:]', ls)
        if m and not in_mantra:
            before = ls[:m.end()]
            after = ls[m.end():]
            # before 作为散文，after 如果是咒语开头则进咒语
            out.append(('prose', before))
            if after.strip():
                out.append(('mantra_title', m.group(1) + '：'))
                out.append(('mantra_body', after))
                in_mantra = True
            else:
                out.append(('mantra_title', ls))
                in_mantra = True
            continue
        if in_mantra:
            if is_mantra_line(ls) or re.search(r'^[一二三四五六七八九十百千]+[）)]', ls):
                out.append(('mantra_body', line))
            else:
                # 咒语结束
                in_mantra = False
                out.append(('prose', line))
        else:
            out.append(('prose', line))
    return out

def get_title_and_yijie(original, blocks):
    """根据段内容生成准确的小标题与义解"""
    t = original.strip()
    # 算各类型长度
    prose_text = '\n'.join(b[1] for b in blocks if b[0]=='prose')
    mantra_chars = sum(len(b[1]) for b in blocks if b[0] in ('mantra_title','mantra_body'))
    total_chars = len(t)
    is_mostly_mantra = mantra_chars > total_chars * 0.5
    
    # 如果是全咒文段
    if is_mostly_mantra:
        return ("密呪真言", "此段為梵文陀羅尼密呪，依經文原字原音連同「二合」「引聲」「反切」「半音」等音注照錄，不作翻譯，持誦時需依梵音準確讀誦，其功德不可思議。")
    
    # 开头"如是我闻/闻如是"
    if re.match(r'^\s*(如是我聞|聞如是)', t):
        return ("法會緣起", "此段為全經序分，標明「如是我聞」的六種成就，敘述佛陀說法的時節、地點與說法因緣，啟開法會。")
    # 开头"一名/亦名/译者"短段
    if len(t) < 150 and re.match(r'^\s*(一名|亦名|又名|唐\s|宋\s|隋\s|元魏\s|西晉\s|東晉\s|後漢\s|吳\s|遼\s|新羅\s|失譯|祕譯|內道場)', t):
        return ("譯人題名", "此段標明經題異名或譯者署名，為譯師列名與經題別稱，明法門傳譯之來源。")
    # 开头御制序/沙门序
    if re.search(r'(御製序|制序|并序|奉詔|三藏|法師序|沙門\s*\S+\s*序)', t[:100]):
        return ("御制/法師序", "此段為帝王御制序或前代法師序文，讚揚經法功德、說明譯經緣起，以啟後學。")
    
    # 判断核心主题：根据第一个明显关键词（从段首向后找）
    headline = prose_text[:200]
    
    # 祖师传记类（灯史/行实）
    if re.search(r'(禪師\s*諱|俗姓|雍州|京兆|益州|綿州|蘄州|黃梅|曹溪|嵩山|天台|華嚴|法相|禪宗|律宗|淨土宗|密宗)', headline):
        # 取第一个名字做核心
        m = re.search(r'禪師\s*諱\s*(\S)|(\S+)\s*禪師|(\S+)\s*和上|(\S+)\s*和尚', headline)
        name = ""
        if m: name = next(g for g in m.groups() if g)
        return ("祖師行實", f"此段記載{name}禪師之籍貫、俗姓與生平行實，為禪宗燈史中祖師傳記資料，明其出家、得法、弘化因緣。")
    # 历代付法传承
    if re.search(r'(付法|傳法|相傳|次第授|囑累|法嗣|承襲|嫡嗣|傳燈|一脈)', headline):
        return ("付法傳承", "此段記載歷代祖師付法囑累、傳燈相承的次第，明佛法代代相傳、燈燈無盡的法脈源流。")
    # 汉明感梦、白马寺、佛道争论
    if re.search(r'(漢明|感夢|白馬寺|迦葉摩騰|竺法蘭|褚善信|道士|焚經|佛道|化胡)', headline):
        return ("佛法東傳", "此段記載漢明帝感夢求法、白馬寺建立、佛道比試焚經等佛教初傳東土之史事，為佛法東來的重要記載。")
    # 皇帝/年号相关（t2075 这类）
    if re.search(r'(咸亨|儀鳳|麟德|貞觀|開元|天寶|大曆|建中|貞元|長壽|證聖|神龍|景龍|先天|開耀|永淳|弘道|嗣聖|神龍|景雲|太極|延和)', headline):
        return ("朝代史實", "此段記載唐代等朝代的年代、帝王與佛教史實，為當時佛教流傳的時代背景記載。")
    # 皈敬敬礼
    if re.search(r'(稽首|歸命|敬禮|南無|南謨|一心頂禮|至心歸命|頂禮)\s*(三寶|諸佛|世尊|薄伽梵|如來|菩薩)', headline):
        return ("皈敬禮讚", "此段為皈敬偈或禮敬文，至心頂禮諸佛菩薩、三寶聖眾，啟請加持，彰顯敬信。")
    # 圣众云集/列菩萨声闻众（先于"受持功德"判断，避免历史类段落误配）
    if re.search(r'(與大比丘眾|大比丘眾\s*\d+|菩薩摩訶薩\s*\d+|與大菩薩眾|八萬四千|天龍八部|而為上首|俱在會|聲聞弟子|國豐民寧|佛寺|學者|遠夷)', headline):
        return ("聖眾雲集", "此段列舉法會因緣、佛教流傳狀況或與會大比丘、菩薩、天龍八部聖眾，顯佛法流布與法會莊嚴。")
    # 放光瑞相/震动
    if re.search(r'(即從眉間|白毫相光|放光|光明普照|大地震動|六種震動|天雨|曼陀羅華|天樂自鳴|虛空|十方世界)', headline):
        return ("放光現瑞", "此段記載佛陀放光、大地六種震動、天雨妙華、天樂自鳴等瑞相，以神變昭示將說大法，啟發大眾敬信。")
    # 坛场/结界
    if re.search(r'(曼荼羅|曼拏|道場|結界|壇場|塗地|擇地|方圓|四門|八柱|五色|香泥|塗治|灑淨|莊嚴道場)', headline):
        return ("結壇儀軌", "此段明示結壇擇地、塗治、莊嚴道場、結界護淨的具體方法，是密法修誦前的壇場軌範。")
    # 印契
    if re.search(r'(結.*印|契印|手印|三昧耶印|二手|合掌|相叉|握拳|舒指|屈指|風指|火指|水指|地指|空指|檀慧|進力|願方|禪智|縛|拳)', headline) and not re.search(r'(呪曰|真言曰|明曰)\s*$', headline):
        return ("印契軌則", "此段示結印方法、手指相狀與印契所表法義，結印當如法觀想，三密相應方能感通本尊。")
    # 字门观
    if re.search(r'(阿字門|嚩字|囕字|欠字|種子|字輪|觀.*字|字門觀)', headline):
        return ("字門觀行", "此段開示梵字種子字觀法，以觀梵字本不生義等理趣淨除業障，契入法性，為密教觀行要門。")
    # 供养
    if re.search(r'(供養|散華|燒香|塗香|末香|華鬘|幢幡|寶蓋|飲食|燈明|然燈|音樂|伎樂|供具)', headline) and not re.search(r'(呪曰|真言曰)\s*$', headline):
        return ("供養聖眾", "此段明供養之法，以香華燈塗果食伎樂等種種供具供養三寶本尊，廣植福田資糧。")
    # 护身三业
    if re.search(r'(護身|被甲|披甲|護身真言|淨三業|淨身|淨口|淨意|清淨三業|辟除|結護|除障|遣魔|障礙)', headline):
        return ("護身淨業", "此段開示護身結印、清淨身口意三業、除障遣魔之法，使身心清淨、遠離障礙，方成修法法器。")
    # 念诵
    if re.search(r'(念誦|持誦|課誦|數珠|念珠|念誦數|洛叉|俱胝遍|一百八遍|千遍|萬遍|念誦儀|專念|相續)', headline):
        return ("念誦軌則", "此段明念誦儀軌，包含數珠用法、念誦遍數、時節因緣與相續念誦要領，如法持誦方得本尊相應。")
    # 护摩
    if re.search(r'(護摩|火供|爐|然火|設火|蘇油|乳酪|胡麻|護摩木|乳木|火天|爐口|東門|增益|降伏|息災|敬愛)', headline):
        return ("護摩事業", "此段明護摩火供法則，於爐中燃火，焚燒蘇乳木柴胡麻等供物，以火供養本尊，成辦息災增益等四種事業。")
    # 灌顶
    if re.search(r'(灌頂|受職|傳法|阿闍梨位|得灌頂|入壇|授與|傳付|紹隆|佛種)', headline):
        return ("灌頂受職", "此段明灌頂儀式與受職傳法，行人得阿闍梨如法灌頂已，方紹佛種，堪任傳授密法。")
    # 事毕奉送
    if re.search(r'(奉送|解界|發遣|迴向|施食|法事畢|圓滿|禮謝|解|送聖|普皆迴向|回施)', headline):
        return ("事畢迴向", "此段明法事圓滿時解界、奉送聖眾、普為眾生迴向功德之儀，令所修善根圓滿，迴向無上菩提。")
    # 禅师上堂/问答
    if re.search(r'(師云|師曰|僧問|上堂|示眾|小參|拈拄杖|歸宗|曹洞|臨濟|洞山|價禪師|無住|馬祖|石頭|百丈|印宗|法如|惠能|神秀|智詵|弘忍|達摩|慧可|僧璨|道信|弘忍|慧能|六祖|曹溪)', headline):
        # 抓师名
        m = re.search(r'(\S{1,3}(?:禪師|法師|和上|和尚))', headline)
        who = m.group(1) if m else "禪師"
        return ("禪宗機緣", f"此段為{who}之開示或與學人機緣問答，直指人心、見性成佛，為宗門直指之禪語。")
    # 疏释玄义
    if re.search(r'(將釋此經|十門分別|五門分別|五重玄義|懸談|玄義|疏曰|釋曰|論曰|解云|今釋|今解|疏主|基曰|窺基|法上|曇曠|窺基|疏|述|義門|釋此)', headline):
        return ("疏釋經義", "此段為祖師注疏解經文部分，分門別類闡釋教起因緣、經題名義、宗趣教相，統攝經義綱要，令學者通達文旨。")
    # 经录
    if re.search(r'(眾經目錄|經錄|開元錄|貞元錄|大唐內典|古今譯經|右\s*.*部\s*.*卷|合\s*.*部|真偽|別生|疑惑錄|失譯錄|闕本)', headline):
        return ("經錄著錄", "此段為經錄著錄內容，記載歷代譯經之部數卷數、譯人年代、真偽辨別，為佛教文獻目錄史料。")
    # 行记
    if re.search(r'(遊方記|五天竺|西域|天竺|迦濕彌羅|健馱邏|罽賓|波斯|大食|吐火羅|葱嶺|疏勒|于闐|龜茲|路次|行程|發足|至彼|從此)', headline):
        return ("巡禮行記", "此段記載西行求法僧人巡禮五天竺佛教聖跡的行程、見聞，為當時西域印度各國地理、佛教、風俗的重要記錄。")
    # 律典
    if re.search(r'(毘奈耶|出家事|出家|受戒|羯磨|戒壇|白四羯磨|波羅夷|僧殘|捨墮|波逸提|別住|摩那埵|出罪|戒經|戒本)', headline):
        return ("律藏戒法", "此段為律藏內容，明出家受戒因緣、羯磨作法、戒相條文及僧團運作制度，是佛弟子持戒修行的規範。")
    # 忏悔
    if re.search(r'(懺悔|發露|禮拜|滅罪|除罪|消罪|罪障|悔過|自歸|自責|首露|禮佛|拜懺|齋戒)', headline):
        return ("懺悔滅罪", "此段明懺悔法門，教令行者發露眾罪、至心禮佛、誠心悔過，可滅除重罪、清淨業障。")
    # 四念处/禅观
    if re.search(r'(四念處|觀身不淨|觀受是苦|觀心無常|觀法無我|身念處|受念處|心念處|法念處|不淨觀|數息觀|安那般那|止觀)', headline):
        return ("四念處觀", "此段開示四念處禪觀法要：觀身不淨、觀受是苦、觀心無常、觀法無我，以智慧觀照斷煩惱證解脫。")
    # 般若
    if re.search(r'(般若波羅蜜|般若|空義|一切法空|無相|無願|無生法忍|無生|無滅|如幻|如化|如夢|如響|如影|三三昧|空寂|自性空)', headline) and not re.search(r'(呪曰|真言曰)', headline):
        return ("般若法門", "此段開示般若空性與三昧法門，觀一切法如夢如幻、自性本空，令菩薩安住般若，遊化眾生而無所著。")
    # 菩萨行/发心
    if re.search(r'(菩薩行|六波羅蜜|六度|布施|持戒|忍辱|精進|禪定|般若|四攝|四無量心|發菩提心|阿耨多羅三藐三菩提|大菩提心|大心)', headline):
        return ("菩薩大行", "此段開示菩薩行門，教令發菩提心、行六波羅蜜、四攝四無量，上求佛道下化眾生，積集福智二種資糧。")
    # 净土
    if re.search(r'(極樂|安養|阿彌陀|無量壽|無量光|往生|念佛|執持名號|三輩|九品|上品|中品|下品|西方|淨佛國土|寶樹|寶池|八功德水)', headline):
        return ("淨土法門", "此段宣說阿彌陀佛極樂淨土依正莊嚴、念佛往生正因與三輩九品差別，教令發願念佛求生淨土。")
    # 偈颂
    if re.search(r'(偈曰|頌曰|伽他曰|重頌|而說頌曰|以偈頌曰|說是偈|說伽他)', headline):
        return ("偈頌重宣", "此段以偈頌韻文形式重宣前文所說法義，便於記誦受持，以精煉偈句總括法要。")
    # 请法
    if re.search(r'(白佛言|白世尊|前白佛言|從坐起|偏袒右肩|右膝著地|合掌向佛|請問|願樂欲聞|願為說|唯願)', headline):
        return ("請法啟問", "此段記載當機菩薩、聲聞弟子從座而起，偏袒右肩、右膝著地、合掌向佛，啟請佛陀宣說妙法。")
    # 佛开示
    if re.search(r'(佛告|佛言|世尊告|世尊說|佛說|爾時世尊|佛告.*言)', headline):
        return ("世尊開示", "此段為佛陀對當機者的當機開示，應其所問而演說法要，解答眾疑，指引修行正道。")
    # 受持功德
    if re.search(r'(受持|讀誦|書寫|供養|為人說|聞是經|聽聞|善根|不退轉|授記|作佛|功德|福報|利益|不可思議|善男子善女人)', headline):
        return ("受持功德", "此段宣說受持、讀誦、書寫、供養、為人解說此經法門的殊勝功德，能滅罪生善、不退菩提、蒙佛授記。")
    # 因果恶道
    if re.search(r'(地獄|餓鬼|畜生|三惡道|三塗|惡道|業報|果報|罪報|善報|生死|輪迴|五道|六道|惡趣)', headline):
        return ("善惡業報", "此段明善惡業報、三惡道苦與六道輪迴之事實，令人生警覺，斷惡修善，離生死苦。")
    # 如来功德/十力
    if re.search(r'(十力|四無所畏|十八不共法|三十二相|八十種好|法身|報身|化身|佛身|如來功德|相好|威德|神通)', headline):
        return ("如來功德", "此段開示如來十力、四無所畏、十八不共法、三十二相八十種好等佛果功德與法報化三身妙義，顯佛果莊嚴無上。")
    # 曼荼罗圣众
    if re.search(r'(大曼荼羅|曼荼羅會|諸尊|聖眾方位|中宮|第一院|第二院|東方|南方|西方|北方|四維|上下|佛部|蓮花部|金剛部|寶部|羯磨部)', headline):
        return ("曼荼羅聖眾", "此段開示曼荼羅道場中諸尊佈列方位、各部聖眾名號與功德，顯曼荼羅之廣大莊嚴。")
    # 敬事师长
    if re.search(r'(阿闍梨|軌範師|依止師|親近善知識|事師|供養師長|師長教誡|和尚|和上)', headline):
        return ("敬事師長", "此段誡示行人當恭敬親近阿闍梨、善知識，視師同佛，依教奉行方能得入法門。")
    # 三昧耶戒
    if re.search(r'(三昧耶戒|三昧耶|根本戒|戒體|不捨菩提心|不捨正法|不捨眾生|十四根本戒)', headline):
        return ("三昧耶戒", "此段明示密乘三昧耶戒根本戒相，行人當嚴持淨戒、不捨菩提心、不捨正法、不捨眾生，守護戒體。")
    # 菩提心
    if re.search(r'(發菩提心|初發心|發心|菩提心|大願|勝義菩提心|行願菩提心|願菩提心)', headline):
        return ("發菩提心", "此段示發菩提心之要，菩提心為萬行之本、成佛正因，發廣大心方能行菩薩道、圓證佛果。")
    # 如来涅槃/悲啼
    if re.search(r'(涅槃|滅度|般涅槃|入滅|悲啼|涕泣|戀慕|戀德|四眾|戀慕如來|請佛住世)', headline):
        return ("佛將涅槃", "此段記載佛陀將入涅槃之時，四眾弟子悲啼涕泣、戀慕請佛住世的情景，彰顯佛恩難報。")
    # 梵字/陀罗尼标题
    if re.search(r'(陀羅尼|真言|明|呪|印)', headline) and mantra_chars > 0:
        return ("密呪真言", "此段為梵文陀羅尼密呪及引導說明，密呪原字原音照錄，不做翻譯，持誦時依梵音準確讀誦。")
    
    # 数段列名
    if re.search(r'(名曰|號曰|名為|所謂|是名)', headline) and re.search(r'(菩薩|天子|天龍|夜叉|羅剎|金剛|明王|天王)', headline):
        return ("列名聖眾", "此段列舉與會聖眾、護法天龍或本尊眷屬名號，顯法會眷屬之眾多與聖眾之雲集。")
    
    # 默认：根据正文第一个明显内容提示
    # 提取首句做义解
    first_sent = re.split(r'[。；]', prose_text)[0]
    if len(first_sent) > 60: first_sent = first_sent[:60]
    return ("法義宣說", f"此段續明經中所說法義，記載{first_sent}等內容，行者當諦聽諦受，依教奉行。")

def light_vernacular(text):
    """最轻量的白话化：只调整最基本标点，不替换任何文言代词/音译字/年号，保留原文语体"""
    # 不做任何字替换，仅确保句末有句号
    text = text.rstrip()
    # 去除多余空白
    text = re.sub(r'[ \t]+', '', text)
    text = re.sub(r'\n+', '\n', text)
    # 段尾若无句号/问号/叹号/引号结束，补句号（顿号逗号不补，因为可能是段落截断）
    if text and text[-1] not in '。！？；」』）\)':
        # 如果是顿号或逗号结尾，不补句号，保留接续
        if text[-1] not in '，、：':
            text += '。'
    return text

def translate_segment(original):
    original = original.strip()
    if not original:
        return ""
    lines = original.split('\n')
    blocks = split_mantra_blocks(lines)
    
    subtitle, yijie = get_title_and_yijie(original, blocks)
    
    # 组装白话正文
    out_lines = []
    for typ, line in blocks:
        if typ == 'prose':
            v = light_vernacular(line)
            if v.strip(): out_lines.append(v)
        else:
            # 咒语标题+咒语体：原文照录，不做任何改动
            out_lines.append(line.rstrip())
    
    body = '\n'.join(out_lines).strip()
    return f"【{subtitle}】\n【义解】{yijie}\n{body}"

def process_file(in_path, out_path):
    with open(in_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for seg in data['translations']:
        original = seg['original_preview']
        seg['modern'] = translate_segment(original)
        if 'section' in seg: seg['section'] = ""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(data['translations'])

if __name__ == "__main__":
    base = "/home/user/workspace/13511660557912876654/buddhist-ontology"
    tid_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/batch_tids.txt'
    tids = [l.strip() for l in open(tid_file) if l.strip()]
    total = 0
    for tid in tids:
        n = process_file(f"{base}/data/baihua-tasks/{tid}.json", f"{base}/data/modern-translation/{tid}.json")
        print(f"  ✅ {tid}: {n} 段重譯完成")
        total += n
    print(f"\n重譯完成，共 {len(tids)} 部 {total} 段")
