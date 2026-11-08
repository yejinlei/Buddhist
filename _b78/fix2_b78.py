# -*- coding: utf-8 -*-
import json, re
TR="data/modern-translation"
def load(t): return json.load(open(f"{TR}/{t}.json",encoding="utf-8"))
def save(t,d): json.dump(d,open(f"{TR}/{t}.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)

# ---- 1) 全部12部：section 与 modern 首部【】标题同步 ----
changed=[]
for t in "t2090 t1031 t1156 t1639 t1947 t2776 t0900 t1149 t1743 t1692 t1627 t2044".split():
    d=load(t)
    for i,s in enumerate(d["translations"]):
        m=re.match(r'^【(.+?)】',s["modern"])
        if m and s.get("section")!=m.group(1):
            changed.append((t,i,s.get("section"),m.group(1))); s["section"]=m.group(1)
    save(t,d)
print("section 同步:",len(changed),"处")
for c in changed: print("   ",c)

# ---- 2) t1627 段30 补漏译整句 ----
d=load("t1627"); T=d["translations"]
old="而国、宋两本与彼丹本文句虽有差异，义理则无不同，【义解】"
assert T[30]["modern"].count(old)==1
T[30]["modern"]=T[30]["modern"].replace(old,"而国、宋两本与彼丹本文句虽有差异，义理则无不同，必定是开元之后后代的改译（重译）；【义解】")
save("t1627",d); print("t1627 段30 补漏译「必是开元之后后代的改译」")

# ---- 3) t1031 段9 繁转简 ----
d=load("t1031"); assert d["translations"][9]["modern"].count("跳躑")==1
d["translations"][9]["modern"]=d["translations"][9]["modern"].replace("跳躑","跳踯")
save("t1031",d); print("t1031 段9 跳躑→跳踯")

# ---- 4) t1149 段11 繁转简 ----
d=load("t1149"); n=d["translations"][11]["modern"].count("世間")
d["translations"][11]["modern"]=d["translations"][11]["modern"].replace("世間","世间")
save("t1149",d); print(f"t1149 段11 世間→世间 ({n}处)")

# ---- 5) t1639 段8 「同一等法」回正为「又如一等法」 ----
d=load("t1639"); assert d["translations"][8]["modern"].count("同一等法的虚妄分别")==1
d["translations"][8]["modern"]=d["translations"][8]["modern"].replace("同一等法的虚妄分别","又如「一等法」的虚妄分别")
save("t1639",d); print("t1639 段8 同一等法→又如一等法")

# ---- 6) t1156 段19/20/21 标题补「歟」以合原文 ----
d=load("t1156"); T=d["translations"]
def rep(i,o,nw):
    assert T[i]["modern"].count(o)==1, (i,o)
    T[i]["modern"]=T[i]["modern"].replace(o,nw)
rep(20,"5《一切如来灌顶真言印》（第五）：","5《一切如来灌顶真言印》（第五歟）：")
rep(20,"6《一切如来结界真言印》（第六）：","6《一切如来结界真言印》（第六歟）：")
rep(21,"7《一切如来心中心真言印》（第七）：","7《一切如来心中心真言印》（第七歟）：")
# 标题同步 section
for i in (19,20,21):
    m=re.match(r'^【(.+?)】',T[i]["modern"]); T[i]["section"]=m.group(1)
save("t1156",d); print("t1156 段20/21 标题补「歟」")

# ---- 7) t2090 专名繁转简 + 「国中之」订正 ----
d=load("t2090")
repl=[("国中之大德三藏法师","国之大德三藏法师"),
      ("毘左耶訖多","毗左耶讫多"),("薩迦般羅訶郍","萨迦般罗诃那"),("娑迦耶幾郍","娑迦耶几那"),
      ("宋多紇恭娘寺","宋多纥恭娘寺"),("犛牛","牦牛"),("紖","纼"),
      ("大乾陀羅國","大乾陀罗国"),("婆羅行國","婆罗行国")]
cnt=0
for s in d["translations"]:
    for o,nw in repl:
        c=s["modern"].count(o)
        if c: s["modern"]=s["modern"].replace(o,nw); cnt+=c
    for i in range(len(d["translations"])):
        pass
# section 里若含繁简也同步
for s in d["translations"]:
    for o,nw in repl:
        if o in s["section"]: s["section"]=s["section"].replace(o,nw)
save("t2090",d); print(f"t2090 专名/用字订正 {cnt} 处")

print("第二轮修正完成")
