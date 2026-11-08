# -*- coding: utf-8 -*-
"""第40批：把切段骨架转为 worker 翻译输入（纯文本），并按组分配。"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK = os.path.join(ROOT, "data", "baihua-tasks")
OUT  = os.path.join(ROOT, "_b40", "in")
os.makedirs(OUT, exist_ok=True)

GROUPS = {
    "W1": ["t0204", "t1055"],
    "W2": ["t0677", "t1338"],
    "W3": ["t0483", "t1197"],
    "W4": ["t0409", "t1266"],
    "W5": ["t0449", "t1079"],
    "W6": ["t1028", "t1131"],
}

def main():
    only = sys.argv[1:] or list(GROUPS)
    for w in only:
        tids = GROUPS[w]
        lines = []
        for tid in tids:
            d = json.load(open(os.path.join(TASK, tid + ".json"), encoding="utf-8"))
            segs = d["translations"]
            lines.append("===== 经号 %s | %s | %s | 共%d段 =====" % (tid, d["title"], d["translator"], len(segs)))
            for i, seg in enumerate(segs, 1):
                lines.append("[段%d]" % i)
                lines.append(seg["original_preview"].strip())
            lines.append("")
        open(os.path.join(OUT, w + ".txt"), "w", encoding="utf-8").write("\n".join(lines))
        print(w, "->", OUT + "/" + w + ".txt", "经:", tids)

if __name__ == "__main__":
    main()
