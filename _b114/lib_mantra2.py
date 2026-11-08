# -*- coding: utf-8 -*-
"""第108批共享构建库（无引号咒文变体）。
与 lib_mantra 相同，但支持「种子词后直接裸写音译咒文（无「」包裹）」的经文：
对每个种子位置，从其后的第一个非空白字符起，取到下一个标点/换行前，作为咒文块。
用法：
    from lib_mantra2 import build
    build('t1919', TITLES, TPL, seeds=('呪曰：',), intro=INTRO)
"""
import json, re, os

def load_task(tid):
    return json.load(open(f'data/baihua-tasks/{tid}.json', encoding='utf-8'))

STOP = set('。！？；：，、\n\r「」『』（）()　 ')

def build(tid, titles, tpl, seeds=('呪曰：',), intro=''):
    task = load_task(tid)
    texts = [t['original_preview'] for t in task['translations']]
    full = ''; ranges = []
    for t in texts:
        a = len(full); full += t; ranges.append((a, len(full)))

    flag = [False]*len(full)
    for seed in seeds:
        pos = 0
        while True:
            k = full.find(seed, pos)
            if k < 0: break
            a = k + len(seed)
            while a < len(full) and full[a] in '：: \n\r\t　': a += 1
            b = a
            while b < len(full) and full[b] not in STOP: b += 1
            for x in range(a, b): flag[x] = True
            pos = b if b > k else k+1

    def chunks(a, b):
        out = []; cur = []; i = a
        while i < b:
            if flag[i]:
                c = full[i]
                if c == '（':
                    j = i+1
                    while j < b and full[j] != '）': j += 1
                    i = j+1; continue
                if c not in '「」『』\n':
                    if not c.isspace(): cur.append(c)
                i += 1
            else:
                if cur: out.append(re.sub(r'\s+', '', ''.join(cur))); cur = []
                i += 1
        if cur: out.append(re.sub(r'\s+', '', ''.join(cur)))
        return out

    MODS = []
    for i, (a, b) in enumerate(ranges):
        body = tpl[i]
        ch = chunks(a, b)
        assert body.count('{@}') == len(ch), (i, body.count('{@}'), len(ch), ch)
        for c in ch:
            body = body.replace('{@}', '⟪%s⟫' % c, 1)
        assert '{@}' not in body, i
        MODS.append("【%s】【义解】%s" % (titles[i], body))

    assert len(titles) == len(task['translations']), (len(titles), len(task['translations']))
    trans = []
    for i, mod in enumerate(MODS):
        m = re.match(r'(【[^】]+】)', mod); sec = m.group(1) if m else f"【段{i+1}】"
        trans.append({"section": sec, "original_preview": task['translations'][i]['original_preview'], "modern": mod})
    out = {"id": tid, "title": task['title'], "translator": task['translator'],
           "vol": task.get('vol', ''), "intro": intro, "translations": trans}
    json.dump(out, open(f'data/modern-translation/{tid}.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    return len(trans)
