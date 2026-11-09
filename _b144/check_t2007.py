# -*- coding: utf-8 -*-
import json, re
d = json.load(open('data/modern-translation/t2007.json'))
print('顶层keys:', list(d.keys()))
secs = d['translations']
print('段数:', len(secs))
bad = 0
for i, s in enumerate(secs):
    if set(s.keys()) != {'section', 'original_preview', 'modern'}:
        bad += 1
    if not s['modern'].startswith(s['section']):
        bad += 1
    if '【义解】' not in s['modern']:
        bad += 1
print('体例异常:', bad)
print('样例0 section:', secs[0]['section'])
print('样例0 op:', secs[0]['original_preview'][:40])
print('样例0 modern:', secs[0]['modern'][:110])
print('样例11 op:', secs[11]['original_preview'][:50])
print('样例11 modern:', secs[11]['modern'][:130])
half_marks = ['"', "'"]
hq = sum(1 for s in secs if any(m in s['modern'] for m in half_marks))
print('modern含半角引号段数:', hq)
o = json.load(open('sutras/t2007.json'))
ot = ''.join(''.join(c['text'].split()) for c in o['content'])
cat = ''.join(''.join(s['original_preview'].split()) for s in secs)
print('原文长:', len(ot), '拼接长:', len(cat), '连续子串:', cat in ot, '覆盖:%.4f' % (len(cat) / len(ot)))
print('title:', d['title'])
print('translator:', d['translator'])
print('mode:', d['mode'], '| sutraPath:', d['sutraPath'])
