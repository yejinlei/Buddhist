# -*- coding: utf-8 -*-
"""第54批修正：① 白话与标题繁转简；② 落实 3 路校对员的真实意见（高/中/低）。"""
import json, os, sys
from opencc import OpenCC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TR = os.path.join(ROOT, "data", "modern-translation")
cc = OpenCC("t2s")

TIDS = ["t1601", "t1872", "t2861", "t1886", "t1570", "t0617"]


def load(tid):
    return json.load(open(os.path.join(TR, tid + ".json"), encoding="utf-8"))


def save(d):
    json.dump(d, open(os.path.join(TR, d["id"] + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


# ---- ① 繁转简（只改 modern 与 section，preview 原文一字不动）----
for tid in TIDS:
    d = load(tid)
    for s in d["translations"]:
        s["modern"] = cc.convert(s["modern"])
        s["section"] = cc.convert(s["section"])
    save(d)
print("① 繁转简完成：", TIDS)


# ---- ② 针对性修正 ----
def rep(tid, idx, old, new, must=True):
    d = load(tid)
    m = d["translations"][idx]["modern"]
    if old not in m:
        print(f"  !! 未找到 [{tid} 段{idx+1}] {old[:30]!r}", "（跳过）" if not must else "（需人工）")
        return
    assert m.count(old) == 1, f"{tid} 段{idx+1} 非唯一: {old[:30]!r}"
    d["translations"][idx]["modern"] = m.replace(old, new)
    save(d)


# t1601
rep("t1601", 3, "引起、连缚、现前——", "引起、连缚、现前、苦果故——")          # 补「苦果故」
rep("t1601", 6, "不如理、不生善根、不起正思惟", "不如理、不生、不起正思惟")        # 去增译
rep("t1601", 8, "修念、智、思、舍。已种顺解脱分",
    "修念、智、思、舍，记言、觉沉掉、伏行灭等流。已种顺解脱分")                     # 补半颂
rep("t1601", 8, "故道支成八。有倒而顺无倒",
    "故道支成八；表见、戒远离、令他深信受，对治本随惑及自在障之故。有倒而顺无倒")     # 补半颂
rep("t1601", 10, "随障灭", "顺障灭")                                        # 顺/随

# t1872：段10 补译日本校勘题记
rep("t1872", 9, "末段为日本明治二十四年（1891）求律沙门智海在唐招提寺的校勘题记，非经文正文，附此以存原貌。",
    "末附日本校勘题记（白话）：时为明治二十四年卯五月，我在南山留学之际，于释迦文院宝库中检出此书；偶接慈母四大不调之急报，欲直接下山探病，乃祈愿母亲平愈，敬于三宝前速写完毕。南都唐招提寺末资、求律沙门智海（五夏），五月十七日。此为校勘题记，非经文正文，附此以存原貌。")

# t2861
rep("t2861", 1, "三祖末田地（胎衣尊者）", "三祖商那和修（意译「胎衣」，即胎衣尊者）")
rep("t2861", 2, "其性非「十七」（非十七种邪见所摄），悟在刹那。",
    "「性非十七」，悟在刹那（颂古简语：或指其年非十七，或指非十七种所摄；语意含蓄，今存原语不作实解）。")
rep("t2861", 4, "其量等虚空；道法萧洒，真体自然。",
    "其量等虚空；道法萧洒，真体自然。因真舒凭、幼世苍杧（原颂语意隐晦，姑存原语），奔腾意马。")
rep("t2861", 8, "名宜万国，稽首归依。", "名宜万国，稽首归依祖林胆蔔（原颂语，姑存）。")
rep("t2861", 10, "人间鸾鷟", "人间鸑鷟")
rep("t2861", 10, "断臂立雪求法，混而不浊", "断臂立灵（原颂作「立靈」），混而不浊")
rep("t2861", 11, "果少花多，以忍（信）传衣钵", "果少花多，弘忍传衣钵")
rep("t2861", 12, "法才极瞻，大耳（达摩）惭羞", "法才极瞻，大耳三藏惭羞")

# t1570：末品名订正
rep("t1570", 7, "【破空品·空亦不执、结颂】", "【教诫弟子品·空亦不执、结颂】")

# t0617：段12/段13 错位修正（把「欲生无量寿佛国者……便得往生」移回段12）
d = load("t0617")
seg13 = d["translations"][12]["modern"]
anchor = "欲生无量寿佛国者，应当如是上观无量寿佛"
i = seg13.find("【小标题】")
head_marker = seg13.find("\n", seg13.find("】"))
moved = seg13[:head_marker + 1]
rest = seg13[head_marker + 1:]
# 段13 开头【法华三昧…】小标题保留，其后若含「欲生无量寿佛国者…便得往生。」则移走
assert anchor in rest, "段13 未含待移文段"
end = rest.find("便得往生。") + len("便得往生。")
moved_text = rest[:end]
rest_new = rest[end:].lstrip()
d["translations"][12]["modern"] = moved + rest_new
d["translations"][11]["modern"] = d["translations"][11]["modern"].rstrip() + " " + moved_text
save(d)
print("② t0617 段12/段13 错位已修正")

# t1886：段7 补成住坏空夹注说明；段8/13 补会通标记
rep("t1886", 6, "劫劫生生轮回不绝，无终无始如汲井轮——",
    "（原文此下附长颂及「议曰」，详述器界成住坏空：空劫中大风起、光音金藏云、雨如车轴、始作金刚界，先成梵王界乃至夜摩天，风鼓清水成须弥七金、滓浊为山地四洲泥犁，方名器界立；经十九增减成劫，住、坏、空劫各二十增减。又附「议曰」会通道教虚无混沌之说：谓空界大风即彼混沌一气、金藏云即太极、梵王界乃至须弥即彼之天、滓浊即地、二禅福尽下生即人，即「一生二、二生三、三才备」之义。原文夹注繁长，此括其要。）劫劫生生轮回不绝，无终无始如汲井轮——")
rep("t1886", 12, "此身或有无恶自祸、无善自福",
    "（原文于此下以夹注标示会通次第：「此下方是第四教，亦同破此已生灭诸相」「此下方是第三法相教中亦同所说」「此下方是第二小乘教中亦同所说」「此下方是第一人天教中亦同所说」「此下方是儒道二教亦同所说」——即将阿赖耶识、法执、我执、贪爱、善恶业报、禀气受质诸层，一一会归前四教之说。）此身或有无恶自祸、无善自福")

print("② 针对性修正完成")
