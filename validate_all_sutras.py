#!/usr/bin/env python3
"""全量校验大正藏经文：原文+白话结构"""
import json, os, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
SUTRAS_DIR = ROOT / 'sutras'
MODERN_DIR = ROOT / 'data' / 'modern-translation'

errors = []          # 严重错误：无法加载
warnings = []        # 警告：格式问题
stats = {
    'total': 0,
    'ok': 0,
    'parse_error': 0,
    'empty_content': 0,
    'chapter_no_text': 0,
    'modern_total': 0,
    'modern_parse_error': 0,
    'modern_format_error': 0,
    'modern_ok': 0,
}

def check_modern_format(modern_text):
    """校验白话段格式：
    - 空内容算错
    - 如果有三个标签，必须顺序正确（小标题 < 义解 < 正文）
    - 长经中间的纯正文段（无任何标签）属于正常分段，不算错
    """
    if not modern_text or not isinstance(modern_text, str):
        return False, "空内容"
    has_xbt = '【小标题】' in modern_text
    has_yj = '【义解】' in modern_text
    has_zw = '【正文】' in modern_text
    has_any = has_xbt or has_yj or has_zw
    if not has_any:
        # 纯正文段（长经中间对话），合法
        return True, ""
    # 有标签时，必须三个都齐，且顺序正确
    if not (has_xbt and has_yj and has_zw):
        miss = []
        if has_any and not has_xbt: miss.append('小标题')
        if has_any and not has_yj: miss.append('义解')
        if has_any and not has_zw: miss.append('正文')
        return False, f"标签不全: 缺{','.join(miss)}"
    pos_xbt = modern_text.find('【小标题】')
    pos_yj = modern_text.find('【义解】')
    pos_zw = modern_text.find('【正文】')
    if not (pos_xbt < pos_yj < pos_zw):
        return False, "三段顺序错误"
    return True, ""

# 1. 校验所有经文原文
print(f"=== 开始校验经文原文 (目录: {SUTRAS_DIR}) ===")
sutra_files = sorted([f for f in SUTRAS_DIR.glob('t*.json') if f.name.startswith('t') and f.name[1:5].isdigit()])
stats['total'] = len(sutra_files)
print(f"共 {len(sutra_files)} 部经文")

for sf in sutra_files:
    sid = sf.stem
    # 1.1 JSON可解析
    try:
        with open(sf, 'r', encoding='utf-8') as f:
            d = json.load(f)
    except Exception as e:
        errors.append(f"[{sid}] JSON解析失败: {e}")
        stats['parse_error'] += 1
        continue
    
    # 1.2 content字段存在且非空
    content = d.get('content')
    if not content or not isinstance(content, list) or len(content) == 0:
        errors.append(f"[{sid}] content为空或不是数组")
        stats['empty_content'] += 1
        continue
    
    # 1.3 每个章节必须有text
    bad_chapters = 0
    for i, chap in enumerate(content):
        if not isinstance(chap, dict):
            bad_chapters += 1
            continue
        text = chap.get('text', '').strip()
        if not text:
            bad_chapters += 1
    if bad_chapters > 0:
        warnings.append(f"[{sid}] {bad_chapters}个章节text为空 (共{len(content)}章)")
        stats['chapter_no_text'] += 1

# 2. 校验所有白话译文
print(f"\n=== 开始校验白话译文 (目录: {MODERN_DIR}) ===")
if MODERN_DIR.exists():
    modern_files = sorted(MODERN_DIR.glob('t*.json'))
    stats['modern_total'] = len(modern_files)
    print(f"共 {len(modern_files)} 部白话译文")
    
    for mf in modern_files:
        sid = mf.stem
        try:
            with open(mf, 'r', encoding='utf-8') as f:
                md = json.load(f)
        except Exception as e:
            errors.append(f"[{sid}] 白话JSON解析失败: {e}")
            stats['modern_parse_error'] += 1
            continue
        
        translations = md.get('translations', [])
        if not translations or not isinstance(translations, list):
            warnings.append(f"[{sid}] 白话translations为空")
            continue
        
        bad_trans = 0
        for t in translations:
            if not isinstance(t, dict):
                bad_trans +=1; continue
            modern_text = t.get('modern', '')
            ok, reason = check_modern_format(modern_text)
            if not ok:
                bad_trans += 1
        if bad_trans > 0:
            warnings.append(f"[{sid}] {bad_trans}个白话段格式错误 (共{len(translations)}段)")
            stats['modern_format_error'] += 1
        else:
            stats['modern_ok'] += 1
else:
    print(f"白话目录不存在: {MODERN_DIR}")

stats['ok'] = stats['total'] - stats['parse_error'] - stats['empty_content']

# 输出结果
print("\n" + "="*60)
print("校验统计：")
print(f"  经文总数: {stats['total']}")
print(f"  原文完全正常: {stats['ok']}")
print(f"  JSON解析错误: {stats['parse_error']}")
print(f"  content为空: {stats['empty_content']}")
print(f"  部分章节无文本: {stats['chapter_no_text']}")
print(f"  白话译文总数: {stats['modern_total']}")
print(f"  白话完全正常: {stats['modern_ok']}")
print(f"  白话JSON解析错误: {stats['modern_parse_error']}")
print(f"  白话格式错误: {stats['modern_format_error']}")
print("="*60)

print(f"\n❌ 严重错误 ({len(errors)}条):")
for e in errors[:20]:
    print(f"  - {e}")
if len(errors) > 20:
    print(f"  ... 还有 {len(errors)-20} 条错误")

print(f"\n⚠️ 警告 ({len(warnings)}条):")
for w in warnings[:30]:
    print(f"  - {w}")
if len(warnings) > 30:
    print(f"  ... 还有 {len(warnings)-30} 条警告")

# 保存结果到文件
with open(ROOT / 'validation_report.md', 'w', encoding='utf-8') as f:
    f.write("# 大正藏经文全量校验报告\n\n")
    f.write(f"校验时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write("## 统计\n")
    f.write(f"- 经文总数: {stats['total']}\n")
    f.write(f"- 原文完全正常: {stats['ok']}\n")
    f.write(f"- JSON解析错误: {stats['parse_error']}\n")
    f.write(f"- content为空: {stats['empty_content']}\n")
    f.write(f"- 部分章节无文本: {stats['chapter_no_text']}\n")
    f.write(f"- 白话译文总数: {stats['modern_total']}\n")
    f.write(f"- 白话完全正常: {stats['modern_ok']}\n")
    f.write(f"- 白话JSON解析错误: {stats['modern_parse_error']}\n")
    f.write(f"- 白话格式错误: {stats['modern_format_error']}\n\n")
    
    f.write(f"## 严重错误 ({len(errors)}条)\n")
    for e in errors:
        f.write(f"- [ ] {e}\n")
    f.write(f"\n## 格式警告 ({len(warnings)}条)\n")
    for w in warnings:
        f.write(f"- [ ] {w}\n")

print(f"\n✅ 报告已保存到: {ROOT / 'validation_report.md'}")

# 返回码：有严重错误返回1
sys.exit(1 if errors else 0)
