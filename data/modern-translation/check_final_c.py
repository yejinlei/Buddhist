import json, os, re

files = ['t1239.json','t0850.json','t2075.json','t1251.json','t0953.json','t0887.json','t2871.json','t0682.json','t0341.json','t1757.json','t2810.json','t1797.json']
total_segments = 0
problems = []

# 空泛小标题
generic_titles = [
    '经文', '佛法要义', '修行法则', '功德利益', '神变瑞相',
    '供养之法', '结坛仪轨', '真言密咒', '结印观想', '护摩火供',
    '业报轮回', '律藏戒法', '净业除障', '圣众集会', '祖师传记',
    '西域巡礼', '皈敬颂文', '灌顶仪轨', '上堂开示', '菩萨行门',
    '法事圆满', '发菩提心', '亲近善知识', '经录著录', '注疏玄义',
    '曼荼罗道场', '序分', '正宗分', '流通分'
]

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

# 常见梵咒音译字（必须原字保留，不得翻译）
mantra_chars = ['曩莫', '娑婆訶', '娑嚩訶', '薩嚩', '莎訶', '唵', '吽', '怛喇', '二合', '引', '反切', '半音',
                '俱胝', '阿闍梨', '陀羅尼', '娑婆', '薩婆', '南無', '納莫', '曩謨', '鉢囉', '迦囉',
                '戍迦', '弭隸', '摩訶', '菩提', '薩埵', '摩尼', '鉢納摩', '伊醯', '婆夜', '那謨',
                '悉殿都', '漫多囉', '跋陀耶', '僧莎訶', '跢姪他', '怛姪他', '地夜他']

# 年号列表（必须原字保留）
era_names = ['咸亨', '貞觀', '永徽', '顯慶', '麟德', '乾封', '總章', '上元', '儀鳳', '調露', '永隆',
             '開耀', '永淳', '弘道', '嗣聖', '文明', '光宅', '垂拱', '永昌', '載初', '天授', '如意',
             '長壽', '延載', '證聖', '天冊萬歲', '萬歲登封', '萬歲通天', '神功', '聖曆', '久視',
             '大足', '長安', '神龍', '景龍', '景雲', '太極', '延和', '先天', '開元', '天寶',
             '至德', '乾元', '上元', '寶應', '廣德', '永泰', '大曆', '建中', '興元', '貞元',
             '永貞', '元和', '長慶', '寶曆', '大和', '開成', '會昌', '大中', '咸通', '乾符',
             '廣明', '中和', '光啟', '文德', '龍紀', '大順', '景福', '乾寧', '光化', '天復', '天祐',
             '建隆', '乾德', '開寶', '太平興國', '雍熙', '端拱', '淳化', '至道', '咸平', '景德',
             '大中祥符', '天禧', '乾興', '天聖', '明道', '景祐', '寶元', '康定', '慶曆', '皇祐',
             '至和', '嘉祐', '治平', '熙寧', '元豐', '元祐', '紹聖', '元符', '建中靖國', '崇寧',
             '大觀', '政和', '重和', '宣和', '靖康', '建炎', '紹興', '隆興', '乾道', '淳熙',
             '紹熙', '慶元', '嘉泰', '開禧', '嘉定', '寶慶', '紹定', '端平', '嘉熙', '淳祐',
             '寶祐', '開慶', '景定', '咸淳', '德祐', '景炎', '祥興', '洪武', '永樂', '宣德',
             '正統', '景泰', '天順', '成化', '弘治', '正德', '嘉靖', '隆慶', '萬曆', '泰昌', '天啟', '崇禎']

for f in files:
    path = os.path.join('/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/', f)
    if not os.path.exists(path):
        problems.append(f'{f}: 文件不存在')
        continue
    with open(path, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    segs = data.get('translations', [])
    total_segments += len(segs)
    
    for i, seg in enumerate(segs):
        op = seg.get('original_preview', '')
        modern = seg.get('modern', '')
        lines = [l for l in modern.split('\n') if l.strip() != '']
        
        # 1. 检查结构完整性：必须有标题（第一行）、【义解】行、白话正文
        if len(lines) < 2:
            problems.append(f'{f} 第{i+1}段: 结构不完整，内容行数不足')
            continue
        
        title_line = lines[0].strip()
        # 标题不能是空泛通用
        for gt in generic_titles:
            if title_line.strip() == gt:
                problems.append(f'{f} 第{i+1}段: 小标题"{gt}"空泛通用，未贴合本段具体内容')
                break
        
        # 找义解行
        yijie = ''
        yijie_idx = -1
        for li, line in enumerate(lines):
            if '【义解】' in line:
                yijie = line.split('【义解】', 1)[1].strip()
                yijie_idx = li
                break
        if yijie_idx == -1:
            problems.append(f'{f} 第{i+1}段: 缺少【义解】段落，结构不完整')
            continue
        
        # 义解后必须有白话正文
        baihua_lines = lines[yijie_idx+1:]
        baihua = '\n'.join(baihua_lines)
        if len(baihua.strip()) < 5:
            problems.append(f'{f} 第{i+1}段: 【义解】后缺少白话正文')
        
        # 2. 义解空泛检查
        is_generic_yj = False
        for gy in generic_yijie:
            if gy in yijie:
                is_generic_yj = True
                break
        if is_generic_yj:
            problems.append(f'{f} 第{i+1}段: 义解空泛模板化，使用通用套话，未针对本段内容做实质说明')
        
        # 3. original_preview 检查（结构上必须存在）
        if not op:
            problems.append(f'{f} 第{i+1}段: original_preview 为空，不符合要求')
        
        # 4. 梵咒原字照录检查：音译字必须原字保留
        for mc in mantra_chars:
            if mc in op:
                # 梵咒相关音译字必须在白话/modern中保留
                if mc not in modern:
                    problems.append(f'{f} 第{i+1}段: 梵咒音译字"{mc}"未原字照录，被替换或遗漏')
        
        # 5. 年号原字检查
        for era in era_names:
            if era in op:
                if era not in modern:
                    problems.append(f'{f} 第{i+1}段: 年号"{era}"被误改，未保留原字')
        
        # 6. 常见错误替换检查
        wrong_replacements = [
            ('爾時', '這時'), ('汝等', '你們'), ('汝', '你'),
            ('吾等', '我們'), ('吾', '我'), ('名曰', '名叫'),
            ('號曰', '名叫'), ('豈', '難道'), ('云何', '為什麼'),
            ('名為', '稱為'), ('汝輩', '你們'), ('爾等', '你們'),
        ]
        for orig, wrong in wrong_replacements:
            if orig in op and wrong in baihua and orig not in baihua:
                problems.append(f'{f} 第{i+1}段: 原文文言"{orig}"被错误替换为白话"{wrong}"，未保留原字')
        
        # 7. 密教仪轨经特别检查：密咒顺序，真言曰/咒曰之后必须是咒语，不能前面已经是咒语后面才出“XX曰”
        if f in ['t1239.json', 't0850.json', 't1251.json', 't0953.json']:
            mantra_markers = list(re.finditer(r'([\u4e00-\u9fa5]{2,12}(?:真言曰|呪曰|明曰|陀羅尼曰|神呪曰)[：:]?)', modern))
            for mm in mantra_markers:
                marker_text = mm.group(1)
                pos = mm.start()
                before = modern[:pos]
                after = modern[pos+len(marker_text):]
                # 检查前面是否已经有大量梵咒字（梵咒字多为生僻字+二合/引等标记）
                mantra_hits_before = 0
                for mc in mantra_chars:
                    if mc in before:
                        mantra_hits_before += 1
                if mantra_hits_before >= 3 and len(before) > 50:
                    problems.append(f'{f} 第{i+1}段: 密咒顺序疑似颠倒，"{marker_text}"说明文出现在大量梵咒文字之后，可能打乱原经文顺序')

print(f'=== C路终轮复核统计 ===')
print(f'检查文件数: {len(files)}')
print(f'总段落数: {total_segments}')
print(f'发现问题总数: {len(problems)}')
print()
for p in problems:
    print(p)

if len(problems) == 0:
    print('\nC路终轮复核通过：12部经文全部零问题，可上线')
