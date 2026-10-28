#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版解析器：补齐之前漏掉的块级元素（item/list/mulu/jl_*/byline/lg/fan/zi/yin 等）
仅对"之前解析字数低于官方字数 70%"的经做重解析，避免浪费时间。
用法: python3 scripts/reparse_fix.py
"""
import json, re, sys, os, time
from pathlib import Path
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'sutras'
CACHE = ROOT / '.xmlcache'
META_CACHE = CACHE / 'meta_cache.json'
LOG = ROOT / 'reparse.log'

NS = {'t': 'http://www.tei-c.org/ns/1.0'}

# 需要剔除的校勘/版面标签
# 注意：note 不在此全局跳过，而是按属性判断（place=inline 是正文内嵌注释要保留，
#       有 resp/corresp/app/rdg/lem 等校勘属性的才删）
SKIP_STRUCT = {'rdg', 'witness', 'app', 'witDetail', 'lem', 'rdgGrp',
        'lb', 'pb', 'anchor', 'space', 'milestone', 'caesura',
        'graphic', 'figure', 'docNumber'}

# 视为"标题"的标签（触发章节切换）
HEAD_TAGS = {'head', 'jhead', 'mulu', 'jl_title', 'byline', 'jl_byline',
             'fan'}  # fan 是翻譯題名

# 视为"正文块"的标签（其文本应被收录）
BLOCK_TAGS = {'p', 'l', 'item', 'list', 'lg', 'jl_juan', 'yin', 'zi', 'div',
              't', 'tt', 'term'}  # t/tt 为梵汉对音字；term 为术语


def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def clean(t):
    """清理空白：保留换行，去首尾空白与多空白"""
    if not t:
        return ''
    t = t.replace('\u3000', ' ')
    t = re.sub(r'[ \t]+', '', t)       # 去空格/tab
    t = re.sub(r'\n+', '\n', t)         # 多换行合一个
    return t.strip()


def is_skip_note(e):
    """判断 note 是否是校勘注（应删除）。
    CBETA 中：place=inline 是正文内嵌注释（如音义释义），要保留；
              有 resp/corresp/type=orig/type=mod 是校勘，要删。
    """
    place = e.get('place') or e.get('{http://www.cbeta.org/ns/1.0}place') or ''
    resp = e.get('resp') or ''
    ntype = e.get('type') or e.get('{http://www.cbeta.org/ns/1.0}type') or ''
    corresp = e.get('corresp') or ''
    if resp or corresp:
        return True
    if ntype and ntype not in ('inline', 'comm'):
        return True
    # 没任何校勘属性、且 place=inline/缺省 → 视为正文内嵌注释，保留
    return False


def extract_text(e):
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
            parts.append(extract_text(ch))
        if ch.tail:
            parts.append(ch.tail)
    return ''.join(parts)


def parse_tei(xml_bytes):
    try:
        root = ET.fromstring(xml_bytes)
    except Exception as e:
        return None, str(e)

    # 取标题
    title = ''
    author = ''
    ts = root.find('.//t:teiHeader//t:titleStmt', NS)
    if ts is not None:
        for t in ts.findall('t:title', NS):
            lang = t.get('{http://www.w3.org/XML/1998/namespace}lang')
            level = t.get('level')
            if lang == 'zh-Hant' and level == 'm':
                title = (t.text or '').strip()
                break
        if not title:
            for t in ts.findall('t:title', NS):
                if t.text and '大正' not in t.text and 'Taishō' not in t.text:
                    title = t.text.strip()
                    break
        a = ts.find('t:author', NS)
        if a is not None:
            author = ''.join(a.itertext()).strip()

    body = root.find('.//t:text/t:body', NS)
    if body is None:
        return None, 'no body'

    chapters = []
    cur_title = None
    cur_parts = []

    def flush():
        if cur_parts:
            txt = '\n'.join(p for p in cur_parts if p and p.strip())
            if txt.strip():
                chapters.append({'chapter': cur_title or '正文', 'text': clean(txt)})
        cur_parts.clear()

    # 正文主体遍历：遍历所有子节点，按深度优先处理 juan/head/block 的顺序
    def walk(e, in_block=False):
        nonlocal cur_title
        tg = e.tag.split('}')[-1]
        if tg in SKIP_STRUCT:
            return
        if tg == 'note' and is_skip_note(e):
            return
        if tg == 'juan':
            flush()
            n = e.get('n') or ''
            cur_title = f'卷{n}' if n else cur_title or '正文'
            for ch in e:
                walk(ch, in_block=False)
            return
        if tg in HEAD_TAGS:
            h = clean(extract_text(e))
            if h and len(h) < 120:
                flush()
                # mulu/jl_* 可能只是目录条目，不作为"大标题"截断；只有真正的 head/jhead/byline/fan 才切换
                if tg in ('head', 'jhead', 'byline', 'jl_byline', 'fan'):
                    cur_title = h
                else:
                    # mulu/jl_title/jl_juan 是目录/小条目，作为正文的一行输出即可
                    cur_parts.append('【' + h + '】')
                for ch in e:
                    walk(ch, in_block=True)
                return
        if tg in BLOCK_TAGS:
            t = clean(extract_text(e))
            if t:
                cur_parts.append(t)
            # 不再深入，extract_text 已拿到；但 lg/list 里 children 可能是 block，处理完就好
            return
        # 其他包装元素（div/body/lg 等），递归
        for ch in e:
            walk(ch, in_block)

    walk(body)
    flush()

    if not chapters:
        return None, 'empty after parse'

    return {'title': title, 'author': author, 'chapters': chapters}, None


def work_short(name):
    m = re.match(r'T(\d+)n(\d+[a-z]?)', name)
    return ('T' + m.group(2)) if m else None


def reparse_targets(force_ratio=0.7):
    """返回需要重解析的经号列表"""
    metas = json.loads(META_CACHE.read_text()) if META_CACHE.exists() else {}
    targets = []
    skipped = 0
    for fp in sorted(CACHE.glob('[Tt]*.xml')):
        short = work_short(fp.stem)
        if not short:
            continue
        outfp = OUT / f'{short.lower()}.json'
        if not outfp.exists():
            targets.append((fp, short))
            continue
        # 有元数据的，比对字数（CBETA 字段是 cjk_chars）
        meta = metas.get(short, {})
        exp_chars = meta.get('cjk_chars') or meta.get('chars') or meta.get('character_count') or 0
        try:
            d = json.loads(outfp.read_text())
            cur = d.get('chars', 0)
        except Exception:
            targets.append((fp, short))
            continue
        # 对 T54/T55 目錄/事彙/音義/史傳部 强制重解析（旧解析器漏 item/jl_* 等标签）
        cat = (meta.get('category') or '')
        is_catalog = (meta.get('vol', '') in ('T54', 'T55')) and any(k in cat for k in ('目錄', '事彙', '音義', '史傳'))
        if is_catalog:
            targets.append((fp, short))
        elif exp_chars and cur < exp_chars * force_ratio:
            targets.append((fp, short))
        else:
            skipped += 1
    return targets, skipped


def one(fp, short):
    try:
        xml_bytes = fp.read_bytes()
        res, err = parse_tei(xml_bytes)
        if not res:
            return (short, 'fail', err, 0)
        # 读现有 json 保留元数据
        outfp = OUT / f'{short.lower()}.json'
        try:
            old = json.loads(outfp.read_text())
        except Exception:
            old = {}
        content = res['chapters']
        chars = sum(len(c['text']) for c in content)
        out = {
            'id': short.lower(),
            'taisho': short,
            'title': old.get('title') or res['title'] or short,
            'translator': old.get('translator') or res['author'] or '',
            'vol': old.get('vol') or '',
            'category': old.get('category') or '',
            'dynasty': old.get('dynasty') or '',
            'time_from': old.get('time_from') or '',
            'time_to': old.get('time_to') or '',
            'juan': len(content),
            'chars': chars,
            'content': content,
        }
        outfp.write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
        return (short, 'ok', '', chars)
    except Exception as e:
        return (short, 'fail', str(e), 0)


def main():
    targets, skipped = reparse_targets()
    log(f'待重解析 {len(targets)} 部，其余 {skipped} 部已达标')
    if not targets:
        log('无需重解析')
        return
    ok = fail = 0
    total_added = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(one, fp, sh): (fp, sh) for fp, sh in targets}
        for i, f in enumerate(futs):
            sh, st, err, chars = f.result()
            if st == 'ok':
                ok += 1
                total_added += chars
            else:
                fail += 1
                log(f'  失败 {sh}: {err}')
            if (i + 1) % 20 == 0 or i + 1 == len(targets):
                log(f'重解析 {i+1}/{len(targets)} ok={ok} fail={fail}')
    log(f'重解析结束: ok={ok} fail={fail}')

    # 重建索引
    index = []
    total_chars = 0
    for fp in sorted(OUT.glob('t*.json')):
        try:
            d = json.loads(fp.read_text())
            total_chars += d.get('chars', 0)
            index.append({k: d.get(k) for k in
                          ('id', 'taisho', 'title', 'translator', 'vol',
                           'category', 'dynasty', 'juan', 'chars')})
        except Exception:
            pass
    index.sort(key=lambda x: (x.get('taisho') or ''))
    idx = {
        'total': len(index),
        'chars': total_chars,
        'source': 'CBETA大正藏',
        'updated': time.strftime('%Y-%m-%d %H:%M'),
        'sutras': index,
    }
    (OUT / 'index.json').write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding='utf-8')
    log(f'索引重建: {idx["total"]} 部 / {idx["chars"]:,} 字')


if __name__ == '__main__':
    t0 = time.time()
    main()
    log(f'== 用时 {int(time.time()-t0)}s ==')
