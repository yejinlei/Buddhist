import json
import os
import re
from openccpy.opencc import OpenCC
# 繁体转简体
cc = OpenCC('t2s')

# 经号列表
sutra_ids = ["t2182", "t2179", "t1041", "t2168a", "t2091", "t2860", "t2086", "t2843", "t2838", "t2857", "t2904", "t1292"]
base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"

problems = []

def is_spell_text(text):
    """判断是否是咒文/真言/梵音/音注部分，这些内容必须照录，不算冗余粘贴"""
    # 包含真言、咒、陀罗尼标记
    if re.search(r"(真言曰|咒曰|呪曰|陀罗尼|陀羅尼|二合|半音|引|反|聲呼|梵字|悉曇|梵语|梵語)", text):
        return True
    # 包含大量梵音常见字
    sanskrit_chars = r"[唵吽嚧哢哆唎娑婆訶薩埵耶涅盤荼楞伽嚩曩迦野戍輸馱麼囉訶怛姪他]"
    if len(re.findall(sanskrit_chars, text)) >= 3:
        return True
    # 包含生僻梵字（unicode私有区字符，这些是梵文种子字）
    if re.search(r"[\U00020000-\U0002FFFF]", text):
        return True
    return False

def check_sutra(sutra_id):
    file_path = os.path.join(base_dir, f"{sutra_id}.json")
    if not os.path.exists(file_path):
        problems.append(f"{sutra_id}|-|文件缺失|文件不存在|请补充该经号的白话译文文件")
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        problems.append(f"{sutra_id}|-|文件读取错误|JSON解析失败：{str(e)}|修复JSON格式")
        return
    
    translations = data.get("translations", [])
    all_modern_names = []
    for seg_idx, seg in enumerate(translations, 1):
        original = seg.get("original_preview", "").strip()
        modern = seg.get("modern", "").strip()
        
        if not modern:
            problems.append(f"{sutra_id}|{seg_idx}|内容缺失|白话译文为空|补充该段白话译文")
            continue
        
        # 1. 格式检查：每段是否以【小标题】开头、接【义解】、【义解】后有正文
        # 匹配开头的标签
        tag_pattern = r"^【[^】]+】【义解】"
        if not re.match(tag_pattern, modern):
            # 检查是否有双【义解】
            yijie_count = modern.count("【义解】")
            if yijie_count > 1:
                problems.append(f"{sutra_id}|{seg_idx}|格式错误|出现{yijie_count}个【义解】标签，存在重复|保留一个【义解】标签，删除重复")
            # 检查开头结构
            if not modern.startswith("【"):
                problems.append(f"{sutra_id}|{seg_idx}|格式错误|段首未以【小标题】开头|段首添加【小标题】标签")
            elif "【义解】" not in modern:
                problems.append(f"{sutra_id}|{seg_idx}|格式错误|缺少【义解】标签|在小标题后添加【义解】标签")
            else:
                problems.append(f"{sutra_id}|{seg_idx}|格式错误|开头结构不符合【小标题】【义解】格式|调整为【小标题】【义解】后接白话正文的结构")
        else:
            # 检查【义解】后是否有正文
            after_yijie = modern.split("【义解】", 1)[1].strip()
            if not after_yijie:
                problems.append(f"{sutra_id}|{seg_idx}|格式错误|【义解】标签后无白话正文|补充白话译文内容")
        
        # 检查半角标点（排除URL、代码、咒文里的？不，半角标点不管什么内容都不应该出现在中文译文里，除非是梵文转写，但这里是中文译文，应该用全角）
        half_punct = re.findall(r"[,.;:!?\(\)\[\]\{\}]", modern)
        if half_punct:
            problems.append(f"{sutra_id}|{seg_idx}|格式错误|存在半角标点：{''.join(half_punct)}|替换为对应的全角标点")
        
        # 检查繁简混用：说明文字必须简体，咒文/古注/经名原文保留原字
        # 提取非标签、非书名号、非咒文部分的文字，检查是否有繁体字
        non_tag = re.sub(r"【[^】]+】", "", modern)
        non_book = re.sub(r"《[^》]+》", "", non_tag)
        # 去掉咒文部分
        non_spell = []
        for part in re.split(r"(真言曰[:：]|咒曰[:：]|呪曰[:：])", non_book):
            if is_spell_text(part) and "真言曰" not in part and "咒曰" not in part and "呪曰" not in part:
                continue
            non_spell.append(part)
        non_spell_text = "".join(non_spell)
        # 转成简体对比，如果有差异说明有繁体字
        simplified = cc.convert(non_spell_text)
        traditional_chars = []
        for o, s in zip(non_spell_text, simplified):
            if o != s and o.strip():
                traditional_chars.append(o)
        if traditional_chars:
            # 排除固定保留的名相："苾芻"、"毘"？不，"毘"现在通常作"毗"，但如果是经名里的保留，不过说明文字里应该用简体？不对，"苾芻"是古译，也可以保留？不对，要求是说明文字必须简体，咒文古注保留原字。如果这些繁体字是在说明文字里，就需要转简体。
            # 去重
            trad_unique = list(set(traditional_chars))
            problems.append(f"{sutra_id}|{seg_idx}|格式错误|说明文字存在繁体字：{''.join(trad_unique)}|说明文字需使用简体中文，咒文、古注、专有经名保留原字")
        
        # 2. 冗余粘贴：检查modern中是否大段照录古文不翻译（非咒文部分）
        modern_content = re.sub(r"【[^】]+】", "", modern).strip()
        # 把modern_content拆分成咒文部分和非咒文部分，只检查非咒文部分是否大段照录原文
        # 先提取modern里的咒文片段，排除出检查范围
        modern_non_spell = []
        # 分割真言/咒之后的内容
        parts = re.split(r"(真言曰[:：]|咒曰[:：]|呪曰[:：])", modern_content)
        for i, part in enumerate(parts):
            if part in ["真言曰：", "真言曰:", "咒曰：", "咒曰:", "呪曰：", "呪曰:"]:
                # 后面跟着的是咒文，跳过下一部分
                continue
            if i > 0 and parts[i-1] in ["真言曰：", "真言曰:", "咒曰：", "咒曰:", "呪曰：", "呪曰:"]:
                # 这部分是咒文，不检查
                continue
            modern_non_spell.append(part)
        modern_non_spell_text = "".join(modern_non_spell)
        
        # 找非咒文部分中连续15字以上和原文完全匹配的片段，排除经名（书名号里的）
        max_common = 0
        common_str = ""
        original_simplified = cc.convert(original)
        modern_non_spell_simplified = cc.convert(modern_non_spell_text)
        for i in range(len(original)):
            for j in range(i+10, len(original)+1):
                substr = original[i:j]
                substr_simp = cc.convert(substr)
                # 排除书名号里的内容
                if f"《{substr}》" in modern or f"《{substr_simp}》" in modern:
                    continue
                # 排除咒文片段
                if is_spell_text(substr):
                    continue
                if substr in modern_non_spell_text or substr_simp in modern_non_spell_simplified:
                    if len(substr) > max_common:
                        max_common = len(substr)
                        common_str = substr
        if max_common >= 15:  # 超过15字的大段照录非咒文古文
            problems.append(f"{sutra_id}|{seg_idx}|冗余粘贴|白话译文中大段照录非咒文类原文古文：{common_str[:30]}...|将该段古文翻译为白话，不要直接粘贴原文（咒文、梵字、音注需照录，不受此限）")
        
        # 3. 咒文/梵字/音注检查：咒文绝对不能意译，必须照录原字。
        # 提取原文中的咒文部分
        spell_matches = list(re.finditer(r"(真言曰|咒曰|呪曰|即說咒曰|即说咒曰)[:：]?\s*(.*?)(?=\n\n|$|由|則|又|如是|修行|即|次|當|應|名|為|成|以|便|即|于是|於是|次|應|當)", original, re.DOTALL))
        for spell_match in spell_matches:
            original_spell = spell_match.group(2).strip()
            # 去掉开头结尾的空白和换行
            original_spell = re.sub(r"\s+", "", original_spell)
            if not original_spell:
                continue
            # 检查译文中是否包含这段咒文（去掉空白）
            modern_spell_check = re.sub(r"\s+", "", modern)
            original_spell_clean = re.sub(r"[\s\(\)\d]+", "", original_spell)  # 去掉括号、数字（序号）、空白
            modern_spell_check_clean = re.sub(r"[\s\(\)\d]+", "", modern_spell_check)
            if original_spell_clean not in modern_spell_check_clean:
                # 检查是否有意译，比如把咒文翻译成意思了，或者错字漏字
                # 计算匹配度
                if len(original_spell_clean) > 5:  # 太短的不判断
                    problems.append(f"{sutra_id}|{seg_idx}|咒文错误|原文咒文未完全逐字照录，存在错字、漏字或意译|咒文、梵字、反切音注必须严格逐字照录原字，不得意译、不得改字漏字")
        
        # 4. 错译漏译：检查原文中提到的典籍/重要内容是否完全翻译
        # 提取原文中的典籍：匹配"X卷"前面的名称，排除总述语句
        # 先去掉括号里的译者注
        orig_no_paren = re.sub(r"（[^）]*）", "", original)
        orig_books = re.findall(r"([^（\n。、]+?)([一二三四五六七八九十百千零]+卷)", orig_no_paren)
        orig_book_names = []
        for b in orig_books:
            bn = b[0].strip()
            # 去掉开头的连接词、总述词
            bn = re.sub(r"^(已上九部並三藏義淨譯|分本末為|分為|或為|今此至人.*|是故今修.*|自達摩後.*|真言經儀軌等合壹佰捌拾卷。|次|又|即|則|當|應)", "", bn)
            bn = bn.strip()
            if bn and len(bn) >= 2 and "卷" not in bn:
                orig_book_names.append(bn)
        # 去重
        orig_book_names = list(set(orig_book_names))
        # 提取译文中的书名
        modern_books = re.findall(r"《([^》]+)》", modern)
        modern_books_simp = [cc.convert(b) for b in modern_books]
        missing_books = []
        for bn in orig_book_names:
            bn_simp = cc.convert(bn)
            found = False
            for mb in modern_books_simp:
                # 简称匹配或者完全匹配
                if bn_simp in mb or mb in bn_simp or bn_simp.replace(" ", "") in mb.replace(" ", ""):
                    found = True
                    break
            if not found:
                missing_books.append(bn)
        if missing_books:
            problems.append(f"{sutra_id}|{seg_idx}|漏译|原文中以下典籍/篇目未在译文中提及：{'、'.join(missing_books)}|补充翻译这些典籍的相关内容")
        
        # 5. 标点疏漏、译名统一
        # 检查句末标点：去掉标签后，正文末尾（包括引号内）应有句末标点
        modern_content_for_punct = re.sub(r"【[^】]+】", "", modern).strip()
        # 去掉末尾的引号
        modern_content_for_punct = modern_content_for_punct.rstrip('”"’')
        if modern_content_for_punct and not re.search(r"[。！？…]$", modern_content_for_punct):
            problems.append(f"{sutra_id}|{seg_idx}|标点疏漏|白话正文句末缺少句号/感叹号/问号等句末标点|补充句末标点")
        
        # 收集译名（人名、寺名、师号）
        names = re.findall(r"(?:三藏|沙门|沙門|法师|法師|律师|律師|菩萨|菩薩|佛|大师|大師|国师|國師|上人|禅师|禪師|仙人|天子|国王|國王|圣王|聖王)[\s]*([\u4e00-\u9fa5·]{2,})", modern)
        all_modern_names.extend(names)
        names2 = re.findall(r"([\u4e00-\u9fa5]{2,4})(?:述|集|译|譯|撰|录|錄|造|注|疏|解|記|记)", modern)
        all_modern_names.extend(names2)
    
    # 单个文件内译名统一检查
    name_map = {}
    for name in all_modern_names:
        name_simp = cc.convert(name)
        if name_simp not in name_map:
            name_map[name_simp] = set()
        name_map[name_simp].add(name)
    for name_simp, variants in name_map.items():
        if len(variants) > 1:
            problems.append(f"{sutra_id}|-|译名不统一|人名/师号“{name_simp}”存在多种译法：{'、'.join(variants)}|同一经内译名需前后统一，说明文字使用简体标准译名")

# 逐个检查
for sid in sutra_ids:
    check_sutra(sid)

# 输出结果
output_path = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/audit-report-D6.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("# 白话译文校对问题列表（D6批次）\n\n")
    f.write("| 经号 | 段号 | 问题类型 | 问题描述 | 修正建议 |\n")
    f.write("|------|------|----------|----------|----------|\n")
    if problems:
        for p in problems:
            parts = p.split("|", 4)
            f.write("| " + " | ".join(parts) + " |\n")
    else:
        f.write("| 全部 | - | 无问题 | 所有经号译文符合检查清单要求 | - |\n")

print(f"校对完成，共发现{len(problems)}个问题，结果已写入{output_path}")
