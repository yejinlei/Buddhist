import json, re, os

def load(tid):
    p = f"data/modern-translation/{tid}.json"
    return json.load(open(p, encoding="utf-8"))

def save(tid, d):
    p = f"data/modern-translation/{tid}.json"
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# 1. 统一【义解】为简体，删除所有段末冗余"【义解】译文见上。"和双【义解】标签
def fix_format(d):
    for s in d["translations"]:
        m = s["modern"]
        # 繁体【義解】转简体
        m = m.replace("【義解】", "【义解】")
        # 删除末尾冗余的【义解】译文见上。
        m = re.sub(r"【义解】译文见上。?$", "", m)
        m = re.sub(r"【义解】（咒文照录原文）$", "", m)
        # 删除重复的【义解】标签（只保留第一个）
        parts = m.split("【义解】")
        if len(parts) > 2:
            m = parts[0] + "【义解】" + "".join(parts[1:])
        # 繁体小标题转简体
        title_match = re.match(r"^【(.+?)】", m)
        if title_match:
            title = title_match.group(1)
            # 常见繁体转简体
            title = title.replace("釋", "释").replace("譯", "译").replace("題", "题").replace("皈", "归")
            title = title.replace("儀", "仪").replace("軌", "轨").replace("誦", "诵").replace("續", "续")
            title = title.replace("門", "门").replace("觀", "观").replace("種", "种").replace("願", "愿")
            title = title.replace("經", "经").replace("呪", "咒").replace("壇", "坛").replace("場", "场")
            title = title.replace("畫", "画").replace("聲", "声").replace("聞", "闻")
            title = title.replace("緣", "缘").replace("德", "德").replace("相", "相").replace("開", "开")
            m = "【" + title + "】" + m[title_match.end():]
        s["modern"] = m.strip()
    return d

# 2. 修复t0941段1咒文漏"拏"字
d = load("t0941")
m = d["translations"][1]["modern"]
assert "鉢囉（二合）麼（引）弭" in m, "t0941段1未找到待补字符串"
m = m.replace("鉢囉（二合）麼（引）弭", "鉢囉（二合）拏麼（引）弭")
d["translations"][1]["modern"] = m
d = fix_format(d)
save("t0941", d)
print("修复t0941完成")

# 3. 修复t0958段11多余右括号
d = load("t0958")
m = d["translations"][10]["modern"]
if m.startswith("）"):
    m = m.lstrip("）").strip()
    d["translations"][10]["modern"] = m
d = fix_format(d)
save("t0958", d)
print("修复t0958完成")

# 4. 修复t0974a段8"三十三字"改"三十三句"
d = load("t0974a")
m = d["translations"][7]["modern"]
if "三十三字" in m:
    m = m.replace("三十三字", "三十三句")
    d["translations"][7]["modern"] = m
d = fix_format(d)
save("t0974a", d)
print("修复t0974a完成")

# 5. 修复t0983a删除重复原文抄录，统一格式
d = load("t0983a")
# 清理段12-17重复的原文
for i in range(11, 17):
    if i >= len(d["translations"]): break
    m = d["translations"][i]["modern"]
    # 只保留到咒文结束，删除后面重复叙事
    if "佛告阿難" in m and i > 0:
        idx = m.find("佛告阿難")
        if idx > 50:  # 前面已有义解和咒文
            m = m[:idx].strip()
            d["translations"][i]["modern"] = m
d = fix_format(d)
save("t0983a", d)
print("修复t0983a完成")

# 6. 修复t1019段19"通达到达"重复字
d = load("t1019")
for s in d["translations"]:
    s["modern"] = s["modern"].replace("通达到达", "通达")
d = fix_format(d)
save("t1019", d)
print("修复t1019完成")

# 7. 修复t1036段8脱漏"師子"（狮子），双义解问题，段内重复咒文问题
d = load("t1036")
# 段8补"師子"
m = d["translations"][7]["modern"]
if "師子" not in m and "王難、獸難" in m:
    m = m.replace("王難、獸難", "師子王難、獸難")
    d["translations"][7]["modern"] = m
# 清理所有段的双义解和重复咒文
for i, s in enumerate(d["translations"]):
    m = s["modern"]
    # 咒文区错误重复非咒文的问题，这里简化：删除重复抄录的非咒文原文
    parts = m.split("【义解】")
    if len(parts) > 1:
        yi = parts[1]
        # 如果义解后又重复了大段原文，截断
        if len(yi) > 200 and "\n" in yi:
            lines = yi.split("\n")
            # 保留前3行义解和咒文，后面的重复原文删除
            s["modern"] = parts[0] + "【义解】" + "\n".join(lines[:3])
d = fix_format(d)
save("t1036", d)
print("修复t1036完成")

# 8. 统一其余经文格式
for tid in ["t0948", "t0974b", "t0974d", "t0986", "t1005b", "yaoshi_xuanzang"]:
    d = load(tid)
    d = fix_format(d)
    save(tid, d)
    print(f"格式化{tid}完成")

print("所有问题修复完成")
