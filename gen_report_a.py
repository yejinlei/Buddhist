import json
import re
import os

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
sutra_ids = ['t2045','t1190','t2794','t0824','t1980','t1802','t0150','t2761','t0817','t1790','t0904','t0130']

issues = []
sutra_info = {}

def check_segment(sid, idx, op, modern):
    op = op.strip()
    modern = modern.strip()
    
    # 1 original_preview为空
    if not op:
        issues.append(f"{sid}-{idx}-字段缺失-original_preview字段为空-请补充对应原文预览内容")
    
    # 2 modern为空
    if not modern:
        issues.append(f"{sid}-{idx}-字段缺失-modern字段为空-请补充完整白话译文")
        return
    
    # 3 开头小标题检查
    if not modern.startswith('【'):
        issues.append(f"{sid}-{idx}-格式错误-modern未以【】格式的小标题开头-请在段首添加四至八字的小标题，格式为【小标题】")
    else:
        first_end = modern.find('】')
        if first_end == -1:
            issues.append(f"{sid}-{idx}-格式错误-开头小标题缺少闭合】符号-请补全小标题的闭合括号")
        else:
            title_part = modern[1:first_end]
            title_len = len(title_part)
            if title_len <4 or title_len >8:
                issues.append(f"{sid}-{idx}-格式错误-开头小标题「{title_part}」字数为{title_len}字，不符合四至八字要求-请将小标题调整为4-8字，准确概括段落内容")
            # 检查无意义小标题
            bad_titles = ['经文第X节', '持名礼拜']
            if title_part in ['持名礼拜'] and '禮拜' not in op and '禮' not in op[:50]:
                issues.append(f"{sid}-{idx}-格式错误-小标题「持名礼拜」与段落内容不符，本段非礼拜内容-请更换为准确概括本段大意的四至八字小标题")
            if re.match(r'^经文第\d+节$', title_part):
                issues.append(f"{sid}-{idx}-格式错误-小标题「{title_part}」过于笼统，未概括段落实际内容-请更换为能体现本段核心义理的四至八字小标题")
    
    # 4 义解标记检查
    if '【义解】' not in modern:
        issues.append(f"{sid}-{idx}-格式错误-modern字段缺少【义解】标记-请在小标题后添加【义解】标记，之后接白话译文")
    else:
        yj_pos = modern.find('【义解】')
        after_yj = modern[yj_pos+4:].strip()
        # 义解后为空
        if not after_yj:
            issues.append(f"{sid}-{idx}-内容缺失-【义解】标记后无正文内容，译文为空-请补充义解后的白话译文")
        else:
            # 重复标点
            punc_errors = []
            if '，，' in after_yj: punc_errors.append('连续逗号「，，」')
            if '。。' in after_yj: punc_errors.append('连续句号「。。」')
            if '：：' in after_yj: punc_errors.append('连续冒号「：：」')
            if punc_errors:
                issues.append(f"{sid}-{idx}-格式错误-译文中存在{','.join(punc_errors)}等重复标点错误-请删除多余标点，修正为规范中文标点")
            
            # 完全照搬原文检查
            op_clean = re.sub(r'\s+', '', op)
            after_clean = re.sub(r'\s+', '', after_yj)
            # 去除译文开头可能的提示语
            if after_clean.startswith('以下为神咒原文'):
                pass # 咒文提示是正常的
            elif op_clean == after_clean:
                issues.append(f"{sid}-{idx}-内容错误-【义解】后完全照搬文言原文，未作白话翻译-请将本段文言经文完整翻译为通顺现代汉语白话，不得直接照录原文")
            elif len(after_clean) > 50 and after_clean[:50] == op_clean[:50] and not any(kw in after_yj for kw in ['就是说', '意思是', '这是说', '指的是', '佛陀说', '应当', '应该', '就是', '这是']):
                # 开头50字和原文完全一致，疑似大段照搬
                copy_ratio = 0
                for a,b in zip(after_clean, op_clean):
                    if a == b: copy_ratio +=1
                    else: break
                if copy_ratio / len(op_clean) > 0.9:
                    issues.append(f"{sid}-{idx}-内容错误-【义解】后{int(copy_ratio/len(op_clean)*100)}%内容照搬文言原文，几乎未作白话翻译-请将本段经文完整翻译为通顺白话，仅咒文部分保留原字")
            
            # 奇怪的混入词汇检查
            weird_words = ['为什么', '太好了', '这时候', '出家受具足戒的男众僧人', '一切有情众生']
            found_weird = []
            for w in weird_words:
                if w in after_yj:
                    found_weird.append(w)
            if found_weird:
                if '为什么' in found_weird:
                    issues.append(f"{sid}-{idx}-翻译错误-译文中混入现代口语词「为什么」，应为文言「云何/何以」对应白话「为什么是」，但此处直接插入原文打断译文-请统一翻译风格，删除突兀的口语词，通顺整段译文")
                if '太好了' in found_weird:
                    issues.append(f"{sid}-{idx}-翻译错误-译文中混入不合语境的现代口语词「太好了」，不符合佛经译文庄重风格-请删除该口语词，根据原文「善哉」准确翻译为「善哉」或「很好」")
                if '这时候' in found_weird and after_yj.count('这时候') > 2:
                    issues.append(f"{sid}-{idx}-翻译错误-译文中大量重复插入口语词「这时候」（共{after_yj.count('这时候')}处），打断译文连贯性，风格不统一-请删除多余的「这时候」，根据原文「尔时/于是」自然翻译，保持译文流畅")
                if '出家受具足戒的男众僧人' in found_weird:
                    issues.append(f"{sid}-{idx}-翻译错误-译文中多次将「比丘」生硬翻译为「出家受具足戒的男众僧人」，表述冗余且不符合佛教用语习惯-请统一译为「比丘」或「僧人」，保持译文简洁庄重")
                if '一切有情众生' in found_weird:
                    issues.append(f"{sid}-{idx}-翻译错误-译文中将「群生/众生」译为「一切有情众生」存在语义重复（有情即众生），且部分位置突兀插入-请统一译为「众生」或「有情」，避免冗余")
            
            # 检查咒文部分
            if any(kw in op for kw in ['咒曰', '呪曰', '真言', '陀羅尼']):
                zhou_start = max(op.find('咒曰'), op.find('呪曰'))
                if zhou_start != -1:
                    op_zhou = op[zhou_start+2:].strip()
                    m_zhou_start = max(after_yj.find('咒曰'), after_yj.find('呪曰'))
                    if m_zhou_start == -1:
                        issues.append(f"{sid}-{idx}-内容错误-本段包含咒文但【义解】后未标注咒文开始，且疑似未完整照录原字-请在咒文前注明，并完整照录原字原音，不得简化转写")
                    else:
                        m_zhou = after_yj[m_zhou_start+2:].strip()
                        op_zhou_clean = re.sub(r'\s+', '', op_zhou)
                        m_zhou_clean = re.sub(r'\s+', '', m_zhou)
                        if op_zhou_clean[:20] != m_zhou_clean[:20]:
                            issues.append(f"{sid}-{idx}-内容错误-咒文部分未照录原文原字，存在转写或简化情况-咒文必须严格照录原文汉字，不得自行更改音译或简化")

def check_sutra(sid):
    path = os.path.join(base_dir, f"{sid}.json")
    if not os.path.exists(path):
        issues.append(f"{sid}-0-文件缺失-经号{sid}对应的译文文件不存在-请补充该经完整白话译文文件")
        return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    sutra_info[sid] = {
        'title': data.get('title', '未知'),
        'translator': data.get('translator', '未知'),
        'seg_count': len(data.get('translations', []))
    }
    translations = data.get('translations', [])
    for idx, seg in enumerate(translations, 1):
        op = seg.get('original_preview', '')
        modern = seg.get('modern', '')
        check_segment(sid, idx, op, modern)

for sid in sutra_ids:
    check_sutra(sid)

# 生成报告
report = "# A路校对报告（第一批176部？不，本次12部经）\n\n"
report += "## 校对概览\n"
report += "本次校对经号：t2045、t1190、t2794、t0824、t1980、t1802、t0150、t2761、t0817、t1790、t0904、t0130\n\n"
for sid in sutra_ids:
    if sid in sutra_info:
        info = sutra_info[sid]
        cnt = len([i for i in issues if i.startswith(f"{sid}-")])
        report += f"- **{sid}**：《{info['title']}》，共{info['seg_count']}段，发现问题{cnt}条\n"
report += f"\n本次共发现问题 **{len(issues)}** 条，问题明细如下：\n\n"
report += "## 问题明细（格式：经号-段号-问题类型-问题描述-修正建议）\n\n"
for issue in issues:
    report += f"- {issue}\n"

with open('/home/user/workspace/13511660557912876654/buddhist-ontology/proofread_a_batch176.md', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"报告已生成，共{len(issues)}条问题")
print("各经问题数：")
for sid in sutra_ids:
    cnt = len([i for i in issues if i.startswith(f"{sid}-")])
    print(f"{sid}: {cnt}")
