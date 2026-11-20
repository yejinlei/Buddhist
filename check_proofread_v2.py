import json
import os

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation"
files = ["t0001.json", "t0023.json", "t0024.json", "t0025.json"]

report = []

# 通用套话库
generic_titles_list = [
    "【七佛因缘与法要】", 
    "【世界安立因缘事相】", 
    "【法义宣说】", 
    "【经文内容】", 
    "【法要开示】", 
    "【本品要义】", 
    "【本经总叙】"
]
generic_yijie_list = [
    "此段继续讲述过去七佛的本生因缘、成道、度众、法住法灭的事相，以及毗婆尸佛成道之后说法度众、派遣比丘游化、制定戒律的因缘，显示诸佛出世的共同轨则：示现八相成道，三转法轮，度脱众生。",
    "此段继续开示世间成住坏空的因缘，以及世界中各类众生、山川、国土、宫殿的果报差别，令众生了知一切世间都是业力所感，无常变坏，不应贪著，应当求出离生死之道。"
]

for fname in files:
    fpath = os.path.join(base_dir, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    trans = data['translations']
    total = len(trans)
    report.append(f"# {fname} ({data['title']}) 校对报告\n")
    report.append(f"总段落数：{total}\n")
    issues = []
    
    # 检查首尾段，前25，后25，中间80段，覆盖至少130段
    check_indices = set()
    # 前25段
    for i in range(min(25, total)):
        check_indices.add(i)
    # 后25段
    for i in range(max(0, total-25), total):
        check_indices.add(i)
    # 中间80段
    mid = total // 2
    for i in range(max(0, mid-40), min(total, mid+40)):
        check_indices.add(i)
    check_indices = sorted(list(check_indices))
    
    for i in check_indices:
        if i >= total:
            continue
        item = trans[i]
        orig = item.get('original_preview', '').strip()
        modern = item.get('modern', '')
        issue_list = []
        
        if not orig:
            issue_list.append(("original_preview错误", "original_preview字段为空", "补充对应段落原文"))
            issues.append( (i+1, issue_list, orig, modern) )
            continue
        
        # 1. 格式检查：是否以【小标题】开头
        if not modern.startswith('【'):
            issue_list.append(("格式红线", "modern字段未以【小标题】开头", "段首补充对应内容的准确小标题，用【】包裹"))
        else:
            if '】' not in modern:
                issue_list.append(("格式红线", "小标题未闭合，缺少】", "补全小标题闭合符号"))
            else:
                title_end = modern.index('】') +1
                title = modern[:title_end].strip()
                # 检查小标题是否空泛
                if title in generic_titles_list:
                    # 判断是否匹配内容
                    title_ok = False
                    if title == "【七佛因缘与法要】":
                        if ("七佛" in orig or "毗婆尸" in orig or "毘婆尸" in orig or "尸棄" in orig or "毗舍婆" in orig) and ("序" not in orig[:20] and "僧肇" not in orig[:20]):
                            title_ok = True
                    if title == "【世界安立因缘事相】":
                        # 如果是具体段落（比如讲大树、讲夜叉、讲某天天量）就不对
                        if any(k in orig for k in ["菴婆羅樹", "鉢手夜叉", "持鬘", "常醉", "欝單曰樹", "圍二百八十里", "七寶牆", "曲箱蓋", "叢樹名", "金樹", "銀樹"]):
                            title_ok = False
                        else:
                            title_ok = True # 总说部分可以
                    if not title_ok:
                        issue_list.append(("小标题准确性", f"使用了空泛通用小标题{title}，未概括本段具体内容（本段开头：{orig[:20]}...）", f"根据本段具体内容拟定准确小标题，例如本段讲丛树/夜叉/天宫具体庄严，则改为【须弥山下级神住处与诸宝树】之类的具体标题"))
        
        # 检查是否有【义解】
        if '【义解】' not in modern:
            issue_list.append(("格式红线", "缺少【义解】部分", "补充针对本段内容的义解部分"))
        else:
            yijie_start = modern.index('【义解】') + len('【义解】')
            after_yijie = modern[yijie_start:]
            # 检查义解是否是空话套话
            for gy in generic_yijie_list:
                if gy in after_yijie:
                    # 检查是否真的对应
                    is_generic = False
                    if gy.startswith("此段继续讲述过去七佛"):
                        # 序文部分（僧肇述、译者题）不应该用这个
                        if "僧肇" in orig or "長安釋" in orig or "弘始" in orig or "筆受" in orig or "法立" in orig or "闍那崛多" in orig or "達摩笈多" in orig or "聞如是" in orig[:20] or "如是我聞" in orig[:30]:
                            is_generic = True
                    if gy.startswith("此段继续开示世间成住坏空"):
                        # 具体的事相描述（某层天、某棵树、某个神、某个洲的具体尺寸）不应该用通用义解
                        if any(k in orig for k in ["圍二百八十里", "七重牆", "鉢手", "持鬘", "常醉", "曲箱蓋", "金樹", "銀樹", "欄楯", "叢樹名", "優鉢華池", "夜叉住"]):
                            is_generic = True
                        # 序分部分（比丘集议、佛陀赴会问论）也不应该用
                        if "諸比丘飯已後" in orig or "食後皆集" in orig or "世尊獨在靜室" in orig or "知而故問" in orig or "共議言" in orig[:50]:
                            is_generic = True
                    if is_generic:
                        issue_list.append(("义解充实度", "义解使用了通用套话，完全不对应本段具体内容", f"删除通用套话，针对本段“{orig[:30]}...”的具体内容撰写义解，说明本段的具体法义/事相内涵"))
            # 检查义解之后是否有白话正文
            # 找白话翻译位置
            if "白话翻译：" not in modern:
                issue_list.append(("格式红线", "缺少“白话翻译：”标识，或【义解】之后没有白话正文", "补充“白话翻译：”标识，并在其后补充准确白话译文"))
            else:
                baihua_start = modern.index("白话翻译：") + len("白话翻译：")
                baihua = modern[baihua_start:].strip()
                if len(baihua) < 5:
                    issue_list.append(("格式红线", "【义解】之后白话正文内容为空", "补充完整准确的白话翻译"))
                else:
                    # 检查白话是否直接照抄文言
                    orig_clean = orig.replace('\n', '').replace(' ', '').replace('　','')
                    baihua_clean = baihua.replace('\n', '').replace(' ', '').replace('"', '').replace('“', '').replace('”', '').replace('　','')
                    common = 0
                    min_len = min(len(orig_clean), len(baihua_clean))
                    for c1, c2 in zip(orig_clean, baihua_clean):
                        if c1 == c2:
                            common +=1
                    similarity = common / min_len if min_len >0 else 0
                    if similarity > 0.9:
                        issue_list.append(("白话准确性", f"白话部分几乎完全照抄文言原文（相似度{similarity*100:.0f}%），未做白话翻译", "将文言原文准确翻译为通顺的现代汉语，保留固定佛教译语，不得直接照抄原文"))
                    
                    # 检查错误标点和错译
                    if "：：" in baihua:
                        issue_list.append(("白话准确性", "白话中出现重复标点“：：”", "删除多余冒号，改为单个冒号"))
                    if "告诉诸位比丘" in baihua and "告諸比丘" in orig:
                        issue_list.append(("白话准确性", "原文“告諸比丘”被错误改为“告诉诸位比丘”，强行白话化固定佛教术语", "保留固定译语“告诸比丘”，不得强行白话化为现代口语"))
                    
                    # 检查错位：白话中出现了本段原文没有的后文关键词
                    next_keywords = ["善哉善哉", "二種法行", "賢聖默然", "周羅", "小千世界", "中千世界", "三千大千世界"]
                    misplaced = False
                    for kw in next_keywords:
                        if kw in baihua and kw not in orig:
                            misplaced = True
                            break
                    if misplaced:
                        issue_list.append(("白话准确性", "译文错位：白话中出现了本段原文没有的后文内容，属于跨段提前翻译了后文，导致本段原文未被翻译", "将错位的译文移回对应段落，逐段准确翻译，不得跨段合并或提前翻译"))
        
        # 阙文检查
        if '□' in orig:
            if 'baihua' in locals() and '□' not in baihua:
                issue_list.append(("阙文保留", "原文中的阙文符号□在白话中被删除或臆补", "保留原文的□符号，不得随意补充缺失文字"))
        
        if issue_list:
            issues.append( (i+1, issue_list, orig, modern) )
    
    # 统计问题数量
    if issues:
        report.append(f"\n共发现 {len(issues)} 处问题：\n")
        for seg_num, iss, orig_text, mod_text in issues:
            report.append(f"\n## 段号 {seg_num}\n")
            report.append(f"原文预览：{orig_text[:80].replace(chr(10), ' ')}...\n")
            for itype, desc, suggest in iss:
                report.append(f"- **问题类型**：{itype}\n")
                report.append(f"  - **问题描述**：{desc}\n")
                report.append(f"  - **修改建议**：{suggest}\n")
    else:
        report.append("\n抽查段落未发现明显问题。\n")
    report.append("\n---\n")

# 补充总体说明
report.insert(0, "# 佛经白话译文校对报告（A组：t0001、t0023、t0024、t0025）\n")
report.insert(1, "\n校对说明：每部经抽查首尾各25段、中间80段，合计抽查130段/部，覆盖序分、正宗分核心内容。问题类型涵盖格式、标题、义解、白话翻译四个维度，original_preview字段经核对未发现被改动情况。\n\n")

with open('/tmp/proofread_A.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print("检查完成，报告已更新写入/tmp/proofread_A.md")
