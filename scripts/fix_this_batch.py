#!/usr/bin/env python3
import json
import os
import re

kids = ['t1062','t1294','t1168','t1150','t1026','t1038','t1183','t1163','t1111','t1054','t1353','t2170']
out_dir = 'data/modern-translation'
tasks_dir = 'data/baihua-tasks'

def reset_original_previews():
    """第一步：重置所有original_preview，确保原文一字不差"""
    for kid in kids:
        task_path = os.path.join(tasks_dir, kid + '.json')
        out_path = os.path.join(out_dir, kid + '.json')
        with open(task_path, encoding='utf-8') as f:
            task = json.load(f)
        with open(out_path, encoding='utf-8') as f:
            out = json.load(f)
        for i in range(len(task['translations'])):
            out['translations'][i]['original_preview'] = task['translations'][i]['original_preview']
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    print("original_preview 已全部重置为原始骨架内容")

def fix_sutra(kid):
    path = os.path.join(out_dir, kid + '.json')
    with open(path, encoding='utf-8') as f:
        s = json.load(f)
    
    for seg in s['translations']:
        op = seg['original_preview']
        m = seg['modern']
        
        # 1. 彻底修复悉昙梵字乱码：识别咒文段落，将咒文部分完全替换为original_preview原文
        # 咒文段落特征：original_preview包含大量高码位悉昙字，或开头是咒文、包含二合/反切注
        # 通用策略：找到modern中咒文开始的位置（"以下为真言/咒文原文"之后），之后到段尾的所有字符，用op中对应咒文完全替换
        if '【义解】' in m:
            parts = m.split('【义解】', 1)
            pre = parts[0] + '【义解】'
            post = parts[1]
            
            # 找咒文起始标记
            mantra_markers = ['以下为真言原文', '以下为咒文原文', '所有梵字、反切音注均照录原文：', '所有梵字、悉昙字、反切音注均照录原文：', '以下为陀罗尼原文']
            mantra_start_idx = -1
            for marker in mantra_markers:
                idx = post.find(marker)
                if idx != -1:
                    mantra_start_idx = idx + len(marker)
                    break
            
            if mantra_start_idx != -1:
                # 咒文开头之前是中文说明，之后应该完全照录original_preview
                # 清理掉所有�开头的乱码，然后把op原封不动放在咒文部分
                # 先去掉post中所有乱码字符
                clean_pre = post[:mantra_start_idx]
                # 咒文部分直接用op，完全照录
                mantra_text = op
                # 替换所有乱码
                new_post = clean_pre + mantra_text
                seg['modern'] = pre + new_post
        
        # 2. 修正通用标点错字问题（每部经通用）
        m = seg['modern']
        # 繁简："靈雲"改为"灵云"，"雲"在非专有名词中改为"云"
        m = m.replace('靈雲', '灵云').replace('灵雲', '灵云')
        # "千大洞夭"改为"千大洞天"
        m = m.replace('千大洞夭', '千大洞天')
        # 修正段首孤立右引号：如果modern开头是”或者」，删除
        while m.startswith('”') or m.startswith('」'):
            m = m[1:]
        # 补译者题记后句号
        m = re.sub(r'奉詔翻譯 $', '奉诏翻译。', m)
        m = re.sub(r'翻譯 $', '翻译。', m)
        m = re.sub(r'奉詔譯 $', '奉诏翻译。', m)
        m = re.sub(r'奉詔注釋義', '奉诏注释义理。', m)
        # "干人鬼"改为"若干人鬼"
        m = m.replace('干人鬼', '若干人鬼')
        # "藥叉"改为"药叉"
        m = m.replace('藥叉', '药叉')
        # 删除所有�替换乱码残留
        m = re.sub(r'�[0-9a-zA-Z]*', '', m)
        
        seg['modern'] = m
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(s, f, ensure_ascii=False, indent=2)
    print(f'{kid}: 修复完成')

def main():
    reset_original_previews()
    for kid in kids:
        fix_sutra(kid)
    print("全部修复完成")

if __name__ == "__main__":
    main()
