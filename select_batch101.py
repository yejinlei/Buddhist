#!/usr/bin/env python3
import json, os, glob, re
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)
SUTRA_DIR = "sutras"
MODERN_DIR = "data/modern-translation"

done = set()
for fn in os.listdir(MODERN_DIR):
    if fn.endswith('.json'):
        done.add(fn[:-5])

SKIP = {"hant2simp","index","index-light","search-index","search-word-index"}

def pua_ratio(text):
    if not text: return 1.0, 0, 0, 0
    total = len(re.sub(r"\s+", "", text))
    pua = 0
    for ch in text:
        cp = ord(ch)
        if (0xF000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0xFFFFD) or (0x100000 <= cp <= 0x10FFFD):
            pua += 1
    blank = text.count('□')
    ratio = (pua + blank) / total if total > 0 else 1.0
    return ratio, pua, blank, total

def get_text(sutra):
    parts = []
    content = sutra.get('content', [])
    if not isinstance(content, list):
        content = []
    for sec in content:
        if isinstance(sec, dict):
            if 'text' in sec:
                parts.append(sec['text'])
            for k in ['paragraphs', 'sections']:
                if k in sec:
                    for p in sec[k]:
                        if isinstance(p, str):
                            parts.append(p)
                        elif isinstance(p, dict) and 'text' in p:
                            parts.append(p['text'])
        elif isinstance(sec, str):
            parts.append(sec)
    return '\n'.join(parts)

def count_segments(text):
    def norm(s): return re.sub(r"\s+", "", s)
    SPLIT_RE = re.compile(r'(?<=[。！？；：」』）\)\n])')
    parts_split = [p for p in SPLIT_RE.split(text) if p != ""]
    segs, buf = [], ""
    for p in parts_split:
        if len(norm(p)) > 340:
            sub = re.split(r'(?<=[，、])', p)
            for q in sub:
                if not q: continue
                buf += q
                if len(norm(buf)) >= 90:
                    segs.append(buf); buf = ""
            continue
        buf += p
        if len(norm(buf)) >= 90:
            segs.append(buf); buf = ""
    if buf.strip():
        if segs and len(norm(buf)) < 30:
            segs[-1] += buf
        else:
            segs.append(buf)
    return len(segs)

candidates = []
lo = 400
hi = 2500
while len(candidates) < 12 and hi <= 10000:
    for fn in os.listdir(SUTRA_DIR):
        if not fn.endswith('.json'): continue
        sid = fn[:-5]
        if sid in done or sid in SKIP: continue
        fp = os.path.join(SUTRA_DIR, fn)
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                s = json.load(f)
        except:
            continue
        if not isinstance(s, dict): continue
        title = s.get('title', '')
        translator = s.get('translator', '')
        text = get_text(s)
        ratio, pua, blank, total = pua_ratio(text)
        if ratio > 0.05: continue
        nseg = count_segments(text)
        if lo <= total <= hi and nseg >= 3:
            # 去重
            if not any(c[2] == sid for c in candidates):
                candidates.append((total, ratio, sid, title, translator, pua, blank, nseg))
    hi += 500
    if len(candidates) >= 12:
        break

candidates.sort(key=lambda x: x[0])
selected = candidates[:12]
print("本批选中经文：")
selected_ids = []
for i, (total, ratio, sid, title, translator, pua, blank, nseg) in enumerate(selected):
    print(f"{i+1:2d}. {sid:6s} {total:4d}字 {nseg:2d}段 PUA+阙={ratio*100:.1f}% ({pua}pua,{blank}□) - {title[:50]} [{translator}]")
    selected_ids.append(sid)

print("\n选中经号列表：")
print(' '.join(selected_ids))
with open(os.path.join(ROOT, 'current_batch.txt'), 'w') as f:
    f.write(' '.join(selected_ids))
