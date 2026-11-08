# -*- coding: utf-8 -*-
"""第55批校对修正（幂等）：old→new；若 old 不存在而 new 已存在则视为已应用。"""
import json, os
TR="/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation"
def load(t): return json.load(open(os.path.join(TR,t+".json"),encoding="utf-8"))
def save(t,d): json.dump(d,open(os.path.join(TR,t+".json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
def rep(d, old, new, cnt=None):
    oh=sum(s["modern"].count(old) for s in d["translations"])
    nh=sum(s["modern"].count(new) for s in d["translations"])
    if oh==0 and nh>0:
        return  # 已应用
    assert oh>0, f"未找到 {old!r}"
    for s in d["translations"]:
        s["modern"]=s["modern"].replace(old,new)

# t0963
d=load("t0963")
rep(d,"画那设都嚕（此云怨敌）之形","画那设都嚕（怨敌）之形")
rep(d,"或临逼帝座","或临帝座")
rep(d,"想相谋害","欲相谋害")
for s in d["translations"]:
    if "曩謨三滿跢" in s["modern"]:
        s["modern"]=s["modern"].replace("(","（").replace(")","）").replace("上声","上聲")
rep(d,"以及于忿怒像前画怨敌形加持以转移灾障。","以及于忿怒像前画设都嚕（意即怨敌）之形、加持以转移灾障。")
save("t0963",d)

# t1077
d=load("t1077")
rep(d,"「七俱胝佛母」意为过去七亿（俱胝＝亿）诸佛之母，指准提菩萨所证之般若、能生诸佛；此经是准提法的根本经典之一。",
      "「七俱胝佛母」中「俱胝」为古印度大数之名，此经是准提法的根本经典之一。")
rep(d,"用瞿摩夷（牛粪，净物）涂地作成方坛","用瞿摩夷涂地作成方坛")
rep(d,"阿鉢罗是多菩萨","阿钵罗是多菩萨")
rep(d,"或见受菩提之记","或见与受菩提之记")
for s in d["translations"]:
    if "南謨颯哆南" in s["modern"]:
        s["modern"]=s["modern"].replace("(","（").replace(")","）")
rep(d,"【义解】此段是准提法的具体事修：坛场结界","【义解】「瞿摩夷」即牛粪制成之净物，密法用以涂坛。此段是准提法的具体事修：坛场结界")
save("t1077",d)

# t1261
d=load("t1261")
rep(d,"烧上香一千零八遍","烧上香一八遍")
rep(d,"一千零八遍","一千八遍")
rep(d,"一千零八十遍","一千八十遍")
rep(d,"一百零八遍","一百八遍")
rep(d,"阇伽香水","閼伽香水")
rep(d,"数目（一百零八、一千零八十、一千零八、七夜）皆依原文。","数目（一百八、一千八十、一千八、七夜）皆依原文。")
save("t1261",d)

# t1158
d=load("t1158")
rep(d,"戒方（无名指）向内掌中来往","戒方向内掌中来往")
rep(d,"禅（右）、智（左）二指竖立来往","禅、智二指竖立来往")
rep(d,"进（食指）、力（无名指）二指竖立来往","进、力二指竖立来往")
save("t1158",d)

# t0804
d=load("t0804")
rep(d,"那别离之痛还说得过去，亲姻也须啼泣","那别离之痛尚且难忍，亲人也须啼泣")
save("t0804",d)
print("=== fix55 done ===")
