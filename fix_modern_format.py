#!/usr/bin/env python3
"""批量修复白话译文格式，统一为【小标题】【义解】【正文】标准三段式（不改动原文内容，只补标签）"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
MODERN_DIR = ROOT / 'data' / 'modern-translation'

fixed_count = 0
total_trans = 0
fixed_trans = 0
fail_samples = []

def fix_modern_text(text):
    """把旧格式统一修复为标准三段式，只补标签不改内容"""
    if not text or not isinstance(text, str):
        return text, False
    original = text
    text = text.strip()
    
    # === 第一步：补【小标题】标签 ===
    # 情况A：开头直接是【Xxx】，但Xxx不是"小标题/义解/正文"
    m = re.match(r'^【([^】]+)】\s*', text)
    if m:
        tag_content = m.group(1).strip()
        if tag_content not in ('小标题', '义解', '正文'):
            # 把【章名】改成【小标题】章名（保留章名，只加标签字）
            text = re.sub(r'^【([^】]+)】', r'【小标题】\1', text, count=1)
    
    # 情况B：开头没有任何标签，直接是内容（异常情况，不处理）
    
    # 找三个标签位置
    xbt_pos = text.find('【小标题】')
    yj_pos = text.find('【义解】')
    zw_pos = text.find('【正文】')
    
    # === 第二步：补【义解】标签（如果有小标题没义解） ===
    if xbt_pos != -1 and yj_pos == -1:
        # 【小标题】后面是标题文字，之后换行就是义解开始，补【义解】
        after_xbt = text[xbt_pos + 5:]
        nl_pos = after_xbt.find('\n')
        if nl_pos != -1:
            insert_pos = xbt_pos + 5 + nl_pos
            text = text[:insert_pos] + '\n【义解】' + text[insert_pos:]
        else:
            # 没有换行，直接在末尾加
            text = text + '\n【义解】'
        # 重新计算位置
        yj_pos = text.find('【义解】')
    
    # === 第三步：补【正文】标签（如果有义解没正文）===
    if yj_pos != -1 and zw_pos == -1:
        after_yj = text[yj_pos + 4:]
        # 找义解结束、正文开始的位置
        # 策略：找到第一个双换行（段落分隔），在那里插入【正文】
        dl_pos = after_yj.find('\n\n')
        if dl_pos != -1:
            insert_pos = yj_pos + 4 + dl_pos
            text = text[:insert_pos] + '\n\n【正文】\n' + text[insert_pos:]
        else:
            # 没有双换行，找译文特征行
            lines = after_yj.split('\n')
            insert_line = len(lines)  # 默认插在末尾
            for i, line in enumerate(lines):
                s = line.strip()
                if not s:
                    continue
                # 义解之后第一个"译文特征行"之前插入
                if i >= 1 and re.match(r'^(.+譯|失譯|聞如是|一時，佛|我是這樣|我是这样|如是我聞|如是我闻)', s):
                    insert_line = i
                    break
                # 义解一般是完整的一句话（以句号/问号结尾），后面就是正文
                if i >= 1 and (s.endswith('。') or s.endswith('？') or s.endswith('！') or s.endswith('旨')) and len(s) > 15:
                    # 再看下一行，如果下一行不是以【开头，且不是接着解释的话，就是正文开始
                    if i+1 < len(lines) and not lines[i+1].strip().startswith('【'):
                        insert_line = i + 1
                        break
            if insert_line < len(lines):
                # 在insert_line之前插入
                insert_pos = yj_pos + 4
                for i in range(insert_line):
                    insert_pos += len(lines[i]) + 1
                text = text[:insert_pos] + '\n【正文】\n' + text[insert_pos:]
            else:
                text = text + '\n\n【正文】\n'
    
    # 清理：确保标签顺序正确
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    
    # 最终校验：三个标签都有且顺序正确
    xbt2 = text.find('【小标题】')
    yj2 = text.find('【义解】')
    zw2 = text.find('【正文】')
    if not (xbt2 != -1 and yj2 != -1 and zw2 != -1 and xbt2 < yj2 < zw2):
        fail_samples.append(text[:100])
    
    return text, (text != original)


# 处理所有白话文件
print(f"=== 开始批量修复白话译文 ===")
modern_files = sorted(MODERN_DIR.glob('t*.json'))
print(f"共 {len(modern_files)} 部白话文件")

for mf in modern_files:
    sid = mf.stem
    try:
        with open(mf, 'r', encoding='utf-8') as f:
            md = json.load(f)
    except Exception as e:
        print(f"  ! {sid} 解析失败: {e}")
        continue
    
    translations = md.get('translations', [])
    file_modified = False
    
    for t in translations:
        total_trans += 1
        if not isinstance(t, dict):
            continue
        old_modern = t.get('modern', '')
        new_modern, was_modified = fix_modern_text(old_modern)
        if was_modified:
            t['modern'] = new_modern
            fixed_trans += 1
            file_modified = True
    
    if file_modified:
        with open(mf, 'w', encoding='utf-8') as f:
            json.dump(md, f, ensure_ascii=False, indent=2)
        fixed_count += 1

print(f"\n修复完成：")
print(f"  修复文件数: {fixed_count} / {len(modern_files)}")
print(f"  修复段落数: {fixed_trans} / {total_trans}")
if fail_samples:
    print(f"  仍有 {len(fail_samples)} 段格式未达标，抽样：")
    for s in fail_samples[:5]:
        print(f"    - {s}")
