# -*- coding: utf-8 -*-
import json
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
TR=ROOT+"/data/modern-translation"; TK=ROOT+"/data/baihua-tasks"
tk=json.load(open(TK+"/t1186.json",encoding="utf-8"))
S=tk["translations"]; pv=[s["original_preview"] for s in S]
cn=["一","二","三","四","五","六","七","八","九","十","十一","十二","十三","十四","十五","十六","十七"]
M=[]
M.append("【题记·归敬偈】西天译经三藏、朝散大夫、试光禄卿、明教大师臣法贤奉诏译。稽首顶礼最上普遍智的佛——如来、应供、正等觉：您心意清净，无与伦比，神通无碍，从未曾有，善能周遍十方世界，随众生根性化度群生。稽首顶礼文殊大导师：您善于除除尘垢，心已清净，以无量功德庄严身相，广说妙法济度群品；天龙、大力、修罗等众，全都捧足顶礼。【义解】本经为宋代法贤所译的妙吉祥（文殊）菩萨陀罗尼单行本。开篇先标译者，继以七言偈颂归敬佛与文殊，末列天龙八部捧足顶礼之相，为下文宣说陀罗尼作序。")
p1=pv[1].split("\n",1)
zhou1=p1[1] if len(p1)>1 else pv[1]
M.append(f"【妙吉祥菩萨陀罗尼（一）】妙吉祥菩萨陀罗尼曰：{zhou1}【义解】此段为妙吉祥（文殊）菩萨陀罗尼的起首，先归命妙吉祥菩萨摩诃萨，下接咒句，咒文与音注皆照录原文用字，不改一字。")
for i in range(2,17):
    M.append(f"【妙吉祥菩萨陀罗尼（{cn[i-1]}）】咒文续：{pv[i]}【义解】咒文续句，照录原文用字与音注，不改一字。")
M.append(f"【妙吉祥菩萨陀罗尼（十七）·结咒】咒文末段：{pv[17]}【义解】陀罗尼至此以「娑嚩贺」圆满收结，全咒共九十七句，皆照录原文用字，不改一字。")
assert len(M)==len(S),(len(M),len(S))
for m in M:
    assert m.startswith("【") and "【义解】" in m and not m.rstrip().endswith("【义解】"), m[:20]
out={"id":"t1186","title":tk["title"],"translator":tk["translator"],"mode":"baihua",
 "intro":"《佛说妙吉祥菩萨陀罗尼》一卷，宋代法贤译。本经为妙吉祥（文殊）菩萨陀罗尼的单行译本，前有七言归敬偈，后为九十七句陀罗尼全文，为宋代密教文殊信仰的重要持诵经典。",
 "sutraPath":"sutras/t1186.json","translations":[]}
for i,s in enumerate(S):
    out["translations"].append({"section":s.get("section",""),"original_preview":s["original_preview"],"modern":M[i]})
json.dump(out,open(TR+"/t1186.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
print("t1186 写入完成 段=",len(M))
