import json, os, re
files = ['t1239.json','t0850.json','t2075.json','t1251.json','t0953.json','t0887.json','t2871.json','t0682.json','t0341.json','t1757.json','t2810.json','t1797.json']
total_segments = 0
problems = []
# 空泛义解模板列表
generic_yijie = [
    '此段為經文正文，繼續宣說佛法要義、修行法則與法門功德，行者當諦聽諦受依教奉行',
    '此段記載佛陀放光現瑞、大地震動等神變瑞相，預示將說殊勝大法，昭示法義深妙',
    '此段宣說受持、讀誦、書寫、供養、為他人解說此經法門的殊勝功德利益，能滅罪生善、植菩提種、不退菩提、蒙佛授記',
    '此段明供養之法，以香華燈塗果食等種種妙供具供養三寶本尊，廣植福田資糧',
    '此段明示結壇儀軌，擇地、塗治、莊嚴道場，安佈尊位結界護淨，迎請聖眾蒞臨壇場',
    '此段開示般若空性與三昧法門，觀一切法如夢如幻、本性空寂，令菩薩安住般若三昧，遊化眾生',
    '此段為梵文真言密呪，原字原音及「二合」「引聲」「反切」「半音」等音注悉依經文照錄，不做翻譯，持誦時依梵音準確讀誦',
    '此段示結印方法、印相所表法義及結印觀想要領，身印相應方能感通本尊，成辦事業',
    '此段明護摩火供之法，於護摩爐中焚燒供物供養本尊，以成辦息災、增益、降伏、敬愛等事業',
    '此段明善惡業報、三惡道苦、六道輪迴之事實，令人生警覺，斷惡修善，離生死苦',
    '此段為律藏內容，明出家受戒的因緣與儀式、羯磨作法、戒相條文及僧團制度軌範',
    '此段開示護身、淨三業、結界除障之法，清淨身心方成修行法器，遣除障礙',
    '此段列舉法會中與會的大比丘、菩薩摩訶薩及天龍八部聖眾，彰顯法會規模莊嚴，聖賢雲集',
    '此段記載禪師或譯經大德的籍貫、生平行實、參禮得法因緣及弘法事跡，為燈史傳記資料',
    '此段記載西行求法僧人巡禮五天竺佛教聖跡的所見所聞，記錄西域印度各國佛教狀況、地理風俗與路程，為中外交通史料',
    '此段為皈敬偈頌或禮敬文，至心頂禮諸佛菩薩三寶，啟請聖眾加持，彰顯敬信之心',
    '此段明灌頂儀軌，得阿闍梨如法灌頂已，方紹佛種堪任修習密法，獲得傳法資格',
    '此段記載禪師上堂開示或與學人機緣問答，直指人心，明見性成佛之禪宗要旨',
    '此段開示菩薩行門，教令發菩提心、行六波羅蜜、四攝四無量，上求佛道下化眾生，積集福智資糧',
    '此段明法事完畢解界、奉送聖眾、普皆迴向之儀，令所修功德圓滿，迴向菩提普及有情',
    '此段示發菩提心之要，菩提心為萬行之本、成佛正因，發廣大心方能行菩薩道',
    '此段誡示行人當恭敬親近阿闍梨、善知識，視同諸佛，依教奉行方能得入法門',
    '此段為經錄著錄內容，記載歷代譯經之部卷、譯人、譯出年代，辨別真偽，為佛教文獻目錄史料',
    '此段為祖師注疏解經文，分門別類闡釋經題、教起因緣、宗趣教相等法義，統攝經義綱要，令學者通達文旨',
    '此段開示曼荼羅道場中諸尊佈列、各部聖眾方位與功德，顯金剛界、胎藏界曼荼羅之廣大莊嚴',
]
# 错误替换对
wrong_pairs = [
    ('爾時', '這時'),
    ('汝等', '你們'), ('汝', '你'),
    ('吾等', '我們'), ('吾', '我'),
    ('欲', '想要'),
    ('名曰', '名叫'), ('號曰', '名叫'),
    ('豈', '難道'),
    ('云何', '為什麼'),
    ('名為', '稱為'),
    ('歎曰', '歎說'),
    ('汝輩', '你們'),
    ('吾今', '我今'),
    ('吾當', '我當'),
    ('爾等', '你們'),
    ('若欲', '若想要'),
]

for f in files:
    if not os.path.exists(f):
        problems.append(f'{f}: 文件不存在')
        continue
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    segs = data['translations']
    total_segments += len(segs)
    for i, seg in enumerate(segs):
        op = seg.get('original_preview', '')
        modern = seg.get('modern', '')
        # 拆分modern
        lines = modern.split('\n')
        title_line = lines[0].strip() if len(lines) > 0 else ''
        # 找义解行
        yijie = ''
        baihua_start = 0
        for li, line in enumerate(lines):
            if line.startswith('【义解】'):
                yijie = line[len('【义解】'):]
                baihua_start = li + 1
                break
        baihua = '\n'.join(lines[baihua_start:])
        # 1. 小标题检查：如果小标题是通用模板，且与内容无关
        # 2. 义解空泛检查
        is_generic_yj = False
        for gy in generic_yijie:
            if gy in yijie:
                is_generic_yj = True
                break
        if is_generic_yj:
            problems.append(f'{f} 第{i+1}段: 义解空泛模板化，无对应段落实质说明，使用通用套话')
        # 3. 白话替换错误检查
        for orig, wrong in wrong_pairs:
            if orig in op: # 原文有这个文言词
                # 检查白话里是否完全把orig替换成了wrong
                if wrong in baihua and wrong not in op and orig not in baihua:
                    problems.append(f'{f} 第{i+1}段: 原文文言“{orig}”被错误替换为白话“{wrong}”，未保留原字')
        # 4. 密咒顺序颠倒检查：先出咒再出“XX真言曰”
        mantra_markers = re.findall(r'([\u4e00-\u9fa5]{2,10}(?:真言曰|呪曰|明曰)[：:]?)', modern)
        for marker in mantra_markers:
            pos = modern.find(marker)
            after = modern[pos+len(marker):]
            # 去掉梵文咒字、数字、音注标记
            cleaned_after = re.sub(r'[􀀀-􏿿\W_\d]+', '', after)
            cleaned_after = re.sub(r'(二合|引|反切|半音|一|二|三|四|五|六|七|八|九|十|入|引聲)', '', cleaned_after)
            if len(cleaned_after) > 30:
                problems.append(f'{f} 第{i+1}段: 密咒/经文顺序颠倒，“{marker}”说明文出现在对应内容之后，打乱原文语序')
        # 5. 专有名词错误
        if '咸亨' in op and '都亨' in baihua:
            problems.append(f'{f} 第{i+1}段: 年号“咸亨”被错误改为“都亨”，原文文字被篡改')
        if '爾時' in op and '這時' in baihua:
            problems.append(f'{f} 第{i+1}段: 原文“爾時”被错误替换为“這時”，违反原字照录要求')
        if '曩莫' in op and ('曩謨' not in op and '曩莫' not in baihua):
            problems.append(f'{f} 第{i+1}段: 梵咒“曩莫”被替换，未原字照录')
        if '俱胝' in op and '胝' not in baihua:
            problems.append(f'{f} 第{i+1}段: 梵咒“俱胝”被替换，未原字照录')

print(f'=== 复核统计 ===')
print(f'总段落数: {total_segments}')
print(f'发现问题总数: {len(problems)}')
print()
for p in problems:
    print(p)
