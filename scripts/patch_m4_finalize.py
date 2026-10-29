#!/usr/bin/env python3
"""M4 补丁收尾：聚合反向索引 + 重写 manifest（按批打印进度）。"""
import json, os, glob, sys

D = 'ontology/instances'

def main():
    print('loading events.json...')
    with open(os.path.join(D, 'events.json'), encoding='utf-8') as f:
        ev = json.load(f)
    print('loading dharma_assemblies.json...')
    with open('ontology/dharma_assemblies.json', encoding='utf-8') as f:
        da = json.load(f)

    rel_da = {aid: set((obj.get('sutras') or [])) for aid, obj in da['assemblies'].items()}
    rel_c  = {e['id']: set(e.get('related_sutras', [])) for e in ev['councils']}
    rel_te = {e['id']: set(e.get('related_sutras', [])) for e in ev['transmission_events']}
    rel_se = {e['id']: set(e.get('related_sutras', [])) for e in ev['story_events']}

    files = sorted(
        fp for fp in glob.glob(D + '/*.json')
        if os.path.basename(fp) not in ('events.json', 'manifest.json')
        and os.path.getsize(fp) > 0
    )
    print(f'total files: {len(files)}')

    tch = tp = tg = tm = 0
    wg = wm = wf = wdoc = wda = wc = wse = 0
    sutra_records = []
    for i, fp in enumerate(files):
        sid = os.path.basename(fp)[:-5]
        with open(fp, encoding='utf-8') as f:
            x = json.load(f)
        chs = x.get('chapters', []); ps = x.get('paragraphs', [])
        gs  = x.get('gathas', []);    ms = x.get('mantras', [])
        tch += len(chs); tp += len(ps); tg += len(gs); tm += len(ms)
        if gs:  wg += 1
        if ms:  wm += 1
        if x.get('figure_mentions'):   wf += 1
        if x.get('doctrine_mentions'): wdoc += 1
        da_id = x.get('dharma_assembly')
        if da_id and da_id in rel_da:
            wda += 1
            rel_da[da_id].add(sid)
        for cid in x.get('councils', []):
            if cid in rel_c:
                wc += 1
                rel_c[cid].add(sid)
        for tid in x.get('transmission_events', []):
            if tid in rel_te:
                rel_te[tid].add(sid)
        for seid in x.get('story_events', []):
            if seid in rel_se:
                wse += 1
                rel_se[seid].add(sid)
        sutra_records.append({
            'id': sid,
            'title': x.get('title', ''),
            'translator': x.get('translator', ''),
            'translator_note': x.get('translator_note', ''),
            'category': x.get('category', ''),
            'juan_count': x.get('juan_count', 1),
            'char_count': x.get('actual_char_count', 0),
            'chapter_count': len(chs),
            'paragraph_count': len(ps),
            'gatha_count': len(gs),
            'mantra_count': len(ms),
            'figure_count': len(x.get('figure_mentions', [])),
            'doctrine_count': len(x.get('doctrine_mentions', [])),
            'vehicle': x.get('vehicle', ''),
            'mode': x.get('mode', ''),
            'belongs_to_school': x.get('belongs_to_school', []),
            'dharma_assembly': da_id,
            'councils': x.get('councils', []),
            'transmission_events': x.get('transmission_events', []),
            'story_events': x.get('story_events', []),
        })
        if (i + 1) % 500 == 0:
            print(f'  processed {i+1}/{len(files)}')

    # 回写 dharma_assemblies
    for aid, obj in da['assemblies'].items():
        obj['sutras'] = sorted(rel_da[aid])
        obj['sutra_count'] = len(obj['sutras'])
    da['total'] = len(sutra_records)
    da['sutras_linked'] = wda
    with open('ontology/dharma_assemblies.json', 'w', encoding='utf-8') as f:
        json.dump(da, f, ensure_ascii=False, indent=2)

    # 回写 events
    for e in ev['councils']:
        e['related_sutras'] = sorted(rel_c[e['id']])
    for e in ev['transmission_events']:
        e['related_sutras'] = sorted(rel_te[e['id']])
    for e in ev['story_events']:
        e['related_sutras'] = sorted(rel_se[e['id']])
    ev['_meta'] = {
        'version': '3.1.0-m4',
        'total_sutras': len(sutra_records),
        'dharma_assemblies_count': len(da['assemblies']),
        'councils_count': len(ev['councils']),
        'transmission_events_count': len(ev['transmission_events']),
        'story_events_count': len(ev['story_events']),
        'total_gathas': tg, 'total_mantras': tm,
        'total_chapters': tch, 'total_paragraphs': tp,
        'sutras_with_dharma_assembly': wda,
        'sutras_with_council': wc,
        'sutras_with_story_event': wse,
    }
    with open(os.path.join(D, 'events.json'), 'w', encoding='utf-8') as f:
        json.dump(ev, f, ensure_ascii=False, indent=2)

    # 写 manifest
    manifest = {
        'meta': {
            'total': len(sutra_records),
            'version': '3.1.0-m4',
            'generated_by': 'build_all_instances + M4 事件层 + 失译补注',
        },
        'sutras': sorted(sutra_records, key=lambda r: r['id']),
        'stats': {
            'total_chapters': tch, 'total_paragraphs': tp,
            'total_gathas': tg, 'total_mantras': tm,
            'sutras_with_gathas': wg, 'sutras_with_mantras': wm,
            'sutras_with_figures': wf, 'sutras_with_doctrines': wdoc,
            'sutras_with_dharma_assembly': wda,
            'sutras_with_council': wc,
            'sutras_with_transmission_event': len(sutra_records),
            'sutras_with_story_event': wse,
        }
    }
    with open(os.path.join(D, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f'实例 {len(sutra_records)} | 章 {tch} | 段 {tp} | 偈 {tg} | 咒 {tm}')
    print(f'含偈 {wg} | 含咒 {wm} | 人物 {wf} | 佛理 {wdoc}')
    print(f'含法会 {wda} | 含结集 {wc} | 含译经 {len(sutra_records)} | 含故事 {wse}')
    print(f'事件总：法会 {len(da["assemblies"])} | 结集 {len(ev["councils"])} | 译经 {len(ev["transmission_events"])} | 故事 {len(ev["story_events"])}')
    # 打印 te_unknown 关联数
    for e in ev['transmission_events']:
        if e['id'] == 'te_unknown':
            print(f'te_unknown 关联经文: {len(e["related_sutras"])}')
            break

if __name__ == '__main__':
    main()
