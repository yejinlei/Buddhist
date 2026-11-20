#!/usr/bin/env python3
"""为白话译文生成对应的经页 HTML"""
import json, os, re, html

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
PAGES = os.path.join(BASE, "pages")

TEMPLATE_HEAD = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>{tid} {title}</title>
<style>
body {{ max-width: 820px; margin: 2em auto; padding: 0 1em; font-family: "Noto Serif CJK SC", "Source Han Serif SC", serif; line-height: 1.8; color: #222; }}
h1 {{ text-align:center; font-size:1.6em; border-bottom:2px solid #8b0000; padding-bottom:0.5em; color:#8b0000; }}
.xiaobiaoti {{ font-weight:bold; color:#8b0000; font-size:1.1em; margin-top:1.5em; }}
.yijie {{ background:#f8f4f0; padding:0.8em 1em; margin:0.5em 0; border-left:3px solid #a0522d; }}
.zhengwen {{ text-indent:2em; margin:0.8em 0; white-space: pre-wrap; }}
.original {{ color:#666; font-size:0.9em; background:#fafafa; padding:0.6em; margin:0.5em 0; border-left:3px solid #ccc; white-space: pre-wrap; }}
hr {{ border:none; border-top:1px dashed #ccc; margin:2em 0; }}
.meta {{ text-align:center; color:#666; margin-bottom:2em; }}
</style>
</head><body>
<h1>{tid} 《{title}》</h1>
<div class="meta">{translator}</div>
"""

TEMPLATE_SEG = """<hr id="seg{i}">
<div class="xiaobiaoti">{xb}</div><div class="yijie"><strong>【义解】</strong> {yj}</div><div class="zhengwen">{zw}</div>
<details><summary>查看原文</summary><div class="original">{orig}</div></details>
"""

TEMPLATE_TAIL = "</body></html>"

def fmt_orig(s):
    return html.escape(s).replace('\n','<br>\n')

def split_modern(m):
    """返回 (小标题, 正文, 义解)"""
    m = m.strip()
    # 小标题
    tm = re.match(r'^【([^】]+)】\s*', m)
    if not tm:
        return ("", m, "")
    title = tm.group(1)
    rest = m[tm.end():].strip()
    # 找【义解】
    ym = re.search(r'【义解】\s*', rest)
    if not ym:
        return (title, rest, "")
    zhengwen = rest[:ym.start()].strip()
    yijie = rest[ym.end():].strip()
    return (title, zhengwen, yijie)

def build_page(tid):
    sutra_path = os.path.join(BASE, "sutras", tid+".json")
    trans_path = os.path.join(BASE, "data", "modern-translation", tid+".json")
    out_path = os.path.join(PAGES, tid+".html")
    
    sd = json.load(open(sutra_path, encoding='utf-8'))
    td = json.load(open(trans_path, encoding='utf-8'))
    title = td.get('title') or sd.get('title','')
    translator = td.get('translator') or sd.get('translator','')
    
    parts = [TEMPLATE_HEAD.format(tid=tid, title=html.escape(title), translator=html.escape(translator))]
    for i, seg in enumerate(td['translations']):
        orig = seg['original_preview']
        xb, zw, yj = split_modern(seg['modern'])
        parts.append(TEMPLATE_SEG.format(
            i=i,
            xb=html.escape('【'+xb+'】') if xb else "",
            yj=html.escape(yj),
            zw=html.escape(zw),
            orig=fmt_orig(orig),
        ))
    parts.append(TEMPLATE_TAIL)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(''.join(parts))
    return out_path

if __name__ == "__main__":
    import sys
    tids = sys.argv[1:] if len(sys.argv)>1 else ['t1239']
    for tid in tids:
        p = build_page(tid)
        print(f"  ✅ {p}")
