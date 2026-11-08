#!/usr/bin/env python3
"""机械切段：把全文按自然意群切成段，保证所有段 preview 是原文连续子串、覆盖全文。"""
import json, re, sys, os

TARGETS = ['t1314','t1389','t1404','t1375','t1346','t1349','t1352','t1356','t1317']
# 再加几个
TARGETS = ['t1314','t1389','t1404','t1375','t1346','t1349','t1352','t1356','t0707','t1389']

def load_sutra(tid):
    f = f'sutras/{tid}.json'
    d = json.load(open(f))
    c = d['content']
    if isinstance(c, list):
        if c and isinstance(c[0], dict):
            text = ''.join(seg.get('text','') for seg in c if isinstance(seg, dict))
        else:
            text = ''.join(str(x) for x in c)
    else:
        text = str(c)
    return d['title'], d['translator'], d.get('category','密教部类' if 't1' in tid else '经集部类'), text

def split_segments(text, target_len=180, min_len=60, max_len=400):
    """按标点切分，尽量保持 target_len 长度、避免跨行截断"""
    # 清理多余空白但保留换行信息
    text = text.replace('\r\n','\n').replace('\r','\n')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    # 优先在句末标点处分段：。！？；
    # 若太长，再在、，处分
    segments = []
    buf = ''
    for line in lines:
        # 跳过经题/译者署名开头几行的处理：并入第一段
        if buf == '' and len(line) < 30 and ('經' in line or '譯' in line or '如是' in line):
            buf = line
            continue
        buf += line
        # 按自然句切
        # 先在句末标点处（。）切
        while len(buf) >= min_len:
            # 找最近的 。在 buf 中不超过 max_len 的位置
            cut = -1
            for i, ch in enumerate(buf):
                if ch in '。！？；':
                    if i+1 >= min_len:
                        cut = i+1
                        break
            if cut == -1 or cut > max_len:
                # 找次一级的 、，
                for i, ch in enumerate(buf):
                    if ch in '、，':
                        if i+1 >= min_len:
                            cut = i+1
                            break
                if cut == -1 or cut > max_len:
                    if len(buf) > max_len:
                        cut = max_len
                    else:
                        break
            seg = buf[:cut].strip()
            if seg:
                segments.append(seg)
            buf = buf[cut:].strip()
    if buf.strip():
        if segments and len(buf) < 30:
            segments[-1] = segments[-1] + buf
        else:
            segments.append(buf.strip())
    
    # 验证：段拼接是否为 text 子串
    clean = re.sub(r'\s+','',text)
    joined = ''
    for s in segments:
        joined += re.sub(r'\s+','',s)
    cov = len(joined) / len(clean) if clean else 0
    # 验证所有段是原文子串
    fails = []
    for i, s in enumerate(segments):
        cs = re.sub(r'\s+','',s)
        if cs not in clean:
            fails.append(i)
    return segments, cov, fails

if __name__ == '__main__':
    out = {}
    for tid in TARGETS:
        if not os.path.exists(f'sutras/{tid}.json'):
            continue
        title, trans, cat, text = load_sutra(tid)
        segs, cov, fails = split_segments(text)
        print(f'{tid} {title} | 译={trans} | 总字={len(text)} | 段={len(segs)} | 覆盖={cov:.2%} | 错段={fails}')
        out[tid] = {
            'title': title, 'translator': trans, 'category': cat,
            'text': text, 'segments': segs, 'coverage': cov, 'fails': fails,
        }
    with open('/tmp/segments_batch.json','w') as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
