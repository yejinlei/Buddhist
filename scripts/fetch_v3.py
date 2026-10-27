#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBETA 大正藏全量抓取器 v3 - 使用curl子进程下载更稳定
"""
import json, re, sys, time, subprocess, os
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'sutras'
OUT.mkdir(exist_ok=True)
CACHE = Path('/tmp/cbeta_cache'); CACHE.mkdir(exist_ok=True)
MANIFEST = Path('/tmp/manifest_T_full.json')
CDN = 'https://cdn.jsdelivr.net/gh/cbeta-org/xml-p5@master'
RAW = 'https://raw.githubusercontent.com/cbeta-org/xml-p5/master'
NS = {'t': 'http://www.tei-c.org/ns/1.0'}
LOG = ROOT / 'fetch_progress.log'

def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line+'\n')

def dl_curl(url, out_path, timeout=60):
    """用curl下载"""
    try:
        r = subprocess.run(
            ['curl', '-sSL', '--max-time', str(timeout), '--retry', '2', '-o', str(out_path), url],
            capture_output=True, timeout=timeout+10
        )
        return r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 500
    except Exception:
        return False

def clean(t):
    return re.sub(r'\s+', '', t or '')

def parse_tei(xml_text):
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return None
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
    if ts is not None:
        a = ts.find('t:author', NS)
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
                if ht and len(ht) < 60:
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
        return cache.read_text(encoding='utf-8', errors='ignore')
    for base in (CDN, RAW):
        url = f'{base}/T/{vol}/{xml_name}'
        tmp = cache.with_suffix('.tmp')
        if dl_curl(url, tmp, timeout=90):
            try:
                txt = tmp.read_text(encoding='utf-8', errors='ignore')
                ET.fromstring(txt)  # 校验
                tmp.rename(cache)
                return txt
            except Exception:
                tmp.unlink(missing_ok=True)
    return None

def build_index():
    items = []
    total_chars = 0
    for fp in sorted(OUT.glob('*.json')):
        if fp.name == 'index.json': continue
        try:
            d = json.loads(fp.read_text(encoding='utf-8'))
            items.append({
                'id': d.get('id'), 'taisho': d.get('taisho'),
                'title': d.get('title'), 'translator': d.get('translator'),
                'vol': d.get('vol'), 'juan': d.get('juan'),
                'chars': d.get('chars'),
            })
            total_chars += d.get('chars', 0)
        except Exception:
            pass
    (OUT/'index.json').write_text(json.dumps({
        'total': len(items), 'chars': total_chars, 'sutras': items
    }, ensure_ascii=False, indent=1), encoding='utf-8')
    return len(items), total_chars

def process(xml_name, vol):
    m = re.match(r'T(\d+)n(\d+[a-z]?)', xml_name.replace('.xml', ''))
    if not m: return 'skip'
    work = 'T' + m.group(2)
    fp = OUT / f'{work.lower()}.json'
    if fp.exists() and fp.stat().st_size > 300:
        return 'skip'
    xml_text = download_xml(xml_name, vol)
    if not xml_text: return 'notfound'
    parsed = parse_tei(xml_text)
    if not parsed: return 'noparse'
    out = {
        'id': work.lower(), 'taisho': work,
        'title': parsed['title'] or xml_name.replace('.xml',''),
        'translator': parsed['author'],
        'vol': vol,
        'juan': len(parsed['chapters']),
        'chars': sum(len(c['text']) for c in parsed['chapters']),
        'content': parsed['chapters'],
    }
    fp.write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
    return out

def main():
    man = json.loads(MANIFEST.read_text(encoding='utf-8'))
    vols = sys.argv[1:] or sorted(man.keys())
    ok = skip = fail = nf = 0
    start = time.time()
    # 初始清理旧的中文名json
    for old in ['amituo_jiumo','bada_renjue','fo_yijiao','jingang_jiumo',
                'puxian_xingyuan','sishi_erzhang','xinjing_fayue','xinjing_jiumo',
                'xinjing_xuanzang','yaoshi_xuanzang','yulan_pen','t0221']:
        op = OUT/f'{old}.json'
        if op.exists(): op.unlink()
    for vol in vols:
        names = man.get(vol, [])
        log(f'== {vol} ({len(names)}部) 开始 ==')
        for n in names:
            try:
                r = process(n, vol)
                if r == 'skip': skip += 1
                elif r == 'notfound': nf += 1
                elif r == 'noparse': fail += 1
                elif r:
                    ok += 1
                    log(f'  ✓ {r["id"]} 《{r["title"][:18]}》 {r["chars"]}字')
                else:
                    fail += 1
            except Exception as e:
                fail += 1
                log(f'  ✗ {n}: {e}')
            if (ok+skip) % 30 == 0:
                cnt, ch = build_index()
                log(f'  [索引更新] {cnt}部 {ch/10000:.1f}万字')
        cnt, ch = build_index()
        elapsed = time.time() - start
        log(f'== {vol} 完成 新抓{ok} 跳过{skip} 未找到{nf} 失败{fail} 累计{cnt}部{ch/10000:.1f}万字 用时{elapsed/60:.1f}分钟 ==')
    cnt, ch = build_index()
    log(f'全部完成: 共{cnt}部 {ch/10000:.1f}万字 用时{(time.time()-start)/60:.1f}分钟')

if __name__ == '__main__':
    main()
