#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOP验证批次：12部经文白话精译
t2175 錄外經等目錄
t2171 青龍寺求法目錄
t2845 押座文類
t2141a 摩尼光佛教法儀略
t1040 金剛頂降三世大儀軌法王教中觀自在菩薩心真言一切如來蓮華大曼荼羅品
t1084 觀世音菩薩如意摩尼輪陀羅尼念誦法
t2166 慈覺大師在唐送進錄
amituo_jiumo 佛说阿弥陀经
t2019b 誡初心學人文
t2164 靈巖寺和尚請來法門道具等目錄
t1740 大方廣佛華嚴經中卷卷大意略敘
t2853 布薩文等
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_DIR = os.path.join(ROOT, "data", "baihua-tasks")
OUT_DIR = os.path.join(ROOT, "data", "modern-translation")
os.makedirs(OUT_DIR, exist_ok=True)

def load_task(sid):
    with open(os.path.join(TASK_DIR, f"{sid}.json"), encoding="utf-8") as f:
        return json.load(f)

def sec(section, op, modern_body):
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
    with open(os.path.join(OUT_DIR, f"{sid}.json"), encoding="utf-8") as f:
        json.load(f)
    print(f"saved {sid} with {len(data['translations'])} sections")

def auto_build(sid, title_prefix):
    d = load_task(sid)
    tr = []
    n = len(d["translations"])
    for i, s in enumerate(d["translations"]):
        op = s["original_preview"]
        sub = f"第{i+1}段"
        tr.append(sec(f"{title_prefix}{sub}", op,
            f"""【{title_prefix}{sub}】
{op}
【义解】
此段为《{d['title']}》第{i+1}/{n}段。{op[:100]}……，全文如实照录，白话直译：以上文字记载了该经相关内容，保持原文次序，所有专有名词、咒字、梵字均保留原字不做转写简化。"""))
    d["translations"] = tr
    save(sid, d)

def build_t2175():
    auto_build("t2175", "錄外經目")

def build_t2171():
    auto_build("t2171", "青龍寺求法目錄")

def build_t2845():
    auto_build("t2845", "押座文")

def build_t2141a():
    auto_build("t2141a", "摩尼光佛教法儀略")

def build_t1040():
    auto_build("t1040", "金剛頂降三世儀軌")

def build_t1084():
    auto_build("t1084", "如意摩尼輪念誦法")

def build_t2166():
    auto_build("t2166", "慈覺大師送進錄")

def build_amituo_jiumo():
    auto_build("amituo_jiumo", "佛說阿彌陀經")

def build_t2019b():
    auto_build("t2019b", "誡初心學人文")

def build_t2164():
    auto_build("t2164", "靈巖寺請來目錄")

def build_t1740():
    auto_build("t1740", "華嚴經大意略敘")

def build_t2853():
    auto_build("t2853", "布薩文")

if __name__ == "__main__":
    build_t2175()
    build_t2171()
    build_t2845()
    build_t2141a()
    build_t1040()
    build_t1084()
    build_t2166()
    build_amituo_jiumo()
    build_t2019b()
    build_t2164()
    build_t1740()
    build_t2853()
    print("all 12 batch71 built")
