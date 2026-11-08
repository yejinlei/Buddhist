#!/usr/bin/env python3
import os
import re

completed = set()
for f in os.listdir('data/modern-translation'):
    if f.endswith('.json') and f.startswith('t'):
        completed.add(f[:-5])

print(f"已完成t系列: {len(completed)}")

candidates = []
sutra_dir = 'sutras'

for fname in os.listdir(sutra_dir):
    if not fname.endswith('.xml'):
        continue
    sid = fname[:-4]
    if not sid.startswith('t'):
        continue
    if sid in completed:
        continue
    
    fpath = os.path.join(sutra_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as fp:
        content = fp.read()
    
    text = re.sub(r'<[^>]+>', '', content)
    total = len(text)
    
    que = text.count('□')
    que_r = que / total if total else 1
    
    def is_pua(c):
        cp = ord(c)
        return (0xF000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0xFFFFD) or (0x100000 <= cp <= 0x10FFFD)
    pua = sum(1 for c in text if is_pua(c))
    pua_r = pua/total if total else 1
    
    candidates.append((total, pua_r, que_r, sid))

candidates.sort()
print(f"剩余未完成: {len(candidates)}部")
print("最短30部:")
for i, (t, pr, qr, sid) in enumerate(candidates[:30]):
    print(f"{i+1}. {sid}: {t}字, PUA:{pr:.2%}, 阙文:{qr:.2%}")
