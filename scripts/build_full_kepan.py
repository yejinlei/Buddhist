#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量结构科判生成器
- 对全藏2495部经生成「序分 / 正宗分 / 流通分」三分科判树
- 有品经把品挂进对应位置；无品经按卷分章
- 自动从关键词/doctrine标引提取义理要点标签（不编造）
- 保留已有64部core.json古德详细科判优先覆盖
- 重点核心经（64+重点扩展）补古德义理要点
"""
import json, re, copy, glob, os
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
INST_DIR = ROOT / 'ontology' / 'instances'
SUTRA_DIR = ROOT / 'sutras'
KEPAN_DIR = ROOT / 'kepan'

# ============ 1. 加载已有数据 ============
print("[1/6] 加载数据...")
CORE = json.load(open(KEPAN_DIR / 'core.json'))
IDX = json.load(open(SUTRA_DIR / 'index.json'))['sutras']
IDX_MAP = {s['id']: s for s in IDX}

# 关键词表：过滤掉分类性词
KW = json.load(open(ROOT / 'ontology' / 'sutra_keywords.json'))
KW_MAP = {}
KW_SUTRAS = KW.get('sutras', {})
if isinstance(KW_SUTRAS, dict):
    for sid, val in KW_SUTRAS.items():
        if isinstance(val, dict):
            KW_MAP[sid] = val.get('keywords', [])
CATEGORY_STOPWORDS = {
    '大乘','小乘','显教','密教','金刚乘','大乘佛教','小乘佛教',
    '阿含部类','般若部类','法华部类','華嚴部类','华严部类','寶積部类','宝积部类',
    '涅槃部类','大集部类','經集部类','经集部类','密教部类','律部类','釋經論部类','釋經論部类','毘曇部类','毗昙部类',
    '中觀部类','中观部类','瑜伽部类','論集部类','论集部类','經疏部类','经疏部类','律疏部类',
    '論疏部类','论疏部类','諸宗部类','诸宗部类','史傳部类','史传部类','事彙部类','事汇部类',
    '外教部类','目錄部类','目录部类','古逸部类','疑似部类','敦煌寫本部类','净土部类',
    '禪宗部类','禅宗部类','天台宗部类','華嚴宗部类','华严宗部类','法相宗部类','三論宗部类',
    '密宗部类','律宗部类'
}

# 段级义理索引：concept -> [{sutra_id, chapter_id, para_no, score}]
DSI = json.load(open(ROOT / 'ontology' / 'doctrine_section_index.json'))
DOCT_BY_SUTRA = defaultdict(list)  # sutra_id -> [(concept_id, score, chapter_id)]
# 概念名：优先读 M2 权威实例（instances/concepts/*.json, 221 个）
CONC_NAME = {}
_cdir = INST_DIR / 'concepts'
if _cdir.exists():
    for _f in sorted(glob.glob(str(_cdir / '*.json'))):
        try:
            _c = json.load(open(_f))
            _nid = _c.get('id')
            if _nid:
                CONC_NAME[_nid] = _c.get('name') or _c.get('name_zh') or _nid
        except Exception:
            pass
# 兜底：concepts-expanded.json（dict 含 concepts list）
if not CONC_NAME:
    _ce = json.load(open(ROOT / 'data' / 'concepts-expanded.json'))
    _cel = _ce.get('concepts', []) if isinstance(_ce, dict) else _ce
    for c in _cel:
        CONC_NAME[c.get('id', '')] = c.get('name_zh') or c.get('name') or c.get('id', '')
# 再兜底：data/concepts.json（list）
for c in json.load(open(ROOT / 'data' / 'concepts.json')):
    CONC_NAME.setdefault(c.get('id', ''), c.get('name', ''))

# 段级义理索引：concepts -> {concept_id, concept_name, hits:[{sutra_id, chapter_title, para_no}]}
for cid, obj in DSI.get('concepts', {}).items():
    _hits = obj.get('hits', []) if isinstance(obj, dict) else obj
    for hit in _hits:
        sid = hit.get('sutra_id')
        if sid:
            DOCT_BY_SUTRA[sid].append((cid, hit.get('score', 1), hit.get('chapter_title')))

print("  核心古德科判:", len(CORE))
print("  索引经:", len(IDX_MAP))
print("  有关键词经:", len(KW_MAP))
print("  段级义理命中概念:", len(DSI.get('concepts',{})))

# ============ 2. 三分判定规则 ============
XU_PATTERNS = [
    r'如是我\s*聞', r'聞\s*如\s*是', r'我聞如是',
    r'一\s*時[,，\s]*佛\s*[在遊住處]', r'一\s*時[,，\s]*婆伽婆',
    r'一\s*時[,，\s]*世尊', r'一\s*時[,，\s]*佛\s*與',
]
XU_CHAPTER_PATTERNS = [r'^序品', r'序分', r'通序', r'證信序', r'發起序', r'^如是我聞']

LIUTONG_PATTERNS = [
    r'皆大歡喜', r'皆\s*大\s*歡\s*喜',
    r'信\s*受\s*奉\s*行', r'信受奉行',
    r'佛\s*說\s*此\s*經\s*已', r'聞\s*佛\s*所\s*說',
    r'作\s*禮\s*而\s*去', r'頂\s*戴\s*受\s*持', r'頂戴受持',
    r'歡\s*喜\s*信\s*受', r'作\s*禮\s*而\s*退',
    r'右繞三匝', r'繞佛三匝', r'禮\s*佛\s*而\s*退',
]
LIUTONG_CHAPTER_PATTERNS = [r'囑累品', r'囑累', r'勸持品', r'流通分', r'付囑品', r'付嘱品']

def find_xu_boundary(texts):
    """返回序分结束的段落索引（不含）；0表示没有明确序分；返回-1表示整段全归序分（极短经）"""
    n = len(texts)
    if n == 0: return 0
    # 前15段中找
    joined = '\n'.join(texts[:min(n, 15)])
    # 找序分末尾标志：比丘众俱/菩萨众俱/will食时/入舍卫大城乞食等说法场景结束
    end_markers = [
        r'與大比丘眾[^。]*俱[，。]', r'與大比丘眾千二百五十人俱',
        r'與大菩薩眾[^。]*俱[，。]', r'與比丘[^。]*俱[，。]',
        r'爾時世尊[^。]*[。？！]', r'白佛言[：:]',
        r'佛告[^。]*[：:]',  # 佛告XX → 正式说法开始
    ]
    xu_text = '\n'.join(texts[:min(n, 8)])
    for m in end_markers:
        mm = re.search(m, xu_text)
        if mm:
            end = mm.end()
            # 数到第几段
            acc = 0
            for i, t in enumerate(texts[:8]):
                if acc + len(t) + 1 >= end:
                    # 序分至少占1段
                    return max(1, i+1) if i+1 < n else max(1, min(2, n))
                acc += len(t) + 1
    # 回退：第一段如果是译者/如是我闻开头，序分=1段
    if texts and re.search(r'如是我聞|聞如是|我聞如是|譯$|^如是我聞', texts[0][:60]):
        return 1
    return 0

def find_liutong_start(texts):
    """返回流通分起始段落索引；n表示无流通分。从尾部向前找。"""
    n = len(texts)
    if n == 0: return n
    tail = '\n'.join(texts[max(0, n-5):])
    for p in LIUTONG_PATTERNS:
        if re.search(p, tail):
            # 找到最早的"结句"位置作为流通分起点
            joined = '\n'.join(texts)
            for pat in LIUTONG_PATTERNS:
                mm = list(re.finditer(pat, joined))
                if mm:
                    m = mm[-1]  # 取最后一次出现
                    pos = m.start()
                    acc = 0
                    for i, t in enumerate(texts):
                        if acc + len(t) + 1 > pos:
                            return max(1, i)  # 流通分至少1段，且不覆盖全部
                        acc += len(t) + 1
    return n

def detect_chapter_part(ch_title, is_first, is_last):
    """根据章节标题判断它属于序/正宗/流通"""
    if ch_title is None: ch_title = ''
    for p in XU_CHAPTER_PATTERNS:
        if re.search(p, ch_title): return '序分'
    for p in LIUTONG_CHAPTER_PATTERNS:
        if re.search(p, ch_title): return '流通分'
    if is_first and re.search(r'序|緣起|開經', ch_title):
        return '序分'
    if is_last and re.search(r'流通|付囑|付嘱|囑累|勸持|囑累', ch_title):
        return '流通分'
    return None  # 由段落判定


# ============ 3. 义理要点提取 ============
def extract_meaning_points(sutra_id, chapters, kw_map):
    """返回该经的义理要点列表（短标签/短语）"""
    points = []
    seen = set()
    # ①从关键词取（排除分类词，取前6个最相关的教理词）
    kws = kw_map.get(sutra_id, [])
    taken = 0
    for w in kws:
        if w in CATEGORY_STOPWORDS: continue
        if w in seen: continue
        # 过滤人名/译师朝代词
        if re.search(r'(譯|師\s*$|大師|菩薩\s*$|佛\s*$|和尚|尊者|论师)', w) and taken >= 4:
            continue
        points.append({'text': w, 'source': 'keyword'})
        seen.add(w); taken += 1
        if taken >= 6: break
    # ②从段级义理索引取top概念
    docts = DOCT_BY_SUTRA.get(sutra_id, [])
    docts_sorted = sorted(docts, key=lambda x: -x[1])[:4]
    for cid, sc, _ in docts_sorted:
        name = CONC_NAME.get(cid)
        if name and name not in seen:
            points.append({'text': name, 'source': 'doctrine', 'cid': cid})
            seen.add(name)
    return points

def extract_chapter_points(sutra_id, chapter_id, all_chapter_docts):
    """返回某章的义理要点（基于段级命中）"""
    arr = all_chapter_docts.get((sutra_id, chapter_id), [])
    arr = sorted(arr, key=lambda x: -x[0])[:3]
    return [CONC_NAME.get(cid, cid) for cid, _ in arr if CONC_NAME.get(cid)]


# ============ 4. 科判树构建 ============
def _has_pin_in_tree(tree):
    for n in tree:
        if _walk_pin(n): return True
    return False

def _walk_pin(n):
    if '品' in (n.get('name') or ''): return True
    for c in n.get('children') or []:
        if _walk_pin(c): return True
    return False

def normalize_name(t):
    return (t or '').strip()

def is_juan_title(t):
    return bool(re.match(r'^卷\s*0?\d+$', t or ''))

def build_struct_kepan(sutra_id, sutra_text_obj, instance):
    """为一部经构建结构科判树。返回 (kepan_tree, points)"""
    content = sutra_text_obj.get('content', [])
    if not content:
        # 空经：生成最简树
        return ([
            {'name': '序分', 'type': '序分', 'description': '（经文内容缺失，按结构占位）', 'children': []},
            {'name': '正宗分', 'type': '正宗分', 'description': '（无正文）', 'children': []},
            {'name': '流通分', 'type': '流通分', 'description': '（无正文）', 'children': []},
        ], [])

    # 把内容块按 "卷xx/品xx" 拆成 chapter 列表
    # content 是 [{chapter, text}, ...]，chapter 可能是"卷001"也可能是品题
    # 按卷分组，卷下再找品
    juan_groups = []  # [(juan_title, [blocks_in_juan])]
    cur_juan = None; cur_blocks = []
    for blk in content:
        ch = blk.get('chapter','')
        if is_juan_title(ch) or re.match(r'^.+序$', ch):
            if cur_juan is not None: juan_groups.append((cur_juan, cur_blocks))
            cur_juan = ch; cur_blocks = [blk]
        else:
            if cur_juan is None:
                cur_juan = '卷001'
            cur_blocks.append(blk)
    if cur_juan is not None: juan_groups.append((cur_juan, cur_blocks))

    if not juan_groups:
        juan_groups = [('卷001', content)]

    # 收集所有块文本（与 juan_groups 顺序严格一致，含短卷标块），用于三分判定
    all_texts = []
    for _, blks in juan_groups:
        for b in blks:
            all_texts.append((b.get('text', '') or '').replace('\n', ''))
    total_blocks = len(all_texts)

    # 序分结束块下标（不含）、流通分起始块下标（均为块级索引，与 all_texts 对齐）
    xu_end = find_xu_boundary(all_texts)
    liu_start = find_liutong_start(all_texts)
    if xu_end < 0: xu_end = total_blocks              # -1 视为整经序分（极短经）
    if liu_start <= xu_end: liu_start = total_blocks  # 异常保护：流通分不得早于序分末

    # 构建章节节点（按卷→品的层级），并标所属分
    xu_nodes = []
    zheng_nodes = []
    liu_nodes = []

    # 收集该经段级义理命中
    chap_docts = defaultdict(list)
    for cid, sc, chid in DOCT_BY_SUTRA.get(sutra_id, []):
        if chid: chap_docts[(sutra_id, chid)].append((cid, sc))

    def part_of(bi):
        """按块级索引判定所属分"""
        if bi < xu_end: return '序分'
        if bi >= liu_start: return '流通分'
        return '正宗分'

    # 处理每卷
    bi = 0  # 全局块序号（与 all_texts 对齐）
    for jt, blks in juan_groups:
        juan_ch_name = normalize_name(jt)
        if not is_juan_title(juan_ch_name): juan_ch_name = juan_ch_name or '卷首'
        xu_in_juan = []; zheng_in_juan = []; liu_in_juan = []
        for b in blks:
            btitle = normalize_name(b.get('chapter',''))
            txt = b.get('text','').strip()
            part = part_of(bi)
            bi += 1
            # 标题判定覆盖（明确的品题如"序品""嘱累品"）
            ch_part = detect_chapter_part(btitle,
                                          is_first=(b is blks[0] and jt == juan_groups[0][0]),
                                          is_last=(b is blks[-1] and jt == juan_groups[-1][0]))
            if ch_part: part = ch_part

            # 纯卷标块（仅含译者行等短文本）跳过；含正文的卷块保留
            if is_juan_title(btitle) and len(txt) < 30:
                continue

            # 提取开头预览
            preview = re.sub(r'\s+','', txt)[:80]
            _suffix = '序分' if part == '序分' else ('流通分' if part == '流通分' else '正宗分')
            node = {
                'name': btitle if (btitle and not is_juan_title(btitle)) else f"{juan_ch_name}·{_suffix}",
                'auto': True,  # 标记为自动结构科判
                'juan': juan_ch_name,
                'desc': preview + ('…' if len(txt) > 80 else ''),
                'char_count': len(txt),
            }
            # 义理要点（若该块有段级命中）
            cpoints = extract_chapter_points(sutra_id, None, chap_docts)
            if cpoints:
                node['points'] = cpoints[:3]

            if part == '序分': xu_in_juan.append(node)
            elif part == '流通分': liu_in_juan.append(node)
            else: zheng_in_juan.append(node)

        # 把该卷的内容归到各分
        if xu_in_juan:
            juan_node = {'name': juan_ch_name, 'children': xu_in_juan, 'auto': True}
            xu_nodes.append(juan_node)
        if zheng_in_juan:
            # 卷下的品（若有"品"字标题）作为正宗分的子节点
            # 把 zheng_in_juan 中标题含"品"的单独标
            juan_node = {'name': juan_ch_name, 'auto': True, 'children': []}
            # 先直接挂（不再在卷内分组品，保持扁平）
            juan_node['children'] = zheng_in_juan
            zheng_nodes.append(juan_node)
        if liu_in_juan:
            juan_node = {'name': juan_ch_name, 'children': liu_in_juan, 'auto': True}
            liu_nodes.append(juan_node)

    # ---------- 描述 ----------
    title = sutra_text_obj.get('title','')
    juan_n = sutra_text_obj.get('juan_count') or len(juan_groups)
    char_n = sutra_text_obj.get('actual_char_count', 0)

    # 序分描述
    xu_desc = '法会缘起，证信发起' if xu_end > 0 else '（此经无标准序分，从正宗分起）'
    # 正宗分描述
    zheng_desc = f'全经主体，共 {juan_n} 卷'
    if char_n: zheng_desc += f'、约 {char_n:,} 字'
    # 流通分描述
    liu_desc = '结劝奉行，付嘱流通' if liu_start < total_blocks else '（此经无标准流通分，至正宗分止）'

    tree = [
        {'name': '序分', 'type': '序分', 'description': xu_desc, 'children': xu_nodes, 'auto': True},
        {'name': '正宗分', 'type': '正宗分', 'description': zheng_desc, 'children': zheng_nodes, 'auto': True},
        {'name': '流通分', 'type': '流通分', 'description': liu_desc, 'children': liu_nodes, 'auto': True},
    ]

    # 义理要点
    points = extract_meaning_points(sutra_id, None, KW_MAP)

    return tree, points

# ============ 5. 重点古德科判扩补（在core.json已有64部之外，再补核心经典）============
# 这里给最核心的20部左右重要经补古德式科判（依传统注疏要点）
ANCIENT_EXT = {
    't0475': {  # 维摩诘所说经
        'title': '維摩詰所說經',
        'ancient': True,
        'kepan': [
            {'name':'序分','type':'序分','description':'佛国缘起，宝积献盖',
             'children':[
                 {'name':'佛国品第一','desc':'宝积菩萨献盖，佛说"直心是菩萨净土"'},
                 {'name':'方便品第二','desc':'维摩诘示疾，为国王长者说法'}]},
            {'name':'正宗分','type':'正宗分','description':'弹偏斥小，叹大褒圆',
             'children':[
                 {'name':'弟子品第三','desc':'维摩诘逐一批斥声闻弟子：舍利弗宴坐、大目连说法、大迦叶乞食等皆被呵'},
                 {'name':'菩萨品第四','desc':'呵诸菩萨：光严/持世/善德等分别心被弹'},
                 {'name':'文殊问疾品第五','desc':'文殊师利承佛旨诣维摩诘问疾，入不二法门之始'},
                 {'name':'不思议品第六','desc':'维摩诘现不思议解脱神力，借座灯王，香积佛饭'},
                 {'name':'观众生品第七','desc':'天女散花，舍利弗天女男女相不可得，无住为本'},
                 {'name':'佛道品第八','desc':'文殊答"云何通达佛道"，行于非道即通达佛道'},
                 {'name':'入不二法门品第九','desc':'三十一位菩萨各说不二，维摩诘默然无言'},
                 {'name':'香积佛品第十','desc':'化菩萨往香积佛国取饭，香饭如一，众生食者得三昧'},
                 {'name':'菩萨行品第十一','desc':'阿难问佛此经名何，佛说此经名维摩诘所说，亦名不可思议解脱'},
                 {'name':'见阿閦佛品第十二','desc':'维摩诘以右手断取妙喜世界，示阿閦佛不动如来'}]},
            {'name':'流通分','type':'流通分','description':'嘱累弘通',
             'children':[
                 {'name':'法供养品第十三','desc':'天帝发愿受持，佛说"法供养为最"；药王菩萨本事'},
                 {'name':'嘱累品第十四','desc':'佛以法付嘱弥勒菩萨，令流通后世'}]}]},
    't0465': {  # 大佛顶如来密因修证了义诸菩萨万行首楞严经（大佛顶首楞严经/楞严经）
        'title': '大佛頂如來密因修證了義諸菩薩萬行首楞嚴經',
        'ancient': True,
        'kepan':[
            {'name':'序分','type':'序分','description':'阿难遭难，佛顶放光说咒',
             'children':[
                 {'name':'法会缘起','desc':'佛在室罗伐城，阿难独归途中遭摩登伽女梵天咒所摄'},
                 {'name':'佛顶神咒','desc':'世尊顶放百宝无畏光明，光中出生千叶宝莲，有佛化身结跏趺坐宣说神咒；文殊师利持咒救护阿难'}]},
            {'name':'正宗分·见道分（奢摩他）','type':'正宗分','description':'十番显见、二决定义，开示如来藏性',
             'children':[
                 {'name':'三番破识（卷一）','desc':'破心在身内/身外/潜根三处，七处征心总破妄识'},
                 {'name':'十番显见（卷二—卷四前半）','desc':'显见性是心非眼、显见不动、显见不灭、显见不失、显见无还、显见不杂、显见无碍、显见不分、显见超情、显见离见'},
                 {'name':'二种决定义','desc':'一者应当审观因地发心与果地觉为同为异；二者汝等若欲捐舍声闻修菩萨乘入佛知见，应当审详烦恼根本、无始菩提涅槃元清净体'},
                 {'name':'会通四科、七大即性','desc':'五阴六入十二处十八界本如来藏妙真如性；地水火风空见识七大圆融周遍法界'}]},
            {'name':'正宗分·修道分（三摩/禅那）','type':'正宗分','description':'修行方便、圆通法门、道场持咒、五阴魔境',
             'children':[
                 {'name':'二十五圆通（卷五—卷六）','desc':'憍陈那五尘、优波尼沙陀色因、香严香严、药王药上味因、跋陀婆罗触因、迦叶音声、阿那律眼、周利盘陀伽鼻、憍梵钵提舌、毕陵伽婆蹉身、须菩提意、舍利弗眼识、普贤耳识、孙陀罗难陀鼻识、富楼那舌识、优波离身识、目犍连意识、大势至菩萨念佛圆通、观世音菩萨耳根圆通'},
                 {'name':'四种清净明诲（卷六）','desc':'淫、杀、盗、妄四戒决定清净明诲'},
                 {'name':'楞严神咒及坛场仪轨（卷七）','desc':'建立道场、诵持楞严神咒功德利益'},
                 {'name':'三界七趣（卷八—卷九前半）','desc':'地狱、鬼、畜生、人、仙、天、阿修罗七趣升沉因由'},
                 {'name':'五阴魔境（卷九后半—卷十）','desc':'色阴/受阴/想阴/行阴/识阴十魔境，行者于定中当善识别'}]},
            {'name':'流通分','type':'流通分','description':'大众获益，礼谢奉行',
             'children':[
                 {'name':'说法功德','desc':'阿难及诸大众闻佛所说，得未曾有，皆大欢喜'},
                 {'name':'礼谢流通','desc':'大众作礼而去，信受奉行'}]}]},
    't0416': {  # 大方广圆觉修多罗了义经（圆觉经）
        'title': '大方廣圓覺修多羅了義經',
        'ancient': True,
        'kepan':[
            {'name':'序分','type':'序分','description':'佛入神通大光明藏，现出净土',
             'children':[{'name':'法会缘起','desc':'佛在神通大光明藏，与十万菩萨俱；文殊师利菩萨为上首'}]},
            {'name':'正宗分','type':'正宗分','description':'十二菩萨请问，佛答三观二十五轮',
             'children':[
                 {'name':'文殊章（一章）','desc':'答"如来本起因地"，说"无明本空、觉性圆明"，成就信解'},
                 {'name':'普贤章（二章）','desc':'答修行方便，说离幻即觉、渐次方便'},
                 {'name':'普眼章（三章）','desc':'答三观方便，说奢摩他/三摩钵提/禅那三观；二十五种清净定轮'},
                 {'name':'金刚藏章（四章）','desc':'答众生何时有无明、何时成佛，说轮回性空'},
                 {'name':'弥勒章（五章）','desc':'答五性差别，说众生本来成佛'},
                 {'name':'清净慧章（六章）','desc':'答修证阶位，说圆觉自性随顺觉性四相'},
                 {'name':'威德自在章（七章）','desc':'答二十五种清净定轮的具体行法'},
                 {'name':'辨音章（八章）','desc':'答辩音菩萨所问二十五种修行方法差别'},
                 {'name':'净诸业障章（九章）','desc':'答我相/人相/众生相/寿者相四相病源，除障方法'},
                 {'name':'普觉章（十章）','desc':'答亲近善知识、三观修法、四病（作/任/止/灭）'},
                 {'name':'圆觉章（十一章）','desc':'答安居结制、道场观行方法'},
                 {'name':'贤善首章（十二章）','desc':'答此经名、持经功德、流布后世'}]},
            {'name':'流通分','type':'流通分','description':'金刚、护法护持，大众奉行',
             'children':[{'name':'护持流通','desc':'金刚、天王、鬼王等发誓护持；闻经大众作礼奉行'}]}]},
    't0366': {  # 佛说无量寿经（曹魏康僧铠本，净土根本经之一）
        'title': '佛說無量壽經',
        'ancient': True,
        'kepan':[
            {'name':'序分','type':'序分','description':'法会缘起，放光现瑞',
             'children':[{'name':'法会众集','desc':'佛在王舍城耆阇崛山，与大比丘众万二千人俱；菩萨普贤/文殊/弥勒/贤护等上首'}]},
            {'name':'正宗分·法藏因行（卷上）','type':'正宗分','description':'阿难启请，世尊说弥陀因行与本愿',
             'children':[
                 {'name':'法藏出家','desc':'过去锭光如来以来，法藏比丘于世自在王佛前出家，发四十八大愿'},
                 {'name':'四十八愿','desc':'国无三恶道/不更恶道/悉皆金色/无有好丑/宿命通/天耳通/他心通/天眼通/神足通/漏尽通/住正定聚/光明无量/寿命无量/声闻无数/眷属长寿/无诸不善/诸佛称叹/十念必生/临终接引/来生我国皆具三十二相/具足诸根/究竟必至一生补处/供养诸佛/供具如意/三十二相/说智辩/那罗延身/国无尘劳/万物严净/道场树/受经慧辩/辩才无尽/国土清净/见十方佛/宝香妙衣/见道场树/耳闻德法/无诸难值/闻名得忍/女身成佛/常修梵行/天人致敬/衣服随念/乐如漏尽/树中现刹/宝香普熏/普等三昧/一生补处/诸佛称叹/顶礼归依/三辈往生/一心系念即生我国'}]},
            {'name':'正宗分·果德圆满','type':'正宗分','description':'法藏成佛号阿弥陀，极乐世界庄严',
             'children':[
                 {'name':'极乐净土庄严','desc':'七宝池八功德水、黄金为地、楼阁栏楯、天乐雨华、百味饮食、化鸟鸣法音'},
                 {'name':'三辈往生','desc':'上辈发菩提心、一向专念；中辈发心多少修善；下辈发心十念一念皆得往生'},
                 {'name':'边地疑城','desc':'疑惑佛智但种善根者，生边地七宝宫殿五百岁不见三宝'}]},
            {'name':'正宗分·劝勉流通','type':'正宗分','description':'付嘱弥勒，末世众生当信此经',
             'children':[{'name':'娑婆五恶五痛五烧','desc':'释迦佛痛说末世众生五恶（杀盗淫妄酒）业报，劝持名念佛'}]},
            {'name':'流通分','type':'流通分','description':'大众获益，信受奉行',
             'children':[{'name':'大众作礼','desc':'弥勒菩萨、阿难尊者及诸大众闻佛所说，皆大欢喜信受奉行'}]}]},
    't0365': {  # 佛说观无量寿佛经
        'title': '佛說觀無量壽佛經',
        'ancient': True,
        'kepan':[
            {'name':'序分','type':'序分','description':'王宫密受，阇王害父，韦提希被禁',
             'children':[{'name':'韦提希请法','desc':'阿阇世王弑父禁母；韦提希夫人幽闭宫中遥礼世尊；佛与目连阿难现身宫中'}]},
            {'name':'正宗分','type':'正宗分','description':'定散二善、十六妙观',
             'children':[
                 {'name':'净业三福','desc':'一者孝养父母奉事师长慈心不杀修十善业；二者受持三皈具足众戒不犯威仪；三者发菩提心深信因果读诵大乘劝进行者'},
                 {'name':'十六观（定善十三观）','desc':'日观、水观、地观、宝树观、宝池观、宝楼观、华座观、像观、真身观、观音观、势至观、普观、杂想观'},
                 {'name':'三辈九品（散善三观）','desc':'上品上生/上品中生/上品下生；中品上生/中品中生/中品下生；下品上生/下品中生/下品下生'}]},
            {'name':'流通分','type':'流通分','description':'阿难传诵，诸天护持',
             'children':[{'name':'付嘱阿难','desc':'佛告阿难汝好受持此法语，韦提希与五百侍女闻法往生，天龙八部信受奉行'}]}]},
    't0399': {  # 大方等大集经
        'title': '大方等大集經',
        'ancient': False,  # 内容庞杂，保留为结构要点
        'kepan': None  # 让结构科判接管，在要点中标重点
    },
    't0458': {  # 梵网经（菩萨戒）
        'title': '梵網經',
        'ancient': True,
        'kepan':[
            {'name':'序分','type':'序分','description':'释迦在摩醯首罗天宫说菩萨心地',
             'children':[{'name':'卢舍那佛说菩萨心地戒品','desc':'佛现千花千叶光，卢舍那佛坐莲花台说十地法门'}]},
            {'name':'正宗分','type':'正宗分','description':'十重四十八轻戒',
             'children':[
                 {'name':'十重戒','desc':'杀/盗/淫/妄语/酤酒/说四众过/自赞毁他/悭惜加毁/嗔不受悔/谤三宝'},
                 {'name':'四十八轻戒','desc':'不敬师友/饮酒/食肉/食五辛/不教悔罪/不供给请法/懈怠不听法/背大向小/不看病/畜杀具/为国使/贩卖/谤毁/放火/僻教/为利倒说/恃势乞求/无解作师/两舌/不行放救/嗔打报仇/骄慢不请/轻慢新学/别请/恶观命终/畜猫狸/蓄养狸猪等'}]},
            {'name':'流通分','type':'流通分','description':'大众受持，礼佛而去',
             'children':[{'name':'受持流通','desc':'菩萨闻此戒法欢喜受持，顶戴奉行'}]}]},
    't1425': {  # 大乘起信论（马鸣菩萨造）
        'title': '大乘起信論',
        'ancient': True,
        'kepan':[
            {'name':'序分（造论因缘）','type':'序分','description':'归敬三宝，述造论因缘',
             'children':[{'name':'归敬与造论意','desc':'归命尽十方，最胜业遍知；为欲令众生除疑舍邪执，起大乘正信，佛种不断故'}]},
            {'name':'正宗分·一心二门','type':'正宗分','description':'一心开真如门与生灭门',
             'children':[
                 {'name':'因缘分','desc':'说八种造论因缘'},
                 {'name':'立义分','desc':'摩诃衍者，一心法有二种门：一者心真如门，二者心生灭门；是二门皆各摄一切法'},
                 {'name':'解释分（三大部分）','desc':'一者显示正义（真如/生灭/三大）；二者对治邪执；三者分别发趣道相'},
                 {'name':'真如/生灭/阿黎耶识','desc':'真如相：如实空/如实不空；生灭因缘：阿黎耶识/觉与不觉/真妄互熏；三大：体大/相大/用大'}]},
            {'name':'正宗分·修行信心','type':'正宗分','description':'五行五信心，修行方便',
             'children':[
                 {'name':'修行信心分','desc':'信心根本：信真如/信佛宝/信法宝/信僧宝；施/戒/忍/进/止观五门；修止修观'},
                 {'name':'劝修利益分','desc':'末世众生持此论者功德无量，令信心不退'}]},
            {'name':'流通分','type':'流通分','description':'回向结劝',
             'children':[{'name':'回向','desc':'回向众生同得菩提'}]}]},
    't1509': {  # 大智度论
        'title': '大智度論',
        'ancient': True,
        'kepan': None  # 卷帙浩繁（100卷），保留结构，义理要点自动
    },
    't1545': {  # 大乘中观释论 等中观论典
        'title': None,
        'ancient': False,
        'kepan': None
    },
}

# 标记哪些是ancient（古德科判），哪些只补标签、结构由自动生成
for sid, obj in ANCIENT_EXT.items():
    if obj.get('kepan') is None:
        # 只标记为重点、不覆盖结构
        obj['_structural_only'] = True
        obj['kepan'] = None

# ============ 6. 逐经生成 ============
print("[2/6] 逐经生成科判...")
FULL_KEPAN = {}
STATS = {
    'total': 0, 'ancient_preserved': 0, 'ancient_extended': 0,
    'structural': 0, 'with_points': 0,
    'xu_with_content': 0, 'liu_with_content': 0,
    'with_pin_titles': 0, 'empty': 0,
}

# 全部经id列表（从sutras目录拿）
all_sutra_files = sorted(glob.glob(str(SUTRA_DIR / 't*.json')))
all_sids = [Path(f).stem for f in all_sutra_files]
print(f"  正文文件数: {len(all_sids)}")

# 先把别名id（如puxian_xingyuan/jingang_jiumo等）转成对应的t号
ALIAS_MAP = {
    'amituo_jiumo': 't0366',  # 鸠摩罗什本阿弥陀经
    'bada_renjue': 't0779',   # 八大人觉经
    'fo_yijiao': 't0389',     # 佛遗教经
    'jingang_jiumo': 't0235', # 鸠摩罗什金刚经（别名）
    'puxian_xingyuan': 't0293',  # 普贤行愿品（华严经入法界品别行）
    'sishi_erzhang': 't0784', # 四十二章经
}

processed = set()
for sid in all_sids:
    try:
        sobj = json.load(open(SUTRA_DIR / f'{sid}.json'))
    except:
        continue
    STATS['total'] += 1
    # 读实例（可能缺失）
    inst_path = INST_DIR / f'{sid}.json'
    inst = None
    if inst_path.exists():
        try: inst = json.load(open(inst_path))
        except: inst = None

    # ===== 优先级：古德扩展 (ancient=True且有kepan) > core.json已有 > 自动结构 =====
    kepan_tree = None
    ancient = False
    if sid in ANCIENT_EXT and ANCIENT_EXT[sid].get('kepan'):
        kepan_tree = ANCIENT_EXT[sid]['kepan']
        ancient = True
        STATS['ancient_extended'] += 1
    elif sid in CORE and isinstance(CORE[sid], dict) and CORE[sid].get('kepan'):
        kepan_tree = CORE[sid]['kepan']
        ancient = True
        STATS['ancient_preserved'] += 1

    if kepan_tree is None:
        # 自动结构生成
        kepan_tree, _ = build_struct_kepan(sid, sobj, inst)
        STATS['structural'] += 1
        # 标记auto
        for n in kepan_tree:
            n['auto'] = True
    else:
        # 古德科判，标记
        for n in kepan_tree:
            n['ancient'] = True
            n['auto'] = False

    # 义理要点
    points = extract_meaning_points(sid, None, KW_MAP)
    # 重点经若有ANCIENT_EXT但仅结构（无kepan覆盖），加重点标记
    if sid in ANCIENT_EXT and ANCIENT_EXT[sid].get('_structural_only'):
        points.insert(0, {'text': '重点核心经典', 'source': 'tag', 'priority': 'high'})

    # 统计序分/流通分是否有内容（按 type 查找，避免硬索引越界）
    def count_children(n):
        t = 0
        for c in n.get('children') or []:
            t += 1 + count_children(c)
        return t
    def _part_node(tree, ptype):
        for _n in tree or []:
            if _n.get('type') == ptype:
                return _n
        return None
    _xu_n = _part_node(kepan_tree, '序分')
    _liu_n = _part_node(kepan_tree, '流通分')
    if _xu_n and count_children(_xu_n) > 0: STATS['xu_with_content'] += 1
    if _liu_n and count_children(_liu_n) > 0: STATS['liu_with_content'] += 1

    # 统计有品题的
    has_pin = _has_pin_in_tree(kepan_tree)
    if has_pin: STATS['with_pin_titles'] += 1

    if points: STATS['with_points'] += 1

    # 组装
    entry = {
        'title': sobj.get('title') or (CORE.get(sid,{}) or {}).get('title',''),
        'taisho': sobj.get('taisho',''),
        'translator': sobj.get('translator',''),
        'juan': sobj.get('juan_count') or sobj.get('juan',0),
        'chars': sobj.get('actual_char_count') or sobj.get('chars',0),
        'category': sobj.get('category',''),
        'ancient': ancient,
        'auto': not ancient,
        'kepan': kepan_tree,
        'meaning_points': points,
    }
    FULL_KEPAN[sid] = entry
    processed.add(sid)

# 处理别名经 id（amituo_jiumo / jingang_jiumo / puxian_xingyuan 等，读经页以这些 id 加载）
ALIAS_IDS = ['amituo_jiumo', 'bada_renjue', 'fo_yijiao', 'jingang_jiumo', 'puxian_xingyuan', 'sishi_erzhang']
for kid in ALIAS_IDS:
    ap = SUTRA_DIR / f'{kid}.json'
    if not ap.exists():
        continue
    try:
        aobj = json.load(open(ap))
    except Exception:
        aobj = {}
    alt_title = aobj.get('title', '')
    real = ALIAS_MAP.get(kid)
    if kid in CORE and isinstance(CORE[kid], dict) and CORE[kid].get('kepan'):
        # 优先用别名自身的古德科判（如普贤行愿品别行本）
        entry = CORE[kid]
        for n in entry['kepan']:
            n['ancient'] = True; n['auto'] = False
        entry['ancient'] = True; entry['auto'] = False
        entry.setdefault('meaning_points', [])
        if alt_title: entry['title'] = alt_title
        FULL_KEPAN[kid] = entry
        STATS['ancient_preserved'] += 1
    elif real and real in FULL_KEPAN:
        # 复用对应 t 号的科判（深拷贝，标注别名来源）
        e = copy.deepcopy(FULL_KEPAN[real])
        e['alias_of'] = real
        if alt_title: e['title'] = alt_title
        FULL_KEPAN[kid] = e
    else:
        continue
    STATS['total'] += 1

# ============ 7. 输出 ============
print("[3/6] 写 core.json...")
with open(KEPAN_DIR / 'core.json', 'w', encoding='utf-8') as f:
    json.dump(FULL_KEPAN, f, ensure_ascii=False, indent=1)

# 写索引（供站点地图/科判页使用）
print("[4/6] 写 kepan_index.json...")
index = {
    'meta': {
        'version': '2.0.0-full',
        'total': STATS['total'],
        'ancient_preserved': STATS['ancient_preserved'],
        'ancient_extended': STATS['ancient_extended'],
        'structural_auto': STATS['structural'],
        'with_meaning_points': STATS['with_points'],
        'xu_with_content': STATS['xu_with_content'],
        'liu_with_content': STATS['liu_with_content'],
        'with_pin_titles': STATS['with_pin_titles'],
        'description': '全藏结构科判+古德义理科判；auto=True 为结构自动生成，ancient=True 为古德/传统注疏科判',
        'updated_at': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M'),
    },
    'sutras': {sid: {
        'title': v.get('title',''),
        'ancient': v.get('ancient',False),
        'auto': v.get('auto',True),
        'category': v.get('category',''),
        'juan': v.get('juan',0),
        'chars': v.get('chars',0),
        'points_count': len(v.get('meaning_points') or []),
        'xu_children': sum(1 for n in v['kepan'] if n.get('type')=='序分' for _ in (n.get('children') or [])),
        'zheng_children': sum(1 for n in v['kepan'] if n.get('type')=='正宗分' for _ in (n.get('children') or [])),
        'liu_children': sum(1 for n in v['kepan'] if n.get('type')=='流通分' for _ in (n.get('children') or [])),
    } for sid, v in FULL_KEPAN.items()}
}
with open(KEPAN_DIR / 'index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, separators=(',', ':'))

print("\n=== 完成统计 ===")
for k,v in STATS.items():
    print(f"  {k}: {v}")
print(f"  index 总条目: {len(index['sutras'])}")
