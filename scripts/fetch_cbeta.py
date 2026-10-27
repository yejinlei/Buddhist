#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBETA 大正藏全文抓取器
数据源：CBETA 官方 TEI P5 XML（github.com/cbeta-org/xml-p5）
流程：列举册目录 -> 下载单经 XML -> 解析 TEI -> 按本拆分为独立 JSON
"""
import json, re, sys, time, urllib.request, urllib.error
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'sutras'
OUT.mkdir(exist_ok=True)
CACHE = Path('/tmp/cbeta_cache')
CACHE.mkdir(exist_ok=True)

RAW = 'https://raw.githubusercontent.com/cbeta-org/xml-p5/master'
API = 'https://api.github.com/repos/cbeta-org/xml-p5/contents'
META = 'https://cbdata.dila.edu.tw/stable/works'
NS = {'t': 'http://www.tei-c.org/ns/1.0', 'cb': 'http://www.cbeta.org/ns/1.0'}

def http(url, binary=False, retry=3):
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=60).read()
            return data if binary else data.decode('utf-8', 'ignore')
        except Exception as e:
            if i == retry - 1:
                raise
            time.sleep(2)

def list_volumes():
    """列举 T 藏全部册目录"""
    txt = http(API + '/T?ref=master')
    return [x['name'] for x in json.loads(txt) if x['type'] == 'dir']

def list_works(vol):
    """列举某册下全部经号 XML"""
    txt = http(f'{API}/T/{vol}?ref=master')
    return [x['name'] for x in json.loads(txt) if x['name'].endswith('.xml')]

def get_meta(work):
    """从 CBETA 元数据 API 取经目信息"""
    try:
        d = json.loads(http(f'{META}?work={work}'))
        r = d.get('results', [])
        return r[0] if r else None
    except Exception:
        return None

def clean(text):
    return re.sub(r'\s+', '', text or '')

def parse_tei(xml_text, work):
    """解析 TEI XML：提取元数据 + 按卷/品分章正文"""
    root = ET.fromstring(xml_text)
    # --- 元数据 ---
    ts = root.find('.//t:teiHeader//t:titleStmt', NS)
    title = ''
    if ts is not None:
        for t in ts.findall('t:title', NS):
            if t.get('{http://www.w3.org/XML/1998/namespace}lang') == 'zh-Hant' and t.get('level') == 'm':
                title = t.text or ''
                break
        if not title:
            for t in ts.findall('t:title', NS):
                if t.text and '大正' not in t.text and 'Taishō' not in t.text:
                    title = t.text
                    break
    author = ''
    a = ts.find('t:author', NS) if ts is not None else None
    if a is not None:
        author = ''.join(a.itertext()).strip()

    # --- 正文 ---
    body = root.find('.//t:text/t:body', NS)
    chapters = []
    if body is not None:
        cur_title = None
        buf = []
        def flush():
            if buf:
                txt = '\n'.join(p for p in buf if p.strip())
                if txt.strip():
                    chapters.append({'chapter': cur_title or '正文', 'text': txt})
                buf.clear()
        for elem in body.iter():
            tag = elem.tag.split('}')[-1]
            if tag == 'juan':
                flush()
                jn = elem.get('n') or ''
                cur_title = f'卷{jn}' if jn else '正文'
            elif tag == 'head':
                head_txt = clean(''.join(elem.itertext()))
                if head_txt and (not chapters or chapters[-1]['chapter'] != head_txt):
                    if chapters and chapters[-1]['text'] == '':
                        chapters[-1]['chapter'] = head_txt
                    else:
                        cur_title = head_txt
            elif tag == 'p':
                # 取段内文本（不含 app/note 校勘）
                parts = []
                for sub in elem.iter():
                    st = sub.tag.split('}')[-1]
                    if st in ('note', 'rdg', 'witness', 'app'):
                        continue
                    if sub.text:
                        parts.append(sub.text)
                    if sub.tail:
                        parts.append(sub.tail)
                p = clean(''.join(parts))
                if p:
                    buf.append(p)
        flush()
    if not chapters:
        return None
    return {'title': title, 'author': author, 'chapters': chapters}

def save(work, meta, parsed):
    out = {
        'id': work.lower(),
        'taisho': work,
        'title': parsed['title'] or (meta or {}).get('title', ''),
        'alt_title': (meta or {}).get('title', ''),
        'translator': parsed['author'] or (meta or {}).get('byline', ''),
        'creators': (meta or {}).get('creators', ''),
        'dynasty': (meta or {}).get('time_dynasty', ''),
        'time_from': (meta or {}).get('time_from'),
        'time_to': (meta or {}).get('time_to'),
        'places': [p.get('name') for p in (meta or {}).get('places', [])],
        'canon': (meta or {}).get('canon', 'T'),
        'vol': (meta or {}).get('vol', ''),
        'category': (meta or {}).get('category', ''),
        'juan': (meta or {}).get('juan', len(parsed['chapters'])),
        'chars': sum(len(c['text']) for c in parsed['chapters']),
        'content': parsed['chapters'],
    }
    fp = OUT / f'{work.lower()}.json'
    fp.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    return out

def fetch_work(xml_name, vol, with_meta=True):
    work = xml_name.replace('.xml', '')
    # 经号形如 T08n0251 -> T0251
    m = re.match(r'T(\d+)n(\d+[a-z]?)', work)
    if not m:
        return None
    sutra_no = 'T' + m.group(2)
    cache_fp = CACHE / f'{work}.xml'
    if cache_fp.exists():
        xml_text = cache_fp.read_text(encoding='utf-8')
    else:
        xml_text = http(f'{RAW}/T/{vol}/{xml_name}')
        cache_fp.write_text(xml_text, encoding='utf-8')
    parsed = parse_tei(xml_text, sutra_no)
    if not parsed:
        return None
    meta = get_meta(sutra_no) if with_meta else None
    return save(sutra_no, meta, parsed)

if __name__ == '__main__':
    vols = sys.argv[1:] or ['T08']
    total = 0
    for vol in vols:
        names = list_works(vol)
        print(f'== {vol}: {len(names)} 部 ==')
        for n in names:
            try:
                r = fetch_work(n, vol)
                if r:
                    total += 1
                    print(f'  ✓ {r["id"]} {r["title"]} {r["chars"]}字 {len(r["content"])}章')
            except Exception as e:
                print(f'  ✗ {n}: {e}')
            time.sleep(0.3)
    print(f'\n合计入库 {total} 部')
