# -*- coding: utf-8 -*-
"""第63批 第二轮微调：按两路第二轮复核的遗留低项做最后订正。"""
import json, os

ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
OUT = os.path.join(ROOT, "data/modern-translation")

FIX = [
 # t1053 义解笔误
 ("t1053", 13, "龙主乃至部多等天神通皆归依称赞", "龙主乃至部多等诸类、若天若神一切王皆归依称赞", 1),
 # t0856 异体字
 ("t0856", 11, "风轮（食指）糺缠执持火轮", "风轮（食指）纠缠执持火轮", 1),
 ("t0856", 11, "风糺持火", "风纠持火", 1),
 # t0846 段9 断句夹注
 ("t0846", 9, "他们以一切庄严的果报，又堕地狱；恶精进天以那神通而作功德",
   "他们以一切庄严的果报，又堕地狱（原文作「复堕地狱、恶精进天」，句读可两读，此从一说）；恶精进天以那神通而作功德", 1),
 # t0734 段12 语气
 ("t0734", 12, "你那时应当作这样的方便，令这道人不再来乞食", "你那时便设下这样的计策，令这道人不再来乞食", 1),
 # t2831 「像」回归
 ("t2831", 12, "万象窈号无名", "万像窈号无名", 2),
 # t0696 段5 括注去重
 ("t0696", 5, "拿出五家（五家所共、易散）的财物", "拿出五家所共、易散之财物", 1),
 # t0696 段15 按语移入义解
 ("t0696", 15, "擦拭之后，自占（择时）再灌（「断后」「自占」文义晦涩，姑从字面），名叫清净灌。",
   "擦拭之后，自占（择时）再灌，名叫清净灌。", 1),
 ("t0696", 15, "成浴佛行法之完整次第。", "成浴佛行法之完整次第（「断后」「自占」文义晦涩，今姑从字面）。", 1),
]

targets = {}
for tid, seg, old, new, cnt in FIX:
    if tid not in targets:
        targets[tid] = json.load(open(os.path.join(OUT, tid + ".json"), encoding="utf-8"))
    d = targets[tid]
    m = d["translations"][seg - 1]["modern"]
    assert m.count(old) == cnt, "命中数不符 %s 段%d %r 实际%d" % (tid, seg, old, m.count(old))
    d["translations"][seg - 1]["modern"] = m.replace(old, new)

# t1209 尊名「吽迦囉」统一转简（叙述部分，非咒文出声字）
d = json.load(open(os.path.join(OUT, "t1209.json"), encoding="utf-8"))
n = d["intro"].count("吽迦囉") + sum(s["modern"].count("吽迦囉") for s in d["translations"])
d["intro"] = d["intro"].replace("吽迦囉", "吽迦啰")
for s in d["translations"]:
    s["modern"] = s["modern"].replace("吽迦囉", "吽迦啰")
targets["t1209"] = d
print("t1209 吽迦囉→吽迦啰:", n)

# t1108b 补体例说明
d = json.load(open(os.path.join(OUT, "t1108b.json"), encoding="utf-8"))
assert d["intro"].endswith("礼赞行仪。")
d["intro"] = d["intro"] + "此经礼赞偈颂中的咒音梵字，为便阅读统一转简，音读不变。"
targets["t1108b"] = d

for tid, d in targets.items():
    json.dump(d, open(os.path.join(OUT, tid + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
print("微调完成：", sorted(targets.keys()))
