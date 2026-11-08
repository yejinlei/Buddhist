# -*- coding: utf-8 -*-
"""按第53批三份独立校对报告修正问题。"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUT = os.path.join(ROOT, "sutras")
TR = os.path.join(ROOT, "data", "modern-translation")


def raw_of(tid):
    d = json.load(open(os.path.join(SUT, tid + ".json"), encoding="utf-8"))
    return "\n".join(c["text"] for c in d["content"])


def rebuild(tid, anchors, moderns, title, translator):
    raw = raw_of(tid)
    pos, cur = [], 0
    for a in anchors:
        i = raw.find(a, cur)
        assert i >= 0, f"{tid} 锚点未找到: {a!r}"
        pos.append(i); cur = i + 1
    pos.append(len(raw))
    segs = [{"section": moderns[k].split("\n")[0].strip("【】"),
             "original_preview": raw[pos[k]:pos[k + 1]],
             "modern": moderns[k]} for k in range(len(anchors))]
    out = {"id": tid, "title": title, "translator": translator, "mode": "full",
           "sutraPath": f"sutras/{tid}.json", "translations": segs}
    json.dump(out, open(os.path.join(TR, tid + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    cov = sum(len(s["original_preview"]) for s in segs)
    print(f"重建 {tid}: 段数={len(segs)} 覆盖={cov}/{len(raw)}")


def patch(tid, pairs):
    p = os.path.join(TR, tid + ".json")
    d = json.load(open(p, encoding="utf-8"))
    n = 0
    for i, s in enumerate(d["translations"]):
        for old, new in pairs:
            if old in s["modern"]:
                s["modern"] = s["modern"].replace(old, new)
                n += 1
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"修正 {tid}: {n} 处")


# ---------- 重建 t1908（补回被漏掉的末段锚点 + 补齐「结」译文） ----------
old = json.load(open(os.path.join(TR, "t1908.json"), encoding="utf-8"))["translations"]
JIE = """【结·如梦三昧得无生忍】
反复思惟这样的梦观，渐渐修得如梦三昧。由此三昧得无生法忍，从长梦中豁然而觉，即知本来永无流转，只是一心卧于一如之床。若能如此反复思惟，虽缘六尘而不以为实，烦恼羞愧而不能自逸，这就名为大乘六情忏悔。
【义解】结归「如梦三昧→无生法忍」，点出「六情忏悔」的极果。"""
rebuild(
    "t1908",
    ["釋元曉撰", "若依法界始遊行者", "所以者何？十方三世一塵一念", "今於此處蓮花藏界",
     "故今佛前深生慚愧", "我及眾生無始以來，無明所醉", "此諸罪實無所有，眾緣和合假名為業",
     "行者若能數數思惟如是實相而懺悔者", "作是悔時莫以為作", "於諸業障作是悔已",
     "靜慮之時，甚可怪哉", "數數思惟如是夢觀"],
    [s["modern"] for s in old] + [JIE],
    "大乘六情懺悔", "新羅 元曉撰",
)
patch("t1908", [
    ("自作、教他、見作隨喜三途皆攝", "自作、教他作、見作隨喜三種方式皆攝"),
    ("时節和合故得果報", "时节和合故得果报"),
    ("唯识「如梦」观", "唯识与如来藏系的「如梦」观"),
])

# ---------- 重建 t1687（补回被漏掉的偈颂起点锚点） ----------
old7 = json.load(open(os.path.join(TR, "t1687.json"), encoding="utf-8"))["translations"]
rebuild(
    "t1687",
    ["西天譯經三藏朝散大夫試鴻臚少卿宣梵大師賜紫沙門臣日稱等奉",
     "依諸經律祕密教", "起最上恭敬，合掌以持花", "若忿恚無慈，貪愛多散亂",
     "若彼求法者，於師生輕毀", "常於阿闍黎，承事而供養", "若足踏師影，獲罪如破塔",
     "不應於師前，覆頂及乘御", "或浣衣濯足，及澡浴等事", "若在家女人，淨心來聽法",
     "說法度弟子，曼拏羅護摩", "彼金剛如來，親如是宣說"],
    [s["modern"] for s in old7],
    "事師法五十頌", "馬鳴菩薩集　宋 日稱等譯",
)
patch("t1687", [
    ("应当伺察他派遣的使者；对他的所作之事", "应当伺察他派来的使者（即受命办理之事）；对那（使者）所作之事"),
])

# ---------- 修正 t0769 ----------
patch("t0769", [
    ("本经收于大正藏第十七册，属阿含部类，专为四众弟子说末世行法。",
     "本经收于大正藏第十七册经集部，专为四众弟子说末世行法。"),
    ("不得刺绣彩帛、色泽艳丽的衣饰", "不得刺绣彩帛、色泽艳丽或熏香的衣饰"),
    ("不得与世间妻女戏笑言语、往来应答。能这样行的，是清净道人。",
     "不得与世间妻女戏笑言语、往来应答，以免造成（往来的）因缘。能这样行的，是清净道人。"),
    ("如用世间的药方、符咒厌祷之说，为人医治众病",
     "如用世间的药方、符咒厌祷之说，为人医治众病，以及外道的解奏之术"),
    ("此段为在家男众立法：受五戒、持六斋、孝顺治家、远离四事（同席、同行、同室异床、戏笑往来）、以四等心待一切",
     "此段为在家男众立法：受五戒、持六斋、孝顺治家，远离同席坐起、结伴同行、同室异床等事（原文概称「四事」），以四等心待一切"),

])

# ---------- 修正 t1643 ----------
patch("t1643", [
    ("以四大和合的身肢为我不成立，因内外推求皆不可见。",
     "以发甲皮肉、筋骨脂髓、肠胃手足等身肢为我不成立，因内外推求皆不可见。"),
    ("那些有天眼的人应当可以见到", "那些有天眼的人应当可以见到那（最上我）"),
    ("则没有自、他、命者、士夫、补特伽罗、作者、受者",
     "则没有自、他、命者、士夫、补特伽罗（人我）、作者、受者"),
])

# ---------- 修正 t1619 ----------
patch("t1619", [
    ("所以它不能像五根那样作为境。", "所以它不是（所缘的）境，就像（眼）根（也不是所缘境）一样。"),
    ("所以它不能像实有的尘那样为境。", "所以它不是境，如同（前文所举的）尘一样。"),
    ("二根（净色根与识）共生，以胜能为根。", "二根共生，以胜能为根。"),
    ("【义解】会通经说：以色为眼识所依之根，即功能义。",
     "【义解】会通经说：经中「依根缘色」的「根」，即能与体相共造果的功能；色是眼识的所缘，而非所依。"),
])

print("第53批修正完成")
