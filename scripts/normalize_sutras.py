# -*- coding: utf-8 -*-
"""统一 sutras/*.json 为规范 14 字段格式。
修复：旧格式（缺 category）、大写 A/B 卷互相覆盖导致的内容丢失、缺 official_char_count 等。
"""
import json, re, sys
from pathlib import Path
from collections import defaultdict
import importlib.util

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'sutras'
CACHE = ROOT / '.xmlcache'

spec = importlib.util.spec_from_file_location('pf', HERE / 'pipeline_full.py')
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)

META = json.loads((CACHE / 'meta_cache.json').read_text(encoding='utf-8'))
STD = {'id', 'taisho', 'title', 'translator', 'vol', 'juan', 'chars', 'content',
       'category', 'time_from', 'translation_place', 'official_char_count',
       'actual_char_count', 'juan_count'}

# 拼音文件 -> 对应经号（用于补元数据）
PINYIN_MAP = {
    'amituo_jiumo': 'T0366', 'bada_renjue': 'T0779', 'fo_yijiao': 'T0389',
    'jingang_jiumo': 'T0235', 'puxian_xingyuan': 'T0293', 'sishi_erzhang': 'T0784',
    'xinjing_fayue': 'T0252', 'xinjing_jiumo': 'T0250', 'xinjing_xuanzang': 'T0251',
    'yaoshi_xuanzang': 'T0450', 'yulan_pen': 'T0685',
}

# XML 按 short 归组（A/B/C 多卷会归到同一 short）
groups = defaultdict(list)
for fp in sorted(CACHE.glob('[Tt]*.xml')):
    s = pf.work_short(fp.stem)
    if s:
        groups[s].append(fp)


def parse_group(short):
    """解析同一 short 下的全部 XML 并合并章节（按文件名排序，A→B→C）"""
    files = sorted(groups.get(short, []))
    chapters, title = [], ''
    for fp in files:
        try:
            p = pf.parse_tei(fp.read_bytes())
        except Exception:
            continue
        if not p:
            continue
        if not title:
            title = p.get('title') or ''
        chapters.extend(p['chapters'])
    if not chapters:
        return None, title
    return chapters, title


def build(short):
    meta = META.get(short) or {}
    chapters, ptitle = parse_group(short)
    if chapters is None:
        return None
    cat = (meta.get('category') or '').replace('類', '类')
    places = meta.get('places') or []
    actual = sum(len(c['text']) for c in chapters)
    return {
        'id': short.lower(),
        'taisho': short,
        'title': ptitle or meta.get('title') or short,
        'translator': meta.get('byline') or '',
        'vol': (meta.get('vol') or '').upper(),
        'juan': len(chapters),
        'chars': actual,
        'content': chapters,
        'category': cat or '其他部类',
        'time_from': meta.get('time_from') or '',
        'translation_place': places[0].get('name', '') if places else '',
        'official_char_count': meta.get('cjk_chars') or 0,
        'actual_char_count': actual,
        'juan_count': meta.get('juan') or len(chapters),
    }


def main():
    targets = []
    for f in sorted(OUT.glob('*.json')):
        b = f.name
        if b in ('index.json', 'index-light.json') or b.startswith('search-') or b == 'hant2simp.json':
            continue
        try:
            d = json.loads(f.read_text(encoding='utf-8'))
        except Exception:
            targets.append(b[:-5]); continue
        if not STD.issubset(set(d.keys())):
            targets.append(b[:-5])
    print('需修复文件数:', len(targets))

    fixed = skipped = 0
    for sid in targets:
        short = sid[0].upper() + sid[1:] if sid.startswith('t') else sid
        if short in groups:
            out = build(short)
            if out:
                (OUT / f'{sid}.json').write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
                fixed += 1
                continue
        # 拼音文件：保留原内容，仅补元数据字段
        if sid in PINYIN_MAP:
            f = OUT / f'{sid}.json'
            d = json.loads(f.read_text(encoding='utf-8'))
            meta = META.get(PINYIN_MAP[sid]) or {}
            places = meta.get('places') or []
            d.setdefault('category', (meta.get('category') or '').replace('類', '类') or '其他部类')
            d.setdefault('time_from', meta.get('time_from') or '')
            d.setdefault('translation_place', places[0].get('name', '') if places else '')
            d.setdefault('official_char_count', meta.get('cjk_chars') or 0)
            d['actual_char_count'] = sum(len(c.get('text', '')) for c in d.get('content', []))
            d.setdefault('juan_count', meta.get('juan') or len(d.get('content', [])))
            f.write_text(json.dumps(d, ensure_ascii=False), encoding='utf-8')
            fixed += 1
            continue
        skipped += 1
        print('  未处理:', sid)
    print(f'已修复 {fixed} 部，跳过 {skipped} 部')


if __name__ == '__main__':
    main()
