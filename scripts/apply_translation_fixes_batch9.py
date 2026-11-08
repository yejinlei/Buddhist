# -*- coding: utf-8 -*-
"""
第9批白话翻译修正脚本（依据 3 个独立校对 agent 的报告）
每条替换断言唯一命中，避免误改。
"""
import json, sys, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MT = os.path.join(BASE, "data", "modern-translation")

# 修正项: (经号, 字段定位, 原文片段, 替换文本)
FIXES = [
    # ---- t0655 佛說勝義空經：删除原文所无的「一味 / 味」增字 ----
    ("t0655", "modern_contains", "此外还有一味正法", "此外还有正法"),
    ("t0655", "modern_contains", "今天所说的这味正法", "今天所说的正法"),

    # ---- t0819 佛說法常住經 段6：按字面直译「無此三事，不為取證」，修正因果方向 ----
    ("t0819", "modern_contains",
     "以及空、无相、无愿；因为这三种（空、无相、无愿）而不取证（不滞于空证而中途止步），具足六种神通与善巧方便",
     "以及空、无相、无愿；若没有这三种（空、无相、无愿），便不能取证。具足六种神通与善巧方便"),
    ("t0819", "modern_contains",
     "「无此三事，不为取证」文义可解为：菩萨虽修空、无相、无愿，却不以之取证涅槃而停步，故能「六通善权」广度众生。",
     "「无此三事，不为取证」一句原文歧义较大，字面可解为「若无此三种（空、无相、无愿），便不能取证」；古今亦有不作此解者。今译文取字面直译，读者宜会通上下文。"),

    # ---- t0491 六菩薩亦當誦持經：修正语句不通「诸根寂静止静」 ----
    ("t0491", "modern_contains", "「寂根」谓诸根寂静止静", "「寂根」谓诸根寂静"),

    # ---- t0799 佛說略教誡經 段3：小标题「答谢」改「应答」（原文为「白佛言」，非答谢）----
    ("t0799", "section", "比丘答谢世尊", "比丘应答世尊"),
    ("t0799", "modern_contains", "【比丘答谢世尊】", "【比丘应答世尊】"),
]

def main():
    changed = 0
    for cid, mode, old, new in FIXES:
        fp = os.path.join(MT, f"{cid}.json")
        d = json.load(open(fp, encoding="utf-8"))
        hits = 0
        if mode == "section":
            for t in d["translations"]:
                if t.get("section") == old:
                    t["section"] = new; hits += 1
        else:  # modern_contains
            for t in d["translations"]:
                if old in t.get("modern", ""):
                    t["modern"] = t["modern"].replace(old, new); hits += 1
        if hits != 1:
            print(f"[ABORT] {cid} 命中 {hits} 次（应唯一）：{old[:30]}")
            sys.exit(1)
        json.dump(d, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        changed += 1
        print(f"[OK] {cid}: {old[:26]}... -> 已修正")
    print(f"\n共落实 {changed} 处修正")

if __name__ == "__main__":
    main()
