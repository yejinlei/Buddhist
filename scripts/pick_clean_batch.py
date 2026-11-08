#!/usr/bin/env python3
import os
import json
import re

# PUA 私用区范围
PUA_RANGES = [
    (0xF000, 0xF8FF),
    (0xF0000, 0xFFFFD),
    (0x100000, 0x10FFFD),
]

def is_pua(c):
    cp = ord(c)
    for start, end in PUA_RANGES:
        if start <= cp <= end:
            return True
    return False

def main():
    project_root = "/home/user/workspace/13511660557912876654/buddhist-ontology"
    sutras_dir = os.path.join(project_root, "sutras")
    done_dir = os.path.join(project_root, "data/modern-translation")
    
    # 已完成经号
    done = set()
    for fn in os.listdir(done_dir):
        if fn.endswith(".json"):
            done.add(fn[:-5])
    
    candidates = []
    min_chars = 400
    max_chars = 2500
    min_segs = 3
    
    while len(candidates) < 12:
        candidates = []
        for fn in os.listdir(sutras_dir):
            if not fn.endswith(".txt"):
                continue
            kid = fn[:-4]
            if kid in done:
                continue
            fp = os.path.join(sutras_dir, fn)
            with open(fp, "r", encoding="utf-8") as f:
                text = f.read()
            # 基础字符数统计（去空白）
            clean_text = re.sub(r'\s+', '', text)
            n_total = len(clean_text)
            if n_total < min_chars or n_total > max_chars:
                continue
            # 段数
            segs = [s.strip() for s in re.split(r'[。！？\n]+', text) if len(s.strip()) > 10]
            if len(segs) < min_segs:
                continue
            # PUA 占比
            n_pua = sum(1 for c in clean_text if is_pua(c))
            # 阙文 □
            n_que = clean_text.count('□')
            pua_ratio = n_pua / n_total if n_total > 0 else 1
            que_ratio = n_que / n_total if n_total > 0 else 1
            if pua_ratio > 0.05 or que_ratio > 0.05:
                continue
            candidates.append((n_total, kid, pua_ratio, que_ratio, clean_text[:30]))
        if len(candidates) >= 12:
            break
        max_chars += 500
        print(f"区间 {min_chars}-{max_chars} 只找到 {len(candidates)} 部，扩大上限到 {max_chars+500}")
    
    # 按字数升序
    candidates.sort()
    selected = candidates[:12]
    print(f"本批选取 {len(selected)} 部经文，字数范围 {min_chars}-{max_chars}")
    print("经号列表:")
    kids = []
    for n, kid, pr, qr, preview in selected:
        print(f"  {kid}: {n}字, PUA={pr:.3%}, 阙文={qr:.3%}")
        kids.append(kid)
    print("\n空格分隔: " + " ".join(kids))
    return kids

if __name__ == "__main__":
    main()
