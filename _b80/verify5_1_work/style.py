# -*- coding: utf-8 -*-
import re
from parse import parse_review, IDS
han=re.compile(r"[\u4e00-\u9fff]")
for tid in IDS:
    segs=parse_review(tid)
    for s in segs:
        sec=s["section"]; mod=s["modern"]
        errs=[]
        if not (1<=len(sec)<=14): errs.append(f"seclen={len(sec)}")
        # section should be all han (allow no punctuation)
        nonhan=[c for c in sec if not han.match(c)]
        if nonhan: errs.append(f"sec_nonhan={nonhan}")
        if any(c in sec for c in "【】《》\"'"): errs.append("sec_char")
        if not mod.startswith("【"+sec+"】"): errs.append("head")
        if "【义解】" not in mod: errs.append("no_yijie")
        if mod.rstrip().endswith("】"): errs.append("end_brace")
        # 义解 followed by 正文
        after=mod.split("【义解】",1)
        if len(after)==2:
            tail=after[1].strip()
            if len(tail)==0: errs.append("yijie_empty")
        if '"' in mod or "'" in mod: errs.append("half_quote")
        if "`" in mod: errs.append("backtick")
        # full-width or other quote check: 「」 allowed? task says no half-width quotes & backticks
        if errs:
            print(f"!! {tid} 段{s['idx']:02d}: {errs}")
print("style scan done")
