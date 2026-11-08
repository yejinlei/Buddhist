# -*- coding: utf-8 -*-
import json
ROOT="/home/user/workspace/13511660557912876654/buddhist-ontology"
def load(s): return json.load(open(f'{ROOT}/data/modern-translation/{s}.json',encoding='utf-8'))
def save(s,d): json.dump(d,open(f'{ROOT}/data/modern-translation/{s}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)

def rep(sid, seg_idx1, old, new, where='modern'):
    d=load(sid); s=d['translations'][seg_idx1-1]; t=s[where]
    assert t.count(old)==1, (sid, seg_idx1, old[:30], t.count(old))
    s[where]=t.replace(old,new); save(sid,d); 
    print(f"OK {sid} 段{seg_idx1}[{where}]: {old[:18]} -> {new[:18]}")

# --- t0593 咒文回正 ---
d=load('t0593')
cm="南谟释迦牟奈曳　怛他揭多也　阿罗𠿒帝三藐三勃陀也　怛姪他唵　苫谜苫谜萨婆波跛　钵罗苫末泥（去）"
om="南謨釋迦牟奈曳　怛他揭多也　阿羅𠿒帝三藐三勃陀也　怛姪他唵　苫謎苫謎薩婆波跛　鉢羅苫末泥（去）"
s18=d['translations'][17]['modern']; assert cm in s18
s18=s18.replace(cm,om).replace("「陀罗尼」","「陀羅尼」")
d['translations'][17]['modern']=s18
s19=d['translations'][18]['modern'].replace("莎诃","莎訶"); d['translations'][18]['modern']=s19
save('t0593',d); print("t0593 咒文回正 OK")

# --- 逐段修正 ---
rep('t0593',2,"「勝光天子」即波斯匿王之子。","「勝光天子」即波斯匿王（勝軍王）。")
rep('t0516',0,"","") if False else None
rep('t0556',10,"七女请往冢间遊观","七女请往冢间游观")
rep('t0556',10,"七女请往冢间遊观","七女请往冢间游观",where='section')
rep('t0831',11,"逕回面顷","径回面顷")
rep('t0831',11,"「逕回面顷」","「径回面顷」")
rep('t0784',23,"「若我不去想你，欲念又从何而生？我都是由思与想才生起（欲念）；我不思想你，那欲念就不生起了。」",
               "「欲啊，我知你的根本：你由思想而生；我不思想你，你就不会生起。」")
rep('t0784',6,"又止息其（向善之）心","又顿然止住其心")
rep('t0784',9,"有人质问道","質（人名）问道")
rep('t0470',6,"过去如来（的法）不可得、未来如来的不可得、现在如来不可得","过去如来不可得、未来如来不可得、现在如来不可得")
rep('t0470',30,"以七宝充满三千大千世界而行布施","以宝物充满三千界（三千大千世界）而行布施")
rep('t0709',1,"今天世尊看见稻苗","今天世尊看见稻芉")
rep('t0709',1,"「稻芉（稻苗）」","「稻芉（稻秆、禾茎）」")
rep('t0709',12,"种与芽的名、相各不相同，所以不一。」","种与芽的名、相各不相同之故。」")
rep('t1657',8,"即使一座佛塔（佛图嗢波柁）","每一座佛塔（佛图嗢波柁）")
rep('t0074',2,"因为那人心求富贵和快乐的缘故，只为自身，所以福报不广。","因为那人的心只求富贵和快乐。")
rep('t0556',19,"「卿」为第二人称的敬称（犹「您」）","「卿」为第二人称代称")
print("全部修正完成")
