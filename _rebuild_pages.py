#!/usr/bin/env python3
"""按线上原版样式(t0002.html)重建全部2043部经页。"""
import json, os, re, html
from pathlib import Path

ROOT = Path("/home/user/workspace/13511660557912876654/buddhist-ontology")
TRANS = ROOT / "data" / "modern-translation"
SUTRAS = ROOT / "sutras"
OUT = ROOT

CSS = """<style>
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
</style>"""

def esc(s):
    return html.escape(s or "", quote=False)

def parse_modern(m):
    """从modern字符串解析 (小标题, 正文, 义解)。格式：【小标题】正文【义解】义解"""
    if not m:
        return "", "", ""
    xbt = ""
    yj = ""
    body = m
    # 提取小标题
    m_xbt = re.match(r'^【([^】]+)】', body)
    if m_xbt:
        xbt = m_xbt.group(1).strip()
        body = body[m_xbt.end():]
    # 提取义解
    m_yj = re.search(r'【义解】(.*)$', body, re.S)
    if m_yj:
        yj = m_yj.group(1).strip()
        body = body[:m_yj.start()].strip()
    else:
        # 可能有 【义贯】 【释义】 等
        m_yj = re.search(r'【(?:义贯|释义|义理|要义|解说)】(.*)$', body, re.S)
        if m_yj:
            yj = m_yj.group(1).strip()
            body = body[:m_yj.start()].strip()
    return xbt, body, yj

def build_page(tid, title, author, segs):
    page_title = f"{tid} 《{title}》" if title and not title.startswith("《") else f"{tid} {title}"
    parts = []
    parts.append("<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>")
    parts.append(esc(page_title))
    parts.append("</title>\n")
    parts.append(CSS)
    parts.append("\n</head><body>\n")
    parts.append('<a class="back" href="pages/sutras.html">← 返回经目</a>\n')
    parts.append(f"<h1>{esc(page_title)}</h1>\n")
    if author:
        parts.append(f'<div class="meta">{esc(author)}</div>\n')
    for i, seg in enumerate(segs):
        parts.append(f'<hr id="seg{i}">')
        if seg["xbt"]:
            parts.append(f'<div class="xiaobiaoti">{esc(seg["xbt"])}</div>')
        if seg["yj"]:
            parts.append(f'<div class="yijie"><strong>【义解】</strong> {esc(seg["yj"])}</div>')
        if seg["zw"]:
            parts.append(f'<div class="zhengwen">{esc(seg["zw"])}</div>')
        if seg["orig"]:
            parts.append(f'<details><summary>查看原文</summary><div class="original">{esc(seg["orig"])}</div></details>')
    parts.append("\n</body></html>")
    return "".join(parts)

# 读取plan.json
with open(ROOT / "_b198" / "plan.json","r",encoding="utf-8") as f:
    plan = json.load(f)
title_map = {k: v.get("title","") for k,v in plan.items()}

# 从原文文件读作者
def find_author(tid):
    fp = SUTRAS / f"{tid}.txt"
    if not fp.exists():
        return ""
    try:
        with open(fp,"r",encoding="utf-8") as f:
            head = f.read(2000)
        # 找第一行含 譯/撰/集/造 的
        for line in head.split('\n')[:5]:
            line = line.strip()
            if re.search(r'(譯|撰|集|造|說)$', line) and 4 < len(line) < 80:
                # 去掉开头可能的==
                line = re.sub(r'^=+\s*SEG\s*\d+\s*=+\s*','', line)
                return line
    except:
        pass
    return ""

done = 0
errs = 0
for fn in sorted(os.listdir(TRANS)):
    if not fn.endswith(".json"):
        continue
    tid = fn[:-5]
    fp = TRANS / fn
    try:
        with open(fp,"r",encoding="utf-8") as f:
            data = json.load(f)
        title = data.get("title") or title_map.get(tid,"") or tid
        author = data.get("translator","") or find_author(tid)
        trans_list = data.get("translations", data.get("segments", []))
        segs = []
        for s in trans_list:
            m = s.get("modern","")
            orig = s.get("original_preview", s.get("original",""))
            xbt, zw, yj = parse_modern(m)
            segs.append({"xbt":xbt, "zw":zw, "yj":yj, "orig":orig})
        html_text = build_page(tid, title, author, segs)
        with open(OUT / f"{tid}.html","w",encoding="utf-8") as f:
            f.write(html_text)
        done += 1
    except Exception as e:
        errs += 1
        print(f"ERR {tid}: {e}")

print(f"done={done} errs={errs}")
with open(OUT/"t0002.html","r",encoding="utf-8") as f:
    t=f.read()
print('xiaobiaoti count:', t.count('class="xiaobiaoti"'))
print('yijie count:', t.count('class="yijie"'))
print('zhengwen count:', t.count('class="zhengwen"'))
print('original count:', t.count('class="original"'))
print('first hr seg0 ok:', 'id="seg0"' in t)
