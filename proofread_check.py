import json
import re

def remove_whitespace(s):
    return re.sub(r'\s+', '', s)

sutra_ids = ["t0131", "t0102", "t1046", "t1379", "t0560", "t0096", "t2836", "t0655", "t0779", "t0934", "t0218", "t1405"]
base_path = "/home/user/workspace/13511660557912876654/buddhist-ontology"
issues = []

for sid in sutra_ids:
    print(f"Checking {sid}...")
    sutra_issues = []
    
    # 1. 读取原文
    try:
        with open(f"{base_path}/sutras/{sid}.json", 'r', encoding='utf-8') as f:
            sutra = json.load(f)
    except Exception as e:
        sutra_issues.append(f"无法读取原文文件：{e}")
        issues.append((sid, sutra_issues))
        continue
    
    # 获取原文全文（content字段）
    original_full = ""
    if 'content' in sutra:
        content = sutra['content']
        if isinstance(content, list):
            for chap in content:
                if 'text' in chap:
                    original_full += chap['text']
        else:
            original_full = content
    else:
        # 找全文字段
        for k in sutra.keys():
            if 'content' in k or 'text' in k or 'body' in k:
                val = sutra[k]
                if isinstance(val, list):
                    for chap in val:
                        if 'text' in chap:
                            original_full += chap['text']
                else:
                    original_full = val
                break
    original_nospace = remove_whitespace(original_full)
    print(f"Original length (nospace): {len(original_nospace)}")
    
    # 2. 读取译文文件
    try:
        with open(f"{base_path}/data/modern-translation/{sid}.json", 'r', encoding='utf-8') as f:
            trans = json.load(f)
    except Exception as e:
        sutra_issues.append(f"无法读取译文文件：{e}")
        issues.append((sid, sutra_issues))
        continue
    
    # 3. 检查顶层字段
    required_top_fields = ['id', 'title', 'translator', 'vol', 'translations']
    for field in required_top_fields:
        if field not in trans:
            sutra_issues.append(f"顶层字段缺失：{field}")
    
    # 4. 拼接所有original_preview
    preview_concat = ""
    for i, seg in enumerate(trans['translations']):
        seg_num = i + 1
        # 检查字段
        if 'original_preview' not in seg:
            sutra_issues.append(f"段{seg_num}：缺失original_preview字段")
            continue
        if 'modern' not in seg:
            sutra_issues.append(f"段{seg_num}：缺失modern字段")
        if 'section' not in seg:
            sutra_issues.append(f"段{seg_num}：缺失section字段")
        preview_concat += seg['original_preview']
    
    preview_nospace = remove_whitespace(preview_concat)
    print(f"Preview length (nospace): {len(preview_nospace)}")
    
    # 5. 检查是否是原文连续子串，且100%覆盖
    if preview_nospace not in original_nospace:
        # 找第一个不匹配的位置
        idx = 0
        max_idx = min(len(preview_nospace), len(original_nospace))
        while idx < max_idx and preview_nospace[idx] == original_nospace[idx]:
            idx += 1
        sutra_issues.append(f"original_preview拼接后与原文不匹配，在位置{idx}处：preview字符为{repr(preview_nospace[idx:idx+20])}，原文对应位置为{repr(original_nospace[idx:idx+20])}")
    else:
        # 检查覆盖率：preview长度应该等于原文长度
        if len(preview_nospace) != len(original_nospace):
            sutra_issues.append(f"original_preview覆盖率不足：原文去空白长度{len(original_nospace)}，preview拼接长度{len(preview_nospace)}，缺失{len(original_nospace)-len(preview_nospace)}字")
    
    # 6. 检查第一段section是否与首标题一致（modern里第一个【】里的标题）
    if len(trans['translations']) > 0:
        first_seg = trans['translations'][0]
        if 'section' in first_seg and 'modern' in first_seg:
            section = first_seg['section']
            # 提取modern里第一个【】的内容
            m = re.match(r'【(.*?)】', first_seg['modern'])
            if m:
                first_title = m.group(1)
                if section != first_title:
                    sutra_issues.append(f"第一段section字段「{section}」与正文首标题「{first_title}」不一致")
    
    issues.append((sid, sutra_issues))

# 输出报告
report = "# 白话佛经独立校对3号worker报告\n\n"
for sid, iss in issues:
    report += f"## {sid}\n"
    if not iss:
        report += "无问题\n\n"
    else:
        for i in iss:
            report += f"- {i}\n"
        report += "\n"

with open(f"{base_path}/proofread_3.md", 'w', encoding='utf-8') as f:
    f.write(report)

print("Report generated.")
print(report)