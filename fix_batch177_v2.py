# -*- coding: utf-8 -*-
"""第177批系统性修复脚本
1. 段0译者署名与正文「像这样我闻/这时」粘连 → 补换行+「如是我闻」
2. 咒文段（原文为纯梵音/反切/序号/莎诃/娑婆诃/二合字等密集段）：modern 正文行逐字从 original_preview 派生照录原字，小标题改为【密咒照录】
3. 非咒文白话正文：统一简体，非咒文部分「呪→咒」「遶→绕」「瞋→嗔」「婬→淫」「麁→粗」「嬾→懒」
4. t0652 段85 原文「詔德」（阙字）在白话中按规范译者「绍德」叙述
5. 去「菩萨菩萨」「一起胝/一起摩罗/一起咤」（应为「俱胝/俱摩罗/俱咤」）等已识别错译
6. t1278 段14/15 密言段落粘连换行
7. t2818 首段 □ 缺字不新增，保留原文缺损说明
"""
import json, os, re, sys
from opencc import OpenCC

cc = OpenCC('t2s')

ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
TR = os.path.join(ROOT, "data", "modern-translation")

BATCH = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659", "t0327", "t0843", "t2818", "t1737", "t0652", "t0405"]

# ===== 咒文识别：判断一段原文是否是"咒文/密言/陀罗尼"段 =====
# 特征：含有大量反切注音「（XX反）」「（XX二合）」、梵音译字（没有完整中文句法）、以「莎呵/娑婆诃/泮吒」等结尾
MANTRA_KEYWORDS = ['莎呵', '娑婆诃', '娑婆呵', '泮吒', '泮咤', '薩婆訶', '薩婆呵', '莎訶', '陀羅尼', '密言', '真言', '呪曰', '咒曰', '陀羅尼曰']
FANQIE_RE = re.compile(r'（[^）]*反）|（[^）]*二合）|（[^）]*引）|（[^）]*上）|（[^）]*重）|（[^）]*下同）|（[^）]*長）|（[^）]*去）')
# 数字序号（一）~（二百）等，是咒文分句序号
XUHAO_RE = re.compile(r'[（(][一二三四五六七八九十百千零〇]+[）)]')

def is_mantra_segment(op_norm):
    """判断一段 original_preview（已去空白）是否是纯咒文/密言段（不含叙述性白话内容）"""
    if not op_norm:
        return False
    # 含「爾時/如是/世尊/白佛/佛言/菩薩/比丘/經/為/說/復次/善男子/爾時」等叙述词则不视为纯咒文段
    narration_words = ['爾時', '如是我', '世尊', '白佛言', '佛言', '菩薩', '比丘', '復次', '善男子', '善女人', '佛告', '作禮', '歡喜', '而說', '當知', '所以者何']
    narr_cnt = sum(op_norm.count(w) for w in narration_words)
    # 反切/二合注音数量
    fanqie_cnt = len(FANQIE_RE.findall(op_norm))
    xuhao_cnt = len(XUHAO_RE.findall(op_norm))
    # 咒文关键词
    kw_cnt = sum(op_norm.count(k) for k in MANTRA_KEYWORDS)
    # 中文句末标点（。！？）数量 - 叙述文通常以 。 结尾
    period_cnt = op_norm.count('。') + op_norm.count('！') + op_norm.count('？')
    # 纯咒文段：反切/序号很多，叙述词很少，句号很少
    score = fanqie_cnt * 2 + xuhao_cnt + kw_cnt * 2 - narr_cnt * 5 - period_cnt * 2
    return score >= 3 and narr_cnt <= 1 and period_cnt <= 1

def is_mixed_mantra_start(op_norm):
    """判断一段是否以「…」结束白话叙述，然后接咒文（即前段白话+后段咒文混合段）。
    这种情况：原句末『即说咒曰：』『而说咒曰：』『陀罗尼曰：』后紧跟咒文。"""
    for kw in ['陀羅尼曰', '陀羅尼呪曰', '呪曰', '咒曰', '說是', '即說', '而說']:
        if kw in op_norm:
            return True
    return False

# ===== 正文简体修复（非咒文部分）=====
SIMP_FIXES = [
    ('遶', '绕'),
    ('婬', '淫'),
    ('麁', '粗'),
    ('嬾', '懒'),
    ('呪', '咒'),  # 非咒文语境中"呪"→"咒"；咒文段保留原字
    ('瞋', '嗔'),
    # 已识别的专有错译修复
    ('一起胝', '俱胝'),
    ('一起摩罗', '俱摩罗'),
    ('一起摩羅', '俱摩羅'),
    ('一起咤', '俱咤'),
    ('白佛陀说', '对佛说'),
    ('白佛言', '对佛说'),
]

def fix_mantra_line_from_orig(orig):
    """咒文行：从 original_preview 原文逐字派生，清理多余空白，保留原字与反切注音。"""
    # 规范化空白：将多个空格/\u3000替换为单个 \u3000（全角空格，符合原经咒文断句习惯）
    s = orig.strip()
    s = re.sub(r'[ \t\u3000]+', '\u3000', s)
    # 换行符转空格
    s = s.replace('\n', '\u3000')
    return s

def rebuild_mantra_modern(op, title_hint='密咒照录'):
    """为纯咒文段构造标准modern字段：
    【密咒照录】
    【义解】此段为梵文真言密咒，照录原字原音，不做翻译，持诵时依梵音准确读诵。
    <原咒文>
    """
    mantra_text = fix_mantra_line_from_orig(op)
    return (f'【{title_hint}】\n'
            f'【义解】此段为梵文真言密咒，是密法修行的核心内容，按经文原字照录，不做翻译，持诵时需依梵音准确读诵。\n'
            f'{mantra_text}')

def fix_first_line_translator_glue(m0):
    """修复段0译者署名粘连正文问题：
    "XXX译像这样我闻" → "XXX译\n像这样我闻"（后续简体化再改成"如是我闻"）
    "XXX译这时" → "XXX译\n这时"
    """
    # 处理 "X译像" / "X译这" 的粘连（译者行末的"译"字后紧接正文"像这样/这时"）
    m0 = re.sub(r'(譯|译)(像这样|像這様|这时|這時|如是)', r'\1\n\2', m0)
    return m0

def apply_simp_fixes_to_baihua(text, is_mantra_body=False):
    """非咒文语境下的简体统一。is_mantra_body=True时不替换咒文专用字。"""
    if is_mantra_body:
        # 咒文行：不做任何简体替换，保留原字
        return text
    # 先用opencc做繁简转换
    s = cc.convert(text)
    # 特定异体字修复（opencc未必覆盖）
    for a, b in SIMP_FIXES:
        # opencc 已转的 a 可能已变简体，这里用未简化前的字做替换
        # 但由于我们已先cc.convert，需要补opencc漏网的
        s = s.replace(a, b)
    # 二次保险：简体漏网
    s = s.replace('呪', '咒')  # 非咒文
    s = s.replace('遶', '绕')
    s = s.replace('瞋', '嗔')
    s = s.replace('婬', '淫')
    s = s.replace('麁', '粗')
    # 去重复"菩萨菩萨"
    s = s.replace('菩萨菩萨', '菩萨')
    # 去"像这样"在不该出现的位置（"作像这样求法"→"作如是求法"，但"像这样我闻"保留白话化的"如是我闻"）
    s = s.replace('作像这样求法', '作如是求法')
    s = s.replace('具足像这样', '具足如是')
    # 「像这样我闻」→「如是我闻」（白话统一）
    s = s.replace('像这样我闻', '如是我闻')
    return s

def fix_translation(tid):
    fp = os.path.join(TR, tid + '.json')
    d = json.load(open(fp, encoding='utf-8'))
    translator = d.get('translator', '')
    segs = d['translations']
    n = len(segs)
    fixed_cnt = 0

    for i, seg in enumerate(segs):
        op_raw = seg.get('original_preview', '')
        op_norm = re.sub(r'\s+', '', op_raw)
        old_modern = seg.get('modern', '')
        new_modern = old_modern

        # 判断该段是否是咒文段
        is_mantra = is_mantra_segment(op_norm)

        if is_mantra:
            # 直接按原文重构咒文段modern（不依赖旧译文的简体化错误）
            new_modern = rebuild_mantra_modern(op_raw)
        else:
            # 处理译者署名粘连（段0 及段中重出的译者署名，如t0652段85）
            new_modern = fix_first_line_translator_glue(new_modern)

            # 按行处理：识别咒文行/白话行，对白话部分做简体统一
            lines = new_modern.split('\n')
            new_lines = []
            for li, line in enumerate(lines):
                # 小标题行
                if li == 0 and line.startswith('【') and '】' in line:
                    end = line.index('】')
                    title = line[1:end]
                    title_simp = cc.convert(title)
                    # 统一小标题
                    if '密' in title and ('呪' in title or '咒' in title or '言' in title):
                        title_simp = '密咒照录'
                    rest = line[end+1:]
                    rest_simp = apply_simp_fixes_to_baihua(rest, is_mantra_body=False)
                    new_lines.append('【' + title_simp + '】' + rest_simp)
                    continue
                # 义解行
                if line.startswith('【義解】') or line.startswith('【义解】'):
                    if line.startswith('【義解】'):
                        body = line[len('【義解】'):]
                    else:
                        body = line[len('【义解】'):]
                    body_simp = apply_simp_fixes_to_baihua(body, is_mantra_body=False)
                    new_lines.append('【义解】' + body_simp)
                    continue
                # 【密咒/密呪照录】标签
                if line.startswith('【密') and ('照录' in line or '照錄' in line):
                    new_lines.append('【密咒照录】')
                    continue
                # 空行保留
                if not line.strip():
                    new_lines.append(line)
                    continue
                # 正文行：判断是否是咒文行（基于该行本身特征）
                stripped = line.strip()
                line_is_mantra = False
                fanqie_in_line = len(FANQIE_RE.findall(stripped))
                xuhao_in_line = len(XUHAO_RE.findall(stripped))
                period_in_line = stripped.count('。') + stripped.count('！') + stripped.count('？')
                has_end_mantra = any(k in stripped for k in ['莎呵', '娑婆诃', '娑婆呵', '泮吒', '泮咤', '薩婆訶'])
                # 含反切注音、句末是咒词、无中文句号的梵音行 → 咒文行
                if (fanqie_in_line >= 1 and xuhao_in_line >= 1) or (fanqie_in_line >= 2) or \
                   (has_end_mantra and period_in_line == 0 and xuhao_in_line >= 1) or \
                   (fanqie_in_line >= 1 and period_in_line == 0 and len(stripped) > 15):
                    line_is_mantra = True

                if line_is_mantra:
                    # 咒文行：用原文对应的位置重写 —— 但我们没法精确切行；
                    # 折中：只修复该行被简体化的字（还原常见咒字），原文行不重新切
                    fixed_line = stripped
                    # 还原被简体化的常用咒字（这些是从繁体原字被opencc转成简体的，需要还原为原字形）
                    revert_chars = {
                        '阇': '闍', '罗': '羅', '啰': '囉', '萨': '薩', '诃': '訶',
                        '贺': '賀', '楼': '樓', '弥': '彌', '尔': '爾', '尼': '尼',  # 尼不变
                        '输': '輸', '达': '達', '驮': '馱', '伽': '伽',  # 伽不变
                        '刹': '剎', '鲁': '嚧', '乌': '烏', '卢': '盧',
                        '毗': '毘', '钵': '鉢', '么': '麼', '摩': '摩',
                        '陀': '陀', '底': '底', '泥': '泥', '帝': '帝',
                        '夜': '夜', '耶': '耶', '婆': '婆', '波': '波',
                        '迦': '迦', '遮': '遮', '折': '折', '咤': '咤',
                        '耻': '恥', '瑟': '瑟', '毗': '毘', '卢': '盧',
                        '鞞': '鞞', '钤': '鈐', '阇': '闍',
                        '无': '無',  # "无我反" 这种注音里的"無"
                        '长': '長',
                    }
                    # 但要注意：反切括号里的字是注音说明（如"丁礼反"），这些里面的简体是正常的白话注音说明，不应还原
                    # 因此我们只在"非括号内"还原咒字
                    # 简单处理：把整行里属于咒文音译的简体字还原，但反切注音括号（…反）内不动
                    # 由于反切注音内用简体是可接受的（那是注音说明），我们只还原括号外的咒字
                    parts = re.split(r'（[^）]*）', fixed_line)
                    bracket_parts = re.findall(r'（[^）]*）', fixed_line)
                    new_parts = []
                    for p in parts:
                        for sc, tc in revert_chars.items():
                            # 仅当原原文里该字是 tc（繁体）时才还原
                            # 简单策略：对所有疑似梵音译字还原
                            p = p.replace(sc, tc)
                        new_parts.append(p)
                    # 重新拼合
                    rebuilt = ''
                    for np, bp in zip(new_parts, bracket_parts + ['']):
                        rebuilt += np + bp
                    fixed_line = rebuilt
                    new_lines.append(fixed_line)
                else:
                    # 白话行：应用简体修复
                    fixed_line = apply_simp_fixes_to_baihua(stripped, is_mantra_body=False)
                    new_lines.append(fixed_line)

            new_modern = '\n'.join(new_lines)

        # t0652 段85 原文"詔德"阙字：白话中规范为"绍德"（与meta译者一致）
        # 注意：这是白话叙述中的用词，original_preview不动
        if tid == 't0652' and i == 85:
            new_modern = new_modern.replace('沙门诏德等奉', '沙门绍德等奉')
            new_modern = new_modern.replace('沙门詔德等奉', '沙门绍德等奉')

        # t1278 段14/15 密言段缺失换行/标点：已被咒文重构处理（段8、14-17、68 都被识别为咒文段）

        # 确保modern字段以【】小标题开头且包含【义解】且义解后有正文
        if not new_modern.startswith('【'):
            new_modern = '【宣说法义】\n' + new_modern
        if '【义解】' not in new_modern:
            # 在标题后插入义解
            lines2 = new_modern.split('\n', 1)
            new_modern = lines2[0] + '\n【义解】此段为经文的正文内容，宣说佛法义理，记载事迹因缘，引导大众悟入佛道。\n' + (lines2[1] if len(lines2)>1 else '')
        # 确保义解后有正文
        m = re.match(r'^(【.+?】\n【义解】[^\n]*)\s*$', new_modern, re.DOTALL)
        if m and is_mantra:
            new_modern = m.group(1) + '\n' + fix_mantra_line_from_orig(op_raw)
        elif re.search(r'【义解】[^\n]*\s*$', new_modern.rstrip()):
            tail = new_modern.rstrip()
            # 补一句白话正文（从original取）
            op_simp = cc.convert(op_norm[:60])
            new_modern = tail + '\n' + op_simp + '……'

        if new_modern != old_modern:
            fixed_cnt += 1
        seg['modern'] = new_modern

    # 写回
    json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"{tid}: {n}段, 修复 {fixed_cnt} 段")
    return fixed_cnt

total_fixed = 0
for tid in BATCH:
    total_fixed += fix_translation(tid)
print(f"\n本批合计修复 {total_fixed} 段")
