#!/usr/bin/env python3
import os
import json
import re

# 配置
SUTRAS_DIR = "sutras"
MODERN_DIR = "data/modern-translation"
MIN_SEGMENTS = 1
PUA_RANGES = [
    (0xF000, 0xF8FF),
    (0xF0000, 0xFFFFD),
    (0x100000, 0x10FFFD),
]
MAX_BAD_RATIO = 0.05  # PUA或阙字占比不超过5%

def is_pua_char(c):
    cp = ord(c)
    for start, end in PUA_RANGES:
        if start <= cp <= end:
            return True
    return False

def count_bad_chars(text):
    pua_count = 0
    missing_count = 0
    for c in text:
        if c == '□':
            missing_count += 1
        elif is_pua_char(c):
            pua_count += 1
    return pua_count, missing_count

def main():
    # 已完成的经号集合
    done = set()
    for fn in os.listdir(MODERN_DIR):
        if fn.endswith('.json'):
            done.add(fn[:-5])
    
    candidates = []
    
    for fn in os.listdir(SUTRAS_DIR):
        if not fn.endswith('.json'):
            continue
        sutra_id = fn[:-5]
        if sutra_id in done:
            continue
        
        path = os.path.join(SUTRAS_DIR, fn)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            continue
        
        if not isinstance(data, dict):
            continue
        
        content = data.get('content', '')
        if isinstance(content, list):
            text = '\n'.join(str(p) for p in content if p)
        else:
            text = str(content)
        if not text:
            continue
        
        # 统计字数
        clean_text = re.sub(r'\s+', '', text)
        char_count = len(clean_text)
        official_count = data.get('actual_char_count', 0) or data.get('chars', 0)
        if official_count > 0:
            char_count = official_count
        
        # 统计坏字符占比
        pua_count, missing_count = count_bad_chars(clean_text)
        total_bad = pua_count + missing_count
        bad_ratio = total_bad / char_count if char_count > 0 else 1
        
        if bad_ratio > MAX_BAD_RATIO:
            continue
        
        # 估算段数
        segments = len(re.split(r'[。\n]', text))
        
        candidates.append((char_count, bad_ratio, sutra_id, data.get('title', ''), segments))
    
    # 按字数从低到高排序
    candidates.sort(key=lambda x: x[0])
    
    print(f"符合坏字率要求的候选经文共 {len(candidates)} 部")
    print("选取前12部（按字数从低到高）：")
    for i, (cnt, ratio, sid, title, segs) in enumerate(candidates[:12]):
        print(f"{i+1}. {sid} {title} - {cnt}字, 坏字率{ratio:.2%}, 段数~{segs}")
    
    # 输出本批经号
    batch = [sid for _, _, sid, _, _ in candidates[:12]]
    print("\n本批经号：")
    print(' '.join(batch))
    
    # 保存到文件
    with open('current_batch.txt', 'w', encoding='utf-8') as f:
        f.write(' '.join(batch))
    
    return batch

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    batch = main()
