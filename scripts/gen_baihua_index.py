# -*- coding: utf-8 -*-
"""扫描 data/modern-translation/*.json，同步更新 pages/sutras.html 中的
BAIHUA_AVAILABLE 白话可用经目清单，避免手工维护漏挂。
用法：python3 scripts/gen_baihua_index.py
"""
import os, re, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MT = os.path.join(BASE, "data", "modern-translation")
PAGE = os.path.join(BASE, "pages", "sutras.html")


def collect():
    ids = []
    for fn in sorted(os.listdir(MT)):
        if not fn.endswith(".json"):
            continue
        try:
            json.load(open(os.path.join(MT, fn), encoding="utf-8"))
            ids.append(fn[:-5])
        except Exception as e:
            print(f"跳过非法 JSON {fn}: {e}")
    return ids


def main():
    ids = collect()
    idset = "[" + ",".join(f"'{i}'" for i in ids) + "]"
    s = open(PAGE, encoding="utf-8").read()
    pat = re.compile(r"const BAIHUA_AVAILABLE = new Set\(\[[^\]]*\]\);")
    assert pat.search(s), "未找到 BAIHUA_AVAILABLE 行"
    s = pat.sub(f"const BAIHUA_AVAILABLE = new Set({idset});", s, count=1)
    open(PAGE, "w", encoding="utf-8").write(s)
    print(f"已同步 {len(ids)} 部：{', '.join(ids)}")


if __name__ == "__main__":
    main()
