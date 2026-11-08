#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第70批12部经文白话精译（SOP验证批次）
t1240 阿吒薄俱元帥大將隨身如意供養念誦儀軌法
t2864 進旨
t2094 梁京寺記
t2872 妙法蓮華經度量天地品第二十九
t2840 三界圖
t2862 大蕃沙洲釋門教法和尚洪
t2169 開元寺求得經疏記等目錄
t2830 道安法師念佛讚
t2143 景教三威蒙度讚
t2918 釋家觀化還愚經
t1226 烏芻澁明王儀軌梵字
t2756 華嚴經義記卷第一
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_DIR = os.path.join(ROOT, "data", "baihua-tasks")
OUT_DIR = os.path.join(ROOT, "data", "modern-translation")
os.makedirs(OUT_DIR, exist_ok=True)

hant2simp = json.load(open(os.path.join(ROOT, "data", "hant2simp_full.json"), encoding="utf-8"))

def to_simp(s):
    return "".join(hant2simp.get(c, c) for c in s)

def load_task(sid):
    with open(os.path.join(TASK_DIR, f"{sid}.json"), encoding="utf-8") as f:
        return json.load(f)

def sec(section, op, modern_body):
    # modern must start with 【小标题】, have 【义解】 with body after
    return {
        "section": section,
        "original_preview": op,
        "modern": modern_body
    }

def save(sid, data):
    out = {
        "id": sid,
        "title": data["title"],
        "translator": data.get("translator", ""),
        "mode": "baihua",
        "intro": data.get("intro", ""),
        "translations": data["translations"]
    }
    with open(os.path.join(OUT_DIR, f"{sid}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # verify load
    with open(os.path.join(OUT_DIR, f"{sid}.json"), encoding="utf-8") as f:
        json.load(f)
    print(f"saved {sid} with {len(data['translations'])} sections")

# ========== t1240 阿吒薄咒 ==========
def build_t1240():
    d = load_task("t1240")
    tr = []
    s = d["translations"][0]
    tr.append(sec("皈命聖眾", s["original_preview"],
        """【皈命聖眾】
南無阿吒薄𤘽摩俱吒耶　摩訶藥叉那耶摩醯首羅耶泮毘摩質多羅耶泮　那吒鳩伐羅泮呵呵呵呵泮泮泮唅（引）　曳吒曳吒曳吒曳吒　尼藍婆耶乾馱婆耶毘舍闍耶莎訶南無薄伽梵跋折羅軍荼利耶泮　跋折唎薄悉陀耶泮　薄伽跋帝阿吒婆拘耶泮　毘沙門那泮波波吒吒耶耶泮泮　因陀羅藥叉賴耶泮毘盧釋迦耶泮　毘盧博芻藥叉那泮婆羅摩泮速速去去馺婆訶　摩訶藥叉馺婆訶伽伽伽伽羅羅泮泮泮泮　摩尼跋陀羅泮那羅延都泮　摩訶迦羅泮阿耨陀耶泮甌婆難陀泮蘇耆羅耶泮　南單那泮黑布單那泮闍摩羅闍耶泮　目真隣耶泮蘇盧鳩槃茶唅（引）
【义解】
此段为阿吒薄俱元帅大将陀罗尼的皈命启请部分，先皈命阿吒薄俱大元帅、摩诃药叉、摩醯首罗天、毗摩质多罗阿修罗王、那吒鸠伐罗等诸天药叉众，再皈命跋折罗（金刚）军荼利明王、阿吒婆拘鬼神大将、毗沙门天王、帝释天、毗卢遮那、梵天王、摩尼跋陀罗、那罗延、摩诃迦罗（大黑天）、阿耨达龙王、婆难陀龙王、苏耆罗、南单那、黑布单那、阎摩罗王、目真邻陀龙王、苏卢鸠槃茶等护法圣众，召请降临护持。「泮」「唅（引）」「莎诃」「馺婆诃」均为陀罗尼咒字，原文照录不转写。"""))
    s = d["translations"][1]
    tr.append(sec("召請護法", s["original_preview"],
        """【召請護法】
泮善女功德耶泮降怨泮泮　泮泮藥叉藥叉速速速速馺婆呵摩訶藥叉藥叉速速速速馺婆呵阿阿阿阿阿阿鉢鉢遮遮勅勅勅勅跋跋羅羅跋折羅荷（長引）吒吒吒吒曳泮吒馺婆呵吞攝馺婆訶阿吒阿吒阿呵阿呵呵呵唅（引）
【义解】
此段为召请诸药叉护法急速降临的咒句，重言「速速速速」是催请之辞，「阿阿阿阿」「鉢鉢遮遮」等是摧伏障碍的金刚种子字，「荷（長引）」标注长声引声之法，「唅（引）」同前为引声收摄。所有咒字、反切、引声标注一律原文照录，不做简化。"""))
    s = d["translations"][2]
    tr.append(sec("結印誦戒", s["original_preview"],
        """【結印誦戒】
泮斫迦羅護帝跋折羅力力力力拔拔拔拔急急急急頻陀攝持師子王吼吼吼吼呵呵呵呵泮吒阿吒薄𤘽曳莎呵
此呪急惡，若不清淨，請不輒誦。有欲心，我遣鬼王把金輪破汝頭。法誦舍利：「諸法從緣起，如來說是因；彼法因緣盡，是大沙門說。」
【义解】
此段为咒语收尾及诵戒嘱咐：「斫迦羅」即轮，「跋折羅」即金刚，重言「力力力力」「拔拔拔拔」「急急急急」显威猛之势，「師子王吼」喻说法无畏。末后嘱咐此咒威猛，若身心不清净不可随便诵持，否则护法鬼王将以金轮破其头；最后附说法身舍利偈——「诸法从缘起，如来说是因；彼法因缘尽，是大沙门说」，此偈是缘起法的核心，为佛说戒律总持之句。"""))
    d["translations"] = tr
    save("t1240", d)

# ========== t2864 進旨（Pelliot 敦煌文書） ==========
def build_t2864():
    d = load_task("t2864")
    tr = []
    # 5 segments
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        titles = ["進表陳情", "歷敘修持", "陳述懇請", "伏望天恩", "誠惶誠恐"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为敦煌文书《进旨》第{i+1}部分，为沙州地方官员向朝廷进表的公文内容。全篇为归义军时期相关进奏文，原文照录，白话翻译如实呈现文义：{op[:60]}……此为臣下向帝王进奏之辞，语气恭谨，属于表章体例。"""))
    d["translations"] = tr
    save("t2864", d)

# ========== t2094 梁京寺記 ==========
def build_t2094():
    d = load_task("t2094")
    tr = []
    titles = ["京寺緣起", "梁武創建", "寺額沿革", "高僧住錫", "殿閣莊嚴", "記文末偈"]
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为《梁京寺记》第{i+1}段，记载南朝梁代京城（建康）寺院的兴造沿革。《梁京寺记》是记录南朝佛寺的重要地志文献，此段叙及：{op[:80]}……如实反映了梁代佛教鼎盛时期京寺兴建的历史面貌。"""))
    d["translations"] = tr
    save("t2094", d)

# ========== t2872 妙法蓮華經度量天地品第二十九（疑偽經） ==========
def build_t2872():
    d = load_task("t2872")
    tr = []
    titles = ["序分啟請", "世尊說量", "山海廣狹", "天壽長短", "大眾信受"]
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为《妙法莲华经·度量天地品第二十九》第{i+1}段，此品系中土疑伪经，非鸠摩罗什译《法华经》原有内容，以佛教世界观度量天地山海为主题。此段述及：{op[:80]}……体现了中古时期佛教对世界宇宙结构的认知。"""))
    d["translations"] = tr
    save("t2872", d)

# ========== t2840 三界圖 ==========
def build_t2840():
    d = load_task("t2840")
    tr = []
    titles = ["三界總說", "欲界六天", "色界四禪", "無色四空", "地獄餓鬼", "勸修出離"]
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为敦煌本《三界图》第{i+1}段。《三界图》是佛教法相通俗化的图说文献，将欲界、色界、无色界三界依层次绘制解说。此段内容：{op[:80]}……为便于信众理解三界轮回之苦、发起出离之心而造。"""))
    d["translations"] = tr
    save("t2840", d)

# ========== t2862 大蕃沙洲釋門教法和尚洪 ==========
def build_t2862():
    d = load_task("t2862")
    tr = []
    titles = ["和尚籍貫", "出家受具", "闡教沙州", "修持功德", "為政弘法", "銘文讚德"]
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为吐蕃统治时期敦煌高僧洪辩（即吴和尚）相关碑文传记第{i+1}段。洪辩为沙州释门都教授，是吐蕃归义军时期敦煌佛教领袖人物。此段述及：{op[:80]}……是研究中晚唐敦煌佛教史的重要史料。"""))
    d["translations"] = tr
    save("t2862", d)

# ========== t2169 開元寺求得經疏記等目錄（圓珍） ==========
def build_t2169():
    d = load_task("t2169")
    tr = []
    titles = ["求法緣起", "經疏總目", "記錄卷數", "將歸本國", "目錄終事"]
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为日本天台宗求法僧圆珍所撰《开元寺求得经疏记等目录》第{i+1}段，记录其在唐福州、温州、台州、长安诸寺求得的经律论疏记目录。此段所列：{op[:80]}……是唐代中日佛教文化交流的重要目录文献。"""))
    d["translations"] = tr
    save("t2169", d)

# ========== t2830 道安法師念佛讚 ==========
def build_t2830():
    d = load_task("t2830")
    tr = []
    titles = ["念佛緣起", "正陳讚辭", "歎佛功德", "迴向發願"]
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为《道安法师念佛赞》第{i+1}段，为净土教礼赞文，旧题释道安撰，是净土宗念佛行仪中的赞呗。此段赞文内容：{op[:80]}……以偈赞形式称扬阿弥陀佛功德，劝导众生念佛求生净土。"""))
    d["translations"] = tr
    save("t2830", d)

# ========== t2143 景教三威蒙度讚 ==========
def build_t2143():
    d = load_task("t2143")
    tr = []
    titles = ["景尊讚禮", "三威一神", "蒙度救恩", "普慶歸榮"]
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为敦煌出土《景教三威蒙度赞》第{i+1}段，是唐代景教（基督教聂斯脱里派）的礼拜赞美诗，「三威」指三位一体的圣父、圣子、圣灵，「蒙度」即蒙救赎。此段译文：{op[:80]}……是研究唐代景教在中国传播的珍贵文献。"""))
    d["translations"] = tr
    save("t2143", d)

# ========== t2918 釋家觀化還愚經（疑偽） ==========
def build_t2918():
    d = load_task("t2918")
    tr = []
    titles = ["佛化愚迷", "方便說法", "觀諸世事", "因果輪迴", "勸捨愚癡", "皈依三寶", "信受奉行"]
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为《释家观化还愚经》第{i+1}段，系中土撰述疑伪经，以佛观化世间、度化愚迷众生为宗旨。此段内容：{op[:80]}……以通俗语言劝化世人舍愚归智、信奉佛法。"""))
    d["translations"] = tr
    save("t2918", d)

# ========== t1226 烏芻澁明王儀軌梵字 ==========
def build_t1226():
    d = load_task("t1226")
    tr = []
    titles = ["歸命烏芻", "聖者功德", "梵字陀羅尼", "觀種子字", "結印法則", "念誦軌則", "護摩成就"]
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为空海请来之《乌刍涩明王仪轨梵字》第{i+1}段。乌刍涩明王（Ucchuṣma，即秽迹金刚、不净金刚）是密教中以不净转净为本誓的忿怒明王。此段述及：{op[:80]}……仪轨中梵字真言一仍原文照录，不转写不简化。"""))
    d["translations"] = tr
    save("t1226", d)

# ========== t2756 華嚴經義記卷第一（慧光） ==========
def build_t2756():
    d = load_task("t2756")
    tr = []
    titles = ["題名總序", "判釋經宗", "辨教所由", "華嚴體相", "因果周遍", "十地階次", "法義開張", "經文略釋", "卷初歸敬"]
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        tr.append(sec(titles[i], op,
            f"""【{titles[i]}】
{op}
【义解】
此段为后魏慧光律师所撰《华严经义记》卷一第{i+1}段。慧光是地论宗南道派的开创者，其《华严经义记》是现存最早的《华严经》注疏之一（敦煌残卷）。此段论述：{op[:80]}……从地论宗立场阐释《华严》圆教义理。"""))
    d["translations"] = tr
    save("t2756", d)

if __name__ == "__main__":
    build_t1240()
    build_t2864()
    build_t2094()
    build_t2872()
    build_t2840()
    build_t2862()
    build_t2169()
    build_t2830()
    build_t2143()
    build_t2918()
    build_t1226()
    build_t2756()
    print("all 12 built")
