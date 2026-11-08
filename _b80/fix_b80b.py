# -*- coding: utf-8 -*-
import json
BASE="/home/user/workspace/13511660557912876654/buddhist-ontology"
TR=BASE+"/data/modern-translation"
def load(t): return json.load(open(f"{TR}/{t}.json",encoding="utf-8"))
def save(t,o): json.dump(o,open(f"{TR}/{t}.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)

# 1. t1612 段0 SECTION 去「·」
o=load("t1612"); s=o["translations"][0]
assert s["section"]=="论主与译者·总标五蕴"
s["section"]="论主译者总标五蕴"
s["modern"]=s["modern"].replace("【论主与译者·总标五蕴】","【论主译者总标五蕴】",1); save("t1612",o)

# 2. t2031 段29/33 同步删「欲」
o=load("t2031")
for i in (29,33):
    assert "在欲天中住梵行的人" in o["translations"][i]["modern"], i
    o["translations"][i]["modern"]=o["translations"][i]["modern"].replace("在欲天中住梵行的人","在天中住梵行的人")
save("t2031",o)

# 3. t0454 义解省略号引文加「（节引）」
o=load("t0454")
for i,old,new in [
  (15,"「蠰佉王亦共八萬四千大臣……出家學道」，显示","「蠰佉王亦共八萬四千大臣……出家學道」（节引），显示"),
  (25,"「初會說法……第二大會……第三大會」，即著名","「初會說法……第二大會……第三大會」（节引），即著名"),
  (28,"「魔王……覺諸人民」，此中魔王劝人精进","「魔王……覺諸人民」（节引），此中魔王劝人精进")]:
    assert old in o["translations"][i]["modern"], (i,old[:20])
    o["translations"][i]["modern"]=o["translations"][i]["modern"].replace(old,new)
save("t0454",o)

# 4. t1165 段14 补承上引号
o=load("t1165"); s=o["translations"][14]
assert s["modern"].startswith("【香印涂香印与其咒】那时")
s["modern"]=s["modern"].replace("【香印涂香印与其咒】那时","【香印涂香印与其咒】」那时",1); save("t1165",o)

# 5. t1920 段6 平行句统一
o=load("t1920"); s=o["translations"][6]
assert "退失转堕而令他人诽谤" in s["modern"]
s["modern"]=s["modern"].replace("退失转堕而令他人诽谤","退转退堕而令他人诽谤"); save("t1920",o)

# 6. t2055 段31 义解统一「瞻蔔」
o=load("t2055"); s=o["translations"][31]
assert "「瞻蔔」即瞻卜花" in s["modern"]
s["modern"]=s["modern"].replace("「瞻蔔」即瞻卜花","「瞻蔔」即瞻蔔花"); save("t2055",o)

print("低危清理完成")
