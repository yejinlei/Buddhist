#!/usr/bin/env python3
import os
import json
import glob
from collections import Counter

# 已完成集合
done = set()
for f in glob.glob('data/modern-translation/*.json'):
    sid = os.path.basename(f).replace('.json', '')
    done.add(sid)

print(f"已完成: {len(done)}")

# 读取所有经文元数据
remaining = []
sutra_dir = 'sutras'
for f in glob.glob(os.path.join(sutra_dir, '*.json')):
    sid = os.path.basename(f).replace('.json', '')
    if sid in done:
        continue
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
        if not isinstance(data, dict):
            continue
        # 拼接全文
        text = ''
        content = data.get('content', [])
        if isinstance(content, str):
            text = content
        else:
            for chap in content:
                if isinstance(chap, dict):
                    text += chap.get('text', '') + '\n'
                elif isinstance(chap, str):
                    text += chap + '\n'
        total_len = len(text.replace('\n', '').replace(' ', ''))
        # 统计PUA字符
        pua_count = 0
        square_count = 0
        for ch in text:
            cp = ord(ch)
            if (0xF000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0xFFFFD) or (0x100000 <= cp <= 0x10FFFD):
                pua_count += 1
            if ch == '□':
                square_count += 1
        bad_ratio = (pua_count + square_count) / max(total_len, 1)
        remaining.append((total_len, sid, data.get('title', ''), bad_ratio))
    except Exception as e:
        continue

print(f"剩余未处理: {len(remaining)}")
# 按字数区间统计
bins = [0, 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 10000, 100000]
for i in range(len(bins)-1):
    low, high = bins[i], bins[i+1]
    cnt = sum(1 for l,_,_,_ in remaining if low <= l < high)
    good_cnt = sum(1 for l,_,_,r in remaining if low <= l < high and r <= 0.05)
    print(f"{low}-{high}字: 共{cnt}部, 合格{good_cnt}部")

# 按字数排序输出前12个合格的（排除0字的异常文件）
good = [(l,s,t,r) for l,s,t,r in remaining if r <= 0.05 and l > 100]
good.sort()
selected = good[:12]
print(f"选中{len(selected)}部经文：")
for length, sid, title, ratio in selected:
    print(f"{sid}\t{length}字\t{title}\t坏字率{ratio:.2%}")

# 写入选中列表
with open('selected_batch.txt', 'w', encoding='utf-8') as fp:
    for length, sid, title, ratio in selected:
        fp.write(f"{sid}\n")
