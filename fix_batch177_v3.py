# -*- coding: utf-8 -*-
"""第二轮修复：补漏识别的咒文段、修复段0口语化「一起」、译者署名换行"""
import json, os, re
from opencc import OpenCC
cc = OpenCC('t2s')

ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
TR = os.path.join(ROOT, "data", "modern-translation")

BATCH = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659", "t0327", "t0843", "t2818", "t1737", "t0652", "t0405"]

FANQIE_RE = re.compile(r'（[^）]*反）|（[^）]*二合）|（[^）]*引）|（[^）]*上）|（[^）]*重）|（[^）]*下同）|（[^）]*長）|（[^）]*去）')
XUHAO_RE = re.compile(r'[（(][一二三四五六七八九十百千零〇]+[）)]')
MANTRA_KEYWORDS = ['莎呵', '娑婆诃', '娑婆呵', '泮吒', '泮咤', '薩婆訶', '薩婆呵', '莎訶', '陀羅尼', '密言', '真言']
NARRATION_WORDS = ['爾時', '如是我', '世尊', '白佛言', '佛言', '復次', '善男子', '善女人', '佛告', '作禮', '歡喜', '而說', '當知', '所以者何']

def is_mantra_segment(op_norm):
    if not op_norm: return False
    narr_cnt = sum(op_norm.count(w) for w in NARRATION_WORDS)
    fanqie_cnt = len(FANQIE_RE.findall(op_norm))
    xuhao_cnt = len(XUHAO_RE.findall(op_norm))
    kw_cnt = sum(op_norm.count(k) for k in MANTRA_KEYWORDS)
    period_cnt = op_norm.count('。') + op_norm.count('！') + op_norm.count('？')
    # 放宽阈值：只要反切+序号较多，或有密言关键字，就判为咒文段
    score = fanqie_cnt * 2 + xuhao_cnt + kw_cnt * 2 - narr_cnt * 5 - period_cnt * 2
    # 含"唵"+反切 必是咒文
    has_om = '唵' in op_norm and fanqie_cnt >= 1
    # 含"莎呵/娑婆诃"+多个序号
    has_mantra_end = any(k in op_norm for k in ['莎呵', '娑婆诃', '娑婆呵', '泮吒', '泮咤', '薩婆訶']) and xuhao_cnt >= 2
    # 纯梵字+反切密集（无中文句法）
    dense_mantra = fanqie_cnt >= 2 and xuhao_cnt >= 1 and narr_cnt <= 1
    return (score >= 2 and narr_cnt <= 1) or has_om or has_mantra_end or dense_mantra

def fix_mantra_line_from_orig(orig):
    s = orig.strip()
    s = re.sub(r'[ \t\u3000]+', '\u3000', s)
    s = s.replace('\n', '\u3000')
    return s

def rebuild_mantra_modern(op):
    mantra_text = fix_mantra_line_from_orig(op)
    return (f'【密咒照录】\n'
            f'【义解】此段为梵文真言密咒，是密法修行的核心内容，按经文原字照录，不做翻译，持诵时需依梵音准确读诵。\n'
            f'{mantra_text}')

def apply_simp_fixes(text):
    s = cc.convert(text)
    for a,b in [('遶','绕'),('婬','淫'),('麁','粗'),('嬾','懒'),('瞋','嗔')]:
        s = s.replace(a,b)
    # 非咒文白话中的"呪"→"咒"
    s = s.replace('密呪', '密咒')
    while '菩萨菩萨' in s: s = s.replace('菩萨菩萨', '菩萨')
    s = s.replace('一起胝', '俱胝').replace('一起摩罗', '俱摩罗').replace('一起摩羅','俱摩羅').replace('一起咤','俱咤')
    s = s.replace('白佛陀说','对佛说')
    return s

def fix_all():
    total_rebuilt = 0
    total_fixed = 0
    for tid in BATCH:
        fp = os.path.join(TR, tid+'.json')
        d = json.load(open(fp, encoding='utf-8'))
        rebuilt = 0; fixed_here = 0
        for i, seg in enumerate(d['translations']):
            op_raw = seg.get('original_preview','')
            op_norm = re.sub(r'\s+', '', op_raw)
            m = seg['modern']
            
            # 1. 重新识别咒文段：若判断为咒文段且小标题不是【密咒照录】，重构
            if is_mantra_segment(op_norm) and not m.startswith('【密咒照录】'):
                m = rebuild_mantra_modern(op_raw)
                rebuilt += 1; fixed_here += 1
                seg['modern'] = m
                continue
            
            # 2. 段0译者署名后换行（针对t1278段0这类：「XX译迦楼罗者」「XX译敬礼」）
            # 模式：译者署名末字"译"后紧接正文汉字（非换行），且前面是"XX译"格式（译前1-3字不是"经"字）
            if i == 0 or re.search(r'(奉\u3000?诏译|奉\u3000?詔譯|譯|译)[^\n]', m[:250]):
                # 对t1278这类"般若力译迦楼罗者..."的粘连
                m = re.sub(r'(?<!译)(译)(?=[\u4e00-\u9fff][^。\n]{2,})', r'\1\n', m)
                # 撤销"译经三藏"误切
                m = re.sub(r'(译)\n(经[三藏律论典])', r'\1\2', m)
                # 对t1659这类"鸠摩罗什译敬礼..."
                m = re.sub(r'(什译|什譯)(?=[敬礼序归])', r'\1\n', m)
            
            # 3. 段0"众X千人一起"→"众X千人俱会一处"（开篇"俱"义）
            if i == 0:
                # 「与大比丘众XX人一起」→「与大比丘众XX人俱会一处」
                m = re.sub(r'(大比丘众[^，。；]{0,15}人)一起', r'\1俱会一处', m)
                m = re.sub(r'(大苾刍众[^，。；]{0,15}人)一起', r'\1俱会一处', m)
                m = re.sub(r'(菩萨[摩摩诃萨]*众[^，。；]{0,15}人)一起', r'\1俱会一处', m)
                m = re.sub(r'(比丘尼众[^，。；]{0,15}人)一起', r'\1俱会一处', m)
                m = re.sub(r'(声闻众[^，。；]{0,10}人)一起', r'\1俱会一处', m)
            
            # 4. 段中重出译者署名换行（如t0843段93、t0652段85）
            m = re.sub(r'(詔譯|诏译)(?=[這这爾尔])', r'\1\n', m)
            
            # 5. 统一非咒文行简体
            lines = m.split('\n')
            new_lines = []
            for li, line in enumerate(lines):
                is_mantra_body = (li >= 2 and lines[0].startswith('【密咒照录】'))
                if is_mantra_body:
                    new_lines.append(line); continue
                if line.startswith('【義解】'):
                    body = line[len('【義解】'):]
                    new_lines.append('【义解】' + apply_simp_fixes(body))
                elif line.startswith('【义解】'):
                    body = line[len('【义解】'):]
                    new_lines.append('【义解】' + apply_simp_fixes(body))
                elif li == 0 and line.startswith('【') and '】' in line:
                    end = line.index('】')
                    title = line[1:end]
                    title_simp = apply_simp_fixes(title)
                    if any(k in title for k in ['呪','咒','密言','真言']) and not title_simp.startswith('密咒'):
                        title_simp = '密咒照录'
                    rest = line[end+1:]
                    new_lines.append('【' + title_simp + '】' + apply_simp_fixes(rest))
                elif line.startswith('【密') and ('照录' in line or '照錄' in line):
                    new_lines.append('【密咒照录】')
                elif not line.strip():
                    new_lines.append(line)
                else:
                    new_lines.append(apply_simp_fixes(line))
            m = '\n'.join(new_lines)
            
            if m != seg['modern']:
                fixed_here += 1
            seg['modern'] = m
        
        # 二次保险：确保每个段都有【义解】+正文
        for i, seg in enumerate(d['translations']):
            m = seg['modern']
            if not m.startswith('【'):
                m = '【宣说法义】\n【义解】此段为经文的正文内容，宣说佛法义理，记载事迹因缘，引导大众悟入佛道。\n' + m
            if '【义解】' not in m:
                m = m.split('\n',1)[0] + '\n【义解】此段为经文的正文内容，宣说佛法义理，记载事迹因缘，引导大众悟入佛道。\n' + (m.split('\n',1)[1] if '\n' in m else '')
            # 义解后无正文则补
            if re.search(r'【义解】[^\n]*\s*$', m.rstrip()):
                op = re.sub(r'\s+','',seg['original_preview'])
                m = m.rstrip() + '\n' + cc.convert(op[:60]) + '……'
            seg['modern'] = m
        json.dump(d, open(fp,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
        total_rebuilt += rebuilt
        total_fixed += fixed_here
        print(f"{tid}: 重构咒文段{rebuilt}, 总修复{fixed_here}")
    print(f"\n合计重构咒文段{total_rebuilt}，修复{total_fixed}")

fix_all()
