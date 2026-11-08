# -*- coding: utf-8 -*-
import json
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
TR=ROOT+"/data/modern-translation"
def load(sid): return json.load(open(f"{TR}/{sid}.json",encoding="utf-8"))
def save(sid,d): json.dump(d,open(f"{TR}/{sid}.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
def rep(s,old,new,n=1):
    assert s.count(old)==n, (old[:30], s.count(old))
    return s.replace(old,new)
log=[]
# ---- 去重复【义解】----
def dedup(m):
    parts=m.split("【义解】")
    if len(parts)<=2: return m,0
    return parts[0]+"【义解】"+"".join(parts[1:]), 1
for sid in ["t0738","t0812","t0828"]:
    d=load(sid); c=0
    for s in d["translations"]:
        s["modern"],n=dedup(s["modern"]); c+=n
    save(sid,d); log.append(f"{sid} 去重复【义解】 {c} 段")

# ---- t0726 intro 补「朝散大夫」----
d=load("t0726")
d["intro"]=rep(d["intro"],"宋代西天译经三藏、试鸿胪少卿","宋代西天译经三藏、朝散大夫、试鸿胪少卿")
save("t0726",d); log.append("t0726 intro 补『朝散大夫』")

# ---- t0731 ----
d=load("t0731"); S=d["translations"]
S[2]["modern"]=rep(S[2]["modern"],"则为人贞疾（安康）","则为人安康（原文作「贞疾」，此字存疑）")
S[2]["modern"]=rep(S[2]["modern"],"更加贞疾","更加安康（原文亦作「贞疾」）")
S[13]["modern"]=rep(S[13]["modern"],"【义解】（以上八火犁说毕。）","【义解】（编者按：以上八火犁说毕。）")
S[22]["modern"]=rep(S[22]["modern"],"小人必定长受生死","小人则必定长久受生（按：原文作「小人必长生」，义存疑）")
S[22]["modern"]=rep(S[22]["modern"],"，（若能如此，）便应当远离忧患","，便应当远离忧患")
save("t0731",d); log.append("t0731 修订 seg2/13/22")

# ---- t0737 ----
d=load("t0737"); S=d["translations"]
S[3]["modern"]=rep(S[3]["modern"],"使之意意欣悦","使之欣悦")
S[28]["modern"]=rep(S[28]["modern"],"诸比丘闻经欢喜，信受奉行。","诸比丘闻经欢喜（按：原文止于「闻经欢喜」，「信受奉行」为诸经通例结语，原文所无）。")
save("t0737",d); log.append("t0737 修订 seg3/28")

# ---- t0738 ----
d=load("t0738"); S=d["translations"]
S[24]["modern"]=rep(S[24]["modern"],"五浊末法之世","五末（末法）之世")
tot=0
for s in S:
    tot+=s["modern"].count("真言"); s["modern"]=s["modern"].replace("真言","真实之法")
# 繁体字
for s in S:
    for a,b in [("嗎","吗"),("夠","够"),("藉","借")]:
        s["modern"]=s["modern"].replace(a,b)
save("t0738",d); log.append(f"t0738 修订 seg24/真言({tot}处)/繁体字")

# ---- t0812 seg9 存疑 ----
d=load("t0812"); S=d["translations"]
S[9]["modern"]=rep(S[9]["modern"],"没有能伤害佛身的。","没有能伤害佛身的（「鞈」字罕见，疑为讹字，存疑）。")
save("t0812",d); log.append("t0812 seg9 补存疑")

# ---- t0828 ----
d=load("t0828"); S=d["translations"]
S[5]["modern"]=rep(S[5]["modern"],"大势至、观世自在菩萨，为无量梵众所围绕","得大势至、观世自在菩萨，为无量梵众所围绕")
S[9]["modern"]=rep(S[9]["modern"],"即指下文「何者一法」的「一法」二字","或谓指「如来」二字，或谓指下文「何者一法」之「一法」二字，姑并存之")
S[22]["modern"]=rep(S[22]["modern"],"何况多说而无利益。这时","何况多说而无利益（此句文义晦涩，疑有讹脱，姑存疑）。这时")
save("t0828",d); log.append("t0828 修订 seg5/9/22")

# ---- t0845 intro ----
d=load("t0845")
d["intro"]=rep(d["intro"],"经中尊那长者问佛","经中大尊者尊那问佛")
save("t0845",d); log.append("t0845 intro 长者→大尊者")

# ---- t1011 ----
d=load("t1011"); S=d["translations"]
S[0]["modern"]=rep(S[0]["modern"],"此经题为《佛说无量门微密持经》，由吴月支优婆塞支谦译出。","（此经题作《佛说无量门微密持经》）由吴月支优婆塞支谦译出。")
S[1]["modern"]=rep(S[1]["modern"],"闚音菩萨","窥音菩萨")
S[5]["modern"]=rep(S[5]["modern"],"无所罣碍","无所挂碍")
save("t1011",d); log.append("t1011 修订 seg0/1/5")

# ---- t1297 seg7 补译 ----
d=load("t1297"); S=d["translations"]
old="此天瞋怒时，刀兵交战，地居的诸王……（此处文义疑有脱误，「皆悉安」上疑脱「不」字，姑照原文译出。原文作「地居诸王皆悉安」。）"
new="此天瞋怒时，刀兵交战，地居诸王皆得安稳（按：原文作「地居诸王皆悉安」，文义疑有脱误，「皆悉安」上或脱「不」字，姑依字面译出）。"
S[7]["modern"]=rep(S[7]["modern"],old,new)
S[20]["modern"]=rep(S[20]["modern"],"（此为经中譬喻之语）","（此句费解，原文疑有讹脱，姑存待考）")
save("t1297",d); log.append("t1297 seg7 补译/seg20 存疑")

# ---- t1755 ----
d=load("t1755"); S=d["translations"]
d["intro"]="《阿弥陀经义记》，旧题隋代天台智者大师（智顗）说、门人记；作者归属学界存疑，且此记未入中国历代大藏经（仅见日本《卍续藏》与《大正藏》）。此记为《阿弥陀经》的疏释，依五重玄义与序、正、流通三段科判，阐发净土依正二报与往生之旨。"
for s in S:
    s["modern"]=s["modern"].replace("鸜","鸲").replace("麁","粗").replace("𫖮","顗")
S[21]["modern"]=rep(S[21]["modern"],"若善男信女听闻此经之名","若男女听闻此经之名")
save("t1755",d); log.append("t1755 intro补注/异体字/seg21")

# ---- t2757 intro 补来源 ----
d=load("t2757")
d["intro"]="《华严经疏卷第三》，新罗元晓撰（作者归属存疑），为《华严经·如来光明觉品》的疏释，依十重光明遍照与各方法门逐段科判经文、赞佛功德。此疏收于《大正藏》第八十五册「古逸部」（敦煌古逸文献系统）。卷末附有宽文十年（日本）写本题记。"
save("t2757",d); log.append("t2757 intro 补文献来源")

print("\n".join(log))
