#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBETA 大正藏 全量流水线 v2（下载 -> 解析 -> 建索引）
修复：
  1) 解析遗漏偈颂(<l>)、标题外正文的问题 —— 递归提取所有块级元素文本
  2) 校勘注(note/rdg/app)正确剔除
  3) 缓存与清单落在工作目录，避免 /tmp 被清空
  4) 多 CDN 节点轮换 + 长超时 + 重试，低并发避免互相拖慢
用法:
  python3 scripts/pipeline_full.py download
  python3 scripts/pipeline_full.py parse
  python3 scripts/pipeline_full.py index
  python3 scripts/pipeline_full.py all
  python3 scripts/pipeline_full.py reparse      # 已入库的也重解析（修复旧数据）
"""
import json, re, sys, os, time, subprocess, uuid
from pathlib import Path
import concurrent.futures
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'sutras'
CACHE = ROOT / '.xmlcache'
CACHE.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

MANIFEST = CACHE / 'manifest_T.json'
META_CACHE = CACHE / 'meta_cache.json'
LOG = ROOT / 'fetch_progress.log'

BASES = [
    'https://testingcf.jsdelivr.net/gh/cbeta-org/xml-p5@master',
    'https://gcore.jsdelivr.net/gh/cbeta-org/xml-p5@master',
    'https://cdn.jsdelivr.net/gh/cbeta-org/xml-p5@master',
    'https://fastly.jsdelivr.net/gh/cbeta-org/xml-p5@master',
    'https://raw.githubusercontent.com/cbeta-org/xml-p5/master',
]
NS = {'t': 'http://www.tei-c.org/ns/1.0'}
META_API = 'https://cbdata.dila.edu.tw/stable/works?work='
SKIP_STRUCT = {'rdg', 'witness', 'app', 'witDetail', 'lem', 'rdgGrp',
        'lb', 'pb', 'anchor', 'space', 'milestone', 'caesura',
        'graphic', 'figure', 'docNumber'}

# 标题/正文块标签
HEAD_TAGS = {'head', 'jhead', 'mulu', 'jl_title', 'byline', 'jl_byline', 'fan'}
BLOCK_TAGS = {'p', 'l', 'item', 'list', 'lg', 'jl_juan', 'yin', 'zi', 'div', 't', 'tt', 'term'}


def is_skip_note(e):
    place = e.get('place') or e.get('{http://www.cbeta.org/ns/1.0}place') or ''
    resp = e.get('resp') or ''
    ntype = e.get('type') or e.get('{http://www.cbeta.org/ns/1.0}type') or ''
    corresp = e.get('corresp') or ''
    if resp or corresp:
        return True
    if ntype and ntype not in ('inline', 'comm'):
        return True
    return False


def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def clean(t):
    if not t:
        return ''
    t = t.replace('\u3000', ' ')
    t = re.sub(r'[ \t]+', '', t)
    t = re.sub(r'\n+', '\n', t)
    return t.strip()


# ---------------- 清单 ----------------
def build_manifest():
    url = 'https://api.github.com/repos/cbeta-org/xml-p5/git/trees/master?recursive=1'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = json.loads(urllib.request.urlopen(req, timeout=90).read().decode('utf-8', 'ignore'))
    man = {}
    for item in data.get('tree', []):
        p = item['path']
        if p.startswith('T/') and p.endswith('.xml') and p.count('/') == 2:
            _, vol, name = p.split('/')
            man.setdefault(vol, []).append(name)
    for v in man:
        man[v].sort()
    MANIFEST.write_text(json.dumps(man, ensure_ascii=False))
    return man


def load_manifest():
    if MANIFEST.exists():
        try:
            return json.loads(MANIFEST.read_text())
        except Exception:
            pass
    return build_manifest()


# ---------------- 下载 ----------------
def dl_one(item):
    vol, name = item
    dest = CACHE / name
    if dest.exists() and dest.stat().st_size > 500:
        return ('skip', name)
    tmp = CACHE / f'.{name}.{os.getpid()}.{uuid.uuid4().hex[:6]}.tmp'
    for _round in range(2):
        for base in BASES:
            url = f'{base}/T/{vol}/{name}'
            try:
                r = subprocess.run(
                    ['curl', '-sSL', '--fail', '--max-time', '120', '--connect-timeout', '20',
                     '-o', str(tmp), url],
                    capture_output=True, timeout=140)
                if r.returncode == 0 and tmp.exists() and tmp.stat().st_size > 500:
                    head = tmp.read_bytes()[:300]
                    if b'<?xml' in head or b'<TEI' in head:
                        tmp.rename(dest)
                        return ('ok', name)
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                if tmp.exists():
                    tmp.unlink()
            time.sleep(0.2)
    return ('fail', name)


def do_download(workers=3):
    man = load_manifest()
    total = sum(len(v) for v in man.values())
    todo = []
    for vol, names in man.items():
        for n in names:
            if not (CACHE / n).exists():
                todo.append((vol, n))
    log(f'待下载 {len(todo)} / 共 {total} 部')
    ok = fail = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(dl_one, it) for it in todo]
        for i, f in enumerate(concurrent.futures.as_completed(futs)):
            st, _ = f.result()
            if st == 'ok':
                ok += 1
            elif st == 'fail':
                fail += 1
            if (i + 1) % 25 == 0 or i == len(todo) - 1:
                log(f'下载 {i+1}/{len(todo)} 新增成功{ok} 失败{fail}')
    log(f'下载结束: 成功{ok} 失败{fail}')
    return ok, fail


# ---------------- 解析 ----------------
def extract(e):
    """递归提取元素全部文本，剔除校勘注子树"""
    parts = []
    if e.text:
        parts.append(e.text)
    for ch in e:
        tg = ch.tag.split('}')[-1]
        if tg in SKIP_STRUCT:
            pass
        elif tg == 'note' and is_skip_note(ch):
            pass
        else:
            parts.append(extract(ch))
        if ch.tail:
            parts.append(ch.tail)
    return ''.join(parts)


def parse_tei(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)
    except Exception:
        return None
    ts = root.find('.//t:teiHeader//t:titleStmt', NS)
    title = ''
    author = ''
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
        a = ts.find('t:author', NS)
        if a is not None:
            author = ''.join(a.itertext()).strip()

    body = root.find('.//t:text/t:body', NS)
    chapters = []
    if body is None:
        return None
    cur_title = None
    cur_parts = []

    def flush():
        if cur_parts:
            txt = '\n'.join(p for p in cur_parts if p)
            if txt.strip():
                chapters.append({'chapter': cur_title or '正文', 'text': txt})
        cur_parts.clear()

    def walk(e):
        nonlocal cur_title
        tg = e.tag.split('}')[-1]
        if tg in SKIP_STRUCT:
            return
        if tg == 'note' and is_skip_note(e):
            return
        if tg == 'juan':
            flush()
            n = clean(e.get('n') or '')
            cur_title = f'卷{n}' if n else (cur_title or '正文')
            for ch in e:
                walk(ch)
            return
        if tg in HEAD_TAGS:
            h = clean(extract(e))
            if h and len(h) < 120:
                flush()
                if tg in ('head', 'jhead', 'byline', 'jl_byline', 'fan'):
                    cur_title = h
                else:
                    cur_parts.append('【' + h + '】')
            for ch in e:
                walk(ch)
            return
        if tg in BLOCK_TAGS:
            t = clean(extract(e))
            if t:
                cur_parts.append(t)
            return
        for ch in e:
            walk(ch)
    walk(body)
    flush()
    if not chapters:
        return None
    return {'title': title, 'author': author, 'chapters': chapters}


def fetch_meta(work):
    for _ in range(3):
        try:
            req = urllib.request.Request(META_API + work, headers={'User-Agent': 'Mozilla/5.0'})
            d = json.loads(urllib.request.urlopen(req, timeout=20).read().decode('utf-8', 'ignore'))
            r = d.get('results', [])
            return r[0] if r else {}
        except Exception:
            time.sleep(1)
    return {}


def load_meta():
    if META_CACHE.exists():
        try:
            return json.loads(META_CACHE.read_text())
        except Exception:
            pass
    return {}


def work_short(name):
    m = re.match(r'T(\d+)n(\d+[a-z]?)', name)
    return ('T' + m.group(2)) if m else None


def do_parse(workers=4, force=False):
    man = load_manifest()
    # vol map: name -> vol
    volof = {}
    for vol, names in man.items():
        for n in names:
            volof[n] = vol
    files = sorted(CACHE.glob('[Tt]*.xml'))
    metas = load_meta()
    results = []

    def one(fp):
        work = fp.stem
        short = work_short(work)
        if not short:
            return None
        outfp = OUT / f'{short.lower()}.json'
        try:
            parsed = parse_tei(fp.read_bytes())
        except Exception:
            return None
        if not parsed:
            return None
        meta = metas.get(short)
        if not meta:
            meta = fetch_meta(short)
            metas[short] = meta
        title = parsed['title'] or meta.get('title', '') or work
        translator = meta.get('byline', '') or parsed['author']
        return (short, work, volof.get(work, ''), title, translator, parsed)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, res in enumerate(ex.map(one, files)):
            if res:
                results.append(res)
            if (i + 1) % 100 == 0:
                try:
                    META_CACHE.write_text(json.dumps(metas, ensure_ascii=False))
                except Exception:
                    pass
                log(f'解析 {i+1}/{len(files)}')

    index = []
    for short, work, vol, title, translator, parsed in results:
        content = parsed['chapters']
        out = {
            'id': short.lower(),
            'taisho': short,
            'title': title,
            'translator': translator,
            'vol': vol,
            'juan': len(content),
            'chars': sum(len(c['text']) for c in content),
            'content': content,
        }
        (OUT / f'{short.lower()}.json').write_text(
            json.dumps(out, ensure_ascii=False), encoding='utf-8')
        index.append({'id': out['id'], 'taisho': short, 'title': title,
                      'translator': translator, 'vol': vol,
                      'juan': out['juan'], 'chars': out['chars']})
    try:
        META_CACHE.write_text(json.dumps(metas, ensure_ascii=False))
    except Exception:
        pass
    log(f'解析结束: 入库 {len(results)} 部')
    return index


def do_index(index=None):
    if index is None:
        index = []
        for fp in sorted(OUT.glob('t*.json')):
            try:
                d = json.loads(fp.read_text())
                index.append({k: d.get(k) for k in
                              ('id', 'taisho', 'title', 'translator', 'vol', 'juan', 'chars')})
            except Exception:
                pass
    index.sort(key=lambda x: (x.get('taisho') or ''))
    idx = {
        'total': len(index),
        'chars': sum((x.get('chars') or 0) for x in index),
        'source': 'CBETA大正藏',
        'updated': time.strftime('%Y-%m-%d %H:%M'),
        'sutras': index,
    }
    (OUT / 'index.json').write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding='utf-8')
    log(f'索引完成: {idx["total"]} 部 / {idx["chars"]} 字')
    return idx


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    t0 = time.time()
    if mode in ('download', 'all'):
        do_download()
    if mode in ('parse', 'all', 'reparse'):
        idx = do_parse()
        do_index(idx)
    if mode == 'index':
        do_index()
    log(f'== 流程结束({mode}) 用时 {int(time.time()-t0)}s ==')
