#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第二轮修正：修复引号嵌套问题、完成剩余繁简转换、恢复t0881原字"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "modern-translation")
hant2simp = json.load(open(os.path.join(ROOT, "data", "hant2simp_full.json"), encoding="utf-8"))

# 补充繁简映射
extra_simp = {
    '毘': '毗',  # 异体字统一
    '著': '着',  # 助词/动词用着
    '滾燙': '滚烫',
    '瘖瘂': '喑哑',
    '嗎': '吗',
    '擱': '搁',
    '婬': '淫',
    '妬': '妒',
    '孃': '娘',  # 但咒语中保留原字
    '裡': '里',
    '後': '后',
    '從': '从',
    '為': '为',
    '會': '会',
    '無': '无',
    '個': '个',
    '這': '这',
    '那': '那',
    '來': '来',
    '時': '时',
    '對': '对',
    '說': '说',
    '國': '国',
    '開': '开',
    '關': '关',
    '還': '还',
    '點': '点',
    '現': '现',
    '顯': '显',
    '總': '总',
    '經': '经',
    '線': '线',
    '與': '与',
    '舉': '举',
    '處': '处',
    '號': '号',
    '實': '实',
    '盡': '尽',
    '畫': '画',
    '異': '异',
    '當': '当',
    '稱': '称',
    '爾': '尔',
    '殺': '杀',
    '獄': '狱',
    '熱': '热',
    '鐵': '铁',
    '繩': '绳',
    '餓': '饿',
    '鬼': '鬼',
    '傍': '傍',
    '脩': '修',
    '冩': '写',
}
hant2simp.update(extra_simp)

def to_simp(s):
    return "".join(hant2simp.get(c, c) for c in s)

def fix_quotes_simple(text):
    """简单引号修正：不做嵌套自动转换，只保证配对，把错误的』开头、』』叠用修正，恢复统一用「」外层，内层需要的地方手动处理"""
    # 去掉句首孤立的』
    text = re.sub(r'\n\s*』', '\n', text)
    text = re.sub(r'^』', '', text)
    # 叠用的』』改成」
    text = text.replace('』』', '」')
    return text

def fix_sutra(tid):
    path = os.path.join(OUT_DIR, f"{tid}.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    
    for seg in data["translations"]:
        m = seg.get("modern", "")
        # 再次繁简转换（彻底）
        m = to_simp(m)
        # 修复引号问题
        m = fix_quotes_simple(m)
        seg["modern"] = m
    
    # t0881 特殊处理：咒语中「枳娘」恢复为「枳孃」（原字照录）
    if tid == "t0881":
        for seg in data["translations"]:
            m = seg["modern"]
            # 只在咒语部分（即引用的真言里）恢复，白话义解部分用简体"娘"
            # 简单处理：如果是在「」内的咒语，恢复枳孃
            m = m.replace("枳娘", "枳孃")
            seg["modern"] = m
    
    # mode 保持 "baihua"（项目约定，不是错误，validate_baihua.py就是按baihua校验的）
    data["mode"] = "baihua"
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"✅ {tid} 二次修正完成")

sutras = ["t0688", "t0698", "t0725", "t0861", "t0872", "t0878", "t0881", "t0915", "t0929", "t0935", "t0938", "t0940"]
for tid in sutras:
    fix_sutra(tid)

print("\n二次修正完成")
