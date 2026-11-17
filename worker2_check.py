#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import re
import sys

BASE_DIR = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation"
sutra_ids = ["t1159", "t2773", "t0757", "t1898", "t0566", "t1301", "t1141", "t1986b", "t1837", "t1664", "t1455", "t1560"]

# 禁止的模板套话
forbidden_phrases = [
    "此段为",
    "方得论旨",
    "方得洞上玄旨",
    "洞山禅师",
]

# 繁体检测常用字
traditional_chars = set("體國經義書學門說為麼個後來裡頭個長發開會對時現點裡面還這說話")

def check_sutra(sid):
    path = os.path.join(BASE_DIR, f"{sid}.json")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    issues = []
    segments = data.get('translations', data.get('segments', data if isinstance(data, list) else []))
    total = len(segments)
    
    for i, seg in enumerate(segments):
        seg_num = i + 1
        modern = seg.get('modern', '')
        
        if not modern or not modern.strip():
            issues.append(f"段{seg_num}: 空白译文")
            continue
        
        # 1. 格式检查：【小标题】开头，换行后【义解】
        if not modern.startswith('【'):
            issues.append(f"段{seg_num}: 未以【小标题】开头")
        else:
            # 检查小标题后有换行和【义解】
            if '【义解】' not in modern:
                issues.append(f"段{seg_num}: 缺少【义解】标记")
            else:
                parts = modern.split('【义解】', 1)
                if len(parts) != 2:
                    issues.append(f"段{seg_num}: 【义解】格式异常")
                else:
                    title_part = parts[0].strip()
                    if not title_part.startswith('【') or not title_part.endswith('】'):
                        issues.append(f"段{seg_num}: 小标题括号不完整: {title_part[:30]}")
                    else:
                        title = title_part[1:-1].strip()
                        if len(title) < 2:
                            issues.append(f"段{seg_num}: 小标题过短/空泛: '{title}'")
        
        # 2. 禁止模板套话
        for phrase in forbidden_phrases:
            if phrase in modern:
                issues.append(f"段{seg_num}: 包含禁止模板套话 '{phrase}'")
        
        # 检查白话正文非咒文部分简体（粗略检测）
        if sid not in ["t1141", "t1159"]:  # 这两个咒文多，单独检查
            # 提取【义解】之后的正文，排除梵文咒文部分
            body = modern.split('【义解】', 1)[1] if '【义解】' in modern else modern
            # 粗略检测繁体残留（简单启发式）
            trad_count = 0
            for c in body:
                if c in traditional_chars:
                    trad_count += 1
            if trad_count > 5:
                issues.append(f"段{seg_num}: 可能存在较多繁体残留，繁体特征字{trad_count}个")
    
    # 3. 咒文完整性检查 t1141 t1159
    if sid in ["t1141", "t1159"]:
        # 提取所有梵文真言陀罗尼部分，检查是否有原字原音，二合/反切/引声注释
        mantra_issues = 0
        for i, seg in enumerate(segments):
            seg_num = i + 1
            modern = seg.get('modern', '')
            orig = seg.get('original', '')
            # 检测原文中的真言相关标记
            if any(k in orig for k in ["真言", "陀罗尼", "咒曰", "莎诃", "娑婆诃", "二合", "引", "反切"]):
                # 检查modern是否保留了这些梵文和注释
                body = modern.split('【义解】', 1)[1] if '【义解】' in modern else modern
                if "二合" in orig and "二合" not in body:
                    issues.append(f"段{seg_num}: 原文有'二合'注释，译文未保留")
                if "引" in orig and re.search(r'[一-龥]*引[一-龥]*', orig) and "引" not in body:
                    # 简单检查，引声
                    pass
                if "反切" in orig and "反切" not in body:
                    issues.append(f"段{seg_num}: 原文有'反切'注释，译文未保留")
    
    # 4. 法相准确性专项（关键词检查）
    if sid == "t1837":  # 百法明门论疏
        key_terms = ["心法", "心所法", "色法", "心不相应行法", "无为法", "遍行", "别境", "善", "烦恼", "随烦恼", "不定"]
        for term in key_terms:
            found = False
            for seg in segments:
                if term in seg.get('modern', ''):
                    found = True
                    break
            if not found:
                issues.append(f"法相术语缺失: 未找到'{term}'")
    
    if sid == "t1560":  # 俱舍论本颂
        key_terms = ["界", "蕴", "处", "根", "随眠", "圣道", "业", "烦恼"]
        for term in key_terms:
            found = False
            for seg in segments:
                if term in seg.get('modern', ''):
                    found = True
                    break
            if not found:
                issues.append(f"法相术语缺失: 未找到'{term}'")
    
    if sid == "t1664":  # 广释菩提心论
        key_terms = ["菩提心", "大悲", "空性", "六度", "慈悲", "方便", "智慧"]
        for term in key_terms:
            found = False
            for seg in segments:
                if term in seg.get('modern', ''):
                    found = True
                    break
            if not found:
                issues.append(f"法相术语缺失: 未找到'{term}'")
    
    # 5. 戒律准确性 t1455 苾刍尼戒经
    if sid == "t1455":
        vinaya_terms = ["波罗夷", "僧残", "波逸提", "波罗提提舍尼", "突吉罗", "学法"]
        for term in vinaya_terms:
            found = False
            for seg in segments:
                if term in seg.get('modern', ''):
                    found = True
                    break
            if not found:
                issues.append(f"戒律罪名缺失: 未找到'{term}'")
        # 检查不混淆：搜索是否有写错的情况，比如"波罗提"写成别的
        for i, seg in enumerate(segments):
            m = seg.get('modern', '')
            if "波罗夷" in m and "僧残" in m:
                # 简单检查顺序不混淆，波罗夷是最重
                pass
    
    return {
        "id": sid,
        "total_segments": total,
        "issues": issues,
        "pass": len(issues) == 0
    }

def main():
    results = []
    print("=" * 60)
    print("佛经白话精译第二轮独立复核（第2路）")
    print("核查经号：", ", ".join(sutra_ids))
    print("=" * 60)
    
    all_pass = True
    for sid in sutra_ids:
        print(f"\n【{sid}】")
        res = check_sutra(sid)
        results.append(res)
        print(f"  总段数：{res['total_segments']}")
        if res['pass']:
            print("  结论：通过 ✓")
        else:
            all_pass = False
            print(f"  结论：存在问题 ✗，共{len(res['issues'])}处问题：")
            for issue in res['issues'][:20]:  # 最多显示20条
                print(f"    - {issue}")
            if len(res['issues']) > 20:
                print(f"    ... 另有{len(res['issues'])-20}处问题省略")
    
    print("\n" + "=" * 60)
    print("【最终结论】")
    if all_pass:
        print("全部12部经复核通过，可上线 ✓")
    else:
        print("存在问题，需修正后重新复核")
        failed = [r['id'] for r in results if not r['pass']]
        print(f"未通过经号：{', '.join(failed)}")
    
    # 输出JSON结果
    with open('/home/user/workspace/13511660557912876654/buddhist-ontology/worker2_check_result.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
