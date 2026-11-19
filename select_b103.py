#!/usr/bin/env python3
import json, os, re
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)

done = {fn[:-5] for fn in os.listdir("data/modern-translation") if fn.endswith('.json')}
SKIP = {"hant2simp","index","index-light","search-index","search-word-index"}

def pua_ratio(text):
    if not text: return 1.0, 0, 0, 0
    norm_text = re.sub(r"\s+", "", text)
    total = len(norm_text)
    pua = sum(1 for ch in norm_text if (0xF000 <= ord(ch) <= 0xF8FF) or (0xF0000 <= ord(ch) <= 0xFFFFD) or (0x100000 <= ord(ch) <= 0x10FFFD))
    blank = norm_text.count('□')
    ratio = (pua + blank) / total if total > 0 else 1.0
    return ratio, pua, blank, total

candidates = []

# 一次性遍历所有经文
for fn in os.listdir("sutras"):
    if not fn.endswith('.json'): continue
    sid = fn[:-5]
    if sid in done or sid in SKIP: continue
    try:
        with open(f"sutras/{fn}", 'r', encoding='utf-8') as f:
            s = json.load(f)
    except:
        continue
    if not isinstance(s, dict): continue
    parts = []
    for sec in s.get('content', []):
        if isinstance(sec, dict):
            if 'text' in sec: parts.append(sec['text'])
        elif isinstance(sec, str):
            parts.append(sec)
    text = '\n'.join(parts)
    ratio, pua, blank, total = pua_ratio(text)
    if ratio > 0.05: continue
    nseg = s.get('content', []) and len([c for c in s.get('content', []) if isinstance(c, dict) and c.get('text','').strip()])
    if nseg < 3: continue
    candidates.append((total, ratio, sid, s.get('title',''), s.get('translator',''), nseg))

# 按字数从低到高排序
candidates.sort(key=lambda x: x[0])
selected = candidates[:12]
selected_ids = [c[2] for c in selected]
print("本批选中：")
for c in selected:
    print(f"  {c[2]:6s} {c[0]:4d}字 {c[5]:2d}段 PUA={c[1]*100:.1f}% - {c[3][:50]} [{c[4]}]")
print(f"\n候选总数：{len(candidates)}，选中12部")
print("经号：", ' '.join(selected_ids))
with open('current_batch.txt', 'w') as f:
    f.write(' '.join(selected_ids))
