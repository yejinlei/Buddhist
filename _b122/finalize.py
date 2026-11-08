# -*- coding: utf-8 -*-
# 简体化：把 intro 与各段 modern 中的繁体转为简体；⟪...⟫ 内的咒文原字保留。
# section 取 modern 首个【...】标题（含括号）。
import json, re, sys
tab = json.load(open("sutras/hant2simp.json", encoding="utf-8"))
def conv(s):
    out = []; protect = False
    for ch in s:
        if ch == "⟪": protect = True; continue
        if ch == "⟫": protect = False; continue
        out.append(ch if protect else tab.get(ch, ch))
    return "".join(out)
for tid in sys.argv[1:]:
    p = f"data/modern-translation/{tid}.json"
    d = json.load(open(p, encoding="utf-8"))
    d["intro"] = conv(d["intro"])
    for s in d["translations"]:
        s["modern"] = conv(s["modern"])
        m = re.match(r"^(【[^】]+】)", s["modern"])
        s["section"] = m.group(1) if m else s.get("section", "")
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(tid, "已简体化(咒文受保护)")
