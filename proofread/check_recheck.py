#!/usr/bin/env python3
import json
import os
import re
import random

random.seed(42)

BASE = "/home/user/workspace/13511660557912876654/buddhist-ontology"
TRANS_DIR = os.path.join(BASE, "data/modern-translation")
ORIG_DIR = os.path.join(BASE, "sutras")

SUTRAS = ["t0818", "t1278", "t1185b", "t1154", "t0339", "t1659", "t0327",
          "t0843", "t2818", "t1737", "t0652", "t0405"]

# 白话中必须简体的繁体黑字表（常见高频错字；注意：婬、瞋、麁在引原文咒文时保留，白话语境中必须改）
TRADITIONAL_BLACKLIST = [
    '時', '這', '為', '說', '無', '眾', '來', '見', '聞', '爾', '於',
    '遶', '國', '後', '還', '過', '進', '開', '將', '點', '對', '發',
    '當', '會', '經', '覺', '實', '處', '長', '樂', '風', '頭', '關',
    '寫', '邊'
]
# 简体替换：白话中这些简体是对的，但咒文中不能用这些简体代替繁体梵字
SIMP_FOR_MANTRA = {
    '罗': '羅', '阇': '闍', '萨': '薩', '诃': '訶', '啰': '囉',
    '弥': '彌', '楼': '樓', '输': '輸', '驮': '馱', '毗': '毘',
    '卢': '盧', '钵': '鉢', '么': '麼', '噜': '嚧', '唵': '唵',
    '陀': '陀', '尼': '尼', '佛': '佛', '迦': '迦', '夜': '夜',
    '耶': '耶', '娑': '娑', '婆': '婆', '阿': '阿', '南': '南',
    '牟': '牟', '帝': '帝', '利': '利', '波': '波', '哆': '哆',
    '伽': '伽', '摩': '摩', '沙': '沙', '醯': '醯', '吽': '吽',
    '泮': '泮', '怛': '怛', '姪': '姪', '他': '他', '伊': '伊',
    '那': '那', '提': '提', '呼': '呼', '藍': '藍', '楞': '楞',
    '皤': '皤', '捨': '捨', '濕': '濕', '縛': '縛', '路': '路',
    '遮': '遮'
}

# 半角标点在中文语境中混用检测
HALF_BAD = re.compile(r'[\u4e00-\u9fff][,!?;:][\u4e00-\u9fff]')

def parse_modern(text):
    """解析modern文本，拆分为title, explanation, content"""
    lines = text.split('\n')
    title = ''
    explanation = ''
    content_lines = []
    state = 'start'
    
    for line in lines:
        line_stripped = line.strip()
        if state == 'start':
            if re.match(r'^【.{1,10}】$', line_stripped):
                title = line_stripped
                state = 'after_title'
            elif line_stripped:
                # 没有标题，直接内容
                content_lines.append(line)
        elif state == 'after_title':
            if line_stripped.startswith('【义解】'):
                explanation = line_stripped[len('【义解】'):].strip()
                state = 'content'
            elif line_stripped:
                # 没有义解，直接内容
                content_lines.append(line)
                state = 'content'
        else:  # content
            content_lines.append(line)
    
    content = '\n'.join(content_lines).strip()
    return title, explanation, content

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_section(num, orig_prev, modern_text, issues=None):
    """检查单个段落"""
    if issues is None:
        issues = []
    
    title, explanation, content = parse_modern(modern_text)
    is_mantra = (title == '【密咒照录】')
    
    # A. 小标题格式
    if not title:
        issues.append((num, 'A-无小标题', '段落缺少【】格式小标题', '添加4-8字中文小标题'))
    elif not re.match(r'^【[\u4e00-\u9fff]{4,8}】$', title):
        issues.append((num, 'A-小标题格式', f'小标题不符合4-8字中文格式: "{title}"', '小标题需为【XXX】格式，4-8字中文，密咒段为【密咒照录】'))
    
    # 密咒段必须是【密咒照录】（如果内容是咒文的话我们靠标题判断）
    
    # B. 义解检查
    if not is_mantra:  # 密咒段也应有义解？按要求B：【义解】必须紧随小标题，不可为空
        if '【义解】' not in modern_text:
            issues.append((num, 'B-缺义解', '小标题后缺少【义解】段', '补充【义解】部分'))
        elif not explanation:
            issues.append((num, 'B-义解为空', '【义解】后内容为空', '补充义解内容'))
    
    # 义解后必须有正文
    if not content:
        issues.append((num, 'B-正文为空', '义解后无白话/咒文正文', '补充正文内容'))
    
    # C. 译者署名换行 + 如是我闻位置（段0）
    if num == 0:
        # 找译者署名行
        content_lines = [l for l in content.split('\n') if l.strip()]
        found_trans = False
        for idx, cl in enumerate(content_lines):
            cl_s = cl.strip()
            if re.search(r'(?:译|奉诏译)\s*$', cl_s):
                # 译者行在句末，后面必须有内容
                if idx + 1 >= len(content_lines):
                    issues.append((num, 'C-译者换行', '译者署名后无正文', '"XX译"后必须换行接正文'))
                found_trans = True
                break
            elif re.search(r'(?:译|奉诏译)', cl_s):
                # 译者署名和正文同一行（末字不是"译"，后面接了其他内容）
                # 排除"译者曰""翻译"这类，但一般译者署名格式是"XXX译"结尾
                after_trans = re.sub(r'^.*?(?:译|奉诏译)\s*', '', cl_s)
                if after_trans and len(after_trans) > 0:
                    issues.append((num, 'C-译者换行', f'译者署名后未换行，同一行接正文: "{cl_s[:80]}..."', '"XX译""XX奉诏译"后必须换行'))
                    found_trans = True
                    break
        
        # "如是我闻"检查：仅当原文original_preview以"如是我聞"开头时，白话才必须有"如是我闻"独占首句
        # （论、疏、仪轨、赞述类文献原文无"如是我闻"，不强制）
        if orig_prev and '如是我聞' in orig_prev[:30]:
            found_ru_shi = False
            for cl in content_lines:
                cl_s = cl.strip()
                if cl_s.startswith('如是我闻'):
                    found_ru_shi = True
                    break
            if not found_ru_shi:
                issues.append((num, 'C-如是我闻位置', f'原文以"如是我聞"开头，但白话正文开头未找到"如是我闻"独占首句', '"如是我闻"必须独占正文首句（译者署名换行后）'))
    
    # D/E. 繁体/简体检查
    if is_mantra:
        # 咒文：正文必须保留梵音译繁体原字
        # 检查简体字是否替换了应保留的繁体
        # 我们只检查常见的错误替换
        simp_err = {
            '罗': '羅', '阇': '闍', '萨': '薩', '诃': '訶', '啰': '囉',
            '弥': '彌', '楼': '樓', '输': '輸', '驮': '馱', '毗': '毘',
            '卢': '盧', '钵': '鉢', '么': '麼', '噜': '嚧'
        }
        for simp, trad in simp_err.items():
            pos = content.find(simp)
            while pos != -1:
                # 排除"反、二合、引"这些注音说明里的简体字（这些是注释，用简体没问题）
                context = content[max(0, pos-15):pos+len(simp)+15]
                if '反' in context or '二合' in context or '引' in context or '注音' in context:
                    pos = content.find(simp, pos+1)
                    continue
                # 排除非咒文部分（义解是白话，用简体）—— 我们只检查content，义解已分离
                issues.append((num, 'E-咒文简体替换', f'咒文中出现简体"{simp}"（应为繁体"{trad}"），上下文: "...{context}..."', f'将咒文中的简体"{simp}"恢复为繁体"{trad}"，保留梵音译原字'))
                pos = content.find(simp, pos+1)
        # 检查反切注音是否保留原字（XX反、XX二合、XX引）—— 这里一般保留就好，不强制繁体
    else:
        # 白话：必须简体，检查黑字表
        for char in TRADITIONAL_BLACKLIST:
            # 检查content、explanation、title
            for text_part, part_name in [(content, '正文'), (explanation, '义解'), (title, '标题')]:
                pos = text_part.find(char)
                if pos != -1:
                    context = text_part[max(0, pos-10):pos+len(char)+10]
                    # 排除是引用原文（如"经文原文"后），但简单点，除了"原文："后的，其他都算
                    # 先排除专有名词引用、书名号内的？简单处理：直接报告
                    issues.append((num, f'D-残留繁体({part_name})', f'{part_name}中残留繁体"{char}"，上下文: "...{context}..."', f'将繁体"{char}"改为简体对应字（时、这、为、说、无等）'))
    
    # F. 重复词、错译、半角标点
    full_text = title + explanation + content
    # 重复词：连续重复2字及以上（排除合理叠字）
    # 注意：密咒段中梵文音译本身大量存在"XYXY"式叠音（如"呼嚧呼嚧"），属于原文正常内容，不检查；
    # 白话段中也要排除"善哉善哉"这类合法重复、以及"像这样像这样"（对应原文"如是如是"，属于特定译法，归G类）
    if not is_mantra:
        repeats = re.finditer(r'([\u4e00-\u9fff]{2,4})\1', full_text)
        seen_repeats = set()
        # 白名单：合法的重复表达（不判为F类错误）
        repeat_whitelist = {'善哉善哉', '如是如是', '快哉快哉', '善来善来', '南无南无', '甚善甚善', '不动不动', '像这样像这样'}
        for m in repeats:
            rep = m.group(1)
            # 排除合法叠字（AA式如"常常"）
            if len(rep) == 2 and rep[0] == rep[1]:
                continue
            if rep in repeat_whitelist or rep + rep in repeat_whitelist:
                continue
            if rep in seen_repeats:
                continue
            seen_repeats.add(rep)
            ctx_start = max(0, m.start() - 10)
            ctx_end = m.end() + 10
            issues.append((num, 'F-重复词', f'白话中出现重复词"{rep}{rep}"，上下文: "...{full_text[ctx_start:ctx_end]}..."', '删除重复词语，保持语句通顺'))
    
    # "白佛陀说"错译
    if '白佛陀说' in full_text:
        issues.append((num, 'F-错译', '出现"白佛陀说"错误译法', '改为"对佛陀说""禀告佛陀"等正确表达'))
    
    # 半角标点混用
    if HALF_BAD.search(full_text):
        m = HALF_BAD.search(full_text)
        issues.append((num, 'F-半角标点', f'半角标点混用: "...{full_text[max(0,m.start()-5):m.end()+5]}..."', '将半角,!?;:改为全角，！？；：，'))
    
    # G. "像这样"过度使用（白话段，非咒文）
    if not is_mantra:
        count = content.count('像这样')
        if count >= 3:
            issues.append((num, 'G-像这样过度', f'单段白话中出现{count}次"像这样"', '替换部分为"如是/如此/尔时/这时"等，使表达更自然'))
    
    return issues

def main():
    all_results = {}
    overall_issues = []
    
    for sutra_id in SUTRAS:
        print(f"Checking {sutra_id}...")
        trans_path = os.path.join(TRANS_DIR, f"{sutra_id}.json")
        orig_path = os.path.join(ORIG_DIR, f"{sutra_id}.json")
        
        trans_data = load_json(trans_path)
        orig_data = load_json(orig_path)
        
        translations = trans_data.get('translations', [])
        total_sections = len(translations)
        sutra_issues = []
        
        # 1. 必查：段0
        check_nums = set([0])
        
        # 2. 必查：末尾5段
        for i in range(max(0, total_sections - 5), total_sections):
            check_nums.add(i)
        
        # 3. 必查：所有【密咒照录】段
        mantra_sections = []
        for i, tr in enumerate(translations):
            if '【密咒照录】' in tr.get('modern', ''):
                check_nums.add(i)
                mantra_sections.append(i)
        
        # 4. 其余随机抽10-15段
        remaining = [i for i in range(total_sections) if i not in check_nums]
        if len(remaining) > 0:
            sample_size = min(15, max(10, len(remaining)))
            if sample_size > len(remaining):
                sample_size = len(remaining)
            sampled = random.sample(remaining, sample_size)
            for i in sampled:
                check_nums.add(i)
        
        # 5. 专项检查：t0818/t0843 中所有"像这样"≥3次的段落必须检查
        if sutra_id in ('t0818', 't0843'):
            for i, tr in enumerate(translations):
                modern = tr.get('modern', '')
                if modern.count('像这样') >= 3:
                    check_nums.add(i)
        
        # H. 核对original_preview是否被改动
        # 先对比原文结构
        orig_translations = orig_data.get('translations', [])
        orig_compare_ok = True
        for i in check_nums:
            if i < len(translations) and i < len(orig_translations):
                trans_op = translations[i].get('original_preview', '').strip()
                orig_op = orig_translations[i].get('original_preview', '').strip()
                if orig_op and trans_op != orig_op:
                    sutra_issues.append((i, 'H-original_preview改动', f'段{i} original_preview与原文不一致', '恢复original_preview为原文内容，不得修改原文'))
                    orig_compare_ok = False
        
        # 检查每个选中的段落
        check_nums_sorted = sorted(list(check_nums))
        for i in check_nums_sorted:
            if i < len(translations):
                tr = translations[i]
                modern = tr.get('modern', '')
                orig_prev = tr.get('original_preview', '')
                sec_issues = check_section(i, orig_prev, modern, issues=[])
                sutra_issues.extend(sec_issues)
        
        # 判定
        passed = len(sutra_issues) == 0
        all_results[sutra_id] = {
            'total': total_sections,
            'checked': len(check_nums_sorted),
            'mantra_count': len(mantra_sections),
            'issues': sutra_issues,
            'passed': passed
        }
        overall_issues.extend([(sutra_id, *iss) for iss in sutra_issues])
        print(f"  {sutra_id}: total={total_sections}, checked={len(check_nums_sorted)}, mantra={len(mantra_sections)}, issues={len(sutra_issues)}")
    
    # 生成报告
    report = []
    report.append("# 第二轮独立复核报告（B batch177）\n\n")
    report.append(f"- 复核时间：2026-11-16\n")
    report.append(f"- 复核经数：{len(SUTRAS)}部\n")
    report.append(f"- 复核范围：每经段0必查、末尾5段必查、所有【密咒照录】段必查，其余段随机抽查10-15段\n")
    report.append(f"- 检查项：A小标题格式/B义解完整性/C格式规范/D白话简体/E咒文繁体/F错漏重复/G「像这样」过度使用/H原文不改动\n\n")
    
    # 总体统计
    total_passed = sum(1 for r in all_results.values() if r['passed'])
    total_issues = sum(len(r['issues']) for r in all_results.values())
    report.append("## 一、总体统计\n\n")
    report.append(f"- ✅ 通过：{total_passed}部\n")
    report.append(f"- ❌ 未通过：{len(SUTRAS) - total_passed}部\n")
    report.append(f"- 问题总数：{total_issues}个\n\n")
    
    # 各类型问题统计
    type_counts = {}
    for sutra, num, typ, frag, sug in overall_issues:
        typ_main = typ.split('-')[0]
        type_counts[typ_main] = type_counts.get(typ_main, 0) + 1
    
    report.append("### 问题类型分布\n\n")
    type_names = {
        'A': 'A类（小标题格式）',
        'B': 'B类（义解/正文完整性）',
        'C': 'C类（格式规范）',
        'D': 'D类（白话残留繁体）',
        'E': 'E类（咒文繁体缺失）',
        'F': 'F类（重复词/错译/标点）',
        'G': 'G类（「像这样」过度使用）',
        'H': 'H类（original_preview改动）'
    }
    for t, c in sorted(type_counts.items()):
        report.append(f"- {type_names.get(t, t)}：{c}个\n")
    
    # 各经结论
    report.append("\n## 二、各经复核结论与问题清单\n")
    for sutra_id in SUTRAS:
        res = all_results[sutra_id]
        status = "✅ 通过" if res['passed'] else "❌ 未通过"
        report.append(f"\n### {sutra_id} {status}\n\n")
        report.append(f"- 总段数：{res['total']}段\n")
        report.append(f"- 实际抽查：{res['checked']}段（段0 + 末尾5段 + 密咒段{res['mantra_count']}段 + 随机抽样）\n")
        if res['issues']:
            report.append(f"- 发现问题：{len(res['issues'])}个\n\n")
            report.append("| 段号 | 问题类型 | 问题片段/描述 | 修改建议 |\n")
            report.append("|:----:|:--------|:-------------|:---------|\n")
            for num, typ, frag, sug in res['issues']:
                frag_clean = str(frag).replace('|', '｜').replace('\n', ' ').strip()
                if len(frag_clean) > 100:
                    frag_clean = frag_clean[:97] + '...'
                sug_clean = str(sug).replace('|', '｜').replace('\n', ' ').strip()
                report.append(f"| {num} | {typ} | {frag_clean} | {sug_clean} |\n")
        else:
            report.append("\n未发现问题，符合翻译规范要求。\n")
    
    out_path = os.path.join(BASE, "proofread/recheck_b_batch177_final.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    print(f"\nReport written to {out_path}")
    print(f"Summary: {total_passed}/{len(SUTRAS)} passed, {total_issues} issues total")

if __name__ == '__main__':
    main()
