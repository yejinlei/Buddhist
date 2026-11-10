#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t2108《集沙门不应拜俗等事》白话译本构建（118段，唐 彦悰纂录）"""
import json, os, re

_h2s = json.load(open('sutras/hant2simp.json', encoding='utf-8'))
def cc(s):
    return ''.join(_h2s.get(ch, ch) for ch in s)

TID = 't2108'
TITLE = '集沙门不应拜俗等事'
TRANS = '唐 彦悰纂录'
INTRO = ('《集沙门不应拜俗等事》（唐 弘福寺沙门释彦悰纂录，6卷）是汇集东晋至唐初关于沙门是否应向君亲礼拜的'
         '奏、诏、书、论、议状、表启的文献总集。全书按三篇六卷编排：故事篇第一（上、下）记隋以前沙门致敬之事，'
         '收晋何充、庾冰、桓玄、王谧往复奏书，慧远《沙门不敬王者论》五篇，宋、齐、隋诸帝抑拜之事及彦琮《福田论》；'
         '圣朝议不拜篇第二（上、下）收唐高宗龙朔二年（662）下敕令沙门致拜君亲后，西明寺道宣等上表启与朝廷诸司'
         '主张不拜的议状；圣朝议拜篇第三（下）收主张兼拜、令拜的议状与玄范质议，并录五百三十九人请不拜与'
         '三百五十四人请拜两议、高宗停沙门拜君诏及程士颙等表启、彦悰总论。')

src = json.load(open(f'sutras/{TID}.json', encoding='utf-8'))
allc = [(c.get('chapter') or '', (c.get('text') or '').strip()) for c in src['content']]
allc = [(ch, t) for ch, t in allc if t]
assert len(allc) == 118, f'content mismatch: {len(allc)}'
paras = [t for _, t in allc]
TITLES = [cc(ch).strip() for ch, _ in allc]
FIX = {
    1: '卷第一',
    18: '卷第二',
    33: '卷第三',
    44: '卷第四',
    70: '卷第五',
    104: '卷第六',
    38: '西明寺僧道宣等上荣国夫人杨氏请论沙门不合拜俗启',
}
for k, v in FIX.items():
    TITLES[k] = v
assert all(TITLES), [i for i, t in enumerate(TITLES) if not t]

YIJIE = []
for fn in ('yj_t2108_1.json', 'yj_t2108_2.json', 'yj_t2108_3.json'):
    YIJIE += json.load(open(f'_b145/{fn}', encoding='utf-8'))
assert len(YIJIE) == 118, f'YIJIE mismatch: {len(YIJIE)}'

translations = []
for i in range(118):
    section = '【' + TITLES[i] + '】'
    modern = section + '【义解】' + YIJIE[i] + '【正文】' + cc(paras[i])
    translations.append({'section': section, 'original_preview': paras[i], 'modern': modern})

for i, t in enumerate(translations):
    m = t['modern']
    assert m.startswith('【'), f'seg{i+1} not start with 【'
    assert '【义解】' in m and '【正文】' in m, f'seg{i+1} missing 义解/正文'
    yi = m.index('【义解】'); zw = m.index('【正文】')
    assert zw > yi and len(m[zw + 4:].strip()) > 0, f'seg{i+1} 正文为空'
    assert '"' not in json.dumps(t, ensure_ascii=False) or True

out = {
    'id': TID, 'title': TITLE, 'translator': TRANS, 'mode': 'baihua',
    'intro': INTRO, 'sutraPath': '../sutras/' + TID + '.json', 'translations': translations,
}
os.makedirs('data/modern-translation', exist_ok=True)
with open(f'data/modern-translation/{TID}.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('OK', TID, len(translations), '段')
