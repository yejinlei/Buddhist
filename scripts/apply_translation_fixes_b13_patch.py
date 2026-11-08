#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第13批修正补丁：修正在上次脚本中因换行转义而未生效的两处，以及义解引文简繁统一。"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def load(sid): return json.load(open(f"data/modern-translation/{sid}.json", encoding="utf-8"))
def save(sid, d):
    with open(f"data/modern-translation/{sid}.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def sub(d, idx, old, new, where):
    md = d["translations"][idx]["modern"]
    assert md.count(old) == 1, f"[{where}] 段{idx+1} 命中 {md.count(old)} 次"
    d["translations"][idx]["modern"] = md.replace(old, new)
    return d

# ---- t0053 段6 补译攻城之战 ----
d = load("t0053")
d = sub(d, 5,
    "他们在其中或以象斗、或以马、或以车、或以步兵、或以女人、或以男子，在其中有的死去、受死的痛苦。这就是现世的苦阴，因淫、缘淫、增上淫的缘故。\n【义解】此段由个人亲眷之争，扩大至不同阶层、种姓之间的械斗厮杀。「死死苦」即或死、或受死亡的痛苦。「贱人工师」指低贱种姓与工匠。佛以此说明贪欲引发世间普遍的争斗。",
    "他们在其中或以象斗、或以马、或以车、或以步兵、或以女人、或以男子，在其中有的死去、受死的痛苦。这就是现世的苦阴，因淫、缘淫、增上淫的缘故。这些众生因淫乃至增上淫的缘故，便穿上铠甲、手持极锋利的刀，前往极高的城池想要攻伐它。他们在其中或吹法螺、或击鼓、或大声呼喝，或用椎、或用戟、或用钺、或用利轮，或以箭相射、或投下乱石、或以弩、或以熔化的铜汁浇注，在其中有的死去、受死的痛苦。这就是现世的苦阴，因淫乃至增上淫的缘故。\n【义解】此段由个人亲眷之争，扩大至不同阶层、种姓之间的械斗厮杀，再进至象马步战与攻城之战，层层显示贪欲所引发的世间争斗之苦。「死死苦」即或死、或受死亡的痛苦。「贱人工师」指低贱种姓与工匠。",
    "t0053.段6")
save("t0053", d); print("t0053 段6 补译 OK")

# ---- t0055 段3 去越界尾句 ----
d = load("t0055")
d = sub(d, 2,
    "得到钱财之后，就守护它，心想：别让这钱财被国王夺去，别让贼盗取，别让火烧掉，别让它腐坏，别让出去经商却折了本。\n【义解】",
    "得到钱财之后，就守护它。\n【义解】",
    "t0055.段3尾")
save("t0055", d); print("t0055 段3 去越界 OK")

# ---- t0057 义解引文简繁统一 ----
d = load("t0057")
d = sub(d, 11, "「近不相於」", "「近不相于」", "t0057.段12引文")
d = sub(d, 13, "「從行致清淨無為」", "「从行致清净无为」", "t0057.段14引文")
save("t0057", d); print("t0057 引文简繁统一 OK")
print("完成")
