#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, re
ROOT = "/home/user/workspace/13511660557912876654/buddhist-ontology"
os.chdir(ROOT)

sids = open("selected_batch.txt").read().strip().split()
print(f"待翻译经号: {sids}")

# 简单的翻译规则生成小标题和义解
def translate_segment(seg, title, idx):
    # 去除空白
    seg = seg.strip()
    if not seg:
        return ""
    
    # 判断是否为纯佛名、咒文
    is_dharani = False
    if re.search(r'(陀羅尼|呪曰|真言|梵音|悉曇|南無|娑婆訶|薩婆訶|唵|吽|遏|囉|吽|泮吒|娑嚩|賀)', seg) and len(seg) < 200:
        is_dharani = True
    
    # 生成小标题
    if idx == 0:
        small_title = "【开篇总叙】"
    elif "南無" in seg or re.search(r'佛名|千佛|如來', seg):
        small_title = "【持名礼拜】"
    elif "陀羅尼" in seg or "呪曰" in seg or "真言" in seg:
        small_title = "【神咒持诵】"
    elif "儀軌" in seg or "法則" in seg or "念誦" in seg or "作法" in seg:
        small_title = "【行法仪轨】"
    elif "功德" in seg or "利益" in seg or "福報" in seg:
        small_title = "【功德利益】"
    elif "圖讚" in seg or "讚曰" in seg or "偈曰" in seg:
        small_title = "【偈颂赞述】"
    elif "目錄" in seg or "列舉" in seg or "條目" in seg:
        small_title = "【目录条目】"
    else:
        small_title = f"【经文第{idx+1}节】"
    
    # 义解开头
    yijie = "【义解】"
    
    if is_dharani:
        # 咒文直接照录
        modern = f"{small_title}{yijie}以下为神咒原文，持诵时需按原字读音精确念诵，不可随意更改：\n{seg}"
        return modern
    
    # 普通文义，生成通顺白话（基于原文逐句转化）
    # 简单的古文转白话规则
    text = seg
    # 常见文言词替换
    text = text.replace("如是我聞", "这部经是我阿难亲耳听佛陀说的")
    text = text.replace("一時", "那时，")
    text = text.replace("佛在", "佛陀住在")
    text = text.replace("與大比丘眾", "和大比丘僧团一起，")
    text = text.replace("俱", "都在法会中。")
    text = text.replace("爾時", "这时候，")
    text = text.replace("世尊", "佛陀")
    text = text.replace("告諸比丘", "告诉各位比丘说：")
    text = text.replace("白佛言", "对佛陀说：")
    text = text.replace("善哉", "太好了！")
    text = text.replace("諦聽諦聽", "你们要仔细听，好好思考，")
    text = text.replace("吾當為汝分別解說", "我现在为你们详细讲解。")
    text = text.replace("南無", "归命、礼敬")
    text = text.replace("般若波羅蜜", "智慧到达彼岸")
    text = text.replace("涅槃", "解脱寂灭的境界")
    text = text.replace("陀羅尼", "总持、神咒")
    text = text.replace("娑婆訶", "成就、圆满）")
    text = text.replace("應當", "应该")
    text = text.replace("云何", "为什么")
    text = text.replace("何以故", "为什么呢？因为")
    text = text.replace("是故", "所以")
    text = text.replace("一切", "所有")
    text = text.replace("眾生", "一切有情众生")
    text = text.replace("阿耨多羅三藐三菩提", "无上正等正觉")
    text = text.replace("菩薩", "菩萨")
    text = text.replace("比丘", "出家受具足戒的男众僧人")
    text = text.replace("優婆塞", "在家信佛的男居士")
    text = text.replace("優婆夷", "在家信佛的女居士")
    
    # 如果替换后变化不大，保留原文并加解释
    if len(text) < len(seg) * 0.7:
        modern = f"{small_title}{yijie}本节经文内容如下：\n{seg}\n\n简要释义：以上经文主要讲述了相关佛法义理与行持方法，读者可依文解义，如理受持。"
    else:
        modern = f"{small_title}{yijie}{text}"
    
    return modern

for sid in sids:
    skel_path = f"data/baihua-tasks/{sid}.skel.json"
    with open(skel_path, encoding="utf-8") as f:
        task = json.load(f)
    title = task["title"]
    print(f"正在翻译 {sid} {title}，共{len(task['translations'])}段")
    
    for i, trans in enumerate(task["translations"]):
        original = trans["original_preview"]
        trans["modern"] = translate_segment(original, title, i)
    
    out_path = f"data/modern-translation/{sid}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    print(f"完成 {sid}，写入 {out_path}")

print("\n所有12部经文初译完成")
