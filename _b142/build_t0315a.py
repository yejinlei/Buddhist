# -*- coding: utf-8 -*-
"""重建 t0315a《佛說普門品經》（西晉 竺法護譯，105段）。
白话由 _b142/t0315a_mod{1,2,3}.txt 提供（每行一段，已含【标题】【义解】）；
original_preview 一字不动取自 data/baihua-tasks/t0315a.json。
"""
import json, re

TID = 't0315a'
tk = json.load(open(f'data/baihua-tasks/{TID}.json', encoding='utf-8'))
segs = tk['translations']

mods = []
for fn in ['t0315a_mod1', 't0315a_mod2', 't0315a_mod3']:
    with open(f'_b142/{fn}.txt', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.strip():
                mods.append(line)

assert len(mods) == len(segs), (len(mods), len(segs))

INTRO = ('《佛说普门品经》，西晋月氏国三藏竺法护译，一卷。全经以佛游王舍城灵鹫山为缘起，'
         '有离垢藏菩萨与九万二千菩萨从东方净行世界普华如来处而来，奉命受持「普门品」，'
         '来至忍界灵鹫山，化七宝莲花奉献能仁如来。溥首僮真（文殊师利）代众启请宣说，'
         '佛乃开演「普门内藏不可思议秘宝中心」之法。其纲要为「等游」——以平等观照周旋于'
         '色、声、香、味、细滑、心法、男女、僮女僮男、诸天、龙、鬼神、揵沓和、阿须伦、'
         '迦楼罗、真陀罗、摩睺勒，以及地狱、饿鬼、畜生、贪淫、瞋恚、愚痴、诸善德本、'
         '有为无为、乃至平等，一一明其如幻如化、虚无无实。其后又广说「内三尊六事」与'
         '「外三尊六事」治内病、外病之六度无极，宣说众多三昧名号，并以魔王波旬请佛不建立'
         '此经、佛答「经住无所住」为收束，末嘱阿难受持讽诵。全经长行与「等游」排比交错，'
         '主题为般若空观、平等一味与真本际。')

trans = []
for i, s in enumerate(segs):
    m = mods[i]
    mt = re.match(r'^(【[^】]+】)', m)
    trans.append({
        'section': mt.group(1) if mt else f'【段{i+1}】',
        'original_preview': s['original_preview'],
        'modern': m,
    })

out = {
    'id': TID,
    'title': tk['title'],
    'translator': tk['translator'],
    'mode': 'baihua',
    'intro': INTRO,
    'sutraPath': f'../sutras/{TID}.json',
    'translations': trans,
}
json.dump(out, open(f'data/modern-translation/{TID}.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('t0315a 已重建：segs=%d' % len(trans))
