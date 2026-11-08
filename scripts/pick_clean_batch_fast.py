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
    
    skip_list = {
        "t2841","t1186","t1975","t2743","t2901","t0924","t0917","t2002b","t1202","t1880",
        "t2150","t1101","t2070","t1603","t1088","t2765","t2160","t1948","t1134","t1310",
        "t1108","t1516","t2168","t0438","t1253","t0974c","t2907","t2908","t2178","t2180",
        "t2867","t2057","t1146","t1409","t2093","t2745","t2144","t1073","t1273","t1220",
        "t1204","t0913","t1400","t0922","t2869","t1232","t1137","t1370","t1045a","t1408"
    }
    
    candidates = []
    
    for fn in os.listdir(sutras_dir):
        if not fn.endswith(".json"):
            continue
        kid = fn[:-5]
        if not re.match(r'^t\d+[a-z]?$', kid):
            continue
        if kid in done or kid in skip_list:
            continue
        fp = os.path.join(sutras_dir, fn)
        size = os.path.getsize(fp)
        # 400字≈1200字节，5000字≈15000字节
        if size < 1200 or size > 15000:
            continue
        try:
            with open(fp, "r", encoding="utf-8") as f:
                s = json.load(f)
        except:
            continue
        text = ""
        for chap in s.get("content", []):
            text += chap.get("text", "")
        clean_text = re.sub(r'\s+', '', text)
        n_total = len(clean_text)
        if n_total < 400 or n_total > 5000:
            continue
        segs = [seg.strip() for seg in re.split(r'[。！？\n]+', text) if len(seg.strip()) > 10]
        if len(segs) < 3:
            continue
        n_pua = sum(1 for c in clean_text if is_pua(c))
        n_que = clean_text.count('□')
        if n_total == 0:
            continue
        pua_ratio = n_pua / n_total
        que_ratio = n_que / n_total
        # 阙文超过5%剔除，梵文悉昙字PUA允许（咒文原字照录）
        if que_ratio > 0.05 or pua_ratio > 0.05:
            continue
        segs = [seg.strip() for seg in re.split(r'[。！？\n]+', text) if len(seg.strip()) > 5]
        if len(segs) < 3:
            continue
        candidates.append((n_total, kid))
    
    candidates.sort()
    selected = []
    for n, kid in candidates:
        segs_ok = True
        # 重新读一下段数确认
        fp = os.path.join(sutras_dir, kid + ".json")
        with open(fp, "r", encoding="utf-8") as f:
            s = json.load(f)
        text = ""
        for chap in s.get("content", []):
            text += chap.get("text", "")
        segs = [seg.strip() for seg in re.split(r'[。！？\n]+', text) if len(seg.strip()) > 10]
        if len(segs) < 3:
            continue
        selected.append((n, kid))
        if len(selected) >= 12:
            break
    kids = [x[1] for x in selected]
    print(" ".join(kids))
    for n, kid in selected:
        print(f"{kid}: {n}字", file=os.sys.stderr)

if __name__ == "__main__":
    main()
