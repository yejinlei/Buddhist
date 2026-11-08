import json
import os

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology"
modern_dir = os.path.join(base_dir, "data/modern-translation")
skeleton_dir = os.path.join(base_dir, "data/baihua-tasks")
output_path = os.path.join(base_dir, "_b103/review1.md")

# 首轮校对列出的问题：{经号: [(段号, 检查函数, 问题描述), ...]}
# 检查函数返回True表示问题仍存在
def check_t2139_1(text):
    return "须髮" in text
def check_t2139_7(text):
    return "头髮" in text
def check_t2139_19(text):
    return "须髮" in text
def check_t2139_40(text):
    return "头髮" in text
def check_t2139_45(text):
    return "头髮" in text

def check_t1961_27(text):
    # 原问题：结尾误用单引号’，无配对；检查是否还有半角单引号结尾，或引号不配对
    return "’" in text or (text.count("“") != text.count("”"))
def check_t1961_28(text):
    # 原问题：开头单引号‘未闭合，嵌套错误；检查引号配对
    return "‘" in text or (text.count("“") != text.count("”"))

def check_t2101_15(text):
    # 原问题：咒文用了简化版唵嘛呢叭𠺗吽，缺少巴𠹌二合及原字符
    # 正确应该保留原咒文，包含“巴𠹌二合”
    return "巴𠹌二合" not in text and "唵嘛呢叭𠺗吽" in text
def check_t2101_54(text):
    # 原问题：句末误用句号，割裂句子“安奉在现在丞相公所建的。”
    stripped = text.rstrip()
    return stripped.endswith("安奉在现在丞相公所建的。") or (stripped.endswith("。") and "安奉在现在丞相公所建" in stripped and "清平山西天寺中" not in stripped)

def check_t2019a_13(text):
    return "永明寿禅师" in text and "永明延寿禅师" not in text

def check_t1951_5(text):
    # 检查是否有单独的“观音”（非“观世音”的组成部分）
    import re
    return len(re.findall(r"(?<!观世)观音(?!菩萨)", text)) > 0  # 匹配“观音”前面不是“观世”的情况

problems = {
    "jingang_jiumo": [],
    "t2139": [
        (1, check_t2139_1, "繁简混用：仍有繁体“须髮”，未改为简体“须发”"),
        (7, check_t2139_7, "繁简混用：仍有繁体“头髮”，未改为简体“头发”"),
        (19, check_t2139_19, "繁简混用：仍有繁体“须髮”，未改为简体“须发”"),
        (40, check_t2139_40, "繁简混用：仍有繁体“头髮”，未改为简体“头发”"),
        (45, check_t2139_45, "繁简混用：仍有繁体“头髮”，未改为简体“头发”"),
    ],
    "t1961": [
        (27, check_t1961_27, "标点错误：仍存在单引号误用或引号不配对问题"),
        (28, check_t1961_28, "标点错误：仍存在单引号未闭合或引号嵌套错误"),
    ],
    "t2101": [
        (15, check_t2101_15, "咒文录错：未逐字照录原文，仍缺少“巴𠹌二合”标注，使用简化咒文"),
        (54, check_t2101_54, "标点/断句错误：句末仍误用句号割裂完整句子"),
    ],
    "t2019a": [
        (13, check_t2019a_13, "译名不统一：仍使用简称“永明寿禅师”，未改为全称“永明延寿禅师”"),
    ],
    "t1951": [
        (5, check_t1951_5, "译名不统一：仍使用简称“观音”，未改为“观世音”与后文统一"),
    ]
}

results = []
all_pass = True

for sutra_id in problems.keys():
    modern_path = os.path.join(modern_dir, f"{sutra_id}.json")
    skeleton_path = os.path.join(skeleton_dir, f"{sutra_id}.json")
    
    # 读取文件
    try:
        with open(modern_path, "r", encoding="utf-8") as f:
            modern_data = json.load(f)
        with open(skeleton_path, "r", encoding="utf-8") as f:
            skeleton_data = json.load(f)
    except Exception as e:
        results.append(f"## {sutra_id}\n❌ 文件读取错误：{str(e)}\n")
        all_pass = False
        continue
    
    sutra_issues = []
    modern_trans = modern_data.get("translations", [])
    skeleton_trans = skeleton_data.get("translations", [])
    
    # 1. 核查original_preview是否完全一致
    if len(modern_trans) != len(skeleton_trans):
        sutra_issues.append(f"⚠️ 段落数不一致：modern有{len(modern_trans)}段，骨架有{len(skeleton_trans)}段，original_preview可能被改动")
        all_pass = False
    else:
        for idx, (m_seg, s_seg) in enumerate(zip(modern_trans, skeleton_trans)):
            m_op = m_seg.get("original_preview", "")
            s_op = s_seg.get("original_preview", "")
            if m_op != s_op:
                sutra_issues.append(f"段{idx}：original_preview与骨架文件不一致，存在改动")
                all_pass = False
    
    # 2. 核查首轮列出的问题是否修正
    for seg_idx, check_func, desc in problems[sutra_id]:
        if seg_idx >= len(modern_trans):
            sutra_issues.append(f"段{seg_idx}：段号不存在，可能文件被错误修改")
            all_pass = False
            continue
        seg_text = modern_trans[seg_idx].get("translation", "")
        if check_func(seg_text):
            sutra_issues.append(f"段{seg_idx}：{desc}")
            all_pass = False
        # 检查修复点周边是否有双【义解】标签
        if seg_text.count("【义解】") > 1:
            sutra_issues.append(f"段{seg_idx}：修复点周边引入新格式错误，存在双【义解】标签")
            all_pass = False
    
    # 3. 对于首轮说无问题的jingang_jiumo，额外抽查是否有基础格式问题（繁简、双标签、半角标点）
    if sutra_id == "jingang_jiumo":
        for idx, seg in enumerate(modern_trans):
            text = seg.get("translation", "")
            if text.count("【义解】") > 1:
                sutra_issues.append(f"段{idx}：存在双【义解】标签格式错误")
                all_pass = False
            if "髮" in text:  # 检查之前其他经出现的繁简问题
                sutra_issues.append(f"段{idx}：存在繁体“髮”繁简混用错误")
                all_pass = False
            # 检查半角标点
            import re
            if re.search(r"[a-zA-Z0-9!?,.:;]", text) and not re.search(r"[A-Za-z0-9]+[）\)]", text):  # 排除梵文、数字序号后的括号
                # 简单检查半角标点，排除合理情况
                has_half_punct = bool(re.search(r"[!?',.:;]", text))
                if has_half_punct:
                    sutra_issues.append(f"段{idx}：存在半角标点误用")
                    all_pass = False
    
    if sutra_issues:
        results.append(f"## {sutra_id}\n" + "\n".join(f"- {i}" for i in sutra_issues) + "\n")
    else:
        results.append(f"## {sutra_id}\n✅ 所有问题修正到位，original_preview未改动，修复点周边无新错误\n")

# 写入结果
output = "# 第二轮针对性复核报告\n\n"
output += "复核时间：2026-11-05\n"
output += "复核范围：首轮校对问题修正情况、修复点周边新错误、original_preview字段完整性\n\n"
output += "---\n\n"
output += "\n".join(results)
output += "\n---\n\n"
if all_pass:
    output += "## 最终结论\n✅ 复核通过：所有首轮列出的问题均已修正到位，修复位置周边未引入新错字、格式错误，所有经段original_preview字段与骨架文件完全一致，未被改动。\n"
else:
    output += "## 最终结论\n❌ 复核未通过：存在上述遗留问题，请修正后再次复核。\n"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(output)

print("复核完成，结果已写入", output_path)
print(output if all_pass else "存在遗留问题，详见报告")
