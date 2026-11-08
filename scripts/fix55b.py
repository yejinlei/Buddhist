# -*- coding: utf-8 -*-
"""第55批二轮修正：咒文照录对齐、t2848 清理。"""
import json, os
T="/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation"
def load(t): return json.load(open(os.path.join(T,t+".json"),encoding="utf-8"))
def save(t,d): json.dump(d,open(os.path.join(T,t+".json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)

# t0963 咒段：用原文 preview 精确重建咒文行
d=load("t0963"); seg=d["translations"][2]
pv=seg["original_preview"].strip()
head="【陀罗尼正文】\n（陀罗尼依唐音音译，不作义译，谨照录如下。）\n"
seg["modern"]=head+pv+"\n"+seg["modern"][seg["modern"].find("【义解】"):]
save("t0963",d)

# t1077 咒段
d=load("t1077"); seg=d["translations"][1]
pv=seg["original_preview"].strip()
head="【准提陀罗尼】\n（陀罗尼依唐音音译，不作义译，谨照录如下。）\n"
seg["modern"]=head+pv+"\n"+seg["modern"][seg["modern"].find("【义解】"):]
save("t1077",d)

# t1261 咒段
d=load("t1261"); seg=d["translations"][1]
pv=seg["original_preview"].strip()
head="【心真言】\n（陀罗尼依唐音音译，不作义译，谨照录如下。）\n"
seg["modern"]=head+pv+"\n"+seg["modern"][seg["modern"].find("【义解】"):]
save("t1261",d)

# t1158 咒文行：半角括号→全角（仅该段）
d=load("t1158"); seg=d["translations"][1]
seg["modern"]=seg["modern"].replace("(二合)","（二合）").replace("(","（").replace(")","）")
save("t1158",d)

# t2848：删多余省略号、繁体「闌」→「阑」
d=load("t2848")
for s in d["translations"]:
    s["modern"]=s["modern"].replace("……","").replace("澄闌","澄阑")
save("t2848",d)

print("=== fix55b done ===")
