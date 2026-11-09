# -*- coding: utf-8 -*-
"""为并发半成品补齐合规结构：顶层 7 字段、段级 section，并统一引号 “”→「」。
不动 original_preview。
"""
import json, re

INTROS = {
 't0338': ('《佛说离垢施女经》，西晋月氏国三藏竺法护译，一卷，属宝积部。经中佛在舍卫国祇树给孤独园，'
           '与千位阿罗汉比丘、万名菩萨俱。舍利弗、大目揵连、大迦叶、须菩提、阿难等八大弟子，'
           '与溥首童真（文殊）、光世音（观音）等八大菩萨，清晨持钵入城乞食，途中各发大愿。'
           '遇离垢施女，女与诸弟子、诸菩萨往复问答，论菩萨发心、净愿与诸法空寂、无生无作之义；'
           '其后离垢施女与五百梵志同诣佛所，佛为授记，梵志等亦得授记成佛。'
           '全经以问答机辩为体，主题为菩萨净愿、般若空观与莲华化生。'),
 't2052': ('《大唐故三藏玄奘法师行状》，唐冥详撰，一卷，属史传部。全文记述唐代高僧玄奘法师的家世、'
           '出家、西行求法、游历西域与印度、归国译经及入寂的始末，并附贤宝师感得本及校点尾记。'
           '内容涵盖法师俗姓陈、名祎、字玄奘，及西行途中诸国见闻、问学戒贤、曲女城无遮大会、'
           '赍归梵本、译场译经、示疾入灭等事迹，是研究玄奘生平与唐代佛教的重要传记文献。'),
}

for tid, intro in INTROS.items():
    p = f'data/modern-translation/{tid}.json'
    d = json.load(open(p, encoding='utf-8'))
    seg = d['translations']
    n = 0
    for s in seg:
        m = s['modern']
        if '“' in m or '”' in m:
            n += m.count('“') + m.count('”')
            m = m.replace('“', '「').replace('”', '」')
            s['modern'] = m
        mt = re.match(r'^(【[^】]+】)', m)
        s['section'] = mt.group(1) if mt else s.get('section', '')
    out = {'id': tid, 'title': d['title'], 'translator': d['translator'],
           'mode': 'baihua', 'intro': intro, 'sutraPath': f'../sutras/{tid}.json',
           'translations': seg}
    json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(tid, '已补全，引号改动', n, '段', len(seg))
