import json
import re
import os

base_dir = "/home/user/workspace/13511660557912876654/buddhist-ontology/data/modern-translation/"
sutra_ids = ['t2045','t1190','t2794','t0824','t1980','t1802','t0150','t2761','t0817','t1790','t0904','t0130']

issues = []

def check_sutra(sid):
    path = os.path.join(base_dir, f"{sid}.json")
    if not os.path.exists(path):
        issues.append(f"{sid}-0-文件缺失-指定经号文件不存在-请补充该经译文文件")
        return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    translations = data.get('translations', [])
    print(f"检查 {sid}，共 {len(translations)} 段")
    
    for idx, seg in enumerate(translations, 1):
        op = seg.get('original_preview', '').strip()
        modern = seg.get('modern', '').strip()
        
        # 检查original_preview是否为空
        if not op:
            issues.append(f"{sid}-{idx}-字段缺失-original_preview字段为空-请补充原文预览内容")
        
        # 检查modern格式
        if not modern:
            issues.append(f"{sid}-{idx}-字段缺失-modern字段为空-请补充白话译文")
            continue
        
        # 检查开头小标题
        if not modern.startswith('【'):
            issues.append(f"{sid}-{idx}-格式错误-modern未以【小标题】开头-请在段首添加四至八字的小标题，格式为【小标题】")
        else:
            # 匹配第一个】的位置
            first_end = modern.find('】')
            if first_end == -1:
                issues.append(f"{sid}-{idx}-格式错误-modern开头小标题未闭合-请补全小标题的闭合】")
            else:
                title_part = modern[1:first_end]
                title_len = len(title_part)
                if title_len <4 or title_len >8:
                    issues.append(f"{sid}-{idx}-格式错误-开头小标题字数为{title_len}字，不符合四至八字要求-请将小标题调整为4-8字，当前为「{title_part}」")
        
        # 检查是否包含【义解】
        if '【义解】' not in modern:
            issues.append(f"{sid}-{idx}-格式错误-modern字段未包含【义解】标记-请在小标题后添加【义解】标记")
        else:
            # 检查义解后是否有正文
            yijie_pos = modern.find('【义解】')
            after_yijie = modern[yijie_pos+4:].strip()
            if not after_yijie:
                issues.append(f"{sid}-{idx}-内容缺失-【义解】后无白话正文，内容为空-请补充义解后的白话译文内容")
            else:
                # 检查义解后是否完全照搬原文（没有翻译）
                # 去除换行空格对比
                op_clean = re.sub(r'\s+', '', op)
                after_clean = re.sub(r'\s+', '', after_yijie)
                # 先检查是否有明显的重复标点
                if '，，' in after_yijie or '。。' in after_yijie or '：：' in after_yijie:
                    dup_punc = []
                    if '，，' in after_yijie: dup_punc.append('连续逗号')
                    if '。。' in after_yijie: dup_punc.append('连续句号')
                    if '：：' in after_yijie: dup_punc.append('连续冒号')
                    issues.append(f"{sid}-{idx}-格式错误-译文中存在{','.join(dup_punc)}等重复标点-请删除多余标点，修正为正常标点格式")
                
                # 检查是否整段照搬原文未翻译（开头有译经题记的话单独算）
                if op_clean.startswith(after_clean[:20]) and len(after_clean) > 30:
                    # 检查是否完全是原文内容
                    if after_clean[:30] in op_clean and not any(kw in after_yijie for kw in ['就是说', '意思是', '这是说', '指的是', '佛陀说', '应当', '应该']):
                        issues.append(f"{sid}-{idx}-内容错误-【义解】后疑似直接照搬原文未做白话翻译-请将文言原文翻译为通顺白话，不要直接照录原文")
        
        # 检查咒文相关：如果原文有"咒曰""真言""陀罗尼"等关键词，检查modern里的咒文是否照录原字
        if any(kw in op for kw in ['咒曰', '真言', '陀罗尼', '呪曰']):
            # 提取原文咒文部分（简单匹配咒曰后面的内容）
            zhou_start = max(op.find('咒曰'), op.find('呪曰'), op.find('真言'))
            if zhou_start != -1:
                op_zhou = op[zhou_start+2:].strip()
                # 提取modern里咒曰后面的内容
                m_zhou_start = max(modern.find('咒曰'), modern.find('呪曰'), modern.find('真言'))
                if m_zhou_start != -1:
                    m_zhou = modern[m_zhou_start+2:].strip()
                    # 对比前20字，看是否有转写简化
                    op_zhou_clean = re.sub(r'\s+', '', op_zhou)[:30]
                    m_zhou_clean = re.sub(r'\s+', '', m_zhou)[:30]
                    if op_zhou_clean[:10] != m_zhou_clean[:10]:
                        issues.append(f"{sid}-{idx}-内容错误-咒文部分疑似未照录原字原音，存在简化转写-咒文必须完全照录原文原字，不得自行音译或简化")

for sid in sutra_ids:
    check_sutra(sid)

print("\n=== 初步检查问题数：", len(issues))
for i in issues[:20]:
    print(i)
