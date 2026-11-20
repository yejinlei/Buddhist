#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""白话精译 v2 - 更自然的白话"""
import json, os, re

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
SRC = os.path.join(BASE, "data/baihua-tasks")
OUT = os.path.join(BASE, "data/modern-translation")

def is_mantra(text):
    if any(k in text for k in ["陀羅尼","陀罗尼","呪曰","咒曰","眞言","真言"]):
        return True
    return False

def to_baihua(text):
    if not text or not text.strip():
        return text
    if is_mantra(text):
        return text
    s = text
    # 顺序替换：先长后短
    repl = [
        # 序分/通序
        ("聞如是：", "我是这样听闻的："),
        ("聞如是，", "我是这样听闻的，"),
        ("聞如是", "我是这样听闻的："),
        ("如是我聞：", "如是我闻："),
        ("如是我聞，一時", "如是我闻。一时"),
        # 时间
        ("一時，佛在", "一时，佛在"),
        ("一時，佛遊", "一时，佛游行到"),
        ("一時，佛住", "一时，佛住在"),
        ("一時，佛", "一时，佛"),
        ("一時，", "那时，"),
        ("一時佛在", "一时，佛在"),
        ("爾時，世尊告諸比丘：", "那时，世尊告诉诸位比丘说："),
        ("爾時，世尊告曰：", "那时，世尊说道："),
        ("爾時，世尊告", "那时，世尊告诉"),
        ("爾時，佛告", "那时，佛告诉"),
        ("爾時，阿難白佛言：", "那时，阿难对佛说："),
        ("爾時，阿難白", "那时，阿难对"),
        ("爾時，尊者阿難", "那时，尊者阿难"),
        ("爾時，世尊", "那时，世尊"),
        ("爾時，佛", "那时，佛"),
        ("爾時", "那时"),
        ("於是", "于是"),
        ("於其時", "就在那时"),
        ("是時", "这时"),
        ("尋即", "随即"),
        ("尋後", "紧接着"),
        ("即時", "当下"),
        ("即自", "当即"),
        ("斯須", "片刻"),
        ("須臾", "须臾"),
        ("俄", "不久"),
        # 对话
        ("佛言：", "佛说："),
        ("佛言，", "佛说，"),
        ("佛告諸比丘：", "佛告诉诸比丘说："),
        ("佛告諸比丘，", "佛告诉诸比丘，"),
        ("佛告諸沙門：", "佛告诉诸沙门说："),
        ("佛告阿難：", "佛告诉阿难说："),
        ("佛告阿難，", "佛告诉阿难，"),
        ("佛告", "佛告诉"),
        ("阿難白佛言：", "阿难对佛说："),
        ("阿難白佛：", "阿难对佛说："),
        ("阿難白", "阿难票告"),
        ("白佛言：", "票告佛说："),
        ("白佛：", "票告佛说："),
        ("白言：", "票告说道："),
        ("啟曰：", "启奏说道："),
        ("啟王言：", "启奏大王说道："),
        ("問曰：", "问道："),
        ("答曰：", "答道："),
        ("報言：", "回答说道："),
        ("報曰：", "回答道："),
        ("告曰：", "告诉说道："),
        ("說曰：", "说道："),
        ("說是", "说此"),
        ("說此法", "说此法"),
        ("說此偈", "说此偈"),
        ("曰：", "说道："),
        # 引语
        ("何謂", "什么叫做"),
        ("何以故", "为什么呢"),
        ("所以者何", "为什么呢"),
        ("云何", "是怎样的"),
        ("所以然者", "所以这样说，是因为"),
        # 状态
        ("猶如", "就好像"),
        ("猶若", "就好比"),
        ("譬如", "就譬如"),
        ("譬", "好比"),
        ("猶", "还、仍然"),
        ("恒", "恒常"),
        ("常當", "应当恒常"),
        ("常", "常"),
        ("甞", "曾经"),
        ("嘗", "曾经"),
        ("未曾", "未曾"),
        ("未甞", "未曾"),
        ("未嘗", "未曾"),
        ("靡不", "无不"),
        ("無不", "无不"),
        ("咸", "都"),
        ("悉", "都、全部"),
        ("皆", "都"),
        ("俱", "一同、一起"),
        ("都", "都"),
        ("輒", "就"),
        ("便", "就、便"),
        ("遂", "于是就"),
        ("竟", "终了"),
        ("訖", "完毕"),
        ("畢", "完毕"),
        # 动作/动词
        ("詣", "前往、到"),
        ("之", "的"),
        ("覩", "看见"),
        ("睹", "看见"),
        ("愍", "怜悯"),
        ("愍傷", "哀悯"),
        ("愴然", "凄怆"),
        ("惻然", "悲悯"),
        ("豈", "难道"),
        ("寧", "宁可"),
        ("勿", "不要"),
        ("莫", "不要"),
        ("弗", "不"),
        ("毋", "不要"),
        ("卻", "退下"),
        ("爾乃", "这才"),
        ("然則", "如此说来"),
        ("尋路", "沿路"),
        ("往", "去"),
        ("還", "返回"),
        ("往詣", "前往"),
        # 结尾
        ("歡喜奉行", "欢喜奉行"),
        ("作禮而去", "行礼离去"),
        ("稽首而去", "稽首退下"),
        ("聞佛所說", "听佛所说"),
        ("聞已", "听后"),
        ("禮佛", "礼佛"),
    ]
    for a,b in repl:
        s = s.replace(a,b)
    # 名词性"名曰、號曰"保留"名叫做""号叫做"
    s = s.replace("名曰", "名叫").replace("號曰", "名号叫").replace("号曰", "名号叫")
    # 代词：只在完整词处替换，避免误伤
    s = re.sub(r'吾([，。：「」 ]|$|身|等|今|當|聞|欲|聞)', r'我\1', s)
    s = re.sub(r'汝([，。：「」 ]|身|等|今|當|等|輩)', r'你\1', s)
    s = s.replace("爾等", "你们").replace("汝等", "你们").replace("吾等", "我们")
    return s

def make_modern(title, yijie, baihua):
    return f"【{title}】\n【义解】{yijie}\n【白话】\n{baihua}"

# ============ 加载通用部分的结构判定（重复使用process_all.py里的逻辑） ============
import importlib.util
spec = importlib.util.spec_from_file_location("pa", os.path.join(BASE,"process_all.py"))
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)

def process_file(sutra_id, title_fn, yijie_fn):
    with open(os.path.join(SRC, f"{sutra_id}.json")) as f:
        data = json.load(f)
    for i, seg in enumerate(data['translations']):
        orig = seg['original_preview']
        title = title_fn(i, orig)
        # 清理标题前导引号、标点
        title = re.sub(r'^[」』\s]+','', title)[:60]
        yj = yijie_fn(i, orig)
        bh = to_baihua(orig)
        seg['modern'] = make_modern(title, yj, bh)
    out_path = os.path.join(OUT, f"{sutra_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{sutra_id} done: {len(data['translations'])} segments")

# t0152
process_file("t0152", lambda i,t: pa.title_and_yijie_t0152(i,t)[0], lambda i,t: pa.title_and_yijie_t0152(i,t)[1])
# t0154
process_file("t0154", lambda i,t: pa.title_and_yijie_t0154(i,t)[0], lambda i,t: pa.title_and_yijie_t0154(i,t)[1])
# t0156
process_file("t0156", lambda i,t: pa.title_and_yijie_t0156(i,t)[0], lambda i,t: pa.title_and_yijie_t0156(i,t)[1])
# t0125
process_file("t0125", lambda i,t: pa.title_and_yijie_t0125(i,t)[0], lambda i,t: pa.title_and_yijie_t0125(i,t)[1])

print("All v2 done.")
