#!/usr/bin/env python3
"""enrich_chapter_alignments.py: 对章级对齐文件补充 chapter_idx/chapter_title/start/end/preview 字段。

单章经（chapter 数 == 1 或章名为"正文"）：chapter_idx=-1，用首段做章节预览。
多章经：根据 refs 段落索引反查其落在哪个 chapter。
"""
import json, glob, os, re
ALIGN_DIR = 'data/segment_alignments'

# 给文本取前N字（去除标点空白），作为预览
def preview_of(text_list, n=30):
    s = ''.join(text_list)
    s = re.sub(r'\s+', '', s)
    return s[:n] + ('…' if len(s) > n else '')

def load_sutra(tid):
    with open(f'sutras/{tid}.json', encoding='utf-8') as f:
        data = json.load(f)
    chapters = data.get('content', [])
    # 计算每章起止段索引
    chap_ranges = []  # [(start_idx, end_idx_exclusive, chapter_title, [paras])]
    pos = 0
    for ci, c in enumerate(chapters):
        paras = c.get('text', [])
        if isinstance(paras, str):
            paras = [paras]
        # 过滤空段
        paras = [p for p in paras if p and p.strip()]
        chap_ranges.append((pos, pos+len(paras), c.get('chapter') or f'第{ci+1}章', paras))
        pos += len(paras)
    return chap_ranges

def chap_idx_for(chap_ranges, para_idx):
    """返回 (chapter_idx, chapter_title, [paras])，若找不到返回 (-1, '', [])"""
    for ci, (s, e, t, ps) in enumerate(chap_ranges):
        if s <= para_idx < e:
            return ci, t, ps
    return -1, '', []

for fp in sorted(glob.glob(f'{ALIGN_DIR}/*.json')):
    if fp.endswith('manifest.json'):
        continue
    with open(fp, encoding='utf-8') as f:
        d = json.load(f)
    if d.get('mode') != 'chapter':
        continue

    # 预先加载所有译本的章节
    s_chaps = {v['id']: load_sutra(v['id']) for v in d['versions']}

    # 把每个 refs 从 list[int] 转为 dict(chapter_idx, title, start, end, preview)
    new_als = []
    for a in d.get('alignments', []):
        new_refs = {}
        for vid, idxlist in a.get('refs', {}).items():
            if not idxlist:
                new_refs[vid] = None
                continue
            start = idxlist[0]
            end = idxlist[-1]
            chap_ranges = s_chaps.get(vid, [])
            ci, title, chap_paras = chap_idx_for(chap_ranges, start) if chap_ranges else (-1, '', [])

            # 如果是单章经（正文/全文）或没找到章节 -> 用首段摘要
            is_single = (len(chap_ranges) <= 1) or (ci == 0 and not title) or (title in ('正文','全文'))
            if ci < 0 or is_single:
                # 取该区间的段落文本做预览
                flat_paras = []
                for _,_,_,ps in chap_ranges:
                    flat_paras.extend(ps)
                seg_paras = [flat_paras[i] for i in idxlist if 0 <= i < len(flat_paras)]
                new_refs[vid] = {
                    'chapter_idx': -1,
                    'title': f'§{a["id"]}（第{start+1}–{end+1}段）',
                    'start': start,
                    'end': end,
                    'para_count': len(idxlist),
                    'preview': preview_of(seg_paras[:20]),
                    'single_chapter': True,
                }
            else:
                # 多章经：如果区间跨章，取首章；如果章名是"卷X"/重名译者，尝试从正文提品名
                # 取该章段落文本前几句
                chap_start, chap_end, chap_title, chap_paras = chap_ranges[ci]
                # 如果章名是卷号或"正文"，尝试在正文首段找"XX品"
                real_title = chap_title
                m = re.search(r'^([\u4e00-\u9fa5]{2,15}品第?[一二三四五六七八九十百千0-9]+)', chap_paras[0] if chap_paras else '')
                if m and (re.match(r'^卷[一二三四五六七八九十百千0-9]+$', chap_title) or '正文' in chap_title or '經' in chap_title and len(chap_title)<4):
                    real_title = m.group(1)
                new_refs[vid] = {
                    'chapter_idx': ci,
                    'title': real_title,
                    'start': start,
                    'end': end,
                    'para_count': len(idxlist),
                    'preview': preview_of(chap_paras[:15]),
                    'single_chapter': False,
                }
        new_als.append({**a, 'refs': new_refs})
    d['alignments'] = new_als
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    print(f'✓ enriched {fp}')

# 重建 manifest
manifest = []
for fp in sorted(glob.glob(f'{ALIGN_DIR}/*.json')):
    if fp.endswith('manifest.json'): continue
    with open(fp, encoding='utf-8') as f:
        d=json.load(f)
    manifest.append({
        'group_id': d.get('group_id'),
        'group_title': d.get('group_title'),
        'mode': d.get('mode'),
        'n_alignments': len(d.get('alignments',[])),
        'n_versions': len(d.get('versions',[])),
        'versions': d.get('versions',[]),
        'file': os.path.basename(fp),
    })
with open(f'{ALIGN_DIR}/manifest.json','w',encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print('manifest rebuilt, total groups:', len(manifest))
