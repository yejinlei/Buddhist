#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_all_instances.py v3 - 简化可靠的偈/咒/三分识别"""
import json, os, re
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUTRA_DIR = os.path.join(ROOT, 'sutras')
OUT_DIR = os.path.join(ROOT, 'ontology', 'instances')

def load_json(p):
    with open(p, encoding='utf-8') as f: return json.load(f)
sutra_index = load_json(os.path.join(SUTRA_DIR, 'index-light.json'))
items = sutra_index['items']
meta_by_id = {it['id']: it for it in items}

persons_raw = load_json(os.path.join(ROOT, 'data', 'persons-expanded.json'))
person_by_name = {}; person_list = persons_raw['persons']
for p in person_list:
    for n in [p['name']] + p.get('alias',[]):
        n = n.strip().replace('《','').replace('》','')
        if n and len(n)>=2: person_by_name[n] = p['id']

concepts_raw = load_json(os.path.join(ROOT, 'data', 'concepts-expanded.json'))
concept_by_name = {}; concept_list = concepts_raw['concepts']
for c in concept_list:
    for n in [c['name']] + c.get('alias',[]):
        n = n.strip().replace('《','').replace('》','')
        if n and len(n)>=2: concept_by_name[n] = c['id']

cat2school = load_json(os.path.join(ROOT, 'ontology', 'category_school_mapping.json'))
parallel = load_json(os.path.join(ROOT, 'ontology', 'parallel_translations.json'))
groups = parallel.get('groups', parallel) if isinstance(parallel, dict) else parallel
para_by_id = defaultdict(list)
for g in groups:
    members = g.get('members') or g.get('sutras') or []
    ids = [m.get('id') or m.get('taisho_id') for m in members if (m.get('id') or m.get('taisho_id'))]
    for i in ids:
        for j in ids:
            if j!=i: para_by_id[i].append(j)
h2s = load_json(os.path.join(ROOT, 'data', 'hant2simp_full.json'))
def to_simp(s): return ''.join(h2s.get(ch,ch) for ch in s)
simp_pn = {to_simp(n):pid for n,pid in person_by_name.items()}
simp_cn = {to_simp(n):cid for n,cid in concept_by_name.items()}
PNS = sorted(set(person_by_name.keys())|set(simp_pn.keys()), key=len, reverse=True)
CNS = sorted(set(concept_by_name.keys())|set(simp_cn.keys()), key=len, reverse=True)
def find_persons(text):
    s=set()
    for n in PNS:
        if len(n)<2: continue
        if n in text:
            pid=person_by_name.get(n) or simp_pn.get(n)
            if pid: s.add(pid)
    return s
def find_concepts(text):
    s=set()
    for n in CNS:
        if len(n)<2: continue
        if n in text:
            cid=concept_by_name.get(n) or simp_cn.get(n)
            if cid: s.add(cid)
    return s

# ========== 识别规则 v3：稳妥启发式 ==========
TRANSLATOR_RE = re.compile(r'(譯$|奉\s*詔譯|共\s*\S+譯|三藏法師\S+\s*(奉\s*詔\s*)?譯|\S+\s*譯$)')

def is_translator_line(line):
    return len(line) <= 60 and bool(TRANSLATOR_RE.search(line))

# 偈颂引导：
GATHA_HEADER_RE = re.compile(
    r'(而(說|作)偈(言|曰)|說偈(言|曰)|偈(曰|言)|以偈(答|頌|問|讚)|而說頌曰|說頌曰|即說偈言|復說偈言|說是偈已|以偈頌|偈讚(曰|言)|承佛威[神力].*而(說|演)頌曰|承佛.*說偈|說偈贊|而說法偈|以偈嘆|復以偈|偈答|偈問)'
)
# 偈颂终止：下一段以长行关键词开头
GATHA_STOP_RE = re.compile(r'^(爾時|佛告|是時|須菩提|舍利弗|佛言|阿難|時|文殊|于是|於是|復次|爾時世尊|菩薩|時諸|唯然|賢護|大王|時有|世尊|阿逸多|彌勒)', re.U)

def clean(s): return re.sub(r'[，。、？！：；「」『』（）()《》\s·…—─　]','',s)

def split_sentences(s):
    """把一段按句末标点切成句子（只在句读处切）。"""
    parts = re.split(r'[，。、？！：；]', s)
    return [p for p in parts if p.strip() and not re.fullmatch(r'[「」『』（）\s]+', p)]

def verse_ratio(s):
    """返回段内诗句（4/5/6/7 言）比例与主句式。"""
    # 先把引号去掉
    s2 = s.replace('「','').replace('」','').replace('『','').replace('』','')
    sents = split_sentences(s2)
    sents = [clean(x) for x in sents]
    sents = [x for x in sents if 3 <= len(x) <= 8]
    if not sents: return 0, None
    cnt = Counter(len(x) for x in sents)
    # 常见诗体：四句偈/五言/六言/七言
    total = len(sents)
    verse_n = sum(v for k,v in cnt.items() if k in (4,5,6,7))
    meter_len = max((v,k) for k,v in cnt.items() if k in (4,5,6,7))[1] if any(k in cnt for k in (4,5,6,7)) else None
    meter = {4:'四句偈',5:'五言',6:'六言',7:'七言'}.get(meter_len, '偈颂') if meter_len else None
    return verse_n/total, meter

def para_is_mantra(text, is_after_mantra_intro=False, ch_title=''):
    """识别咒语：依据密咒特征——音译字+以'莎婆訶/娑婆訶/娑訶'结尾，或以'南謨/唵/吽/怛儞也'开头且全文为梵音。
    is_after_mantra_intro: 上一段是"即说咒曰/咒曰/陀羅尼曰"等咒语导语，本段为咒文。
    """
    t = text.strip()
    if not t: return False, None
    end_m = re.search(r'(莎婆訶|娑婆訶|薩婆訶|莎訶|娑訶|薩訶|娑嚩訶|薩嚩訶|梭哈|svāhā|svaha)\s*[。！？」』」]*$', t)
    start_m = re.match(r'^(「\s*)?(南謨|曩莫|那謨|娜莫|怛儞也(他)?|唵\s|捺謨|納莫|曩莫三曼多|揭帝|揭諦|竭諦|羯諦)', t)
    has_siddham = bool(re.search(r'(唵\s|吽\s|鉢喇|波羅弭多曳|毘舍耶|阿彌唎|薩婆訶|莎婆訶|娑婆訶|哆他伽哆夜|阿嚧|闇\s|嚧|醯|尸棄|菩提薩婆訶|般羅揭帝|般羅僧揭帝)', t))
    spaces = t.count(' ') + t.count('　')
    prose_punct = t.count('。')
    chinese_prose = sum(1 for h in ['佛言','爾時','菩薩白','比丘','須菩提白','舍利弗白','白佛言','合掌','偏袒右肩'] if h in t)
    # 明确咒语
    if end_m and (start_m or has_siddham or spaces >= 2 or is_after_mantra_intro):
        name = '真言'
        m = re.search(r'([\u4e00-\u9fff]{2,12})(真言|陀羅尼|神咒|咒)(曰|：)?', ch_title)
        if m: name = m.group(1)+m.group(2)
        # 在段首找咒名（"故說般若波羅蜜多咒"）
        m2 = re.search(r'說([\u4e00-\u9fff]{2,12})(咒|陀羅尼|真言)', t[-60:])
        if m2 and name == '真言': name = m2.group(1)+m2.group(2)
        return True, name
    if start_m and (spaces >= 2 or has_siddham) and prose_punct <= 2 and chinese_prose == 0:
        return True, '真言'
    # 咒语导语后的一段且含梵音
    if is_after_mantra_intro and (end_m or has_siddham or start_m or spaces >= 2) and chinese_prose <= 1:
        return True, '真言'
    return False, None

def is_verse_paragraph(text):
    """严格齐言偈判定（v3.2）：
    一句如实偈颂应为齐言短句。要求：
      1) 去引号切句后不存在长句（>8 字）——出现长句即视为长行散文，拒绝；
      2) 4-7 字句 >= 2；
      3) 4-7 字句占全部实句 >= 0.6（排挤偶发短句的散文）；
      4) 众数句长出现 >= 2 次（确保是"齐言"而非长短杂陈）。
    宁可漏判也不误判——汉字散文每句本就 4-7 字，比例法无法区分，故加上"无长句"硬闸。
    """
    # 叙述/对话标志：出现"曰：/云：/白："等说话动词者，是长行散文而非偈颂
    if re.search(r'(曰|云|告|答|白|言|語|問)\s*[：:]', text):
        return False, None
    t2 = text.replace('「','').replace('」','').replace('『','').replace('』','')
    sents = [clean(x) for x in split_sentences(t2)]
    sents = [x for x in sents if x]
    if len(sents) < 2: return False, None
    lens = [len(x) for x in sents]
    if max(lens) > 8: return False, None          # 含长句 → 长行散文
    verse = [l for l in lens if 4 <= l <= 7]
    if len(verse) < 2: return False, None
    if len(verse) / len(lens) < 0.6: return False, None
    top_len, top_n = Counter(verse).most_common(1)[0]
    if top_n < 2: return False, None
    meter = {4:'四句偈',5:'五言',6:'六言',7:'七言'}.get(top_len,'偈颂')
    return True, meter

def para_is_gatha(text, after_header=False):
    """识别偈颂：
    仅在"上一段是明确偈头（而說偈言/說偈言/偈曰/而說頌曰等）"或"末尾总结偈"时，
    再用 is_verse_paragraph 做严格齐言校验，避免把偈后的长行散文一并吞入。
    """
    t = text.strip()
    if not t: return False, None
    if not after_header: return False, None
    return is_verse_paragraph(t)

def meter_of(text):
    t2 = text.replace('「','').replace('」','')
    sents = [clean(x) for x in split_sentences(t2)]
    sents = [x for x in sents if 4 <= len(x) <= 7]
    if not sents: return '偈颂'
    cnt = Counter(len(x) for x in sents)
    com = cnt.most_common(1)[0][0]
    return {4:'四句偈',5:'五言',6:'六言',7:'七言'}.get(com,'偈颂')

# ========== 三分划分 ==========
XU_CHAPTER_PAT = re.compile(r'(序$|序并序|并序$|後序$|傳序$|弘傳序$|御製序$|序文$|目錄$|贊$|製序$|序并)')
LIUTONG_CHAPTER_PAT = re.compile(r'(囑累人天|囑累品|付囑品|付法品|流通品|勸持品|法師功德品|普賢菩薩勸發品|囑累品第|流通分|付囑累|勸發品|付法藏)')

def split_kepan(chapters):
    n = len(chapters)
    if n == 0: return
    parts = ['正宗分']*n
    # 前连续序/目录/赞为序分
    for i,ch in enumerate(chapters):
        t = ch['chapter_title']
        if re.match(r'^卷\s*\d+$', t):
            # 首卷通常含"如是我闻"正式开经，归正宗分
            parts[i] = '正宗分'
        elif XU_CHAPTER_PAT.search(t) and '品' not in t:
            parts[i] = '序分'
        else:
            break
    # 末章跋/铭归流通
    if chapters:
        last_t = chapters[-1]['chapter_title']
        if re.search(r'(跋$|銘$|記$|後序$|後記$|後序|并序)$', last_t):
            parts[-1] = '流通分'
    for i in range(n-1,-1,-1):
        if LIUTONG_CHAPTER_PAT.search(chapters[i]['chapter_title']):
            parts[i] = '流通分'
        else:
            break
    for i,ch in enumerate(chapters):
        ch['part_of_kepan'] = parts[i]

def classify_section_type(ch_title):
    if re.search(r'(真言|陀羅尼|神咒)$', ch_title): return '咒语'
    if re.search(r'(偈|頌)$', ch_title) and '品' not in ch_title: return '偈颂'
    if re.search(r'(序$|序并序|并序$|後序$|傳序$|弘傳序$|御製序$|序文$)', ch_title): return '序文'
    if re.search(r'(跋$|銘$|記$)', ch_title): return '跋记'
    if re.search(r'(目錄|贊$)', ch_title): return '附录'
    if re.match(r'^卷\s*\d+$', ch_title): return '卷首'
    if '品' in ch_title: return '品'
    if re.match(r'^第[一二三四五六七八九十百零〇]+章', ch_title): return '章节'
    return '章节'

def build_sutra(sid):
    p = os.path.join(SUTRA_DIR, f'{sid}.json')
    if not os.path.exists(p): return None
    s = load_json(p)
    meta = meta_by_id.get(sid, {})
    title = s.get('title','')
    translator = s.get('translator','') or meta.get('translator','')
    category = s.get('category','') or meta.get('category','')
    vol = s.get('vol','') or meta.get('vol','')
    taisho = s.get('taisho') or meta.get('taisho') or sid.upper()
    if not taisho.startswith('T'):
        taisho = 'T'+taisho.zfill(4) if taisho.isdigit() else taisho
    mt = re.match(r'^T(\d+)$', taisho)
    canon_ref = ('T.'+mt.group(1).lstrip('0').zfill(3)) if mt else taisho
    juan_count = s.get('juan_count') or meta.get('juan_count',1) or 1
    chars = s.get('actual_char_count',0) or meta.get('chars',0)
    time_from = s.get('time_from') or meta.get('time_from')
    trans_place = s.get('translation_place') or meta.get('translation_place','')
    vehicle='大乘'; mode='显教'
    if any(k in category for k in ['阿含','本缘','毗昙']): vehicle='小乘'
    if '密教' in category: mode='密教'
    schools = list(cat2school.get(category,[])) if isinstance(cat2school,dict) else []
    if '法華' in title or '妙法蓮華' in title:
        if '天台宗' not in schools: schools.append('天台宗')
    if '華嚴' in title or '大方廣佛' in title:
        if '华严宗' not in schools: schools.append('华严宗')
    if '阿彌陀' in title or '無量壽' in title or '觀無量壽' in title:
        if '净土宗' not in schools: schools.append('净土宗')
    if '金剛頂' in title or '大日' in title or '陀羅尼集' in title or '蘇悉地' in title:
        if '密宗' not in schools: schools.append('密宗'); mode='密教'
    if '梵網' in title or '四分律' in title or '五分律' in title or '十誦律' in title:
        if '律宗' not in schools: schools.append('律宗')
    if '楞伽' in title or '唯識' in title or '成唯識' in title or '瑜伽師地' in title:
        if '唯识宗' not in schools: schools.append('唯识宗')
    if '中論' in title or '百論' in title or '十二門論' in title or '大智度' in title:
        if '三论宗' not in schools: schools.append('三论宗')
    if '壇經' in title or ('金剛' in title and '般若' in title) or '六祖' in title:
        if '禅宗' not in schools: schools.append('禅宗')

    raw = s.get('content', [])
    if isinstance(raw, str): raw = [{'chapter':'全文','text':raw}]
    chapters=[]; all_paras=[]; all_g=[]; all_m=[]
    pid=gid=mid=cid=0
    fig_ch=defaultdict(set); doc_ch=defaultdict(set)

    for ci,ch in enumerate(raw):
        cht = ch.get('chapter','') or f'第{ci+1}章'
        chtxt = ch.get('text','') or ''
        if not chtxt.strip() and not cht: continue
        cid_o = f'c{cid:03d}'; cid+=1
        stype = classify_section_type(cht)
        paras_raw = [p for p in re.split(r'\n+', chtxt) if p.strip()]
        pids=[]; gids=[]; mids=[]
        cfigs=set(); cdocs=set(); cchar=0
        in_gatha = False
        cur_gatha = None
        pending_gatha_header = False
        pending_mantra_intro = False

        for pi,p in enumerate(paras_raw):
            pt = p.strip()
            if not pt: continue
            # 段类型
            ptype = '长行'
            # 上一段是偈头（"爾時…而說偈言"）的情况
            after_gatha_header = False
            if pi > 0:
                prev_t = paras_raw[pi-1].strip()
                if GATHA_HEADER_RE.search(prev_t[-60:]) or (GATHA_HEADER_RE.search(prev_t) and len(prev_t) < 50):
                    after_gatha_header = True
            # 当前段就是偈头/咒头
            is_gatha_header = bool(GATHA_HEADER_RE.search(pt) and len(pt) < 60 and ('偈' in pt or '頌' in pt))
            is_mantra_intro = bool(re.search(r'(即說咒曰|咒曰|陀羅尼曰|神咒曰|而說咒曰|說是咒曰|明咒曰)\s*[：。]?$', pt))
            # 末尾总结偈（无偈头引导的四句总结）："如夢幻泡影…應作如是觀"
            is_summary_gatha = bool(re.search(r'(應作如是觀|應當如是觀|作如是觀)\s*[。！？」』」]*$', pt))
            if is_translator_line(pt) and pi<2:
                ptype = '译者署名'
                in_gatha = False; cur_gatha=None; pending_gatha_header = False; pending_mantra_intro = False
            elif is_gatha_header:
                ptype = '偈颂引导'
                pending_gatha_header = True
                in_gatha = False; cur_gatha=None; pending_mantra_intro = False
            elif is_mantra_intro:
                ptype = '咒语引导'
                pending_mantra_intro = True
                pending_gatha_header = False; in_gatha=False; cur_gatha=None
            else:
                is_m, mname = para_is_mantra(pt, is_after_mantra_intro=pending_mantra_intro, ch_title=cht)
                is_g, gmeter = para_is_gatha(pt, after_header=(after_gatha_header or pending_gatha_header or is_summary_gatha))
                if is_summary_gatha and not is_g:
                    is_g = True; gmeter = meter_of(pt) or '四句偈'
                # 上一段正在偈中：若本段仍以齐言句为主（≥2句 5/6/7言 且无长行起词）则续偈，否则停
                if in_gatha and not is_g:
                    if GATHA_STOP_RE.match(pt.lstrip('「『')):
                        in_gatha = False; cur_gatha=None
                    else:
                        is_g2, gm2 = is_verse_paragraph(pt)
                        prose_hits = sum(1 for h in ['佛言','白佛言','爾時','須菩提白','舍利弗白','佛告','合掌','偏袒右肩'] if h in pt)
                        if is_g2 and prose_hits == 0:
                            is_g = True; gmeter = gm2 or meter_of(pt)
                        else:
                            in_gatha = False; cur_gatha=None
                if is_m:
                    ptype='咒语'; in_gatha=False; cur_gatha=None
                    pending_gatha_header=False; pending_mantra_intro=False
                elif is_g:
                    ptype='偈颂'; in_gatha=True
                    pending_gatha_header=False; pending_mantra_intro=False
                else:
                    pending_gatha_header=False; pending_mantra_intro=False

            pid_o = f'p{pid:05d}'; pid+=1
            pids.append(pid_o); cchar += len(pt)
            gref=None; mref=None

            if ptype=='咒语':
                mid_o = f'm{mid:03d}'; mid+=1
                name = mname or '真言'
                if name=='真言':
                    mm = re.search(r'([\u4e00-\u9fff]{2,12})(真言|陀羅尼|神咒|咒)', cht)
                    if mm: name = mm.group(1)+mm.group(2)
                all_m.append({'id':mid_o,'chapter_id':cid_o,'name':name,
                              'text_preview':pt[:80],'char_count':len(pt)})
                mids.append(mid_o); mref=mid_o
            elif ptype=='偈颂':
                # 如果紧跟偈头且已有未完成的偈，追加
                is_continuation = bool(cur_gatha and (GATHA_HEADER_RE.search(paras_raw[pi-1][:60]) if pi>0 else False))
                # 或上一段就是偈
                if pi>0 and in_gatha and cur_gatha and not GATHA_HEADER_RE.search(pt[:60]):
                    # 续偈
                    all_g[-1]['char_count'] += len(pt)
                    prev_preview = all_g[-1]['text_preview']
                    all_g[-1]['text_preview'] = (prev_preview+pt[:20])[:150]
                    gref = cur_gatha
                else:
                    gid_o = f'g{gid:03d}'; gid+=1
                    all_g.append({'id':gid_o,'chapter_id':cid_o,'name':'偈颂',
                                  'meter':gmeter or meter_of(pt),
                                  'text_preview':pt[:80],'char_count':len(pt)})
                    gids.append(gid_o); gref=gid_o; cur_gatha=gid_o
            else:
                in_gatha=False; cur_gatha=None

            pfigs = find_persons(pt); pdocs = find_concepts(pt)
            cfigs |= pfigs; cdocs |= pdocs
            for f in pfigs: fig_ch[f].add(cid_o)
            for d in pdocs: doc_ch[d].add(cid_o)

            all_paras.append({
                'id':pid_o,'chapter_id':cid_o,'para_no':pi+1,
                'text_preview':pt[:80],'char_count':len(pt),
                'section_type':ptype,'gatha_id':gref,'mantra_id':mref,
                'figures':sorted(pfigs),'doctrines':sorted(pdocs)
            })
        chapters.append({
            'id':cid_o,'chapter_no':ci+1,'chapter_title':cht,
            'section_type':stype,'part_of_kepan':'正宗分',
            'paragraphs':pids,'gathas':gids,'mantras':mids,
            'figures':sorted(cfigs),'doctrines':sorted(cdocs),
            'char_count':cchar,
        })
    split_kepan(chapters)
    kepan={'序分':[],'正宗分':[],'流通分':[]}
    for ch in chapters: kepan[ch['part_of_kepan']].append(ch['id'])

    fm=[]
    for fid,chs in fig_ch.items():
        p=next((x for x in person_list if x['id']==fid),None)
        fm.append({'figure_id':fid,'name':p['name'] if p else fid,'chapters':sorted(chs),'mention_count':len(chs)})
    fm.sort(key=lambda x:-x['mention_count'])
    dm=[]
    for cid_d,chs in doc_ch.items():
        c=next((x for x in concept_list if x['id']==cid_d),None)
        dm.append({'concept_id':cid_d,'name':c['name'] if c else cid_d,'chapters':sorted(chs),'mention_count':len(chs)})
    dm.sort(key=lambda x:-x['mention_count'])

    parallels = sorted(set(para_by_id.get(sid,[])+para_by_id.get(taisho,[])+para_by_id.get(sid.lower(),[])) - {sid,taisho})

    return {
        'id':sid,'type':'Text','title':title,'title_zh':title,'translator':translator,
        'category':category,'volume':vol,'juan_count':juan_count,'actual_char_count':chars,
        'canon_ref':canon_ref,'taisho':taisho,'vehicle':vehicle,'mode':mode,
        'translation_place':trans_place,'time_from':time_from,
        'belongs_to_school':schools,'parallel_translations':parallels,
        'kepan':kepan,'chapters':chapters,'paragraphs':all_paras,
        'gathas':all_g,'mantras':all_m,
        'figure_mentions':fm,'doctrine_mentions':dm,
    }

def main():
    ids = [it['id'] for it in items]
    ok=0; fail=0; tg=tm=tp=tch=0; wg=wm=wf=wd=0
    for i,sid in enumerate(ids):
        try:
            inst = build_sutra(sid)
            if not inst: fail+=1; continue
            with open(os.path.join(OUT_DIR,f'{sid}.json'),'w',encoding='utf-8') as f:
                json.dump(inst,f,ensure_ascii=False)
            ok+=1; tp+=len(inst['paragraphs']); tch+=len(inst['chapters'])
            tg+=len(inst['gathas']); tm+=len(inst['mantras'])
            if inst['gathas']: wg+=1
            if inst['mantras']: wm+=1
            if inst['figure_mentions']: wf+=1
            if inst['doctrine_mentions']: wd+=1
        except Exception as e:
            fail+=1
            if fail<=3: print('FAIL',sid,e)
    print(f'成功 {ok} / 失败 {fail}')
    print(f'章节 {tch} | 段 {tp} | 偈 {tg} | 咒 {tm}')
    print(f'含偈 {wg} | 含咒 {wm} | 含人物 {wf} | 含佛理 {wd}')
    # manifest
    manifest={'meta':{'total':ok,'version':'1.0.0','generated_by':'build_all_instances.py v3'},
              'sutras':[],'stats':{'total_chapters':tch,'total_paragraphs':tp,
                'total_gathas':tg,'total_mantras':tm,'sutras_with_gathas':wg,
                'sutras_with_mantras':wm,'sutras_with_figures':wf,'sutras_with_doctrines':wd}}
    for it in items:
        sid=it['id']; fp=os.path.join(OUT_DIR,f'{sid}.json')
        if os.path.exists(fp):
            try:
                d=load_json(fp)
                manifest['sutras'].append({'id':sid,'title':it['title'],
                    'chapter_count':len(d['chapters']),'juan_count':d['juan_count'],
                    'char_count':d['actual_char_count'],'vehicle':d['vehicle'],
                    'mode':d['mode'],'translator':d['translator'],'category':d['category']})
            except: pass
    with open(os.path.join(OUT_DIR,'manifest.json'),'w',encoding='utf-8') as f:
        json.dump(manifest,f,ensure_ascii=False)
    print(f'manifest: {len(manifest["sutras"])}')

if __name__=='__main__':
    main()
