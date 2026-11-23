#!/usr/bin/env python3
"""重新审计全库白话译文质量，更新台账"""
import json, os, re, opencc, sys, glob
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding='utf-8')

cc = opencc.OpenCC('t2s.json')
FORCE_MAP = {'為':'为','於':'于','無':'无','說':'说','爾':'尔','雲':'云','蓋':'盖','恆':'恒','呪':'咒',
             '過':'过','還':'还','這':'这','那':'那','麼':'么','裡':'里','會':'会','個':'个','並':'并',
             '薩':'萨','葉':'叶','闍':'阇','乾':'乾','餘':'余','後':'后','係':'系','徵':'征','鍾':'钟',
             '瀋':'沈','醜':'丑','瞭':'了','藉':'借','么':'么','佈':'布','儘':'尽','驚':'惊','亂':'乱','個':'个','師':'师','恥':'耻'}

trad_chars = set('為於無說爾雲蓋恆呪過還這麼裡會個並薩葉闍乾餘後係徵鍾瀋醜瞭藉么佈儘驚亂個師恆國實現對發應當時來從長門關點樂經書學問話語見聞覺知')

forbidden_patterns = [
    '这一段文字告诉我们', '这段内容主要讲了', '这一节经文开示我们', '本段主要', '这一品主要',
    '这一段佛陀教导我们', '这一部分说明', '这段经文主要讲述', '此段经文告诉我们', '这段话揭示了',
    '这一部分佛陀为我们开示', '这一段宣说了', '本节经文主要说明', '此段大意是说', '这一段主要阐述了',
    '这段话开示了', '这一品中佛陀告诉我们', '这里宣说了', '这段文字的核心意思是', '这一段文字向我们开示',
    '这一段讲的是', '这一节主要讲了', '这一段核心内容是', '这一段揭示了', '这一段中佛陀告诉我们',
]

TRANS_DIR = 'data/modern-translation'
SUTRA_DIR = 'sutras'

def audit_file(tid):
    fpath = os.path.join(TRANS_DIR, f'{tid}.json')
    issues = set()
    detail = {'segments': 0, 'empty_zw': 0, 'paste_classical': 0, 'truncate': 0, 
              'trad_modern': 0, 'stacked': 0, 'short_ratio': 0, 'yijie_repeat': 0,
              'dup_title_count': 0, 'forbidden_count': 0, 'bad_structure': 0, 'missing_section_all': False,
              'missing_original': 0, 'wrong_field': 0}
    if not os.path.exists(fpath):
        issues.add('file_missing')
        return issues, detail
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        issues.add('json_error')
        return issues, detail
    
    trans = data.get('translations', [])
    detail['segments'] = len(trans)
    if len(trans) == 0:
        issues.add('empty_file')
        return issues, detail
    
    titles = Counter()
    yijie_starts = Counter()
    has_any_section = False
    has_bad_structure = False
    
    for i, t in enumerate(trans):
        # 检查字段名
        if 'modern' not in t and 'explanation' in t:
            issues.add('wrong_field')
            detail['wrong_field'] += 1
        
        mod = t.get('modern', '')
        if not mod:
            mod = t.get('explanation', '')
            if mod:
                issues.add('wrong_field')
        
        orig = t.get('original_preview', '')
        if not orig:
            issues.add('missing_original')
            detail['missing_original'] += 1
        
        # 检查section字段
        sec = t.get('section', '')
        if sec:
            has_any_section = True
        
        # 解析三段式
        title = ''
        yijie = ''
        zw = ''
        m = re.search(r'【小标题】\s*(.*?)(?=\n?【|$)', mod, re.DOTALL)
        if m: title = m.group(1).strip()
        m = re.search(r'【义解】\s*(.*?)(?=\n?【|$)', mod, re.DOTALL)
        if m: yijie = m.group(1).strip()
        m = re.search(r'【正文】\s*(.*?)$', mod, re.DOTALL)
        if m: zw = m.group(1).strip()
        
        # 检查三段式结构
        if not (title and yijie and zw):
            # 检查是否是其他标签
            if re.search(r'【(?!小标题|义解|正文|原文)', mod):
                issues.add('bad_structure')
                has_bad_structure = True
            elif not mod:
                pass
            else:
                # 可能旧格式，也算结构问题
                if not zw and mod:
                    # 没有正文标签
                    issues.add('bad_structure')
                    has_bad_structure = True
        
        if title:
            titles[title] += 1
        if yijie:
            yijie_starts[yijie[:20]] += 1
        
        # 空正文
        if not zw or len(zw.strip()) < 10:
            detail['empty_zw'] += 1
            issues.add('empty_zw')
        
        # 贴文言（白话太短或全是文言特征字）
        if zw and len(zw) < 50 and orig:
            orig_text = re.sub(r'\s', '', orig)
            if len(orig_text) > 100:
                detail['short_ratio'] += 1
                issues.add('short_ratio')
        
        # 繁体残留（modern中）
        trad_in_mod = 0
        for ch in mod:
            if ch in trad_chars:
                trad_in_mod += 1
        if trad_in_mod > 2:
            detail['trad_modern'] += 1
            issues.add('trad')
        
        # 截断（末尾是冒号/逗号/顿号等）
        if zw and re.search(r'[：，、；：「『（]$', zw.strip()):
            detail['truncate'] += 1
            issues.add('truncate')
        
        # 标签堆叠
        stacked = re.findall(r'【[^】]*】\s*【', mod)
        if stacked and len(stacked) > 1:
            detail['stacked'] += 1
            issues.add('stacked')
        
        # 套话
        for pat in forbidden_patterns:
            if pat in yijie:
                detail['forbidden_count'] += 1
                issues.add('forbidden')
                break
    
    if not has_any_section:
        issues.add('missing_section_all')
        detail['missing_section_all'] = True
    
    # 小标题重名
    dup = sum(1 for k,v in titles.items() if v > 3)
    if dup > 0:
        issues.add('dup_title')
        detail['dup_title_count'] = dup
    
    # 义解高重复
    high_rep = sum(1 for k,v in yijie_starts.items() if v >= 10)
    if high_rep > 0:
        issues.add('yijie_repeat')
        detail['yijie_repeat'] = high_rep
    
    # 贴文言检测（取前几段做抽样）
    paste_count = 0
    for t in trans[:20]:
        mod = t.get('modern', '')
        orig = t.get('original_preview', '')
        zw_m = re.search(r'【正文】\s*(.*?)$', mod, re.DOTALL)
        if zw_m and orig:
            zw_text = re.sub(r'\s', '', zw_m.group(1))
            orig_text = re.sub(r'\s', '', orig)
            if zw_text and orig_text:
                # 白话和原文前50字重合度
                overlap = len(set(zw_text[:80]) & set(orig_text[:80])) / max(len(set(orig_text[:80])),1)
                if overlap > 0.9 and len(zw_text) < len(orig_text) * 0.8:
                    paste_count += 1
    if paste_count >= 10:
        issues.add('paste_classical')
        detail['paste_classical'] = paste_count
    
    return issues, detail

def main():
    all_tids = sorted([f.replace('.json','') for f in os.listdir(TRANS_DIR) if f.endswith('.json') and f != 'tree.json'])
    print(f'总经数: {len(all_tids)}')
    
    # 排除别名经页
    real_tids = [t for t in all_tids if re.match(r'^t\d+[a-z]?$', t)]
    alias_tids = [t for t in all_tids if t not in real_tids]
    print(f'正式经: {len(real_tids)}, 别名经: {len(alias_tids)}')
    
    results = {}
    issue_counts = Counter()
    p0_list = []
    p1_list = []
    p2_list = []
    
    p0_issues = {'wrong_field', 'missing_original', 'stacked', 'json_error', 'empty_file', 'file_missing'}
    p1_issues = {'missing_section_all', 'trad', 'bad_structure', 'paste_classical'}
    p2_issues = {'empty_zw', 'short_ratio', 'truncate', 'dup_title', 'yijie_repeat', 'forbidden'}
    
    ok_count = 0
    for tid in real_tids:
        issues, detail = audit_file(tid)
        results[tid] = {'issues': list(issues), 'detail': detail}
        for iss in issues:
            issue_counts[iss] += 1
        if not issues:
            ok_count += 1
        elif issues & p0_issues:
            p0_list.append(tid)
        elif issues & p1_issues:
            p1_list.append(tid)
        else:
            p2_list.append(tid)
    
    print(f'\n合格经数: {ok_count}')
    print(f'P0 致命: {len(p0_list)}')
    print(f'P1 机械/结构: {len(p1_list)}')
    print(f'P2 内容质量: {len(p2_list)}')
    print(f'\n问题分布:')
    for iss, cnt in issue_counts.most_common():
        print(f'  {iss}: {cnt}')
    
    # 写出JSON结果供后续修复使用
    with open('/tmp/audit_result.json', 'w', encoding='utf-8') as f:
        json.dump({tid: {'issues': results[tid]['issues'], 'detail': results[tid]['detail']} for tid in real_tids}, f, ensure_ascii=False, indent=2)
    
    # 生成台账
    lines = ['# 全库白话译文质量审计台账', f'', f'**审计时间**：2026-11-24（更新）', f'**总经数**：{len(real_tids)} 部', f'**合格数**：{ok_count} 部', f'**待返修数**：{len(real_tids)-ok_count} 部', '']
    lines.append('## 缺陷分类统计')
    lines.append('')
    lines.append('| 缺陷类别 | 涉及经数 | 说明 |')
    lines.append('|----------|----------|------|')
    desc = {
        'empty_zw': '【正文】字段过短，白话译文缺失或不足',
        'missing_section_all': '全书缺失section字段',
        'forbidden': '存在模板套话',
        'bad_structure': '三段式结构缺失/错误',
        'dup_title': '小标题重名',
        'paste_classical': '正文贴文言，未白话化',
        'yijie_repeat': '义解前20字高重复(≥10次)',
        'truncate': '正文截断',
        'stacked': '标签堆叠',
        'short_ratio': '正文严重缩水',
        'trad': '简体残留繁体',
        'missing_original': '缺失original_preview',
        'wrong_field': '字段名错误(explanation而非modern)',
        'json_error': 'JSON语法错误',
        'empty_file': '译文文件为空',
        'file_missing': '译文文件缺失',
    }
    for iss, cnt in issue_counts.most_common():
        lines.append(f'| {iss} | {cnt} | {desc.get(iss, "")} |')
    
    lines.append('')
    lines.append(f'### P0 致命硬伤（{len(p0_list)} 部）')
    lines.append('')
    for i in range(0, len(p0_list), 10):
        lines.append('、'.join(p0_list[i:i+10]))
    
    lines.append('')
    lines.append(f'### P1 机械/结构问题（{len(p1_list)} 部）')
    lines.append('')
    for i in range(0, len(p1_list), 10):
        lines.append('、'.join(p1_list[i:i+10]))
    
    lines.append('')
    lines.append(f'### P2 内容质量问题（{len(p2_list)} 部）')
    lines.append('')
    for i in range(0, len(p2_list), 10):
        lines.append('、'.join(p2_list[i:i+10]))
    
    with open('全库白话译文质量审计台账.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'\n台账已更新')

if __name__ == '__main__':
    main()
