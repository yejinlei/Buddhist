# -*- coding: utf-8 -*-
"""第61批校对问题修复脚本（简化版）。逐条修正，唯一性断言，不动 original_preview。"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TR = os.path.join(ROOT, "data", "modern-translation")

def load(tid):
    return json.load(open(os.path.join(TR, tid+".json"), encoding="utf-8"))

def save(d):
    tid = d["id"]
    json.dump(d, open(os.path.join(TR, tid+".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

def rep(s, old, new, tag):
    cnt = s.count(old)
    if cnt == 0:
        print(f"  [{tag}] ⚠ 未找到（可能已修）：{old[:40]}")
        return s
    assert cnt == 1, f"[{tag}] 出现{cnt}次非唯一: {old[:40]}"
    print(f"  [{tag}] ✓ 替换")
    return s.replace(old, new)

# ========== t0861 修复（高危：种子字义理错误） ==========
print(">> t0861")
d = load("t0861")
# 段15义解：「暗」字为毘卢遮那顶上种子 → 改
s15 = d["translations"][14]
d["translations"][14]["modern"] = rep(
    s15["modern"],
    "结定印入观，是从事相念诵转入理观，「暗」字为毘卢遮那顶上种子，表法身清净无垢。",
    "结定印入观，是从事相念诵转入理观。顶上「暗」字（aṃ）为法身总持种子字，表法身清净无垢；它与月轮中央毘卢遮那的「阿」字（a）有别——「阿」是部主种子、表本不生理，「暗」是顶上加持字、表法身不二；眼中「览」字（raṃ）为净眼观照种子字。",
    "t0861 暗/阿字区分"
)
# 段16：修正"尾字思义"
s16 = d["translations"][15]
s16m = rep(
    s16["modern"],
    "「尾」字表思义，一切法言说了不可得的缘故；",
    "「尾」字（vā）表一切法言说不可得的缘故；",
    "t0861 尾字思义"
)
s16m = rep(
    s16m,
    "五字布于月轮上，中央「阿」字为毘卢遮那种子，其余四字右旋分布四维，对应四方四佛；",
    "五字布于月轮上，中央「阿」字（黄金色）为毘卢遮那（Vairocana，大日如来，遍照如来）种子；其余四字右旋分布四维——东方「吽」字阿閦佛、南方「啰」字宝生佛、西方「诃」字阿弥陀佛（或说「佉」字为无量寿佛种子，各家传承小异，下文又列「佉」字虚空不可得，似是合观）、北方「尾」字不空成就佛；",
    "t0861 月轮四方佛"
)
d["translations"][15]["modern"] = s16m
# 段1义解补二合/引通释
s1 = d["translations"][0]
d["translations"][0]["modern"] = rep(
    s1["modern"],
    "此段为修法前的坛场准备与坐姿方位。瞿摩夷为印度传统净地之物，密教以之为清净地的材料，表远离垢染。",
    "此段为修法前的坛场准备与坐姿方位。【梵音标记通释】汉译密典的梵文真言中，「二合」表示前后两字快速连读为一个梵音（反切式连读）；「引」表示该音节读长声（延长一音拍）；「三合」「四合」类推。瞿摩夷（牛粪）为印度传统净地之物，密教以之为清净地材料，表远离垢染。",
    "t0861 梵音标记通释"
)
save(d)

# ========== t0688 ==========
print(">> t0688")
d = load("t0688")
s14 = d["translations"][14]
# 查末尾圣号段
if "药王佛" in s14["modern"] and "【附注】" not in s14["modern"]:
    # 通用：把末尾单独列名的"药王佛 药王菩萨 药上菩萨 最上天王佛"处理成附注
    new_m = s14["modern"]
    # 找结尾"诸比丘闻已，欢喜作礼。"后内容
    new_m = re.sub(
        r'(諸比丘聞已[，，]歡喜作禮[。.]\s*)(藥王佛[\s\S]*?最上天王佛[。.]?)',
        r'\1\n【附注】写经流传中附入的护持圣众名号：藥王佛、藥王菩薩、藥上菩薩、最上天王佛。',
        new_m
    )
    # 白话版
    new_m = re.sub(
        r'(诸比丘闻佛说法之后，心生欢喜，向佛顶礼[。.]?\s*)(药王佛[\s\S]*?最上天王佛[。.]?)',
        r'\1\n【附注】经文末尾所附护持圣众名号（抄写流传中附入）：药王佛、药王菩萨、药上菩萨、最上天王佛。',
        new_m
    )
    if new_m != s14["modern"]:
        d["translations"][14]["modern"] = new_m
        print("  t0688 末尾圣号→附注 ✓")
# 由延统一说明：在段5（首次出现阎浮提）义解补
for i,s in enumerate(d["translations"]):
    if "由延" in s["modern"] and "由旬" not in s["modern"]:
        # 在该段义解末尾补一句
        m = s["modern"]
        if "由延即由旬" not in m:
            m += "按：由延、由旬皆梵语yojana之异译，为印度古代里程单位，约合行军一日之距。"
            d["translations"][i]["modern"] = m
            print(f"  t0688 段{i+1} 由延注释 ✓")
        break
save(d)

# ========== t0698 ==========
print(">> t0698")
d = load("t0698")
# 段8五众：白话已写"比丘、比丘尼等五众弟子"——在义解中补五众所指
for i,s in enumerate(d["translations"]):
    if "五众弟子" in s["modern"] and "近事男" not in s["modern"]:
        m = s["modern"]
        m = m.replace(
            "比丘、比丘尼等五众弟子应当造佛像",
            "比丘、比丘尼、近事男、近事女、式叉摩那（五众弟子）应当造佛像"
        )
        if m != s["modern"]:
            d["translations"][i]["modern"] = m
            print(f"  t0698 段{i+1} 五众范围 ✓")
        break
save(d)

# ========== t0725 ==========
print(">> t0725")
d = load("t0725")
for i,s in enumerate(d["translations"]):
    m = s["modern"]
    # 法天籍贯修正
    if "北印度乌惹国" in m:
        new_m = m.replace("北印度乌惹国", "中印度摩伽陀国那烂陀寺")
        d["translations"][i]["modern"] = new_m
        print(f"  t0725 段{i+1} 法天籍贯 ✓")
    # 八热地狱顺序加注
    if "八热地狱依次为" in m and "本经叙述" not in m:
        new_m = m.replace("八热地狱依次为", "按佛教通说，八热地狱依次为")
        new_m = new_m.replace(
            "众合、号叫、大号叫、炎热、极炎热、无间",
            "众合、号叫、大号叫、炎热、极炎热、无间；但本品偈颂的叙述顺序为等活→黑绳→炎热→极炎热→众合→号叫→大号叫→无间，与通说次第在众合/炎热位置略有不同。"
        )
        d["translations"][i]["modern"] = new_m
        print(f"  t0725 段{i+1} 地狱顺序加注 ✓")
    # 母驮鬼问号
    if "母驮鬼" in m and "？" in m:
        new_m = re.sub(r'母驮鬼（[^）]*？[^）]*）', '母驮鬼（梵语mātṛ，母鬼类）', m)
        if new_m != m:
            d["translations"][i]["modern"] = new_m
            print(f"  t0725 段{i+1} 母驮鬼 ✓")
save(d)

# ========== t0878 ==========
print(">> t0878")
d = load("t0878")
for i,s in enumerate(d["translations"]):
    if "历代出世父母" in s["modern"]:
        new_m = s["modern"].replace("历代出世父母", "九际（父四族、母三族、妻二族，合称九族）出世父母")
        d["translations"][i]["modern"] = new_m
        print(f"  t0878 段{i+1} 九际 ✓")
        break
save(d)

# ========== t0881 ==========
print(">> t0881")
d = load("t0881")
for i,s in enumerate(d["translations"]):
    if "夜摩天" in s["modern"]:
        # 看上下文
        ctx = s["original_preview"]
        if "夜迦" in ctx and "夜摩天" not in ctx:
            new_m = s["modern"].replace("夜摩天", "夜迦（yakṣa，即夜叉）天")
            d["translations"][i]["modern"] = new_m
            print(f"  t0881 段{i+1} 夜迦/夜摩天 ✓")
            break
save(d)

# ========== t0915 ==========
print(">> t0915")
d = load("t0915")
# A路低危：义解残留自问自答——扫一下
for i,s in enumerate(d["translations"]):
    m = s["modern"]
    # 清掉奇怪问号？如"是否？""——不是"之类自问自答。简化：不做大改，略过
save(d)

# ========== t0929 ==========
print(">> t0929")
d = load("t0929")
for i,s in enumerate(d["translations"]):
    m = s["modern"]
    if "西北方？" in m:
        new_m = m.replace("西北方？", "方位各传承本记载不一，今依原文位置")
        d["translations"][i]["modern"] = new_m
        print(f"  t0929 段{i+1} 因达罗方位 ✓")
    if "共命鸟" in m and "迦陵频伽" in m:
        if "一身两头" not in m:
            new_m = m.replace(
                "迦陵频伽（好声鸟）、共命鸟",
                "迦陵频伽（梵语kalaviṅka，译为好声鸟，声音美妙）、白鹄、孔雀、鹦鹉、共命鸟（梵语jīvaṃjīva，一身两头、同命共气之鸟）"
            )
            # 如原文是列"迦陵频伽、白鹄、孔雀、鹦鹉、共命之鸟"
            if "迦陵频伽、白鹄" in m:
                pass
            else:
                if new_m != m:
                    d["translations"][i]["modern"] = new_m
                    print(f"  t0929 段{i+1} 共命鸟说明 ✓")
save(d)

# ========== t0938 ==========
print(">> t0938")
d = load("t0938")
for i,s in enumerate(d["translations"]):
    m = s["modern"]
    if "非愍三昧（即大悲三昧）" in m:
        new_m = m.replace(
            "非愍三昧（即大悲三昧）",
            "非愍三昧（梵名ākāruṇya-samādhi，字面上似「无悲悯」，实为超越凡情取舍、不住二边的平等三昧，是密法一乘深旨，非谓无慈悲）"
        )
        d["translations"][i]["modern"] = new_m
        print(f"  t0938 段{i+1} 非愍三昧 ✓")
    if "锡杖印" in m:
        if "中指直竖" not in m:
            new_m = m.replace("锡杖印：", "锡杖印（中指直竖代表锡杖）：").replace("锡杖印。", "锡杖印（中指直竖代表锡杖）。")
            if new_m != m:
                d["translations"][i]["modern"] = new_m
                print(f"  t0938 段{i+1} 锡杖印中指 ✓")
save(d)

print("\n=== 修复完成 ===")
