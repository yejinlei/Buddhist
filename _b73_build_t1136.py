# -*- coding: utf-8 -*-
import json
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
TR=ROOT+"/data/modern-translation"; TK=ROOT+"/data/baihua-tasks"
h2s=json.load(open(ROOT+"/data/hant2simp_full.json",encoding="utf-8"))
def simp(s): return "".join(h2s.get(c,c) for c in s)
def simp_protect(s, spans):
    # 先按 spans 切分，非 span 段转简
    parts=[s]
    for sp in spans:
        np=[]
        for p in parts:
            if sp in p:
                idx=p.index(sp); np += [p[:idx], sp, p[idx+len(sp):]]
            else: np.append(p)
        parts=np
    return "".join(p if p in spans else simp(p) for p in parts)

tk=json.load(open(TK+"/t1136.json",encoding="utf-8"))
pv=[s["original_preview"] for s in tk["translations"]]
old=json.load(open(TR+"/t1136.json",encoding="utf-8"))["translations"]
def om(i): return old[i]["modern"]

mods=[]
# 段0/1 纯白话
mods.append(simp(om(0)))
mods.append(simp(om(1)))
# 段2 纯咒文
mods.append("【宣说神咒（一）】世尊即说金刚寿命陀罗尼曰："+pv[2]+"【义解】此段为金刚寿命陀罗尼的开端，先归敬诸佛菩萨，下接“怛儞也他”（即说咒曰）转入咒体，咒文与音注皆照录原文用字，不改一字。")
# 段3 纯咒文
mods.append("【宣说神咒（二）】咒文续："+pv[3]+"【义解】咒文续句，仍照录原文用字与音注，不改一字。")
# 段4 咒文+白话
idx=pv[4].find("」"); zhou=pv[4][:idx+1]
pr4=om(4); j=pr4.find("」")
mods.append("【神咒宣毕】"+zhou+simp(pr4[j+1:])+"【义解】咒文至此圆满宣毕，大地山河震动、地狱摧碎，病苦众生当即苏息，显此陀罗尼之效力。")
# 段5-9 纯白话
for i in (5,6,7,8,9):
    mods.append(simp(om(i)))
# 段10-13 混合：保护咒文 span
prot={10:["唵嚩日羅（二合）諭勢吽吽尸棄娑嚩（二合）賀"],
      11:["唵嚩日囉（二合）諭勢。濕吠帝濕吠帝濕吠多隷理娑嚩（二合）賀"],
      12:["唵嚩日羅（二合）諭勢摩蹬儗摩蹬儗摩蹬儗儞輸摩輸謀嚩（二合）賀"],
      13:["唵嚩日羅（二合）諭勢者理者理者理隷","唵嚩日羅（二合）諭勢未臨嚩嚩嚩娑嚩（二合）"]}
for i in (10,11,12,13):
    mods.append(simp_protect(om(i), prot[i]))
# 段14 咒尾“賀」”保护
mods.append(simp_protect(om(14), ["賀"]))
# 段15 纯白话
mods.append(simp(om(15)))

assert len(mods)==len(tk["translations"]), (len(mods),len(tk["translations"]))
out={"id":"t1136","title":tk["title"],"translator":tk["translator"],"mode":"baihua",
     "intro":"《佛说一切诸如来心光明加持普贤菩萨延命金刚最胜陀罗尼经》一卷，唐代不空译。本经为密教延命法门的单行译本，说普贤菩萨承诸佛心印宣说金刚寿命陀罗尼，并及造像、建坛、持诵仪轨与天王护持、受持功德。",
     "sutraPath":"sutras/t1136.json","translations":[]}
for i,s in enumerate(tk["translations"]):
    out["translations"].append({"section":s.get("section",""),
        "original_preview":s["original_preview"],"modern":mods[i]})
json.dump(out,open(TR+"/t1136.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
ntr=sum(1 for m in mods for c in m if c in h2s)
print("t1136 写入完成 段=",len(mods),"剩余可转简字数=",ntr)
