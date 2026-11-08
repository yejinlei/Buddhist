#!/usr/bin/env python3
"""按校对报告修正第6批10部白话翻译的高/中严重度问题"""
import json, os, re, copy
from pathlib import Path

ROOT = Path('/home/user/workspace/13511660557912876654/buddhist-ontology')
BAI = ROOT/'data/modern-translation'

def load(tid):
    with open(BAI/f'{tid}.json','r',encoding='utf-8') as f:
        return json.load(f)
def save(tid, data):
    with open(BAI/f'{tid}.json','w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  saved {tid}.json")

def find_seg(d, sec_match):
    """按 section 名（子串匹配）找段落"""
    for s in d['translations']:
        if sec_match in s.get('section',''):
            return s
    return None

def replace_in_modern(seg, old, new):
    if old in seg['modern']:
        seg['modern'] = seg['modern'].replace(old, new)
        return True
    return False

# ========== t0102 五蕴皆空经 ==========
def fix_t0102():
    print("fix t0102...")
    d = load('t0102')
    # H1: intro 舍利弗杜撰
    d['intro'] = d['intro'].replace('经中舍利弗遵佛所教，系统阐释了色、受、想、行识五蕴「无常、苦、空、无我」的本质', '经中世尊亲自在鹿野苑为五比丘宣说色、受、想、行识五蕴「无常、苦、空、无我」的本质')
    # M1: 第四段"观察一切色法"多余
    seg = find_seg(d, '以正智') or find_seg(d, '正智') or d['translations'][3]
    seg['modern'] = re.sub(
        r'你们应当知道，应当以正确的智慧如实地观察一切色法；同样的，所有受、想、行、识，无论是过去、未来还是现在的，也都应当像前面观察色法那样，以正智如实观察',
        '你们应当知道，应当以正智善加观察；所有受、想、行、识，无论过去、未来、现在，都应当像前面观察色法那样，以正智如实观察，了知它们无常、苦、空、无我的本质',
        seg['modern']
    )
    save('t0102', d)

# ========== t0131 婆罗门避死经 ==========
def fix_t0131():
    print("fix t0131...")
    d = load('t0131')
    # H1: intro/末段布施持戒杜撰
    d['intro'] = re.sub(
        r'并开示布施、持戒、修善才能获得生天果报、真正超越生死苦海[。]?',
        '揭示了死亡无人能免、无常无处可逃的真相',
        d['intro']
    )
    # 末段
    last = d['translations'][-1]
    # 删除"佛陀进一步开示：唯有布施…解脱。"
    last['modern'] = re.sub(
        r'佛陀进一步开示：[^\n]*唯有布施、持戒、修习善法，才能获得生天的果报，进而走向真正的解脱。\s*',
        '', last['modern']
    )
    # 末段义解
    last['modern'] = re.sub(
        r'【义解】.*$',
        '【义解】这一句是经典的常例结语。无常偈警醒众生：死亡无处可逃，应当正视生命的实相。',
        last['modern'], flags=re.S
    )
    # M1: 末段preview去重复偈子
    last['original_preview'] = '爾時，比丘聞佛所說，歡喜奉行。'
    # L1/L2: 第三段"四个方向"、第一段"共同商议"
    for s in d['translations']:
        s['modern'] = s['modern'].replace('四个方向', '四个处所')
        s['modern'] = s['modern'].replace('便共同商议', '便各自这样想')
    save('t0131', d)

# ========== t0217 譬喻经 ==========
def fix_t0217():
    print("fix t0217...")
    d = load('t0217')
    # H1: 第一段补"如是我闻"
    first = d['translations'][0]
    first['modern'] = first['modern'].replace('【法会缘起】那时', '【法会缘起】我是这样听闻的：\n那时')
    # 补 original_preview 开头
    if first['original_preview'].startswith('一時'):
        first['original_preview'] = '如是我聞：\n' + first['original_preview']
    # H2: 偈末翻译错误（找"不愿出离做个解脱的凡夫"）
    for s in d['translations']:
        if '不愿出离' in s['modern'] and '凡夫' in s['modern']:
            s['modern'] = s['modern'].replace(
                '哪里知道贪恋声色五欲的过失，不愿出离做个解脱的凡夫呢？',
                '却只知贪恋声色五欲，不乐于出离凡夫之位、迈向解脱。」'
            )
            # H3: 补闭合引号已在上方
            # 若替换后还缺少闭合」在义解前补
            idx = s['modern'].find('【义解】')
            before = s['modern'][:idx]
            if before.count('「') > before.count('」'):
                s['modern'] = s['modern'][:idx].rstrip() + '」\n' + s['modern'][idx:]
        # M1/M2: "尝蜜忘危"原文无
        s['modern'] = s['modern'].replace('他尝到甜味就暂时忘了危难，这时', '这时')
        s['modern'] = s['modern'].replace('仅因贪着五滴蜂蜜的短暂甜味就暂忘危难，又遭蜂螫、火烧。', '五滴蜂蜜恰巧堕入口中，紧接着又遭蜂螫、火烧。')
        # L1: 小标题统一为 section 值
        m = re.match(r'【[^】]+】', s['modern'])
        if m:
            s['modern'] = s['modern'].replace(m.group(0), f'【{s["section"]}】', 1)
        # L2: "毒龙等着吞食他"→"井底伏有毒龙"
        s['modern'] = s['modern'].replace('井底还有一条毒龙等着吞食他', '井底伏有毒龙')
        s['modern'] = s['modern'].replace('等着吞食他', '伏在井底')
    save('t0217', d)

# ========== t0218 灌顶王喻经 ==========
def fix_t0218():
    print("fix t0218...")
    d = load('t0218')
    # H1-H4: 全经"转轮圣王"改为"灌顶王"，"统御四方"去除
    d['intro'] = d['intro'].replace(
        '经中佛陀以古印度刹帝利种姓的灌顶转轮圣王传统为喻',
        '经中佛陀以古印度刹帝利种姓受王灌顶的传统为喻'
    ).replace(
        '三位受灌顶的转轮圣王',
        '三位领受灌顶的刹帝利王'
    ).replace(
        '佛教中借用灌顶的世俗仪式意象，引申为受法王位、得佛受记的象征',
        '佛教中借用灌顶的世俗仪式意象，类比出世圣位的成就'
    )
    for s in d['translations']:
        # H2
        if '第二王' in s.get('section',''):
            s['modern'] = s['modern'].replace('成为更高阶的转轮王', '领受灌顶即位成为国王')
            s['modern'] = s['modern'].replace('如同国王势力渐大，得登更尊胜的王位', '如同国王威德势力渐增，安稳治化')
        # H3
        if '第三王' in s.get('section',''):
            s['modern'] = s['modern'].replace('成为统御四方的转轮圣王', '依照灌顶礼法领受灌顶，安住于最尊胜的王位')
            s['modern'] = s['modern'].replace('如同转轮圣王统御四境，自在无碍', '如同最威勇的灌顶王安住胜位，一切怨敌归顺')
            s['modern'] = s['modern'].replace('胜妙的王位', '胜位')  # M5
        # H4
        if '上位' in s.get('section','') or '罗汉' in s.get('section',''):
            s['modern'] = s['modern'].replace('这一位对应第三位最尊胜的转轮圣王，断尽诸漏、证得阿罗汉果如同转轮圣王统御四方', '这一位对应第三位最威勇的灌顶王，断尽诸漏、证得阿罗汉果')
        # 兜底：所有"转轮圣王""统御四方"清除
        s['modern'] = s['modern'].replace('转轮圣王', '灌顶王').replace('统御四方', '')
    save('t0218', d)

# ========== t0391 灌腊经 ==========
def fix_t0391():
    print("fix t0391...")
    d = load('t0391')
    # H1: "五逆重罪"删除
    d['intro'] = d['intro'].replace('经中还论及妄语之罪、五逆重罪、三涂恶报', '经中还论及妄语之罪、五种恶报、三涂（三恶道）果报')
    # H2/H3: "灌腊"定义纠偏
    d['intro'] = d['intro'].replace(
        '"灌腊"即四月八日浴佛灌佛、七月十五日自恣日"受岁"（受戒腊）等法会仪轨',
        '"灌腊"特指七月十五日僧自恣日（受腊/受岁法会），即比丘结夏安居结束、戒腊增长一岁的法会仪轨；经中亦兼明四月八日浴佛供养法。四月八日浴佛、七月十五日自恣受腊是两个相关但性质不同的法会'
    ).replace('浴佛灌佛','浴佛')
    for s in d['translations']:
        # 各段"灌腊包含浴佛"等纠偏
        s['modern'] = s['modern'].replace('"灌腊"包含四月八日浴佛（灌佛）与七月十五日僧自恣受腊（戒腊增长日，即僧岁腊日）两类法会', '"灌腊"特指七月十五日自恣日受腊法会；四月八日浴佛是另一相关供养法')
        s['modern'] = s['modern'].replace('「灌腊」兼有「浴佛」与「腊岁」两重含义', '「灌腊」即受腊/受岁，指七月十五日夏安居结束后戒腊增长一岁')
        # M4: 因果误判
        s['modern'] = s['modern'].replace(
            '五重前报是现世花报（财物减损、健忘、经营失利、地狱苦、畜生奴婢身），三恶道是果报',
            '五种恶报兼具现生花报（财物日减、健忘、经营失利）与后世果报（堕地狱受拷、转生畜生奴婢）；进而更堕三恶道（饿鬼、畜生、地狱），罪报无量'
        )
        # M5: "侵妻子分"方向反
        s['modern'] = s['modern'].replace(
            '甚至分出本应供养妻儿的份来求福',
            '甚至夸口说连本属于妻儿的份额也拿来求福'
        )
        # M6: 回向
        s['modern'] = s['modern'].replace('由师父为他咒愿回向', '由师父为他达嚫祝愿')
        # L10: "奠定基础"
        s['modern'] = s['modern'].replace(
            '这一原则奠定了后世寺院共财制度与慈善布施的基础',
            '这体现了僧团利和同均、布施及众的原则'
        )
        # L11: "换取"→"求得"
        s['modern'] = s['modern'].replace('用以换取度脱世间的福报', '用以求得度脱世间的福德')
    save('t0391', d)

# ========== t0503 比丘避女恶名欲自杀经 ==========
def fix_t0503():
    print("fix t0503...")
    d = load('t0503')
    # H1: intro 洗白比丘
    d['intro'] = d['intro'].replace(
        '经中记载一位在林间修行的比丘，因被人诽谤与长者妇女有染，恶声流布，不堪受辱而欲自尽。天神化身长者女前往警醒，教示他：是非善恶不由他人言语决定，应当自证自知。经中比丘实无破戒过失，所有恶名皆是无根诽谤，闻偈后专精思惟，证得阿罗汉果。',
        '经中记载一位在林间修行的比丘，因与长者家妇女嬉戏往来，招致恶名流布；比丘戒行未破、不犯根本重罪，却不堪羞辱欲自尽明志。天神化身长者女前往警醒，教示他：是非善恶不由他人言语决定，应当自证自知。比丘闻偈后专精思惟，断除烦恼，证得阿罗汉果。'
    )
    for s in d['translations']:
        # H1: "正常接触/恶意编排"→"轻浮嬉戏"
        s['modern'] = s['modern'].replace(
            '当时这位比丘因与长者家妇女有正常接触，竟被旁人恶意编排，传出了行为不端的恶名。',
            '当时这位比丘与长者家妇女有轻浮嬉戏的往来，因此在地方上生出了行为不端的恶名。'
        )
        # M2: "以证明清白"删除
        s['modern'] = s['modern'].replace(
            '我不堪受这等污辱，今天才要在这里自杀，以证明我的清白！',
            '我正是因为这些街巷路口都在传我和你之间有染、往来不正的恶名，所以现在就要在这里自杀！'
        )
        # M3: 内心独白收敛
        s['modern'] = s['modern'].replace(
            '比丘心中极为痛苦，自认既已受戒出家修行，不该沾惹这样的污名，一时想不开，竟萌生了在林中自杀以明心志的念头。',
            '比丘心中这样想："我既已出家，不该与妇女惹出这样的恶名，我要在这林中自杀！"'
        )
        # M4: "护法天神""平白被谤"
        s['modern'] = s['modern'].replace(
            '当时住在林中的护法天神察知此事',
            '当时住在那林中的天神察知此事'
        )
        s['modern'] = s['modern'].replace(
            '平白被谤就要在林中轻生',
            '无重罪却要在林中自杀'
        )
        s['modern'] = s['modern'].replace(
            '这位比丘原本持戒清净，却因不实的污名险些轻生，我应当前去方便开导，让他醒悟。',
            '这事不好！这位比丘未破戒、无重罪，却想在林中自杀，我应当前去方便开导，让他醒悟。'
        )
        # M5: "考验道心"→"方便度化"
        s['modern'] = s['modern'].replace(
            '天神明辨清白，故意化现诱惑对境，是为考验比丘的道心是否真正坚固',
            '天神明比丘无重罪故，化现长者女之形为作逆耳之语，以激发比丘省思，是为方便度化'
        )
        # M6: "几句夸赞"→"几句言语"，"凭空"删
        s['modern'] = s['modern'].replace(
            '也不会因为别人几句夸赞，你就能凭空证得阿罗汉果',
            '也不会因为别人几句言语，就能让你证得阿罗汉果'
        )
        # L7: original_preview 补"如是我聞"
        if s['original_preview'].startswith('一時') and not s['original_preview'].startswith('如是我聞'):
            s['original_preview'] = '如是我聞：\n' + s['original_preview']
        # L10: "失去方寸"收敛
        s['modern'] = s['modern'].replace(
            '听到几句流言就恐惧慌乱、失去方寸，和林间受惊的鸟兽有什么区别？这种心浮气躁的状态，根本不符合出家修行人的本分',
            '听到恶声就恐怖惊惧的，那就像林间的走兽；这种心浮气躁的众生，不能成就出家之法'
        )
        # L9: "打家劫舍的强盗"→"强盗"
        s['modern'] = s['modern'].replace('打家劫舍的强盗','强盗')
    save('t0503', d)

# ========== t0560 老母女六英经 ==========
def fix_t0560():
    print("fix t0560...")
    d = load('t0560')
    # H1: "六英"是花名非六根
    d['intro'] = d['intro'].replace(
        '经题中「六英」即六根（眼耳鼻舌身意）又称六衰、六情。',
        '经题中「六英」指六种英华（花），为老母得名之由；经文中所说「五阴、六衰」才是五蕴与六根（六情）。'
    )
    # H2/H3: intro 杜撰情节
    d['intro'] = d['intro'].replace(
        '经中记载一位贫穷、年老、驼背的老妇人，因五阴六根衰老朽坏、苦不堪言，来到佛前请问五阴六衰从何而来、归向何处。',
        '经中记载一位贫穷、年老、驼背的老妇人，来到佛前请问五阴六衰会合我身、从何而来、归向何处。'
    )
    d['intro'] = d['intro'].replace(
        '国土庄严、人民安乐，衣食如忉利天，',
        '人民衣食如忉利天，'
    )
    for s in d['translations']:
        # M1: "六衰(六根/六英)"
        s['modern'] = s['modern'].replace(
            '六衰（六根/六英）',
            '六衰（即眼耳鼻舌身意六根，因其能衰损善法，故称六衰）'
        )
        # M2: "五体投地"
        s['modern'] = s['modern'].replace(
            '感动得五体投地',
            '欢喜得身体俯仰摇动（喜不自胜）'
        )
        # M3: 过度发挥
        s['modern'] = s['modern'].replace(
            '原本衰老疲惫的身体也顿觉轻安，不再有疲困苦痛',
            '身体不再感到疲惫'
        )
    save('t0560', d)

# ========== t1497 大乘戒经 ==========
def fix_t1497():
    print("fix t1497...")
    d = load('t1497')
    for s in d['translations']:
        # M2: "戒行壽命"直陈
        s['modern'] = s['modern'].replace(
            '有人破坏自己的戒行，如同断坏了修行的慧命',
            '有人破坏戒行与寿命（戒行即修行者的法身慧命）'
        )
        # M4: "女人无信"忠实
        s['modern'] = s['modern'].replace(
            '没有正信的女众不可随意亲近',
            '女众易生染着，不可亲近'
        )
    save('t1497', d)

# ========== t1498 八种长养功德经 ==========
def fix_t1498():
    print("fix t1498...")
    d = load('t1498')
    # H2: intro 补"长"读音注
    if '长养' in d['intro'] and 'zhǎng' not in d['intro']:
        d['intro'] += '「长」读 zhǎng，意为增长养育。'
    for s in d['translations']:
        # H1/M1: 八眾/八種加注
        s['modern'] = s['modern'].replace(
            '之后依教修行八种长养功德法',
            '之后依教修行八种长养功德法（原文偈颂作「八众」，即八种）'
        )
        # M2: "不久的将来"→"此生不久"
        s['modern'] = s['modern'].replace(
            '在不久的将来成就无上正等正觉',
            '以此善业因缘，愿我此生不久便得成就无上正等正觉'
        )
        # M3: "花、璎珞等香饰"
        s['modern'] = s['modern'].replace(
            '不以花、璎珞等香饰庄严自身，也不参与歌舞、观戏等放逸娱乐活动',
            '不以花鬘（花环等花饰）庄严自身，也不歌舞作乐、观听倡伎戏笑等'
        )
    save('t1498', d)

# ========== t1685 八大灵塔名号经 ==========
def fix_t1685():
    print("fix t1685...")
    d = load('t1685')
    for s in d['translations']:
        # H1: 第五处 桑迦尸/曲女城地理错误
        s['modern'] = re.sub(
            r'曲女城即僧伽尸（Saṃkāśya），佛上忉利天为母说法后下降处',
            '第五处曲女城，梵文或作僧伽尸（Saṃkāśya，桑迦尸），即佛上忉利天为摩耶夫人说法后下降人间处，在今印度 Sankisa；然佛典中另有曲女城（Kanyākubja，今 Kanauj）为另一地名，此经法贤译本将二名连用，系译者以"曲女城"指桑迦尸降凡处',
            s['modern']
        )
        s['modern'] = s['modern'].replace(
            '「桑迦尸」即梵文Saṃkāśya（僧伽尸），与曲女城为同地异名',
            '「桑迦尸」即梵文Saṃkāśya（今Sankisa），为佛从忉利天下降处；曲女城为该地区的另一汉译名，或为法贤译时的地名连称'
        )
        # H2: 第六处"声闻分别"非结集
        s['modern'] = s['modern'].replace(
            '王舍城为佛长期弘法、声闻弟子分别结集经典处',
            '王舍城——是佛在此为声闻弟子分别抉择佛法、教化度脱声闻众之处'
        )
        s['modern'] = s['modern'].replace(
            '「僧分别」指声闻弟子分别问法、结集经典',
            '「僧分别」即「声闻分别」，指如来在王舍城为声闻弟子分别（辨析）开示佛法、化度声闻众；非指「结集经典」（结集是佛灭后之事）'
        )
        # H3: 第七处"广严城灵塔"理解补正
        s['modern'] = s['modern'].replace(
            '廣嚴城靈塔——是佛思念寿量之处',
            '第七，廣嚴城——此处灵塔是佛思念寿量之处（佛在此观照住世寿量，预告即将入灭）'
        )
        # M4: "十二行法"→"三转十二行相"
        s['modern'] = s['modern'].replace(
            '转大法轮十二行法',
            '转大法轮，演说三转十二行相法'
        )
        # L1: 最后一段 modern/义解边界
        if s.get('section','').find('总结') >= 0 or s['modern'].find('总收一代时教') >= 0:
            # 把"总收一代时教..."移到【义解】中
            s['modern'] = re.sub(
                r'佛说完此偈，总收一代时教：八十年住世说法，最后于拘尸那城娑罗双树间入涅槃，八大灵塔正是释迦牟尼佛从降生到入灭一生化迹的永恒见证，[^】]*',
                '【义解】佛如是八十年住世说法，最后于拘尸那城娑罗双树间入涅槃。八大灵塔是释迦牟尼佛从降生到入灭一生化迹的永恒见证，为后世佛弟子提供了具体可朝拜、可供养、可忆念佛陀功德的圣地。',
                s['modern']
            )
            # 若modern首句是原句翻译则保留
            if '佛如是八十年住世' not in s['modern'][:50]:
                s['modern'] = '【总结】佛如是八十年住世，然后牟尼入于涅槃。\n' + s['modern']
    # 另：第七处"廣嚴城靈塔思念壽量處"重颂修正
    for s in d['translations']:
        s['modern'] = s['modern'].replace(
            '广严大城灵塔思念寿量',
            '广严大城灵塔之中，是如来思念寿量之处'
        )
    save('t1685', d)

# ========== t0102 / t0217 等额外清理：所有段中未闭合的「 """ 补全 ==========
def fix_unclosed_quotes():
    print("check unclosed quotes...")
    for tid in ['t0102','t0131','t0217','t0218','t0391','t0503','t0560','t1497','t1498','t1685']:
        d = load(tid)
        for s in d['translations']:
            m = s['modern']
            # 找【义解】前的部分（直译文）
            yijie_pos = m.find('【义解】')
            if yijie_pos < 0: continue
            body = m[:yijie_pos]
            if body.count('「') > body.count('」'):
                # 在义解前补闭合
                m = m[:yijie_pos].rstrip() + '」\n' + m[yijie_pos:]
                s['modern'] = m
        save(tid, d)

if __name__ == '__main__':
    for f in [fix_t0102, fix_t0131, fix_t0217, fix_t0218, fix_t0391, fix_t0503, fix_t0560, fix_t1497, fix_t1498, fix_t1685]:
        try:
            f()
        except Exception as e:
            print(f"  ERROR in {f.__name__}: {e}")
    fix_unclosed_quotes()
    print("Done.")
