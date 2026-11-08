#!/usr/bin/env python3
"""批量抽取本轮 10 部经的繁体原文到临时目录（供翻译 worker 使用）。"""
import json, os, re

SUTRAS = ['t0080','t0367','t1476','t0537','t0022','t0248','t1325','t0116','t0174','t0686']
SRC_DIR = 'sutras'
OUT_DIR = '_translate_src_batch2'
os.makedirs(OUT_DIR, exist_ok=True)

def split_paragraphs(text):
    """按『「」』前后的句末标点 + 长行拆分段落，保持原文不改动。"""
    # 按双换行/连续段落拆
    # 先把硬折行全部合并（换行→空）
    text = re.sub(r'\n', '', text)
    # 在句末标志处切分：。」、！」、？」、。（后面跟中文引号外/下句开头）
    # 但不拆偈颂/对话内部。简化：按中文段落「。」「！」「？」+「」」后紧跟中文汉字（非「」『』内），按大约 80-200 字切分
    chunks = []
    # 以佛说对白自然分段
    # 先按常见对话开头"佛言"、"佛告"、"爾時"、"是時"、"於是"等切
    # 或者直接按 。/！/？ + 引号闭合 → 切，每段 100-200 字
    pos = 0
    buf = ''
    for m in re.finditer(r'([。！？][」』]*)', text):
        end = m.end()
        buf = text[pos:end]
        if len(buf) >= 80 or len(chunks)==0:
            chunks.append(buf)
            pos = end
            buf = ''
        else:
            continue
    if pos < len(text):
        chunks.append(text[pos:])
    # 过滤空段
    return [c.strip() for c in chunks if c.strip() and len(c.strip())>=15]

for sid in SUTRAS:
    fp = os.path.join(SRC_DIR, f'{sid}.json')
    with open(fp, 'r', encoding='utf-8') as f:
        d = json.load(f)
    # 提取全部原文
    full_text = ''
    for c in d.get('content', []):
        full_text += c.get('text','')
    # 去掉译者署名行
    full_text = re.sub(r'^[^」\"]+?譯\s*', '', full_text, count=1)
    paragraphs = split_paragraphs(full_text)
    out = [
        f'# {sid} {d["title"]}',
        f'# 译者: {d.get("translator","")}',
        f'# 全文字数: {d.get("actual_char_count", d.get("chars"))}',
        f'# 切分段落数: {len(paragraphs)}',
        '',
    ]
    for i,p in enumerate(paragraphs,1):
        out.append(f'=== 段落 {i} ===')
        out.append(p)
        out.append('')
    out_path = os.path.join(OUT_DIR, f'{sid}.txt')
    with open(out_path, 'w', encoding='utf-8') as o:
        o.write('\n'.join(out))
    print(f'{sid} {d["title"]:25s} 译者={d.get("translator",""):20s} 字数={d.get("actual_char_count",d.get("chars",0)):5d} 切分={len(paragraphs)} 段')
