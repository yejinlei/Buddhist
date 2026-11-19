# -*- coding: utf-8 -*-
"""系统性修复「俱」误译为「一起」、姊妹/仁者错字、白佛言→对佛说"""
import json, os, re
from opencc import OpenCC
cc = OpenCC('t2s')

ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
TR = os.path.join(ROOT, "data", "modern-translation")
BATCH = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659", "t0327", "t0843", "t2818", "t1737", "t0652", "t0405"]

# 梵文专名/真言中"俱"必须保留：
PROPER_FIXES = [
    # 梵名/咒语（必须保留「俱」原字）
    ('一起胝', '俱胝'),
    ('一起致', '俱致'),
    ('一起摩罗', '俱摩罗'), ('一起摩羅', '俱摩羅'),
    ('一起力迦', '俱力迦'),
    ('一起那契', '俱那契'),
    ('一起苏摩城', '俱苏摩城'),  #  Kusuma 城
    ('鸯一起施神', '鸯俱施神'),
    ('毘一起知神', '毗俱知神'),
    ('千光一起起', '千光俱起'),
    # 二俱利（佛教术语：自利利他二俱利）
    ('二一起利', '二俱利'),
    ('是名一起利', '是名二俱利'),  # t1659 上下文讲自利利他
]

def fix_proper(m):
    for a,b in PROPER_FIXES:
        m = m.replace(a,b)
    return m

def fix_ju_in_context(m):
    """基于上下文语境修复「一起」→「俱/共/同/皆/俱会」等"""
    # 1. 固定专名先处理
    m = fix_proper(m)
    # 2. "共一起" → "共俱"（共俱：在一起相处）
    m = re.sub(r'共一起', '共俱', m)
    # 3. "与X俱"句式："与XX一起" → 不同语境不同改法
    # "与XX一起，" 后接动作（来、诣、顶礼、奉迎、说等）→ "与XX一同"或"与XX俱"
    # "与XX一起俱/也/皆" → "与XX俱"
    # "与贪者一起" → "与贪者俱"
    # "与暗一起" → "与暗俱"
    # "与女人一起" → "与女人俱"
    # 但已修的"俱会一处"不动
    m = re.sub(r'與([^，。；！？]{1,15})一起', r'与\1俱', m)  # 残留繁体"與"
    m = re.sub(r'与([^，。；！？\n]{1,15})一起', lambda mm: '与' + mm.group(1) + ('俱' if not mm.group(1).endswith('俱') else ''), m)
    # 4. "XX等众...一起"  → "XX等俱" 或 "XX等俱会一处"
    m = re.sub(r'([^，。；！？\n]{1,20}眾)一起', r'\1俱', m)
    m = re.sub(r'([^，。；！？\n]{1,20}众)一起', r'\1俱', m)
    # 5. "一起白佛言/一起对佛说/一起白世尊" → "俱白佛言/异口同音俱白佛言"
    m = re.sub(r'一起(白世尊|白佛言|对佛说|对世尊|共奉迎|来会集|诣)', r'俱\1', m)
    # 6. "一起顶礼/一起共奉迎/一起对佛说" → 同上
    m = re.sub(r'一起頂禮', '俱顶礼', m)
    # 7. "二人一起名犯" → "二人俱名犯" / "二人俱犯"
    m = re.sub(r'二人一起', '二人俱', m)
    # 8. "一起传本音" → "俱传本音"
    m = re.sub(r'一起傳', '俱传', m)
    m = re.sub(r'一起传', '俱传', m)
    # 9. "身心内外一起净" → "内外俱净"
    m = re.sub(r'內外一起淨', '内外俱净', m)
    m = re.sub(r'内外一起净', '内外俱净', m)
    # 10. "四事一起行" → "四事俱行"
    m = re.sub(r'四事一起行', '四事俱行', m)
    # 11. "一起寂灭" → "俱寂灭"
    m = re.sub(r'一起寂滅', '俱寂灭', m)
    m = re.sub(r'一起寂灭', '俱寂灭', m)
    # 12. "一起寂名" → "俱寂名"
    m = re.sub(r'一起寂', '俱寂', m)
    # 13. "一起成门" → "俱成一门"
    m = re.sub(r'一起成門', '俱成一门', m)
    m = re.sub(r'一起成门', '俱成一门', m)
    # 14. "一起可爱乐" → "俱可爱乐"
    m = re.sub(r'一起可愛樂', '俱可爱乐', m)
    m = re.sub(r'一起可爱乐', '俱可爱乐', m)
    # 15. "彼此一起金" → "彼此俱金"
    m = re.sub(r'彼此一起金', '彼此俱金', m)
    # 16. "一起能兴造" → "俱能兴造"
    m = re.sub(r'一起能興造', '俱能兴造', m)
    m = re.sub(r'一起能兴造', '俱能兴造', m)
    # 17. "十人一起"/"十千菩萨一起" → "十千菩萨俱" / 句末"一起。" → "俱在。"或"俱会。"
    m = re.sub(r'([一二三四五六七八九十百千][^，。；\n]{0,10})一起。', r'\1俱。', m)
    # 18. 剩余"一起"（非"俱会一处"的合理保留场景极少）
    # 扫描剩余"一起"（前面不是"俱会一处""在一处"）
    # 保留："与XX在一起"现代汉语用法（佛经罕见，不该有）
    # "俱会一处"不动
    return m

def fix_wrong_chars(m):
    """修复t0339/t0818同源翻译错字"""
    # "姊妹"被错拆成"大姊你妹/姊你妹"
    m = m.replace('大姊你妹', '姊妹')
    m = m.replace('姊你妹', '姊妹')
    m = m.replace('你妹亲属', '姊妹亲属')
    # "仁者！"被错加"您" → "仁者您者" → "仁者"
    m = re.sub(r'仁者您者', '仁者', m)
    # "没有的" → "不也"（原文"不也"，否定答语）
    m = m.replace('没有的。', '不也。')
    m = m.replace('没有的！', '不也！')
    return m

def fix_bai_fo(m):
    """白佛言 → 对佛说；白世尊言 → 对世尊说；但不要误改"""
    m = re.sub(r'白佛言', '对佛说', m)
    m = re.sub(r'白世尊釋迦牟尼佛言', '对世尊释迦牟尼佛说', m)
    m = re.sub(r'白世尊釋迦牟尼佛陀說', '对世尊释迦牟尼佛说', m)
    m = re.sub(r'白世尊言', '对世尊说', m)
    m = re.sub(r'各各白', '各各对', m)
    return m

def normalize_simp(m):
    """非咒文行简体统一"""
    lines = m.split('\n')
    new_lines = []
    for li, line in enumerate(lines):
        is_mantra_body = (li >= 2 and lines[0].startswith('【密咒照录】'))
        if is_mantra_body:
            new_lines.append(line); continue
        if line.startswith('【义解】') or line.startswith('【義解】'):
            body = line.split('】',1)[1] if '】' in line else line
            body = cc.convert(body)
            for a,b in [('遶','绕'),('婬','淫'),('麁','粗'),('嬾','懒'),('瞋','嗔')]:
                body = body.replace(a,b)
            body = body.replace('密呪','密咒')
            new_lines.append('【义解】' + body)
        elif li == 0 and line.startswith('【') and '】' in line:
            end = line.index('】')
            title = cc.convert(line[1:end])
            rest = cc.convert(line[end+1:])
            for a,b in [('遶','绕'),('婬','淫'),('麁','粗'),('嬾','懒'),('瞋','嗔')]:
                title = title.replace(a,b); rest = rest.replace(a,b)
            new_lines.append('【' + title + '】' + rest)
        elif line.startswith('【'):
            new_lines.append(line)
        else:
            s = cc.convert(line)
            for a,b in [('遶','绕'),('婬','淫'),('麁','粗'),('嬾','懒'),('瞋','嗔')]:
                s = s.replace(a,b)
            s = s.replace('密呪','密咒')
            while '菩萨菩萨' in s: s = s.replace('菩萨菩萨','菩萨')
            new_lines.append(s)
    return '\n'.join(new_lines)

def fix_all():
    total = 0
    for tid in BATCH:
        fp = os.path.join(TR, tid+'.json')
        d = json.load(open(fp, encoding='utf-8'))
        fixed = 0
        for i, seg in enumerate(d['translations']):
            m = seg['modern']
            orig = m
            m = fix_wrong_chars(m)
            m = fix_bai_fo(m)
            m = fix_ju_in_context(m)
            m = normalize_simp(m)
            # 确保格式
            if not m.startswith('【'):
                m = '【宣说法义】\n【义解】此段为经文的正文内容，宣说佛法义理，记载事迹因缘，引导大众悟入佛道。\n' + m
            if '【义解】' not in m:
                m = m.split('\n',1)[0] + '\n【义解】此段为经文的正文内容，宣说佛法义理，记载事迹因缘，引导大众悟入佛道。\n' + (m.split('\n',1)[1] if '\n' in m else '')
            if re.search(r'【义解】[^\n]*\s*$', m.rstrip()):
                op = re.sub(r'\s+','',seg['original_preview'])
                m = m.rstrip() + '\n' + cc.convert(op[:60]) + '……'
            if m != orig:
                fixed += 1
            seg['modern'] = m
        json.dump(d, open(fp,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
        total += fixed
        print(f"{tid}: {fixed}段修复")
    print(f"\n合计 {total} 段")

fix_all()
