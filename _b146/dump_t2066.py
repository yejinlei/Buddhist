#!/usr/bin/env python3
import json, re
from pathlib import Path
ROOT = Path(__file__).parent.parent
d = json.loads((ROOT/"sutras/t2066.json").read_text("utf-8"))
paras = []
for item in d.get("content", []):
    t = item["text"]
    if re.match(r'^卷[0-9上下中]+$', t.strip()):
        continue
    t_clean = re.sub(r'\s+', '', t)
    if len(t_clean) < 20:
        continue
    paras.append(t_clean)
task = {"tid":"t2066","title":d["title"],"tr":d.get("translator",""),"paras":paras}
(ROOT/"data/baihua-tasks/t2066.json").write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"t2066 {d['title']} {d.get('translator','')} {len(paras)}段 {sum(len(p) for p in paras)}字")
print("="*60)
for i,p in enumerate(paras,1):
    print(f"\n---[{i}]---")
    print(p[:400])
