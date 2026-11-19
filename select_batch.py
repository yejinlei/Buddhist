#!/usr/bin/env python3
import os
import json

completed = set()
for f in os.listdir('data/modern-translation'):
    if f.endswith('.json') and f.startswith('t'):
        completed.add(f[:-5])

print(f"已完成t系列: {len(completed)}")

candidates = []
sutra_dir = 'sutras'

for fname in os.listdir(sutra_dir):
    if not fname.endswith('.json') or not fname.startswith('t'):
        continue
    sid = fname[:-5]
    if sid in completed:
        continue
    
    fpath = os.path.join(sutra_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    
    # 拼接所有content段落的text
    text = ""
    for para in data.get('content', []):
        if isinstance(para, dict) and 'text' in para:
            text += para['text']
    total = len(text)
    if total < 400:
        continue
    
    que = text.count('□')
    que_r = que / total if total else 1
    
    def is_pua(c):
        cp = ord(c)
        return (0xF000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0xFFFFD) or (0x100000 <= cp <= 0x10FFFD)
    pua = sum(1 for c in text if is_pua(c))
    pua_r = pua/total if total else 1
    
    if pua_r <= 0.05 and que_r <= 0.05:
        candidates.append((total, pua_r, que_r, sid, data.get('title',''), data.get('translator','')))

candidates.sort()
print(f"合格候选（400字以上，PUA和阙文<5%）: {len(candidates)}部")
print("最短30部:")
for i, (t, pr, qr, sid, title, trans) in enumerate(candidates[:30]):
    print(f"{i+1}. {sid} {title[:30]}: {t}字, PUA:{pr:.2%}, 阙文:{qr:.2%}")

batch = [sid for t,pr,qr,sid,_,_ in candidates[:12]]
batch_info = [(sid, title, trans, t) for t,pr,qr,sid,title,trans in candidates[:12]]
print("\n本批12部:")
for sid, title, trans, t in batch_info:
    print(f"{sid} {title} {trans} {t}字")
print(" ".join(batch))
with open('current_batch_sids.txt', 'w') as fp:
    fp.write(" ".join(batch))
import pickle
with open('current_batch_info.pkl', 'wb') as fp:
    pickle.dump(batch_info, fp)
