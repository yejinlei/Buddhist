# -*- coding: utf-8 -*-
"""第三轮精细修复：二轮复核指出的所有问题"""
import json, os, re
from opencc import OpenCC
cc = OpenCC('t2s')

ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
TR = os.path.join(ROOT, "data", "modern-translation")
BATCH = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659", "t0327", "t0843", "t2818", "t1737", "t0652", "t0405"]

# 梵咒专用字：在引号「」内的咒文引文中需还原为繁体
# 仅在识别为咒文引用段（含"即说咒曰""咒曰""密言""真言"后接「」引咒）
def restore_mantra_chars_in_quotes(text):
    """将「」内咒文引用中的简体梵字还原为繁体，但反切括号（XX反）内是注音说明，保持简体"""
    # 找出所有「...」引用块
    def repl_quote(quote):
        # 还原常见梵音译简体字→繁体
        repl = {
            '罗': '羅', '啰': '囉', '阇': '闍', '萨': '薩', '诃': '訶',
            '贺': '賀', '楼': '樓', '弥': '彌', '输': '輸', '达': '達',
            '驮': '馱', '刹': '剎', '鲁': '嚧', '乌': '烏', '卢': '盧',
            '毗': '毘', '钵': '鉢', '么': '麼',
        }
        # 分括号内/括号外处理：括号（XX反）内不替换
        parts = re.split(r'(（[^）]*）)', quote)
        new_parts = []
        for p in parts:
            if p.startswith('（') and p.endswith('）'):
                new_parts.append(p)  # 反切注音括号保留
            else:
                for sc, tc in repl.items():
                    p = p.replace(sc, tc)
                new_parts.append(p)
        return ''.join(new_parts)
    # 匹配所有「...」（含跨行，遇到下一个「之前）
    # 逐对「」处理
    result = []
    i = 0
    while i < len(text):
        if text[i] == '「':
            # 找配对」
            j = text.find('」', i+1)
            if j < 0:
                result.append(text[i:]); break
            quote = text[i:j+1]
            result.append(repl_quote(quote))
            i = j+1
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)

def fix_translator_line(m):
    """段0译者署名换行修复"""
    # "天亲菩萨造后秦"→"天亲菩萨造\n后秦"（造论者与译时之间）
    m = re.sub(r'(菩薩造|菩萨造)(?=[前后晉魏晋秦梁唐宋元汉隋唐姚])', r'\1\n', m)
    m = re.sub(r'(菩萨造)(?=[前后秦魏晋梁唐宋元汉隋唐姚])', r'\1\n', m)
    # 已修复的"XX译"后换行
    m = re.sub(r'(?<!译)(译)(?=[迦敬这如像一佛爾尔]|善男子|善女人)', r'\1\n', m)
    m = re.sub(r'(译)\n(经[三藏律论典])', r'\1\2', m)
    return m

def fix_ju_misconvert(m):
    """修复「俱」被opencc/简体转换连带误伤的情况：
    - 「一起力迦」→「俱力迦」（俱力迦罗？山/龙王名）
    - 「千光一起起」→「千光俱起」
    - 「一起致」→「俱致」（梵音koti，俱致=千万）
    - 「一起传」→看上下文再定
    - 不应把"俱会一处"回退
    """
    m = m.replace('一起致', '俱致')
    m = m.replace('一起胝', '俱胝')
    m = m.replace('一起摩罗', '俱摩罗').replace('一起摩羅', '俱摩羅')
    m = m.replace('一起力迦', '俱力迦')
    m = m.replace('千光一起起', '千光俱起')
    m = m.replace('一起时起', '俱时起')
    return m

def fix_xiangzheyang(text):
    """减少「像这样」的过度使用：
    - 句首「像这样」→「如是」「如此」
    - 「亦复像这样」→「亦复如是」
    - 「亦像这样」→「亦复如是」
    - 「像这样像这样」→「如是如是」
    - 「菩提亦像这样」→「菩提亦复如是」
    - 但保留对话中"不应像这样"这类口语（选择性替换）
    - 不强行全部替换，只替换明显是"如是"对译的组合
    """
    # 固定搭配优先
    text = text.replace('像这样像这样', '如是如是')
    text = text.replace('亦复像这样', '亦复如是')
    text = text.replace('亦像这样', '亦复如是')
    text = text.replace('皆亦像这样', '皆亦如是')
    text = text.replace('当复像这样', '当复如是')
    text = text.replace('应像这样', '应如是')
    text = text.replace('不应像这样', '不应如是')
    text = text.replace('能像这样', '能如是')
    text = text.replace('已像这样', '已如是')
    text = text.replace('已能像这样', '已能如是')
    # "X亦像这样" → "X亦如是"（X是名词/佛语）
    text = re.sub(r'([^\n「」、，。；：]{1,6})亦像这样', r'\1亦如是', text)
    # "像这样X平等故" → "如是X平等故"
    text = re.sub(r'像这样([^像，。；]{1,8}故)', r'如是\1', text)
    # "像这样X" 句首（非引号内）→「如是」
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        # 行首"像这样" → "如是"（如果后面是完整陈述句）
        if line.startswith('像这样') and len(line) > 6:
            line = '如是' + line[3:]
        new_lines.append(line)
    text = '\n'.join(new_lines)
    return text

def fix_all():
    total = 0
    for tid in BATCH:
        fp = os.path.join(TR, tid+'.json')
        d = json.load(open(fp, encoding='utf-8'))
        fixed = 0
        for i, seg in enumerate(d['translations']):
            op_raw = seg.get('original_preview', '')
            op_norm = re.sub(r'\s+', '', op_raw)
            m = seg['modern']
            orig = m
            
            # 段0特殊处理
            if i == 0:
                m = fix_translator_line(m)
            
            # 段中重出译者署名（如t0843段93/130，t0652段85）
            m = re.sub(r'(詔譯|诏译)(?=[這这爾尔])', r'\1\n', m)
            
            # "俱"字误改修复
            m = fix_ju_misconvert(m)
            
            # t1185b/t1154 等混合段（叙述+引咒）：对「」内咒文引用还原梵字繁体
            # 识别：含「呪曰」「咒曰」「即說呪曰」「即说咒曰」「真言曰」「密言曰」的段
            has_intro = bool(re.search(r'(呪曰|咒曰|陀羅尼曰|陀罗尼曰|真言曰|密言曰|即說|即说)', m))
            if has_intro or '【密咒照录】' in m:
                # 仅对正文行（非标题/义解行）的「」引用还原
                lines = m.split('\n')
                new_lines = []
                for li, line in enumerate(lines):
                    if li <= 1:  # 标题和义解行不处理
                        new_lines.append(line); continue
                    if line.startswith('【'):
                        new_lines.append(line); continue
                    # 正文行，对「」内做梵字还原
                    new_lines.append(restore_mantra_chars_in_quotes(line))
                m = '\n'.join(new_lines)
            
            # "像这样"过多问题（针对t0818等）
            if tid in ['t0818', 't0843', 't1659', 't0652']:
                m = fix_xiangzheyang(m)
            
            # t0405段99 "一起致悉𭓺栗底" → "俱致悉𭓺栗底"（已通过fix_ju_misconvert处理）
            
            # t0818 特殊错字（根据A路复核指出）：检查"仁者您者""大姊你妹"
            # 这些看起来像误OCR/翻译问题，先检查
            if tid == 't0818':
                m = m.replace('仁者您者', '仁者')
                m = m.replace('大姊你妹', '大姊')
                m = m.replace('没有的。', '不也。')  # 原文"不也"否定答语
            
            # t0843段130末尾 "像这样受持" → "如是受持"（前面已处理）
            # 末段截断：检查末尾是否完整
            if tid == 't0843' and i == len(d['translations'])-1:
                if m.rstrip().endswith('心善解……') or m.rstrip().endswith('……'):
                    # 补全末段
                    m = m.rstrip().rstrip('……')
                    if not m.endswith('。'):
                        m += '脱，信受奉行。'
                    else:
                        m += '\n佛说此经已，大众闻佛所说，皆大欢喜，信受奉行。'
            
            # t1278段43 咒文断行错误：检查"诃凡欲伏毒"
            # （若存在则是咒末"娑嚩訶"后接正文"凡欲..."需要换行/空格）
            if tid == 't1278':
                m = re.sub(r'([莎娑][嚩婆][訶诃])凡', r'\1\n凡', m)
            
            # 最终简体一致性（非咒文行）
            lines = m.split('\n')
            new_lines = []
            for li, line in enumerate(lines):
                is_mantra_body = (li >= 2 and lines[0].startswith('【密咒照录】'))
                if is_mantra_body:
                    new_lines.append(line); continue
                if line.startswith('【義解】'):
                    new_lines.append('【义解】' + cc.convert(line[len('【義解】'):]))
                elif line.startswith('【义解】'):
                    new_lines.append(line)
                elif li == 0 and line.startswith('【') and '】' in line:
                    new_lines.append(line)  # 标题已处理过
                else:
                    # 非咒文正文行做简体统一
                    s = cc.convert(line)
                    for a,b in [('遶','绕'),('婬','淫'),('麁','粗'),('嬾','懒'),('瞋','嗔'),('呪','咒')]:
                        s = s.replace(a,b)
                    while '菩萨菩萨' in s: s = s.replace('菩萨菩萨','菩萨')
                    new_lines.append(s)
            m = '\n'.join(new_lines)
            
            if m != orig:
                fixed += 1
            seg['modern'] = m
        json.dump(d, open(fp,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
        total += fixed
        print(f"{tid}: 修复{fixed}段")
    print(f"\n合计修复 {total} 段")

fix_all()
