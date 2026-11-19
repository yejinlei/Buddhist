#!/usr/bin/env python3
import json
import random
import os
import re
from pathlib import Path

BASE_DIR = Path("/home/user/workspace/13511660557912876654/buddhist-ontology")
TRANSLATION_DIR = BASE_DIR / "data" / "modern-translation"
OUTPUT_FILE = BASE_DIR / "_recheck_B.md"

SUTRAS = [
    # 密教经
    ("t0894a", "密教经，重点检查咒文"),
    ("t1217", "密教经，重点检查咒文"),
    ("t0920", "密教经，重点检查咒文"),
    ("t1299", "密教经，重点检查咒文"),
    # 天台
    ("t1913", "天台宗《止观义例》，检查五时八教/五味四教义理，湛然大师义例"),
    # 净土
    ("t1979", "净土《法事赞》，识别为法事赞而非佛经，小标题区分礼佛/赞偈/发愿/行道"),
    # 大乘经
    ("t0647", "大乘经，检查白话化到位"),
    ("t0321", "大乘经，检查白话化到位"),
    ("t0815", "大乘经，检查白话化到位"),
    ("t0651", "大乘经，检查白话化到位"),
    ("t0346", "大乘经，检查白话化到位"),
    ("t0637", "大乘经，检查白话化到位"),
]

def load_sutra(sutra_id):
    path = TRANSLATION_DIR / f"{sutra_id}.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_modern(modern_text):
    # 解析modern字段：格式是【小标题】\n【义解】...\n正文
    subtitle = ""
    yijie = ""
    body = ""
    lines = modern_text.split("\n")
    i = 0
    if i < len(lines) and lines[i].startswith("【") and lines[i].endswith("】"):
        subtitle = lines[i].strip("【】")
        i += 1
    if i < len(lines) and lines[i].startswith("【义解】"):
        yijie = lines[i][len("【义解】"):].strip()
        i += 1
    body = "\n".join(lines[i:]).strip()
    return subtitle, yijie, body

def check_segment(seg, sutra_type, seg_num):
    issues = []
    modern_full = seg.get("modern", "")
    subtitle, yijie, body = parse_modern(modern_full)
    original = seg.get("original_preview", "")
    
    # 检查段首多余逗号（正文开头）
    if body.startswith("，") or body.startswith(","):
        issues.append(f"正文段首多余逗号")
    # 检查"这样我闻"/"如此我闻"等错误翻译
    if "这样我闻" in body or "如此我闻" in body:
        issues.append(f"错误将固定译法「如是我闻」译为「{body[body.find('我闻')-2:body.find('我闻')]}我闻」，应保留「如是我闻」固定译法")
    # 检查小标题是否是"经义直解"千篇一律
    if subtitle == "经义直解":
        issues.append(f"小标题使用千篇一律的「经义直解」，未概括段意")
    # 检查义解是否空泛
    if len(yijie.strip()) < 20 or yijie.strip() in ["这段经文的义理如下。", "此段义解。", "经文义理直解。", ""]:
        issues.append(f"【义解】内容空泛，无实质法义解读，仅为套话")
    # 检查original_preview是否存在
    if not original:
        issues.append(f"original_preview缺失")
    # 检查繁体残留
    traditional_chars = ["羅", "漢", "長", "發", "國", "經", "後", "為", "與", "眾", "無", "盡", "煩", "惱", "解", "脫", "調", "伏", "象", "內", "外", "清", "淨", "究", "竟", "斷", "除", "陰", "重", "擔", "所", "作", "已", "辦", "受", "後", "有", "猶", "如", "佛", "為", "遷", "動", "學", "地", "謂", "阿", "難", "比", "丘", "寂", "滅", "法", "具", "足", "最", "勝", "住", "意", "識", "種", "在", "神", "通"]
    # 只检查不应该出现的繁体（专有名词除外？不，首轮问题说陀罗尼段汉文繁体未转，其他地方也要转）
    found_fanti = []
    for c in body:
        if c in traditional_chars and c not in ["阿", "難", "比", "丘", "佛", "法"]:  # 这些字简体繁体同形？不对，"羅"是繁体，"罗"是简体
            if c == "羅" and "罗" not in body:
                found_fanti.append(c)
            if c == "漢" and "汉" not in body:
                found_fanti.append(c)
            if c == "長" and "长" not in body:
                found_fanti.append(c)
    if found_fanti:
        issues.append(f"白话正文残留繁体汉字：{''.join(list(set(found_fanti)))}，未完成繁简转换")
    # 密教经特殊检查
    if "密教" in sutra_type:
        # 检查是否有陀罗尼/咒文，汉文繁体未转，咒文与说明混处理
        if "陀羅尼" in original or "咒曰" in original or "真言" in original:
            # 咒文本身是梵文音译，保留繁体？不，首轮问题是"陀罗尼段汉文繁体未转，咒文与说明混处理"，指说明部分的汉文要转简体
            # 检查咒文是否被错误意译
            if "翻译为" in yijie or "意思是" in yijie and "真言" in yijie:
                issues.append(f"陀罗尼/真言咒文被错误意译，密教咒文应保留原音译，不做意译")
            # 检查说明部分是否混在咒文里
            zhou_pos = body.find("咒曰")
            if zhou_pos != -1:
                after_zhou = body[zhou_pos+2:]
                # 如果咒文后面紧跟着汉文说明而没有分隔
                if "即说咒曰" in after_zhou[:20] or "此咒" in after_zhou[:30] or "能" in after_zhou[:20]:
                    issues.append(f"咒文与说明文字混排，未明确分隔咒文与解释说明")
    return issues

def main():
    report = []
    report.append("# 佛经白话精译第二轮独立复核报告（B路）")
    report.append("")
    total_issues = 0
    
    for sutra_id, sutra_type in SUTRAS:
        report.append(f"## {sutra_id}（{sutra_type}）")
        try:
            data = load_sutra(sutra_id)
            segments = data.get("translations", data.get("segments", []))
            total_segs = len(segments)
            report.append(f"- 总段落数：{total_segs}")
            
            if total_segs == 0:
                report.append("- 错误：经文段落数为0，无法复核")
                total_issues += 1
                report.append("")
                continue
            
            # 必查首段和末段
            check_seg_indices = set()
            check_seg_indices.add(0)
            if total_segs >= 2:
                check_seg_indices.add(total_segs - 1)
            # 随机抽查25段
            random.seed(42)  # 固定种子保证可复现
            sample_count = min(25, total_segs - 2)
            if sample_count > 0:
                random_indices = random.sample(range(1, total_segs - 1), sample_count)
                for idx in random_indices:
                    check_seg_indices.add(idx)
            
            sutra_issues = []
            # 天台特殊检查
            if sutra_id == "t1913":
                title = data.get("title", "")
                if "止观义例" not in title and "止觀義例" not in title:
                    sutra_issues.append((0, "经题未正确标识为《止观义例》"))
                for i, seg in enumerate(segments):
                    subtitle, yijie, body = parse_modern(seg.get("modern", ""))
                    original = seg.get("original_preview", "")
                    # 检查五时八教、五味四教义理表述
                    if ("五时" in original or "八教" in original or "五味" in original or "四教" in original or
                        "五時" in original or "八教" in original or "五味" in original or "四教" in original):
                        yijie_text = yijie + body
                        if ("五时八教" not in yijie_text and "华严时" not in yijie_text and "阿含时" not in yijie_text 
                            and "方等时" not in yijie_text and "般若时" not in yijie_text and "法华涅槃时" not in yijie_text
                            and "鹿苑时" not in yijie_text and "鹿苑時" not in yijie_text and "華嚴時" not in yijie_text
                            and "方等時" not in yijie_text and "般若時" not in yijie_text and "法華涅槃時" not in yijie_text
                            and "藏教" not in yijie_text and "通教" not in yijie_text and "别教" not in yijie_text and "圆教" not in yijie_text
                            and "化仪四教" not in yijie_text and "化法四教" not in yijie_text):
                            sutra_issues.append((i+1, "涉及五时八教/五味四教的段落，义解未准确阐释天台宗核心义理"))
                    if "湛然" in original or "荊溪" in original or "止观义例" in original:
                        if "湛然大师" not in yijie and "荆溪湛然" not in yijie:
                            sutra_issues.append((i+1, "涉及作者湛然大师的段落，义解未正确标明作者为天台宗九祖荆溪湛然"))
            # 净土特殊检查
            if sutra_id == "t1979":
                title = data.get("title", "")
                intro = data.get("intro", data.get("translator_note", ""))
                if "法事赞" not in title and "往生禮讚" not in title and "法事讚" not in title and "轉經行道" not in title:
                    sutra_issues.append((0, "未正确识别本作为善导大师《转经行道愿往生净土法事赞》（法事赞类），而非佛说经律论三藏经典"))
                # 检查小标题是否区分类型
                subtitle_types = set()
                for i, seg in enumerate(segments):
                    subtitle, _, _ = parse_modern(seg.get("modern", ""))
                    sub = subtitle
                    if "礼佛" in sub or "禮佛" in sub or "礼拜" in sub or "敬禮" in sub:
                        subtitle_types.add("礼佛/礼拜")
                    if "赞偈" in sub or "赞佛" in sub or "讚佛" in sub or "偈颂" in sub or "偈讚" in sub:
                        subtitle_types.add("赞偈/赞佛")
                    if "发愿" in sub or "回向" in sub or "發願" in sub or "迴向" in sub or "願生" in sub:
                        subtitle_types.add("发愿/回向")
                    if "行道" in sub or "绕佛" in sub or "繞佛" in sub or "行道" in sub:
                        subtitle_types.add("行道/绕佛")
                if len(subtitle_types) < 3:
                    sutra_issues.append((0, f"小标题未充分区分法事赞不同仪轨环节，仅识别到：{', '.join(subtitle_types) if subtitle_types else '无分类'}"))
                # 检查末段是否是流通分？不，法事赞最后是发愿回向
                last_seg = segments[-1]
                _, _, last_body = parse_modern(last_seg.get("modern", ""))
                if "皆大欢喜" in last_body or "信受奉行" in last_body:
                    sutra_issues.append((total_segs, "错误将法事赞末段处理为佛经流通分「皆大欢喜信受奉行」，不符法事赞文体"))
            
            # 大乘经特殊检查白话化
            if "大乘经" in sutra_type:
                wenyan_words = ["乎", "者也", "矣", "焉", "哉", "何以故", "所以者何"]
                for i, seg in enumerate(segments):
                    _, _, body = parse_modern(seg.get("modern", ""))
                    # 排除固定术语和偈颂
                    body_check = body.replace("如是我闻", "").replace("舍利弗", "").replace("须菩提", "")
                    for w in wenyan_words:
                        if w in body_check:
                            if w in ["何以故", "所以者何"]:
                                if "为什么" not in body and "是什么缘故" not in body:
                                    sutra_issues.append((i+1, f"白话译文中残留文言疑问词「{w}」，未译为现代白话"))
                            elif w in ["乎", "矣", "焉", "哉", "者也"]:
                                sutra_issues.append((i+1, f"白话译文中残留文言虚词「{w}」，造成文白夹杂不通顺"))
            
            # 检查选中的段落
            for idx in sorted(check_seg_indices):
                seg = segments[idx]
                seg_issues = check_segment(seg, sutra_type, idx+1)
                if seg_issues:
                    for issue in seg_issues:
                        sutra_issues.append((idx+1, issue))
            
            # 首段特殊检查"如是我闻"
            first_seg = segments[0]
            _, _, first_body = parse_modern(first_seg.get("modern", ""))
            if "如是我闻" not in first_body and ("我闻" in first_body):
                sutra_issues.append((1, "序分开头未使用固定译法「如是我闻」，替换为其他表述不符合译经传统"))
            # 末段特殊检查（大乘经/密教经才检查，天台和净土不用）
            if "大乘经" in sutra_type or "密教经" in sutra_type:
                last_seg = segments[-1]
                _, _, last_body = parse_modern(last_seg.get("modern", ""))
                if "皆大欢喜" not in last_body or "信受奉行" not in last_body:
                    if len(last_body) > 100:  # 长段可能包含流通分
                        sutra_issues.append((total_segs, "流通分末段未包含「皆大欢喜，信受奉行」类流通分译文"))
            
            # 去重
            sutra_issues = list(sorted(set(sutra_issues), key=lambda x: x[0]))
            
            if not sutra_issues:
                report.append("- 复核结果：抽查段落未发现问题")
            else:
                report.append("- 残留问题：")
                for seg_num, issue in sutra_issues:
                    report.append(f"  - 段{seg_num}：{issue}")
                    total_issues += 1
            report.append("")
        except Exception as e:
            report.append(f"- 加载/复核失败：{str(e)}")
            import traceback
            traceback.print_exc()
            report.append("")
            total_issues += 1
    
    report.append("## 整体结论")
    if total_issues == 0:
        report.append("B路第二轮复核零问题，本批可放行")
    else:
        report.append(f"本轮复核共发现 {total_issues} 处问题，需修正后重新复核。")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print(f"复核完成，报告写入 {OUTPUT_FILE}，共发现 {total_issues} 处问题")

if __name__ == "__main__":
    main()
