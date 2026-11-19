#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量生成2043部已译佛经的经页HTML，并更新sutras.html加上（译）标记。"""
import os, re, json, html, sys

BASE = '/home/user/workspace/13511660557912876654/buddhist-ontology'
MT = os.path.join(BASE, 'data/modern-translation')
SUTRAS_HTML = os.path.join(BASE, 'sutras.html')
PAGES_SUTRAS = os.path.join(BASE, 'pages/sutras.html')

PAGE_CSS = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>__TITLE__</title>
<style>
body { max-width: 820px; margin: 2em auto; padding: 0 1em; font-family: "Noto Serif CJK SC", "Source Han Serif SC", serif; line-height: 1.8; color: #222; }
h1 { text-align:center; font-size:1.6em; border-bottom:2px solid #8b0000; padding-bottom:0.5em; color:#8b0000; }
.xiaobiaoti { font-weight:bold; color:#8b0000; font-size:1.1em; margin-top:1.5em; }
.yijie { background:#f8f4f0; padding:0.8em 1em; margin:0.5em 0; border-left:3px solid #a0522d; }
.zhengwen { text-indent:2em; margin:0.8em 0; }
.original { color:#666; font-size:0.9em; background:#fafafa; padding:0.6em; margin:0.5em 0; border-left:3px solid #ccc; white-space: pre-wrap; }
hr { border:none; border-top:1px dashed #ccc; margin:2em 0; }
.meta { text-align:center; color:#666; margin-bottom:2em; }
.back { display:inline-block; margin:1em 0; color:#8b0000; text-decoration:none; font-size:0.95em; }
.back:hover { text-decoration:underline; }
details { margin:0.5em 0; }
details summary { cursor:pointer; color:#888; font-size:0.9em; }
</style>
</head><body>
<a class="back" href="sutras.html">← 返回经目</a>
<h1>__ID__ 《__TITLE__》</h1>
<div class="meta">__TRANS__</div>
__BODY__
</body></html>
"""

SUTRAS_HEAD = """<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>佛经白话总目</title>
<style>
body { max-width: 1100px; margin: 2em auto; padding: 0 1em; font-family: "Noto Serif CJK SC", "Source Han Serif SC", serif; color:#222; background:#fbfaf7; }
h1 { text-align:center; color:#8b0000; border-bottom:2px solid #8b0000; padding-bottom:0.4em; }
.stat { text-align:center; color:#666; margin-bottom:1.5em; font-size:0.95em; }
.grid { column-count: 3; column-gap: 1em; }
@media (max-width: 900px) { .grid { column-count: 2; } }
@media (max-width: 600px) { .grid { column-count: 1; } }
.sutra-link { display:block; padding:6px 10px; margin:2px 0; color:#333; text-decoration:none; font-size:0.92em; border-bottom:1px dashed #eee; break-inside:avoid; }
.sutra-link:hover { background:#fff3e8; color:#8b0000; }
.yi { color:#c8350d; font-weight:bold; margin-left:4px; font-size:0.85em; }
</style>
</head><body>
<h1>佛经白话总目</h1>
<div class="stat">已完成白话精译 <strong style="color:#8b0000">__COUNT__</strong> 部；标记为 <span class="yi">（译）</span> 的即有白话译文。</div>
<div class="grid">
"""
SUTRAS_TAIL = """</div>
</body></html>"""


def html_escape(s):
    return html.escape(s, quote=False)


def parse_modern(modern):
    """通用解析：段首【标题】=小标题；【义解】/【正文】为固定分隔；
    其余【…】按原文保留为正文。任何形式的译文都能完整还原、不丢内容。"""
    titles, yj, zw = [], [], []
    segs = re.split(r'(【义解】|【正文】)', modern)
    head = segs[0]
    m = re.match(r'^\s*【([^】]{1,80})】', head)
    if m:
        tag = m.group(1)
        rest = head[m.end():]
        if tag == '小标题':
            if rest.strip():
                titles.append(rest.strip())
        else:
            titles.append(tag)
            if rest.strip():
                zw.append(rest.strip())
    else:
        if head.strip():
            zw.append(head.strip())
    for i in range(1, len(segs), 2):
        mk = segs[i]
        ct = (segs[i + 1] if i + 1 < len(segs) else '').strip()
        if mk == '【义解】':
            yj.append(ct)
        else:
            zw.append(ct)
    if not titles and not yj and not zw:
        zw = [modern.strip()]
    return (' · '.join(t for t in titles if t),
            '\n'.join(y for y in yj if y),
            '\n'.join(z for z in zw if z))


def render_segment(i, seg):
    """渲染一段：小标题 / 义解 / 正文 + 可折叠原文。"""
    modern = seg.get('modern', '') or ''
    original = seg.get('original_preview', '') or ''
    xbt, yj, zw = parse_modern(modern)

    parts = [f'<hr id="seg{i}">']
    if xbt:
        parts.append(f'<div class="xiaobiaoti">{html_escape(xbt)}</div>')
    if yj:
        yj_html = html_escape(yj).replace('\n', '<br>\n')
        parts.append(f'<div class="yijie"><strong>【义解】</strong> {yj_html}</div>')
    if zw:
        zw_html = html_escape(zw).replace('\n', '<br>\n')
        parts.append(f'<div class="zhengwen">{zw_html}</div>')
    if original:
        orig_html = html_escape(original)
        parts.append(f'<details><summary>查看原文</summary><div class="original">{orig_html}</div></details>')
    return ''.join(parts)


def render_page(tid, data):
    title = data.get('title', '') or ''
    trans = data.get('translator', '') or ''
    trans_html = html_escape(trans)
    title_html = html_escape(title)
    segs = data.get('translations', []) or []
    body_parts = []
    for i, seg in enumerate(segs):
        body_parts.append(render_segment(i, seg))
    body = '\n'.join(body_parts)

    # <title>用 tid+title；<h1> 用 《title》（不含 tid）
    page = PAGE_CSS
    page = page.replace('__TITLE__', html_escape(f"{tid} {title}"), 1)  # 仅替换第一个，即 <title>
    page = page.replace('__ID__', html_escape(tid))
    page = page.replace('__TITLE__', title_html, 1)  # 替换第二个，即 <h1>
    page = page.replace('__TRANS__', trans_html)
    page = page.replace('__BODY__', body)
    return page


def parse_links(sutras_text):
    """从旧sutras.html里解析每一条<a ...>tid 经名</a>，返回顺序列表 [(tid, title, full_link_text)]"""
    # 支持 ../ 前缀与无前缀两种
    pat = re.compile(r'<a\s+href="(\.\./)?(t\d+[a-z]?)\.html"\s+class="sutra-link"\s+data-id="(t\d+[a-z]?)">(.*?)</a>', re.DOTALL)
    items = []
    for m in pat.finditer(sutras_text):
        _, href_id, data_id, text = m.groups()
        # 去掉开头的 "t0007 "
        title = re.sub(r'^t\d+[a-z]?\s*', '', text).strip()
        items.append((data_id, title))
    return items


def main():
    # 1) 解析旧sutras.html的经目顺序
    old = open(SUTRAS_HTML, encoding='utf-8').read()
    items = parse_links(old)
    print(f'解析经目 {len(items)} 条')

    # 2) 收集哪些tid有译文
    translated = set()
    for fn in os.listdir(MT):
        m = re.match(r'^(t\d+[a-z]?)\.json$', fn)
        if m:
            translated.add(m.group(1))
    print(f'有译文 {len(translated)} 部')

    # 3) 为每一部有译文的经生成HTML
    ok = 0
    fail = []
    for tid in translated:
        json_path = os.path.join(MT, f'{tid}.json')
        try:
            data = json.load(open(json_path, encoding='utf-8'))
            page = render_page(tid, data)
            out = os.path.join(BASE, f'{tid}.html')
            with open(out, 'w', encoding='utf-8') as f:
                f.write(page)
            ok += 1
        except Exception as e:
            fail.append((tid, str(e)))
    print(f'经页生成完成：成功 {ok}，失败 {len(fail)}')
    if fail:
        for tid, err in fail[:20]:
            print('  FAIL', tid, err)

    # 4) 重建 sutras.html（根目录）：加（译）标记 + 完整头
    links = []
    for tid, title in items:
        yi = '<span class="yi">（译）</span>' if tid in translated else ''
        href = f'{tid}.html'
        # 显示文本：tid 经名
        text = f'{tid} {html_escape(title)}'
        links.append(f'<a href="{href}" class="sutra-link" data-id="{tid}">{text}{yi}</a>')

    new_sutras = SUTRAS_HEAD.replace('__COUNT__', str(len(translated))) + '\n'.join(links) + '\n' + SUTRAS_TAIL
    with open(SUTRAS_HTML, 'w', encoding='utf-8') as f:
        f.write(new_sutras)
    print(f'写入 {SUTRAS_HTML}')

    # 5) 重建 pages/sutras.html（相对路径 ../）
    links_pages = []
    for tid, title in items:
        yi = '<span class="yi">（译）</span>' if tid in translated else ''
        href = f'../{tid}.html'
        text = f'{tid} {html_escape(title)}'
        links_pages.append(f'<a href="{href}" class="sutra-link" data-id="{tid}">{text}{yi}</a>')
    new_pages = SUTRAS_HEAD.replace('__COUNT__', str(len(translated))) + '\n'.join(links_pages) + '\n' + SUTRAS_TAIL
    with open(PAGES_SUTRAS, 'w', encoding='utf-8') as f:
        f.write(new_pages)
    print(f'写入 {PAGES_SUTRAS}')

    print('DONE')


if __name__ == '__main__':
    main()
