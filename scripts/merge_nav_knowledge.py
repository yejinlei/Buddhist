#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导航合并脚本：把全站导航栏中的 宗派判教 / 佛典译学 / 译传时间轴
三个入口合并为一个「佛学知识」下拉菜单。

- 桌面导航：悬停展开下拉（纯 CSS，样式在 css/custom.css 的 .nav-dropdown）
- 移动菜单：同一份下拉结构，由媒体查询在窄屏平铺为分组
- 正文中的锚点/JS 变量不受影响（仅处理导航容器内的链接）

处理范围：index.html 与 pages/*.html。
"""
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = [os.path.join(BASE, 'index.html')] + sorted(
    os.path.join(BASE, 'pages', f) for f in os.listdir(os.path.join(BASE, 'pages'))
    if f.endswith('.html')
)

# 三个入口的链接目标（支持 xxx.html 与 #xxx 两种写法）
TARGET = r'(?:\.\./)?(?:pages/)?(?:panjiao|translation|timeline)\.html|#(?:panjiao|translation|timeline)'
ANCHOR_RE = re.compile(
    r'<a\b[^>]*href="(?:' + TARGET + r')"[^>]*>[\s\S]*?</a>'
)

# 允许出现的中文标签（避免误伤正文其它链接）
ALLOWED_LABELS = {
    '宗派判教', '判教对比', '佛典译学', '译学本体', '译学',
    '译传时间轴', '时间轴',
}

# 移动菜单容器 id（需与桌面导航分开处理，各自生成一份下拉）
MOBILE_IDS = ['mobileMenu', 'mobile-menu', 'mobileNav']


def label_of(anchor_html):
    txt = re.sub(r'<[^>]+>', '', anchor_html)
    return txt.strip()


def make_dropdown(prefix, hover_cls, dark, active):
    """生成下拉菜单 HTML。prefix 为相对前缀（index.html 用 'pages/'）。"""
    if active:
        toggle_cls = ('text-gold font-bold' if dark else 'text-buddha-primary font-bold')
    else:
        toggle_cls = hover_cls
    menu_cls = 'nav-dropdown-menu' + (' nav-dropdown-menu--dark' if dark else '')
    return (
        '<div class="nav-dropdown">'
        f'<a href="javascript:void(0)" class="{toggle_cls} nav-dropdown-toggle"'
        ' role="button" aria-haspopup="true">佛学知识<span class="nav-caret">▾</span></a>'
        f'<div class="{menu_cls}">'
        f'<a href="{prefix}panjiao.html">宗派判教</a>'
        f'<a href="{prefix}translation.html">佛典译学</a>'
        f'<a href="{prefix}timeline.html">译传时间轴</a>'
        '</div></div>'
    )


def merge_in_region(region_text, dropdown_html):
    """把区域内的三个目标链接替换成一个下拉（第一个位置插入，其余删除）。"""
    matches = list(ANCHOR_RE.finditer(region_text))
    if not matches:
        return region_text, 0
    for m in matches:
        lb = label_of(m.group(0))
        if lb not in ALLOWED_LABELS:
            raise ValueError(f'发现未预期的链接标签：{lb!r} -> {m.group(0)[:80]}')
    # 从后往前删除，再在第一个位置插入
    out = region_text
    first = matches[0]
    for m in reversed(matches):
        out = out[:m.start()] + out[m.end():]
    return out[:first.start()] + dropdown_html + out[first.start():], len(matches)


def process_file(path, prefix, hover_cls, dark, active):
    with open(path, encoding='utf-8') as f:
        text = f.read()

    dropdown = make_dropdown(prefix, hover_cls, dark, active)

    # 1) 先抽取移动菜单块，用占位符替换，避免与桌面列表混在一起
    holders = {}

    def stash(m):
        key = f'\x00MOBILE{len(holders)}\x00'
        inner = m.group(0)
        new_inner, n = merge_in_region(inner, dropdown)
        holders[key] = new_inner
        return key

    for mid in MOBILE_IDS:
        pat = re.compile(r'<div id="' + mid + r'"[\s\S]*?</div>')
        text = pat.sub(stash, text)

    # 2) 处理其余（桌面）导航中的三个链接
    text, n_desktop = merge_in_region(text, dropdown)

    # 3) 还原移动菜单
    for key, val in holders.items():
        text = text.replace(key, val)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    return n_desktop, len(holders)


CONFIG = {
    'index.html': dict(prefix='pages/', hover_cls='hover:text-buddha-secondary', dark=True, active=False),
    'dict.html': dict(prefix='', hover_cls='text-stone-600 hover:text-amber-700', dark=False, active=False),
    'parallel.html': dict(prefix='', hover_cls='hover:text-gold', dark=True, active=False),
    'search.html': dict(prefix='', hover_cls='hover:text-gold', dark=True, active=False),
    'sutras.html': dict(prefix='', hover_cls='hover:text-gold', dark=True, active=False),
}
DEFAULT = dict(prefix='', hover_cls='hover:text-buddha-secondary', dark=False, active=False)


def main():
    total = 0
    for path in FILES:
        name = os.path.basename(path)
        if name == 'categories.html':
            continue  # 跳转页，无导航
        cfg = dict(CONFIG.get(name, DEFAULT))
        cfg['active'] = name in ('panjiao.html', 'translation.html', 'timeline.html')
        nd, nm = process_file(path, **cfg)
        total += nd
        print(f'{os.path.relpath(path, BASE):28s} 桌面导航替换 {nd} 处 / 移动菜单 {nm} 处')
    print(f'完成，共处理 {total} 个桌面导航。')


if __name__ == '__main__':
    sys.exit(main())
