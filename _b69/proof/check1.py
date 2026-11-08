#!/usr/bin/env python3
import json, os, re, sys

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation"
SUTRAS = ["t0688","t0698","t0725","t0861","t0872","t0878","t0881","t0915","t0929","t0935","t0938","t0940"]

# 常见繁体字符正则（非穷举，扫描常用字）
TRAD_PAT = re.compile(r'[為無個對這來國說發經長門關愛見體點學書會實現當將應麼時還裡個後從問聽讀買賣東車馬魚鳥]')
HALF_QUOTE = re.compile(r'["\']')
SHAN_NVZI = re.compile(r'善女子')

issues = []

for sid in SUTRAS:
    path = os.path.join(BASE, f"{sid}.json")
    with open(path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            issues.append(f"[{sid}] JSON解析错误: {e}")
            continue

    # 7. 顶层字段检查
    required_fields = ["id","title","translator","translations","mode","intro","sutraPath"]
    for fld in required_fields:
        if fld not in data:
            issues.append(f"[{sid}] 缺少顶层字段: {fld}")

    # mode
    if data.get("mode") != "modern":
        issues.append(f"[{sid}] mode={data.get('mode')} 应为modern")

    translations = data.get("translations", [])
    if not isinstance(translations, list) or len(translations) == 0:
        issues.append(f"[{sid}] translations为空或非数组")
        continue

    for idx, seg in enumerate(translations):
        loc = f"{sid} seg#{idx}"
        # 必须字段
        for k in ["original_preview","modern"]:
            if k not in seg:
                issues.append(f"[{loc}] 缺少字段 {k}")

        modern = seg.get("modern","")
        orig   = seg.get("original_preview","")

        # 1. 繁体扫描（modern部分；original_preview是原文可能含繁体，不计）
        m_trad = TRAD_PAT.search(modern)
        if m_trad:
            issues.append(f"[{loc}] modern疑似繁体字符「{m_trad.group()}」")

        # intro 也要扫
        intro = data.get("intro","")
        i_trad = TRAD_PAT.search(intro)
        if i_trad:
            issues.append(f"[{sid}] intro疑似繁体字符「{i_trad.group()}」")

        # 3. 善女人
        if SHAN_NVZI.search(modern) or SHAN_NVZI.search(intro):
            issues.append(f"[{loc}] 出现「善女子」应为「善女人」")

        # 4. 半角引号
        if HALF_QUOTE.search(modern):
            issues.append(f"[{loc}] modern含半角引号")
        if HALF_QUOTE.search(intro):
            issues.append(f"[{sid}] intro含半角引号")

        # 2. modern格式：应以【小标题】开头，含【义解】
        if not modern.startswith("【"):
            issues.append(f"[{loc}] modern未以【小标题】开头，首字符={modern[:1]}")
        if "【义解】" not in modern:
            issues.append(f"[{loc}] modern中未找到【义解】标记")
        else:
            parts = modern.split("【义解】", 1)
            if len(parts) != 2 or not parts[1].strip():
                issues.append(f"[{loc}] 【义解】后无解说内容")
        # 小标题标记
        # 开头第一个】位置之前应有小标题文字
        m2 = re.match(r'^【([^】]+)】', modern)
        if not m2:
            issues.append(f"[{loc}] modern开头小标题格式异常")

        # 5. original_preview 不要求简体，但要求非空；"一字未改"需要对照原文，脚本侧只报非空/疑似问题
        if not orig or not orig.strip():
            issues.append(f"[{loc}] original_preview为空")

        # 引号嵌套：外层「」内层『』，检查是否存在「『」及「』」是否配对大致正常
        # 简单统计
        lo = modern.count("「")
        lc = modern.count("」")
        lo2 = modern.count("『")
        lc2 = modern.count("』")
        if lo != lc:
            issues.append(f"[{loc}] 「」不配对（{lo}/{lc}）")
        if lo2 != lc2:
            issues.append(f"[{loc}] 『』不配对（{lo2}/{lc2}）")
        # 若存在半角" 已在上面报

print("===== 自动检查发现问题 =====")
if not issues:
    print("（未发现规则层面问题）")
for i in issues:
    print(i)
print(f"\n共 {len(issues)} 条")
