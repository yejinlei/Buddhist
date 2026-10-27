#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBETA 大正藏全量全文抓取器
- 经目清单：/tmp/manifest_T.json（逐册列举结果）
- 全文源：jsdelivr CDN 优先，raw 备用
- 输出：sutras/{id}.json（每经独立文件）+ sutras/index.json
- 支持断点续抓（已存在文件跳过）
"""
import json, re, sys, time, urllib.request, os
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'sutras'
OUT.mkdir(exist_ok=True)
CACHE = Path('/tmp/cbeta_cache'); CACHE.mkdir(exist_ok=True)
MANIFEST = Path('/tmp/manifest_T.json')
META = 'https://cbdata.dila.edu.tw/stable/works'
CDN = 'https://cdn.jsdelivr.net/gh/cbeta-org/xml-p5@master'
RAW = 'https://raw.githubusercontent.com/cbeta-org/xml-p5/master'
NS = {'t': 'http://www.tei-c.org/ns/1.0', 'cb': 'http://www.cbeta.org/ns/1.0'}
FETCH_META = os.environ.get('FETCH_META', '0') == '1'

def http(url, timeout=120, retry=3):
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return urllib.request.urlopen(req, timeout=timeout).read()
        except Exception:
            if i == retry - 1: raise
            time.sleep(3)

def get_meta(work):
    try:
        d = json.loads(http(f'{META}?work={work}', timeout=30, retry=2))
        r = d.get('results', [])
        return r[0] if r else None
    except Exception:
        return None

def clean(t):
    return re.sub(r'\s+', '', t or '')

def parse_tei(xml_text):
    root = ET.fromstring(xml_text)
    ts = root.find('.//t:teiHeader//t:titleStmt', NS)
    title = ''
    if ts is not None:
        for t in ts.findall('t:title', NS):
            if t.get('{http://www.w3.org/XML/1998/namespace}lang') == 'zh-Hant' and t.get('level') == 'm':
                title = t.text or ''; break
        if not title:
            for t in ts.findall('t:title', NS):
                if t.text and '大正' not in t.text and 'Taishō' not in t.text:
                    title = t.text; break
    author = ''
    a = ts.find('t:author', NS) if ts is not None else None
    if a is not None:
        author = ''.join(a.itertext()).strip()
    body = root.find('.//t:text/t:body', NS)
    chapters = []
    if body is not None:
        cur = None; buf = []
        def flush():
            if buf:
                txt = '\n'.join(p for p in buf if p.strip())
                if txt.strip():
                    chapters.append({'chapter': cur or '正文', 'text': txt})
                buf.clear()
        for elem in body.iter():
            tag = elem.tag.split('}')[-1]
            if tag == 'juan':
                flush(); jn = elem.get('n') or ''
                cur = f'卷{jn}' if jn else '正文'
            elif tag == 'head':
                ht = clean(''.join(elem.itertext()))
                if ht:
                    cur = ht
            elif tag == 'p':
                parts = []
                for sub in elem.iter():
                    st = sub.tag.split('}')[-1]
                    if st in ('note', 'rdg', 'witness', 'app'): continue
                    if sub.text: parts.append(sub.text)
                    if sub.tail: parts.append(sub.tail)
                p = clean(''.join(parts))
                if p: buf.append(p)
        flush()
    if not chapters:
        return None
    return {'title': title, 'author': author, 'chapters': chapters}

def download_xml(xml_name, vol):
    cache = CACHE / xml_name
    if cache.exists() and cache.stat().st_size > 500:
        return cache.read_text(encoding='utf-8')
    for base in (CDN, RAW):
        for _ in range(3):
            try:
                data = http(f'{base}/T/{vol}/{xml_name}', timeout=150, retry=1)
                txt = data.decode('utf-8', 'ignore')
                ET.fromstring(txt)  # 校验完整性
                cache.write_text(txt, encoding='utf-8')
                return txt
            except Exception:
                time.sleep(2)
    return None

def process(xml_name, vol):
    m = re.match(r'T(\d+)n(\d+[a-z]?)', xml_name.replace('.xml', ''))
    if not m: return None
    work = 'T' + m.group(2)
    fp = OUT / f'{work.lower()}.json'
    if fp.exists() and fp.stat().st_size > 300:
        return 'skip'
    xml_text = download_xml(xml_name, vol)
    if not xml_text: return None
    parsed = parse_tei(xml_text)
    if not parsed: return None
    meta = get_meta(work) if FETCH_META else None
    out = {
        'id': work.lower(), 'taisho': work,
        'title': parsed['title'] or (meta or {}).get('title', ''),
        'translator': parsed['author'] or (meta or {}).get('byline', ''),
        'creators': (meta or {}).get('creators', ''),
        'dynasty': (meta or {}).get('time_dynasty', ''),
        'vol': (meta or {}).get('vol', vol),
        'category': (meta or {}).get('category', ''),
        'juan': (meta or {}).get('juan', len(parsed['chapters'])),
        'chars': sum(len(c['text']) for c in parsed['chapters']),
        'content': parsed['chapters'],
    }
    fp.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    return out

def main():
    man = json.loads(MANIFEST.read_text())
    vols = sys.argv[1:] or sorted(man.keys())
    ok = skip = fail = 0
    for vol in vols:
        names = man.get(vol, [])
        print(f'== {vol} ({len(names)}部) ==', flush=True)
        for n in names:
            try:
                r = process(n, vol)
                if r == 'skip': skip += 1
                elif r:
                    ok += 1
                    print(f'  ✓ {r["id"]} {r["title"][:20]} {r["chars"]}字', flush=True)
                else:
                    fail += 1
            except Exception as e:
                fail += 1
                print(f'  ✗ {n}: {e}', flush=True)
    print(f'\n新抓 {ok}  跳过 {skip}  失败 {fail}', flush=True)

if __name__ == '__main__':
    main()
