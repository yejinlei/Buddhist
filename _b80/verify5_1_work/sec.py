# -*- coding: utf-8 -*-
import re
from parse import parse_review, IDS
han=re.compile(r"[\u4e00-\u9fff]")
for tid in IDS:
    segs=parse_review(tid)
    out=[]
    for s in segs:
        sec=s["section"]
        nonhan=[c for c in sec if not han.match(c)]
        flag=" <== NONHAN:"+ "".join(nonhan) if nonhan else ""
        out.append(f"{s['idx']:02d}({len(sec)}){sec}{flag}")
    print(tid, " | ".join(out))
