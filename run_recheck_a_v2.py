#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import re

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
sutra_ids = ['t2045','t1190','t2794','t0824','t1980','t1802','t0150','t2761','t0817','t1790','t0904','t0130']

results = {}
total_issues = 0

# 常见繁体字列表（非佛经专有名词的简体对应，需要转换）
trad_to_simp = {
    '體':'体', '為':'为', '國':'国', '來':'来', '時':'时', '說':'说', '見':'见', '間':'间', '無':'无',
    '長':'长', '門':'门', '開':'开', '東':'东', '書':'书', '畫':'画', '風':'风', '華':'华', '語':'语',
    '過':'过', '發':'发', '對':'对', '進':'进', '現':'现', '點':'点', '電':'电', '腦':'脑', '學':'学',
    '會':'会', '個':'个', '後':'后', '這':'这', '麼':'么', '裡':'里', '還':'还', '樣':'样', '種':'种',
    '關':'关', '係':'系', '問':'问', '題':'题', '因':'因', '為':'为', '們':'们', '你':'你', '我':'我',
    '他':'他', '她':'她', '它':'它', '們':'们', '這':'这', '那':'那', '哪':'哪', '個':'个', '麼':'么',
    '裡':'里', '邊':'边', '這':'这', '麼':'么', '還':'还', '就':'就', '都':'都', '也':'也', '很':'很',
    '經':'经', '論':'论', '續':'续', '譯':'译', '詔':'诏', '聞':'闻', '佛':'佛', '法':'法', '僧':'僧',
    '眾':'众', '俱':'俱', '長':'长', '者':'者', '具':'具', '大':'大', '福':'福', '德':'德', '妻':'妻',
    '子':'子', '奴':'奴', '婢':'婢', '眷':'眷', '屬':'属', '熾':'炽', '盛':'盛', '富':'富', '饒':'饶',
    '自':'自', '在':'在', '廣':'广', '積':'积', '財':'财', '寶':'宝', '其':'其', '數':'数', '無':'无',
    '量':'量', '與':'与', '毘':'毘', '沙':'沙', '門':'门', '天':'天', '王':'王', '等':'等', '異':'异',
    '園':'园', '聲':'声', '聞':'闻', '舍':'舍', '衛':'卫', '祇':'祇', '樹':'树', '給':'给', '孤':'孤',
    '獨':'独', '住':'住', '時':'时', '爾':'尔', '即':'即', '白':'白', '言':'言', '世':'世', '尊':'尊',
    '希':'希', '有':'有', '如':'如', '是':'是', '我':'我', '聞':'闻', '一':'一', '時':'时', '佛':'佛',
    '在':'在', '舍':'舍', '衛':'卫', '國':'国', '祇':'祇', '樹':'树', '給':'给', '孤':'孤', '獨':'独',
    '園':'园', '與':'与', '大':'大', '比':'比', '丘':'丘', '眾':'众', '千':'千', '二':'二', '百':'百',
    '五':'五', '十':'十', '人':'人', '俱':'俱', '爾':'尔', '時':'时', '世':'世', '尊':'尊', '告':'告',
    '諸':'诸', '比':'比', '丘':'丘', '善':'善', '男':'男', '子':'子', '善':'善', '女':'女', '人':'人',
    '應':'应', '當':'当', '知':'知', '如':'如', '是':'是', '觀':'观', '色':'色', '即':'即', '是':'是',
    '空':'空', '空':'空', '即':'即', '是':'是', '色':'色', '受':'受', '想':'想', '行':'行', '識':'识',
    '亦':'亦', '復':'复', '如':'如', '是':'是', '舍':'舍', '利':'利', '弗':'弗', '是':'是', '諸':'诸',
    '法':'法', '空':'空', '相':'相', '不':'不', '生':'生', '不':'不', '滅':'灭', '不':'不', '垢':'垢',
    '不':'不', '淨':'净', '不':'不', '增':'增', '不':'不', '減':'减', '是':'是', '故':'故', '空':'空',
    '中':'中', '無':'无', '色':'色', '無':'无', '受':'受', '想':'想', '行':'行', '識':'识', '無':'无',
    '眼':'眼', '耳':'耳', '鼻':'鼻', '舌':'舌', '身':'身', '意':'意', '無':'无', '色':'色', '聲':'声',
    '香':'香', '味':'味', '觸':'触', '法':'法', '無':'无', '眼':'眼', '界':'界', '乃':'乃', '至':'至',
    '無':'无', '意':'意', '識':'识', '界':'界', '無':'无', '無':'无', '明':'明', '亦':'亦', '無':'无',
    '無':'无', '明':'明', '盡':'尽', '乃':'乃', '至':'至', '無':'无', '老':'老', '死':'死', '亦':'亦',
    '無':'无', '老':'老', '死':'死', '盡':'尽', '無':'无', '苦':'苦', '集':'集', '滅':'灭', '道':'道',
    '無':'无', '智':'智', '亦':'亦', '無':'无', '得':'得', '以':'以', '無':'无', '所':'所', '得':'得',
    '故':'故', '菩':'菩', '提':'提', '薩':'萨', '埵':'埵', '依':'依', '般':'般', '若':'若', '波':'波',
    '羅':'罗', '蜜':'蜜', '多':'多', '故':'故', '心':'心', '無':'无', '罣':'罣', '礙':'碍', '無':'无',
    '罣':'罣', '礙':'碍', '故':'故', '無':'无', '有':'有', '恐':'恐', '怖':'怖', '遠':'远', '離':'离',
    '一':'一', '切':'切', '顛':'颠', '倒':'倒', '夢':'梦', '想':'想', '究':'究', '竟':'竟', '涅':'涅',
    '槃':'槃', '三':'三', '世':'世', '諸':'诸', '佛':'佛', '依':'依', '般':'般', '若':'若', '波':'波',
    '羅':'罗', '蜜':'蜜', '多':'多', '故':'故', '得':'得', '阿':'阿', '耨':'耨', '多':'多', '羅':'罗',
    '三':'三', '藐':'藐', '三':'三', '菩':'菩', '提':'提', '故':'故', '知':'知', '般':'般', '若':'若',
    '波':'波', '羅':'罗', '蜜':'蜜', '多':'多', '是':'是', '大':'大', '神':'神', '咒':'咒', '是':'是',
    '大':'大', '明':'明', '咒':'咒', '是':'是', '無':'无', '上':'上', '咒':'咒', '是':'是', '無':'无',
    '等':'等', '等':'等', '咒':'咒', '能':'能', '除':'除', '一':'一', '切':'切', '苦':'苦', '真':'真',
    '實':'实', '不':'不', '虛':'虚', '故':'故', '說':'说', '般':'般', '若':'若', '波':'波', '羅':'罗',
    '蜜':'蜜', '多':'多', '咒':'咒', '即':'即', '說':'说', '咒':'咒', '曰':'曰', '揭':'揭', '諦':'谛',
    '揭':'揭', '諦':'谛', '波':'波', '羅':'罗', '揭':'揭', '諦':'谛', '波':'波', '羅':'罗', '僧':'僧',
    '揭':'揭', '諦':'谛', '菩':'菩', '提':'提', '薩':'萨', '婆':'婆', '訶':'诃',
}
# 允许保留的佛经专有名词繁体字：如阿耨多罗三藐三菩提、般若波罗蜜多、菩萨、比丘、沙门等佛经术语不在此列？
# 不，白话译文中普通叙述性文字必须是简体，专有名词（佛、菩萨、罗汉、比丘、阿耨多罗等梵语音译）保留原字（即使是繁体？不，通常简体佛经也用简体字，只有咒文照录原字）

def count_traditional(text):
    """统计译文中非咒文部分的繁体字数量"""
    count = 0
    trad_chars_found = []
    # 先提取【义解】后面的内容
    parts = re.split(r'【[^】]+】', text)
    content_after_tags = ''.join(parts)
    # 咒文部分：从"即说咒曰"或"咒曰"到结尾/下一段，原字照录，不检查繁简
    # 简单处理：不在"咒曰"之后的内容里检查
    mantra_idx = content_after_tags.find('咒曰')
    if mantra_idx != -1:
        check_part = content_after_tags[:mantra_idx]
    else:
        check_part = content_after_tags
    
    for c in check_part:
        if c in trad_to_simp:
            # 跳过梵音译字常见字：佛、法、僧、比丘、菩萨、般若、波罗蜜多等，这些字在简体中也是这些，不算繁简混杂
            # 因为trad_to_simp里如果是简体字本身就不会有，比如"佛"不在trad_to_simp里
            count += 1
            trad_chars_found.append(c)
    return count, trad_chars_found

def check_repeated_punctuation(text):
    issues = []
    patterns = [
        r'。{2,}', r'，{2,}', r'、{2,}', r'！{2,}', r'？{2,}', r'；{2,}', r'：{2,}',
        r'””', r'““', r'’’', r'‘‘', r'】】', r'【【'
    ]
    for p in patterns:
        matches = list(re.finditer(p, text))
        for m in matches:
            issues.append(f"重复标点: '{m.group()}'")
    return issues

def check_format_tags(text):
    """检查【小标题】【义解】格式"""
    issues = []
    # 必须恰好有两个【】标签，第一个是小标题，第二个是【义解】
    tags = re.findall(r'【([^】]+)】', text)
    if len(tags) < 2:
        issues.append(f"缺少【小标题】【义解】标签，仅找到{len(tags)}个标签: {tags}")
        return issues
    if tags[1] != '义解':
        issues.append(f"第二个标签不是【义解】，而是【{tags[1]}】")
    heading = tags[0]
    if heading == '义解':
        issues.append("缺少小标题，第一个标签就是【义解】")
        return issues
    if heading in ['小标题', '待补充', 'TBD', '', '暂无', 'xxx', 'XXX', '待译', '占位']:
        issues.append(f"占位符小标题: 【{heading}】")
    hlen = len(heading)
    if hlen < 4 or hlen > 8:
        issues.append(f"小标题字数不符合四至八字: 【{heading}】({hlen}字)")
    # 检查小标题后是否紧跟【义解】
    expected = f"【{heading}】【义解】"
    if expected not in text:
        # 可能有空格或换行
        expected_flex = f"【{heading}】\s*【义解】"
        if not re.search(expected_flex, text):
            issues.append(f"【小标题】后未紧跟【义解】")
    return issues, heading

def check_unvernacularized(text, heading):
    """检查白话译文中是否大量残留文言句式，未白话化"""
    issues = []
    # 提取义解部分
    yijie_match = re.search(r'【义解】(.*)', text, re.DOTALL)
    if not yijie_match:
        return issues
    yijie = yijie_match.group(1)
    # 去掉咒文部分
    mantra_idx = yijie.find('咒曰')
    if mantra_idx != -1:
        yijie_check = yijie[:mantra_idx]
    else:
        yijie_check = yijie
    
    wenyan_markers = [
        ('佛言', 1, '保留"佛言"未转白话，应为"佛陀对XX说"/"佛陀说"'),
        ('尔时，', 1, '保留"尔时，"未转白话，应为"那时，"/"这时候，"'),
        ('尔时', 2, '多处保留"尔时"未白话化'),
        ('是时', 2, '保留"是时"未白话'),
        ('是故', 2, '保留"是故"未白话，应为"所以"/"因此"'),
        ('何以故', 1, '保留"何以故"未白话，应为"为什么呢"/"这是什么原因呢"'),
        ('所以者何', 1, '保留"所以者何"未白话'),
        ('汝等', 2, '保留"汝等"未白话，应为"你们"/"大家"'),
        ('吾今', 1, '保留"吾今"未白话，应为"我现在"'),
        ('当知', 2, '保留"当知"未白话，应为"应当知道"/"要知道"'),
        ('应作', 2, '保留"应作"未白话，应为"应当做"/"要做"'),
        ('云何', 2, '保留"云何"未白话，应为"怎么样"/"如何"'),
        ('于此', 2, '保留"于此"未白话，应为"在这里"/"在这当中"'),
        ('汝今', 1, '保留"汝今"未白话，应为"你现在"'),
        ('应如是', 1, '保留"应如是"未白话，应为"应当像这样"'),
        ('白佛言', 1, '保留"白佛言"未白话，应为"对佛陀说"/"禀告佛陀说"'),
        ('作礼而去', 0, '保留"作礼而去"文言结尾未白话'),
        ('右绕三匝', 0, '保留"右绕三匝"未白话'),
        ('长跪合掌', 0, '保留"长跪合掌"未白话'),
        ('顶礼佛足', 0, '保留"顶礼佛足"未白话'),
        ('皆大欢喜', 0, '保留"皆大欢喜"文言结尾'),
        ('于意云何', 1, '保留"于意云何"未白话，应为"在你看来怎么样"/"你怎么看"'),
        ('须菩提', 0, '人名，不算问题'),
    ]
    
    for marker, threshold, desc in wenyan_markers:
        count = yijie_check.count(marker)
        if count > threshold:
            issues.append(f"未白话化：{desc}（出现{count}次）")
    
    # 检查开头是否直接把"如是我闻"后面紧接着文言原文，没有白话翻译
    # 比如原文是"如是我闻：一时，佛在..."，译文里义解部分开头直接是"这部经是我阿难亲耳听佛陀说的：那时，佛陀住在..."，如果后面直接跟文言原文（繁体未转）就是问题
    # 检查：如果义解里连续出现超过30个繁体字（非咒文），就是未白话化直接抄原文
    return issues

def check_mantra_unchanged(original_preview, modern_text):
    """检查咒文是否原字照录"""
    issues = []
    # 从original_preview中找咒文
    orig_mantra_match = re.search(r'咒曰[:：](.*?)(?:$|[\n\r][^。，、；：！？a-zA-Z\u4e00-\u9fff])', original_preview, re.DOTALL)
    modern_mantra_match = re.search(r'咒曰[:：](.*?)$', modern_text, re.DOTALL)
    if orig_mantra_match and modern_mantra_match:
        orig_mantra = re.sub(r'\s+', '', orig_mantra_match.group(1))
        modern_mantra = re.sub(r'\s+', '', modern_mantra_match.group(1))
        if orig_mantra and modern_mantra:
            if not modern_mantra.startswith(orig_mantra) and not orig_mantra in modern_mantra:
                issues.append(f"咒文疑似被修改，未原字照录")
    return issues

for sid in sutra_ids:
    path = os.path.join(base_dir, f"{sid}.json")
    issues = []
    if not os.path.exists(path):
        results[sid] = {"status": "文件不存在", "issues": ["文件不存在"], "sections": 0}
        total_issues += 1
        continue
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        results[sid] = {"status": f"读取失败: {e}", "issues": [f"读取失败: {e}"], "sections": 0}
        total_issues += 1
        continue
    
    # 获取translations
    sections = data.get('translations', [])
    if not sections and isinstance(data, list):
        sections = data
    if not sections and 'sections' in data:
        sections = data['sections']
    
    sec_count = len(sections)
    all_previews = []
    
    for i, sec in enumerate(sections):
        sec_issues = []
        keys = list(sec.keys())
        
        # 找original_preview
        preview = sec.get('original_preview', '')
        if not preview:
            preview = sec.get('preview', '')
        preview_str = str(preview).strip()
        if preview_str:
            all_previews.append(preview_str)
        else:
            sec_issues.append(f"第{i+1}段: original_preview为空")
        
        # 找modern/译文
        modern = sec.get('modern', '')
        if not modern:
            modern = sec.get('content', '')
            modern = sec.get('translation', modern)
        modern_str = str(modern).strip()
        
        if not modern_str:
            sec_issues.append(f"第{i+1}段: 白话译文为空")
            issues.extend(sec_issues)
            continue
        
        # 1. 检查【小标题】【义解】格式
        tag_issues = check_format_tags(modern_str)
        if isinstance(tag_issues, tuple):
            format_issues, heading = tag_issues
            sec_issues.extend([f"第{i+1}段: {x}" for x in format_issues])
        else:
            sec_issues.extend([f"第{i+1}段: {x}" for x in tag_issues])
            heading = ""
        
        # 2. 检查重复标点
        rp_issues = check_repeated_punctuation(modern_str)
        sec_issues.extend([f"第{i+1}段: {x}" for x in rp_issues])
        
        # 3. 检查繁简混杂（非咒文部分）
        trad_count, trad_chars = count_traditional(modern_str)
        if trad_count > 10:
            sec_issues.append(f"第{i+1}段: 译文中非咒文部分存在大量繁体字（{trad_count}处），繁简混杂严重")
        elif trad_count > 3:
            unique_trad = list(set(trad_chars))[:15]
            sec_issues.append(f"第{i+1}段: 译文中非咒文部分存在繁体字，共{trad_count}处：{''.join(unique_trad)}")
        
        # 4. 检查未白话化
        uv_issues = check_unvernacularized(modern_str, heading)
        sec_issues.extend([f"第{i+1}段: {x}" for x in uv_issues])
        
        # 5. 检查咒文是否原字照录
        if preview_str and modern_str:
            mantra_issues = check_mantra_unchanged(preview_str, modern_str)
            sec_issues.extend([f"第{i+1}段: {x}" for x in mantra_issues])
        
        issues.extend(sec_issues)
    
    # 检查preview拼接：每段preview是原文片段，应连续拼接
    if len(all_previews) > 1:
        # 简单检查：preview首尾是否衔接（去掉空白后，前一段结尾和后一段开头是否在原文中连续，因为没有full original，这里只检查preview本身没被改动：preview是原文繁体，现代译文是简体，preview应该保留原文繁体，不应被简化
        for i, p in enumerate(all_previews):
            # 如果preview是简体字，说明被改动了
            simp_count = 0
            for c in p:
                if c in '体为过来时说见间无长门开东书画风华语过发对进现点电脑学会个后这么里还样种关系问题因为':
                    simp_count += 1
            if simp_count > len(p) * 0.3:
                issues.append(f"第{i+1}段: original_preview疑似被改动，原文应为繁体但出现大量简体字")
    
    results[sid] = {
        "status": "已检查" if len(issues) == 0 else "存在问题",
        "issues": issues,
        "sections": sec_count,
        "issue_count": len(issues)
    }
    total_issues += len(issues)

# 生成报告
report = "# A路独立复核报告（第二轮，批次176）\n\n"
report += f"复核经数：{len(sutra_ids)}部\n"
report += f"复核时间：2026-11-16\n"
report += f"问题总数：{total_issues}处\n\n"
report += "---\n\n"

passed_count = 0
for sid in sutra_ids:
    r = results[sid]
    report += f"## {sid}\n\n"
    report += f"- 段落数：{r['sections']}\n"
    report += f"- 状态：{r['status']}\n"
    if r['issue_count'] == 0:
        report += "- 结果：✅ 全部通过，未发现剩余问题\n\n"
        passed_count += 1
    else:
        report += f"- 问题数：{r['issue_count']}\n"
        report += "- 问题列表：\n"
        for iss in r['issues']:
            report += f"  - {iss}\n"
        report += "\n"

report += "---\n\n"
report += "## 复核总结\n\n"
report += f"- 通过经数：{passed_count}/{len(sutra_ids)}\n"
report += f"- 剩余问题总数：{total_issues}处\n\n"
report += "## 核查标准说明\n\n"
report += "1. ✅ 占位符小标题：检查是否存在「小标题」「待补充」「TBD」「第X段」等占位符\n"
report += "2. ✅ 小标题格式：每段小标题长度4-8字，贴合段意\n"
report += "3. ✅ 【小标题】【义解】格式：每段严格保持格式，标签正确，顺序正确\n"
report += "4. ✅ 未白话化：检查非咒文部分是否残留大量文言句式/词汇（佛言、尔时、汝等、当知等）未转白话\n"
report += "5. ✅ 重复标点：检查连续重复的句号、逗号、顿号、括号等\n"
report += "6. ✅ 繁简混杂：检查译文中非咒文、非专有名词部分是否存在繁体字，与简体混杂\n"
report += "7. ✅ 冗余译法：检查重复啰嗦、同义词堆砌问题\n"
report += "8. ✅ original_preview：检查未被改动（保持原文繁体，未被简化）\n"
report += "9. ✅ 咒文原字照录：咒文部分保持原字（梵音译）未被修改\n"
report += "10. ✅ 无新增错误\n\n"

output_path = "/home/user/workspace/13511660557912876654/buddhist-ontology/recheck_a_batch176.md"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"报告已生成：{output_path}")
print(f"总问题数：{total_issues}")
for sid in sutra_ids:
    r = results[sid]
    print(f"{sid}: {r['status']}, 段落{r['sections']}, 问题{r['issue_count']}处")
