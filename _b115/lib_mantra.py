# -*- coding: utf-8 -*-
"""第105批共享构建库：咒文由原文程序化派生，导出 {//} 占位后替换为 ⟪...⟫。
用法（在各 build_tXXXX.py 中）：
    from lib_mantra import build
    build('t0886', TITLES, TPL, seeds=('大明曰：',), intro=INTRO)
"""
import json, re, os

def load_task(tid):
    return json.load(open(f'data/baihua-tasks/{tid}.json', encoding='utf-8'))

def build(tid, titles, tpl, seeds=('真言曰：',), intro=''):
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
            a = full.find('「', k)
            if a < 0: break
            e1 = full.find('」', a+1)
            e2 = full.find('』', a+1)
            b1 = len(full)
            for e in (e1, e2):
                if e >= 0: b1 = min(b1, e+1)
            b2 = len(full); j = a+1
            while True:
                j = full.find('「', j)
                if j < 0: break
                if '\n' in full[a:j]: b2 = j; break
                j += 1
            b = min(b1, b2)
            for x in range(a, b): flag[x] = True
            pos = b

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
