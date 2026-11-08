#!/usr/bin/env python3
import os
import json
import re

def is_pua(c):
    cp = ord(c)
    return (0xF000 <= cp <= 0xF8FF) or (0xF0000 <= cp <= 0xFFFFD) or (0x100000 <= cp <= 0x10FFFD)

def main():
    project_root = "/home/user/workspace/13511660557912876654/buddhist-ontology"
    sutras_dir = os.path.join(project_root, "sutras")
    done_dir = os.path.join(project_root, "data/modern-translation")
    
    done = set()
    for fn in os.listdir(done_dir):
        if fn.endswith(".json"):
            done.add(fn[:-5])
    print(f"已完成: {len(done)}部", file=os.sys.stderr)
    
    candidates = []
    
    for fn in os.listdir(sutras_dir):
        if not fn.endswith(".json"):
            continue
        kid = fn[:-5]
        if not re.match(r'^t\d+[a-z]?$', kid):
            continue
        if kid in done:
            continue
        fp = os.path.join(sutras_dir, fn)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                s = json.load(f)
        except Exception as e:
            continue
        text = ""
        for chap in s.get("content", []):
            text += chap.get("text", "")
        clean_text = re.sub(r'\s+', '', text)
        n_total = len(clean_text)
        if n_total < 300 or n_total > 8000:
            continue
        n_pua = sum(1 for c in clean_text if is_pua(c))
        n_que = clean_text.count('□')
        if n_total == 0:
            continue
        pua_ratio = n_pua / n_total
        que_ratio = n_que / n_total
        if que_ratio > 0.05 or pua_ratio > 0.3:
            continue
        segs = [seg.strip() for seg in re.split(r'[。！？\n]+', text) if len(seg.strip()) > 5]
        if len(segs) < 3:
            continue
        candidates.append((n_total, kid))
    
    candidates.sort()
    print(f"候选总数: {len(candidates)}", file=os.sys.stderr)
    selected = candidates[:12]
    kids = [x[1] for x in selected]
    print(" ".join(kids))
    for n, kid in selected:
        print(f"{kid}: {n}字", file=os.sys.stderr)

if __name__ == "__main__":
    main()
