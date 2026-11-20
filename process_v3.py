#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""白话精译 v3 - 修正误替换"""
import json, os, re, importlib.util

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
SRC = os.path.join(BASE, "data/baihua-tasks")
OUT = os.path.join(BASE, "data/modern-translation")

def is_mantra(text):
    return any(k in text for k in ["陀羅尼","陀罗尼","呪曰","咒曰","眞言","真言","二合","引","反切"])

def is_verse(s):
    """检测是否为偈颂（五言/七言韵文）"""
    non_space = re.sub(r'[，。、；：「」『』（）\s]', '', s)
    if len(non_space) < 12: return False
    clauses = [c for c in re.split(r'[，；。]', s) if c.strip()]
    if len(clauses) < 3: return False
    # 所有分句字数4-8
    lens = [len(re.sub(r'[^\u4e00-\u9fff]','',c)) for c in clauses]
    return all(4<=l<=8 for l in lens) and len(set(lens)) <= 2

def to_baihua(text):
    if not text or not text.strip():
        return text
    if is_mantra(text):
        return text
    # 分行处理，偈颂保留原句
    lines = text.split("\n")
    out = []
    for line in lines:
        s = line
        # 译者题注原样保留
        if re.match(r"^\s*(吳|吴|晉|晋|東晉|东晋|西晉|西晋|失譯|失译|後漢|后汉|姚秦|宋|梁|唐|元魏|高齊|高齐|陳|陈|隋|苻秦|三國)[\s\S]{0,30}(譯|译)\s*$", s.strip()):
            out.append(s)
            continue
        # 偈颂保留
        if is_verse(s):
            out.append(s)
            continue
        # 替换（先长后短，避免误伤）
        repl = [
            ("聞如是：", "我是这样听闻的："),
            ("聞如是，", "我是这样听闻的，"),
            ("聞如是。", "我是这样听闻的。"),
            ("聞如是", "我是这样听闻的："),
            ("如是我聞：", "如是我闻："),
            ("如是我聞，一時", "如是我闻。一时"),
            ("一時，佛在", "一时，佛在"),
            ("一時，佛遊", "一时，佛游行到"),
            ("一時，佛住", "一时，佛住在"),
            ("一時，佛", "一时，佛"),
            ("一時佛在", "一时，佛在"),
            ("一時佛", "一时，佛"),
            ("爾時，世尊告諸比丘：", "那时，世尊告诉诸比丘说："),
            ("爾時，世尊告曰：", "那时，世尊说道："),
            ("爾時，世尊告", "那时，世尊告诉"),
            ("爾時，佛告諸比丘：", "那时，佛告诉诸比丘说："),
            ("爾時，佛告", "那时，佛告诉"),
            ("爾時，阿難白佛言：", "那时，阿难对佛说："),
            ("爾時，阿難白", "那时，阿难禀告"),
            ("爾時，尊者", "那时，尊者"),
            ("爾時，世尊", "那时，世尊"),
            ("爾時，佛", "那时，佛"),
            ("爾時", "那时"),
            ("於是", "于是"),
            ("於其時", "就在那个时候"),
            ("是時", "这时"),
            ("尋即", "随即"),
            ("尋後", "紧接着"),
            ("即時", "当下"),
            ("即自", "当即"),
            ("斯須", "片刻"),
            ("須臾", "须臾"),
            # 对话标识
            ("佛言：", "佛说："),
            ("佛言，", "佛说，"),
            ("佛告諸比丘：", "佛告诉诸比丘说："),
            ("佛告諸比丘，", "佛告诉诸比丘，"),
            ("佛告諸沙門：", "佛告诉诸沙门说："),
            ("佛告阿難：", "佛告诉阿难说："),
            ("佛告阿難，", "佛告诉阿难，"),
            ("阿難白佛言：", "阿难对佛说："),
            ("阿難白佛：", "阿难对佛说："),
            ("阿難白", "阿难禀告"),
            ("白佛言：", "禀告佛说："),
            ("白佛：", "禀告佛说："),
            ("白言：", "禀告说道："),
            ("問曰：", "问道："),
            ("問言：", "问道："),
            ("答曰：", "答道："),
            ("答言：", "答道："),
            ("報言：", "回答说道："),
            ("報曰：", "回答道："),
            ("告曰：", "告诉说道："),
            ("告言：", "告诉说道："),
            ("說曰：", "说道："),
            ("說是語已", "说了此话之后"),
            ("說此言已", "说了此话之后"),
            ("說此偈已", "说此偈之后"),
            ("說是偈已", "说此偈之后"),
            ("何謂", "什么叫做"),
            ("何以故", "为什么呢"),
            ("所以者何", "为什么呢"),
            ("所以然者", "之所以如此，是因为"),
            ("云何為", "什么是"),
            ("云何", "如何"),
            ("猶如", "就好像"),
            ("猶若", "就好比"),
            ("譬如", "譬如"),
            ("恒", "恒常"),
            ("常當", "应当恒常"),
            ("未曾", "未曾"),
            ("未甞", "未曾"),
            ("未嘗", "未曾"),
            ("靡不", "无不"),
            ("無不", "无不"),
            ("咸", "都"),
            ("悉", "全都"),
            ("皆", "都"),
            ("俱", "一同"),
            ("輒", "就"),
            ("便", "便"),
            ("遂", "于是就"),
            ("訖", "完毕"),
            ("畢", "完毕"),
            ("詣", "到"),
            ("覩", "看见"),
            ("睹", "看见"),
            ("愍", "怜悯"),
            ("愍傷", "哀悯伤痛"),
            ("愴然", "凄怆悲伤"),
            ("惻然", "悲悯伤痛"),
            ("惻", "悲悯"),
            ("豈", "难道"),
            ("寧", "宁可"),
            ("勿", "不要"),
            ("莫", "不要"),
            ("弗", "不"),
            ("卻", "退下"),
            ("爾乃", "这才"),
            ("然則", "如此说来"),
            ("尋路", "沿路"),
            ("往詣", "前往到"),
            ("歡喜奉行", "欢喜奉行"),
            ("作禮而去", "行礼离去"),
            ("稽首而去", "稽首退下"),
            ("為佛作禮", "向佛行礼"),
            ("聞佛所說", "听佛所说"),
            ("聞已", "听后"),
            ("禮佛", "礼佛"),
            ("頭面禮足", "顶礼佛足"),
            ("右遶三匝", "右绕三匝"),
            ("五體投地", "五体投地"),
            ("稽首", "稽首"),
            ("頂禮", "顶礼"),
            ("名曰", "名叫"),
            ("號曰", "号为"),
            ("号曰", "号为"),
            ("字曰", "字为"),
        ]
        for a,b in repl:
            s = s.replace(a,b)
        # 处理剩下的"曰："为"说道："
        s = re.sub(r'(?<![名號偈銘])曰：', '说道：', s)
        # 代词替换（只在对话/叙述中明显处替换，不大规模改）
        # 不替换"吾""之"，保留半文半白风格，避免错换
        out.append(s)
    return "\n".join(out)

def make_modern(title, yijie, baihua):
    return f"【{title}】\n【义解】{yijie}\n【白话】\n{baihua}"

spec = importlib.util.spec_from_file_location("pa", os.path.join(BASE,"process_all.py"))
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)

def process_file(sutra_id, title_fn, yijie_fn):
    with open(os.path.join(SRC, f"{sutra_id}.json")) as f:
        data = json.load(f)
    for i, seg in enumerate(data['translations']):
        orig = seg['original_preview']
        title = title_fn(i, orig)
        title = re.sub(r'^[」』「『\s]+','', title)[:60]
        yj = yijie_fn(i, orig)
        bh = to_baihua(orig)
        seg['modern'] = make_modern(title, yj, bh)
    out_path = os.path.join(OUT, f"{sutra_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{sutra_id} done: {len(data['translations'])} segments")

process_file("t0152", lambda i,t: pa.title_and_yijie_t0152(i,t)[0], lambda i,t: pa.title_and_yijie_t0152(i,t)[1])
process_file("t0154", lambda i,t: pa.title_and_yijie_t0154(i,t)[0], lambda i,t: pa.title_and_yijie_t0154(i,t)[1])
process_file("t0156", lambda i,t: pa.title_and_yijie_t0156(i,t)[0], lambda i,t: pa.title_and_yijie_t0156(i,t)[1])
process_file("t0125", lambda i,t: pa.title_and_yijie_t0125(i,t)[0], lambda i,t: pa.title_and_yijie_t0125(i,t)[1])
print("v3 All done.")
