# -*- coding: utf-8 -*-
"""修复 JSON 字符串值内部未转义的英文双引号（内容引用）。
策略：状态机扫描；字符串内的裸 " 若其后紧跟结构字符(, : } ])则视为结束引号，
否则视为内容引号，替换为成对的中文引号 “ ”。"""
import json, glob, os, sys

def fix_text(text):
    out = []
    i, n = 0, len(text)
    in_str = False
    toggle = False  # False -> 下一个内容引号用 “，True -> 用 ”
    while i < n:
        c = text[i]
        if not in_str:
            out.append(c)
            if c == '"':
                in_str = True
            i += 1
            continue
        # 在字符串内部
        if c == '\\':
            out.append(c)
            if i + 1 < n:
                out.append(text[i+1]); i += 2
            else:
                i += 1
            continue
        if c == '"':
            j = i + 1
            while j < n and text[j] in ' \t\r\n':
                j += 1
            nxt = text[j] if j < n else ''
            if nxt in ',:}]' or nxt == '':
                out.append('"'); in_str = False
            else:
                out.append('”' if toggle else '“')
                toggle = not toggle
            i += 1
            continue
        out.append(c); i += 1
    return ''.join(out)

def process(path):
    raw = open(path, encoding='utf-8').read()
    try:
        json.loads(raw); return 'SKIP-OK'
    except Exception:
        pass
    fixed = fix_text(raw)
    try:
        json.loads(fixed)
    except Exception as e:
        return 'FAIL ' + str(e)
    open(path, 'w', encoding='utf-8').write(fixed)
    return 'FIXED'

if __name__ == '__main__':
    pats = sys.argv[1:] or ['data/*.json']
    for pat in pats:
        for f in sorted(glob.glob(pat)):
            print(process(f), f)
