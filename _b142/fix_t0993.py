# -*- coding: utf-8 -*-
"""抢救 t0993《大雲經請雨品第六十四》：
   - 顶层补 mode/intro/sutraPath，去掉非标准 vol
   - 每段 modern 缺【义解】者，在首个【...】标题后插入【义解】
   - section = modern 首个【...】标题
   - original_preview 一字不动
"""
import json, re

TID = 't0993'
P = f'data/modern-translation/{TID}.json'
d = json.load(open(P, encoding='utf-8'))

INTRO = ('《大雲經請雨品第六十四》，北周天竺三藏闍那耶舍譯，一卷。此品為《大雲經》'
         '第六十四品，屬大乘祈雨法門。經以佛在難陀、跋難陀龍王宮摩尼德大雲輪藏寶樓閣為緣起，'
         '諸大龍王與其眷屬以香花、寶蓋、瓔珞、音樂廣作供養，發弘誓願，啟請如來說「大雲輪'
         '請雨法門」。佛先說慈心功德、佛名除患，次說「施安樂陀羅尼」根本咒及諸隨咒——'
         '依《大雲輪請雨經》儀式，誦此咒句、稱諸佛名，可令閻浮提普降甘雨、百穀滋茂，'
         '亦能除疫病、息災厄。全品以長行與陀羅尼咒句交織，咒句皆音譯照錄，'
         '並保留原書反切、引聲等音注。')

seg = d['translations']
for s in seg:
    m = s.get('modern', '')
    if '【义解】' not in m and '【義解】' not in m:
        mt = re.match(r'^(【[^】]+】)', m)
        if mt:
            m = mt.group(1) + '【义解】' + m[len(mt.group(1)):]
        else:
            m = '【陀罗尼照录】【义解】' + m
    s['modern'] = m
    mt = re.match(r'^(【[^】]+】)', m)
    s['section'] = mt.group(1) if mt else s.get('section', '')

out = {
    'id': TID,
    'title': d['title'],
    'translator': d['translator'],
    'mode': 'baihua',
    'intro': INTRO,
    'sutraPath': f'../sutras/{TID}.json',
    'translations': seg,
}
json.dump(out, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('t0993 已抢救：segs=%d' % len(seg))
