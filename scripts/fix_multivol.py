#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复「跨册分卷」经典：同一经号分布在大正藏多个册目录（如 T0220 大般若经在 T05/T06/T07），
之前按经号命名 JSON 会互相覆盖，只剩最后一部分。此脚本按册序拼接全部卷，合并为一部。
同时处理 A/B/C 后缀的合卷本，以及解析失败的空文件。
"""
import importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('pf', Path(__file__).parent / 'pipeline_full.py')
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)


def main():
    man = pf.load_manifest()
    volof = {n: v for v, names in man.items() for n in names}
    metas = pf.load_meta()

    groups = {}
    for fp in sorted(pf.CACHE.glob('[Tt]*.xml')):
        s = pf.work_short(fp.stem)
        if not s:
            continue
        groups.setdefault(s, []).append(fp)

    multi = {k: v for k, v in groups.items() if len(v) > 1}
    print(f'跨册/多卷组: {len(multi)} 组，涉及 XML {sum(len(v) for v in multi.values())} 个')

    fixed = 0
    for short, fps in sorted(multi.items()):
        # 按 册号(vol)+文件名 排序，保证卷序正确
        fps = sorted(fps, key=lambda p: (volof.get(p.stem, ''), p.name))
        chapters = []
        title = ''
        author = ''
        vols = []
        for fp in fps:
            try:
                parsed = pf.parse_tei(fp.read_bytes())
            except Exception:
                parsed = None
            if not parsed:
                continue
            if not title:
                title = parsed['title']
            if not author:
                author = parsed['author']
            chapters.extend(parsed['chapters'])
            vols.append(volof.get(fp.stem, ''))
        if not chapters:
            print(f'  [跳过] {short} 无内容')
            continue
        meta = metas.get(short) or pf.fetch_meta(short)
        metas[short] = meta
        title = meta.get('title') or title or short
        translator = meta.get('byline', '') or author
        out = {
            'id': short.lower(),
            'taisho': short,
            'title': title,
            'translator': translator,
            'vol': ','.join(sorted(set(vols))),
            'juan': len(chapters),
            'chars': sum(len(c['text']) for c in chapters),
            'content': chapters,
        }
        (pf.OUT / f'{short.lower()}.json').write_text(
            json.dumps(out, ensure_ascii=False), encoding='utf-8')
        fixed += 1
        print(f'  合并 {short} {title}: {len(fps)}册 -> {out["juan"]}章 {out["chars"]}字')

    try:
        pf.META_CACHE.write_text(json.dumps(metas, ensure_ascii=False))
    except Exception:
        pass

    # 重建索引
    index = []
    for fp in sorted(pf.OUT.glob('t*.json')):
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
        'updated': __import__('time').strftime('%Y-%m-%d %H:%M'),
        'sutras': index,
    }
    (pf.OUT / 'index.json').write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n修复完成: {fixed} 组 | 索引 {idx["total"]} 部 / {idx["chars"]} 字')


if __name__ == '__main__':
    main()
